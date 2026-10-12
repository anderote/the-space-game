# Clock speed, fabrication economy and tower mastery

Modern XP skill upgrades added 2026-10-11. Press **I** during play, then choose **Base stats** or **Tower mastery**. Base stats use Command XP points; tower specializations use a separate persistent Mastery XP pool. Each rank costs one point and applies immediately. Technology research still uses Intel. Classic disables these persistent bonuses; Sandbox earns progression too.

## Global skills

**Clock speed** replaces Build speed while preserving its saved `fabrication` ID and ranks. Every rank adds 5% to construction/upgrade speed, mining-cycle frequency and solar-cycle frequency, up to 250%. Energy/material cost per cycle stays intact. Harvesting and Power output improve quantity per cycle separately, so both stack with the clock.

**Efficient fabrication** reduces building and mineral-upgrade prices by 1% per rank, up to 50%. Costs round to the nearest whole mineral. At maximum, a solar costs 100 instead of 200, a laser costs 50 instead of 100, and a THEL conversion costs 250 instead of 500. Placement affordability, build cards, ghosts, inspectors and actual purchases use the same configured price. Missile ammunition remains five minerals per shot.

Buildings retain the original amounts paid in their `baseCost` and `upgradeSpent`. Buying a discount cannot change an existing building’s refund or allow a discounted build/recycle loop to create minerals.

## Class specializations

Every class has Health (+5% hull per rank), Armor (2% reduction of remaining hull damage per rank) and Powered shields (absorb 1% of otherwise unshielded damage per rank). Additional skills suit its function:

| Class | Additional mastery tracks | Per rank |
| --- | --- | --- |
| Energy relay | Link reach; Connection ports | +3% link range; +1 connection |
| Mineral miner | Extraction yield; Drill speed; Mining reach | +5% quantity per cycle; +5% cycle frequency; +3% mining range |
| Solar station | Collector output; Collector clock; Link reach | +5% energy per cycle; +5% generation frequency; +3% link range |
| Energy store | Storage density; Link reach | +5% capacity; +3% link range |
| Repair station | Repair speed; Service range; Drone reserves | +5% drone healing rate; +3% dispatch range; +5% carried drone energy |
| Basic laser | Damage; Fire rate; Targeting range | +5% damage; +3% firing-cycle speed; +3% range |
| Pulser | Damage; Fire rate; Targeting range | +5% damage; +3% firing-cycle speed; +3% range |
| THEL beam | Damage; Beam cycling; Targeting range | +5% full beam damage; +3% beam throughput; +3% range |
| Missile launcher | Damage; Fire rate; Targeting range | +5% damage; +3% salvo/launch-cycle speed; +3% range |

There are nine building/weapon specializations plus Missile ordnance, totaling 58 skill tracks. Every track has fifty ranks, including Connection ports. Basic laser points affect level-one lasers; Pulser points affect their upgraded branch. THEL has its own specialization. Converting a laser changes which specialization applies; the tree explains this distinction.

## Actual simulation effects

- Faster mining/solar cycles do not multiply their per-cycle yield twice. For example, maximum Clock speed divides the basic mining interval by 3.5, from 3 to approximately 0.857 seconds, and the solar interval from 0.55 to approximately 0.157 seconds. Tower cadence multiplies the same way; local output skills separately increase pulse size.
- Faster firing preserves shot energy and missile ammunition charges. THEL damage/cycling strengthens the entire sustained beam and increases energy draw proportionately. Laser/Pulser burst spacing and missile launch spacing scale with firing mastery.
- Shields cost 0.1 energy per absorbed hull point and fail without enough available power. Armor applies before shielding. Independent reductions combine on remaining damage rather than adding toward immunity: 40% global armor plus 20% tower armor gives 52% reduction.
- New hull capacity preserves the existing health percentage. Larger storage/drone reserves create no free energy; increased drone capacity must recharge normally. Repairs still consume one carried energy per restored hull point.
- Link/port upgrades rebuild eligible connections, preserving circular obstruction and endpoint limits. Range upgrades do not bypass terrain or enemy validity checks.
- Live cadence changes preserve each timer’s elapsed fraction. Accelerated callbacks carry small timestep overshoots rather than accumulating rounding delays; source supply and fixed simulation steps still constrain actual throughput.
- Saves include tower ranks and operation rules. Old profiles gain an empty specialization map while retaining existing global purchases and XP. Shared-point normalization rejects unknown tracks, excess ranks and overspending.

The inspector displays configured output, cycle/burst/salvo intervals, hull, range and defensive percentages. The tree shows each class’s invested points, rank caps and disabled purchases when the mastery budget is empty. Numbers remain initial balance tuning.

## Independent mastery experience

The third progression currency is Mastery XP: player-attributed ship kills award 20 XP each; completed paid construction and upgrades award 0.2 XP per mineral actually paid; restoring tracked battle/objective damage awards 0.2 XP per hull point. Free starting structures, canceled construction, intercepted missiles, mining, overkill and untracked maintenance grant no mastery reward. One point arrives at 100 XP, then subsequent levels require 150, 200, 250 XP, and so on.

Mastery points can be assigned to any of the ten specializations. Command XP remains reserved for global base stats, and Intel remains reserved for technology. All three persist between operations and after losses. All modern Free play and Challenge modes award rewards; Classic awards none. Construction completion consumes its pending reward once; snapshot counters bank only positive uncredited deltas alongside the profile.

Migration retains old mastery ranks, grants exactly enough mastery XP to fund them, and returns their former cost to the Command point budget. Subsequent normalization is idempotent. Existing operations start tracking mastery now; historical activity is not guessed.

Tower mastery’s Powered shields still provide energy-funded percentage absorption. The new mineral-purchased rechargeable module is a separate reserve, unlocked through Capacitive armor research. Armor acts first, the module reserve absorbs the remaining hit, and percentage shields apply to any damage spilling through. Shield-reserve damage earns no repair XP. [Rechargeable modules](RECHARGEABLE_SHIELDS.md).

Global Armor removes 3% of remaining damage per rank: `1 − 0.97^rank`. Tower Armor removes 2%: `1 − 0.98^rank`. At fifty ranks in both, combined reduction is approximately 92.1%, preserving finite incoming damage. New Command and Mastery XP earnings are doubled; banked history is unchanged.

## Missile ordnance

A separate ammunition specialization sits beside Missile launcher in Tower mastery. Launcher Health, Armor and Powered shields protect the building; ordnance hull/shields protect each projectile. Both use the same persistent mastery budget. Existing purchases retain their IDs and ranks.

| Ordnance track | Per rank | Rank-50 effect before other bonuses |
| --- | --- | --- |
| Warhead damage | +5% missile damage | +250% damage |
| Engagement range | +3% launcher acquisition range | +150% range |
| Blast radius | +4% explosion radius | +200% radius |
| Fuel reserves | +5% flight lifetime | 28 seconds from 8 |
| Missile hull | +5% projectile hull | 70 HP from 20 |
| Missile shields | Reserve equal to 2% of projectile hull | Reserve equal to 100% of upgraded hull |

Damage and acquisition range multiply the launcher specialization and research bonuses. Radius changes real explosion falloff, not only its visual. Fuel affects expiry and hunting time while inertia/turn limits remain. Shields are a finite reserve charged at launch, absorb point defense first, and cost 0.2 extra energy per shield HP. They never recharge in flight. Mineral ammunition cost stays five. New hull, fuel and shielding attach to the projectile snapshot at launch; live purchases do not repair or refill shots already traveling. The launcher inspector reports configured fuel, hull, shielding, blast radius and launch energy. Shielded missile trails appear cyan until the reserve is spent. Classic excludes persistent ordnance modifiers.
