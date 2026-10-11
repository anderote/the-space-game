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

Research has 40 technologies in four eight-tier prerequisite branches, with every purchased technology active together. Rare elites award 2 Intel; motherships award 3. XP from mining, enemy hull damage and battle-damage repairs earns points for six base-stat tracks. All progression persists across modern games; Classic ignores the profile. In-game purchases pause time and update the active network immediately. Freight is launch-only. Existing balances/purchases migrate, and a recoverable fresh-start control backs up and resets the profile. See [RESEARCH_TREE_DESIGN.md](RESEARCH_TREE_DESIGN.md).

All buildable structures have at least four levels; solar stations unfold two through six textured petals across five levels. Compact miners, minimalist repair hubs, smaller enemy models, relaxed central-hull placement, and 50% richer new fields are intentional requested changes. The expanded upgrades and ore changes also apply to Classic. Restored fields are not refilled. See [STRUCTURE_UPGRADES.md](STRUCTURE_UPGRADES.md).

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
