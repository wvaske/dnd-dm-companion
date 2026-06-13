---
name: manage-crafting
description: Publish and maintain the dragon harvest & crafting system on the wiki — bootstrap the player pages and DM reference, reveal recipes as the party earns them, resolve harvest checks, and run crafting projects at the Greywatch. Use when the DM asks to set up crafting, reveal/teach/research a recipe, harvest a dragon (or other) carcass, craft an item, or check what the party can make.
---

# Manage Dragon Harvesting & Crafting

The crafting system is **wiki content plus this workflow**. Live state — which
recipes are revealed, what the party has built — lives on the wiki; the
canonical rules live in two reference files next to this skill:

- `reference/build-doc.md` — the DM master doc: harvest table, materials
  catalog, knowledge-tier ledger (Part 1), the verbatim player-page markup
  (Parts 2–3), and the D&D Beyond item text (Part 4).
- `reference/recipes.md` — the derived per-recipe `{{Recipe}}` fields
  (materials, tool, facility, cost, time) the build doc doesn't spell out.

**Progressive reveal is the whole point.** Players see only what they've earned:
Known recipes from the start, Discoverable ones when found/taught/researched,
Locked ones only by DM fiat. Part 1 is **DM-private** and lives in the `DM:`
namespace (hidden from players); never paste harvest DCs, yields, or the tier
ledger onto a player-facing page.

All wiki writes go through the MCP tools (`write_page`, `read_page`,
`search_wiki`, `list_category`) with mandatory edit summaries. Use
`mode="create"` for new pages (fails safely if the title exists) and
`read_page` then `mode="replace"` when editing an existing page — never blank or
overwrite blind.

Pick the operation that matches the DM's request.

## Operation: Bootstrap (first-time setup)

Run once, to publish the initial system. Skip any step whose page already
exists (`search_wiki` / `read_page` first).

1. **`Template:Recipe`** (prerequisite — recipe pages render raw without it).
   Create with `mode="create"`, summary `"Crafting: add Recipe infobox template"`:
   ```wikitext
   <includeonly>{| class="wikitable" style="float:right; margin:0 0 1em 1em; width:22em"
   ! colspan="2" | Recipe
   |-
   | '''Rarity''' || {{{rarity|—}}}
   |-
   | '''Materials''' || {{{materials|—}}}
   |-
   | '''Tool''' || {{{tool|—}}}
   |-
   | '''Facility''' || {{{facility|—}}}
   |-
   | '''Cost''' || {{{cost|—}}}
   |-
   | '''Time''' || {{{time|—}}}
   |}</includeonly><noinclude>
   Crafting summary infobox for a dragon-crafting recipe. See [[Dragon Crafting Recipes]].
   [[Category:Templates]]
   </noinclude>
   ```

2. **DM-private reference → `DM:` namespace** (id **3000**, read-restricted).
   **Before publishing any Part 1 content, confirm the `DM:` namespace is
   actually player-hidden** — query the wiki's namespaces (`siteinfo`) and verify
   id 3000 exists and is read-restricted (an anonymous fetch of a `DM:` page must
   be denied). If it isn't, stop: writing Part 1 to an unprotected namespace
   leaks every DC and yield. Then publish Part 1 of `build-doc.md` as three
   pages, summary `"Crafting (DM): <page>"`:
   - `DM:Dragon Harvest Tables` — "How a harvest check works", the master
     harvest table, and the tiered-outcome rule.
   - `DM:Dragon Materials Catalog` — the materials catalog.
   - `DM:Crafting Recipe Ledger` — the Known/Discoverable/Locked tier table.

   Keep these pages out of player-facing categories (do **not** add
   `[[Category:Crafting]]`) so their titles don't surface in public category
   listings. After publishing, remind the DM to set `INDEX_NAMESPACES=0,3000` so
   `dmc index` includes the DM reference for session-prep (it is reference scope,
   not campaign lore).

3. **Player pages** — publish verbatim from `build-doc.md`, summary
   `"Crafting: add <page>"`:
   - `Dragon Harvesting` (Part 2)
   - `Crafting at the Greywatch` (Part 3)
   - `Dragon Crafting Recipes` (Part 2 index) — Known recipes as live
     `[[links]]`, Discoverable/Locked left as the "Rumored / Unproven" stubs.

4. **Known recipe pages (16).** For each row in the **Known** table of
   `reference/recipes.md`, create the page with `mode="create"` from this
   template, summary `"Crafting: add recipe <name>"`:
   ```wikitext
   == {{PAGENAME}} ==
   {{Recipe
   | rarity      = <rarity>
   | materials   = <materials>
   | tool        = <tool>
   | facility    = <facility>
   | cost        = <cost>
   | time        = <time>
   }}
   '''Result:''' <the item's Description from build-doc.md Part 4>

   '''Notes:''' Any character proficient with <tool> knows this conversion.

   [[Category:Crafting]] [[Category:<type category>]]
   ```
   Use the matching item's **Description** text from `build-doc.md` Part 4 for
   the Result line. Do **not** create Discoverable or Locked recipe pages here.

5. **Navigation.** Confirm `Dragon Harvesting`, `Dragon Crafting Recipes`, and
   `Crafting at the Greywatch` interlink, and that `Dragon Harvesting` is
   reachable from `Main Page` (read it, add a link under the crafting/resources
   section if missing — same as the Bestiary index).

6. **Index.** Tell the DM to run `uv run dmc index` so the new lore is searchable.

## Operation: Reveal a recipe

When the party finds a formula, is taught it, or completes a research project
(Discoverable: 1 week + 25 gp/rarity tier + DC 13/15/17/19 Arcana/Nature/
Medicine — see Part 1). Confirm it's actually unlocked before revealing.

1. Look the recipe up in the **Discoverable** (or, only on explicit DM
   instruction, **Locked**) table of `reference/recipes.md`.
2. Create its page with `mode="create"` using the recipe template above and the
   Part 4 Description for the Result line. Summary `"Crafting: reveal <name> (<how obtained>)"`.
3. **Flip the index** (`Dragon Crafting Recipes`): `read_page`, then
   `mode="replace"` to add `* [[<Name>]] — ''<Rarity>''` under the right section
   and remove the matching "Rumored / Unproven" bullet if present. Keep the
   established style. This sync is mandatory — an unrevealed-looking recipe the
   party actually earned is a bug.

## Operation: Run a harvest

Resolve recovering parts from a carcass against `DM:Dragon Harvest Tables` (or
`build-doc.md` Part 1 if the DM pages aren't up yet).

- One ability check per component: **d20 + ability mod + PB (if proficient with
  the tool) + Advantage (if proficient with the skill)**. Never add PB twice.
  No tool & no skill → raw ability check, DM may raise DC 2–5.
- Group components by **station** (Alchemy / Smithing / Skinning / Scavenge);
  spare hands `Help` for Advantage; total time ≈ the busiest station.
- If the DM uses the optional tiered outcome: beat DC by 5+ = Pristine (full
  yield, one result a tier higher); meet to +4 = Clean; miss by 1–4 = Damaged
  (half yield, capped a tier lower); miss by 5+ = Ruined.
- Parts are **stable — no spoilage**. Report each component's check, outcome,
  and yield. Record results wherever the DM tracks party inventory (a wiki
  page if they keep one; otherwise just report).

## Operation: Craft an item

Verify the **five gates** (Part 3) before anything is built:

1. **Recipe** — is the page live (revealed)? If not, route to *Reveal* first.
2. **Proficient crafter** — a PC proficient with the recipe's tool.
3. **Facility** — the matching Greywatch facility (Forge / Tannery / Laboratory
   / Arcane Study), or a rented town facility.
4. **Materials** — the harvested parts on hand (from `reference/recipes.md`).
5. **Cost & time** — from the recipe's fields. At a **controlled** Greywatch
   facility the materials cover raw cost (pay only the listed labor figure). A
   **rented** facility removes that offset (pay full market) and adds 50% to the
   time. One bastion turn = 7 days; long projects continue across turns while
   the crafter and facility stay assigned.

Report which gates pass, the gold and downtime owed, and the finished item with
its Part 4 effect text. The optional **Heartfrost Residue catalyst** adds a cold
rider with no rarity bump if the DM wants it — consume it as a material.

## Safety & edit summaries

- Every write needs an edit summary (formats above). Never delete or blank a page.
- **Never publish Part 1 content (DCs, yields, tier ledger) to a player page**,
  and never reveal a Discoverable/Locked recipe the party hasn't earned —
  confirm with the DM when unsure.
- Use `mode="create"` for new pages; `read_page` before any `mode="replace"`.
- The system's tunables are set in the build doc: spoilage **off**,
  recipe-knowledge **moderate**. Don't change tiers without the DM's say-so.

## Report

Summarise what changed: pages created/updated, recipes revealed (and how),
harvest outcomes and yields, crafting projects started (gold + downtime), index
entries synced, and any reminder to run `uv run dmc index`.
