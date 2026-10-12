# Fighter hangars and craft

A modern addition, available immediately with build key **8**. Classic keeps its original seven structures.

| Hangar tier | Berths | Intercept range | Launch interval | Service units/s | Upgrade cost |
| --- | --- | --- | --- | --- | --- |
| 1 | 2 | 340 | 5s | 10 | Build: 350 minerals |
| 2 | 3 | 390 | 4.5s | 13 | 350 minerals |
| 3 | 4 | 440 | 4s | 16 | 600 minerals |
| 4 | 6 | 500 | 3.5s | 20 | 900 minerals |

Fabrication discounts apply to hangar construction/upgrades. New craft cost 20 minerals each, without a recycle refund, plus all 24 carried energy and any shield charge at 0.2 energy per shield HP. Hangars accumulate a local reserve from their connected network. They manufacture only when an enemy is within interception range, a berth is free, construction is complete, launch cooldown has ended and resources are available.

Baseline craft have 80 hull, 120 movement speed, 20 seconds of fuel, 90 gun range, and 20 damage every 0.6 seconds. Each shot consumes one carried energy. Global armor and hull/laser damage research stack with aircraft mastery. Aircraft turn at a bounded rate, visibly fly to enemies, and earn normal player-attributed combat XP, kills, Intel and mastery. Enemy fighters and swarms can target airborne craft. Aircraft shields absorb damage before hull and do not recharge during flight.

Craft return when no valid enemy remains, the target exceeds the hangar patrol area, hull falls below 35%, ammunition is empty, fuel approaches the time needed to return, or the hangar is upgrading. Docking restores tracked damage, ammunition energy, fuel and shields with real network power. Hull and ammunition cost one energy per restored unit; fuel and shield reserves cost 0.2 per unit. Only repair of recorded battle damage earns repair XP/mastery. Survivors relaunch after replenishment rather than being manufactured and charged again. Exhausted fuel or loss/recycling of the home hangar removes the craft without a refund or player kill reward.

## Mastery

**Fighter hangar** has berth capacity (+1 each rank), launch cadence (+3% cycling), dock servicing (+5%), and ordinary building health, armor and powered shields.

**Fighter craft** has damage (+5%), firing speed (+3%), gun range (+3%), movement speed (+3%), endurance (+5%), hull (+5%), multiplicative armor (2% less remaining damage), and shields (reserve equal to 2% of upgraded hull). All tracks cap at fifty and use the existing shared mastery pool. Craft settings are attached at manufacture; purchasing upgrades cannot heal existing aircraft or refill reserves. Existing aircraft retain their original configuration through later dock/relaunch cycles.

Hangar inspectors show tier, berth capacity, intercept range, launch/service rates, flying/docked counts and new-craft price. Aircraft render as cyan delta-wing silhouettes with engine wakes, shield rings and damaged-hull bars; the minimap marks airborne fighters. Flight, targets, resources, home assignments and cooldowns are included in snapshots.
