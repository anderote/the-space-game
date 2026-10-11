# The Space Game: original mechanics research

Research date: 2026-10-11. Target: **The Space Game** by David Scott / The Casual Collective (2009), with **The Space Game: Missions** treated as a separate sequel. These notes describe the original; they are not a claim that the modern edition already implements every detail.

The strongest evidence is the archived original executable, `zones/pub/10/thespacegame.v83.swf`, preserved in [Flashpoint's original-game data pack](https://download.unstable.life/gib-roms/Games/944ea5a3-558d-feda-4eb7-e900f3e60b06-1631483058057.zip). Its coherent, legible data and control branches were inspected locally using JPEXS. Only factual parameters are recorded here; no original executable, art, audio or decompiled implementation is added to this repository. The numeric companion is [research/original-constants.json](research/original-constants.json), including hashes, confidence notes and primary campaign wave parameters. The SWF contains obfuscation, so uncertain timing and branches are explicitly identified.

## The core game

This is a spatial mining and base-defense RTS: construct a network, extract finite asteroid minerals, grow solar generation and energy storage, defend against pirates, recycle obsolete infrastructure, and advance toward the current mission objective. Buildings are stationary. The player does not directly fly a ship or direct an army. Enemies attack the infrastructure from open space; there are no maze lanes or exit lives. Minerals are currency, including missile ammunition. Energy is generated locally and must reach the consumer through a valid network.

The original has a nine-mission campaign plus training, mining modes, survival modes and bonus modes. Mining missions reward total extraction, rather than minerals still in the bank. The display includes current mineral cash, mining income per minute, stored energy and percent, mission progress, incoming-wave information, a minimap, structure health/construction/energy, range circles and upgrade/recycle controls. Contemporary reviews praised fast building, legible information and the ability to plan while paused. [Jay is Games original review](https://jayisgames.com/review/the-space-game.php)

## Exact original controls

These keys were checked in the original SWF's keyboard handler, not inferred from a modern RTS layout.

| Input | Original action |
| --- | --- |
| 1 | Energy Relay |
| 2 | Mineral Miner |
| 3 | Solar Station |
| 4 | Energy Store |
| 5 | Repair Station |
| 6 | Basic Laser |
| 7 | Missile Launcher |
| U or Space | Upgrade selected completed building; Basic Laser takes the Pulser branch |
| P | Upgrade a Basic Laser to Pulser |
| T | Upgrade a Basic Laser to THEL |
| R | Recycle selected structure |
| Escape | Cancel construction selection |
| Shift held while placing | Continue placing the same structure |
| WASD / arrow keys | Pan |
| Q | Zoom in |
| E | Zoom out |
| Mouse drag | Pan |
| Mouse wheel | Zoom |
| Left click | Select or place |

**Neither Space nor P is a pause key in the original.** An added pause shortcut must use another key or avoid shadowing P's original context. Q/E direction matters: Q increases original scale, E decreases it. Original zoom scale runs 20%–100%, in 30-point keyboard steps; placement snaps to a 5-unit grid. Period guides independently corroborate most controls, though they often omit P. [Japanese period guide](https://kongregate.blog.fc2.com/blog-entry-180.html), [Tower Defense Wiki](https://w.atwiki.jp/tower_d/pages/68.html)

## Structure economy and upgrades

Costs below are incremental mineral costs, not cumulative totals. Range is in original world units. The original's damage field is not necessarily damage per complete shot or DPS: laser damage may be applied on multiple simulation ticks. See the machine-readable companion for exact counters and warnings.

| Structure | Base cost | HP by level | Upgrade costs | Capability |
| --- | ---: | --- | --- | --- |
| Energy Relay | 20 | 100 | none | Extends distribution; six connections |
| Mineral Miner | 45 | 300 / 500 | 100 | UI 80 / 200 minerals per minute |
| Solar Station | 200 | 600 / 800 / 1000 | 200 / 200 | Efficiency 30% / 70% / 100%; local capacity 4 / 9 / 14 |
| Energy Store | 300 | 500 / 750 | 500 | Capacity 200 / 600 |
| Repair Station | 300 | 400 / 600 | 150 | Four drones; dispatch range 200 / 300 |
| Basic Laser | 100 | 200 | branches below | Range 90; damage field 30; intercepts missiles |
| Missile Launcher | 400 | 500 / 520 / 540 | 500 / 1000 | Range 400 / 480 / 576; salvo 1 / 2 / 4 |

| Laser branch | Incremental costs | HP | Range | Damage field |
| --- | --- | --- | --- | --- |
| Pulser I / II / III | 100 / 150 / 300 | 300 / 500 / 900 | 110 / 115 / 130 | 12 / 14 / 16 |
| THEL I / II / III | 500 / 800 / 1000 | 400 / 600 / 960 | 200 / 290 / 390 | 1 / 5 / 10, plus sustained-beam ramp |

The total cost of a Pulser III, including Basic Laser, is 650; THEL III is 2400; Missile Launcher III is 1900. Upgrade paths are exclusive. The original has no generic level-four tower. Primary data agrees with most period [Ayumilove laser statistics](https://ayumilove.wordpress.com/2009/03/01/casualcollective-the-space-game-walkthrough-tips-review/).

Recycling normally refunds all base construction cost plus half of paid upgrade costs, multiplied by remaining-health fraction and rounded down. This encourages temporary defenses and redeployment. Recycling any miner also removes other exhausted miners. An indiscriminate 50% sell value loses an important original strategy. Some original storage/repair refund code appears to contain historical number-wrapper bugs; do not deliberately reproduce accidental zero/NaN results as a design feature.

## The network is a real graph

Only **Energy Relay, Solar Station and Energy Store** distribute energy onward. Miners, repair stations, lasers and missile launchers are endpoints; they receive a single connection and do not form a power backbone. Every building's energy connection range is 90; both ends must be strictly within that center-to-center distance.

The placement checks refuse additional links to an existing relay that already has six. No comparable explicit connection-count cap was found for solar stations or stores. The original checks geometry: asteroids and intervening buildings block links; a new building cannot sit on an existing link. Placement previews distinguish backbone links, dead ends and blocked segments. Connections are established during placement. Destroyed/recycled connectors can cut off a whole branch; energy must not remain globally available to disconnected defenses.

Miners reach asteroids when center distance minus the asteroid's size field is less than 35. They can draw from multiple in-range rocks and switch among those with remaining minerals. The rocks are finite, and depleted miners stop. Construction itself consumes energy over time, so an isolated blueprint is not magically completed just because minerals were available. Initial solar stations are prebuilt to bootstrap the network.

Solar generation and storage are distinct. Each consumer/producer has local reserves, and stores cannot charge from other stores. Building a store increases reserve capacity, not production. Global mining and global missile toggles are original controls: pause mining to save energy, pause missiles to save ammunition.

## Weapons and threats

Basic lasers and Pulsers can intercept incoming enemy missiles; THELs and missile launchers cannot. Pulsers are rapid close defense. THELs have the range to reach standoff ships and increase damage while holding a beam on a target, also increasing energy use. Reducing THEL to a slow projectile cannon or a flat damage figure misses its behavior.

Player missiles home and deal area damage. Each missile costs **5 minerals and 1 energy**. A level-three salvo is **four**, not five, missiles; the source resolves an error in one secondary table. Damage is 450 / 500 / 550 with splash radius 40 / 44 / 48.4. A volley reload counter of 200 ordinary building ticks corresponds nominally to ten seconds at normal speed; missiles within a salvo are separated by 15 ticks. The broad roles are also documented in the [Kongregate Wiki](https://kongregate.fandom.com/wiki/The_Space_Game%3A_Missions), whose precise timing should not override executable evidence.

Original enemy archetypes:

1. Small red fighters: short-range laser attackers.
2. Green missile launchers: standoff ships firing destructible homing missiles.
3. Orange Self Destructors: kamikaze attackers with area damage.
4. Yellow Ringers: shielded ships with a laser attack.
5. Gray Swarmers: many small fast attackers.
6. Purple Mother Ships: long-range beam plus launched fighters.
7. Mother Ship Attack Fighters: small children of a mothership.

Primary spawning gives ordinary wave ships 200 base HP times the wave multiplier and motherships an additional eightfold factor (1600 base HP). Child fighters have 100 HP. The default attack parameter is 50, but individual archetypes divide it differently and fire over multiple ticks; it is not a universal 50-damage shot. Mothership range is 200. Primary per-tick values and remaining confidence notes are in the JSON. [Period enemy guide](https://blog.livedoor.jp/lkrejg/archives/65334558.html)

## Repair has drones and a resource cycle

A repair station makes up to four flying drones, rather than applying a healing aura. Drone creation consumes 10 station energy and no additional minerals. Drones have 60 maximum HP, start at 20 HP, and are repaired/refueled at the station before deployment. They carry 80 local energy; one local energy heals one HP. The station exchanges one energy for six drone-energy units, and one station energy repairs three drone HP.

A drone's own healing reach is 50. Its nominal peak is one HP per moving tick, or 20 HP/second at normal speed, so four active drones could briefly reach 80 HP/second before travel, launch delays, recharging and target availability. Launch cooldown is 60 moving ticks (nominally three seconds), retarget cooldown 20 ticks (one second). The station upgrade extends dispatch range from 200 to 300; it does not unlock more than four drones.

## Original nine-mission campaign

The source displays **Mission 1** through **Mission 9**. It does not provide the modern edition's authored mission titles. Most missions use seeded narrow asteroid belts with random rotation. The numeric generation parameters and mining-wave records are preserved in the JSON; exact pixel-for-pixel map recreation would additionally require matching the original generator and PRNG semantics.

| Mission | Goal | Cash after initial solar | Primary focus |
| --- | --- | ---: | --- |
| 1 | Mine half the field | 500 | Three red-fighter waves |
| 2 | Mine half the field | 600 | Missile ships |
| 3 | Survive 10 minutes | 700 | Timed mixed threats |
| 4 | Mine half the field | 800 | Yellow ringers and mixed ships |
| 5 | Mine half the field | 900 | Swarmers |
| 6 | Destroy mothership assault | 19800 | No asteroid field; prepare for first arrival at 3 minutes |
| 7 | Mine half the field | 1100 | All six main enemy types |
| 8 | Mine half the field | 1200 | Larger mixed waves, including eight motherships |
| 9 | Survive 20 minutes | 1300 | Escalating timed mixed attack |

**Mining-mission waves are triggered by mining-progress percentages, not elapsed time.** For example, Mission 1 launches 5/10/15 red fighters at 20%/50%/80% of its mining goal. Spending minerals does not lower mined progress. All seven base structures are enabled in these original campaign missions; progression introduces threats, not a persistent stat tree.

Mission 6 has six source wave records (5/5/5/5/5/10 motherships at 180/190/200/210/220/300 seconds), but its victory check after 190 seconds only checks active ships. A strong defense may finish before all later scheduled ships appear. This explains some conflicting reported ship totals and should be documented if corrected.

## Sequel: The Space Game: Missions

The sequel was published on Kongregate July 20, 2009 and on Newgrounds July 26, 2009. Its developer description advertises **21 missions and four difficulty levels**, including repairing space stations, defending jump ships, mining mega asteroids and destroying new super ships. These are not original-nine campaign scenarios. [Creator's Kongregate page](https://www.kongregate.com/en/games/casualcollective/the-space-game-missions), [creator's Newgrounds submission](https://www.newgrounds.com/portal/view/505024)

Period guides describe eight main missions plus thirteen side missions, progression across a mission map, and harder difficulties unlocked by completion. Player reviews repeatedly request target prioritization: automatic missiles could waste ammunition on ringers while ignoring motherships. Escorting a moving jump ship changes base-building into a forward construction/repair problem. These are strong expansion ideas, but a newly written campaign, permanent upgrades, target priorities, challenge modifiers, medals or unlock trees should be presented as additions. [Sequel review and contemporary discussion](https://jayisgames.com/review/the-space-game-missions.php)

## Preservation and sources

The [Space Game Launcher preservation project](https://github.com/br3nt/the-space-game-launcher) explains the loading failure: common approximately 16 KB SWFs are only loaders. They request a widget, session configuration and the full game from now-dead Casual Collective servers. Its restoration uses a service worker plus Ruffle; it does not ship original game assets. The original data pack contains a 1,942,037-byte game and the loader/widget dependencies. The sequel's corresponding [Flashpoint pack](https://download.unstable.life/gib-roms/Games/3f7c5f17-19df-30d3-2deb-a6c1b7252af3-1631483066872.zip) preserves `zones/pub/16/tsgmissions.v16.swf`.

The restoration project is a useful playable reference and documents archived package locations. Its MIT license covers the launcher, not Casual Collective's game. These notes and the modern implementation do not depend on redistributing the original files.

Visual-reference sources include the [original review](https://jayisgames.com/review/the-space-game.php), its [player base screenshot](https://jayisgames.com/images/hs_pam_thespacegame_newbase.jpg), the [period wiki's structure images](https://w.atwiki.jp/tower_d/pages/68.html), and the [sequel guide's screenshots](https://kongregate.blog.fc2.com/blog-entry-180.html). They are reference material, not artwork licensed for the new game's asset bundle.

## Fidelity checks before claiming a full reproduction

- Preserve exact numbered ordering and Space/U/P/T/R behavior; keep modern pause controls separate.
- Support distributed energy and broken network branches; do not let every building relay.
- Retain finite asteroids, multi-miner expansion, mineral-funded missiles, recycling and global toggles.
- Keep construction/upgrade delays and energy pressure meaningful.
- Retain missile interception, standoff threats, swarm pressure and THEL's sustained ramp.
- Distinguish original campaign goals/wave triggers from authored expansion missions and permanent unlocks.
- Measure original wall-clock production and weapon cycles in a live emulator before claiming frame-level fidelity. The SWF is 40 FPS, with ordinary entities at 20 ticks/second and miners/relays staggered separately. The displayed miner income and some community timing estimates do not necessarily equal actual simulation throughput.
