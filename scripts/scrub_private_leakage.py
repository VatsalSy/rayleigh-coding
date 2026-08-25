#!/usr/bin/env python3
"""Scrub private / fleet / personal leakage from rayleigh-coding skills."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "rayleigh-coding" / "skills"

# Order matters for some replacements.
REPLACEMENTS: list[tuple[str, str]] = [
    # Trigger phrasing
    (r"Use when Vatsal says", "Use when the user says"),
    (r"Use when Vatsal asks", "Use when the user asks"),
    (r"Use only when Vatsal explicitly says", "Use only when the user explicitly says"),
    (r"when Vatsal says", "when the user says"),
    (r"when Vatsal asks", "when the user asks"),
    (r"Do not make Vatsal", "Do not make the user"),
    (r"wait for Vatsal to", "wait for the user to"),
    (r"ask Vatsal", "ask the user"),
    (r"Ask Vatsal", "Ask the user"),
    (r"require Vatsal", "require the user"),
    (r"Require Vatsal", "Require the user"),
    (r"Vatsal may leave", "The user may leave"),
    (r"Vatsal's workflow", "this workflow"),
    (r"Vatsal's Chrome profile", "the user's Chrome profile"),
    (r"Vatsal's mental model", "the user's mental model"),
    (r"for Vatsal", "for the user"),
    (r"to Vatsal", "to the user"),
    (r"Vatsal reads", "the user reads"),
    (r"anything Vatsal reads", "anything the user reads"),
    (r"CoMPhy-native,?\s*", ""),
    (r"CoMPhy/Jarvis counterpart", "coding-workflow counterpart"),
    (r"Jarvis-native", "coding-native"),
    (r"Jarvis workflows", "coding workflows"),
    (r"the Jarvis catalogue", "the skill catalogue"),
    (r"jarvis-skills", "this-skills-repo"),
    (r"VatsalSy/jarvis-skills", "OWNER/skills-repo"),
    (r"git@github\.com:VatsalSy/jarvis-skills\.git", "git@github.com:OWNER/skills-repo.git"),
    # Personal identity defaults
    (r"vatsal\.sanjay@comphy-lab\.org", "AUTHOR_EMAIL"),
    (r"vatsalsy@comphy-lab\.org", "AUTHOR_EMAIL"),
    (r"vatsalsanjay@gmail\.com", "AUTHOR_EMAIL"),
    (r"\$\{AUTHOR_EMAIL:-AUTHOR_EMAIL\}", "${AUTHOR_EMAIL:-you@example.com}"),
    (r"\$\{AUTHOR_NAME:-Vatsal Sanjay\}", "${AUTHOR_NAME:-Your Name}"),
    (r"Vatsal Sanjay", "Your Name"),
    (r"--assignee VatsalSy", "--assignee OWNER"),
    (r"assignee `VatsalSy`", "assignee `OWNER`"),
    (r"assignee VatsalSy", "assignee OWNER"),
    (r"DEFAULT_FORK_URL = ['\"]git@github\.com:VatsalSy/raycast-extensions\.git['\"]",
     "DEFAULT_FORK_URL = os.environ.get('RAYCAST_FORK_URL', 'git@github.com:OWNER/raycast-extensions.git')"),
    (r"git@github\.com:VatsalSy/raycast-extensions\.git",
     "git@github.com:OWNER/raycast-extensions.git"),
    # Fleet hosts → generic
    (r"Rayleigh and Worthington", "controller A"),
    (r"Taylor and Kelvin/Stokes", "controller B"),
    (r"Rayleigh/Taylor/Kelvin/Worthington", "controllers"),
    (r"Rayleigh, Taylor and Kelvin", "controllers"),
    (r"Taylor, Kelvin and Worthington", "controllers"),
    (r"\bRayleigh\b", "controller-a"),
    (r"\bWorthington\b", "controller-b"),
    (r"\bKelvin\b", "controller-c"),
    (r"\bTaylor\b", "controller-d"),
    # Stokes as host (careful: Navier-Stokes physics stays — only host-like phrases)
    (r"Stokes `sgit`", "private context-git"),
    (r"Stokes/`sgit`", "private context-git"),
    (r"Stokes context", "private context"),
    (r"on Stokes", "on the private compute host"),
    (r"Stokes is the HMAC mirror", "The lock mirror is the HMAC mirror"),
    (r"Stokes generation", "lock-mirror generation"),
    (r"dual-sync-main", "dual-sync"),
    (r"\bsgit\b", "context-git"),
    (r"comphy-state", "project-state"),
    (r"comphy-bot", "merge-bot"),
    (r"@merge-bot approve\?", "@merge-bot approve?"),
    (r"comphy-lab", "EXAMPLE_ORG"),
    (r"comphy-homeV0", "HOME_VOLUME"),
    (r"/Volumes/HOME_VOLUME/_Playground-controller-b", "~/Projects"),
    (r"~/Projects-cowork", "~/Projects"),
    (r"Projects-cowork", "Projects"),
    (r"cowork-os", "workspace-os"),
    (r"second-brain", "personal-notes"),
    (r"openclaw", "agent-runtime"),
    (r"~/\.agent-runtime/", "~/.local/share/agent-runtime/"),
    (r"python-worthy", "python-tooling"),
    (r"pip-worthy", "pip-tooling"),
    (r"worthy-def", "default-env"),
    (r"WorthyDB", "personal-db"),
    (r"query_second_brain_index\.py", "query_notes_index.py"),
    (r"research-compute-dispatch", "shared-compute-dispatch"),
    (r"Synosync", "NAS-mirror"),
    (r"/volume1/Dropbox", "/mnt/nas/Dropbox"),
    (r"/Users/vatsal", "/Users/USER"),
    (r"/Users/comphy-mac", "/Users/USER"),
    (r"vatsal@stokes-ts", "user@compute-host"),
    (r"/mnt/stokesInt0/", "/mnt/compute/"),
    (r"state\.comphy-lab\.org", "state.example.org"),
    (r"blogs-comphy-lab\.org", "blogs.example.org"),
    (r"comphy-lab\.org", "example.org"),
    (r"comphy-lab\.com", "example.com"),
    (r"vatsalsanjay\.com", "example-personal.com"),
    (r"sl2-vatsal-sanjays-projects\.vercel\.app", "project.vercel.app"),
    (r"origin\.cursor\.com/vatsalsy/", "origin.cursor.com/OWNER/"),
    (r"origin\.cursor\.com/vatsalSy/", "origin.cursor.com/OWNER/"),
    # Inline agent directives (personal names)
    (r"@Worthy:", "@Agent:"),
    (r"@Jarvis:", "@Agent:"),
    (r"@Taylor:", "@Agent:"),
    (r"@Worthy / @Taylor / @Jarvis", "@Agent"),
]

# Patterns that must not remain after scrub (physics Stokes/Navier-Stokes may still match \bStokes\b — use host-specific set in CI)
TEXT_EXTS = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".toml", ".txt", ".csv"}


def scrub_text(text: str) -> str:
    out = text
    for pat, repl in REPLACEMENTS:
        out = re.sub(pat, repl, out)
    # Soften remaining "Vatsal" references in prose (not URLs already handled)
    out = re.sub(r"\bVatsal\b", "the user", out)
    out = re.sub(r"\bVatsalSy\b", "OWNER", out)
    return out


def main() -> int:
    changed = 0
    for path in SKILLS.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTS and path.name not in {"SKILL.md", "Dockerfile"}:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = scrub_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"scrubbed {path.relative_to(ROOT)}")
    print(f"files_changed={changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
