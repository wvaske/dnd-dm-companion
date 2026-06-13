# Elder White Dragon — Harvest, Crafting & Homebrew Build Doc

> **Canonical source for the `manage-crafting` skill.** This is the DM master
> document. The skill publishes from it: Part 1 → the `DM:` namespace, Parts 2–3
> → player-facing wiki pages, Part 4 item text → the "Result" line of each
> recipe page. Derived per-recipe crafting fields (materials/tool/facility/cost/
> time) live in `recipes.md` next to this file.

**How to use this file.** It has four parts, each self-contained:

1. **DM Master Reference** — everything, private. Spoilage is intentionally *not* a mechanic (see note).
2. **Player Wiki Pages** — MediaWiki markup, ready to POST, structured for progressive reveal.
3. **Greywatch Crafting Page** — MediaWiki markup, player-facing rules with cost + time.
4. **D&D Beyond Homebrew Items** — paste-ready blocks with all builder fields.

> **Spoilage note:** harvested parts are now **stable** — they do not decay. Difficulty lives in the harvest *check* and the downtime *cost*, not a timer. All clocks and the Stasis Bead / Preservative Brine items from earlier drafts are removed.

> **Recipe-knowledge default (tunable):** *moderate.* Proficient crafters begin knowing the obvious single-component conversions (**Known**); non-obvious combinations are found, taught, or researched (**Discoverable**); premium results are gated behind a named expert or quest (**Locked**). Make it **generous** by promoting Discoverable→Known, or **lean** by demoting Known→Discoverable.

---

# PART 1 — DM MASTER REFERENCE (private)

## How a harvest check works (2024 tool rules)

One ability check per component:

> **d20 + ability modifier + Proficiency Bonus (if proficient with the Tool), with Advantage (if proficient with the Skill).**

- The **ability** is fixed by the task; the skill never changes it.
- **Tool** proficiency → add PB. **Skill** proficiency → Advantage only (the skill's own ability is irrelevant; never add PB twice).
- **No tool, no skill:** raw ability check, DM may raise DC 2–5.
- **Optional fallback (houserule):** a character with the *skill* but not the *tool* may make a normal skill check using that skill's own ability and PB, at **+2 DC**.

## Master harvest table

★ = premium component.

| # | Component | Ability | Tool → PB | Skill → Advantage | DC | Yield |
|---|---|---|---|---|---|---|
| 1 | ★ Breath Gland (Frost Sac) | INT | Alchemist's Supplies | Medicine | 16 | 1 sac (3–4 doses) |
| 2 | ★ Heartfrost Residue | INT | Alchemist's Supplies | Arcana | 16 | 2–3 pinches |
| 3 | ★ Rimeforged Heart | INT | Alchemist's Supplies | Medicine | 18 | 1 |
| 4 | Cryogland Bile | INT | Alchemist's Supplies | Medicine | 14 | 1–2 vials |
| 5 | ★ Glacial Eyes | INT | Alchemist's Supplies | Perception | 15 | 2 eyes |
| 6 | Sluggish Blood | INT | Alchemist's Supplies | Medicine | 12 | 4–6 vials |
| 7 | Glacial Scales | STR | Smith's Tools | Nature | 15 | 1 hide's worth |
| 8 | Talon Hooks (claws) | STR | Smith's Tools | Athletics | 14 | 6 claws |
| 9 | Frostfang Teeth | STR | Smith's Tools | Nature | 13 | 4–6 fangs |
| 10 | Horn & Frill | DEX | Smith's / Carver's | Nature | 13 | 2 horns + frill |
| 11 | Tail Vertebrae | STR | Smith's Tools | Medicine | 12 | 3–4 bones |
| 12 | Frost-Tanned Hide | DEX | Leatherworker's | Survival | 13 | 1 hide |
| 13 | Wing Membrane | DEX | Leatherworker's | Survival | 12 | 2 membranes |
| 14 | Gizzard Stones | WIS | — (no tool) | *Survival skill check* | 10 | 1d6 stones |

**Stations (tool = station):** Alchemy (Alchemist's Supplies — #1–6), Smithing (Smith's/Carver's — #7–11), Skinning (Leatherworker's — #12–13), Scavenge (none — #14). Each player runs a station; spare hands take **Help** for Advantage. Total time ≈ the busiest station.

**One-roll tiered outcome (optional):** beat DC by 5+ = *Pristine* (full yield, one result a tier higher); meet to +4 = *Clean* (standard); miss by 1–4 = *Damaged* (half yield, results capped a tier lower); miss by 5+ = *Ruined*.

## Materials catalog

Each entry: description · harvest (from table above) · appears in.

**Rimeforged Heart** ★ — The cardiac core, frozen at death into a fist-sized knot of blue-black ice that never melts. *Not a recipe — a natural treasure.* Thawed against living skin over a long rest and swallowed (ritual): **permanent +1 Constitution, raises CON maximum by 1**; optional rider: immune to exhaustion from extreme cold. One heart, one beneficiary, indivisible. *Appears in:* — (consumed directly).

**Frostfang Teeth** — Front fangs that hold a permanent cold edge. *Appears in:* Frostfang Dagger, Rimebite Ammunition, Frostfang Blade, Frostfang Spike, Glacier Caltrops, Shatterfrost Vial.

**Talon Hooks** — Six shortsword-length claws. *Appears in:* Glacier-Pick / Talon Warhammer, Rending Claw-blade.

**Tail Vertebrae** — Dense terminal bones, shatter-resistant. *Appears in:* Weighted Bone Mace, Frostbone Staff.

**Glacial Scales** — Belly/flank plates, the prize of the carcass; frost-rimed. *Appears in:* Glacial Half-Plate, Glacial Plate (gland-worked), Scaled Shield, Potion of Frostskin (powdered), Rimeward Wax (powdered), Avalanche Pellet.

**Frost-Tanned Hide** — Supple cold-cured back/wing-root leather. *Appears in:* Frostweave Studded Leather, Cloak of the Rimewalker, Rime Ration (pouch).

**Wing Membrane** — Translucent, tough. *Appears in:* Glider-Cloak, Stormtent, Coldfire Candle (wax).

**Breath Gland (Frost Sac)** ★ — The volatile cold reservoir; the bottleneck component. *Appears in:* Potion of Cold Resistance, Frost-Bomb, Elixir of the Dragon's Breath, Shatterfrost Vial, Avalanche Pellet, Glacial Plate (gland-worked), Distilled Dragon's Breath dose.

**Sluggish Blood** — Half-frozen ichor; base reagent and binder. *Appears in:* Cold-Infused Oil, Draught of the Slow Pulse, Glacial Vigor, Rime Flask, Rune-Ink binder, Rime Ration.

**Cryogland Bile** — Bitter chilling fluid. *Appears in:* Potion of Slowing, Hoarfrost Smoke, Cryostasis Flask, Potion of Footing, Slick-Ice Grease, Coldfire Candle.

**Glacial Eyes** ★ — Crystal-clear, "remembering" eyes. *Appears in:* Frost-Seer's Lens, Pendant of the Spiteful Eye, Dragon's Eye Marble, Winter's Clarity (ground).

**Horn & Frill** — Crown horns and cheek spines; arcane resonance for evocation. *Appears in:* Wand of Frost, Frill-Spine Arcane Focus, Frostbreath Whistle.

**Heartfrost Residue** ★ — Rime from the heart cavity (distinct from the Heart). A catalyst that adds a cold rider to an in-progress craft with no rarity bump. *Appears in:* Biting Frost Oil, Glacial Vigor, Heartfrost Ember, Cryostasis Flask, and as a **catalyst** in any cold-property upgrade.

**Gizzard Stones** — Smooth, faintly magical swallowed stones. *Appears in:* Gizzard Luckstone, focus blanks/sling stones.

## Recipe knowledge ledger (DM master)

| Tier | Recipes | How obtained |
|---|---|---|
| **Known** | Frostfang Dagger, Rending Claw-blade, Weighted Bone Mace, Scaled Shield, Frostweave Studded Leather, Glider-Cloak, Stormtent, Glacial Half-Plate, Rimebite Ammunition, Cold-Infused Oil, Potion of Cold Resistance, Potion of Footing, Glacier Caltrops, Rime Ration, Gizzard Luckstone, Frill-Spine Arcane Focus | Free to any character proficient with the relevant tool |
| **Discoverable** | Frostfang Blade, Glacier-Pick, Frostbone Staff, Cloak of the Rimewalker, Potion of Frostskin, Draught of the Slow Pulse, Winter's Clarity, Glacial Vigor, Frost-Bomb, Rime Flask, Hoarfrost Smoke, Shatterfrost Vial, Cryostasis Flask, Biting Frost Oil, Rimeward Wax, Slick-Ice Grease, Frostfang Spike, Coldfire Candle, Frostbreath Whistle, Dragon's Eye Marble, Frost-Seer's Lens, Wand of Frost, Potion of Slowing, Heartfrost Ember, Elixir of the Dragon's Breath, Avalanche Pellet | Hoard formula, NPC instructor (Order quartermaster, draconic-harvest specialist, Candlekeep researcher), guild purchase, or a downtime **research project** (1 week + 25 gp/rarity tier + DC 13/15/17/19 Arcana, Nature, or Medicine) |
| **Locked** | Glacial Plate (gland-worked), Pendant of the Spiteful Eye | Named expert or short quest only |
| **Not a recipe** | Rimeforged Heart | Identified (Arcana / *identify* / sage / Zarchelia), then consumed as a ritual |

---

# PART 2 — PLAYER WIKI PAGES (MediaWiki markup)

> Reveal pages as the party earns them. Filled sections = Known; stub sections = Discoverable (revealed on discovery); omit Locked entirely until unlocked.

### Page: `Dragon Harvesting`

```mediawiki
{{Lore|type=Crafting Knowledge}}
== Dragon Harvesting ==
A slain dragon is a mobile treasury of crafting materials. White dragon parts in particular keep their bite of cold long after death, and a careful hand can turn scale, fang, gland, and bone into arms, armor, and alchemy.

=== Harvesting a carcass ===
Each part is recovered with a single ability check, using the tool appropriate to the work. If you are proficient with the tool you add your Proficiency Bonus; if you are also proficient with a related skill, you make the check with Advantage. A failed check ruins only that part.

Work is divided into '''stations''' by tool:
* '''Alchemy''' (Alchemist's Supplies) — glands, blood, eyes, and the rarest organs
* '''Smithing''' (Smith's / Carver's Tools) — scales, claws, fangs, horn, bone
* '''Skinning''' (Leatherworker's Tools) — hide and wing membrane
* '''Scavenging''' (no tools) — whatever the beast had swallowed

A full party can work every station at once. Spare hands may [[Help]] another harvester for Advantage.

=== What can be made ===
See [[Dragon Crafting Recipes]] for known formulae, and [[Crafting at the Greywatch]] for where and how to build them.

[[Category:Crafting]] [[Category:Lore]]
```

### Page: `Dragon Crafting Recipes`

```mediawiki
== Dragon Crafting Recipes ==
Recipes the party currently knows. New formulae are added as they are learned, taught, or researched.

=== Weapons ===
* [[Frostfang Dagger]] — ''Uncommon''
* [[Rending Claw-blade]] — ''Uncommon''
* [[Weighted Bone Mace]] — ''Uncommon''
* [[Rimebite Ammunition]] — ''Uncommon''

=== Armor & Worn ===
* [[Scaled Shield]] — ''Uncommon''
* [[Frostweave Studded Leather]] — ''Uncommon''
* [[Glacial Half-Plate]] — ''Rare''
* [[Glider-Cloak]] — ''Uncommon''
* [[Stormtent]] — ''Common''

=== Alchemy & Sundries ===
* [[Potion of Cold Resistance]] — ''Uncommon''
* [[Cold-Infused Oil]] — ''Uncommon''
* [[Potion of Footing]] — ''Common''
* [[Glacier Caltrops]] — ''Common''
* [[Rime Ration]] — ''Common''
* [[Gizzard Luckstone]] — ''Common''
* [[Frill-Spine Arcane Focus]] — ''Uncommon''

=== Rumored / Unproven ===
''The party has heard these are possible but lacks the formula.''
* Distilled dragon's breath — ''a weaponized exhalation''
* Gland-worked plate — ''armor that bites back''
* A focus cut from a dragon's eye — ''said to remember''
<!-- DM: convert a bullet to a real [[link]] when the recipe is discovered -->

[[Category:Crafting]]
```

### Template: a single recipe page (copy per recipe)

```mediawiki
== {{PAGENAME}} ==
{{Recipe
| rarity      = Uncommon
| materials   = 4–6 Frostfang Teeth
| tool        = Smith's Tools
| facility    = Greywatch Forge
| cost        = 150 gp
| time        = 1 week
}}
'''Result:''' A dagger whose edge never warms. ''+1 weapon; deals an extra 1d4 cold damage on a hit (once per turn).''

'''Notes:''' Any character proficient with Smith's Tools knows this conversion.

[[Category:Crafting]] [[Category:Weapons]]
```

---

# PART 3 — GREYWATCH CRAFTING PAGE (MediaWiki markup)

### Page: `Crafting at the Greywatch`

```mediawiki
== Crafting at the Greywatch ==
The Greywatch is the party's workshop as much as its fortress. Its facilities are what turn raw dragon-parts into finished gear.

=== The five gates ===
To craft any item you need all of the following:
# '''The recipe''' — see [[Dragon Crafting Recipes]].
# '''A proficient crafter''' — a character proficient with the listed tool.
# '''A facility''' — the matching Greywatch facility (or a town that rents one, at extra cost and time).
# '''The materials''' — harvested parts on hand.
# '''Cost and time''' — gold and downtime days below.

=== Greywatch facilities ===
{| class="wikitable"
! Facility !! Tool !! Crafts
|-
| Forge || Smith's Tools || Weapons, shields, metal & scale armor
|-
| Tannery || Leatherworker's Tools || Hide armor, cloaks, membrane goods
|-
| Laboratory || Alchemist's Supplies || Potions, oils, bombs, organ processing
|-
| Arcane Study || Arcana / spell focus || Wands, foci, lenses, and any enchanted (magic) item
|}

A facility the party '''controls''' lets the harvested material cover the item's raw-material cost — you pay only the labor/reagent figure below. Renting a town facility removes that offset (pay full market) and adds 50% to the time.

=== Cost and time by rarity ===
''(At a controlled Greywatch facility, materials supplied.)''
{| class="wikitable"
! Rarity !! Cost (labor & reagents) !! Time
|-
| Common || 25–50 gp || 1–3 days
|-
| Uncommon || 100–200 gp || 1–2 weeks
|-
| Rare || 1,000–2,000 gp || 3–6 weeks
|-
| Very Rare || 10,000–20,000 gp || 8–12 weeks
|}

=== Bastion turns ===
One bastion turn = 7 days. A crafter occupies one facility for the duration of a project; multiple crafters at different facilities work in parallel. A project longer than one bastion turn continues across turns so long as the facility and crafter remain assigned.

=== Example ===
The party wants ''Glacial Half-Plate'' (Rare). They have a smith proficient with Smith's Tools, a Forge at the Greywatch, and a hide's worth of Glacial Scales. They pay 1,500 gp and assign the smith to the Forge for 5 weeks (most of one bastion turn five times over — or run it alongside other projects at other facilities).

[[Category:Crafting]] [[Category:Greywatch]]
```

---

# PART 4 — D&D BEYOND HOMEBREW ITEMS

**Builder fields per item:** Name · Item Type (+ subtype) · Rarity · Requires Attunement · Snippet (short card text) · Description (HTML for the description box). **Magic = Yes** for all but the plainest gear.

**Global rule for consumables:** a thrown/ingested item's save DC is **15**, or **8 + the crafter's Proficiency Bonus + crafting ability modifier** if higher. State whichever you use at the table.

### Frostfang Dagger
- **Type:** Weapon (dagger) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** You have a +1 bonus to attack and damage rolls with this magic dagger, which deals an extra 1d4 cold damage on a hit (once per turn).
- **Description:** Knapped from the fang of a white dragon, this dagger's edge never warms; frost beads along it in any climate. You have a +1 bonus to attack and damage rolls made with this magic weapon. Once per turn when you hit a creature with it, the target takes an extra 1d4 cold damage.

### Frost-Seer's Lens
- **Type:** Wondrous Item · **Rarity:** Rare · **Attunement:** Yes
- **Snippet:** While attuned, you have advantage on Wisdom (Perception) checks that rely on sight, and on the spellcasting of scrying against arctic or cold-dwelling targets.
- **Description:** A lens cut from the crystalline eye of a white dragon, set in a rime-silvered frame. While attuned, you have advantage on Wisdom (Perception) checks that rely on sight. When you cast a divination spell that targets a creature native to cold or arctic environments, you have advantage on any check or save the spell calls for to locate or perceive that creature.

## Weapons

### Rimebite Ammunition (20)
- **Type:** Weapon (ammunition) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** +1 to attack/damage; on a hit, extra 1d4 cold and target's speed −10 ft until your next turn. Single use.
- **Description:** Arrowheads or bolts tipped with white-dragon fang. On a hit, the ammunition deals an extra 1d4 cold damage and the target's speed is reduced by 10 feet until the start of your next turn, then the cold charge is spent.

### Frostfang Blade
- **Type:** Weapon (any sword) · **Rarity:** Rare · **Attunement:** Yes
- **Snippet:** +1 sword, extra 1d6 cold on a hit (1/turn); cast Ray of Frost from it once per day.
- **Description:** A larger fang reforged into a blade. You gain a +1 bonus to attack and damage rolls; once per turn on a hit it deals an extra 1d6 cold damage. Once per day you may cast Ray of Frost (save DC 13) from the blade.

### Glacier-Pick (Talon Warhammer)
- **Type:** Weapon (warhammer or war pick) · **Rarity:** Rare · **Attunement:** Yes
- **Snippet:** +1 weapon; on a critical hit, the target is restrained by ice until the end of its next turn.
- **Description:** Forged around a dragon's talon. +1 to attack and damage rolls. On a critical hit, biting ice locks the target in place — it is restrained until the end of its next turn.

### Rending Claw-blade
- **Type:** Weapon (any finesse) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** +1 finesse weapon; its slashing damage ignores resistance.
- **Description:** A single claw honed to a razor's hook. +1 to attack and damage rolls; the slashing damage it deals ignores resistance to slashing damage.

### Weighted Bone Mace
- **Type:** Weapon (mace) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** +1 mace; advantage on checks and saves to avoid being disarmed, and it cannot be broken by nonmagical means.
- **Description:** A mace head of dense tail-bone. +1 to attack and damage rolls; you have advantage on ability checks and saving throws to keep hold of it, and it can't be broken by nonmagical means.

### Frostbone Staff
- **Type:** Staff (arcane focus) · **Rarity:** Rare · **Attunement:** Yes (by a spellcaster)
- **Snippet:** +1 to cold spell damage rolls; holds 3 charges of Armor of Agathys (regains 1d3 at dawn).
- **Description:** A staff cored with dragon vertebrae. While holding it, add +1 to one damage roll of any spell that deals cold damage. It has 3 charges; expend 1 to cast Armor of Agathys (2nd level). It regains 1d3 charges daily at dawn.

## Armor & Worn

### Glacial Half-Plate
- **Type:** Armor (half plate or breastplate) · **Rarity:** Rare · **Attunement:** No
- **Snippet:** You have resistance to cold damage while wearing this armor.
- **Description:** Scaled with white-dragon plates that never lose their chill. While you wear this armor, you have resistance to cold damage.

### Glacial Plate (gland-worked)
- **Type:** Armor (plate) · **Rarity:** Very Rare · **Attunement:** Yes
- **Snippet:** Resistance to cold; once per day as a reaction to being hit in melee, deal 2d6 cold to the attacker.
- **Description:** Plate armor worked with distilled breath-gland frost. You have resistance to cold damage. Once per day, when a creature within 5 feet hits you with a melee attack, you can use your reaction to wreath yourself in frost-recoil, dealing 2d6 cold damage to that attacker.

### Scaled Shield
- **Type:** Armor (shield) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** +1 shield; advantage on saving throws against being frozen, paralyzed, or magically slowed.
- **Description:** A shield faced in overlapping dragon scales. You gain a +1 bonus to AC (already included). You have advantage on saving throws against being slowed, frozen, or paralyzed.

### Frostweave Studded Leather
- **Type:** Armor (studded leather) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** +1 armor; you suffer no harm from extreme cold environments.
- **Description:** Cold-cured dragon hide, supple and quiet. +1 bonus to AC; you automatically endure the effects of extreme cold (per the DMG environment rules) without harm.

### Cloak of the Rimewalker
- **Type:** Wondrous Item (cloak) · **Rarity:** Rare · **Attunement:** Yes
- **Snippet:** Resistance to cold while worn; you leave no tracks on snow or ice and ignore difficult terrain from them.
- **Description:** A cloak of frost-tanned hide. While you wear it, you have resistance to cold damage, you leave no tracks across snow or ice, and ice and snow are not difficult terrain for you.

### Glider-Cloak
- **Type:** Wondrous Item (cloak) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Negates fall damage; with a DC 10 Acrobatics check you may glide horizontally as you descend.
- **Description:** Stretched from translucent wing membrane. You take no damage from falling. While falling, you may make a DC 10 Dexterity (Acrobatics) check to glide, moving up to 5 feet horizontally for every 10 feet you descend.

### Stormtent
- **Type:** Wondrous Item · **Rarity:** Common · **Attunement:** No
- **Snippet:** A two-person shelter; occupants are unharmed by extreme-cold environments while inside.
- **Description:** A compact tent of treated wing membrane. Creatures sheltering inside automatically endure extreme cold without harm and are protected from arctic wind and precipitation.

## Potions & Ingested

### Potion of Cold Resistance
- **Type:** Potion · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Resistance to cold damage for 1 hour.
- **Description:** A flask of pale, slushy liquid. When you drink it, you gain resistance to cold damage for 1 hour.

### Draught of the Slow Pulse
- **Type:** Potion · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** 1 hour: advantage on saves vs. exhaustion and being knocked prone; hold breath 10× as long.
- **Description:** For 1 hour after drinking, your metabolism crawls: you have advantage on saving throws against exhaustion and against being knocked prone, and you can hold your breath ten times longer than normal.

### Glacial Vigor
- **Type:** Potion · **Rarity:** Rare · **Attunement:** No
- **Snippet:** Gain 3d10 temp HP as icy rime; while any remain, melee attackers take 1d6 cold.
- **Description:** You gain 3d10 temporary hit points, manifesting as a rime of ice over your skin. While you have any of these temporary hit points, a creature that hits you with a melee attack takes 1d6 cold damage.

### Potion of Frostskin
- **Type:** Potion · **Rarity:** Rare · **Attunement:** No
- **Snippet:** 1 hour: resistance to cold; the first time each turn a melee attacker hits you, its speed drops 10 ft.
- **Description:** For 1 hour, you have resistance to cold damage. The first time on each of your turns that a creature hits you with a melee attack, that creature's speed is reduced by 10 feet until the end of its next turn.

### Winter's Clarity
- **Type:** Potion · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** 1 hour: advantage on Wisdom (Perception); see normally through fog, sleet, and falling snow.
- **Description:** Brewed with ground dragon-eye. For 1 hour you have advantage on Wisdom (Perception) checks and can see normally through fog, sleet, and falling snow.

### Elixir of the Dragon's Breath
- **Type:** Potion · **Rarity:** Rare · **Attunement:** No
- **Snippet:** Within 1 hour, use an action to exhale a 30-ft cone: 6d8 cold, DEX save half.
- **Description:** After drinking, for the next hour you can use an action to exhale a 30-foot cone of freezing vapor. Each creature in the cone makes a Dexterity saving throw, taking 6d8 cold damage on a failure, or half as much on a success. Once used, the elixir is spent.

### Potion of Footing
- **Type:** Potion · **Rarity:** Common · **Attunement:** No
- **Snippet:** 1 hour: ice and snow aren't difficult terrain for you; you can't be knocked prone on frozen ground.
- **Description:** For 1 hour, ice and snow are not difficult terrain for you, and you cannot be knocked prone while standing on frozen ground.

## Throwables (Adventuring Gear, consumable)

### Frost-Bomb
- **Type:** Adventuring Gear (thrown) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Thrown; 10-ft radius: 3d6 cold, DEX save or restrained until end of next turn.
- **Description:** As an action, throw this flask up to 60 feet. Each creature within 10 feet of where it lands makes a Dexterity saving throw, taking 3d6 cold damage and being restrained until the end of its next turn on a failure.

### Rime Flask
- **Type:** Adventuring Gear (thrown) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** 15-ft radius becomes difficult ice terrain for 1 min; creatures there on impact make STR save or fall prone.
- **Description:** On impact, a 15-foot-radius area is sheathed in ice, becoming difficult terrain for 1 minute. Each creature in the area when it lands makes a Strength saving throw, falling prone on a failure.

### Shatterfrost Vial
- **Type:** Adventuring Gear (thrown) · **Rarity:** Rare · **Attunement:** No
- **Snippet:** 15-ft radius: 5d6 cold (DEX half); creatures that fail also take 1d6 piercing from ice shards.
- **Description:** Throw up to 60 feet. Each creature within 15 feet makes a Dexterity saving throw, taking 5d6 cold damage on a failure (half on a success). A creature that fails also takes 1d6 piercing damage from exploding ice shards.

### Hoarfrost Smoke
- **Type:** Adventuring Gear (thrown) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** 20-ft radius of freezing fog (heavily obscured) for 1 min; creatures starting their turn inside have speed halved.
- **Description:** Creates a 20-foot-radius sphere of freezing fog for 1 minute; the area is heavily obscured. A creature that starts its turn in the fog has its speed halved until the start of its next turn.

### Cryostasis Flask
- **Type:** Adventuring Gear (thrown) · **Rarity:** Rare · **Attunement:** No
- **Snippet:** Single target: 4d8 cold and slowed (as the spell) 1 min, CON save ends at end of each of its turns.
- **Description:** Hurled at one creature within 30 feet. The target takes 4d8 cold damage and is affected by the Slow spell for 1 minute. At the end of each of its turns, it may make a Constitution saving throw, ending the effect on a success.

### Glacier Caltrops (bag)
- **Type:** Adventuring Gear · **Rarity:** Common · **Attunement:** No
- **Snippet:** Cover a 5-ft square; a creature entering takes 1d4 cold + 1d4 piercing and speed −10 ft until its next turn.
- **Description:** Scatter to cover a 5-foot square. A creature that enters the area takes 1d4 cold and 1d4 piercing damage, and its speed is reduced by 10 feet until the start of its next turn.

### Avalanche Pellet
- **Type:** Adventuring Gear (thrown) · **Rarity:** Rare · **Attunement:** No
- **Snippet:** 20-ft radius: 6d6 cold + 2d6 bludgeoning, DEX save half; area becomes ice rubble (difficult terrain).
- **Description:** On impact a slab of ice erupts. Each creature within 20 feet makes a Dexterity saving throw, taking 6d6 cold plus 2d6 bludgeoning damage on a failure (half on a success). The area becomes ice rubble — difficult terrain — for 1 minute.

## Oils & Coatings

### Cold-Infused Oil
- **Type:** Adventuring Gear · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Coat a weapon: +1d4 cold on hits for 1 hour (up to 10 hits).
- **Description:** Applied as an action to one weapon or up to 5 pieces of ammunition. For 1 hour (or until 10 hits are made), the weapon deals an extra 1d4 cold damage on a hit.

### Biting Frost Oil
- **Type:** Adventuring Gear · **Rarity:** Rare · **Attunement:** No
- **Snippet:** 1 hour: the weapon's cold damage ignores resistance; on a crit the target can't regain HP until end of its next turn.
- **Description:** For 1 hour after application, the coated weapon's cold damage ignores resistance. On a critical hit, the target can't regain hit points until the end of its next turn.

### Rimeward Wax
- **Type:** Adventuring Gear · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Coat armor; the next time you take cold damage within 1 hour, halve it (one use).
- **Description:** Rubbed onto armor as an action. The next time you take cold damage within the following hour, you take half that damage. The wax is then spent.

### Slick-Ice Grease
- **Type:** Adventuring Gear · **Rarity:** Common · **Attunement:** No
- **Snippet:** Coat a surface or object; the first creature to climb or grab it makes a save or loses its grip.
- **Description:** Smear over a 5-foot surface or an object. The first creature to climb the surface or grab the object must succeed on a Dexterity saving throw or fail the attempt, losing its grip.

## Other Items

### Frostfang Spike
- **Type:** Adventuring Gear · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Throw (60 ft) for 2d6 cold, or plant to freeze a 10-ft pool/ground solid for 10 min.
- **Description:** A fang shod for throwing. As an action, hurl it up to 60 feet as a ranged attack dealing 2d6 cold damage on a hit; or drive it into water or ground to freeze a 10-foot square solid for 10 minutes.

### Heartfrost Ember
- **Type:** Adventuring Gear · **Rarity:** Rare · **Attunement:** No
- **Snippet:** Crush to flash-freeze: extinguishes nonmagical fire in 20 ft and ends a fire spell of 3rd level or lower (caster's check).
- **Description:** Crush as an action. All nonmagical fire within 20 feet is snuffed, and any ongoing fire spell of 3rd level or lower in that area ends if you succeed on an ability check (DC 10 + the spell's level).

### Dragon's Eye Marble
- **Type:** Wondrous Item · **Rarity:** Rare · **Attunement:** No
- **Snippet:** Once: cast Clairvoyance (sight only) anchored to a visible spot; the watching eye lingers 10 minutes.
- **Description:** A polished sphere of dragon-eye. As an action, cast Clairvoyance (sight only, no material component) anchored to a point you can see. The sensor manifests as a faint, watching eye and lasts up to 10 minutes. The marble is then spent.

### Coldfire Candle
- **Type:** Wondrous Item · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** Burns 1 hour with cold blue light (no heat); creatures within 5 ft have disadvantage on saves vs. your cold spells.
- **Description:** Burns with a heatless blue flame for 1 hour, shedding bright light in a 10-foot radius. While it burns, creatures within 5 feet of the candle have disadvantage on saving throws against cold spells you cast.

### Frostbreath Whistle
- **Type:** Wondrous Item · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** One blast: 15-ft cone of sleet, CON save or blinded until end of next turn (no damage).
- **Description:** Carved from dragon horn. As an action, blow it to loose a 15-foot cone of stinging sleet. Each creature in the cone makes a Constitution saving throw or is blinded until the end of its next turn. The whistle's charge then needs a long rest to renew.

### Rime Ration
- **Type:** Adventuring Gear · **Rarity:** Common · **Attunement:** No
- **Snippet:** Eat before a long rest in the cold: ignore extreme-cold exposure 24 hr; +1d4 to your next CON save.
- **Description:** A frost-cured trail food. Eaten before a long rest, it lets you ignore the effects of extreme cold for 24 hours, and you add 1d4 to the next Constitution saving throw you make during that time.

### Gizzard Luckstone
- **Type:** Wondrous Item · **Rarity:** Common · **Attunement:** No
- **Snippet:** One use: reroll one d20 before the result is read.
- **Description:** A stone worn smooth inside a dragon. Once, before the outcome of any d20 roll you make is determined, you may reroll it and use the new result. The stone then crumbles.

### Wand of Frost
- **Type:** Wand · **Rarity:** Rare · **Attunement:** Yes (by a spellcaster)
- **Snippet:** 7 charges; cast Ray of Frost (0), Ice Knife (1 charge), or Sleet Storm (3 charges). Regains 1d6+1 at dawn.
- **Description:** Cut from a dragon's horn. It has 7 charges. While holding it you can expend charges to cast Ray of Frost (0 charges), Ice Knife (1 charge), or Sleet Storm (3 charges), using your spell save DC. It regains 1d6+1 charges daily at dawn; if you spend its last charge, roll a d20 — on a 1 it crumbles to frost.

### Frill-Spine Arcane Focus
- **Type:** Wondrous Item (arcane focus) · **Rarity:** Uncommon · **Attunement:** No
- **Snippet:** While held as a focus, +1 to spell attack rolls of evocation spells.
- **Description:** A wand-like spine from the dragon's frill. While you hold it as a spellcasting focus, you gain a +1 bonus to spell attack rolls you make with evocation spells.

### Pendant of the Spiteful Eye
- **Type:** Wondrous Item · **Rarity:** Rare · **Attunement:** Yes
- **Snippet:** While attuned, cast Detect Thoughts once per day; the dragon's memory makes it feel like the eye watches.
- **Description:** A dragon's eye set in cold silver. While attuned, you can cast Detect Thoughts (save DC 13) once per day without expending a spell slot. Some bearers report the unsettling sense of being watched in return.

### Catalyst (reagent, not a sheet item)
**Heartfrost Residue / Cold-Property Catalyst** — consumed during crafting to add a cold-damage rider to an item already in production, with no rarity increase. Track as a material, not a D&D Beyond item entry.
