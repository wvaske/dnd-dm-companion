---
name: update-bestiary
description: Add a creature to the campaign Bestiary as a Monster Lore dossier (or update an existing one), wire it into the creature hierarchy, find an open-licensed image, and keep the Bestiary index page in sync. Use when the party encounters or fights a new kind of creature, when the DM asks to add or update a monster or the bestiary, or after a session introduces new creature types.
---

# Add a Creature to the Bestiary

The **Bestiary** is the players' field reference: Harper "field dossiers" on
every *kind* of creature the party has faced, written in qualities and tactics,
**never in numbers**. The model entry is `Adult White Dragon`; the index page is
`Bestiary` (linked from the `Main Page`). Work the steps below, then report.

## Phase 1 — Decide whether it gets a page

A bestiary dossier is for a creature **type** the party has encountered or fought
and would gain from tracking (vulnerabilities, resistances, abilities, tactics).
Prioritise recurring or dangerous kinds.

- **Not** a type page for a *named individual* monster (a specific dragon, a
  unique villain) — those are NPC pages under `Category:NPCs`. A singular
  creature the party actually fought (e.g. the `Mind Gobbler`) may still get a
  dossier, but most named wyrms stay NPCs.
- **Not** a combat dossier for a *sapient people / society* (e.g. `Drow`,
  `Lizardfolk`, `Illithids`, `Myconid`). Keep their lore page intact; if combat
  notes are wanted, add a short section *there* instead of converting it. When
  unsure, ask the DM — do not overwrite a rich people-page with a statblock.
- **Search before you write** (`search_wiki`): the creature may already exist,
  often as a people/lore page, or under a variant name.

## Phase 2 — Write the dossier

Use the `{{Monster Lore}}` infobox plus body. Every infobox field is **prose —
qualities, never numbers** (no AC, HP, CR, dice, or DCs). Empty fields fall back
to honest defaults, so fill what's known and leave the rest.

```wikitext
{{Monster Lore
| creature_name =
| type          = e.g. Chromatic dragon (black) — short flavour line
| vulnerabilities = what wounds it worse than it should ("None discovered")
| resistances   = what merely glances off
| immunities    = what does nothing at all
| condition_immunities = conditions it cannot suffer (frightened, poisoned…)
| strong_saves  = what it rarely fails (reflexes, body, will, force of personality)
| senses        = how it perceives — sight in the dark, blind-sense, keen scent
| movement      = how it gets around — flight, swimming, burrowing, ice-walking
| abilities     = breath, presence, signature tricks, magic it can refuse
| confidence    = Fragmentary | Partial | Well-attested
| encountered   = [[Session N - Title|Session N]], where
| agent         = Agent Wren, of the Tellstone circle
}}

== The Harpers' Read ==
The tactical synthesis in the agent's voice: how to fight it, what to bring,
what to avoid.

== Encounters of Record ==
Where the party met it, linked to the sessions; this grows with each encounter.
```

Write descriptively and in-world. As the party learns more across encounters,
raise `confidence` and move facts up the entry. `Agent Wren, of the Tellstone
circle` is the bestiary's standing compiler — keep the voice consistent.

## Phase 3 — Wire it into the hierarchy

When a creature has subtypes or kin, connect them:

- **Baseline + subtypes** (a real "plain" form exists, e.g. `Troll`): the base
  creature is the parent dossier and gains a `== Subtypes ==` section linking each
  subtype. Each subtype opens with a nav line — `''A <kind> subtype of [[Troll]].
  See also [[…]].''` — and links back.
- **No baseline / family of equals** (every member is a subtype, e.g. `Giant`,
  `Dragon`): make the parent an **overview hub** (no infobox) — a short framing
  paragraph plus a table of the kinds, each linking its dossier. Each kind links
  back to the hub.
- **Make a hub** once a family has 2+ dossiers; below that, a shared category is
  enough.
- Carry kinship with categories too: `Dragons`, `Giants`, `Trolls`, `Goblinoids`,
  `Undead`, `Elementals`, etc.

## Phase 4 — Categories

- The `{{Monster Lore}}` template auto-files the page into `Category:Monsters`
  (via `includeonly`) — **do not** add that by hand.
- In the page body add `[[Category:Creatures]]` plus any kinship category from
  Phase 3.

## Phase 5 — Image (InstantCommons is enabled)

The wiki can embed Wikimedia Commons media **directly by filename — no upload**.

- Use **only open-licensed art**: public-domain-by-age artwork, or CC0/CC-BY
  (credit the source in the caption). A "close enough" likeness is fine — a CC0
  animal photo for a beast, classic public-domain art for a folklore creature.
- Verify the file resolves first:
  `curl -sI "https://commons.wikimedia.org/wiki/Special:FilePath/<urlencoded name>"`,
  then embed: `[[File:<Commons filename>|thumb|right|<caption> (artist, year;
  public domain via Wikimedia Commons)]]`.
- **Never upload copyrighted WotC / Monster Manual art** to the wiki.
- If no open match exists (common for fantasy-specific creatures), leave a
  commented slot and add the creature to a "needs image" list for the DM:
  `<!-- IMAGE NEEDED: [[File:<Name>.jpg|thumb|right|<Name>]] -->`.

## Phase 6 — Update the Bestiary index (mandatory)

A dossier no one can find is half-built. After writing or updating an entry,
`read_page` the `Bestiary` index and `mode="replace"` to add the creature under
the correct section (Dragons, Giants, Trolls, Goblinoids, Undead, Aberrations,
Elementals, Other monsters & beasts, Underdark folk, Peoples & societies), in the
established style:

```wikitext
* '''[[Creature]]''' — <one-line signature: its element, threat, or signature trick>
```

Keep the section order; add a new section only for a genuinely new family. The
`Bestiary` is linked from the `Main Page` (Quick Start sidebar + Campaign
Resources) — if you add a new top-level family **hub**, confirm it's reachable
from the index.

## Safety & edit summaries

- Every write needs an edit summary: `"Session <N> ingest: <what>"` when driven
  by a session, otherwise `"Bestiary: <what>"`.
- Never delete or blank a page. Never overwrite a rich people/society page with a
  combat dossier — ask the DM first.
- Descriptive and in-world only — what the party has **learned**, in the Harper's
  voice. No statistics.

## Report

Summarise: dossiers created/updated, hierarchy/hub changes, the `Bestiary` index
entries added, images embedded, and the list of creatures still needing an
open-licensed image.
