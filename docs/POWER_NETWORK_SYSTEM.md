# Power Network System

## 📋 Overview

The Power Network System is the core unique mechanic that differentiates this game from traditional tower defense games. All buildings require power connections to operate, creating strategic depth in building placement and network management.

## 🔌 Core Concepts

### Power vs Energy
- **Power**: Real-time generation and consumption for building operation
- **Energy**: Stored currency spent on building actions (shooting, mining, etc.)
- **Power Generation**: Converts to energy over time when connected
- **Power Consumption**: Required for buildings to remain operational

### Network Connectivity
- **Power Nodes**: Buildings that can connect to other buildings
- **Connection Range**: 170 pixels maximum distance between buildings
- **Connection Limits**: Each building type has maximum connection capacity
- **Network Graphs**: Connected buildings form power blocks

## 🏗️ Building Connection Types

### Connection Capacities
```
Connector:         6 connections (hub)
Hangar:           2 connections (special)
All Others:       1 connection (endpoint)
```

### Power Generation Buildings
```
Solar Panel:      0.1 energy per level per frame
Power Plant:      0.2 energy per level per frame (if implemented)
```

### Power Storage Buildings
```
Battery:          120 energy storage per level
```

### Power Consumption Buildings
```
Miner:            6 energy per mining operation
Turret:           4 energy per shot + 3 minerals
Laser:            0.12 energy per level per frame (continuous)
Super Laser:      1.2 energy per level per frame (continuous)
Repair Node:      0.15 energy per frame when repairing
Hangar:           0.025 energy per frame maintenance
Missile Launcher: 8 energy per shot + 5 minerals
Force Field:      2.0 energy per frame (continuous)
```

## 🔗 Connection Algorithm

### Automatic Connection Process
1. **New Building Placement**: When a building is constructed
2. **Range Check**: Find all buildings within 170 pixels
3. **Priority Selection**: Prioritize connectors over other buildings
4. **Capacity Check**: Verify both buildings have available connections
5. **Connection Creation**: Establish bidirectional link
6. **Network Update**: Recalculate power distribution

### Connection Priority Order
1. **Connectors**: Always preferred for hub functionality
2. **Power Generators**: Solar panels, power plants
3. **Power Storage**: Batteries for load balancing
4. **Other Buildings**: Based on proximity

### Manual Connection Override
- Players cannot manually create/destroy connections
- All connections are automatic based on proximity and capacity
- Buildings auto-connect to nearest available power sources

## ⚡ Power Distribution Algorithm

### Network Analysis (BFS Traversal)
```python
def update_power_network():
    # 1. Clear all existing power blocks
    clear_power_blocks()
    
    # 2. Find all disconnected building groups
    unvisited = set(all_buildings)
    block_id = 0
    
    while unvisited:
        # Start BFS from unvisited building
        start_building = unvisited.pop()
        power_block = create_new_power_block(block_id)
        
        # Traverse connected buildings
        queue = [start_building]
        visited = {start_building}
        
        while queue:
            current = queue.pop(0)
            power_block.add_building(current)
            
            # Check all connections
            for connected_building in current.connections:
                if connected_building not in visited:
                    visited.add(connected_building)
                    queue.append(connected_building)
        
        # Remove visited buildings from unvisited set
        unvisited -= visited
        block_id += 1
```

### Power Block Properties
```python
class PowerBlock:
    def __init__(self):
        self.buildings = []
        self.total_generation = 0.0    # Energy per frame
        self.total_consumption = 0.0   # Energy per frame
        self.total_capacity = 0.0      # Maximum energy storage
        self.current_energy = 0.0      # Current stored energy
        self.is_powered = False        # Has active generation
```

### Power Calculation
```python
def calculate_power_block_stats(power_block):
    generation = 0.0
    consumption = 0.0
    capacity = 0.0
    
    for building in power_block.buildings:
        if building.type == "solar":
            generation += 0.1 * building.level
        elif building.type == "battery":
            capacity += 120 * building.level
        elif building.type == "laser" and building.powered:
            consumption += 0.12 * building.level
        # ... other building types
    
    power_block.total_generation = generation
    power_block.total_consumption = consumption
    power_block.total_capacity = capacity
    power_block.is_powered = (generation > 0)
```

## 🔋 Energy Management

### Energy Generation
- **Rate**: Power generation buildings add energy each frame
- **Formula**: `energy += generation_rate * building_level * delta_time`
- **Storage**: Limited by total battery capacity in power block
- **Overflow**: Excess generation is lost if storage is full

### Energy Consumption
- **Continuous**: Lasers, repair nodes, force fields consume per frame
- **Per-Action**: Turrets, miners consume per shot/operation
- **Priority**: Critical systems (defense) have consumption priority
- **Shortage**: Buildings shut down when insufficient energy

### Energy Distribution Rules
1. **Block Isolation**: Energy cannot transfer between power blocks
2. **Shared Pool**: All buildings in a block share the same energy pool
3. **Real-time Updates**: Energy levels update every frame
4. **Deficit Handling**: When energy is insufficient, buildings shut down

## 📡 Visual Representation

### Connection Lines
```
Powered Connections:    Bright cyan lines (0, 255, 255)
Unpowered Connections:  Gray lines (128, 128, 128)
Building-to-Node:       Dashed green lines (0, 255, 0)
```

### Building States
```
Powered Building:       Normal color
Unpowered Building:     Dimmed to 50% brightness
Under Construction:     Flashing or different color
Damaged:               Red tint overlay
```

### Energy Flow Animation
- **Flow Direction**: From generators toward consumers
- **Flow Speed**: Proportional to energy transfer rate
- **Flow Particles**: Small moving dots along connection lines
- **Flow Color**: Yellow/gold particles indicating energy

## 🚫 Network Failure Scenarios

### Power Block Isolation
- **Cause**: Connection destroyed by enemy fire or building destruction
- **Effect**: Network splits into multiple smaller blocks
- **Resolution**: Reconnect by building new connectors or repairing links

### Generator Destruction
- **Cause**: All solar panels in a block destroyed
- **Effect**: Block loses power generation capability
- **Impact**: All buildings in block become non-functional
- **Recovery**: Build new generators or connect to powered block

### Cascade Failures
- **Overload**: High energy consumption exceeds generation
- **Brownout**: Insufficient energy causes building shutdowns
- **Recovery**: Reduce consumption or increase generation

## 🔧 Strategic Implications

### Network Design Principles
1. **Redundancy**: Multiple paths between critical buildings
2. **Hub Strategy**: Use connectors to create efficient networks
3. **Defense Priority**: Protect generators and key connectors
4. **Expansion Planning**: Extend power before building new structures

### Tactical Considerations
- **Connector Placement**: Central hubs reduce total connection length
- **Generator Distribution**: Spread across map to avoid single points of failure
- **Battery Placement**: Strategic energy storage for high-consumption periods
- **Defense Coverage**: Ensure power network components are well-defended

### Enemy Targeting
- **Priority Targets**: Enemies may prioritize power infrastructure
- **Network Attacks**: Destroying key connectors can cripple large areas
- **Recovery Time**: Network repairs require time and resources

## 📊 Performance Metrics

### Network Efficiency
- **Connection Ratio**: Total connections / theoretical maximum
- **Coverage Percentage**: Powered buildings / total buildings
- **Energy Utilization**: Consumed energy / generated energy
- **Network Resilience**: Alternative paths between critical nodes

### Optimization Targets
- **Minimize Connection Length**: Reduce total cable distance
- **Maximize Redundancy**: Multiple paths to critical buildings
- **Balance Load**: Distribute consumption across generators
- **Future-Proof**: Plan for expansion and upgrades

---

*The Power Network System creates emergent strategic gameplay where network topology becomes as important as individual building placement, requiring players to think systematically about infrastructure design and defense.* 