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
- `src/dm_companion/embeddings.py`, `vector_store.py`, `indexing.py` —
  semantic search; embeddings via OpenAI-compatible HTTP only (no SDK);
  storage pluggable (sqlite default, opensearch for sourcebook-scale corpora);
  main wiki namespace = campaign lore, all other sources = official/reference
- `skills/` — workflows as SKILL.md (canonical; `.claude/skills` and
  `.opencode/skill` are symlinks to it)

## Commands

```bash
uv sync --extra dev    # install
uv run pytest          # tests
uv run dmc check       # wiki connectivity (needs .env)
uv run dmc transcript <file.vtt> -o out.md
uv run dmc index       # refresh semantic lore index (needs EMBEDDINGS_* in .env)
uv run dmc ingest-book book.md --title "..."   # add official material to the index
```

## Rules

- Never add an LLM SDK dependency — provider choice belongs to the harness.
- New deterministic behavior gets tests; new judgment behavior gets a skill.
- Wiki safety invariants live in `WikiClient`, not in prompts: mandatory edit
  summaries, `DMC_READ_ONLY`, no delete capability. Don't weaken them.
- Secrets only in `.env` (gitignored). Personal roster in `campaign.yaml`
  (gitignored) and on the wiki as `Campaign:Roster`.
