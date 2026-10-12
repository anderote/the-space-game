# Expedition waves

All modern campaign missions have enemies and require their primary objective, minimum operation time and every scheduled wave to be cleared. The minimum is a floor; extracting enough minerals or defeating surviving enemies can take longer. Par time is the minimum plus two minutes.

| Sector | Minimum duration | Waves | Formation theme |
| --- | --- | --- | --- |
| 1. First light | 3:30 | 4 | Prospector raids |
| 2. A wider orbit | 4:30 | 5 | Outer-deposit ambushes |
| 3. Unwelcome company | 5:30 | 6 | Raider escalation |
| 4. The long night | 6:30 | 7 | Energy siege |
| 5. Signal in the dust | 7:00 | 7 | Rescue corridor |
| 6. Scattershot | 7:30 | 8 | Swarm fronts |
| 7. Heavy metal | 8:00 | 8 | Capital pursuit |
| 8. Broken constellation | 8:30 | 9 | Fractured perimeter |
| 9. Lifeline | 9:00 | 9 | Jump-drive blockade |
| 10. Solar storm | 9:30 | 10 | Storm hunters |
| 11. The last reserve | 10:00 | 10 | Reserve interdiction |
| 12. Hold the line | 11:00 | 12 | Three capital offensives |

The early sectors provide 55–65 seconds to establish defenses. Inter-wave gaps are 45–64 seconds, with occasional longer recovery intervals. Counts scale with difficulty, then multiply the original fleet size by five. Each new enemy has half the previous hull and attack damage. Early missions introduce fighters and swarms before ring ships; later missions add bombers, suicide ships, opposite-side flanks and capital escorts. Heavy metal has two separate capital waves, and Hold the line has three, with the last arriving in the final wave. Rare elites retain their every-third-wave rewards.

The HUD advertises the next wave number, countdown, formation and incoming compass bearing. Compass north is the top of the sector map. Every distinct approach has a minimap arrow at its actual spawn perimeter; arrows turn red in the last fifteen seconds. Spawn spread is at most about nine degrees around an authored bearing. Countdown time follows simulation speed and pauses with the operation. Sandbox shows ON YOUR SIGNAL and the next manually called wave’s bearing. Endless and Challenges use deterministic advertised approach bearings too. Classic preserves its recovered schedules.

Existing campaign completion records and progression are retained. Saved campaign operations keep their ships, resources and elapsed time, and use the current sector definition for remaining waves. New operation timers and plans are covered by simulation tests.

These are initial balance settings. Automated checks cover viable ore, actual formations, directions, objective gating and all twelve sectors; a full campaign playthrough and long-duration balance testing remain.

## Streamed arrivals and open equipment access

Modern fleets queue five times each authored group, interleave approach groups, and move capitals to the end of the stream. Arrival spacing distributes the fleet over 70% of the wave gap, bounded to 8–40 seconds. The first ship arrives immediately; further ships arrive individually at scheduled simulation times. Repeated manual calls append fleets behind already queued arrivals. HUD hostile counts include a separate inbound count. Final-wave victory and wave-clear accounting wait for the pending queue. Queue entries preserve their originating wave for Endless hull scaling and survive pause/resume. Existing saved enemies retain their current hull.

All modern sectors and challenges now grant the full seven-key build palette plus Pulser and THEL upgrade branches from the start, including old resumed mission definitions. Classic retains its source-backed equipment access. Campaign sector and cosmetic unlocks remain.

Ring ships and motherships now intercept friendly missiles in modern combat. Missile acceleration, velocity inertia, a bounded turn rate and swept hull collision allow evasive passes and fuel exhaustion. The half-strength per-enemy modern hull and attack balance remains in effect.
