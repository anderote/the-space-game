# Research tree: source research and shipped design

Implemented 2026-10-11. Persistent research is a modern addition, not a recovered feature of the original campaign. Original in-mission structure upgrades and Pulser/THEL branching remain baseline mechanics. The current definitions are in [research.js](../web/src/research.js).

## Five primary sources and useful lessons

1. **Factorio developer API: TechnologyPrototype.** Its technology definition separates prerequisites, research cost/trigger, applied effects, and presentation flags. That is a useful data model for a small browser game too: keep conditions and outcomes inspectable instead of embedding purchasing rules in button handlers. [Official prototype documentation](https://lua-api.factorio.com/latest/prototypes/TechnologyPrototype.html)
2. **Factorio developers: Friday Facts #376.** The team describes action-triggered technologies, such as mining or crafting something, to connect progression to actually using a system. The post also describes avoiding temporary research machinery that becomes disposable clutter. Our inference: award Intel through mining and combat activity as well as completed operations and milestones, without requiring a separate research building in the original combat loop. [Research and Technology](https://www.factorio.com/blog/post/fff-376)
3. **Mindustry: official Serpulo technology-tree source.** The actual tree combines parent nodes with sector-completion and researched-content objectives, and groups related infrastructure into branches. Our inference: tie advanced research to demonstrated campaign progress, while keeping a short, visible dependency graph. We should not copy Mindustry's much larger graph or resource costs. [Developer repository, SerpuloTechTree.java](https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/content/SerpuloTechTree.java)
4. **Subset Games: FTL.** The developer's description emphasizes alternative responses to a crisis, including reallocating power or powering more weapons. Our inference: upgrades should strengthen distinct economy, power, firepower and recovery plans, while stronger weapons still need adequate energy. Permanent research must not erase the original network's constraints. [Official FTL page](https://www.subsetgames.com/ftl.html)
5. **Subset Games: Into the Breach.** The developer emphasizes readable enemy attacks, counterplay, and finding new weapons/pilots. Our inference: preview exact research effects and expose changed targeting behavior clearly; avoid hidden global combat modifiers and random critical-hit bonuses. This page does not document reactor-core arithmetic, so this brief makes no sourced claim about those details. [Official Into the Breach page](https://www.subsetgames.com/itb.html)

These sources establish facts about those games. The following rules, numbers, currency schedule and node designs are our proposed adaptation, not claims that those games use this particular progression.


## Implemented progression

Four branches × five technologies. Each uses a diamond prerequisite graph: entry → two specializations → advanced technology → capstone. Prices are 2 / 4 / 4 / 6 / 9 Intel, or 25 per complete branch and 100 for the complete tree.

Every profile begins with 6 Intel. Actual extraction banks **1 Intel per 200 minerals**, and **5 enemy ships defeated by player weapons bank 1 Intel**. Mining research increases the actual extraction that counts. Recycling refunds and starting cargo do not count as mining; intercepted projectiles and ships that detonate themselves do not count as defeated ships. Escorts eliminated with a defeated mothership do count. Partial progress carries across operations, including defeats and restarts. Replaying a mission can earn activity Intel through fresh mining and combat.

New best Expedition and Challenge stars additionally earn 2 Intel each; each newly cleared five-wave Endless milestone earns 4. Repeating an unchanged achievement cannot multiply this achievement reward. Calling a wave without defeating its ships earns nothing. Sandbox and Classic do not award research Intel. Existing profiles receive credit for already-earned stars.

The profile saves lifetime eligible extraction/defeats, and each operation snapshot saves the last credited counters and its field-Intel earnings. Banking takes only the positive uncredited delta; profile and checkpoint are serialized together in the same localStorage write. Reloading or resuming therefore cannot award the same activity twice. Old snapshots start their activity checkpoint at migration and earn from subsequent play; earlier activity is not retroactively estimated. Export/import includes lifetime activity totals, while imported operation snapshots remain disabled.

Purchased technologies are available permanently until a free respec. A deployment has 6 slots; ordinary technologies weigh 1 and capstones weigh 2. A whole branch fills all 6 slots, or the player can mix specialties. Prerequisites must be researched but do not need to remain equipped. Selecting an owned technology offers Equip/Unequip; purchases auto-equip if space is available. Full respec refunds exactly the invested Intel.

Research works in Expedition, Challenge, Endless and Sandbox operations. Press **I**, click the HUD Intel counter, or use the mission menu to open the full tree during play. The operation pauses; buying, equipping, unequipping and confirming a free respec update its existing and future structures immediately. Returning with Escape or the return button restores the previous running/paused state. The HUD exposes the available balance and acquisition progress; the tree shows separate mining and combat progress bars. Classic always uses baseline rules.

Saved operations store their active IDs. Command changes leave the saved configuration intact until its in-game tree is opened. On opening, the deployed IDs still owned in the profile become the editable loadout; a technology refunded in Command is removed from the run at that point. Live changes also become the profile's next-launch configuration. Old active saves begin with no research effects.

Live hull changes preserve health percentage, capacity increases create no energy, capacity decreases clamp existing reserves, and link-range changes rebuild eligible connections while retaining obstruction and degree limits. Existing drones have excess energy clamped when endurance is removed. **Expedition freight is explicitly launch-only:** equipping it mid-operation never adds cargo, and restoring a snapshot never re-awards cargo. Multiple generation modifiers multiply, so Prismatic cells and Stellar overdrive together give 1.2 × 1.4 = 1.68 generation.

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

The UI displays every node, prerequisite connection, cost, loadout weight, availability state and exact effect. Color is reinforced by Locked / Available / Need Intel / Researched / Equipped text. The selected node explains the effect and unmet requirements. A deployment summary appears in the briefing and the live in-mission research tree. On narrow screens the tree becomes one branch per row and selecting a node scrolls to its detail.

## Validation and tuning limits

Tests cover the graph, purchase eligibility, single charges, best-star and cleared-wave earnings, free refunds, six-slot weighting, old saves, run isolation, Classic isolation and actual simulation effects. Regression tests additionally cover actual extraction, combat attribution, partial carryover, loss banking, save checkpoints, old-save migration, live effects and health/energy/cargo conservation. Browser checks verify live purchasing, pause/return behavior, Intel accrual, prerequisites, respec and desktop/narrow layouts.

The numbers are an initial playable balance, not the result of a long campaign-wide tuning study. The early research proposal considered more modest automatic bonuses and fixed-rule challenges; the final implementation uses stronger bonuses constrained by a six-slot loadout and applies them to all explicitly modern modes. There are no research wait timers, daily gates, payments or backend services.
