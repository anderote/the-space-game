# Research tree: source research and shipped design

Implemented 2026-10-11. Persistent research is a modern addition, not a recovered feature of the original campaign. Original in-mission structure upgrades and Pulser/THEL branching remain baseline mechanics. The current definitions are in [research.js](../web/src/research.js).

## Five primary sources and useful lessons

1. **Factorio developer API: TechnologyPrototype.** Its technology definition separates prerequisites, research cost/trigger, applied effects, and presentation flags. That is a useful data model for a small browser game too: keep conditions and outcomes inspectable instead of embedding purchasing rules in button handlers. [Official prototype documentation](https://lua-api.factorio.com/latest/prototypes/TechnologyPrototype.html)
2. **Factorio developers: Friday Facts #376.** The team describes action-triggered technologies, such as mining or crafting something, to connect progression to actually using a system. The post also describes avoiding temporary research machinery that becomes disposable clutter. Our inference: earn XP through mining, combat and repairs, with Intel reserved for rare-ship kills, without requiring a separate research building in the original combat loop. [Research and Technology](https://www.factorio.com/blog/post/fff-376)
3. **Mindustry: official Serpulo technology-tree source.** The actual tree combines parent nodes with sector-completion and researched-content objectives, and groups related infrastructure into branches. Our inference: tie advanced research to demonstrated campaign progress, while keeping a short, visible dependency graph. We should not copy Mindustry's much larger graph or resource costs. [Developer repository, SerpuloTechTree.java](https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/content/SerpuloTechTree.java)
4. **Subset Games: FTL.** The developer's description emphasizes alternative responses to a crisis, including reallocating power or powering more weapons. Our inference: upgrades should strengthen distinct economy, power, firepower and recovery plans, while stronger weapons still need adequate energy. Permanent research must not erase the original network's constraints. [Official FTL page](https://www.subsetgames.com/ftl.html)
5. **Subset Games: Into the Breach.** The developer emphasizes readable enemy attacks, counterplay, and finding new weapons/pilots. Our inference: preview exact research effects and expose changed targeting behavior clearly; avoid hidden global combat modifiers and random critical-hit bonuses. This page does not document reactor-core arithmetic, so this brief makes no sourced claim about those details. [Official Into the Breach page](https://www.subsetgames.com/itb.html)

These sources establish facts about those games. The following rules, numbers, currency schedule and node designs are our proposed adaptation, not claims that those games use this particular progression.


## Implemented progression

Four branches contain ten technologies each, spanning eight tiers. Each branch starts with a diamond prerequisite sequence, then expands into a second fork, a merge and two deeper upgrades. Original twenty research IDs and purchases are preserved. A whole branch costs 69 Intel; all forty cost 276.

Every profile begins with 6 Intel. A gold-marked elite appears as the first ordinary ship of every third modern wave, with 60% additional hull and 2 Intel on player defeat. Motherships carry 3 Intel. Deaths from self-destruction, inherited escort cleanup or intercepted missiles cannot award Intel. Intel is awarded directly at defeat, with a gold marker before the kill and a floating reward afterward. Ordinary ships and mining award XP instead. New medals and wave records do not mint Intel.

Every purchased technology stays active: no equipment slots, weight limits or equip/unequip controls. Dependencies must be researched; purchasing deducts the listed Intel once. Free technology respec refunds the exact invested Intel and preserves XP/base stats. Some mid-tree technologies retain explicit tradeoffs: solar overdrive reduces hull, broader warheads reduce impact damage, and stronger THEL beams consume proportionally more energy. Later upgrades can offset these costs.

Research and XP persist across games and campaigns. Expedition, Challenges and Endless earn progression. Sandbox uses existing bonuses but awards no Intel/XP. Classic disables both research and XP modifiers. Press I, the HUD progression counter or the mission-menu Research button to pause and open Technology tree / Base stats. The previous pause state returns on exit.

## Command XP and base stats

| Activity | XP | Accounting |
| --- | ---: | --- |
| Actual extraction | 1 per 5 minerals | Finite ore removed by miners; no cargo or recycle refunds |
| Enemy hull damage | 1 per 20 HP | Actual damage, excluding shields, overkill and projectiles |
| Battle-damage repairs | 1 per 10 HP | Drone/autoseal restoration of recorded incoming damage or initial objective damage; no drone dock servicing |

The first level takes 100 XP, then 150, 200, 250 and so on. Each level grants one stat point. Every base-stat track costs one point per rank and caps at twenty. Tower mastery uses the same point pool, with seven base tracks and 52 tower-specific tracks total. Technology and stat multipliers stack.

| Base stat | Per rank | Maximum bonus |
| --- | --- | --- |
| Armor | 2 percentage points incoming hull damage reduction | 40% reduction |
| Clock speed | +5% construction, mining and solar cycle speed | +100% |
| Harvesting | +5% minerals per cycle | +100% |
| Firepower | +3% laser/Pulser/THEL/missile damage | +60% |
| Repair efficiency | +5% drone throughput | +100% |
| Power output | +5% energy per solar pulse | +100% |
| Efficient fabrication | 1% cheaper buildings/upgrades | 20% discount |

Armor reduces hull damage before powered shielding, while derelict mission objectives retain baseline behavior. Clock speed preserves cost per construction/mining increment and energy per solar pulse; output/yield ranks separately improve each pulse. Existing Build speed ranks retain their fabrication ID and become Clock speed. Efficient fabrication discounts the actual charged price, with refunds based on historical amounts paid. Harvesting consumes finite ore faster. Repairs continue spending one drone energy per healed hull. Firepower raises THEL’s energy demand as well as damage. Rank increases apply immediately when purchased in an active operation.

## Tower mastery

A third progression tab specializes nine classes: relay, miner, solar, energy store, repair, Basic laser, Pulser, THEL and missile. Their 52 tracks cover appropriate combat/utility improvements plus health, armor and powered shields on every class. Each rank costs one shared XP point. Purchases apply to existing and future buildings of that class, stack with technology/base stats, and persist. Classic disables them. Mineral tier upgrades remain separate. The complete effects and conservation rules are in [TOWER_MASTERY.md](TOWER_MASTERY.md).

## Saves, migration and reset

The profile holds Intel and XP; snapshots hold cumulative collected rewards and their last banked counters. Only positive uncredited deltas are banked, and profile plus snapshot are saved together. Reloading cannot duplicate a kill or mining cycle. Legacy snapshots begin the new counters at migration.

The old currency schedule is frozen into a one-time legacy Intel credit, preserving existing balances and purchases. All valid owned technology IDs become active, including formerly unequipped upgrades. Recorded historical mining/combat totals convert once into XP at 0.2 XP/mineral and 5 XP/recorded kill; historical repair activity is not estimated. Legacy conversion disappears after the new profile schema is saved.

On launch or resume, the UI applies the current profile’s full technology tree, base-stat ranks and tower mastery. Live hull changes preserve health percentage, reserve increases do not charge free energy, reserve decreases clamp stored energy, and link changes rebuild eligible connections. Freight adds cargo only to a new operation; it never adds cargo on resuming or purchasing mid-operation.

Settings offers Start fresh: save a local backup and download the previous profile before clearing campaign records, technologies, Intel, XP, stats and the active operation. Settings remain. Other tabs receive the reset marker and stop autosaving an old operation. The owner requested one fresh reset on 2026-10-11; persistence remains enabled afterward.

## Technology table

| Branch | Technology | Intel | Requires | Effect |
| --- | --- | ---: | --- | --- |
| Power systems | Prismatic cells | 2 | None | +20% solar generation |
| Power systems | Dense capacitors | 4 | Prismatic cells | +40% energy-store capacity |
| Power systems | Field couplers | 4 | Prismatic cells | +15 energy-link range |
| Power systems | Storm shielding | 6 | Dense capacitors + Field couplers | 50% solar output during storms |
| Power systems | Stellar overdrive | 9 | Storm shielding | +40% generation · −20% solar hull |
| Power systems | Relay lattice | 6 | Stellar overdrive | +15 energy-link range |
| Power systems | Buffer matrix | 6 | Stellar overdrive | +35% storage · +25% weapon buffers |
| Power systems | Fusion cells | 8 | Relay lattice + Buffer matrix | +15% generation · +25% solar hull |
| Power systems | Storm harvest | 10 | Fusion cells | 80% solar output during storms |
| Power systems | Dyson petals | 14 | Storm harvest | +30% generation · +25% storage |
| Deep-space industry | Resonant drills | 2 | None | +25% minerals per mining cycle |
| Deep-space industry | Survey optics | 4 | Resonant drills | +15 mining range |
| Deep-space industry | Rapid fabrication | 4 | Resonant drills | 25% faster construction and upgrades |
| Deep-space industry | Closed-loop recovery | 6 | Survey optics + Rapid fabrication | Recover 80% of upgrade minerals |
| Deep-space industry | Expedition freight | 9 | Closed-loop recovery | +300 starting minerals |
| Deep-space industry | Deep-core resonance | 6 | Expedition freight | +25% minerals per cycle |
| Deep-space industry | Belt tomography | 6 | Expedition freight | +20 mining range |
| Deep-space industry | Orbital nanoforge | 8 | Deep-core resonance + Belt tomography | +35% construction speed |
| Deep-space industry | Total reclamation | 10 | Orbital nanoforge | Recover 100% of upgrade minerals |
| Deep-space industry | Orbital supply chain | 14 | Total reclamation | +600 starting minerals |
| Applied ballistics | Focus lenses | 2 | None | +15% laser and Pulser damage |
| Applied ballistics | Predictive guidance | 4 | Focus lenses | +15% missile range · +25% speed |
| Applied ballistics | Pulse reservoirs | 4 | Focus lenses | +50% weapon energy buffers |
| Applied ballistics | Beam coherence | 6 | Predictive guidance + Pulse reservoirs | +25% THEL damage and energy use |
| Applied ballistics | Proximity warheads | 9 | Beam coherence | +30% blast radius · −15% missile damage |
| Applied ballistics | Beam lattice | 6 | Proximity warheads | +20% laser, Pulser and THEL damage |
| Applied ballistics | Smart payloads | 6 | Proximity warheads | +25% missile damage |
| Applied ballistics | Deep-field targeting | 8 | Beam lattice + Smart payloads | +20% beam range · +15% missile range |
| Applied ballistics | Siege capacitors | 10 | Deep-field targeting | +50% weapon energy buffers |
| Applied ballistics | Singularity arsenal | 14 | Siege capacitors | +20% all weapon damage · +15% blast |
| Field engineering | Composite hulls | 2 | None | +15% structure hull |
| Field engineering | Precision repair | 4 | Composite hulls | +25% drone repair throughput |
| Field engineering | Drone endurance | 4 | Composite hulls | +50% carried drone energy |
| Field engineering | Autoseal plating | 6 | Precision repair + Drone endurance | Powered hull regeneration after 8s |
| Field engineering | Capacitive armor | 9 | Autoseal plating | Absorb 25% incoming damage with power |
| Field engineering | Reactive plating | 6 | Capacitive armor | +20% structure hull |
| Field engineering | Autonomous servicing | 6 | Capacitive armor | +30% repair · +30% drone reserves |
| Field engineering | Redundant shields | 8 | Reactive plating + Autonomous servicing | 35% powered damage absorption |
| Field engineering | Field restoration | 10 | Redundant shields | +40% drone repair throughput |
| Field engineering | Citadel protocol | 14 | Field restoration | +25% hull · 45% powered absorption |

## Validation and tuning

Tests cover the complete dependency graph, all-active purchasing, migration, persistence, rare drops, XP thresholds, actual stat effects, repair/combat attribution, energy conservation, save idempotency and recoverable reset. Browser checks cover the expanded tree, base-stat purchases, import, live pause/return and new-launch modifiers. Balance is initial tuning; full campaign and long-duration Endless playtesting remain. No research wait timers, payments or backend services are introduced.
