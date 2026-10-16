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

## Wiki namespaces

| Namespace | ID | Visibility | Use |
|---|---|---|---|
| Main | 0 | players | campaign lore (player-facing canon) |
| `DM:` | 3000 | dm group only | spoilers, plot machinery, secret rules |
| `DM talk:` | 3001 | dm group only | dated change logs for `DM:` pages; superseded design |
| `Map:` | 2900 | players | interactive map data |
| `Map talk:` | 2901 | players | map-data discussion |

**`DM:` and `DM talk:` are both verified gated** (Lockdown; an anonymous API
read of either namespace returns `accessdenied`; verified 2026-10-16, probe
page `DM talk:Test Access Controls`). Write DM material to them freely, but if
wiki configuration ever changes, re-verify before writing secrets: fetch a
gated page anonymously (`curl "https://wiki.deeznuts.wiki/api.php?action=query&titles=DM:Home&prop=revisions&format=json"`
must return `accessdenied`).

Convention: a `DM:` page carries **current canon only** — when superseding
design, move the old text to the page's `DM talk:` counterpart as a dated
change log instead of leaving stale layers on the article.

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

## Writing style

Default to plain wiki style for all generated prose: complete sentences, plain
explanation, no literary effect. AI-isms are banned everywhere in the campaign,
including in-character text — no negation-first antithesis, no rule-of-three
tricolons, no aphoristic closers, no stacked em-dashes, no portentous
abstraction, no empty intensifiers. Distinct NPC voices come from human technique
(sentence shape, register, practical clutter), never from those tics. Use a
non-plain style only on explicit DM request. Full rules: `AGENT.md` and the
on-wiki `DM:Writing Style`.
