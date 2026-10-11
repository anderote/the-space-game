# Research tree: source research and shipped design

Implemented 2026-10-11. Persistent research is a modern addition, not a recovered feature of the original campaign. Original in-mission structure upgrades and Pulser/THEL branching remain baseline mechanics. The current definitions are in [research.js](../web/src/research.js).

## Five primary sources and useful lessons

1. **Factorio developer API: TechnologyPrototype.** Its technology definition separates prerequisites, research cost/trigger, applied effects, and presentation flags. That is a useful data model for a small browser game too: keep conditions and outcomes inspectable instead of embedding purchasing rules in button handlers. [Official prototype documentation](https://lua-api.factorio.com/latest/prototypes/TechnologyPrototype.html)
2. **Factorio developers: Friday Facts #376.** The team describes action-triggered technologies, such as mining or crafting something, to connect progression to actually using a system. The post also describes avoiding temporary research machinery that becomes disposable clutter. Our inference: award Intel through meaningful completed operations and milestones, without introducing a second mining-like resource or a mandatory research building into the original combat loop. [Research and Technology](https://www.factorio.com/blog/post/fff-376)
3. **Mindustry: official Serpulo technology-tree source.** The actual tree combines parent nodes with sector-completion and researched-content objectives, and groups related infrastructure into branches. Our inference: tie advanced research to demonstrated campaign progress, while keeping a short, visible dependency graph. We should not copy Mindustry's much larger graph or resource costs. [Developer repository, SerpuloTechTree.java](https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/content/SerpuloTechTree.java)
4. **Subset Games: FTL.** The developer's description emphasizes alternative responses to a crisis, including reallocating power or powering more weapons. Our inference: upgrades should strengthen distinct economy, power, firepower and recovery plans, while stronger weapons still need adequate energy. Permanent research must not erase the original network's constraints. [Official FTL page](https://www.subsetgames.com/ftl.html)
5. **Subset Games: Into the Breach.** The developer emphasizes readable enemy attacks, counterplay, and finding new weapons/pilots. Our inference: preview exact research effects and expose changed targeting behavior clearly; avoid hidden global combat modifiers and random critical-hit bonuses. This page does not document reactor-core arithmetic, so this brief makes no sourced claim about those details. [Official Into the Breach page](https://www.subsetgames.com/itb.html)

These sources establish facts about those games. The following rules, numbers, currency schedule and node designs are our proposed adaptation, not claims that those games use this particular progression.


## Implemented progression

Four branches × five technologies. Each uses a diamond prerequisite graph: entry → two specializations → advanced technology → capstone. Prices are 2 / 4 / 4 / 6 / 9 Intel, or 25 per complete branch and 100 for the complete tree.

Every profile begins with 6 Intel. New best Expedition and Challenge stars earn 2 each; each newly cleared five-wave Endless milestone earns 4. Earnings are derived from persistent best achievements, so repeats, reloads, and importing the same save cannot multiply rewards. Calling a wave without defeating its ships earns nothing. Sandbox and Classic do not award research Intel. Existing profiles receive credit for already-earned stars.

Purchased technologies are available permanently until a free respec. A deployment has 6 slots; ordinary technologies weigh 1 and capstones weigh 2. A whole branch fills all 6 slots, or the player can mix specialties. Prerequisites must be researched but do not need to remain equipped. Selecting an owned technology offers Equip/Unequip; purchases auto-equip if space is available. Full respec refunds exactly the invested Intel.

Research applies to newly launched Expedition, Challenge, Endless and Sandbox operations. Classic always uses baseline rules. A saved operation stores its equipped IDs, preserving its launch configuration through later purchases and respecs; starting cargo is never re-awarded on resume. Old active saves have an empty research loadout. Multiple generation modifiers multiply, so Prismatic cells and Stellar overdrive together give 1.2 × 1.4 = 1.68 generation.

## Technology table

| Branch | Technology | Intel | Slots | Requires | Actual effect |
| --- | --- | ---: | ---: | --- | --- |
| Power systems | Prismatic cells | 2 | 1 | None | +20% solar generation |
| Power systems | Dense capacitors | 4 | 1 | Prismatic cells | +40% energy-store capacity |
| Power systems | Field couplers | 4 | 1 | Prismatic cells | +15 energy-link range |
| Power systems | Storm shielding | 6 | 1 | Dense capacitors + Field couplers | 50% solar output during storms |
| Power systems | Stellar overdrive | 9 | 2 | Storm shielding | +40% generation · −20% solar hull |
| Deep-space industry | Resonant drills | 2 | 1 | None | +25% minerals per mining cycle |
| Deep-space industry | Survey optics | 4 | 1 | Resonant drills | +15 mining range |
| Deep-space industry | Rapid fabrication | 4 | 1 | Resonant drills | 25% faster construction and upgrades |
| Deep-space industry | Closed-loop recovery | 6 | 1 | Survey optics + Rapid fabrication | Recover 80% of upgrade minerals |
| Deep-space industry | Expedition freight | 9 | 2 | Closed-loop recovery | +300 starting minerals |
| Applied ballistics | Focus lenses | 2 | 1 | None | +15% laser and Pulser damage |
| Applied ballistics | Predictive guidance | 4 | 1 | Focus lenses | +15% missile range · +25% speed |
| Applied ballistics | Pulse reservoirs | 4 | 1 | Focus lenses | +50% weapon energy buffers |
| Applied ballistics | Beam coherence | 6 | 1 | Predictive guidance + Pulse reservoirs | +25% THEL damage and energy use |
| Applied ballistics | Proximity warheads | 9 | 2 | Beam coherence | +30% blast radius · −15% missile damage |
| Field engineering | Composite hulls | 2 | 1 | None | +15% structure hull |
| Field engineering | Precision repair | 4 | 1 | Composite hulls | +25% drone repair throughput |
| Field engineering | Drone endurance | 4 | 1 | Composite hulls | +50% carried drone energy |
| Field engineering | Autoseal plating | 6 | 1 | Precision repair + Drone endurance | Powered hull regeneration after 8s |
| Field engineering | Capacitive armor | 9 | 2 | Autoseal plating | Absorb 25% incoming damage with power |

## Keeping the choices meaningful

Higher damage still consumes power, finite ore stays finite, stores only charge from solar, and link obstructions remain. Research does not lock any original control, interception, repair, pause or recycling feature. Overdrive sacrifices solar hull; proximity warheads sacrifice single-target damage; amplified THEL damage increases its energy use. Autoseal and capacitive armor explicitly draw from the existing energy system. Hull bonuses exclude the supplied mission-critical derelict. Salvage improves upgrade refunds without returning more than total paid cost.

The UI displays every node, prerequisite connection, cost, loadout weight, availability state and exact effect. Color is reinforced by Locked / Available / Need Intel / Researched / Equipped text. The selected node explains the effect and unmet requirements. A deployment summary appears in the briefing and an in-mission research dialog. On narrow screens the tree becomes one branch per row and selecting a node scrolls to its detail.

## Validation and tuning limits

Tests cover the graph, purchase eligibility, single charges, best-star and cleared-wave earnings, free refunds, six-slot weighting, old saves, run isolation, Classic isolation and actual simulation effects. Browser checks verify purchasing, prerequisite unlocks, denied purchases, visible bonus generation/hull, active-run summaries, respec and desktop/narrow layouts.

The numbers are an initial playable balance, not the result of a long campaign-wide tuning study. The early research proposal considered more modest automatic bonuses and fixed-rule challenges; the final implementation uses stronger bonuses constrained by a six-slot loadout and applies them to all explicitly modern modes. There are no research wait timers, daily gates, payments or backend services.
