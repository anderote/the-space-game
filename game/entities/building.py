"""
Building Entity System - Phase 3 Implementation
Core building classes that integrate with Panda3D visualization
"""

import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

class BuildingState(Enum):
    """Building operational states"""
    UNDER_CONSTRUCTION = "under_construction"
    OPERATIONAL = "operational"
    UNPOWERED = "unpowered"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"

class BuildingType(Enum):
    """Building type enumeration matching configuration"""
    STARTING_BASE = "starting_base"
    SOLAR = "solar"
    CONNECTOR = "connector"
    BATTERY = "battery"
    MINER = "miner"
    TURRET = "turret"
    LASER = "laser"
    SUPERLASER = "superlaser"
    REPAIR = "repair"
    HANGAR = "hangar"
    FORCE_FIELD = "force_field"
    MISSILE_LAUNCHER = "missile_launcher"
    CONVERTER = "converter"

class Building:
    """Base building entity that preserves original game logic"""
    
    def __init__(self, building_type: str, x: float, y: float, config: dict, building_id: str = None):
        # Core identity
        self.building_id = building_id or f"{building_type}_{int(time.time() * 1000)}"
        self.building_type = building_type
        self.x = x
        self.y = y
        
        # Configuration data
        self.config = config
        building_config = config.buildings.get("building_types", {}).get(building_type, {})
        
        # Basic properties from config
        self.max_health = building_config.get("base_health", building_config.get("health", 100))
        self.current_health = self.max_health
        self.radius = building_config.get("radius", 25)
        
        # Handle cost format (can be number or dict)
        cost_config = building_config.get("cost", 50)
        if isinstance(cost_config, dict):
            self.cost = cost_config
        else:
            # Simple number cost means minerals only
            self.cost = {"minerals": cost_config, "energy": 0}
        
        # Power and connection properties
        power_gen = building_config.get("power_generation", False)
        self.power_generation = building_config.get("base_power_generation", 5) if power_gen else 0
        self.power_consumption = building_config.get("power_consumption", 0)
        self.max_connections = building_config.get("max_connections", 0)
        self.connection_range = building_config.get("connection_range", 100)
        
        # Operational properties
        self.range = building_config.get("range", 0)  # For turrets, miners, etc.
        self.damage = building_config.get("damage", 0)
        self.fire_rate = building_config.get("fire_rate", 1.0)
        
        # Construction properties
        self.construction_time = building_config.get("construction_time", 3.0)
        self.construction_energy_cost = building_config.get("construction_energy_cost", 10)
        
        # Runtime state
        self.state = BuildingState.UNDER_CONSTRUCTION
        self.construction_start_time = time.time()
        self.construction_progress = 0.0
        self.last_fire_time = 0.0
        self.powered = False
        self.selected = False
        
        # Connections and networking
        self.connections = set()  # Set of connected building IDs
        self.power_block_id = None
        
        # Visual representation (Phase 2 integration)
        self.visual_node = None
        self.range_indicator = None
        
        # Building-specific data
        self.mining_targets = []  # For miners
        self.repair_targets = []  # For repair nodes
        self.target_enemy = None  # For turrets
        
    def update(self, dt: float):
        """Update building state and logic"""
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._update_construction(dt)
        elif self.state == BuildingState.OPERATIONAL:
            self._update_operational(dt)
            
    def _update_construction(self, dt: float):
        """Handle construction progress"""
        if self.state != BuildingState.UNDER_CONSTRUCTION:
            return
            
        # Update construction progress
        elapsed_time = time.time() - self.construction_start_time
        self.construction_progress = min(1.0, elapsed_time / self.construction_time)
        
        # Check if construction is complete
        if self.construction_progress >= 1.0:
            self.state = BuildingState.OPERATIONAL
            print(f"✓ {self.building_type.title()} construction complete at ({self.x:.0f}, {self.y:.0f})")
            
    def _update_operational(self, dt: float):
        """Update operational building logic"""
        # Building-specific operational updates will be implemented per type
        # This is where turret targeting, mining, repair, etc. logic goes
        pass
        
    def can_connect_to(self, other_building: 'Building') -> bool:
        """Check if this building can connect to another building"""
        if not other_building or other_building == self:
            return False
            
        # Check distance
        distance = ((self.x - other_building.x) ** 2 + (self.y - other_building.y) ** 2) ** 0.5
        if distance > self.connection_range:
            return False
            
        # Check connection capacity
        if len(self.connections) >= self.max_connections and self.max_connections > 0:
            return False
            
        # Check if already connected
        if other_building.building_id in self.connections:
            return False
            
        return True
        
    def connect_to(self, other_building: 'Building') -> bool:
        """Establish a connection to another building"""
        if not self.can_connect_to(other_building):
            return False
            
        # Add bidirectional connection
        self.connections.add(other_building.building_id)
        other_building.connections.add(self.building_id)
        
        print(f"✓ Connected {self.building_type} to {other_building.building_type}")
        return True
        
    def disconnect_from(self, other_building: 'Building'):
        """Remove connection to another building"""
        self.connections.discard(other_building.building_id)
        other_building.connections.discard(self.building_id)
        
    def set_powered(self, powered: bool):
        """Set building power state"""
        if self.powered != powered:
            self.powered = powered
            if powered:
                if self.state == BuildingState.UNPOWERED:
                    self.state = BuildingState.OPERATIONAL
            else:
                if self.state == BuildingState.OPERATIONAL:
                    self.state = BuildingState.UNPOWERED
                    
    def take_damage(self, amount: int):
        """Apply damage to building"""
        self.current_health = max(0, self.current_health - amount)
        
        if self.current_health <= 0:
            self.state = BuildingState.DESTROYED
            print(f"✗ {self.building_type.title()} destroyed at ({self.x:.0f}, {self.y:.0f})")
        elif self.current_health < self.max_health * 0.5:
            self.state = BuildingState.DAMAGED
            
    def repair(self, amount: int):
        """Repair building damage"""
        self.current_health = min(self.max_health, self.current_health + amount)
        
        if self.current_health > self.max_health * 0.5 and self.state == BuildingState.DAMAGED:
            self.state = BuildingState.OPERATIONAL if self.powered else BuildingState.UNPOWERED
            
    def get_info(self) -> Dict:
        """Get building information for UI display"""
        return {
            'id': self.building_id,
            'type': self.building_type,
            'position': (self.x, self.y),
            'health': (self.current_health, self.max_health),
            'state': self.state.value,
            'powered': self.powered,
            'construction_progress': self.construction_progress,
            'connections': len(self.connections),
            'max_connections': self.max_connections,
            'power_generation': self.power_generation,
            'power_consumption': self.power_consumption,
            'range': self.range
        }
        
    def can_place_at(self, x: float, y: float, existing_buildings: List['Building']) -> bool:
        """Check if building can be placed at given position"""
        # Check minimum distance from other buildings
        min_distance = self.radius + 10  # Small buffer
        
        for building in existing_buildings:
            distance = ((x - building.x) ** 2 + (y - building.y) ** 2) ** 0.5
            if distance < min_distance + building.radius:
                return False
                
        return True
        
    def is_in_range_of(self, target_x: float, target_y: float) -> bool:
        """Check if a position is within building's operational range"""
        if self.range <= 0:
            return False
            
        distance = ((self.x - target_x) ** 2 + (self.y - target_y) ** 2) ** 0.5
        return distance <= self.range
        
    def __str__(self):
        return f"{self.building_type}({self.building_id}) at ({self.x:.0f}, {self.y:.0f}) - {self.state.value}" 