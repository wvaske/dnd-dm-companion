---
name: canon-check
description: Compare campaign lore against official D&D source material - find where the campaign diverges from published canon. Use when the DM asks how their version compares to official lore, whether something is canon, or to canon-check an NPC, location, or event.
---

# Check Campaign Lore Against Official Canon

Compare what the table has established against what the books say, and report
the differences. **Divergence is not error** — homebrew is the point of a
campaign. Your job is to make divergence *visible* so the DM can confirm it's
intentional, never to "correct" the wiki toward canon.

## Prerequisites

Official material must be in the lore index: either ingested sourcebooks
(`uv run dmc ingest-book`) or reference wiki namespaces. If
`find_related_lore(scope="official")` comes back empty, tell the DM what's
missing and how to add it; don't substitute your own training-data knowledge
of D&D lore as if it were the indexed source — quote only what the index
returns.

## For a single entity (NPC, location, faction, item, deity)

1. Read the campaign version: `read_page` on the entity, plus
   `search_wiki("<name>")` for session-log mentions that may contradict the
   entity page itself.
2. Pull the official version: `find_related_lore("<name and identifying
   details>", scope="official")` — run 2–3 phrasings (the name alone, the
   name plus role, distinctive events). Read the matching chunks carefully.
3. Compare on the facts that matter at the table: identity/role, allegiances,
   location, timeline, abilities, fate (alive/dead/imprisoned), and
   relationships to other canon entities.

## For a sweep ("how far have we drifted from the module?")

Work through `list_category("NPCs")` and `list_category("Locations")` for
entities that plausibly exist in published material (skip obvious original
creations), applying the single-entity check briefly to each. Batch your
report rather than interrupting per entity.

## Report

For each entity, classify each difference:

- **Matches canon** — note it briefly, no action.
- **Diverges** — quote both versions (campaign wiki page vs. official chunk,
  citing the book/section from the match title). Ask: intentional?
- **Campaign-only** — exists in the campaign with no official counterpart.
  That's homebrew, not a finding; list it only if the DM asked for a full map.
- **Underspecified** — canon has rich material the campaign hasn't used yet.
  These are *opportunities*, worth surfacing for prep.

If the DM confirms a divergence is intentional, offer to record it on the
entity's wiki page in a `== Canon notes ==` section (edit summary:
`"Canon check: documented intentional divergence from <book>"`), so future
checks and future-you know it was a choice.
