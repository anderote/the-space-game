# Validation receipt

2026-10-11, local browser edition.

## Automated

- `npm test`: **84 passed, 0 failed**. Tests cover resource conservation, isolated graph components, incomplete-relay gating, source ordering, local buffers, construction, burst/interception behavior, missiles, Ringers, mothership escorts, suicide fuse, repair, classic schedules, mode objectives, deterministic frame-rate behavior, snapshot restoration, progression and research effects.
- `npm run build`: passed with Vite 7.3.7. JavaScript bundle ~664 kB / 181 kB gzip; CSS ~28 kB / 6.7 kB gzip. Vite reports its advisory >500 kB chunk warning. No build errors.
- `npm install` audit: 0 vulnerabilities at implementation time.
- `git diff --check`: passed.

## Browser

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

## Live research follow-up

- Added 10 regression tests for threshold/carryover accounting, idempotent banking across reloads, legacy snapshots, losses and excluded modes, real extraction versus recycle refunds, player-attributed kills, immediate modifiers, reversible hull changes, capacity conservation, link rebuilding and the live UI's earning/launch-only labels.
- In the isolated browser profile, resumed A wider orbit, opened the tree using I, bought Resonant drills with 2 Intel, and returned to the same operation with Escape. Extraction increased to five minerals per cycle.
- At 223 total minerals extracted, the HUD showed the first new activity Intel and 15/200 progress toward the next. The legacy snapshot had eight minerals before activity tracking began.
- At 02:27, manually paused the mission, opened research, unequipped Prismatic cells and returned. The mission remained paused and its generation immediately changed from 2.0 to 1.6 E/s. Re-equipping restored 2.0 E/s with time still 02:27.
- Reloaded and resumed: balance remained 1 Intel, progress remained 35/200, and the two equipped technologies persisted. No duplicate reward.
- Live respec refunded 12 Intel (balance 1 → 13), removed the active solar bonus, and returned to the operation. The mission-menu research path also returned to the same running operation correctly.
- The new acquisition bars and live return control were checked at desktop and 390×844. Narrow-screen node selection scrolled to usable upgrade details. Viewport override was reset. Console warnings/errors: none.
- Screenshot: [live research](screenshots/research-in-game.jpg), captured from the isolated QA profile. Player's main preview/save was not used for purchases or respec tests.

## Limits

This is not a complete campaign playthrough, long-duration endless stress benchmark, Safari/Firefox certification, or original-Flash runtime comparison. Original source fidelity and remaining differences are documented in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Balance values for new research and authored missions remain initial tuning.
