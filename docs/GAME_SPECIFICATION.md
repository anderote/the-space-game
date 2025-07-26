# Space Game Clone - Technical Specification

## 📋 Overview

**Space Game Clone** is a real-time strategy tower defense game where players defend a central base against waves of enemy ships by constructing and managing a network of buildings connected through a power grid system.

### 🎯 Game Concept
- **Genre**: Real-time Strategy / Tower Defense
- **Perspective**: Top-down 2D
- **Core Mechanic**: Base defense through strategic building placement and resource management
- **Victory Condition**: Survive as many waves as possible
- **Defeat Condition**: Central base health reaches zero

### 🏗️ Key Systems
1. **Power Network System**: Buildings require power connections to operate
2. **Resource Management**: Minerals for construction, Energy for operations
3. **Wave-Based Combat**: Increasingly difficult enemy waves
4. **Building Construction**: 12 different building types with unique functions
5. **Research System**: Technology upgrades that improve capabilities
6. **Real-time Strategy**: Camera movement, building placement, tactical decisions

## 🌍 Game World

### World Dimensions
- **World Size**: 4800 × 2700 pixels
- **Screen Size**: 1600 × 900 pixels (configurable)
- **Camera**: Movable viewport with zoom capabilities (0.5x to 5.0x)

### Coordinate System
- **Origin**: Top-left corner (0, 0)
- **Units**: Pixels
- **Camera Position**: Center of the camera view in world coordinates
- **Building Positions**: Center point of the building

### Map Elements
- **Central Base**: Fixed position at world center (2400, 1350)
- **Asteroid Fields**: 4-8 clusters of 4 asteroids each, randomly distributed
- **Enemy Spawn Points**: Around the perimeter of the world
- **No Terrain**: Flat, obstacle-free environment except asteroids

## 🎮 Core Gameplay Loop

### Phase 1: Preparation (60 seconds initial)
1. **Build Power Infrastructure**: Place solar panels and connectors
2. **Establish Mining**: Place miners near asteroid clusters
3. **Basic Defense**: Build initial turrets around the base
4. **Resource Accumulation**: Gather minerals for expansion

### Phase 2: Wave Defense
1. **Enemy Wave Spawns**: Enemies appear around map perimeter
2. **Combat**: Turrets automatically engage enemies within range
3. **Resource Management**: Monitor power and energy consumption
4. **Tactical Decisions**: Build additional defenses, upgrade buildings

### Phase 3: Post-Wave Expansion
1. **Assess Damage**: Repair destroyed or damaged buildings
2. **Expand Infrastructure**: Add more miners, power generation
3. **Research**: Invest in technology upgrades
4. **Prepare for Next Wave**: Strengthen defenses based on enemy types

### Progression
- **Wave Difficulty**: Increases exponentially (1.6x growth factor)
- **Enemy Diversity**: New enemy types introduced over time
- **Special Waves**: Formation, Elite, Swarm, and Boss waves
- **Technology Advancement**: Research unlocks new capabilities

## 📊 Core Metrics

### Resources
- **Minerals**: Primary construction currency (starting: 600)
- **Energy**: Operational currency for building actions (starting: 50)
- **Power**: Real-time generation/consumption for building operation

### Building Stats
- **Health**: Damage resistance before destruction
- **Radius**: Physical size and interaction range
- **Connections**: Number of power network links (1-6)
- **Costs**: Mineral and energy requirements

### Combat Stats
- **Damage**: Amount of health removed per attack
- **Range**: Maximum engagement distance
- **Cooldown**: Time between attacks (in frames at 60 FPS)
- **Speed**: Movement rate for projectiles and enemies

### Timing
- **Frame Rate**: 60 FPS target
- **Wave Intervals**: 120 frames (2 seconds) between waves
- **Spawn Intervals**: 30 frames (0.5 seconds) between enemy spawns
- **Mining Cycles**: 240 frames (4 seconds) per mining operation

## 🏗️ Building System Overview

### Building Categories
1. **Power Infrastructure**: Solar panels, connectors, batteries
2. **Resource Extraction**: Miners, converters
3. **Defense Systems**: Turrets, lasers, super lasers, missile launchers
4. **Support Systems**: Repair nodes, hangars, force fields

### Construction Process
1. **Selection**: Use hotkey or click building type
2. **Placement**: Move cursor to valid location
3. **Validation**: Check resource availability and placement rules
4. **Construction**: Deduct costs and create building
5. **Connection**: Automatically connect to nearby power network

### Power Network Rules
- **Connection Range**: 170 pixels between buildings
- **Connection Limits**: Buildings have maximum connection counts
- **Power Propagation**: BFS algorithm distributes power through network
- **Network Isolation**: Disconnected buildings lose power and functionality

## ⚔️ Combat System Overview

### Enemy Behavior
- **Targeting**: Enemies prioritize nearest target (buildings or base)
- **Movement**: Path directly toward target with orbital behavior when close
- **Attacks**: Various weapon types based on enemy class
- **AI States**: Seeking, attacking, orbiting, retreating

### Turret Behavior
- **Auto-Targeting**: Engage nearest enemy within range
- **Line of Sight**: No obstruction mechanics (simplified)
- **Ammunition**: Unlimited with energy/mineral costs
- **Upgrade System**: Damage and range increase with building levels

### Damage System
- **Direct Damage**: Instant health reduction
- **Area Damage**: Splash damage for missiles and explosions
- **Damage Over Time**: Laser weapons apply continuous damage
- **Armor**: No armor system (simplified)

## 📈 Progression Systems

### Wave Progression
- **Difficulty Scaling**: Enemy health = 24 × wave number
- **Point System**: Waves spawn enemies worth total points based on formula
- **Composition Changes**: Enemy type ratios change with game phases
- **Special Events**: Every 6th wave is a formation wave

### Building Upgrades
- **Experience System**: Buildings gain XP from kills and operations
- **Level Advancement**: XP thresholds unlock new levels (max 10)
- **Stat Improvements**: Health, damage, efficiency increase per level
- **Cost Scaling**: Upgrade costs increase by 1.2x per level

### Research Tree
- **Categories**: Energy, Weapons, Defense, Mining, Engineering
- **Prerequisites**: Technology dependencies create branching paths
- **Research Points**: Earned through kills, waves, and operations
- **Permanent Upgrades**: Effects persist throughout game session

## 🎯 Victory and Defeat Conditions

### Defeat Conditions
- **Base Destroyed**: Central base health reaches zero
- **Power Failure**: All power generation buildings destroyed (optional)

### Victory Metrics
- **Survival Score**: Number of waves survived
- **Kill Score**: Total enemies destroyed
- **Efficiency Score**: Resources spent vs. damage dealt
- **High Score System**: Track best performance across sessions

### Difficulty Scaling
- **Exponential Growth**: Wave difficulty increases rapidly
- **Enemy Variety**: More complex enemy types in later waves
- **Resource Pressure**: Higher costs and energy demands
- **Time Pressure**: Shorter intervals between waves in late game

---

*This specification provides the foundation for understanding the complete game system. Additional detailed documentation covers specific mechanics, algorithms, and implementation details.* 