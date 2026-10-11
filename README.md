# The Space Game

A modern browser recreation of David Scott and Casual Collective’s 2009 asteroid-mining strategy game. Connect solar stations, relays, miners, stores and defenses into a living energy network. Three.js provides lit models, procedural asteroid materials, a nebula, bloom, and electrical activity driven by real power transfers.

## Play locally

Requires Node.js 20.19+ or 22.12+ and a browser with WebGL 2. Mouse and keyboard recommended.

```sh
npm ci
npm start
```

Open **http://127.0.0.1:5178**. Progress, research, settings and your current operation save in this browser. Settings offers progress export/import; imports restore campaign/research records, not an arbitrary running simulation.

```sh
npm test
npm run build
npm run preview
```

`dist/` is a static build; serve it over HTTP. There is no backend or account requirement. Nothing in this checkout deploys the site automatically.

## Modes and progression

- **Expedition:** 12 new missions, mining/rescue/defense/boss objectives, structure unlocks, three medals per mission and cosmetic liveries.
- **Classic:** nine reconstructed missions with original budgets, structure access, extraction-driven waves and recovered survival schedules. Research bonuses are disabled.
- **Challenges:** six independent economy, combat, power and rescue scenarios.
- **Endless frontier:** escalating fleets with a mothership every fifth wave, personal records and research rewards for cleared milestones.
- **Sandbox:** generous resources, all structures and manual wave controls.
- **Research division:** 20 technologies in Power, Industry, Ballistics and Engineering. Six loadout slots, prerequisite branches, capstone tradeoffs and free refunds. Your equipped research takes effect when starting a modern operation; saved operations retain their original loadout.

Research starts with 6 Intel. Each new best Expedition/Challenge star earns 2, and each newly cleared five-wave Endless milestone earns 4. Replaying an unchanged result or simply calling a wave earns nothing. [Research design and sources](docs/RESEARCH_TREE_DESIGN.md).

## Original shortcuts

| Key | Action |
| --- | --- |
| 1 / 2 / 3 / 4 | Relay / Miner / Solar / Energy Store |
| 5 / 6 / 7 | Repair / Laser / Missile |
| U or Space | Upgrade selected structure |
| P / T | Basic laser → Pulser / THEL |
| R | Recycle selected structure |
| Shift + click | Repeat construction |
| Esc / right-click | Cancel placement/selection |
| WASD / arrows / drag | Pan |
| Q / E / wheel | Zoom in/out |
| Pause button | Freeze time while planning and purchasing |

P and Space retain their original upgrade meanings. Home centers the camera as a browser convenience.

## Fidelity and provenance

This is an independent recreation, not an official release or bit-exact emulator. Both full original game SWFs were acquired and hashed for private reference. Decompiled code supplied factual controls, costs, buffers, ranges, upgrade branches, wave tables and special combat rules. Original binaries, code, art and audio are not distributed here.

- [Current implementation and remaining fidelity gaps](docs/IMPLEMENTATION_STATUS.md)
- [Original mechanics extracted from the SWF](docs/ORIGINAL_MECHANICS.md)
- [Research, reviews, screenshots, downloads and archive hashes](docs/RESEARCH.md)
- [Power audit](docs/FIDELITY_AUDIT_POWER.md) and [combat audit](docs/FIDELITY_AUDIT_COMBAT.md)
- [Graphics research](docs/GRAPHICS_RESEARCH.md)
- [Browser and simulation validation](docs/VALIDATION.md)

Models, textures, shaders and synthesized effects in the browser edition are newly created. Three.js and Vite retain their upstream licenses. The game name and original design are credited to their creators.

The earlier Panda3D prototype remains in `game/`, `config/`, and the Python files. Its [previous README](docs/PANDA3D_README.md) and older design documents are historical prototype material, not the browser build’s specification.
