# Browser implementation and fidelity status

Updated 2026-10-11. The full original `thespacegame.v83.swf` and `tsgmissions.v16.swf` were downloaded, hashed and privately inspected. The local excluded `.reference/` directory contains the originals and archive bundles. The browser edition distributes newly written code/assets and factual numerical reference data only. Original runtime playback has not been independently verified; source inspection and modern simulation tests are the evidence here.

## Implemented from the original audit

- Seven numbered structures and original U/Space/P/T/R shortcuts, repeated construction, camera controls and paused planning. P and T require a completed level-one basic laser.
- Source-derived early-tier prices, HP, upgrade prices, capacities, mining rates advertised by the original UI, weapon ranges, burst damage, salvos and branching. Explicit browser-edition tiers are appended to these recovered values.
- Local energy buffers, shortest-hop graph paths, farthest-hop source ordering, partial withdrawals and solar-only storage charging. Incomplete new relays block onward transfer; completed upgrading infrastructure can conduct but cannot supply. Solar generation and storage charging have separate 0.55s/1.05s cycles.
- Static blue cables plus cyan jagged flashes and node pulses only when energy actually moves. Pause freezes these effects. An idle full grid stays quiet.
- Energy-funded construction and upgrade downtime, full starting construction HP, preserved absolute damage on upgrade, staged relay chains, disconnected waiting blueprints and finite intermittent mining.
- Burst-firing Basic/Pulser, sustained energy-scaled THEL ramp and one-second recovery/reacquisition waits, missile salvos staggered by 0.75s with minerals/energy charged per projectile, homing retargeting, and destructible hostile missiles as ordinary laser targets.
- Ringer direct-hit missile resistance, linear blast falloff, self-destructor fuse/target-centered blast, immediate hostile beam attacks, five owned mothership escorts and parent-death cleanup.
- Four energy-built repair drones, initially damaged hulls, docking hull repairs, energy recharge, most-missing-HP dispatch, home repair, 50-unit reach, launch delays and finite carried energy.
- Original nine mission budgets and structure availability; mining progression triggers original wave records. Missions 3/9 use recovered numeric survival schedules and their skipped-index behavior. Classic wave spawn queues release one ship per 40Hz simulation step from the original 2,500-unit approach radius.
- Original damaged-hull recycle formula, including upgrade spending and depleted-miner group recycling.

## Modern features

12 authored Expedition missions; six Challenges; Endless and Sandbox; medal progression; cosmetic liveries; persistent saves; four difficulty choices; research; WebGL 2 models/materials/lights/bloom; procedural nebula/asteroid textures; synthesized audio; performance/reduced-motion settings; responsive command screens.

Research has 41 technologies in four eight-tier prerequisite branches, with every purchased technology active together. Rare elites award 2 Intel; motherships award 3. Command XP from mining, enemy hull damage and eligible repairs funds seven base-stat tracks. Separate Mastery XP from player kills, completed paid construction/upgrades and eligible repairs funds ten tower/ordnance specializations / 58 mastery tracks. Clock speed accelerates construction, mining and solar cycles. Efficient fabrication reaches a 50% construction/upgrade discount. Tower-specific damage, cadence, range, hull, armor, shields and utility effects apply in the simulation. All progression persists across modern games; Classic ignores the profile. In-game purchases pause time and update the active network immediately. Freight is launch-only. Existing balances/purchases migrate, and a recoverable fresh-start control backs up and resets the profile. See [RESEARCH_TREE_DESIGN.md](RESEARCH_TREE_DESIGN.md) and [TOWER_MASTERY.md](TOWER_MASTERY.md).

All buildable structures have at least four levels; solar stations unfold two through six textured petals across five levels. Compact miners, minimalist repair hubs, smaller enemy models, relaxed central-hull placement, and new fields with double the previous ore are intentional requested changes. The expanded upgrades and ore changes also apply to Classic. Restored fields are not refilled. See [STRUCTURE_UPGRADES.md](STRUCTURE_UPGRADES.md).

Graphics work is reduced through material-batched static structures, consolidated cable arcs, offscreen electrical-effect culling and glow strokes instead of per-arc blur filters. Energy-route and stat caching additionally reduces simulation cost. Benchmarks report mesh/effect counts and CPU simulation time; they are not claims about browser FPS.

## Remaining differences and uncertainties

1. **Original replay benchmark:** decompilation is obfuscated in places. Timings have not been measured against a running original. The port uses deterministic 40Hz simulation steps; original ordinary/moving/miner callbacks used different scheduler phases. Consumer refill is demand-driven rather than the original per-class callback sequence. Basic/Pulser acquisition boundaries, starvation skips and THEL first-tick behavior are approximations around the recovered totals and cadence.
2. **Maps and collisions:** Classic uses recovered map parameters with a new seeded field generator, not the original complete PRNG/geometry pipeline. Placement uses compact central-hull circles, a smaller cable clearance, nearest-first new-link selection and simplified circular obstruction. Decorative panels may overlap. Original spatial-cell/tie ordering and visual scales still differ.
3. **Movement:** ships, drones and missiles use simpler steering and constant cruise speed rather than the original acceleration, easing and spatial-grid queries. Missile retargeting is nearest valid enemy rather than the original bounded periodic search. Repair drone hull/energy service ratios are matched, but station construction/refill/dispatch scheduling is approximate. Enemies currently target buildings, not drones. Mothership escort recall when no target remains is not modeled.
4. **Modes:** the original Survivor variants, Wave Mode and Speed Miner are not individually reconstructed. Endless and the modern campaign are new designs. The Missions follow-up's complete campaign, escort ship and super-ship content are not ported. Both raw game files are available locally for further study.
5. **Endless balance:** waves continue without a win condition and scale in count/HP; each wave caps at 100 ordinary ships for browser practicality. Ore remains finite. Long-run balance and performance at hundreds of structures need extended playtesting.
6. **Intentional corrections:** energy cannot overdeliver a request; classic Mission 6 requires all 35 scheduled motherships instead of the historical early-clear condition. Survival missions require remaining attackers to be cleared after the clock. Smooth camera zoom, larger viewport and modern difficulty factors differ from the Flash UI.
7. **Presentation:** original music, sounds, art, menus, portals, achievements and online score services are not reused. The modern scene is a visual redesign. Original short transfer flashes are extended to 0.28s and enriched with glow/jitter for readability.

These are explicit fidelity limits, not claims that every original feature is complete. The earlier audit documents retain the pre-fix findings to explain the source evidence; this file describes the resulting implementation.

## Longer expedition and wave reconnaissance

All twelve modern campaign sectors now have authored formations, longer objective/hold requirements and wave-clear victory gating. The first two mining sectors include raids and a starting defensive laser. Later sectors introduce multi-front attacks, mixed bomber/swarm escorts, suicide wings and separate late mothership assaults. `expedition.js` defines pacing and spawn groups. The next-wave preview shares actual spawn bearings, exposes all fronts, and survives pause/save; the HUD countdown and minimap entry markers are available in modern modes. Classic wave scheduling is unchanged. See [EXPEDITION_WAVES.md](EXPEDITION_WAVES.md) for timing and remaining playtesting limits.

## Rechargeable shields and gentler enemy damage

Modern direct attacks, bomber impacts and suicide splash damage are reduced by 10%; Classic is unchanged. Existing Capacitive armor research now also unlocks individual three-tier shield modules in building inspectors. Modules use paid construction, stored charge, delayed network-energy recharge, real hit absorption, persistent snapshot state, refund accounting and mastery completion rewards. The blue charge ring reuses the canvas overlay; charge and recharge state appear in the inspector. See [RECHARGEABLE_SHIELDS.md](RECHARGEABLE_SHIELDS.md).

## Stable local play environment

A macOS user service now serves an isolated build at 127.0.0.1:5178. The source-watching development server uses 5179, so live edits have separate save storage and cannot reload the play build. `npm run play:update` atomically publishes a completed build without restarting the service; loaded pages retain their old assets until the player refreshes. [Setup and service details](LOCAL_PREVIEW.md).

All 65 Command/tower/ordnance skill tracks now support fifty ranks, with doubled new Command/Mastery earnings and stronger multiplicative armor. Adaptive grid adds researched automatic cable repair; upgraded miners target one through four asteroids with per-beam energy accounting. Asteroid inspectors expose live ore. Existing profile balances and saved deposits are preserved.

Modern enemy fleets now contain three times the previous ships, with half the previous per-ship hull and attack damage. Arrival queues interleave fronts over 8–40 seconds with capitals last; pending arrivals prevent premature wave clearing and persist in saves. All modern towers and laser branches are accessible immediately. Friendly missiles reacquire living targets without extra cost and continue searching through empty arrival gaps within their original fuel lifetime. Classic fleet balance/access remains unchanged.

The latest modern fleet multiplier is five times the original modern count. Ring/mothership point defense deals real missile-hull damage with range/cooldown limits and orange beams. Modern missiles now carry velocity, acceleration, bounded steering, eight-second fuel and bounded curved trail history in snapshots. Swept contact allows misses without tunneling through a hull. Enemy building targeting uses a linear nearest-target scan, and point defense shares a live missile list with a short idle-search cooldown to reduce larger-fleet overhead.

Missile ordnance adds six fifty-rank mastery tracks for payload damage, engagement range, blast radius, fuel, hull and finite projectile shielding. Launcher and payload stats stack; shields charge with paid network energy at launch and absorb interception before hull. Existing in-flight missile stats stay fixed through live upgrades and save/resume.
