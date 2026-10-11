# Clock speed, fabrication economy and tower mastery

Modern XP skill upgrades added 2026-10-11. Press **I** during play, then choose **Base stats** or **Tower mastery**. All purchases use one persistent XP-point budget, cost one point per rank, and apply immediately. Technology research still uses Intel. Classic disables these persistent bonuses; Sandbox can use them without earning XP.

## Global skills

**Clock speed** replaces Build speed while preserving its saved `fabrication` ID and ranks. Every rank adds 5% to construction/upgrade speed, mining-cycle frequency and solar-cycle frequency, up to 100%. Energy/material cost per cycle stays intact. Harvesting and Power output improve quantity per cycle separately, so both stack with the clock.

**Efficient fabrication** reduces building and mineral-upgrade prices by 1% per rank, up to 20%. Costs round to the nearest whole mineral. At maximum, a solar costs 160 instead of 200, a laser costs 80 instead of 100, and a THEL conversion costs 400 instead of 500. Placement affordability, build cards, ghosts, inspectors and actual purchases use the same configured price. Missile ammunition remains five minerals per shot.

Buildings retain the original amounts paid in their `baseCost` and `upgradeSpent`. Buying a discount cannot change an existing building’s refund or allow a discounted build/recycle loop to create minerals.

## Class specializations

Every class has Health (+5% hull per rank), Armor (1% reduction of remaining hull damage per rank) and Powered shields (absorb 1% of otherwise unshielded damage per rank). Additional skills suit its function:

| Class | Additional mastery tracks | Per rank |
| --- | --- | --- |
| Energy relay | Link reach; Connection ports | +3% link range; +1 connection, six ranks maximum |
| Mineral miner | Extraction yield; Drill speed; Mining reach | +5% quantity per cycle; +5% cycle frequency; +3% mining range |
| Solar station | Collector output; Collector clock; Link reach | +5% energy per cycle; +5% generation frequency; +3% link range |
| Energy store | Storage density; Link reach | +5% capacity; +3% link range |
| Repair station | Repair speed; Service range; Drone reserves | +5% drone healing rate; +3% dispatch range; +5% carried drone energy |
| Basic laser | Damage; Fire rate; Targeting range | +5% damage; +3% firing-cycle speed; +3% range |
| Pulser | Damage; Fire rate; Targeting range | +5% damage; +3% firing-cycle speed; +3% range |
| THEL beam | Damage; Beam cycling; Targeting range | +5% full beam damage; +3% beam throughput; +3% range |
| Missile launcher | Damage; Fire rate; Targeting range | +5% damage; +3% salvo/launch-cycle speed; +3% range |

There are nine independent class specializations and 52 skill tracks. Every track has twenty ranks except Connection ports, which has six. Basic laser points affect level-one lasers; Pulser points affect their upgraded branch. THEL has its own specialization. Converting a laser changes which specialization applies; the tree explains this distinction.

## Actual simulation effects

- Faster mining/solar cycles do not multiply their per-cycle yield twice. For example, maximum Clock speed halves the basic mining interval from 3 to 1.5 seconds and the solar interval from 0.55 to 0.275 seconds. Tower cadence multiplies the same way; local output skills separately increase pulse size.
- Faster firing preserves shot energy and missile ammunition charges. THEL damage/cycling strengthens the entire sustained beam and increases energy draw proportionately. Laser/Pulser burst spacing and missile launch spacing scale with firing mastery.
- Shields cost 0.1 energy per absorbed hull point and fail without enough available power. Armor applies before shielding. Independent reductions combine on remaining damage rather than adding toward immunity: 40% global armor plus 20% tower armor gives 52% reduction.
- New hull capacity preserves the existing health percentage. Larger storage/drone reserves create no free energy; increased drone capacity must recharge normally. Repairs still consume one carried energy per restored hull point.
- Link/port upgrades rebuild eligible connections, preserving circular obstruction and endpoint limits. Range upgrades do not bypass terrain or enemy validity checks.
- Live cadence changes preserve each timer’s elapsed fraction. Accelerated callbacks carry small timestep overshoots rather than accumulating rounding delays; source supply and fixed simulation steps still constrain actual throughput.
- Saves include tower ranks and operation rules. Old profiles gain an empty specialization map while retaining existing global purchases and XP. Shared-point normalization rejects unknown tracks, excess ranks and overspending.

The inspector displays configured output, cycle/burst/salvo intervals, hull, range and defensive percentages. The tree shows each class’s invested points, rank caps and disabled purchases when the shared budget is empty. Numbers remain initial balance tuning.
