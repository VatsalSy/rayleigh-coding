# Figma MCP config reference

Use this snippet to register the Figma MCP server. Configuration format varies by agent platform (e.g., `config.toml` for Codex, `mcp.json` for Claude Code). The key settings are the URL and bearer token.

```toml
[mcp_servers.figma]
url = "https://mcp.figma.com/mcp"
bearer_token_env_var = "FIGMA_OAUTH_TOKEN"
http_headers = { "X-Figma-Region" = "us-east-1" }
```

## Notes and options
- The bearer token must be available as `FIGMA_OAUTH_TOKEN` in the environment that launches the agent.
- Keep the region header aligned with your Figma region. If your org uses another region, update `X-Figma-Region` consistently.
- Harness note: OAuth on streamable HTTP may require a feature flag depending on the harness (e.g. `[features].rmcp_client = true` for Codex's `config.toml`). Check your harness's MCP docs.
- Optional per-server timeouts: `startup_timeout_sec` (default 10) and `tool_timeout_sec` (default 60) can be set inside `[mcp_servers.figma]` if needed.

## Env var setup (if missing)
- One-time set for current shell: `export FIGMA_OAUTH_TOKEN="<token>"`
- Persist for future sessions: add the export line to your shell profile (e.g., `~/.zshrc` or `~/.bashrc`), then restart the shell or your IDE.
- Verify before launching: `echo $FIGMA_OAUTH_TOKEN` should print a non-empty token.

## Setup + verification checklist
- Add the Figma MCP server to your harness's MCP configuration (e.g. `.claude/mcp.json` for Claude Code, or the equivalent for your harness).
- Restart the harness after updating config and env vars.
- Ask the agent to list Figma tools or run a simple call to confirm the server is reachable.

## Troubleshooting
- Token not picked up: Export `FIGMA_OAUTH_TOKEN` in the same shell that launches the agent, or add it to your shell profile and restart.
- OAuth errors: Verify MCP client features are enabled and the bearer token is valid. Tokens copied from Figma should not include surrounding quotes.
- Network/headers: Keep the `X-Figma-Region` header; if your org uses another region, update the header consistently across config and requests.

## Usage reminders
- The server is link-based: copy the Figma frame or layer link, then ask the MCP client to implement that URL. The client will extract the node ID from the link (it does not browse the page).
- If output feels generic, restate the project-specific rules from the main skill and ensure you follow the required flow (get_design_context → get_metadata if needed → get_screenshot).
