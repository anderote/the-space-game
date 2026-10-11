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
npm run benchmark
npm run preview
```

`dist/` is a static build; serve it over HTTP. There is no backend or account requirement. Nothing in this checkout deploys the site automatically.

## Modes and progression

- **Expedition:** 12 new missions, mining/rescue/defense/boss objectives, structure unlocks, three medals per mission and cosmetic liveries.
- **Classic:** nine reconstructed missions with original budgets, structure access, extraction-driven waves and recovered survival schedules. Research and XP stat bonuses are disabled. Building upgrades use the browser edition’s expanded tiers.
- **Challenges:** six independent economy, combat, power and rescue scenarios.
- **Endless frontier:** escalating fleets with a mothership every fifth wave, personal records and rare ships carrying Intel.
- **Sandbox:** generous resources, all structures and manual wave controls.
- **Research division:** 40 technologies in four branches. Every purchased technology stays active together, with no equipment limit. Open with **I** during a modern operation; time pauses and upgrades apply immediately.
- **Command XP:** mining, combat damage and damage repairs award experience. Each level grants a base-stat point. Seven base tracks cover Armor, Clock speed, Harvesting, Firepower, Repair efficiency, Power output and Efficient fabrication. Clock speed accelerates construction, mining and solar cycles; Efficient fabrication reaches 20% cheaper buildings and upgrades.

- **Tower mastery:** nine building/weapon specializations with 52 skill tracks for combat, utility output, health, armor and powered shields. Earn mastery XP from ship kills (10 each), completed buildings/upgrades (1 per 10 paid minerals), and damage repairs (1 per 10 hull). Spend its independent points on a specific class, including separate Basic laser, Pulser and THEL tracks. [Skill effects](docs/TOWER_MASTERY.md).

Research, Intel, XP and base stats persist across modern games and campaigns, including losses. Begin with **6 Intel**; defeat a gold-marked elite for **2 Intel** or a mothership for **3**. One elite appears every third wave. Mining and ordinary combat earn XP: **5 minerals**, **20 enemy hull damage** or **10 damage repairs** each grant 1 XP. The first point costs 100 XP, then each subsequent level requires 50 more XP than the last. Classic and Sandbox award no progression; Sandbox can use existing upgrades. Freight research applies only when launching a new operation. [Progression design](docs/RESEARCH_TREE_DESIGN.md).

Settings includes **Start fresh · back up progress**. It saves a local backup and downloads a JSON before clearing campaign records, research, XP and the current operation. Settings are preserved. Import restores profile records and upgrades; it does not restore arbitrary running simulations.

## Building and graphics updates

Every buildable structure has at least four levels; solar stations have five, unfolding **2 → 3 → 4 → 5 → 6 petals**. Miners are 25% smaller, repair stations are 35% smaller with a minimalist four-port hub, other structures are 15% smaller, and enemy models are 40% smaller. Solar arrays retain full scale. Placement allows decorative overlap while protecting central hulls and cable cores. Newly generated asteroid fields contain **50% more minerals**; restored saves retain their remaining deposits.

Static station parts are batched by material, shared power transfers draw one arc per cable, and offscreen electrical arcs are skipped. Jagged electricity and node pulses still follow real energy use. Performance graphics mode also uses a lower render resolution on high-density displays while keeping UI text crisp. [Upgrade definitions and performance notes](docs/STRUCTURE_UPGRADES.md).

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
