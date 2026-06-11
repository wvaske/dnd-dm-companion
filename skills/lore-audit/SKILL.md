---
name: lore-audit
description: Audit the campaign wiki for inconsistencies, duplicates, orphan pages, missing categories, and broken conventions. Use when the DM asks to audit, clean up, or check the wiki's health.
---

# Audit the Campaign Wiki

Find problems and **report them — do not fix anything without explicit
approval of the specific change**. Lore "inconsistencies" are sometimes
deliberate (unreliable narrators, secrets the players haven't uncovered).

## Sweep

1. **Inventory**: `list_pages()` and the major categories (`Sessions`, `NPCs`,
   `Locations`, `Quests`, `Items`, `Factions`). Note pages in no category.
2. **Duplicates**: look for near-identical titles (e.g. "Leosin" vs "Leosin
   Erlanthar") and search snippets describing the same entity.
3. **Contradictions**: for major NPCs and quests, compare the entity page
   against mentions in session logs (`search_wiki("<name>")`). Status drift is
   the common failure: an NPC killed in Session 12 still "Active" on their page.
4. **Convention drift**: pages not using the standard templates, missing
   `[[links]]` for entity mentions, stale stub pages.

## Report

Group findings by severity:

- **Contradictions** (lore says two different things) — quote both sources
  with page titles.
- **Duplicates** — proposed merge direction and what content would move.
- **Hygiene** — uncategorized/orphan/stub pages, listed compactly.

For each finding propose a concrete fix. After DM approval, apply fixes with
edit summaries like `"Lore audit: <fix>"`, using `mode="replace"` only on
pages you have just read. Page merges: copy content into the surviving page
and turn the duplicate into a redirect (`#REDIRECT [[Target]]`) — never blank
a page without leaving a redirect.
