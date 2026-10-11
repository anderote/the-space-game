# Validation receipt

2026-10-11, local browser edition.

## Automated

- `npm test`: **74 passed, 0 failed**. Tests cover resource conservation, isolated graph components, incomplete-relay gating, source ordering, local buffers, construction, burst/interception behavior, missiles, Ringers, mothership escorts, suicide fuse, repair, classic schedules, mode objectives, deterministic frame-rate behavior, snapshot restoration, progression and research effects.
- `npm run build`: passed with Vite 7.3.7. JavaScript bundle ~660 kB / 179 kB gzip; CSS ~26 kB / 6.5 kB gzip. Vite reports its advisory >500 kB chunk warning. No build errors.
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

## Limits

This is not a complete campaign playthrough, long-duration endless stress benchmark, Safari/Firefox certification, or original-Flash runtime comparison. Original source fidelity and remaining differences are documented in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Balance values for new research and authored missions remain initial tuning.
