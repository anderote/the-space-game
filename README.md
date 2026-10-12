# The Space Game

A modern browser recreation of David Scott and Casual Collective’s 2009 asteroid-mining strategy game. Connect solar stations, relays, miners, stores and defenses into a living energy network. Three.js provides lit models, procedural asteroid materials, a nebula, bloom, and electrical activity driven by real power transfers.

## Play locally

Requires Node.js 20.19+ or 22.12+ and a browser with WebGL 2. Mouse and keyboard recommended.

On macOS, install the stable play preview once:

```sh
npm ci
npm run play:install
```

Play at **http://127.0.0.1:5178**. The macOS user service runs independently of terminals, starts at login and recovers after a crash. It serves a separate build copy outside the repository, so editing code or running another build cannot reload your game. Progress, research, settings and your current operation remain saved on the same browser origin.

```sh
npm run play:status  # Check the running preview
npm run play:update  # Build and switch to the latest code without restarting the server
npm run play:stop    # Stop it for the current login session
npm run play:start   # Start an already installed preview
```

After `play:update`, refresh the game when ready. Existing pages stay on their loaded version, and their hashed assets remain available. These commands only manage the local loopback preview; they do not deploy a public site.

For active development:

```sh
npm run dev
```

Open **http://127.0.0.1:5179** for live changes. This separate origin has its own browser save storage. `npm start` also starts this development server. On other operating systems, use the development server or serve `dist/` after building. [Local preview setup](docs/LOCAL_PREVIEW.md).

```sh
npm test
npm run build
npm run benchmark
npm run preview
```

`dist/` is a static build; serve it over HTTP. There is no backend or account requirement. Settings offers progress export/import; imports restore campaign/research records, not an arbitrary running simulation. Nothing in this checkout deploys the site automatically.

## Modes and progression

- **Expedition:** 12 longer missions with enemies in every sector, 4–12 authored waves, mining/rescue/defense/boss objectives, all towers available immediately, three medals per mission and cosmetic liveries.
- **Classic:** nine reconstructed missions with original budgets, structure access, extraction-driven waves and recovered survival schedules. Research and XP stat bonuses are disabled. Building upgrades use the browser edition’s expanded tiers.
- **Challenges:** six independent economy, combat, power and rescue scenarios.
- **Endless frontier:** escalating fleets with five motherships every fifth wave, personal records and rare ships carrying Intel.
- **Sandbox:** generous resources, all structures and manual wave controls.
- **Research division:** 41 technologies in four branches. Every purchased technology stays active together, with no equipment limit. Open with **I** during a modern operation; time pauses and upgrades apply immediately.
- **Command XP:** mining, combat damage and damage repairs award experience. Each level grants a base-stat point. Seven base tracks cover Armor, Clock speed, Harvesting, Firepower, Repair efficiency, Power output and Efficient fabrication. Clock speed accelerates construction, mining and solar cycles; Efficient fabrication reaches 50% cheaper buildings and upgrades.
- **Tower mastery:** ten building/weapon/ordnance specializations with 58 skill tracks for combat, utility output, health, armor and powered shields. Earn mastery XP from ship kills (20 each), completed buildings/upgrades (2 per 10 paid minerals), and damage repairs (2 per 10 hull). Spend its independent points on a specific class, including separate Basic laser, Pulser and THEL tracks. [Skill effects](docs/TOWER_MASTERY.md).

Research, Intel, XP and base stats persist across modern games and campaigns, including losses. Begin with **6 Intel**; defeat a gold-marked elite for **2 Intel** or a mothership for **3**. One elite appears every third wave. Mining and ordinary combat earn XP: **5 minerals**, **20 enemy hull damage** or **10 damage repairs** each grant 2 XP. The first point costs 100 XP, then each subsequent level requires 50 more XP than the last. All modern modes earn progression, including Endless, Sandbox and Challenges. Classic awards no progression. Freight research applies only when launching a new operation. [Progression design](docs/RESEARCH_TREE_DESIGN.md).

Expedition missions now have 4–12 authored waves and minimum operation times from 3:30 to 11:00. Every sector has enemies, with distinct swarm, bomber, flanking and capital-ship formations. Complete the sector objective, hold through the operation and clear every wave to win. The HUD shows the next-wave countdown and incoming compass bearings; matching arrows mark approaches on the sector map. [Expedition pacing](docs/EXPEDITION_WAVES.md).

Settings includes **Start fresh · back up progress**. It saves a local backup and downloads a JSON before clearing campaign records, research, XP and the current operation. Settings are preserved. Import restores profile records and upgrades; it does not restore arbitrary running simulations.

## Building and graphics updates

Every buildable structure has at least four levels; solar stations have five, unfolding **2 → 3 → 4 → 5 → 6 petals**. Miners are 25% smaller, repair stations are 35% smaller with a minimalist four-port hub, other structures are 15% smaller, and enemy models are 40% smaller. Solar arrays retain full scale. Placement allows decorative overlap while protecting central hulls and cable cores. Newly generated asteroid fields contain **twice the previous minerals (3× the initial browser baseline)**; restored saves retain their remaining deposits.

Modern enemy attacks deal **10% less damage** across direct fire, bomber impacts and suicide explosions. Classic retains its recovered damage rules.

**Rechargeable building shields:** research **Capacitive armor** in Field engineering (9 Intel after Autoseal plating), then select a player building and use **Install shield** in its inspector. Three module tiers cost **100 / 160 / 240 minerals** before fabrication discounts and provide a shield reserve equal to **20% / 35% / 50% of maximum hull**. Installation uses construction time and starts with an empty reserve. After **5 seconds without a hit**, reserves recharge at up to 10% capacity per second, capped at 25 shield HP/s, spending **0.2 energy per shield HP**. The inspector shows charge and recharge state; a blue ring shows remaining reserve. Empty grids cannot recharge, and shield upgrades preserve existing charge. Research unlocks persist, while each new building needs its own module. [Shield details](docs/RECHARGEABLE_SHIELDS.md).

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

Pulser upgrades are available from the first Expedition. THEL conversion unlocks in sector 7, Heavy metal, and is available immediately in Free play and Challenges. Both require a completed level-one basic laser and minerals.

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

All seven base-stat tracks and all 58 tower mastery tracks now cap at **50 ranks**. Global Armor removes 3% of remaining hull damage per rank; tower Armor removes a further 2%, combining multiplicatively. Existing XP and ranks are preserved.

**Adaptive grid:** research Field couplers, then spend **6 Intel** on Adaptive grid to reconnect disconnected buildings automatically. It respects cable obstacles, range, construction state and connection limits, retrying stalled branches every two seconds.

**Multi-asteroid mining:** miner tiers provide **1 / 2 / 3 / 4 simultaneous beams**, with normal energy charged per beam and each target receiving the tier’s configured yield. Click an asteroid to inspect remaining minerals, harvested ore and nearby miners. Saved asteroid deposits are preserved.

**Streamed enemy fleets:** modern Expedition, Challenges and Free play waves contain **5× the original modern fleet size**, including capital ships. Each newly spawned enemy has **half the previous hull and attack damage**, retaining difficulty/elite/Endless scaling. Waves release one ship at a time over 8–40 seconds, interleave fronts, and place capitals after escorts. The HUD counts ships still inbound; queued ships must arrive and be defeated before a wave clears. Saves and pause preserve the stream. Classic retains its original fleet strength and release schedule.

**Every modern tower is unlocked from the start**, including resumed operations: build keys 1–7 cover relays, miners, solar, stores, repair, lasers and missiles. Select a Basic laser and use **U / Space** for Pulser or **T** for THEL, paying the normal upgrade price. Campaign sectors and cosmetic liveries retain their progression.

**Homing missiles** reacquire the nearest living enemy from their current position whenever their target dies. If no enemy is present, they coast and continue searching for later arrivals until their configured fuel lifetime (eight seconds before Fuel reserves) expires. Retargeting costs no extra ammunition or energy.

**Missile flight and countermeasures:** modern missiles launch at 60 units/s, accelerate at 100 units/s² toward their configured cruise speed (160 units/s before guidance research), and turn at up to 1.6 radians/s. Velocity follows heading gradually, producing visible curved trails and overshoot. Hits require swept contact with the target hull, rather than proximity to the distance a missile could travel. Baseline eight-second fuel limits reacquisition and missed approaches.

Ring ships defend a 100-unit radius with a 10-damage shot every 1.1 seconds; motherships defend 160 units with the same shot every 0.7 seconds. Friendly missiles start with 20 hull before Missile hull mastery. Orange point-defense beams show interception; two shots destroy a missile without awarding player XP. These countermeasures and inertial flight apply to modern modes; Classic preserves its existing flight/combat behavior.

**Missile ordnance mastery:** press **I → Tower mastery → Missile ordnance**. All six tracks cost one mastery point per rank and cap at fifty: damage **+5%**, engagement range **+3%**, blast radius **+4%**, fuel **+5%**, missile hull **+5%**, and shield reserve **+2% of missile hull** per rank. Damage/range stack with launcher mastery and research. Range controls launcher acquisition; fuel governs flight endurance. At rank fifty, baseline fuel reaches 28 seconds and hull reaches 70 HP. Shields absorb interception before hull, cost 0.2 extra launch energy per shield HP, and do not recharge in flight. Normal ammunition remains five minerals per launch. These upgrades apply to new missiles; in-flight shots keep their launch stats.
