# Building System

## 📋 Overview

The Building System is the primary player interaction mechanism, allowing construction and management of 12 different building types that work together to defend against enemy waves through a connected power network.

## 🏗️ Construction Mechanics

### Building Placement Process
1. **Selection**: Player presses hotkey or clicks building icon
2. **Preview Mode**: Ghost building follows mouse cursor
3. **Validation**: System checks placement requirements continuously
4. **Confirmation**: Left-click places building if valid
5. **Deduction**: Resources are deducted and construction begins
6. **Connection**: Building automatically connects to nearby power network

### Placement Validation Rules
```python
def validate_building_placement(building_type, x, y):
    # Check resource availability
    if minerals < building_cost[building_type]:
        return False, "Insufficient minerals"
    
    if energy < building_energy_cost[building_type]:
        return False, "Insufficient energy"
    
    # Check collision with existing buildings
    for existing in buildings:
        distance = calculate_distance(x, y, existing.x, existing.y)
        if distance < (building_radius + existing.radius):
            return False, "Too close to existing building"
    
    # Check collision with asteroids
    for asteroid in asteroids:
        distance = calculate_distance(x, y, asteroid.x, asteroid.y)
        if distance < (building_radius + asteroid.radius):
            return False, "Cannot build on asteroids"
    
    # Check world bounds
    if not is_within_world_bounds(x, y, building_radius):
        return False, "Outside world boundaries"
    
    return True, "Valid placement"
```

### Construction Timeline
- **Instant Placement**: Buildings appear immediately upon payment
- **No Construction Time**: Unlike some RTS games, buildings are operational instantly
- **Immediate Connection**: Power network connections established automatically
- **Resource Deduction**: Costs paid upfront before placement

## 🏢 Building Categories

### 1. Power Infrastructure

#### Solar Panel
```json
{
  "name": "Solar Panel",
  "hotkey": "S",
  "cost": 50,
  "health": 100,
  "radius": 25,
  "color": [255, 255, 0],
  "connections": 1,
  "function": "Generates 0.1 energy per level per frame"
}
```
- **Purpose**: Primary power generation
- **Strategy**: Place multiple units for steady energy supply
- **Vulnerability**: High priority enemy target
- **Scaling**: Efficiency increases with building level

#### Power Connector
```json
{
  "name": "Power Connector", 
  "hotkey": "C",
  "cost": 30,
  "health": 80,
  "radius": 20,
  "color": [0, 255, 255],
  "connections": 6,
  "function": "Hub for power distribution"
}
```
- **Purpose**: Network hub for connecting multiple buildings
- **Strategy**: Central placement to minimize total connection distance
- **Critical Role**: Network failure point if destroyed
- **Unique Feature**: Only building with 6 connection capacity

#### Battery
```json
{
  "name": "Battery",
  "hotkey": "B", 
  "cost": 80,
  "health": 120,
  "radius": 22,
  "color": [0, 255, 0],
  "connections": 1,
  "function": "Stores 120 energy per level"
}
```
- **Purpose**: Energy storage and load balancing
- **Strategy**: Buffer for high-consumption periods
- **Capacity**: Scales with building level (120 × level)
- **Network Role**: Stabilizes power grid during demand spikes

### 2. Resource Extraction

#### Asteroid Miner
```json
{
  "name": "Asteroid Miner",
  "hotkey": "M",
  "cost": 100, 
  "health": 100,
  "radius": 25,
  "color": [128, 128, 128],
  "connections": 1,
  "function": "Extracts minerals from nearby asteroids"
}
```
- **Purpose**: Primary mineral income source
- **Range**: 80 pixels for asteroid detection
- **Capacity**: Can mine up to 6 asteroids simultaneously
- **Operation**: 240 frames (4 seconds) per mining cycle
- **Energy Cost**: 6 energy per mining operation
- **Output**: 2.3 minerals per level per cycle

#### Resource Converter
```json
{
  "name": "Resource Converter",
  "hotkey": "V",
  "cost": 90,
  "health": 100, 
  "radius": 23,
  "color": [255, 165, 0],
  "connections": 1,
  "function": "Processes raw materials"
}
```
- **Purpose**: Advanced resource processing
- **Energy Cost**: 100 energy per conversion
- **Output**: 2 minerals per conversion
- **Cycle**: 120 frames (2 seconds) between conversions
- **Strategy**: Late-game mineral boost when asteroids depleted

### 3. Defense Systems

#### Defense Turret
```json
{
  "name": "Defense Turret",
  "hotkey": "T",
  "cost": 150,
  "health": 120,
  "radius": 28, 
  "color": [255, 0, 0],
  "connections": 1,
  "function": "Basic projectile defense"
}
```
- **Damage**: 15 per level per shot
- **Range**: 350 pixels
- **Cooldown**: 170 frames (2.8 seconds)
- **Costs**: 4 energy + 3 minerals per shot
- **Projectile**: Instant-hit with visual effects
- **Targeting**: Nearest enemy within range

#### Laser Turret
```json
{
  "name": "Laser Turret",
  "hotkey": "L", 
  "cost": 125,
  "health": 110,
  "radius": 26,
  "color": [255, 100, 100],
  "connections": 1,
  "function": "Continuous energy weapon"
}
```
- **Damage**: 0.25 per level per frame (continuous)
- **Range**: 270 pixels
- **Energy Cost**: 0.12 energy per level per frame
- **Beam Type**: Continuous damage while enemy in range
- **Advantage**: No cooldown, steady DPS
- **Disadvantage**: Continuous energy drain

#### Super Laser
```json
{
  "name": "Super Laser",
  "hotkey": "X",
  "cost": 500,
  "health": 200,
  "radius": 35,
  "color": [255, 0, 255], 
  "connections": 1,
  "function": "Ultimate long-range defense"
}
```
- **Damage**: 2.5 per level per frame (continuous)
- **Range**: 700 pixels (longest in game)
- **Energy Cost**: 1.2 energy per level per frame
- **Purpose**: Late-game powerhouse defense
- **Strategy**: Requires dedicated power generation
- **Target**: Heavy enemies and motherships

#### Missile Launcher
```json
{
  "name": "Missile Launcher",
  "hotkey": "Q",
  "cost": 300,
  "health": 140,
  "radius": 32,
  "color": [200, 100, 0],
  "connections": 1,
  "function": "Area damage missiles"
}
```
- **Damage**: 25 per shot + area damage
- **Range**: 400 pixels
- **Cooldown**: 200 frames (3.3 seconds)
- **Costs**: 8 energy + 5 minerals per shot
- **Splash Radius**: 60 pixels area damage
- **Strategy**: Effective against enemy groups

### 4. Support Systems

#### Repair Node
```json
{
  "name": "Repair Node",
  "hotkey": "R",
  "cost": 120,
  "health": 100,
  "radius": 24,
  "color": [0, 255, 0],
  "connections": 1, 
  "function": "Automatically repairs nearby buildings"
}
```
- **Repair Rate**: 0.15 health per level per frame
- **Range**: 275 pixels
- **Energy Cost**: 0.15 energy per frame when repairing
- **Behavior**: Auto-targets damaged buildings in range
- **Strategy**: Central placement for maximum coverage

#### Fighter Hangar
```json
{
  "name": "Fighter Hangar",
  "hotkey": "H",
  "cost": 250,
  "health": 150,
  "radius": 30,
  "color": [100, 150, 255],
  "connections": 2,
  "function": "Launches friendly attack ships"
}
```
- **Ship Capacity**: 4 fighters maximum
- **Launch Cooldown**: 300 frames (5 seconds)
- **Energy Cost**: 0.025 energy per frame maintenance
- **Ship Range**: 500 pixels engagement range
- **Recall Range**: 600 pixels return-to-base range
- **Regeneration**: 1200 frames (20 seconds) to replace destroyed fighters

#### Force Field Generator
```json
{
  "name": "Force Field Generator",
  "hotkey": "F",
  "cost": 400,
  "health": 180,
  "radius": 30,
  "color": [0, 200, 255],
  "connections": 1,
  "function": "Provides energy shields"
}
```
- **Shield Range**: 200 pixels
- **Shield Strength**: 50 additional health per building
- **Energy Cost**: 2.0 energy per frame (continuous)
- **Regen Rate**: 0.5 shield points per frame
- **Strategy**: Protect critical infrastructure clusters

## 🔧 Building Management

### Upgrade System
```python
class BuildingUpgrade:
    def __init__(self):
        self.max_level = 10
        self.cost_multiplier = 1.2
        self.xp_per_level = 600
        
    def calculate_upgrade_cost(self, base_cost, current_level):
        return int(base_cost * (self.cost_multiplier ** (current_level - 1)))
    
    def calculate_xp_needed(self, level):
        return self.xp_per_level * level
```

### Experience Gain Sources
- **Turret Kills**: 20 XP per enemy destroyed
- **Mining Operations**: 5 XP per successful mining cycle  
- **Repair Actions**: 10 XP per building repaired
- **Wave Survival**: 25 XP per wave survived (all buildings)

### Building States
```python
class BuildingState:
    CONSTRUCTING = "constructing"    # Not implemented (instant build)
    OPERATIONAL = "operational"      # Normal functioning
    UNPOWERED = "unpowered"         # No power connection
    DAMAGED = "damaged"             # Health below 50%
    DESTROYED = "destroyed"         # Health at 0
    DISABLED = "disabled"           # Manually shut down
```

### Health and Damage
- **Base Health**: Defined per building type
- **Health Scaling**: +20 health per upgrade level
- **Damage Threshold**: Buildings function until health reaches 0
- **Repair Mechanics**: Repair nodes restore health over time
- **Visual Indicators**: Health bars appear when damaged

## 🎯 Strategic Building Patterns

### Early Game Build Order
1. **Solar Panel** → Basic power generation
2. **Connector** → Network hub establishment
3. **Miner** → Resource extraction near asteroids
4. **Turret** → Basic defense around base
5. **Battery** → Energy storage for turret operations

### Mid Game Expansion
1. **Additional Miners** → Scale resource income
2. **Laser Turrets** → Upgrade defense capability
3. **Repair Node** → Maintain infrastructure
4. **Power Network Expansion** → Support distant buildings

### Late Game Powerhouse
1. **Super Lasers** → Ultimate defense
2. **Hangars** → Active defense units
3. **Force Fields** → Infrastructure protection
4. **Missile Launchers** → Area denial

### Network Topology Strategies

#### Star Pattern
- Central connector with 6 connections
- All buildings connect through hub
- **Advantage**: Minimal connection distance
- **Disadvantage**: Single point of failure

#### Ring Pattern  
- Buildings form connected loop
- Multiple paths between any two points
- **Advantage**: High redundancy
- **Disadvantage**: Higher connection overhead

#### Grid Pattern
- Regular spacing with connector intersections
- Balanced coverage and redundancy
- **Advantage**: Scalable and robust
- **Disadvantage**: Requires more connectors

## 📊 Building Performance Metrics

### Efficiency Measurements
- **Resource ROI**: Minerals earned vs. minerals spent
- **Energy Efficiency**: Energy generated vs. energy consumed
- **Defense Rating**: Damage dealt per unit cost
- **Network Connectivity**: Average paths between buildings

### Optimization Guidelines
- **Generator Ratio**: 1 solar panel per 3 combat buildings
- **Storage Ratio**: Battery capacity = 2× peak energy consumption
- **Defense Density**: 1 turret per 400 pixel radius coverage
- **Redundancy Factor**: 2+ paths between critical building pairs

---

*The Building System creates rich strategic depth through interdependent structures that must be carefully planned, positioned, and protected to create an effective defense network.* 