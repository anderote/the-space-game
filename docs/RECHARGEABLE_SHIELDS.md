# Rechargeable building shields

Capacitive armor research (Field engineering, nine Intel after Autoseal plating) unlocks mineral-purchased shield modules for every player building class. Existing owners gain the unlock automatically. Classic disables the modules; modern Expedition, Challenges, Endless and Sandbox support them. Mission-critical derelicts do not accept modules.

Select a completed building and click Install shield, then Upgrade shield for further tiers:

| Tier | Mineral price before discounts | Maximum reserve |
| --- | --- | --- |
| 1 | 100 | 20% of maximum hull |
| 2 | 160 | 35% of maximum hull |
| 3 | 240 | 50% of maximum hull |

Each installation adds five construction increments and follows the building's construction cadence and power rules. Modules cannot be installed during another upgrade. The module starts empty, and later tiers retain charge without granting extra shield HP. Ordinary hull upgrades and mastery health increases raise capacity without refilling it. Completed module construction awards mastery XP based on the actual paid cost, just like other upgrades. Paid spending participates in existing upgrade-refund rules.

After five seconds without a hit, charge restores at 10% maximum reserve per second, capped at 25 HP/s. Each point restored costs 0.2 energy. The simulation consumes local reserve first and requests the remainder through the actual power network; partial available energy buys only its corresponding charge. Recharge demand appears in power consumption and normal electricity flows. No power means no recharge; stored charge still absorbs hits while disconnected. Pausing stops recharge.

Damage order is armor, rechargeable reserve, existing energy-funded percentage absorption, then hull. Every absorbed hit restarts the recharge delay. Only actual hull damage creates repair debt and repair XP; charging shields grants no repair XP. The previous Capacitive armor and Tower mastery percentage-shield effects remain and apply to spillover damage.

Module level, charge, last-hit time, construction progress and amounts paid survive operation saves. Live research removal disables and empties the reserve; re-enabling it does not grant free charge. Technology unlocks persist across games, while building modules belong to their individual operation structures.

The inspector displays reserve HP, module tier, installation/recharge state and the next cost. A thin blue arc shows charge around the existing structure, with the existing hit pulse on absorption. This uses the shared canvas overlay rather than additional animated 3D meshes.

Modern enemy direct attacks, bomber impacts and suicide splash damage also receive a 0.9 multiplier. Difficulty scaling still applies. Classic retains the original damage multiplier.

See [validation](VALIDATION.md) for automated conservation checks and isolated browser proof. Shield prices, recharge rates and the damage adjustment are initial balance values.
