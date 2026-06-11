# D&D DM Companion

An AI companion for running D&D campaigns. The campaign wiki (MediaWiki) is
the single source of truth for lore; Zoom session transcripts are the raw
input; an LLM agent — running in whatever harness and on whatever model
provider you prefer — does the work of turning sessions into lore and lore
into prep.

```
Zoom recording (.vtt)
      │  dmc transcript (deterministic parse/merge)
      ▼
clean markdown transcript
      │  ingest-session skill (attribution, extraction — LLM judgment)
      ▼
┌────────────────────────────┐      ┌──────────────────────────────┐
│  Agent harness (portal)    │ MCP  │  dm-companion-mcp server     │
│  opencode + openchamber,   │─────▶│  search/read/write tools     │──▶ MediaWiki
│  Claude Code, Claude       │      │  (mwclient, bot credentials) │    (source of truth)
│  Desktop — your choice     │      └──────────────────────────────┘
│  + skills/ (workflows)     │
└────────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design decisions and
their rationale.

## What's here

| Path | What it is |
|---|---|
| `src/dm_companion/wiki/` | MediaWiki client: search (CirrusSearch), read, write with mandatory edit summaries, read-only mode |
| `src/dm_companion/server.py` | MCP server exposing the wiki to any MCP host |
| `src/dm_companion/transcripts/` | Zoom WebVTT parser: cue merging, speaker stats, markdown output |
| `src/dm_companion/cli.py` | `dmc` CLI: `dmc transcript`, `dmc check` |
| `skills/` | Agent workflows as SKILL.md: `ingest-session`, `session-prep`, `lore-audit` |
| `.mcp.json`, `opencode.json` | MCP server registration for Claude Code and opencode |
| `campaign.example.yaml` | Roster template (Zoom account → player → character, colocation) |

## Setup

Requires Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/).

```bash
git clone <this repo> && cd dnd-dm-companion
uv sync

cp .env.example .env        # fill in wiki URL + bot credentials
cp campaign.example.yaml campaign.yaml   # fill in your table's roster

uv run dmc check            # verifies wiki connectivity + login
```

Create the bot password at `Special:BotPasswords` on your wiki with grants for
editing and creating pages — **not** deletion. The companion is designed to
never delete; the bot account shouldn't be able to even if prompted badly.

## Choose your portal

The companion has no UI of its own — any MCP-capable agent harness is the
portal, and the harness is also what gives you **model-provider choice**
(OpenRouter, Anthropic, a local LiteLLM server, Ollama, ...).

**opencode + openchamber** (recommended for a shareable web portal):
`opencode.json` in this repo registers the MCP server automatically; configure
your provider in opencode's own config, run openchamber for the web UI, and
start it from this directory.

**Claude Code**: `.mcp.json` registers the server; `.claude/skills` already
links to `skills/`. Just run `claude` from this directory.

**Claude Desktop**: add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dnd-wiki": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/dnd-dm-companion", "dm-companion-mcp"]
    }
  }
}
```

## A typical week

```bash
# After the session: drop the Zoom transcript in sessions/ (gitignored)
uv run dmc transcript sessions/session-25.vtt -o sessions/session-25.md

# In your agent portal:
#   "Ingest session 25 from sessions/session-25.md"
#       → ingest-session skill: attributes speakers, writes the Session 25
#         page, updates NPC/quest/location pages, reports what changed
#
# Before the next session:
#   "Help me prep the next session"
#       → session-prep skill: open threads, NPC reminders, three hooks
#
# Occasionally:
#   "Audit the wiki"
#       → lore-audit skill: contradictions, duplicates, orphan pages
```

## Extending the companion

New capabilities are **skills** (markdown workflows) plus, when needed, new
**MCP tools** (Python). See [skills/README.md](skills/README.md) for the
authoring guide and the rationale for markdown-over-code workflows.

```bash
uv run pytest          # run the test suite
```

## Safety rails

- Every wiki write requires an edit summary → full audit trail in page history.
- `DMC_READ_ONLY=1` blocks all writes at the client level (test new
  models/skills against the real wiki without risk).
- `mode="create"` write mode fails on existing pages — skills use it for new
  entities so nothing gets silently overwritten.
- MediaWiki page history is the undo button for everything else.
