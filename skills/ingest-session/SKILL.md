---
name: ingest-session
description: Turn a Zoom session recording transcript (.vtt) into campaign lore - attribute speakers, write the session log, and update NPC/location/quest pages on the wiki. Use when the DM provides a new session transcript or asks to ingest/process a session.
---

# Ingest a Session Transcript

Convert a raw session transcript into durable campaign lore on the wiki. This is
the core workflow of the companion.

The guiding standard is **completeness, not just comprehensiveness**. A
*comprehensive* log captures the spine of the session — the arcs, the fights,
the quests. A *complete* log also captures the small, texture-rich **beats**
that give the world life: an item that gains a voice, a one-line character
decision, a piece of foreshadowing, a running gag that has become canon, a
permanent mechanical change. Sessions routinely run 5+ hours, and a single
summarizing read **will** flatten these beats away. So this workflow runs in
**two extraction passes** (spine, then texture) and treats **routing each beat
to the entity page that owns it** as a first-class step — not just dumping
everything into the session log.

Work through the phases below and report at the end. **Never delete or blank a
page.** Corrections are edits; merges become redirects. Every edit summary
references the session: `"Session <N> ingest: <what changed>"`.

## Phase 1 — Convert (deterministic, do not do this by hand)

```bash
uv run dmc transcript <path-to.vtt> -o sessions/session-<N>.md
```

The output header lists Zoom accounts and talk time. If the session number
`<N>` is unknown, check the wiki: `list_pages(prefix="Session")`, parse the
numbers, and take the highest + 1. (Titles come back alphabetically — "Session
9" sorts *after* "Session 10" — so compare numerically, never take the last
list entry.) If a session was played across **two sittings**, treat both
transcripts as one session and cover both in one page (label the parts).

**Keep the giant transcript out of your main context.** Delegate each reading
pass below to a subagent that returns a structured report; the orchestrator
works from the reports, not the raw transcript. Give every subagent the roster
(Phase 2) and a "transcription garbles proper nouns — flag odd ones with a
best guess" caution.

## Phase 2 — Attribute speakers

Zoom labels identify **microphones, not people**. Some players sit together and
share one account, one player may run an absent player's character, and a
single person may appear under two device labels.

1. Read the roster from the wiki page `Campaign:Roster` (fall back to a local
   `campaign.yaml`). It maps Zoom accounts → people → characters and flags who
   is colocated.
2. For accounts mapped to a single person, attribution is mechanical.
3. For shared/ambiguous accounts, infer the speaker from context: the DM
   narrates, voices NPCs, and asks "what do you do?"; players speak in first
   person and cite their own sheets/rolls; characters address each other by
   name; in-character speech ≠ table talk.
4. **Establish presence/absence explicitly** — who was there, who was absent,
   and who covered an absent character. Record it; it changes attribution.
5. Mark anything you cannot confidently attribute as `[uncertain]`. Never
   invent attribution for plot-significant statements. Low-quality recordings
   (e.g. phone audio with only "Speaker 0/1" diarization) get **no** committed
   line-level player attribution — attribute by content and flag confidence.

## Phase 3 — Extract lore (TWO passes)

Run both. Pass A and Pass B can be two separate subagent reads of the same
transcript, or one subagent explicitly instructed to deliver both — but the
texture pass must be its own deliberate step, never an afterthought to the
summary.

### Pass A — the spine (comprehensive)

Collect the arc-level lore:

- **Recap**: a 2–4 paragraph in-world narrative of what happened.
- **Chronology**: the ordered beats of the session, enough to write prose.
- **Entities**: every NPC, location, faction, item, and quest. For each: new or
  existing? what changed this session?
- **Creatures**: every *kind* of monster encountered or fought (the type, not
  the named individual — a named wyrm is an NPC). Note what the party learned:
  what hurt it, what it shrugged off, what it could do.
- **Quest movement**: threads opened, advanced, or closed (see Phase 4's quest
  step for exactly what to capture — quest giver, objective, status change,
  sessions, and any new hooks).
- **Loot & rewards**, **DM rulings** worth remembering, **memorable quotes**
  (attributed, with confidence).

### Pass B — the texture (completeness)

Re-read hunting **specifically** for the small beats a summary drops. Do **not**
re-summarize. For every beat found, name the **target entity page** it belongs
on (not just the session log). Hunt this checklist:

- **Items, familiars & companions gaining character** — sentience, a "voice",
  will, warnings, quirks, or naming (e.g. an artifact that speaks to its bearer;
  a familiar with a personality; a weapon that hungers). → the item/companion page.
- **Character-defining moments** — a single decision, oath, fear, cruelty,
  mercy, or line that reveals who a PC or NPC *is*. → the character page.
- **Foreshadowing, prophecy, and unresolved hooks** — riddles, omens, names
  dropped, threats deferred. → a quest/lore page (create a stub if needed) AND
  the Quest Leads list (Phase 4 quest step).
- **Relationship shifts** — an alliance, betrayal, debt, grudge, or flirtation
  between named parties. → both parties' pages.
- **Permanent changes** — a stat/ability gained or lost, an attunement that
  can't be undone, a body altered, a death that sticks. → the character/item page.
- **World/lore reveals** — cosmology, history, faction motives, the *why* behind
  something. → the relevant location/faction/lore page.
- **Recurring gags that have become canon** — a bit the table treats as real
  in-world. → the relevant page; keep it light but record it.
- **DM rulings that became standing campaign rules** — house rules that will
  recur. → the session page (and the `House Rules` page).
- **Evolving per-character mechanics, especially [[Tempered Soul]] usage** —
  some abilities are narrative by design and meant to deepen over the campaign.
  Tempered Soul in particular: each time a PC spends it, the player narrates the
  **emotion, memory, or instinct** that fuels the surge. Capture, per use: which
  PC, what the roll was for, and the **verbatim emotion/memory they narrated**.
  → the `Tempered Soul/Usage Log` wiki page (one row per use per character:
  what was empowered, the feeling, a verbatim quote, the outcome), so the
  mechanic's evolution is visible across sessions, not lost each week.
  Treat any similarly roleplay-forward, evolving feature the same way.

Separate genuine in-world lore from table talk, scheduling, and rules debates
(a single Quotes section is the only exception). Flag uncertainty; never assert
a garbled name without verifying it (Phase 4).

**DM-only information goes in the `DM:` namespace.** Anything the players do not
know — hidden mechanics, secret NPC motives, plot twists, the analysis of how an
evolving feat is trending — belongs on a `DM:`-prefixed page (which is access-
controlled), never on a player-visible page behind a styled "DM box." A box
hides nothing; the namespace does. Keep the player-safe record (e.g. a usage log
of things said at the table) public, and put the secret layer in `DM:`.

## Phase 4 — Write & integrate (the routing step matters)

**Search before you write** — entities often already exist under a different or
correctly-spelled name ("the innkeeper" might be `Elmar Barthen`; a garbled
"Solera" might be `Lady Calera`). Verify every proper noun against existing
pages before creating anything. When a name is genuinely unverifiable, prefer
the most conservative edit (a flagged note over a new asserted "fact").

1. **Write the session page** using the structure in the next section. If it
   already exists, enrich it — preserve what you aren't changing, and bring it
   up to the template (prose Detailed Chronology, not bare bullets).
2. **Route every Pass-B beat to its home entity page.** This is the step that
   makes the wiki complete: the Eye that spoke goes on the Eye's page; the oath
   sworn goes on the character's page. A beat that lives only in the session log
   is only half-recorded. For each target page: `read_page`, then update
   (`mode="replace"`, preserving everything else) or append a dated note.
3. **Maintain the quest tracker.** Quests are tracked in three places that must
   stay in sync — keep them aligned every session:
   - The **quest's own page** (`[[Template:Quest]]`): update its Status and
     append the session's progress. When a quest finishes, set Status to
     **Completed**, add outcome/rewards, and switch its category from
     `[[Category:Active Quests]]` to `[[Category:Completed Quests]]`.
   - The **`Quests`** tracker page: move the row between the Active and
     Completed tables, and update the Quest Statistics counts.
   - The **`Main Page`** "Active Quests" table and "Quest Leads" list (the
     player-facing front door).
   Classify each thread: **Active** (in progress), **Completed** (resolved), or
   a **Quest Lead / hook** (a rumor, omen, or deferred thread not yet a full
   quest — every Pass-B foreshadowing beat becomes a Quest Lead here, and gets a
   stub quest/lore page if substantial). A new quest needs a page from
   `[[Template:Quest]]` (giver, objective, locations/factions, status, rewards,
   related quests, sessions).
   **Category-link gotcha:** when you *mention* a category in prose or
   instructions, always escape it as `[[:Category:Foo]]` (leading colon). An
   unescaped `[[Category:Foo]]` silently files the current page *into* that
   category — on a category page that creates self-loops and infinite
   subcategory nesting.
4. **Link the session on the `Session Logs` index** — a bold, linked bullet
   under the current story-arc heading, matching the existing one-sentence dash
   style. A session page is invisible to readers until it is listed here.
5. **Reconcile duplicates** — if you find stub/alternate pages for the same
   session or entity ("- Unknown", "- Untitled", a dated-suffix variant, an
   alternate spelling), consolidate to the canonical page (the one in
   `Session Logs` / the roster) and turn the others into `#REDIRECT`s. Never
   delete — redirect.
6. **Bestiary**: for each new *kind* of creature, add/update its dossier and the
   `Bestiary` index per the **update-bestiary** skill (`{{Monster Lore}}`,
   hierarchy wiring, open-licensed image, index entry). Named individuals are
   NPC pages, not bestiary types.
7. **Images**: if the DM provided maps/handouts/token art, `upload_image`
   (summary references the session; description carries a category), then embed
   via `[[File:<name>|thumb|<caption>]]`. Report any upload Warning instead of
   forcing it.
8. **Link aggressively** — `[[Page Name]]` for every entity mention.
9. Every edit summary references the session.

### Session page structure (enforce this shape)

Match the established wiki house style — a prose page, not bare lists. If a
`{{Session}}` template exists, use it; otherwise match recent session pages.

```wikitext
== Session <N> - <Title> (<date or dates>) ==
''(If played across two sittings, note both dates here.)''

== Summary ==
<2–4 paragraph in-world recap — the spine.>

== Detailed Chronology ==
=== <Scene/beat heading> ===
<Prose. Walk the session scene by scene in full sentences — NOT bullets.
Weave the Pass-B texture beats into the narrative where they happened. This is
the backbone of the page; the sections below are a reference index.>
=== <Next scene> ===
<...>

== Notable Characters ==      <!-- PCs (player), NPCs (role); link each -->
== Locations ==
== Factions ==
== Items ==                    <!-- gained, used, lost; link each -->
== Creatures ==               <!-- kinds; link Bestiary dossiers -->
== Quests ==                  <!-- opened / advanced / closed; mirror to the Quests tracker -->
== Quotes ==                  <!-- attributed, with confidence if uncertain -->
== Session End ==             <!-- cliffhanger / where things stand -->

[[Category:Sessions]] [[Category:<current arc>]]
```

The **Detailed Chronology in prose is mandatory** — a session whose events are
only a bullet list is not finished. Bullets are fine inside the reference
sections, never as the substitute for the narrative.

## Phase 5 — Verify completeness (self-check before reporting)

Before finishing, confirm:

- [ ] The session page has a prose **Detailed Chronology**, not just bullets.
- [ ] **Every Pass-B beat landed on its target entity page**, not only the log.
- [ ] **Tempered Soul (and any evolving per-character mechanic) usage is logged
      on each PC's page** with the narrated emotion/memory.
- [ ] **The quest tracker is in sync** — quest pages, the `Quests` page, and the
      `Main Page` Active Quests + Quest Leads all reflect this session's opened /
      advanced / closed threads, with categories switched for any completions.
- [ ] Every new significant entity has a page; every garbled name was verified
      against the wiki; duplicates were redirected.
- [ ] New creature kinds are in the Bestiary.
- [ ] The session is listed on `Session Logs`.
- [ ] Attribution uncertainties and any low-confidence guesses are flagged.

If anything is unchecked, it isn't done.

## Report

Finish with a summary for the DM: pages created, pages edited (with edit
summaries), the texture beats routed and where, the quest-tracker changes
(active/completed/new leads), the `Session Logs` entry, Bestiary additions,
images uploaded, attribution/presence notes, and anything needing a human
decision. Remind the DM to run `uv run dmc index` so semantic search picks up
the new lore. Never delete or blank a page in this workflow.
