# MCP Email Server (Option A)

A standalone Model Context Protocol (MCP) server that exposes your email data to MCP-compatible AI clients (e.g., Claude Desktop). Your existing web UI/backend remain unchanged.

## What it provides

Tools:
- `search_emails(query, recipient?, limit=5, since_days=30)` → returns concise email summaries
- `get_email_details(email_id)` → returns full body + metadata
- `summarize_thread(thread_ids[])` → returns a compiled thread context

All tools are read-only and scoped by optional `recipient` (recommended). You can set a default via `MCP_DEFAULT_RECIPIENT`.

## Run locally (Windows PowerShell)

```powershell
# From repo root
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r mcp_server\requirements.txt

# Point to your Postgres (compose exposes 5432 on localhost)
$env:MCP_DATABASE_URL = "postgresql+asyncpg://mailuser:mailpass@localhost:5432/maildb"

# Optional: set a default user scope
$env:MCP_DEFAULT_RECIPIENT = "you@example.com"

# Start the MCP server (normally launched by a client like Claude Desktop)
python -m mcp_server.server
```

> Note: This process waits for an MCP client over stdio and won’t print output by itself. Stop with Ctrl+C when done.

## Use with Claude Desktop

Edit (or create) `~/.claude/config.json` and add:

```json
{
  "mcpServers": {
    "emails": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MCP_DATABASE_URL": "postgresql+asyncpg://mailuser:mailpass@localhost:5432/maildb",
        "MCP_DEFAULT_RECIPIENT": "you@example.com"
      }
    }
  }
}
```

Restart Claude Desktop. You should see the `emails` server appear in the tools list. Try prompts like:
- "Using the emails server, search for nginx errors in the last week"
- "Get email details for id 42"
- "Summarize this thread: [12, 15, 18]"

## Docker (optional)
You generally don’t need Docker for the MCP server, but you can add it as a separate service if desired. Running it locally is recommended so desktop apps can launch it via stdio.

## Security
- The server is read-only and respects an optional `recipient` filter to avoid cross-user exposure.
- If you expose it beyond localhost, ensure you manage credentials and network boundaries appropriately.

## Troubleshooting
- `ImportError: mcp`: Install requirements into your active venv: `pip install -r mcp_server/requirements.txt`
- `psycopg/asyncpg` errors: Ensure Postgres is running (`docker compose ps`) and port 5432 is reachable.
- No results: Confirm your `MCP_DATABASE_URL` is correct and that emails exist in `messages` table.
