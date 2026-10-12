# Compact structures, expanded tiers and effects performance

Browser-edition updates requested on 2026-10-11. The recovered original tiers retain their source-backed stats and prices; explicit later tiers are appended. These extensions apply to modern and Classic missions. The mission-critical derelict remains an objective, rather than a purchasable upgradeable building.

| Structure | Levels | Progression before research |
| --- | ---: | --- |
| Relay | 4 | 6 / 8 / 10 / 12 connections; 90 / 95 / 100 / 110 link range |
| Miner | 4 | 1 / 2 / 3 / 4 beams; 80 / 200 / 320 / 480 minerals per minute per beam |
| Solar | 5 | 2 / 3 / 4 / 5 / 6 petals; 1.6 / 3.8 / 5.5 / 7.6 / 9.8 E/s |
| Energy store | 4 | 200 / 600 / 1,200 / 2,000 energy |
| Repair station | 4 | 200 / 300 / 350 / 400 repair range; 20 / 20 / 25 / 30 HP/s per drone |
| Basic laser / Pulser | 4 | Original basic-to-Pulser progression retained |
| Missile launcher | 4 | 1 / 2 / 4 / 5 missiles per salvo |
| THEL | 4 | Original conversion and early upgrades, plus a stronger fourth tier |

The inspector shows current level, output, next upgrade and mineral cost. U and Space still upgrade; P and T retain the original beam branches. Construction still spends energy, pauses production during upgrades, and respects maximum levels. High-level miners consume 1.5 / 2 energy per cycle at levels 3 / 4. Repair drones retain four-per-station count and finite carried energy.

## Scale and placement

Miners use 75% of their previous scale; repair stations use 65%, with a low-profile hub and four small drone ports. Other buildings use 85%. Solar arrays retain full scale and unfold rounded textured petals. Enemy models use 60% scale, with corresponding engine-trail/shield offsets; their underlying combat stats are retained.

Placement tests compact central hulls at 82% of their visual base radius. Decorative panels and barrel tips may overlap, but central hulls cannot. Cable clearance uses 35% of the base radius with a two-unit minimum. The same clearance is used when checking links, so a legal near-cable building does not silently cut an existing connection. Asteroid clearance uses 88% of the currently visible depleted-rock radius. Solar petal tips are selectable without increasing construction exclusion.

All newly generated modern and Classic fields contain twice the previous ore (three times the initial browser baseline). Generation seeds and asteroid positions stay deterministic. Saved fields retain the ore and maximum values in their snapshot; they are not refilled or multiplied again on resume. Classic mining objectives remain half of the generated field.

## Graphics and simulation work

- Relay, solar, energy-store, repair and missile meshes are merged by material. Nested solar petal transforms and texture UVs are preserved. Moving beam/miner turrets remain separate.
- A basic relay uses four meshes rather than twelve; a level-five six-petal solar station uses six meshes, independent of the number of petals.
- Simultaneous transfers over the same cable draw one combined arc, preserving current load, most recent direction and lifetime. Passive cables use two batched canvas strokes.
- Offscreen electrical arcs are skipped. A translucent broad glow stroke replaces a blur filter per arc; jagged electricity, moving transfer dots and node pulses remain tied to actual withdrawals. Idle full grids stay quiet, and pause freezes transfers.
- Performance graphics mode bypasses bloom and uses a 1× render pixel ratio; high graphics retains the display’s ratio up to 2×. The HUD/overlay stays sharp at its own display ratio.
- Building stat caches invalidate on level, type or research-rule changes. Supply-route caches invalidate on network rebuilding and defer caching paths blocked by unfinished relays. Current energy, construction state and solar-only charging restrictions are still checked on every withdrawal.

`npm run benchmark` runs a reproducible 120-structure, 1,200-step simulation with 12,000 requests and reports actual model mesh counts plus a shared-cable workload. In the synthetic shared-cable workload, 1,680 overlapping path segments become 30 arcs. CPU timing varies with machine load. This benchmark does not measure GPU frame time or browser FPS; browser QA verifies the resulting visuals separately.

Each mining beam targets a distinct asteroid and pays the normal tier energy cost. Insufficient energy limits active beams. Click asteroid hulls to inspect live remaining/initial ore, harvested quantity, miners in reach and current beams. Selection follows the visible shrinking rock radius.
