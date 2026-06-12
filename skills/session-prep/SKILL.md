---
name: session-prep
description: Build a prep document for the next D&D session from current wiki state - open quests, active NPCs, unresolved threads, and suggested hooks. Use when the DM asks to prep, plan, or brainstorm the next session.
---

# Prep the Next Session

Produce a one-page prep document grounded in the wiki — never invent
established lore; flag gaps instead.

## Gather

1. `list_pages(prefix="Session")` → read the **two most recent** session logs.
2. From the latest log, note where the party is and what they said they'd do next.
3. Pull open threads:
   - `search_wiki("incategory:Quests")` and read quests not marked complete
   - NPCs in or near the party's current location: `search_wiki("incategory:NPCs <location>")`
   - Recent wiki edits (`recent_changes`) — the DM may have planted new material since the session.
4. Go beyond keywords with `find_related_lore`: query it with the session's
   themes ("betrayal in the merchant guild", "the black dragon mask") to
   surface forgotten lore that keyword search misses. If it reports an empty
   or stale index, suggest the DM run `dmc index`.

## Build the prep doc

Present in chat (and save to the wiki as `Prep:Session <N>` only if asked):

- **Where we left off** — 3 sentences.
- **Promises made to players** — things the table expects to happen.
- **Open threads** — each with current state and 1–2 ways it could surface
  this session.
- **NPCs likely on stage** — name, motivation, what they want *from the party
  right now*, a voice/mannerism reminder.
- **Three hooks** — small / medium / arc-advancing. Hooks must grow out of
  established lore; cite the wiki page each one builds on.
- **Loose ends & contradictions** — anything inconsistent you noticed while
  reading (don't fix it here; just flag it for the lore-audit workflow).

Suggestions are the DM's to take or leave — offer options, not a script.
