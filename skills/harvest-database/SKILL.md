---
name: harvest-database
description: Maintain and query the monster-harvest database on the wiki (Cargo tables HarvestComponents, HarvestLog, DMHarvest) - add a slain creature's manifest and harvest record, log or spend components, prep DM-only manifests, and answer "what do we have / what can we build" questions. Use when a session includes harvesting, when the DM asks about banked components or harvest data, or when a Harvest Profile/Record needs editing.
---

# The Monster-Harvest Database

The harvest system ([[Monster Harvesting]] rules, September 2026 carcass-first
manifests) is backed by **three Cargo tables** inside the wiki's own database.
The tables are populated **only** by template calls on pages — never write SQL,
never hand-edit the [[Harvested Materials]] inventory table (it is a live
query and regenerates itself).

| Table | Fed by template | On pages | Holds |
|---|---|---|---|
| `HarvestComponents` | `{{Harvest Component}}` | creature pages, "Harvest Profile" section | one row per component that exists on a known carcass |
| `HarvestLog` | `{{Harvest Log Entry}}` | creature pages, "Harvest Record" section | one row per harvest event (rolls, units, outcome) |
| `DMHarvest` | `{{DM Harvest Component}}` | `DM:Harvest Manifests` only | unrevealed manifests; the template refuses to store outside the `DM:` namespace |

Helper templates: `{{Harvest Profile Header}}`, `{{Harvest Record Header}}`,
`{{DM Harvest Header}}`, `{{Harvested Materials Header}}`, and
`{{Harvest Table End}}` open/close the display tables around runs of row calls.

## Invariants (do not break)

- **Component names are globally unique across all creatures.** The ledger
  joins `HarvestLog.component = HarvestComponents.component` by name. Prefix
  generic names with the creature (`Hydra Hide Scraps`, not `Hide Scraps` —
  that one belongs to Arauthator). Check for collisions before adding:
  `search_wiki` the name, or query the table.
- **Log quantities are net banked units** including margin bonuses. `outcome=`
  vocabulary: `Recovered` (banked, positive qty), `Left` (on the carcass,
  qty 0), `Eaten` (recovered but consumed, never banked), `Spent` (banked
  stock consumed by crafting, **negative** qty). The ledger sums
  `Recovered + Spent` rows and hides components at ≤ 0.
- **Never `#cargo_query` the `DMHarvest` table from a player-visible page.**
  Cargo data is not protected by the DM-namespace read lock once stored; the
  only thing keeping DM manifests private is that queries against that table
  live exclusively on `DM:` pages.
- Rarity vocabulary: `Scraps, Common, Uncommon, Rare, Very Rare, Legendary,
  Artifact` (CV 1/2/4/8/16/32/64 and DC 0/5/10/15/20/25/30 derive from it).
  Item-type vocabulary for `primary_for`/`contributor_to`:
  `Potion, Poison, Bomb, Wand, Staff, Wondrous, Armor, Weapon, Rations`.

## Operation: a new creature is harvested

1. Build the manifest per [[Monster Harvesting]] (CR → ceiling, cumulative
   slot counts 1/2/3/4/5/6, one signature at the ceiling). If the DM prepped
   it on `DM:Harvest Manifests`, migrate those rows.
2. On the creature's page (see the update-bestiary skill for the dossier
   itself) add:

   ```wikitext
   == Harvest Profile ==
   ''CR N — <Ceiling> ceiling. Rules: [[Monster Harvesting]].''
   {{Harvest Profile Header}}
   {{Harvest Component|component=...|signature=yes|tool=...|rarity=...|effect=...|primary_for=...|contributor_to=...}}
   ...
   {{Harvest Table End}}

   == Harvest Record ==
   Harvested in [[<session page>|Session N]]; quantities include margin bonuses. Banked totals: [[Harvested Materials]].
   {{Harvest Record Header}}
   {{Harvest Log Entry|component=...|session=N|session_page=<session page>|quantity=..|harvester=..|roll=..|notes=..}}
   {{Harvest Log Entry|component=...|session=N|session_page=<session page>|quantity=0|outcome=Left}}
   ...
   {{Harvest Table End}}
   ```

   Every manifest component gets a log row — `Left` rows document what stayed
   on the carcass. Structure-only Common parts: omit `effect`.
3. Nothing else: [[Harvested Materials]] and the creature index on
   [[Monster Harvesting]] update themselves.

## Operation: spend components on crafting

Append a `{{Harvest Log Entry}}` with **negative** `quantity`,
`outcome=Spent`, and a note naming the item built, to the creature page's
Harvest Record (or the Trade goods section of [[Harvested Materials]] for
gathered stock). The inventory decrements automatically.

## Operation: DM prep

Add `{{DM Harvest Component}}` rows under a creature heading on
`DM:Harvest Manifests` (`status=Unrevealed`/`Pending`). On reveal, move rows
to the creature page as `{{Harvest Component}}` calls and delete them there.

## Operation: answer questions

Prefer a `#cargo_query` (on a page, in a sandbox preview, or via the DB
read-only) over manual tallying. Useful shapes:

```wikitext
{{#cargo_query:tables=HarvestComponents
|fields=creature,component,rarity,effect
|where=tool LIKE '%Poisoner%' |order by=cv DESC}}
```

Banked totals replicate the ledger:
`tables=HarvestLog=L,HarvestComponents=C |join on=L.component=C.component
|fields=C.component,SUM(L.quantity)=QTY |where=L.outcome IN ('Recovered','Spent')
|group by=C.component |having=SUM(L.quantity)>0`.

`Special:CargoTables` shows raw rows; `Special:Drilldown` gives faceted
browsing.

## Infrastructure notes

- Cargo 3.8 + ParserFunctions (with `$wgPFEnableStringFunctions`) are loaded in
  LocalSettings on alder01 (host path
  `/var/lib/docker/volumes/deeznuts_deeznuts/_data/configs/LocalSettings.php`).
- If a template's `#cargo_declare` schema changes, recreate that table:
  `docker exec mw_app php maintenance/run.php ./extensions/Cargo/maintenance/cargoRecreateData.php --table <Table>`.
- `{{Harvested Materials Row}}`'s leading/trailing newlines are load-bearing:
  Cargo `format=template` concatenates row outputs without line breaks.
- After content changes, refresh the semantic index: `uv run dmc index`.
