# Original-game fidelity audit: electricity, construction and mining

**Audit snapshot:** many discrepancies below were fixed during this implementation. See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for the current shipped behavior and remaining gaps.

Research date: 2026-10-11. This is an audit of the original `thespacegame.v83.swf`, compared with the browser edition during active development. Findings describe the original executable; they do not imply that every difference remains in the current branch. The lead implementation was already replacing pooled energy and cosmetic link animation while this document was written.

## Evidence and limits

Primary evidence is [Flashpoint's preserved original game data pack](https://download.unstable.life/gib-roms/Games/944ea5a3-558d-feda-4eb7-e900f3e60b06-1631483058057.zip), containing `content/storage.cloud.casualcollective.com/zones/pub/10/thespacegame.v83.swf`. The companion [original mechanics report](ORIGINAL_MECHANICS.md) and [numeric facts](research/original-constants.json) record provenance and file hashes. Only factual constants and independent behavioral descriptions are retained in this repository.

For this local investigation, readable decompiler output lives outside the repository at `/tmp/space-game-original-research/readable/`. It is obfuscated ActionScript 2, with bogus duplicate branches. Locations below refer to coherent branches of these local research files. Ordinary simulation callbacks occur every other game tick; the nominal normal-speed model is 40 game ticks/second and 20 ordinary building callbacks/second. Durations inferred from that model are distinguished from directly observed counter values. Runtime measurement remains useful for frame-rate-sensitive behavior.

| Original local source | Relevant locations |
| --- | --- |
| `root.as` | 528 game simulation; 606–649 scheduler; 1309 quick path; 1324 path reset; 1332 BFS; 1410 energy withdrawal; 1485 placement links; 1591 link commit; 1625 cable rendering; 1656 obstruction; 2185 colors |
| `buildingEnergy.as` | 90 constructor; 125 upgrades; 235 construction; 285 generation |
| `buildingStore.as` | 47 constructor; 89 upgrade; 175 construction; 205 periodic charging |
| `buildingMiner.as` | 252 constructor; 305 upgrade; 368 placement; 406 construction; 434 mining |
| `buildingRelay.as` | 31 constructor; 138 construction |
| `buildingLaser.as` | 199 constructor; 255–398 upgrades; 475 construction; 655 refill |
| `buildingRocket.as` | 48 constructor; 102 upgrade; 193 construction; 253 salvo; 293 refill |
| `buildingRepair.as` | 74 constructor; 140 upgrade; 207 construction; 235 drone creation; 265 refill |
| `repairDrone.as` | 509 docking; 628 repair; 650 constants |

## Highest-impact discrepancy: power is a local transaction

The original does not evenly share a single component-wide energy pool among nodes. Solar stations and energy stores are sources with independent balances. Consumers have small local working buffers. Relays carry paths but have no operational energy reservoir. A consumer asks for energy; a source balance decreases immediately; the amount actually received increases the consumer's buffer or its construction accumulator. A source may be empty while a connected consumer can still work briefly on its own reserve.

At initial inspection, `web/src/engine.js` used component energy in `useEnergy` (around line 121), accumulated generation centrally (around 127), and redistributed the remaining balance proportionally to each structure every frame (around 205). That erased source location, path, charging cadence and consumer reserve behavior. `renderer.js` around 122–123 animated a moving dot on every powered link from wall-clock time, including idle links. Those paths had no relationship to a mining cycle, shot or construction request. Both areas were being replaced during this audit.

Original source selection and transfer rules:

1. Calculate a shortest-hop path from each solar/store source to consumers, using BFS over existing links.
2. A node can be reached while incomplete, but only a relay-capable node with construction counter **at least 10** can extend a path farther. Relay-capable types are relay, solar and store. A leaf consumer cannot extend the path.
3. An upgrading solar/store still has counter at least 10 and can conduct through itself. It cannot supply energy until its construction equals its current target. This is different from disabling all conduction during upgrades.
4. Sort reachable source entries by hop depth **descending**: farthest available source first. Source order among equal-depth entries depends on original collection order and should not be asserted without runtime confirmation.
5. Skip a source without a valid route or without completed current construction. A storage consumer also skips all storage sources; it charges from solar only, even if that path travels through another storage building.
6. Transfer immediately from a source's available balance, then continue to another source if the requested amount has not been reached. Partial receipts are valid and accumulate where the consumer uses an accumulator.
7. No per-cable capacity or travel-time delay was found. The flash is a visual receipt of an immediate transfer.

The source appears to cap each successive withdrawal against the initial request rather than the remaining deficit, which can overdeliver from multiple partly depleted sources. This is a likely original bug. A modern implementation should conserve energy and record that correction rather than deliberately create energy overflow.

Independent behavioral pseudocode:

```text
when a consumer's own refill/build timer is due:
    deficit = desired buffer minus current buffer
    obtain eligible reachable sources and shortest-hop routes
    order sources by greatest hop count first
    for each eligible source until deficit is satisfied:
        received = minimum(source balance, remaining deficit)
        debit the source; credit the consumer or build accumulator
        if received is positive, emit a short-lived flow event for its route
```

Recommended event facts are source id, consumer id, route ids, amount, purpose and simulation timestamp. Derive electrical glow and node pulses from these facts. Use simulation time so pausing also freezes effects. Aggregate network totals for the HUD without using those totals as the operating energy model.

## Electricity visuals

The original separates persistent cables from active electrical flashes:

| Layer | Primary values and behavior |
| --- | --- |
| Backbone cable | Both endpoints relay energy; width 2, normal color `#1D74EA`, alpha 80% |
| Consumer cable | At least one endpoint is a leaf; width 1, same normal color and alpha |
| Blocked preview candidate | `#EA1D4E`, width 1; not committed as a usable link |
| Active energy withdrawal | Whole used route flashes cyan `#04D3FF`, width 2, alpha 100%; generated only for a positive withdrawal |
| Arc jitter | Each path vertex receives an independent integer x/y offset in `[-2, 1]` original world units |
| Flash lifetime | Counter initialized to 2; removed when nonpositive on an `onEnterFrame` callback, so roughly 2–3 display frames |
| Alternate color option | Backbone `#72ABF8`, leaf `#4692F9`, blocked preview `#FF5F85` |

The original flashes the entire route. It does not send a permanently orbiting particle down every live cable. A contemporary glow, subdivided jagged line, local node flare and moving highlight can improve the effect while preserving its meaning: they should be emitted only when power is actually withdrawn. Full batteries and inactive fully charged weapons must leave cables quiet. Storage charging may generate a large flash even without combat.

## Buffers and refill cadence

These are operational buffers, separate from construction energy accumulators:

| Structure | Local operating capacity | Original refill/generation action |
| --- | --- | --- |
| Relay | None | No steady transfer requests after construction |
| Solar levels 1/2/3 | 4 / 9 / 14 | Add 0.9 / 2.1 / 3 energy on each generation action; clamp to capacity |
| Store levels 1/2 | 200 / 600 | Ask solar sources for the entire missing capacity per charging action |
| Miner levels 1/2 | 1 / 1 | Ask for the missing part of 1 after mining logic on a miner callback |
| Repair station | 5 | Ask for missing capacity when it is not currently constructing a drone |
| Basic Laser | 1 | Refill toward half its energy-needed parameter |
| Pulser levels 1/2/3 | 2.5 / 5 / 7.5 | Same half-parameter rule |
| THEL levels 1/2/3 | 5 / 10 / 17.5 | Same half-parameter rule |
| Missile levels 1/2/3 | 1 / 3 / 5 | Request 1 per eligible ordinary callback, then clamp to capacity |

Solar resets a counter to 10 and otherwise decrements it: a generation action every 11 ordinary callbacks, nominally 0.55 seconds. Store similarly resets to 20: a charge action every 21 callbacks, nominally 1.05 seconds. Lasers reset to 1: a refill action every 2 callbacks, nominally 0.1 seconds. These distinct rhythms are part of the visible electrical activity.

The missile launcher charges and pays **per projectile**: 1 energy and 5 minerals, not a prepaid entire salvo. The basic laser and Pulser discharge their small local buffer across the firing sequence; THEL consumption follows its growing beam damage. Disconnection should therefore allow a loaded weapon's remaining reserve to act, then stop it when depleted.

## Construction and upgrades

At initial inspection, `engine.js` construction used a universal 2.5-second duration and energy approximately proportional to mineral price; `upgrade` around lines 84–91 changed stats instantly. Both differ materially from the original.

All normal buildings begin with full structure HP and construction counter 0, target 10. Health is not multiplied by build progress. An upgrade adds the max-HP increase to current HP immediately, preserving absolute preexisting damage, then increases the construction target. That building's ordinary function stops until the new target is reached. Upgrading a solar stops generation and source withdrawals; its old stored balance remains local. Completed relay-capable infrastructure can still conduct through an upgrading solar/store as explained above.

| Structure | Construction increment and payment | Upgrade target increase | Build timer values |
| --- | --- | --- | --- |
| Relay | Ask 1 E each relay callback; receipt >=0.5 advances 2 construction units; reset its temporary energy | No upgrade | Five accepted requests; no ordinary timer |
| Miner | Accumulate toward 1 E, then advance 1 and spend 1 E each miner callback | +5 | One request opportunity per special miner callback |
| Solar | 1 unit per 1 E accumulated at level 1; upgrades self-build without an external energy charge | +10, +10 | 10 / 8 / 6 ordinary ticks per steady increment |
| Store | 1 unit per 1 E accumulated; solar-only source rule applies | +10 | 10 / 8 ordinary ticks |
| Repair | 1 unit per 1 E accumulated | +10 | 15 / 13 ordinary ticks |
| Missile | 1 unit per 1 E accumulated | +20, +20 | 15 / 10 / 5 ordinary ticks |
| Basic Laser | Ask 1 E; any positive receipt advances 1 unit | — | Step adds 2 against threshold 15: steady 8 ordinary ticks |
| Pulser branch/levels | Same laser rule | +5 for conversion and each upgrade | Threshold 13 / 11 / 9: steady 7 / 6 / 5 ordinary ticks |
| THEL branch/levels | Same laser rule | +10 / +10 / +20 | Threshold 13 / 11 / 9: steady 7 / 6 / 5 ordinary ticks |

Counters are checked before the step increment. Initial construction starts at zero, so its first action is one callback later than a steady interval; upgrades may inherit a residual step. With constant sufficient supply, initial solar/store construction therefore takes approximately 5.05 seconds; initial repair/missile approximately 7.55 seconds; initial Basic Laser approximately 4.05 seconds. These wall times are derived from the nominal 20 Hz ordinary callbacks, not independently measured recordings.

Miner completion fills its 1 E local buffer. Missile completion adds 1 E. Other completion effects should be taken from the specific class rather than uniformly filling all structures. Original laser construction accepting any fractional positive energy and relay's >=0.5 threshold are unusual verified branches; choose deliberately whether the recreation preserves them.

Do not let an incomplete new relay transmit energy onward. This naturally creates sequential network construction: a distant blueprint can have physical cables in the graph but cannot receive through the unfinished relay until the relay completes. The original accepts disconnected non-miner blueprints; they can remain stalled indefinitely until another connection supplies them. A miner additionally requires at least one live asteroid in range at placement.

## Mining is intermittent and locally powered

At initial inspection, `engine.js` mining was continuous nearest-asteroid extraction at a per-second rate, with pooled energy paid every frame. The original does the following:

- Cache all eligible asteroids at placement: positive ore and center distance minus asteroid size less than 35.
- On each scheduled miner callback, remove exhausted cached targets and choose a random remaining asteroid.
- Mining counter starts at 60, triggers at >=60, then resets to 0; add 8 at the end of each active callback. After a successful first opportunity, subsequent cycles need 8 miner callbacks.
- A due cycle extracts an entire 4- or 10-mineral chunk, capped by the target's remaining ore, only if the local buffer contains 1 E. It consumes that local energy completely. A failed cycle resets the mining counter too, so a tiny energy shortage can cost a whole mining interval.
- Then attempt to refill the 1 E local buffer. New supply does not retroactively save the cycle that just failed.
- Draw a green `#00FF00` beam, width 1/2 by level, to a randomized point within approximately half the asteroid size. Its alpha decreases by 20 per miner callback until removed. This is a fading intermittent beam, not a continuous line to the center.
- When all cached asteroids are depleted, stop mining and show the depleted/low indicator. Manual mining off is a separate state.

The original UI advertises 80 and 200 minerals/minute. The root scheduler ticks miners only when its relay counter reaches 3, with a reset after 8. Coupled to the +8/60 cycle, this suggests a different literal throughput at nominal frame rate. The declared UI rate and code counters should remain separate research facts until measured in the original. Do not assert that 80/200 mpm has been demonstrated from runtime.

## Physical graph and placement differences

Initial `engine.js` placement around 51–59 required sum-of-radii clearance, a completed connected relay candidate and a current path to supply. Original placement rejects center distance less than either individual `_size` (effectively the larger size), uses strict range <90 at **both** cable endpoints, and does not require the candidate to be complete or connected. Miner placement still requires live ore.

Original new cables are committed from the placement preview's candidate list. They are not globally regenerated between every existing pair when an asteroid disappears or a building is removed. Leaf nodes accept one cable; existing relays reject additional links at six. Solar/store have no explicit relay-six cap. Ordering of candidate links uses the original spatial lookup's order, not an explicitly nearest-first sort. The currently developing browser graph added `linkInitialized`, which addresses unsolicited reconnection; review its load/restore and recycle behavior too.

Original link obstruction uses asteroid `_size/2 + 8`, other structure `_size/2`, and new-building-on-existing-cable clearance `_size/2`. Depleted-asteroid behavior depends on the asteroid's destruction/removal path; simply ignoring ore-zero objects in obstruction code should be checked against that lifecycle, not assumed equivalent.

## Repair details still worth matching

Drone construction costs 10 network energy and no minerals, requested directly in units of 1 on a separate construction counter. The station's local 5 E buffer is used for docking services. New drones have HP 20 of 60, energy 80 of 80, and initially return to base; they need healing before full deployment. A docked drone receives 3 HP per station energy and 6 local energy per station energy. Each docked moving callback can independently attempt those services if enough station energy exists.

Four drones maximum. Movement speed 1.8 per moving callback; repair range 50; each repair callback heals 1 HP and spends 1 drone energy. Launch cooldown is 60 moving callbacks; retarget cooldown 20. Original station dispatch checks use a 30-callback counter after the first delay. Nominal equivalents are speed 36 world units/second, 20 HP/second repair, 3-second launch delay and 1-second retarget delay. These are distinct from arbitrary continuous home recharge rates.

## Focused verification cases

1. A miner consumes local energy in a whole cycle, causes a flash only when refilling, and continues one stored cycle after its supply cable is lost.
2. An empty battery charges from solar through relays and emits a route flash; a second full battery alone cannot refill it.
3. An unfinished relay blocks onward power while allowing its own construction; completion starts the next structure down the chain.
4. Upgrading a solar preserves absolute damage and stored energy, stops its production/source withdrawals, but still allows a path through it to a different completed source.
5. A full idle network draws only static cables. Pausing freezes activity effects. Resuming does not manufacture transfers for elapsed wall time.
6. Two paths to a source choose a minimum-hop route. Two eligible sources prioritize greater source depth. Each displayed arc corresponds to an actual source debit.
7. Upgrading a miner interrupts production for its five construction increments and consumes five construction energy; it resumes with its local buffer filled.
8. Missile salvo minerals and energy are paid when each projectile launches; interruption between shots cannot spend resources for an unlaunched projectile.

These cases test meaningful gameplay consequences and observable electrical behavior without mirroring implementation details.
