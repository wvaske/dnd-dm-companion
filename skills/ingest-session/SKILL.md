---
name: ingest-session
description: Turn a Zoom session recording transcript (.vtt) into campaign lore - attribute speakers, write the session log, and update NPC/location/quest pages on the wiki. Use when the DM provides a new session transcript or asks to ingest/process a session.
---

# Ingest a Session Transcript

Convert a raw Zoom transcript into durable campaign lore on the wiki. This is
the core workflow of the companion. Work in four phases and report at the end.

## Phase 1 — Convert (deterministic, do not do this by hand)

```bash
uv run dmc transcript <path-to.vtt> -o sessions/session-<N>.md
```

The output header lists Zoom accounts and talk time. Read the markdown
transcript before going further. If the session number `<N>` is unknown,
check the wiki: `list_pages(prefix="Session")`, parse the numbers, and take
the highest + 1. (Titles come back alphabetically — "Session 9" sorts *after*
"Session 10" — so compare numerically, never take the last list entry.)

## Phase 2 — Attribute speakers

Zoom labels identify **microphones, not people**. Some players sit together
and share one account (usually the DM's or a host player's).

1. Read the roster from the wiki page `Campaign:Roster` (fall back to a local
   `campaign.yaml` if the page doesn't exist). It maps Zoom accounts →
   people → characters, and flags who is colocated.
2. For accounts mapped to a single person, attribution is mechanical.
3. For shared accounts, infer the actual speaker from context:
   - The DM narrates, describes scenes, voices NPCs, and asks "what do you do?"
   - Players speak in first person as their characters or refer to their own
     sheets ("I rolled a 14", "my character would...")
   - Characters address each other by name — use that to anchor identities.
   - Distinguish in-character speech from table talk; table talk is not lore.
4. Mark any utterance you cannot confidently attribute as `[uncertain]` rather
   than guessing. Never invent attribution for plot-significant statements.

## Phase 3 — Extract lore

From the attributed transcript, collect:

- **Recap**: 2–4 paragraph narrative summary of what happened, in-world.
- **Entities**: every NPC, location, faction, item, and quest mentioned.
  For each: new or existing? what changed this session?
- **Creatures**: every *kind* of monster the party encountered or fought (the
  type, not the named individual — a named wyrm is an NPC). Note what the party
  learned about each: what hurt it, what it shrugged off, what it could do.
- **Quest movement**: threads opened, advanced, or closed.
- **Loot & rewards**, **memorable quotes** (attributed), **DM rulings** worth
  remembering.

Only in-world events become lore. Scheduling chatter, rules debates, and
jokes stay out (a single Quotes section is the exception).

## Phase 4 — Write to the wiki

Search before you write — entities often already exist under a different
name ("the innkeeper" might be page `Elmar Barthen`).

1. Create `Session <N>` with `write_page(mode="create")` using the structure
   below. If it already exists, stop and ask the DM instead of overwriting.
2. Link the new session on the **`Session Logs`** index page
   (`read_page`, then `mode="replace"`). Add a bold, linked bullet under the
   current story-arc heading, matching the one-sentence style and dash format
   of the existing entries:
   `* '''[[Session <N> - <Title>]]''' – <one-line summary>`. A freshly created
   session page is invisible to readers until it is listed here, so this step
   is not optional. While you're there, add any earlier sessions that are
   missing from the index.
3. For each entity:
   - existing page → `read_page`, then update with `mode="replace"` (preserve
     everything you aren't changing) or add a dated note with `mode="append"`.
   - genuinely new → `mode="create"`, following the wiki's template and
     category conventions (read a similar page first to copy its shape).
4. For each new **kind** of creature the party met or fought, add or update its
   Bestiary dossier and the `Bestiary` index — follow the **update-bestiary**
   skill (`{{Monster Lore}}` dossier, hierarchy wiring, open-licensed image,
   index entry). Named individual monsters are NPC pages, not bestiary types.
5. Every edit summary references the session: `"Session <N> ingest: <what changed>"`.
6. Link aggressively: `[[Page Name]]` for every entity mention in the session log.
7. If the DM provided images (maps, handouts, token art), upload them with
   `upload_image` — summary like `"Session <N> ingest: <what it is>"`, a
   description with a category (e.g. `[[Category:Maps]]`), then embed via
   `[[File:<name>|thumb|<caption>]]` on the relevant page. If the upload
   returns a Warning (usually a duplicate), report it instead of forcing.

### Session page structure

```wikitext
{{Session
| number = <N>
| date = <real-world date>
| location = [[<primary in-world location>]]
}}

== Summary ==
<recap>

== Events ==
<bulleted chronology>

== NPCs Encountered ==
* [[Name]] — <role this session>

== Quests ==
* [[Quest Name]] — <advanced/opened/closed: detail>

== Loot ==
== Quotes ==

[[Category:Sessions]]
```

(If the wiki has no `{{Session}}` template yet, check how previous session
pages are formatted and match them.)

## Report

Finish with a summary for the DM: pages created, pages edited (with edit
summaries), the `Session Logs` index entry added, any Bestiary dossiers and
index entries added, images uploaded, attribution uncertainties flagged in
Phase 2, and anything that needs a human decision. Remind the DM to run
`uv run dmc index` so semantic search picks up the new lore. Never delete or
blank a page in this workflow.
