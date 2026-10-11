# The Space Game: reference research

Research date: 2026-10-11. This document records the historical game, evidence gathered for this browser reconstruction, and the limits of what was verified. It describes the reference game; it is not a claim that every feature or original tuning value has already been implemented.

No original game binaries, extracted code, sounds, textures, or screenshots are tracked or distributed with this repository. The full original and Missions SWFs and archive bundles are retained locally in the git-ignored `.reference/` directory, with a hash manifest. Decompiled inspection material is private under `/tmp/the-space-game-research`. The machine-readable [source manifest](research/sources.json) records URLs, hashes, sizes, and verification status. Temporary files may disappear; the URLs and hashes provide the reproducible record.

## Identity and versions

The target is the asteroid-mining and defense strategy game created by **David Scott / The Casual Collective**, with sound credited to **Soma Tone**, released in early 2009. It is a two-dimensional network-building game: structures mine finite asteroid deposits, solar stations power the network, and weapons defend it against ships arriving from open space.

There are two relevant releases:

| Release | Evidence | Distinction |
| --- | --- | --- |
| **The Space Game** | [Flashpoint entry](https://ooooooooo.ooo/?id=944ea5a3-558d-feda-4eb7-e900f3e60b06), [contemporary review](https://jayisgames.com/review/the-space-game.php) | Original. The archived metadata lists version 1.07 and February 16, 2009; the review was published February 15. Treat the release as February 2009 rather than resolving that one-day discrepancy without further evidence. |
| **The Space Game: Missions** | [Kongregate developer listing](https://www.kongregate.com/en/games/casualcollective/the-space-game-missions), [Newgrounds author upload](https://www.newgrounds.com/portal/view/504419), [Flashpoint entry](https://ooooooooo.ooo/?id=3f7c5f17-19df-30d3-2deb-a6c1b7252af3) | Follow-up with 21 missions and four difficulties. Kongregate lists July 20, 2009; Newgrounds was uploaded July 22. |

The Missions developer descriptions identify station repair, jump-ship defense, giant-asteroid mining, and enemy super ships. These are useful references for extending objectives, but they must not be attributed to the original nine-mission campaign.

Unrelated games share the name: the Kongregate shooter by `unforsakengames`, *Ascent: The Space Game*, and *The Space Game Redux* by Squared Tower. Their images, controls, or features are not evidence for this project. A modern AI-generated page on `seeles.ai` was also excluded: its command-hub design is not reliable evidence of original behavior.

## Evidence standards

- **Directly verified:** downloaded binary contents and hashes; original keyboard handler; original mode strings; pixels visible in the downloaded screenshots.
- **Publisher/author confirmed:** the sequel's mission count, release listing, and broad mission types.
- **Contemporary secondary evidence:** reviews, walkthroughs, and player descriptions. These establish reception and plausible behavior but are not substitutes for exact simulation constants.
- **Implementation proposals:** recommendations in this document are explicitly marked and do not claim historical authenticity.
- **Unverified:** full live playback through Ruffle, frame-by-frame behavior, every original mission script, all difficulty multipliers, and exact timing inferred only from descriptions.

The original SWF was inspected with JPEXS for factual controls and identifiers. Decompiled source remains outside the repository and is not an implementation dependency. Numeric mechanics research is tracked separately in [original-constants.json](research/original-constants.json); consult its evidence and uncertainty fields when using a value.

## Original controls

The original archived `thespacegame.v83.swf` keyboard handler was directly inspected. The important compatibility detail is that **P selects the Pulser upgrade; Space upgrades the selected building**. Neither should be reassigned to pause in the original control scheme.

| Input | Verified original action |
| --- | --- |
| `1` | Build Energy Relay |
| `2` | Build Mineral Miner |
| `3` | Build Solar Station |
| `4` | Build Energy Store |
| `5` | Build Repair Station |
| `6` | Build Basic Laser |
| `7` | Build Missile Launcher |
| `U` or `Space` | Default upgrade of an eligible completed selected building |
| `P` | Basic Laser to Pulser |
| `T` | Basic Laser to THEL |
| `R` | Recycle selected structure |
| `Escape` | Cancel building placement |
| `WASD` or arrow keys | Pan the map |
| `Q` | Zoom in |
| `E` | Zoom out |
| Mouse wheel | Zoom |
| Left-drag background | Pan |

The Q/E handler changes the target zoom by 30 percentage points, bounded to 20–100%. The inspected original handler contains no pause key binding. Pause, Slow, Normal, and Fast are visible toolbar controls. The downloaded screenshot and contemporary descriptions establish that pausing is part of the intended interface; an additional modern pause shortcut should avoid the original keys.

Private inspection location: `original-scripts/scripts/DefineSprite_1084/frame_1/DoAction.as`, lines 618–714, beneath the temporary research directory. [Miniplay's host instructions](https://www.miniplay.com/game/the-space-game) independently corroborate Q/E/U/T/R. [Addicting Games](https://www.addictinggames.com/strategy/the-space-game) corroborates WASD, Q/E, and mouse construction. The original review independently mentions numeric build keys and Space upgrading.

## Gameplay and progression

The central tension is expanding income while maintaining a connected, adequately powered defensive network. Mineral Miners work near finite deposits. Solar Stations generate energy. Storage buffers demand, and relays extend the network across the field. Laser defenses, missile launchers, and repair structures make the economic network survivable. [Chris Jean's contemporary explanation](https://chrisjean.com/the-space-game-a-flash-rts/) identifies minerals and energy as the two resources, finite asteroid depletion, and mineral expenditure for missile ammunition.

The original binary contains identifiers for nine missions and two training levels. It also contains these mode labels:

- Easy Mode, Normal Mode, Hard Mode, Madness!
- Survivor: Gentle, Survivor: Bring it, Survivor: No Hope
- Wave Mode, Speed Miner, Sandbox Mode

The archive notes that some content was membership-gated. Its default original-game launcher is a modified membership-unlocked build. Finding those labels proves their presence in the archive, not that every mode was available to every historical portal user.

Verified original UI also includes separate global switches for miners and missiles. These are important resource-management affordances: a player should be able to control extraction or ammunition use without dismantling the network. Exact original simulation effects require checking their implementation separately.

The [Ayumilove original guide](https://ayumilove.wordpress.com/2009/03/01/casualcollective-the-space-game-walkthrough-tips-review/) describes the Basic Laser branching into Pulser and THEL, with the Pulser handling small targets and missiles and THEL useful against motherships. It also describes motherships spawning fighters. Its reported per-hit and per-frame damage numbers should not be conflated with damage per second.

### What reviews reveal

The [February 2009 Jay Is Games review](https://jayisgames.com/review/the-space-game.php) values open placement, understandable indicators, rapid keyboard building, approaching swarms, and the power-relay network. Player discussion explicitly appreciates building while paused or slowed. Criticism centers on repeated objectives and tactics involving cheap, recyclable basic defenses. These observations support preserving planning and rebuilding while adding mission variety.

The [July 2009 sequel review and comments](https://jayisgames.com/review/the-space-game-missions.php) identify more varied objectives, difficult optional missions, a moving-ship escort, and final super ships. One player asks for persistent peaceful mining. These are reception signals, not an exact design specification.

**Proposed extension:** add campaign context, distinct challenges, and persistent accomplishment tracking around the economic/defense loop. Unlocks should preserve access to the original controls and distinguish challenge rewards from original mechanics. A relaxed sandbox can support experimentation with the network, while campaign objectives can require repair, escort, extraction, and survival. These are modern design choices unless separately tied to specific original missions.

## Visual reference and interface

The screenshots below were downloaded and inspected. Repository documentation links to them; no copies are committed.

| Reference | Dimensions | Use |
| --- | --- | --- |
| [Original Mission 1](https://infinity.unstable.life/images/Screenshots/94/4e/944ea5a3-558d-feda-4eb7-e900f3e60b06.png) | 700×525 | Clear original build palette, status bar, resource area, minimap, asteroids, and power links. |
| [Missions gameplay](https://infinity.unstable.life/images/Screenshots/3f/7c/3f7c5f17-19df-30d3-2deb-a6c1b7252af3.png) | 697×522 | Follow-up visual comparison; populated network and depleted energy state. |
| [Original Mission 6 formation](https://ayumilove.files.wordpress.com/2009/03/cc_spacegame_mission6b.jpg) | 700×502 | Structure silhouettes, energy stores, compact defense, and threat countdown. Guide annotations are external to the game. |
| [Mining tutorial](https://cdn.gamingcloud.com/img/general/games/screen/2863.jpg) | 701×525 | Tutorial sidebar and first mining/energy setup. |
| [Late Survivor defense network](https://jayisgames.com/images/hs_pam_thespacegame_newbase.jpg) | 1280×960 file; only the upper-left region contains gameplay | Dense network and long weapon beams. Do not treat the white surrounding area as game UI. |
| [Host controls diagram](https://www.officegamespot.com/office_games_images/the-space-game-control.gif) | 300×254 | Coarse movement illustration, not a complete keyboard reference. |

### Direct pixel observations

Normal gameplay leaves most of the screen open. A thin top toolbar holds speed controls, mission/timer information, a colored objective meter, and Quit/Restart/Setup. A minimap occupies the bottom-left. Seven icon buttons span the bottom middle; each has a separate Info button. Resource numbers and a cyan energy bar occupy the bottom-right. The left instructional sidebar is tutorial-specific, not the normal permanent layout.

The seven palette costs visible in the original screenshot are **20, 45, 200, 300, 300, 100, and 400 minerals**, matching relay/miner/solar/storage/repair/laser/missile order. The `m` labels are mineral costs, not weapon ranges.

| Element | Observed appearance |
| --- | --- |
| Background | Dark starfield and soft nebula, tinted green, blue, or purple across examples |
| Asteroids | Irregular brown rocky forms with bright green ore patches |
| Relays | Small silver-blue nodes with solid straight blue links |
| Miners | Small black circular chassis with a green center and thin green mining beam |
| Solar | Black circular body with white/cyan bow-tie-like panels |
| Energy storage | Black circle containing two bright cyan vertical bars |
| Repair | Four small cyan circles around a center |
| Basic laser | Yellow core inside a dark circular body |
| Missile launcher | Magenta polygon inside a dark chassis |
| Network | Bright blue lines; readable even when dense |
| Resource area | Mineral amount and rate, then cyan energy amount/percentage and fill bar |

**Proposed graphics direction:** retain these distinct silhouettes and color roles while adding original higher-resolution geometry, surface texture, shaded asteroid relief, restrained bloom, and weapon illumination. At wide zoom, links, ore, power state, placement validity, and incoming enemies must remain legible. Strong effects should not obscure the network or the small-target/mothership distinction.

## Archives and file verification

[9o3o's FAQ](https://ooooooooo.ooo/faq/) identifies it as an experimental Flashpoint frontend that uses Ruffle for Flash and JSZip/request redirection for archived dependencies. This explains why downloading only a portal SWF may fail: a small loader can request additional files from defunct services.

Both full packages below were successfully downloaded and opened as ZIP archives. SWF signatures and extracted file sizes were checked. **Successful live gameplay in Ruffle has not been verified in this research pass.**

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Original bundle](https://download.unstable.life/gib-roms/Games/944ea5a3-558d-feda-4eb7-e900f3e60b06-1631483058057.zip) | 4,772,279 | `80790aab1c8da74fa7d2202fc9a788e23e7480a7c41933ff5140c9f8534dd5ab` |
| Original actual game, `zones/pub/10/thespacegame.v83.swf` | 1,942,037 | `8d193481fb87e994a53d390a96bf9774b26fa5d479e4af2f0e1dd3497955d237` |
| Original alternate actual game, `zones/pub/100/thespacegame.v83.swf` | 1,941,696 | `2b0dc9d8c5e87677cebdf61f16256687d13a33bafef8f126756636a601aa68e6` |
| Original loader, `games/thespacegame.swf` | 16,745 | `b37ddffae11996b89897780c724e6b743816cae1c791992a0df1254504a55a2a` |
| [Missions bundle](https://download.unstable.life/gib-roms/Games/3f7c5f17-19df-30d3-2deb-a6c1b7252af3-1631483066872.zip) | 3,382,593 | `937d1e37774f82a1968f122e21d715e78988eac8579902cffb2c185da12b36b2` |
| Missions actual game, `zones/pub/16/tsgmissions.v16.swf` | 2,963,297 | `f88a785b9701e5cdcdb49c9349057d88f58e367a63a006c7d009f715464291cf` |
| [OfficeGameSpot Missions loader](https://www.officegamespot.com/flashgames/the-space-game-missions.swf) | 16,098 | `d2ae5711f2aaf4f742630f0f14876c7031f90c2ca5375de01c4bb8c32846b2ef` |

The original bundle contains the standard and modified launchers, both numbered publication directories, background SWFs, widgets, and session endpoints. The Missions bundle contains its launcher, actual game, widget, and session dependencies. The original direct host `storage.cloud.casualcollective.com` did not resolve during this pass. Preserved copies were obtained from Flashpoint infrastructure instead.

The OfficeGameSpot file was confirmed to be a loader containing a request to `widget.casualcollective.com/load`. Its download success does not establish a working standalone game. Archive variant names and byte differences are retained because they may matter when comparing behavior.

## Walkthroughs, videos, and remaining work

- [Original Mission 6 video](https://www.youtube.com/watch?v=bAARH9NuTtE) — located through the embedded link in the contemporary Ayumilove post. The link was recovered; full playback was not reviewed.
- [Ayumilove Missions walkthrough](https://ayumilove.wordpress.com/2009/07/30/the-space-game-mission-walkthrough-official-guide/) — historical achievement and completion context; its save-file links were not downloaded or validated.
- The other embedded video, `Ml5NKh8-vkE`, is explicitly presented as an infinite-energy exploit. It is not a reference for ordinary balance.
- [Kongregate community wiki](https://kongregate.fandom.com/wiki/The_Space_Game%3A_Missions) — secondary candidate source for unit data. Some timing descriptions are explicitly uncertain; prefer binary or observed-game verification before adopting exact numbers.

Remaining fidelity work includes checking original and Missions playback, verifying full enemy movement/target-selection behavior, comparing mining and energy transfer at equal simulation speed, checking paused construction semantics, and playing every mission objective. Original balance and modern campaign additions should be reported separately when their behavior differs. A reconstruction can accurately preserve controls and the central loop before it achieves frame-exact reproduction.
