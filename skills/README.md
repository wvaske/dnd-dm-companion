# Skills: the companion's workflows

Each subdirectory holds one workflow as a `SKILL.md` — plain markdown with
YAML frontmatter (`name`, `description`). The agent harness loads the
description into context and reads the full skill when the workflow is
triggered.

This directory is the canonical location. Harnesses discover them via
symlinks committed in this repo:

- Claude Code: `.claude/skills/` → `skills/`
- opencode: `.opencode/skill/` → `skills/` (opencode reads the same SKILL.md
  format; check your opencode version's docs for the exact directory name)

## Why markdown, not TypeScript/JavaScript plugins

These workflows are **judgment-heavy**: deciding which colocated player said
a line, whether an innkeeper deserves a wiki page, whether two pages describe
the same NPC. That is instruction-following, and natural language is the
right encoding for it — a TS plugin would just wrap prose in code.

Code still has a place, split by determinism:

| Layer | Encoding | Examples |
|---|---|---|
| Judgment / workflow | `SKILL.md` markdown | speaker attribution, lore extraction, audit triage |
| Deterministic steps | Python (`dmc` CLI) | VTT parsing, connectivity checks, future bulk ops |
| Wiki access | Python MCP server | search/read/write tools |
| Harness event hooks | TS/JS plugin (only if needed) | e.g. auto-running something on session start in opencode |

Markdown skills are also portable across harnesses and editable by non-programmer
DMs — both matter for sharing this with other DM groups.

## Adding a skill

1. `mkdir skills/<name>` and write `skills/<name>/SKILL.md`.
2. Frontmatter `description` should say *when to use it*, not just what it is —
   that's what the agent matches against.
3. Keep deterministic steps as `dmc` commands or scripts the skill shells out
   to; keep judgment as instructions.
4. State the safety rules explicitly (what the skill must never do without
   asking the DM). Agents follow written guardrails; unwritten ones don't exist.
