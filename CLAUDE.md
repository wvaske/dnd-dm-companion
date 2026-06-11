# D&D DM Companion — agent guide

MediaWiki is the source of truth for campaign lore; this repo is the tooling
around it. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before changing
structure — the layering (deterministic code / MCP tools / markdown skills)
is deliberate.

## Layout

- `src/dm_companion/wiki/` — the only wiki client; all writes need edit summaries
- `src/dm_companion/server.py` — MCP server (`dm-companion-mcp`); tools stay
  low-level, entity semantics belong in skills
- `src/dm_companion/transcripts/` + `cli.py` — deterministic Zoom VTT pipeline (`dmc`)
- `skills/` — workflows as SKILL.md (canonical; `.claude/skills` and
  `.opencode/skill` are symlinks to it)

## Commands

```bash
uv sync --extra dev    # install
uv run pytest          # tests
uv run dmc check       # wiki connectivity (needs .env)
uv run dmc transcript <file.vtt> -o out.md
```

## Rules

- Never add an LLM SDK dependency — provider choice belongs to the harness.
- New deterministic behavior gets tests; new judgment behavior gets a skill.
- Wiki safety invariants live in `WikiClient`, not in prompts: mandatory edit
  summaries, `DMC_READ_ONLY`, no delete capability. Don't weaken them.
- Secrets only in `.env` (gitignored). Personal roster in `campaign.yaml`
  (gitignored) and on the wiki as `Campaign:Roster`.
