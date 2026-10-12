# Validation receipt

2026-10-11, local browser edition.

## Automated

- `npm test`: **181 passed, 0 failed**. Tests cover resource conservation, isolated graph components, incomplete-relay gating, source ordering, local buffers, construction, burst/interception behavior, missiles, Ringers, mothership escorts, suicide fuse, repair, classic schedules, mode objectives, deterministic frame-rate behavior, snapshot restoration, progression and research effects.
- `npm run build`: passed with Vite 7.3.7. JavaScript bundle ~705 kB / 194 kB gzip; CSS ~33 kB / 7.7 kB gzip. Vite reports its advisory >500 kB chunk warning. No build errors.
- `npm install` audit: 0 vulnerabilities at implementation time.
- `git diff --check`: passed.

## Earlier browser checks

These receipts predate the expanded progression below. Equip/unequip slots and the old activity-Intel schedule have since been replaced.

Tested in a dedicated Chrome automation surface; an isolated second local origin protected the main preview's save.

- Home, Expedition selection, locked sectors, mission launch and HUD rendered correctly.
- Placed a miner with key 2, upgraded using Space, completed First light, received three stars, and verified the next sector unlocked.
- Paused an Endless operation, converted a basic laser to Pulser with P, and verified upgrade construction remained paused. Fixed a pointer-intercepting pause overlay found during this check.
- Saved/resumed the Endless operation, manually requested five waves, and observed the fifth-wave counter and hostile signals. Simulation tests separately verify the fifth-wave mothership and ongoing escalation.
- Research: bought Prismatic cells and Composite hulls; verified Intel deduction, equipped state and newly available prerequisites. A newly launched mission showed 2.0 solar E/s and a 690-HP solar station versus baseline 1.6 E/s and 600 HP. Its active-research dialog listed both technologies.
- Respec refunded all four invested Intel and cleared the next-launch loadout. Saved-operation isolation is also covered by a simulation snapshot test.
- Bought both Power branch prerequisites, selected Storm shielding, and observed the correct disabled purchase / “Need 4 more Intel” state.
- Research tree reviewed at the normal 1392×902 viewport and at 390×844. Fixed narrow-header wrapping and node overlap; narrow layout now stacks one branch per row and opens selected details. Viewport override reset afterward.
- Browser console check returned no warnings or errors during final research interaction.

Captured research screenshots in [screenshots/](screenshots/). These show an isolated QA profile, not the player's main save.

## Earlier live research follow-up

- Added 10 regression tests for threshold/carryover accounting, idempotent banking across reloads, legacy snapshots, losses and excluded modes, real extraction versus recycle refunds, player-attributed kills, immediate modifiers, reversible hull changes, capacity conservation, link rebuilding and the live UI's earning/launch-only labels.
- In the isolated browser profile, resumed A wider orbit, opened the tree using I, bought Resonant drills with 2 Intel, and returned to the same operation with Escape. Extraction increased to five minerals per cycle.
- At 223 total minerals extracted, the HUD showed the first new activity Intel and 15/200 progress toward the next. The legacy snapshot had eight minerals before activity tracking began.
- At 02:27, manually paused the mission, opened research, unequipped Prismatic cells and returned. The mission remained paused and its generation immediately changed from 2.0 to 1.6 E/s. Re-equipping restored 2.0 E/s with time still 02:27.
- Reloaded and resumed: balance remained 1 Intel, progress remained 35/200, and the two equipped technologies persisted. No duplicate reward.
- Live respec refunded 12 Intel (balance 1 → 13), removed the active solar bonus, and returned to the operation. The mission-menu research path also returned to the same running operation correctly.
- The new acquisition bars and live return control were checked at desktop and 390×844. Narrow-screen node selection scrolled to usable upgrade details. Viewport override was reset. Console warnings/errors: none.
- Screenshot: [live research](screenshots/research-in-game.jpg), captured from the isolated QA profile. Player's main preview/save was not used for purchases or respec tests.

## Compact structures, effects and expanded progression

- `npm test`: 111 passed. Added real tier-construction/save/cap checks for all eight building branches; miner yield/energy, higher repair throughput, relay port increases, permissive placement, richer fields and preserved old deposits; actual solar/repair/enemy geometry; shared arc aggregation and cached-route invalidation.
- Progression tests cover all forty nodes, unlimited active research, rare-ship rewards and exclusions, actual mining/combat/repair XP, level thresholds, point overspending, six stat effects, scenario-objective repairs, migration, persistence, save idempotency, Classic/Sandbox exclusions and recoverable fresh reset.
- Synthetic benchmark: 120 structures, 1,200 steps and 12,000 requests. Before caches: median 1,539.8 ms. Final recorded run: median 70.9 ms / 0.059 ms per step. These are CPU simulation measurements, not browser FPS or GPU timings.
- Actual model counts: basic relay 12 → 4 meshes; six-petal solar 6 meshes. Synthetic shared-cable workload: 1,680 overlapping path segments → 30 unique electrical arcs.
- Dedicated Chrome QA at `127.0.0.1:5179` imported a backed-up profile through the normal save-import UI. All eight owned technologies became active; a ninth was purchased, reducing Intel 18 → 14 with no equipment restriction.
- The base-stat screen showed level 6 and five available points. Buying Harvesting reduced points 5 → 4 while keeping Intel 18. A new Sandbox inherited the research and harvesting rank.
- Opened live progression with I; bought another Harvesting rank; returned with Escape to the same operation. The miner inspector showed **110 minerals/min**, matching 80 × 1.25 research × 1.10 XP bonus. Intel remained 14. Sandbox did not earn new progression.
- Upgraded solar through all five levels using both U and Space. Verified 2/3/4/5/6 petals, finite construction and the level-five maximum configuration. Built and visually checked the small four-port repair hub beside it.
- Current desktop layout was reviewed at 1,911 × 1,085. Attempted narrow viewport emulation did not change the reported DOM size, so this receipt does not claim a new narrow-layout check. Temporary overrides were cleared.
- Browser console during final gameplay/progression interaction: no warnings or errors.
- Owner-authorized fresh reset was performed on the main preview. The old profile was saved locally and exported to a JSON download, then home showed 6 starting Intel and no saved operation. Research/XP persistence remains enabled for future games. The backup was successfully imported into the isolated QA profile; the main fresh profile was not used for QA purchases.

Screenshots: [expanded tree](screenshots/research-expanded.jpg), [XP base stats](screenshots/base-stats.jpg), [six-petal solar and compact repair hub](screenshots/solar-petals.jpg). Screenshots of upgraded progress are from the isolated QA origin.

## Clock speed, discounts and tower mastery

- `npm test`: 130 passed, including actual mining, solar pulses, laser bursts, missile salvos, repair throughput, armor/shield energy, shared XP budgets, save migration, live timer/hull/capacity conservation, relay links, Classic exclusions and paid-cost refunds.
- Added seven global XP tracks and 52 class-specific tracks across nine building/weapon classes. Existing fabrication ranks migrate to Clock speed; progression remains persistent.
- Dedicated desktop Chrome QA used the isolated `127.0.0.1:5179` save. Purchased Clock speed, Efficient fabrication and Basic laser Damage for one XP point each; available points fell from three to zero, with Intel unchanged at 14.
- Returning to the same operation showed mining 110 → 116 minerals/min, generation 11.8 → 12.4 E/s, laser cost 99 and THEL conversion 495. Basic laser damage showed 36. Reload preserved purchases and effects.
- Tower mastery displayed all nine classes, independent Basic laser/Pulser ranks, repair-specific throughput/range/reserves and disabled purchases when no points remained. Browser console warnings/errors: none.
- The player's main save was preserved. This follow-up claims desktop QA only.

Screenshot: [Tower mastery](screenshots/tower-mastery.jpg), captured from the isolated QA profile.

## Independent mastery XP follow-up

- `npm test`: 136 passed. New simulation checks cover once-only ship-kill rewards, real paid construction/upgrade completion, canceled/free builds, real repair debt, independent purchasing, snapshot banking, save round trips, migration and testing-mode exclusions.
- Added a third persistent economy: mastery earns 10 XP per ship kill, 0.1 per mineral paid for completed construction/upgrades, and 0.1 per eligible hull repair. Level thresholds mirror Command XP; only tower specialization purchases spend mastery points.
- Dedicated desktop Chrome QA on isolated port 5179 showed old Basic laser Damage rank one preserved, mastery level two funded with 100 XP, zero available mastery points and one returned base-stat point. Intel remained 14 and Command level six remained intact. All three currencies and earning rules were visible; no console warnings/errors.
- Main player save was not used for QA. New game rewards were validated in actual simulation tests; this browser check verifies migration and UI, not a complete campaign playthrough.
- Screenshot: [Independent mastery XP](screenshots/mastery-xp.jpg).

## Free play and Challenge rewards

- `npm test`: 144 passed. Each of the six modern Challenges, Endless and Sandbox now has a real enemy-kill/repair integration test verifying Intel, Command XP and Mastery XP banking without duplicate rewards on resume.
- Endless and modern Challenges were already eligible. Removed Sandbox’s reward exclusion; its generous resources and manual waves remain available. Classic retains its original progression exclusion.
- Updated mode/progression help and current design documentation. Production build and diff checks pass.

## Longer expeditions and next-wave bearings

- `npm test`: 150 passed. Tests validate all twelve authored plans, viable mining deposits, varied enemy classes, exact formation counts, advertised spawn bearings, every victory kind’s wave/time gates, automatic arrivals, paused countdowns, snapshot previews, multiple fronts and staggered capital goals.
- First light now requires 600 mined minerals, four cleared waves and 3:30 minimum duration. The final sector has twelve waves, three staggered motherships and an 11:00 minimum. Briefings and HUD show compound objectives.
- Isolated desktop Chrome QA launched First light, showed a powered initial laser, NEXT WAVE 1/4 countdown, FROM N arrow, formation name and matching northern minimap entry arrow. Countdown decreased from 1:04 to 0:50 and froze when paused. No console warnings/errors. Main player save was preserved.
- Screenshot: [Expedition countdown and approach](screenshots/expedition-waves.jpg). Production build passes. Campaign balance remains initial tuning; this is not a full playthrough.

## Rechargeable building shields

- `npm test`: 159 passed. New tests cover research/price/construction locks, all three module tiers, full-hit absorption and hull spillover, repair debt, five-second recharge delay, exact energy cost, own-solar reserves, network supplier flows, powerless isolation, saved charge, live research changes, discounts/refunds and actual weaker direct/bomber attacks. Suicide falloff tests now expect the modern 0.9 multiplier.
- Isolated Chrome QA imported a disposable synthetic research profile through the regular import UI. Installed a solar shield for 100 minerals, saw 0/138 while installing and gradual recharge, then resumed the save with 138/138 charge intact.
- Tier two cost 160 minerals and retained 138 charge during installation, then recharged to its roughly 241-HP maximum. The inspector showed tier 2/3, the 240-mineral final upgrade and a blue reserve ring. Final console warnings/errors: none. Main player profile was not changed by QA.
- Screenshot: [Rechargeable shield](screenshots/rechargeable-shields.jpg). Build and diff checks pass. README now documents progression, longer expeditions, incoming bearings, shield unlock/costs and the damage adjustment.

## Persistent isolated local preview

- `npm test`: 160 passed. Added an HTTP integration test verifying isolated snapshots, live manifest changes without server restart, retained older hashed assets, HEAD requests, unsupported-method rejection, path confinement and malformed URL handling.
- Installed a per-user macOS launchd service serving a separate build on loopback port 5178. `play:install` completed the production build, validated the property list and returned the correct health identity. launchd reports running with KeepAlive and RunAtLoad.
- Stable HTML and its JavaScript asset returned HTTP 200. Stable HTML contains no Vite reload client, and `/@vite/client` returns 404. The separate live-development server on 5179 returns 200 for its reload client.
- The original 5178 origin is retained for player saves; no browser profile/reset operation was performed. README documents installation, update, status, start/stop and the new development port.

## Limits

This is not a complete campaign playthrough, long-duration endless stress benchmark, Safari/Firefox certification, or original-Flash runtime comparison. Original source fidelity and remaining differences are documented in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Balance values for new research and authored missions remain initial tuning.

## Adaptive grid, multi-mining and fifty-rank progression

- 175 tests pass; production build passes. New integration coverage checks disconnected branches and stalled blueprints, cable obstacles/ports, retry budgeting, save restoration, distinct mining targets, per-beam energy, finite deposits, doubled reward accounting, fifty-rank budgets and finite armor stacking.
- Dedicated browser QA on port 5179 recycled a relay, observed its miner disconnected, purchased Adaptive grid for 6 Intel after Field couplers, and observed immediate reconnection. Base and tower panels show rank 50, doubled earning rules and strengthened armor. Player origin 5178 was untouched.
- Screenshots: [Adaptive grid](screenshots/adaptive-grid.jpg), [Fifty-rank base stats](screenshots/progression-fifty.jpg).

- Asteroid browser QA selected the seed-2 starter deposit and verified 3,300 initial minerals, 3,224 remaining and 76 extracted. This caught and fixed a missing inspector render binding. Multi-target yield and energy limits are covered by simulation integration tests. [Ore inspector](screenshots/asteroid-inspector.jpg).

## Streamed fleets, default towers and hunting missiles

- 181 tests pass. Every authored wave queues exactly triple its prior difficulty-scaled groups at advertised bearings. New integration tests verify staggered release, pending-clear gating, pause/save determinism, halved modern hull with elite modifiers, original Classic hull, complete modern equipment access including resumed legacy definitions, repeated missile reacquisition, empty-gap searching, unchanged ammo spending, save restoration and fuel expiry. Attack, bomber-impact and suicide-splash tests verify half the prior modern damage.
- Dedicated browser QA on isolated port 5179 verified sector one offers all seven build cards and both Pulser/THEL upgrade actions. Sandbox wave one showed **1 hostile / 11 inbound**, then **5 hostile / 7 inbound**, proving arrivals are staggered. Browser console warnings/errors: none.
- Screenshots: [Default towers](screenshots/default-towers.jpg), [Streamed wave](screenshots/streamed-waves.jpg).
