# Original combat and controls fidelity audit

**Audit snapshot:** many discrepancies below were fixed during this implementation. See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for the current shipped behavior and remaining gaps.

Audit date: 2026-10-11. This is a bounded comparison of the archived **original The Space Game v83**, not the separate Missions sequel, against the browser port's `web/src/{engine,classic,content,main,renderer}.js`. The implementation was being updated during the audit; findings describe the inspected snapshot and should be checked against the latest code before treating them as outstanding defects.

## Evidence and confidence

Primary artifact: `10-thespacegame.v83.swf`, 1,942,037 bytes, SHA-256 `8d193481fb87e994a53d390a96bf9774b26fa5d479e4af2f0e1dd3497955d237`, from the [Flashpoint original-game data pack](https://download.unstable.life/gib-roms/Games/944ea5a3-558d-feda-4eb7-e900f3e60b06-1631483058057.zip). Private inspection directory: `/tmp/the-space-game-research/original-scripts/scripts`. Paths and line numbers below refer to that local JPEXS export. No extracted implementation, executable or original assets are included here.

The executable is obfuscated. Some classes retain coherent methods with names; others retain coherent arithmetic and control flow with constant-pool references. Several exported files also contain unreachable-looking duplicate classes and damaged decompiler output. This report uses coherent branches, labels timing assumptions, and does not claim live original-emulator verification. Nominal 20 Hz timings use the moving/building update rate already recorded in [ORIGINAL_MECHANICS.md](ORIGINAL_MECHANICS.md). Frame-perfect claims need a measured replay.

## Highest-impact combat differences

| Priority | Original behavior and evidence | Port observed during audit | Required outcome |
| --- | --- | --- | --- |
| P0 | Basic/Pulser weapons fire multi-tick bursts, with distinct acquisition, firing and cooldown counters. `__Packages/buildingLaser.as:600–675`. | `Simulation.update()` uses one instantaneous hit per approximate interval. | Reproduce burst counters and local energy discharge. The current damage field is not damage per complete shot. |
| P0 | A player missile striking a type-4 Ringer has its impact damage divided by 15. `__Packages/rocket.as:155–184`. | `damageEnemy()` uses a finite 140-point shield for general damage, and THEL bypasses it. | Treat the Ringer trait as missile resistance, with a transient visual hit shield. No laser damage reduction was found in the inspected laser path. |
| P0 | `splash()` applies full integer damage to its direct target, then linear distance falloff to neighbors. `frame_2/DoAction.as:1300–1308`. | Every enemy in player missile splash radius receives full damage. Self-destructor splash is centered on the ship. | Center on the impact target; adjacent damage is approximately `floor(damage * (1 - distance / radius))`. Keep direct target separate from neighbors to avoid double damage. |
| P0 | Mothership creates **five** children once, on first valid attack target. It forwards later targets to those children; when no valid target remains, children return toward parent. Its death kills all its children. `__Packages/ship6.as:189–199, 265–314`. | Three children every 11 seconds indefinitely; no parent ownership or parent-death cleanup. | Track parent and fixed escort group, shared orders, recall and parent death. This changes both threat growth and boss-clear conditions. |
| P0 | Most hostile archetypes attack with immediate laser damage; missile ship alone uses destructible homing rockets. Mothership uses continuous `damageParameter / 50` per moving tick. `__Packages/ship6.as:318–339`, original enemy records. | All non-suicide enemies fire homing projectiles with arbitrary intervals. | Separate laser and rocket attacks. Enemy beams need neither player THEL ramp nor projectile flight time. |
| P1 | Launcher pays **5 minerals + 1 energy per launched missile**, and can reacquire a target between salvo shots. `__Packages/buildingRocket.as:223–289`. | Entire salvo paid up front; all shots hold one target; projectile disappears when target dies. | Stagger actual launch events, charge individually and permit target reacquisition. Insufficient resources can cause individual shots to be skipped. |
| P1 | Missiles have HP, accelerate, turn with easing, continue after losing a target, and search within 100 for a replacement on a retarget timer. `__Packages/rocket.as:80–199`. | Constant-speed perfect homing; target death deletes projectile; basic/Pulser interception instantly removes first qualifying rocket. | Damage missiles through normal targeting, preserve their HP, and distinguish missile death from loss of its target. |
| P1 | Self Destructor acquires a building within 70, changes visual frame, then detonates after a fuse greater than 60 moving ticks while holding a target. Blast is centered on that target. `__Packages/ship2.as:120–280`, coherent `_global.ship3` branch. | Contact explosion at range 15, no fuse. | Add readable arming state and nominal three-second fuse. Damage is 60, splash radius 100. |
| P1 | Upgrading consumes construction energy/time and disables normal operation until target construction progress is reached. `buildingLaser.as:265–394, 474–511`; `buildingRocket.as:190–219`. | `upgrade()` immediately changes type/level and HP with no construction phase. | Preserve building/upgrade eligibility and downtime; do not allow instant successive upgrades. |

### Exact Basic/Pulser cadence

These counters are supported directly by the coherent constructor, upgrade and weapon-update branches of `__Packages/buildingLaser.as:195–394, 600–675`. Names here describe their role rather than reproducing implementation identifiers.

| Weapon | Acquisition counter | Reset counter | Damage each firing tick | Energy-needed parameter | Energy per firing tick | Local recharge target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Basic | 5 | 20 | 30 | 2 | 2 / 35 | 1 |
| Pulser I | 4 | 10 | 12 | 5 | 5 / 28 | 2.5 |
| Pulser II | 4 | 8 | 14 | 10 | 10 / 28 | 5 |
| Pulser III | 4 | 6 | 16 | 15 | 15 / 28 | 7.5 |

The counter starts at zero. At the acquisition value the weapon selects a target, preferring an eligible attacker recorded by the retaliation mechanism. Below the acquisition value it fires on each tick with a live target and positive local energy. **Zero is also a firing tick** before resetting to the cooldown value; the counter is then decremented. Hence sustained Basic bursts contain five damage applications, and Pulsers contain four. On an uninterrupted target at nominal 20 Hz, resulting theoretical DPS is 150, 96, 140, and approximately 213.33 respectively. These values exclude acquisition failures, target death, starvation and construction. They are a consequence of the counters, not an invitation to replace the bursts with flat DPS.

Each firing tick subtracts `energyNeeded / 7 / acquisitionCounter`. The original tests positive reserve, rather than reserve greater than exact shot cost, so its last shot may slightly overdraw. Every other weapon tick it requests enough energy to refill to `energyNeeded / 2`. The inspected port's approximate per-shot costs and capacities therefore also change economic balance.

THEL is a different branch: acquisition starts its firing counter at 40; damage per tick is `baseDamage + (counter - 39) / 4`, and energy is damage/20. Target death sets a 20-tick reacquisition delay. Insufficient energy sets its firing counter to 20, producing a recovery period before the beam resumes, rather than merely slowing its ramp. See `buildingLaser.as:513–600`. Current port retains a similar ramp but omits the exact recovery/reacquisition semantics and deliberately prioritizes motherships, which was not found in the original selection path.

### Targeting and interception

`frame_2/DoAction.as:1230–1299` routes lasers straight into target HP. It records an attacker for eligible defending weapon types when defending range is at least attacking range. Laser/launcher branches consult that retaliation target before ordinary queries. The current nearest-enemy loop lacks this behavior.

`__Packages/cells.as:175–306` collects candidates from spatial cells and sorts ordinary queries by integer distance. Basic/Pulser include rockets; THEL excludes them. This supports missiles being ordinary competing targets, rather than an unconditional separate first-priority interception pass. The bounded-cell limit and tie ordering need live comparison before claiming exact equivalence. The current bomber preference for solar/relay/miner buildings is an authored targeting rule, not verified original behavior.

For Ringers, the verified special case occurs when the **direct missile target** is type 4, before the splash call. Therefore the original scales the entire blast passed to that call when a Ringer is hit directly. A Ringer caught in another target's blast is not separately divided by 15 by the inspected `splash()` function. This unusual asymmetry should be implemented deliberately or documented as a modern correction. Root laser damage has no equivalent type-4 modifier in the inspected branch.

## Repair drones

Primary evidence: `__Packages/buildingRepair.as:185–335` and `DefineSprite_566_repair1/frame_1/DoAction.as:463–660`.

- Four drones per station is correct. Creation requires 10 station energy, but original creation requests one unit on a recurring counter (roughly one request per 11 station ticks); the inspected port uses a continuous 3-energy/second build rate.
- New drones are assigned **20 of 60 HP**, despite their symbol's default full HP. They remain docked until fully repaired and charged; launch eligibility explicitly requires both. Current drones spawn at 60 HP and immediately qualify for work.
- Docking repairs 3 drone HP per station energy and restores 6 carried energy per station energy. Each can occur every moving tick when supply permits. Current charging is capped at 24 carried energy/second and omits drone hull repair.
- Drones have 80 carried energy; each repair tick consumes one and repairs one HP. Repair reach is **50**, not the current 35. Their movement accelerates and turns gradually; they can repair while flying/orbiting within range, instead of stopping rigidly at a distance threshold.
- Initial station dispatch uses damaged-target sorting by **largest absolute missing HP**, not lowest HP fraction. The spatial query allows the querying station itself as a repair target. Current code excludes home, preventing self-repair.
- After completing a repair, the drone can choose a random damaged target from its station query, with a nominal 20-tick delay. Station dispatch sets a 60-tick initial delay. Current direct transition has neither precise timer.
- Drones register in the spatial grid and have visible hull HP/destruction handling. Current enemy target candidates contain only buildings, so drone HP is functionally unused. Verify all enemy query filters in a live original before promising every archetype's drone-targeting behavior.

## Controls and mode semantics

The port already has the correct numbered build order and original U/Space/P/T/R, WASD/arrows, Q/E and mouse-wheel directions. Original keyboard evidence is `DefineSprite_1084/frame_1/DoAction.as:618–714`. Space and P are **not pause**. Original P/T only branch a completed basic level-one laser and reject upgrading structures; current P can perform a further Pulser upgrade and general upgrade code does not check construction. Exact original zoom bounds/steps and discrete pan easing differ from the smoother modern camera; these are lower priority than combat and can remain a labeled modern convenience.

Mining-triggered classic waves are implemented correctly in the inspected `Simulation.update()`: percentage of mining goal triggers records, independent of elapsed time or cash in hand. The nine classic missions make all seven structures available. Preserve the modern authored unlock campaign as a separate mode.

Classic survival missions 3 and 9 still use generated placeholder waves in `classic.js`/`callWave()`. Their original tables are procedural but recoverable in `__Packages/levels.as:1077–1115, 1142–1195`: scheduled times are `10 + index * 60`; Mission 3 cycles types 1–3, while Mission 9 cycles 1–6 with additional index increment at cycle wrap. Counts, spread and HP multipliers have type-specific adjustments. Use those original constructors instead of the generic increasing mixed-wave fallback.

Original Mission 6 victory has a historical early-clear condition after 190 seconds, despite further scheduled waves. The port's 35-mothership goal deliberately requires all six scheduled waves; this is a reasonable modern correction, but is not exact original victory semantics. See [ORIGINAL_MECHANICS.md](ORIGINAL_MECHANICS.md).

The source also has Survivor Gentle/Bring it/No Hope, Wave Mode, Speed Miner and Sandbox, apart from campaign difficulty. In `levels.as:1000–1063`, Wave Mode starts with 2000 pre-solar minerals, its own wave controls and an 80-asteroid field; Speed Miner starts at 400 pre-solar minerals and aims to mine its whole generated field; Sandbox starts at 100200 pre-solar minerals. The new endless mode is an addition until its generator, start resources and manual wave semantics are matched to one of these originals. Do not describe all survival variants as one identical historical endless mode.

## Suggested verification order

1. Fixed-step duel with unlimited power: count Basic/Pulser firing ticks and damage across two complete cycles; repeat with reserve starvation and target death.
2. Fire identical missiles into a Ringer and a neighboring ordinary ship; check direct resistance, integer radial falloff and splash asymmetry.
3. Kill a salvo target after the first shot; inspect resource charge times and retargeting of both launcher and airborne missiles.
4. Let a mothership acquire, lose and regain a target, then kill it: exactly five owned fighters, shared orders, no periodic growth, parent cleanup.
5. Damage the repair station itself and a high-HP structure with a small missing-health fraction; verify dispatch ranking, self-repair, dock hull repair and energy pressure.
6. Compare timed Mission 3/9 schedules from source against the classic campaign. Keep an explicit list of intentional modern differences.

These are small behavioral checks of meaningful gameplay, not screenshot-only tests. Full original playback and wall-clock measurements remain the final fidelity benchmark.
