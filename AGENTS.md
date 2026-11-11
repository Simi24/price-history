# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Gemini CLI, Cursor, Copilot...) working with this repository.

## What this is
`price-history`: price history by store from Google Shopping with a deal verdict via SerpApi, for LLM agents. A Python CLI with compact text or JSON output, an agent skill in
`skills/price-history/SKILL.md` (Agent Skills format), and an optional MCP server.

## Setting it up for a user
1. **Install the CLI** (needs [uv](https://docs.astral.sh/uv/)): `uv tool install git+https://github.com/Simi24/price-history`. Ask before installing.
2. **Install the skill** in the agent's skills folder, e.g. `~/.claude/skills/price-history` for Claude Code: copy or symlink
   `skills/price-history`. Agents without skills support can read `skills/price-history/SKILL.md` directly.
3. **SerpApi key** (free plan: 250 searches a month). The account must be created by the person: sign-up needs email verification. Ask them to run `price-history setup` in their own terminal (it opens the sign-up page, reads the key without echoing it, checks it and saves it to `~/.config/serpapi/key`, shared with other SerpApi tools). Non-interactive alternatives: `price-history setup --key <key>` or the `SERPAPI_KEY` environment variable. Never print the key or commit it.
4. **Check**: `price-history credits`.

Agents without a shell can use the MCP server instead: see "MCP server" in README.md for client configurations.

## Developing
```bash
uv sync
uv run pytest            # offline, against tests/fixtures/
uv run ruff check . && uv run ruff format .
```
Keep code, comments and docs in English. Never commit API keys or personal data in fixtures.
