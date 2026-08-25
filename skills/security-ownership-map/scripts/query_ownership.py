#!/usr/bin/env python3
"""Query the ownership knowledge graph for common investigation questions.

This script provides a CLI for querying the Neo4j ownership graph with
pre-built query templates for common security investigation patterns.

Usage:
    python query_ownership.py --list-queries
    python query_ownership.py --query who-owns --service payments-api
    python query_ownership.py --query blast-radius --service auth-service
    python query_ownership.py --query find-expert --path src/auth/
    python query_ownership.py --query deps-of --service checkout-service
    python query_ownership.py --query who-depends-on --service user-db
    python query_ownership.py --query team-services --team platform
    python query_ownership.py --query oncall --team payments
    python query_ownership.py --query stale --days 90
    python query_ownership.py --query shared-code --min-teams 2
    python query_ownership.py --cypher "MATCH (s:Service) RETURN s.name"

Requires:
    pip install neo4j
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD environment variables
    (or pass --uri, --user, --password)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


# ---------------------------------------------------------------------------
# Query templates
# ---------------------------------------------------------------------------

QUERIES: dict[str, dict[str, Any]] = {
    "who-owns": {
        "description": "Who owns a service? Returns team, tech lead, and on-call.",
        "params": ["service"],
        "cypher": """
            MATCH (s:Service {name: $service})
            OPTIONAL MATCH (t:Team)-[:OWNS]->(s)
            OPTIONAL MATCH (tl:Person)-[:TECH_LEAD_OF]->(t)
            OPTIONAL MATCH (oc:Person)-[:ONCALL_FOR]->(t)
            RETURN s.name AS service,
                   s.repo AS repo,
                   s.language AS language,
                   s.criticality AS criticality,
                   t.name AS team,
                   t.slack_channel AS slack,
                   tl.name AS tech_lead,
                   tl.email AS tech_lead_email,
                   oc.name AS oncall,
                   oc.email AS oncall_email,
                   oc.slack_handle AS oncall_slack
        """,
    },
    "blast-radius": {
        "description": "What is the blast radius of a service failure? Returns dependent services and their owners.",
        "params": ["service"],
        "cypher": """
            MATCH (s:Service {name: $service})
            OPTIONAL MATCH (dependent:Service)-[:DEPENDS_ON]->(s)
            OPTIONAL MATCH (t:Team)-[:OWNS]->(dependent)
            OPTIONAL MATCH (oc:Person)-[:ONCALL_FOR]->(t)
            RETURN s.name AS failed_service,
                   dependent.name AS affected_service,
                   dependent.criticality AS criticality,
                   t.name AS owning_team,
                   t.slack_channel AS team_slack,
                   oc.name AS oncall,
                   oc.slack_handle AS oncall_slack
            ORDER BY
                CASE dependent.criticality
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    ELSE 3
                END
        """,
    },
    "find-expert": {
        "description": "Who knows a file/directory best? Returns top contributors by commit count.",
        "params": ["path"],
        "cypher": """
            MATCH (f:File)
            WHERE f.path STARTS WITH $path OR f.path = $path
            MATCH (p:Person)-[c:COMMITS_TO]->(f)
            OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
            RETURN f.path AS file,
                   p.name AS contributor,
                   p.email AS email,
                   p.slack_handle AS slack,
                   c.commit_count AS commits,
                   c.last_commit_at AS last_commit,
                   t.name AS team
            ORDER BY c.commit_count DESC
            LIMIT 20
        """,
    },
    "deps-of": {
        "description": "What does a service depend on? Returns direct and transitive dependencies.",
        "params": ["service"],
        "cypher": """
            MATCH (s:Service {name: $service})
            MATCH (s)-[:DEPENDS_ON*1..3]->(dep:Service)
            OPTIONAL MATCH (t:Team)-[:OWNS]->(dep)
            WITH dep, t,
                 length(shortestPath((s)-[:DEPENDS_ON*]->(dep))) AS depth
            RETURN dep.name AS dependency,
                   dep.criticality AS criticality,
                   depth,
                   t.name AS owning_team,
                   t.slack_channel AS team_slack
            ORDER BY depth, dep.name
        """,
    },
    "who-depends-on": {
        "description": "What depends on a service? Returns all dependents (reverse deps).",
        "params": ["service"],
        "cypher": """
            MATCH (s:Service {name: $service})
            MATCH (dependent:Service)-[:DEPENDS_ON*1..3]->(s)
            OPTIONAL MATCH (t:Team)-[:OWNS]->(dependent)
            WITH dependent, t, s,
                 length(shortestPath((dependent)-[:DEPENDS_ON*]->(s))) AS depth
            RETURN dependent.name AS dependent_service,
                   dependent.criticality AS criticality,
                   depth,
                   t.name AS owning_team,
                   t.slack_channel AS team_slack
            ORDER BY depth, dependent.name
        """,
    },
    "team-services": {
        "description": "What services does a team own?",
        "params": ["team"],
        "cypher": """
            MATCH (t:Team {name: $team})-[:OWNS]->(s:Service)
            OPTIONAL MATCH (s)-[:DEPENDS_ON]->(dep:Service)
            RETURN s.name AS service,
                   s.repo AS repo,
                   s.language AS language,
                   s.criticality AS criticality,
                   s.description AS description,
                   collect(DISTINCT dep.name) AS dependencies
            ORDER BY
                CASE s.criticality
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    ELSE 3
                END,
                s.name
        """,
    },
    "oncall": {
        "description": "Who is on-call for a team?",
        "params": ["team"],
        "cypher": """
            MATCH (t:Team {name: $team})
            OPTIONAL MATCH (oc:Person)-[:ONCALL_FOR]->(t)
            OPTIONAL MATCH (tl:Person)-[:TECH_LEAD_OF]->(t)
            OPTIONAL MATCH (t)-[:OWNS]->(s:Service)
            RETURN t.name AS team,
                   t.slack_channel AS slack,
                   oc.name AS oncall,
                   oc.email AS oncall_email,
                   oc.slack_handle AS oncall_slack,
                   oc.github_username AS oncall_github,
                   tl.name AS tech_lead,
                   tl.email AS tech_lead_email,
                   collect(s.name) AS services
        """,
    },
    "stale": {
        "description": "Find code with no recent commits (default: 90 days). Useful for finding abandoned ownership.",
        "params": ["days"],
        "cypher": """
            MATCH (f:File)<-[c:COMMITS_TO]-(p:Person)
            WHERE c.last_commit_at < datetime() - duration({days: toInteger($days)})
            OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
            WITH f, p, c, t
            ORDER BY c.last_commit_at ASC
            RETURN f.path AS file,
                   p.name AS last_contributor,
                   p.email AS email,
                   c.last_commit_at AS last_commit,
                   c.commit_count AS total_commits,
                   t.name AS team
            LIMIT 50
        """,
    },
    "shared-code": {
        "description": "Find files/dirs touched by multiple teams (ownership ambiguity).",
        "params": ["min_teams"],
        "cypher": """
            MATCH (f:File)<-[:COMMITS_TO]-(p:Person)-[:MEMBER_OF]->(t:Team)
            WITH f, collect(DISTINCT t.name) AS teams, count(DISTINCT t) AS team_count
            WHERE team_count >= toInteger($min_teams)
            RETURN f.path AS file,
                   team_count,
                   teams
            ORDER BY team_count DESC, f.path
            LIMIT 50
        """,
    },
    "critical-path": {
        "description": "Find all critical services and their ownership chain.",
        "params": [],
        "cypher": """
            MATCH (s:Service {criticality: 'critical'})
            OPTIONAL MATCH (t:Team)-[:OWNS]->(s)
            OPTIONAL MATCH (tl:Person)-[:TECH_LEAD_OF]->(t)
            OPTIONAL MATCH (oc:Person)-[:ONCALL_FOR]->(t)
            OPTIONAL MATCH (s)-[:DEPENDS_ON]->(dep:Service)
            RETURN s.name AS service,
                   s.repo AS repo,
                   t.name AS team,
                   tl.name AS tech_lead,
                   oc.name AS oncall,
                   oc.slack_handle AS oncall_slack,
                   collect(DISTINCT dep.name) AS dependencies
            ORDER BY s.name
        """,
    },
    "orphaned": {
        "description": "Find services with no owning team (orphaned services).",
        "params": [],
        "cypher": """
            MATCH (s:Service)
            WHERE NOT (:Team)-[:OWNS]->(s)
            OPTIONAL MATCH (s)<-[:DEPENDS_ON]-(dependent:Service)
            RETURN s.name AS service,
                   s.repo AS repo,
                   s.criticality AS criticality,
                   s.language AS language,
                   count(dependent) AS dependent_count
            ORDER BY
                CASE s.criticality
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    ELSE 3
                END,
                dependent_count DESC
        """,
    },
    "person-lookup": {
        "description": "Look up a person — their team, services, and expertise areas.",
        "params": ["name"],
        "cypher": """
            MATCH (p:Person)
            WHERE toLower(p.name) CONTAINS toLower($name)
               OR toLower(p.email) CONTAINS toLower($name)
               OR toLower(p.github_username) CONTAINS toLower($name)
            OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
            OPTIONAL MATCH (p)-[:TECH_LEAD_OF]->(tl_team:Team)
            OPTIONAL MATCH (p)-[:ONCALL_FOR]->(oc_team:Team)
            OPTIONAL MATCH (p)-[c:COMMITS_TO]->(f:File)
            WITH p, t, tl_team, oc_team,
                 collect({path: f.path, commits: c.commit_count}) AS files
            RETURN p.name AS name,
                   p.email AS email,
                   p.github_username AS github,
                   p.slack_handle AS slack,
                   t.name AS team,
                   tl_team.name AS tech_lead_of,
                   oc_team.name AS oncall_for,
                   [f IN files WHERE f.path IS NOT NULL | f][..10] AS top_files
        """,
    },
}


# ---------------------------------------------------------------------------
# Neo4j connection helpers
# ---------------------------------------------------------------------------

def get_driver(uri: str, user: str, password: str):
    """Create a Neo4j driver. Imports neo4j lazily so --help works without it."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Error: neo4j package required. Install with: pip install neo4j", file=sys.stderr)
        sys.exit(1)
    return GraphDatabase.driver(uri, auth=(user, password))


def run_query(driver, cypher: str, params: dict | None = None) -> list[dict]:
    """Execute a Cypher query and return results as a list of dicts."""
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [dict(record) for record in result]


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_table(rows: list[dict]) -> str:
    """Format query results as a simple text table."""
    if not rows:
        return "(no results)"

    # Collect all keys, preserving order from first row
    keys = list(rows[0].keys())
    for row in rows[1:]:
        for k in row:
            if k not in keys:
                keys.append(k)

    # Stringify values
    str_rows = []
    for row in rows:
        str_rows.append({k: _stringify(row.get(k)) for k in keys})

    # Column widths
    widths = {k: len(k) for k in keys}
    for row in str_rows:
        for k in keys:
            widths[k] = max(widths[k], len(row[k]))

    # Build table
    header = " | ".join(k.ljust(widths[k]) for k in keys)
    separator = "-+-".join("-" * widths[k] for k in keys)
    lines = [header, separator]
    for row in str_rows:
        lines.append(" | ".join(row[k].ljust(widths[k]) for k in keys))

    return "\n".join(lines)


def _stringify(val: Any) -> str:
    """Convert a value to a display string."""
    if val is None:
        return "-"
    if isinstance(val, list):
        if not val:
            return "[]"
        # Handle list of dicts (e.g., top_files)
        if val and isinstance(val[0], dict):
            return ", ".join(
                f"{d.get('path', '?')}({d.get('commits', '?')})" for d in val if d.get("path")
            )
        return ", ".join(str(v) for v in val if v is not None)
    return str(val)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def list_queries() -> None:
    """Print available query templates."""
    print("Available queries:\n")
    for name, q in QUERIES.items():
        params = ", ".join(f"--{p}" for p in q["params"]) if q["params"] else "(none)"
        print(f"  {name}")
        print(f"    {q['description']}")
        print(f"    Params: {params}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query the ownership knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s --list-queries
  %(prog)s --query who-owns --service payments-api
  %(prog)s --query blast-radius --service auth-service
  %(prog)s --query find-expert --path src/auth/
  %(prog)s --query stale --days 90
  %(prog)s --cypher 'MATCH (s:Service) RETURN s.name LIMIT 10'
        """,
    )

    # Query selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-queries", action="store_true", help="List available query templates")
    group.add_argument("--query", "-q", help="Run a named query template")
    group.add_argument("--cypher", "-c", help="Run raw Cypher query")

    # Query parameters
    parser.add_argument("--service", help="Service name (for who-owns, blast-radius, deps-of, etc.)")
    parser.add_argument("--team", help="Team name (for team-services, oncall)")
    parser.add_argument("--path", help="File/directory path (for find-expert)")
    parser.add_argument("--name", help="Person name/email/username (for person-lookup)")
    parser.add_argument("--days", type=int, default=90, help="Days threshold for stale query (default: 90)")
    parser.add_argument("--min-teams", type=int, default=2, dest="min_teams",
                        help="Minimum teams for shared-code query (default: 2)")

    # Connection
    parser.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                        help="Neo4j URI (default: $NEO4J_URI or bolt://localhost:7687)")
    parser.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"),
                        help="Neo4j username (default: $NEO4J_USER or neo4j)")
    parser.add_argument("--password", default=os.environ.get("NEO4J_PASSWORD", ""),
                        help="Neo4j password (default: $NEO4J_PASSWORD)")

    # Output
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of table")

    args = parser.parse_args()

    if args.list_queries:
        list_queries()
        return

    # Build parameters dict from args
    params: dict[str, Any] = {}
    if args.service:
        params["service"] = args.service
    if args.team:
        params["team"] = args.team
    if args.path:
        params["path"] = args.path
    if args.name:
        params["name"] = args.name
    params["days"] = str(args.days)
    params["min_teams"] = str(args.min_teams)

    # Determine Cypher and validate params
    if args.cypher:
        cypher = args.cypher
    elif args.query:
        if args.query not in QUERIES:
            print(f"Unknown query: {args.query}", file=sys.stderr)
            print(f"Available: {', '.join(QUERIES.keys())}", file=sys.stderr)
            sys.exit(1)
        query_def = QUERIES[args.query]
        cypher = query_def["cypher"]
        # Check required params
        for p in query_def["params"]:
            # Map param names: min_teams comes from --min-teams
            arg_val = params.get(p)
            if not arg_val and p not in ("days", "min_teams"):
                print(f"Error: --{p.replace('_', '-')} is required for query '{args.query}'", file=sys.stderr)
                sys.exit(1)
    else:
        print("Error: specify --query or --cypher", file=sys.stderr)
        sys.exit(1)

    # Connect and run
    if not args.password:
        print("Error: Neo4j password required. Set NEO4J_PASSWORD or pass --password", file=sys.stderr)
        sys.exit(1)

    driver = get_driver(args.uri, args.user, args.password)
    try:
        rows = run_query(driver, cypher, params)
    finally:
        driver.close()

    # Output
    if args.json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        print(format_table(rows))
        print(f"\n({len(rows)} result{'s' if len(rows) != 1 else ''})")


if __name__ == "__main__":
        main()
