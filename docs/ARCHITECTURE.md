# Architecture

This document records the opinionated choices and why they were made, so
future capabilities get added in the right place.

## The shape of the system

Three layers, separated by what kind of correctness they need:

1. **Deterministic code** (`src/dm_companion/`, `dmc` CLI) — things that must
   be exactly right every time: VTT parsing, wiki API calls, write safety
   rules. Python, tested.
2. **Tools** (`dm-companion-mcp`) — the wiki exposed over MCP. The narrow
   waist of the system: every harness, model, and skill goes through the same
   seven tools, so safety rules (edit summaries, read-only mode, create-only
   writes) are enforced once, in code, not per-prompt.
3. **Workflows** (`skills/*/SKILL.md`) — judgment-heavy procedures expressed
   as instructions: speaker attribution, lore extraction, audit triage,
   session prep. Markdown, versioned in git alongside the code.

The **agent harness is deliberately not part of this repo.** opencode,
Claude Code, and Claude Desktop all speak MCP and all read markdown skills.
The harness is where the user picks their model provider, their UI, and their
permission model — all things this project should not rebuild.

## Decision log

### Wiki access: MCP server, Python, mwclient

The previous generation of this project had three parallel wiki integrations
(FastAPI middleware for ChatGPT, a TypeScript MCP server for Claude Desktop,
ad-hoc Python scripts). Each had its own auth handling and its own bugs.

Now there is **one** wiki client (`WikiClient`) and one server. Python over
TypeScript because mwclient is the most mature MediaWiki client library, the
transcript pipeline is Python anyway, and one language keeps the project
maintainable by one person. The old FastAPI middleware can keep running
unchanged for ChatGPT users; it's orthogonal.

The MCP tools are intentionally low-level (search/read/write/list/history)
rather than entity-specific (`create_npc`, `update_quest`). Entity semantics
live in skills, where they can evolve per-campaign without code changes.
Add a new tool only when a capability *can't* be composed from the existing
ones (e.g. file upload, semantic search — see Future).

### Portal: the harness is the portal

Requirement 3 (a portal for an LLM that can search and update the wiki) and
requirement 4 (opencode/openchamber, but direct MediaWiki integration
preferred) are both satisfied by the same move: **openchamber is the UI,
opencode is the agent runtime, and the MCP server is the direct MediaWiki
integration.** There is no middleman API between the LLM and the wiki — the
agent calls `write_page` and mwclient hits `api.php`.

Because the integration is MCP rather than an opencode plugin, switching or
adding harnesses costs one config file (`.mcp.json` for Claude Code is
already in the repo, next to `opencode.json`).

### Provider flexibility: delegated to the harness

Requirement 5 (OpenRouter / Anthropic / LiteLLM / Ollama) is configuration in
opencode (or Claude Code), not code in this repo. Nothing in this project
imports an LLM SDK. This is deliberate: a provider-routing layer here would
duplicate what the harness already does well, and would have to chase every
provider API change.

If a **headless** pipeline is ever needed (e.g. cron job auto-ingesting
transcripts without a human at the portal), the right tool is the harness's
non-interactive mode (`opencode run`, `claude -p`) driving the same skills and
MCP tools — still no LLM SDK in this repo.

### Workflows: SKILL.md markdown, not TypeScript/JavaScript plugins

The question was whether to define workflows in TS/JS (like opencode plugins
or Claude Code plugins). Decision: **markdown skills as the primary workflow
format; code only below the judgment line.**

Reasoning:

- The hard parts of these workflows are judgment calls: *which colocated
  player said this line, is this innkeeper page-worthy, do these two pages
  describe the same NPC.* Encoding judgment in TS means embedding prompt
  strings in code — all of the indirection, none of the type safety, since
  the types end at the LLM boundary anyway.
- Markdown skills are portable across harnesses (opencode and Claude Code
  both read the same SKILL.md format). A TS plugin locks workflows to one
  harness's plugin API — directly against the goal of sharing this with
  other DMs, who will arrive with different setups.
- Non-programmer DMs can read and edit a SKILL.md. That's the difference
  between a tool other DMs *use* and one they *adapt*.
- Where determinism matters inside a workflow, the skill shells out to the
  `dmc` CLI (e.g. VTT parsing). The split is: **prose decides, code executes.**

TS/JS plugins remain the right answer for one narrow case: harness *event
hooks* (e.g. "when a session starts in opencode, do X"). If that need
appears, write the thinnest possible plugin that triggers a skill, and keep
the workflow itself in markdown.

### Transcripts: deterministic parse, LLM attribution

Zoom's VTT identifies *microphones*, not people (requirement: colocated
players share accounts). So the pipeline splits exactly at that line:

- `dmc transcript` (code): parse cues, merge same-speaker runs, compute talk
  stats, emit clean markdown. Testable, instant, never hallucinates.
- `ingest-session` (skill): attribute utterances to people/characters using
  the roster (`Campaign:Roster` wiki page / `campaign.yaml`) plus context
  (DM narration patterns, characters addressing each other, first-person
  sheet talk). Uncertainty is flagged, never papered over.

Raw recordings and transcripts stay out of git (`sessions/` is ignored);
the wiki is where session knowledge persists.

### Semantic search: local index, provider-agnostic embeddings

CirrusSearch answers "which pages contain these words"; prep questions are
often "which pages are *about* this" — so `find_related_lore` is a separate,
embeddings-based tool rather than a CirrusSearch feature.

Two choices worth recording:

- **Embeddings over plain HTTP** (`embeddings.py`): any OpenAI-compatible
  `/v1/embeddings` endpoint — Ollama locally, LiteLLM, OpenRouter, OpenAI.
  This keeps the no-LLM-SDK rule intact and provider choice with the user,
  same as chat models. Configured by `EMBEDDINGS_URL`/`EMBEDDINGS_MODEL`.
- **Local SQLite index + in-process cosine** (`lore_index.py`), *not*
  OpenSearch k-NN, even though the wiki's OpenSearch could do it. At
  campaign-wiki scale (hundreds of pages) brute force is instantaneous, the
  index is derived data anyone can rebuild with `dmc index`, and other DMs
  adopting this project don't need an OpenSearch deployment with the k-NN
  plugin. Revisit only if a wiki reaches tens of thousands of pages.

Indexing (`dmc index`) is deterministic-side, incremental by content hash,
one vector per page (title prepended, truncated at 6k chars). It's a CLI
command, not an MCP tool: first runs take minutes (network + embedding), which
fits a shell command better than a tool call inside a chat turn.

### Image upload: same rails as page writes

`upload_image` (tool) → `WikiClient.upload_image()` follows the write
invariants: blocked by `DMC_READ_ONLY`, mandatory summary (the upload log
comment), and an image-extension allowlist in code. MediaWiki duplicate/
re-upload warnings are surfaced to the caller instead of auto-overridden —
the tool's docstring tells the agent to report warnings to the DM rather than
retry with `ignore_warnings=True` on its own. The bot password needs the
upload grant (still not delete).

### Wiki as source of truth — consequences

- The roster, templates, and conventions live **on the wiki**, not in this
  repo, so they're editable by the table and visible to the agent through the
  same tools as everything else.
- The companion never deletes pages, and the bot password shouldn't have the
  delete grant. Merges become redirects. MediaWiki revision history is the
  undo mechanism, which is why edit summaries are mandatory at the client
  level.
- Search is CirrusSearch (already deployed): skills are written assuming
  full-text search with `incategory:`/`intitle:`/`prefix:` filters.

## Adding a capability — decision guide

| You want to... | Add a... |
|---|---|
| New DM workflow (e.g. "generate a shop inventory", "track initiative") | skill (`skills/<name>/SKILL.md`) |
| New deterministic transform (e.g. parse a different transcript format) | `dmc` subcommand + tests |
| New wiki primitive that can't be composed from existing tools (e.g. image upload, move page) | MCP tool in `server.py` + method on `WikiClient` |
| React to a harness event | thin harness plugin that invokes a skill |
| Support another knowledge store | new client module behind the same MCP tool names |

## Future (in rough order of value)

- **`Campaign:Roster` bootstrap skill** — interview the DM and write the
  roster page.
- **Headless ingest** — cron/watch folder → `claude -p` / `opencode run`
  invoking ingest-session; needs a review step before writes (or
  `DMC_READ_ONLY` + a diff-for-approval flow). Could also auto-run
  `dmc index` after ingest.
- **Whisper-based diarization** — if Zoom attribution quality disappoints,
  re-transcribe audio with speaker diarization and feed that to the same
  ingest skill.
- **Per-section embeddings** — the lore index stores one vector per page;
  if long pages (session logs) dilute retrieval quality, split on wikitext
  `==` headings.
