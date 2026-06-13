# Recipe field ledger (derived)

The build doc (`build-doc.md`) gives the harvest table, the materials catalog,
the knowledge-tier ledger, and the D&D Beyond item text — but **not** the
per-recipe `{{Recipe}}` fields. This file derives them once, so `bootstrap`,
`reveal`, and `craft` stay deterministic instead of re-guessing materials each
run.

How each column was derived:

- **Materials** — reverse-indexed from the catalog's "Appears in" lists in
  `build-doc.md` Part 1, with quantities from the harvest table's Yield column.
- **Tool / Facility** — from the Greywatch facility table in Part 3 (Forge =
  Smith's, Tannery = Leatherworker's, Laboratory = Alchemist's, Arcane Study =
  any enchanted/magic item, wands, foci, lenses).
- **Cost / Time** — representative midpoint of the rarity band in Part 3; the
  DM may pick anywhere in the band. Bands: Common 25–50 gp / 1–3 days · Uncommon
  100–200 gp / 1–2 weeks · Rare 1,000–2,000 gp / 3–6 weeks · Very Rare
  10,000–20,000 gp / 8–12 weeks.
- **Result text** — use the matching item's *Description* from `build-doc.md`
  Part 4 verbatim for the recipe page's `'''Result:'''` line.
- **Page categories** — always `[[Category:Crafting]]` plus the type category
  in the table.

`+ Heartfrost Residue` in a materials cell marks the optional cold-property
catalyst (Part 1) — consumed for a cold rider with no rarity bump; not required.

---

## Known (bootstrap publishes these as live recipe pages)

| Page | Rarity | Tool / Facility | Materials | Cost / Time | Type category |
|---|---|---|---|---|---|
| Frostfang Dagger | Uncommon | Smith's Tools / Greywatch Forge | 4–6 Frostfang Teeth | 150 gp / 1 week | Weapons |
| Rending Claw-blade | Uncommon | Smith's Tools / Greywatch Forge | 1 Talon Hook (claw) | 150 gp / 1 week | Weapons |
| Weighted Bone Mace | Uncommon | Smith's Tools / Greywatch Forge | 2–3 Tail Vertebrae | 150 gp / 1 week | Weapons |
| Rimebite Ammunition | Uncommon | Smith's Tools / Greywatch Forge | 4–6 Frostfang Teeth (makes 20) | 150 gp / 1 week | Weapons |
| Scaled Shield | Uncommon | Smith's Tools / Greywatch Forge | Glacial Scales (partial hide) | 150 gp / 1 week | Armor |
| Frostweave Studded Leather | Uncommon | Leatherworker's Tools / Greywatch Tannery | 1 Frost-Tanned Hide | 150 gp / 1 week | Armor |
| Glacial Half-Plate | Rare | Smith's Tools / Greywatch Forge | 1 hide's worth of Glacial Scales | 1,500 gp / 5 weeks | Armor |
| Glider-Cloak | Uncommon | Leatherworker's Tools / Greywatch Tannery | 2 Wing Membranes | 150 gp / 1 week | Wondrous |
| Stormtent | Common | Leatherworker's Tools / Greywatch Tannery | 2 Wing Membranes | 40 gp / 2 days | Wondrous |
| Potion of Cold Resistance | Uncommon | Alchemist's Supplies / Greywatch Laboratory | 1 Breath Gland dose | 150 gp / 1 week | Alchemy |
| Cold-Infused Oil | Uncommon | Alchemist's Supplies / Greywatch Laboratory | 1–2 vials Sluggish Blood | 150 gp / 1 week | Alchemy |
| Potion of Footing | Common | Alchemist's Supplies / Greywatch Laboratory | 1 vial Cryogland Bile | 40 gp / 2 days | Alchemy |
| Glacier Caltrops | Common | Smith's Tools / Greywatch Forge | 2–3 Frostfang Teeth | 40 gp / 2 days | Alchemy |
| Rime Ration | Common | Alchemist's Supplies / Greywatch Laboratory | Sluggish Blood + Frost-Tanned Hide scrap (pouch) | 40 gp / 2 days | Alchemy |
| Gizzard Luckstone | Common | Arcana (spell focus) / Greywatch Arcane Study | 1 Gizzard Stone | 40 gp / 2 days | Wondrous |
| Frill-Spine Arcane Focus | Uncommon | Arcana (spell focus) / Greywatch Arcane Study | 1 Frill-spine (from Horn & Frill) | 150 gp / 1 week | Wondrous |

## Discoverable (do NOT publish at bootstrap; `reveal` on discovery)

| Page | Rarity | Tool / Facility | Materials | Cost / Time | Type category |
|---|---|---|---|---|---|
| Frostfang Blade | Rare | Smith's Tools / Greywatch Forge | 1 large Frostfang Tooth | 1,500 gp / 5 weeks | Weapons |
| Glacier-Pick | Rare | Smith's Tools / Greywatch Forge | 1 Talon Hook (claw) | 1,500 gp / 5 weeks | Weapons |
| Frostbone Staff | Rare | Arcana (spell focus) / Greywatch Arcane Study | 1 Tail Vertebra (core) | 1,500 gp / 5 weeks | Wondrous |
| Cloak of the Rimewalker | Rare | Leatherworker's Tools / Greywatch Tannery | 1 Frost-Tanned Hide | 1,500 gp / 5 weeks | Wondrous |
| Potion of Frostskin | Rare | Alchemist's Supplies / Greywatch Laboratory | powdered Glacial Scales | 1,500 gp / 5 weeks | Alchemy |
| Draught of the Slow Pulse | Uncommon | Alchemist's Supplies / Greywatch Laboratory | 1–2 vials Sluggish Blood | 150 gp / 1 week | Alchemy |
| Winter's Clarity | Uncommon | Alchemist's Supplies / Greywatch Laboratory | ground Glacial Eye | 150 gp / 1 week | Alchemy |
| Glacial Vigor | Rare | Alchemist's Supplies / Greywatch Laboratory | Sluggish Blood + Heartfrost Residue | 1,500 gp / 5 weeks | Alchemy |
| Frost-Bomb | Uncommon | Alchemist's Supplies / Greywatch Laboratory | 1 Breath Gland dose | 150 gp / 1 week | Alchemy |
| Rime Flask | Uncommon | Alchemist's Supplies / Greywatch Laboratory | 1–2 vials Sluggish Blood | 150 gp / 1 week | Alchemy |
| Hoarfrost Smoke | Uncommon | Alchemist's Supplies / Greywatch Laboratory | 1 vial Cryogland Bile | 150 gp / 1 week | Alchemy |
| Shatterfrost Vial | Rare | Alchemist's Supplies / Greywatch Laboratory | Frostfang Teeth + 1 Breath Gland dose | 1,500 gp / 5 weeks | Alchemy |
| Cryostasis Flask | Rare | Alchemist's Supplies / Greywatch Laboratory | Cryogland Bile + Heartfrost Residue | 1,500 gp / 5 weeks | Alchemy |
| Biting Frost Oil | Rare | Alchemist's Supplies / Greywatch Laboratory | Heartfrost Residue | 1,500 gp / 5 weeks | Alchemy |
| Rimeward Wax | Uncommon | Alchemist's Supplies / Greywatch Laboratory | powdered Glacial Scales | 150 gp / 1 week | Alchemy |
| Slick-Ice Grease | Common | Alchemist's Supplies / Greywatch Laboratory | 1 vial Cryogland Bile | 40 gp / 2 days | Alchemy |
| Frostfang Spike | Uncommon | Smith's Tools / Greywatch Forge | 1 Frostfang Tooth | 150 gp / 1 week | Alchemy |
| Coldfire Candle | Uncommon | Alchemist's Supplies / Greywatch Laboratory | Wing Membrane (wax) + Cryogland Bile | 150 gp / 1 week | Wondrous |
| Frostbreath Whistle | Uncommon | Arcana (spell focus) / Greywatch Arcane Study | 1 horn (from Horn & Frill) | 150 gp / 1 week | Wondrous |
| Dragon's Eye Marble | Rare | Arcana (spell focus) / Greywatch Arcane Study | 1 Glacial Eye | 1,500 gp / 5 weeks | Wondrous |
| Frost-Seer's Lens | Rare | Arcana (spell focus) / Greywatch Arcane Study | 1 Glacial Eye | 1,500 gp / 5 weeks | Wondrous |
| Wand of Frost | Rare | Arcana (spell focus) / Greywatch Arcane Study | 1 horn (from Horn & Frill) | 1,500 gp / 5 weeks | Wondrous |
| Potion of Slowing | Rare | Alchemist's Supplies / Greywatch Laboratory | 1 vial Cryogland Bile | 1,500 gp / 5 weeks | Alchemy |
| Heartfrost Ember | Rare | Alchemist's Supplies / Greywatch Laboratory | Heartfrost Residue | 1,500 gp / 5 weeks | Alchemy |
| Elixir of the Dragon's Breath | Rare | Alchemist's Supplies / Greywatch Laboratory | 1 Breath Gland dose | 1,500 gp / 5 weeks | Alchemy |
| Avalanche Pellet | Rare | Alchemist's Supplies / Greywatch Laboratory | powdered Glacial Scales + 1 Breath Gland dose | 1,500 gp / 5 weeks | Alchemy |

## Locked (named expert or short quest only — never reveal without DM say-so)

| Page | Rarity | Tool / Facility | Materials | Cost / Time | Type category |
|---|---|---|---|---|---|
| Glacial Plate | Very Rare | Smith's Tools / Greywatch Forge (gland-work in Laboratory) | 1 hide's worth of Glacial Scales + 1 Breath Gland dose | 15,000 gp / 10 weeks | Armor |
| Pendant of the Spiteful Eye | Rare | Arcana (spell focus) / Greywatch Arcane Study | 1 Glacial Eye | 1,500 gp / 5 weeks | Wondrous |

## Not a recipe

**Rimeforged Heart** — a natural treasure, not crafted. Identified (Arcana /
*identify* / sage / Zarchelia), then consumed as a ritual over a long rest:
permanent +1 CON (raises the CON maximum by 1); optional rider — immune to
exhaustion from extreme cold. One heart, one beneficiary, indivisible. Document
it as an NPC/treasure note, not a recipe page.
