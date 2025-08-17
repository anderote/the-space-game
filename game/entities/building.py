"""
Building Entity System - Phase 3 Implementation
Core building classes that integrate with Panda3D visualization
"""

import time
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

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
    NUCLEAR = "nuclear"
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
    
    def __init__(self, building_type: str, x: float, y: float, config: dict, building_id: str = None, completion_callback=None, game_engine=None):
        # Core identity
        self.building_id = building_id or f"{building_type}_{int(time.time() * 1000)}"
        self.building_type = building_type
        self.completion_callback = completion_callback
        self.game_engine = game_engine  # Reference to game engine for resource management
        self.x = x
        self.y = y
        
        # Configuration data
        self.config = config
        building_config = config.buildings.get("building_types", {}).get(building_type, {})
        
        # Building level and upgrade system (initialize early)
        self.level = 1
        self.max_level = 5
        self.disabled = False
        self.is_upgrading = False
        
        # Basic properties from config
        self.base_max_health = building_config.get("base_health", building_config.get("health", 100))
        self.current_health = self.max_health  # This will use the property
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
        if power_gen:
            # Use effective energy generation for power buildings
            if self.building_type in ["solar", "nuclear"]:
                self.power_generation = 0  # Will be set correctly after initialization
            else:
                self.power_generation = building_config.get("base_power_generation", 5)
        else:
            self.power_generation = 0
        self.power_consumption = building_config.get("power_consumption", 0)
        self.max_connections = building_config.get("max_connections", 0)
        self.connection_range = building_config.get("connection_range", 100)
        
        # Operational properties
        self.range = building_config.get("range", 0)  # For turrets, miners, etc.
        self.damage = building_config.get("damage", 0)
        self.fire_rate = building_config.get("fire_rate", 1.0)
        
        # Energy storage (for batteries and power buildings)
        self.energy_capacity = building_config.get("energy_capacity", 0)
        self.energy_storage = self.energy_capacity  # Initialize energy storage
        
        # Construction properties
        self.construction_time = building_config.get("construction_time", 3.0)
        self.construction_energy_cost = building_config.get("construction_energy_cost", 10)
        
        # Enhanced construction system
        # Calculate total energy needed: 100 minerals = 50 energy
        total_mineral_cost = self.cost.get("minerals", 0)
        self.total_construction_energy = (total_mineral_cost / 100.0) * 30.0
        self.construction_energy_consumed = 0.0
        self.max_build_rate = 7.5  # Maximum energy per second during construction
        self.construction_paused = False
        self.construction_start_time = time.time()
        self.last_construction_update = time.time()
        self.is_upgrading = False  # Track if this is an upgrade vs new construction
        
        # Runtime state
        self.state = BuildingState.UNDER_CONSTRUCTION if total_mineral_cost > 0 else BuildingState.OPERATIONAL
        self.construction_progress = 0.0 if total_mineral_cost > 0 else 1.0
        self.last_fire_time = 0.0
        self.disabled = False  # Buildings can be disabled by player
        # Note: powered is now a property, not an attribute
        self.selected = False
        
        # Connections and networking
        self.connections = set()  # Set of connected building IDs
        self.power_block_id = None
        
        # Visual representation (Phase 2 integration)
        self.visual_node = None
        self.range_indicator = None
        self.health_bar = None  # Visual health/construction progress bar
        
        # Building-specific data
        self.mining_targets = []  # For miners
        self.repair_targets = []  # For repair nodes
        self.target_enemy = None  # For turrets
        
        # Mining system (for miner buildings)
        self.is_mining = False
        self.mining_targets = []  # List of nearby asteroids
        self.last_mining_time = 0.0
        self.current_mining_target = None
        self.mining_laser_effect = None
        
        # Converter system (for converter buildings)
        self.last_conversion_time = 0.0

    @property
    def powered(self) -> bool:
        """Check if building is currently powered"""
        # Starting base is always powered
        if self.building_type == "starting_base":
            return True
            
        # Solar panels and batteries power themselves when operational
        if self.building_type in ["solar", "battery"] and self.state == BuildingState.OPERATIONAL:
            return True
            
        # Other buildings under construction are not considered powered for mining/operations
        if self.state != BuildingState.OPERATIONAL:
            return False
            
        # Other buildings need to be connected to power network
        return self._is_connected_to_powered_network()
        
    def update(self, dt: float):
        """Update building state and logic"""
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._update_construction(dt)
        elif self.state == BuildingState.OPERATIONAL and not self.disabled:
            # Update mining for miner buildings
            if self.building_type == "miner":
                self._update_mining(dt)
            # Update conversion for converter buildings  
            elif self.building_type == "converter" and self.powered:
                self._update_conversion(dt)
            # Update combat for turret buildings
            elif self.building_type in ["turret", "laser", "superlaser", "missile_launcher"] and self.powered:
                self._update_turret_combat(dt)
            # Update repair for repair buildings
            elif self.building_type == "repair" and self.powered:
                self._update_repair_logic(dt)
            
    def _update_construction(self, dt: float):
        """Handle energy-based construction progress"""
        if self.state != BuildingState.UNDER_CONSTRUCTION:
            return
        
        # Pause construction if building is disabled
        if self.disabled:
            if not self.construction_paused:
                self.construction_paused = True
                print(f"⏸️  Construction paused for {self.building_type} - building disabled")
            return
            
        # Pause construction if building has 0 health (needs repair)
        if self.current_health <= 0:
            if not self.construction_paused:
                self.construction_paused = True
                print(f"⏸️  Construction paused for {self.building_type} - needs repair (0 health)")
            return
            
        # Check if building is connected to a powered network
        # Buildings under construction should check if they're connected to ANY powered building
        is_connected_to_powered_network = self._is_connected_to_powered_network()
        
        # Pause construction if not connected to powered network
        if not is_connected_to_powered_network:
            if not self.construction_paused:
                self.construction_paused = True
                print(f"⏸️  Construction paused for {self.building_type} - no power connection")
            return
        else:
            if self.construction_paused and not self.disabled:
                self.construction_paused = False
                if self.is_upgrading:
                    print(f"▶️  Upgrade resumed for {self.building_type} - power restored")
                else:
                    print(f"▶️  Construction resumed for {self.building_type} - power restored")
        
        # Calculate energy consumption for this frame
        current_time = time.time()
        time_delta = current_time - self.last_construction_update
        
        # Only update every 0.1 seconds to prevent spam and excessive calculations
        if time_delta < 0.1:
            return
            
        self.last_construction_update = current_time
        
        # Consume energy at max build rate (25 energy per second)
        energy_to_consume = min(
            self.max_build_rate * time_delta,  # Rate-limited consumption
            self.total_construction_energy - self.construction_energy_consumed  # Remaining energy needed
        )
        
        if energy_to_consume > 0:
            # Actually deduct energy from power network
            if self.game_engine and self.game_engine.consume_energy(energy_to_consume):
                self.construction_energy_consumed += energy_to_consume
                
                # Update construction progress based on energy consumed
                if self.total_construction_energy > 0:
                    self.construction_progress = self.construction_energy_consumed / self.total_construction_energy
                else:
                    self.construction_progress = 1.0  # Free buildings complete instantly
                
                # Check if construction is complete
                if self.construction_progress >= 1.0:
                    self.state = BuildingState.OPERATIONAL
                    
                    # Update energy-related stats when becoming operational
                    if self.building_type in ["solar", "nuclear"]:
                        self.power_generation = self.get_effective_energy_generation()
                        self.energy_storage = self.get_effective_energy_capacity()
                    elif self.building_type == "battery":
                        self.energy_storage = self.get_effective_energy_capacity()
                    
                    if self.is_upgrading:
                        # Update energy-related stats after upgrade completion
                        if self.building_type in ["solar", "nuclear"]:
                            self.power_generation = self.get_effective_energy_generation()
                            self.energy_storage = self.get_effective_energy_capacity()
                        elif self.building_type == "battery":
                            self.energy_storage = self.get_effective_energy_capacity()
                        
                        print(f"✓ {self.building_type.title()} upgrade complete at ({self.x:.0f}, {self.y:.0f})")
                        print(f"  Now Level {self.level} - Total energy consumed: {self.construction_energy_consumed:.1f}")
                        if self.building_type == "solar":
                            print(f"  New energy generation: {self.power_generation:.2f}/sec")
                        self.is_upgrading = False
                    else:
                        print(f"✓ {self.building_type.title()} construction complete at ({self.x:.0f}, {self.y:.0f})")
                        print(f"  Total energy consumed: {self.construction_energy_consumed:.1f}")
                    
                    # Notify completion callback if provided
                    if self.completion_callback:
                        self.completion_callback(self.building_type)
            else:
                # Not enough energy available - pause construction (but limit message spam)
                current_time = time.time()
                if not self.construction_paused or (hasattr(self, 'last_energy_warning') and current_time - self.last_energy_warning > 2.0):
                    self.construction_paused = True
                    self.last_energy_warning = current_time
                    print(f"⚡ Construction paused for {self.building_type} - insufficient energy")
    
    def _is_connected_to_powered_network(self) -> bool:
        """Check if building is connected to a network that has at least one powered building"""
        # Starting base is always powered
        if self.building_type == "starting_base":
            return True
            
        # Solar panels and batteries power themselves
        if self.building_type in ["solar", "battery"]:
            return True
            
        # Check if any connected building is powered (for construction purposes)
        if not hasattr(self, 'game_engine') or not self.game_engine:
            return False
            
        building_system = getattr(self.game_engine, 'building_system', None)
        if not building_system:
            return False
            
        # Check all connected buildings to see if any are powered
        for building_id in self.connections:
            connected_building = building_system.buildings.get(building_id)
            if connected_building and connected_building.is_connected_to_power:
                return True
                
        return False
    
    def _is_connected_to_power(self) -> bool:
        """Check if building is connected to a powered network"""
        # Starting base is always powered (even during construction for initial setup)
        if self.building_type == "starting_base":
            return True
            
        # Solar panels and batteries power themselves when operational
        if self.building_type in ["solar", "battery"] and self.state == BuildingState.OPERATIONAL:
            return True
            
        # Other buildings under construction are not considered powered
        if self.state != BuildingState.OPERATIONAL:
            return False
            
        # Other buildings need connections to be powered
        return len(self.connections) > 0
    
    @property
    def is_connected_to_power(self) -> bool:
        """Property accessor for power connection status"""
        return self._is_connected_to_power()
        
    def should_show_health_bar(self) -> bool:
        """Determine if health bar should be visible"""
        # Never show health bars on asteroids
        if self.building_type == "asteroid":
            return False
        
        # Show during construction/upgrade
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            return True
        
        # Show when damaged (health < max), but hide when at full health
        if self.current_health < self.max_health:
            return True
            
        return False
    
    def get_health_progress(self) -> float:
        """Get health/construction progress as percentage (0.0 to 1.0)"""
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            return self.construction_progress
        else:
            return self.current_health / self.max_health if self.max_health > 0 else 1.0
    
    def is_construction_progress(self) -> bool:
        """Check if progress bar represents construction vs health"""
        return self.state == BuildingState.UNDER_CONSTRUCTION
        
    def _update_operational(self, dt: float):
        """Update operational building logic"""
        # Building-specific operational updates will be implemented per type
        # This is where turret targeting, mining, repair, etc. logic goes
        pass
        
    def can_connect_to(self, other_building: 'Building') -> bool:
        """Check if this building can connect to another building"""
        # Check basic connection requirements
        if self.building_id == other_building.building_id:
            return False  # Can't connect to self
            
        if other_building.building_id in self.connections:
            return False  # Already connected
            
        # Calculate distance
        distance = ((self.x - other_building.x) ** 2 + (self.y - other_building.y) ** 2) ** 0.5
        
        # Check if within connection range for both buildings
        if distance > self.get_effective_connection_range() or distance > other_building.get_effective_connection_range():
            return False  # Too far apart
        
        # Special connection limit logic for connectors
        if self.building_type == "connector":
            # Count connector-to-connector connections
            connector_connections = sum(1 for conn_id in self.connections 
                                      if self.game_engine and conn_id in self.game_engine.building_system.buildings 
                                      and self.game_engine.building_system.buildings[conn_id].building_type == "connector")
            
            # Count non-connector connections
            non_connector_connections = sum(1 for conn_id in self.connections 
                                          if self.game_engine and conn_id in self.game_engine.building_system.buildings 
                                          and self.game_engine.building_system.buildings[conn_id].building_type != "connector")
            
            # If connecting to another connector, check connector limit (max 3)
            if other_building.building_type == "connector":
                if connector_connections >= 3:
                    return False  # Already at max connector connections
            else:
                # If connecting to a non-connector, check non-connector limit (max 6)
                if non_connector_connections >= 6:
                    return False  # Already at max non-connector connections
            
            # Check total connection limit (max 9)
            if len(self.connections) >= 9:
                return False  # This building is at max total connections
        else:
            # Non-connector buildings use normal connection limits
            if len(self.connections) >= self.get_effective_max_connections():
                return False  # This building is at max connections
        
        # Check connection limits for the other building (same logic)
        if other_building.building_type == "connector":
            # Count connector-to-connector connections for other building
            other_connector_connections = sum(1 for conn_id in other_building.connections 
                                            if self.game_engine and conn_id in self.game_engine.building_system.buildings 
                                            and self.game_engine.building_system.buildings[conn_id].building_type == "connector")
            
            # Count non-connector connections for other building
            other_non_connector_connections = sum(1 for conn_id in other_building.connections 
                                                if self.game_engine and conn_id in self.game_engine.building_system.buildings 
                                                and self.game_engine.building_system.buildings[conn_id].building_type != "connector")
            
            # If this is a connector connecting to another connector, check connector limit
            if self.building_type == "connector":
                if other_connector_connections >= 3:
                    return False  # Other building already at max connector connections
            else:
                # If this is a non-connector connecting to a connector, check non-connector limit
                if other_non_connector_connections >= 6:
                    return False  # Other building already at max non-connector connections
            
            # Check total connection limit for other building (max 9)
            if len(other_building.connections) >= 9:
                return False  # Other building is at max total connections
        else:
            # Non-connector buildings use normal connection limits
            if len(other_building.connections) >= other_building.get_effective_max_connections():
                return False  # Other building is at max connections
            
        # Special connection rules for certain building types
        # Mining and defense buildings can only connect to one building
        single_connection_types = ['miner', 'turret', 'laser', 'superlaser', 'missile_launcher', 'repair', 'hangar']
        
        if self.building_type in single_connection_types and len(self.connections) >= 1:
            return False  # This building type can only have one connection
            
        if other_building.building_type in single_connection_types and len(other_building.connections) >= 1:
            return False  # Other building type can only have one connection
            
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
        
    def take_damage(self, amount: int):
        """Apply damage to building"""
        self.current_health = max(0, self.current_health - amount)
        
        if self.current_health <= 0:
            # Only destroy operational buildings, not those under construction
            if self.state == BuildingState.OPERATIONAL:
                self.state = BuildingState.DESTROYED
                
                if self.building_type == "asteroid":
                    print(f"⛏️ Asteroid fully mined at ({self.x:.0f}, {self.y:.0f})")
                else:
                    print(f"💥 {self.building_type.title()} destroyed at ({self.x:.0f}, {self.y:.0f})")
                
                # Remove destroyed building from game
                if hasattr(self, 'game_engine') and self.game_engine:
                    self.game_engine.remove_building(self)
            else:
                # Buildings under construction with 0 health just pause construction
                # but don't get destroyed (they can be repaired)
                if self.state == BuildingState.UNDER_CONSTRUCTION:
                    print(f"⚠️ {self.building_type.title()} under construction damaged to 0 health")
        elif self.current_health < self.max_health * 0.5:
            self.state = BuildingState.DAMAGED
            
    def repair(self, amount: int):
        """Repair building damage"""
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        
        # If building was at 0 health during construction and got repaired, resume construction
        if (old_health == 0 and self.current_health > 0 and 
            self.state == BuildingState.UNDER_CONSTRUCTION):
            print(f"🔧 {self.building_type.title()} construction can resume - health restored")
        
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

    @property
    def health(self):
        """Current health"""
        return self.current_health
        
    @property
    def max_health(self):
        """Get effective max health with level bonuses"""
        return self.get_effective_health()

    @max_health.setter
    def max_health(self, value):
        """Set max health and update current health if necessary"""
        self._max_health = value
        # Update effective max health based on level
        effective_max = self.get_effective_health()
        # If current health exceeds new max, adjust it
        if self.current_health > effective_max:
            self.current_health = effective_max

    @property
    def effective_range(self):
        """Attack/mining range with level bonuses"""
        base_range = self.range
        return base_range * (1 + (self.level - 1) * 0.25)  # 25% increase per level
        
    @property
    def effective_damage(self):
        """Damage with level bonuses"""
        base_damage = self.damage
        return base_damage * (1 + (self.level - 1) * 0.25)  # 25% increase per level
        
    def get_upgrade_cost(self):
        """Calculate upgrade cost for next level"""
        if self.level >= self.max_level:
            return None
        base_cost = self.cost.get("minerals", 50)
        mineral_cost = base_cost * self.level
        energy_cost = mineral_cost // 4
        return {"minerals": mineral_cost, "energy": energy_cost}
        
    def get_recycle_value(self) -> dict:
        """Calculate recycle value (50% of build cost)"""
        if isinstance(self.cost, dict):
            return {resource: amount // 2 for resource, amount in self.cost.items()}
        else:
            return {"minerals": self.cost // 2, "energy": 0}
    
    def can_be_recycled(self) -> bool:
        """Check if building can be recycled"""
        return self.state != BuildingState.DESTROYED
        
    def start_upgrade(self):
        """Start building upgrade process"""
        if self.level >= self.max_level or self.is_upgrading:
            return False
            
        upgrade_cost = self.get_upgrade_cost()
        if not upgrade_cost:
            return False
            
        # Check if we have resources (would be handled by building system)
        self.level += 1
        self.is_upgrading = True
        self.state = BuildingState.UNDER_CONSTRUCTION
        
        # Reset construction for upgrade
        self.total_construction_energy = upgrade_cost["energy"]
        self.construction_energy_consumed = 0.0
        self.construction_progress = 0.0
        self.construction_start_time = time.time()
        self.last_construction_update = time.time()
        
        # Update max health and heal to new max
        self.current_health = self.max_health
        
        return True
        
    def toggle_disable(self) -> bool:
        """Toggle building disabled state"""
        self.disabled = not self.disabled
        
        if self.disabled:
            print(f"🔇 Disabled {self.building_type} at ({self.x:.0f}, {self.y:.0f})")
            # Pause construction/upgrade if in progress
            if self.state == BuildingState.UNDER_CONSTRUCTION:
                self.construction_paused = True
        else:
            print(f"🔊 Enabled {self.building_type} at ({self.x:.0f}, {self.y:.0f})")
            # Resume construction/upgrade if was paused due to disable
            if self.state == BuildingState.UNDER_CONSTRUCTION and self.construction_paused:
                # Check if we still have power connection before resuming
                if self._is_connected_to_powered_network():
                    self.construction_paused = False
        
        return True

    def _find_nearest_asteroids(self, max_range: float, max_count: int = 5):
        """Find up to max_count nearest asteroids within range for mining"""
        if not self.game_engine or not hasattr(self.game_engine, 'building_system'):
            return []
        
        nearby_asteroids = []
        asteroids = self.game_engine.building_system.buildings_by_type.get("asteroid", [])
        
        for asteroid in asteroids:
            if asteroid.current_health <= 0:
                continue
                
            # Calculate distance
            distance = math.sqrt((asteroid.x - self.x)**2 + (asteroid.y - self.y)**2)
            
            if distance <= max_range:
                nearby_asteroids.append((distance, asteroid))
        
        # Sort by distance and return up to max_count closest asteroids
        nearby_asteroids.sort(key=lambda x: x[0])
        return [asteroid for _, asteroid in nearby_asteroids[:max_count]]

    def _update_mining(self, dt: float):
        """Update mining operations for miner buildings"""
        current_time = time.time()
        
        # Only mine if miner is powered
        if not self.powered:
            return
        
        # Get mining configuration with level bonuses
        mining_interval = 2.9  # Base interval + 0.5s delay
        mining_range = self.get_effective_range()
        
        # Check if it's time to mine
        if current_time - self.last_mining_time >= mining_interval:
            # Find nearby asteroids to mine
            if self.game_engine and hasattr(self.game_engine, 'building_system'):
                nearby_asteroids = self._find_nearest_asteroids(mining_range, max_count=5) # Mine up to 5
                
                if nearby_asteroids:
                    num_asteroids_mined = len(nearby_asteroids)
                    base_minerals_per_zap = self.get_effective_mining_rate()
                    
                    if num_asteroids_mined == 1:
                        minerals_per_zap = base_minerals_per_zap * 1.67  # Higher rate for single asteroid
                    else:
                        minerals_per_zap = base_minerals_per_zap  # Normal rate for multiple
                    
                    print(f"⛏️ Miner (Level {self.level}) mining {num_asteroids_mined} asteroids at {minerals_per_zap:.1f} minerals/zap each")
                    for asteroid_building in nearby_asteroids:
                        self._start_mining_asteroid(asteroid_building, minerals_per_zap)
                    self.last_mining_time = current_time
                else:
                    # Occasionally show debug for miners with no targets
                    if hasattr(self, '_last_no_target_message'):
                        if current_time - self._last_no_target_message > 10.0:  # Every 10 seconds
                            print(f"🔍 Miner at ({self.x:.0f}, {self.y:.0f}) - no asteroids in range {mining_range:.0f}")
                            self._last_no_target_message = current_time
                    else:
                        self._last_no_target_message = current_time

    def _start_mining_asteroid(self, asteroid_building, minerals_per_zap):
        """Initiate mining on a specific asteroid building."""
        if not asteroid_building or asteroid_building.current_health <= 0:
            return
        
        # Get effective energy cost based on level
        energy_cost_per_zap = self.get_effective_mining_energy_cost()
        
        # Check if we have enough energy for mining
        if self.game_engine.energy < energy_cost_per_zap:
            # Not enough energy to mine
            return
            
        # Consume energy for mining
        self.game_engine.energy -= energy_cost_per_zap
        
        # Calculate mining rate and mineral gain
        mining_rate = minerals_per_zap
        minerals_gained = mining_rate
        
        # Apply damage to asteroid (reduces its health)
        asteroid_building.take_damage(mining_rate)
        
        # Add minerals to player resources
        self.game_engine.minerals += minerals_gained
        print(f"⛏️ Miner extracted {minerals_gained:.1f} minerals from asteroid ({asteroid_building.current_health:.1f}/{asteroid_building.base_max_health} remaining) [Energy: -{energy_cost_per_zap:.1f}]")
        
        # Create visual effects
        if hasattr(self.game_engine, 'scene_manager') and hasattr(self.game_engine.scene_manager, 'entity_visualizer'):
            # Get asteroid radius for laser targeting
            asteroid_radius = getattr(asteroid_building, 'radius', 25)
            
            # Create mining laser effect
            self.game_engine.scene_manager.entity_visualizer.create_mining_laser_effect(
                self.x, self.y, asteroid_building.x, asteroid_building.y, asteroid_radius
            )
            
            # Create dust particle effect
            self.game_engine.scene_manager.entity_visualizer.create_mining_dust_effect(
                asteroid_building.x, asteroid_building.y
            )
    
    def _update_conversion(self, dt: float):
        """Update energy to mineral conversion for converter buildings"""
        current_time = time.time()
        
        # Get conversion configuration
        building_config = self.config.buildings.get("building_types", {}).get(self.building_type, {})
        conversion_interval = building_config.get("conversion_interval", 100) / 100.0  # Convert to seconds
        energy_cost = building_config.get("energy_rate", -2.0)  # Energy consumed per conversion
        mineral_gain = building_config.get("mineral_generation", 1.0)  # Minerals generated per conversion
        
        # Check if it's time to convert
        if current_time - self.last_conversion_time >= conversion_interval:
            # Check if we have enough energy
            if self.game_engine and self.game_engine.energy >= abs(energy_cost):
                # Consume energy and generate minerals
                self.game_engine.energy -= abs(energy_cost)
                self.game_engine.minerals += mineral_gain
                
                self.last_conversion_time = current_time
                
                print(f"🔄 Converter consumed {abs(energy_cost)} energy → generated {mineral_gain} minerals")
                
                # Create visual effect
                if hasattr(self.game_engine, 'scene_manager'):
                    self.game_engine.scene_manager.entity_visualizer.create_conversion_effect(
                        self.x, self.y
                    )
            else:
                # Not enough energy for conversion
                if current_time - self.last_conversion_time >= conversion_interval * 2:
                    print(f"⚠️  Converter needs {abs(energy_cost)} energy for conversion") 

    def get_effective_health(self):
        """Get health with level and research bonuses applied"""
        level_bonus = (self.level - 1) * 0.5  # 50% per level above 1
        research_bonus = 1.0
        if self.game_engine and hasattr(self.game_engine, 'research_system'):
            research_bonus = self.game_engine.research_system.get_bonus("building_health_multiplier")
        return self.base_max_health * (1.0 + level_bonus) * research_bonus
    
    def get_effective_range(self):
        """Get range with level and research bonuses applied"""
        if self.building_type in ["miner", "turret", "laser", "superlaser", "repair", "missile_launcher"]:
            # Turrets get 30% range bonus per level, others get 20%
            if self.building_type in ["turret", "laser", "superlaser", "missile_launcher"]:
                level_bonus = (self.level - 1) * 0.3  # 30% per level above 1 for turrets
            else:
                level_bonus = (self.level - 1) * 0.2  # 20% per level above 1 for others
            building_config = self.config.buildings.get("building_types", {}).get(self.building_type, {})
            
            # Get the appropriate range value for each building type
            if self.building_type == "miner":
                base_range = building_config.get("mining_range", 80)
            elif self.building_type in ["turret", "laser", "superlaser", "missile_launcher"]:
                # For combat buildings, use the "range" property from config (attack range)
                base_range = building_config.get("range", 100)
            elif self.building_type == "repair":
                base_range = building_config.get("healing_range", 60)
            else:
                base_range = self.range or 80  # Fallback to loaded range or default
            
            # Apply research bonuses
            research_bonus = 1.0
            if self.game_engine and hasattr(self.game_engine, 'research_system'):
                if self.building_type in ["turret", "laser", "superlaser", "missile_launcher"]:
                    research_bonus = self.game_engine.research_system.get_bonus("turret_range_multiplier")
                elif self.building_type == "miner":
                    research_bonus = self.game_engine.research_system.get_bonus("wconnection_range_multiplier")  # Could add mining_range_multiplier later
                else:
                    research_bonus = self.game_engine.research_system.get_bonus("connection_range_multiplier")
                
            return base_range * (1.0 + level_bonus) * research_bonus
        return 0
    
    def get_effective_damage(self):
        """Get damage with level and research bonuses applied"""
        if self.building_type in ["turret", "laser", "superlaser", "missile_launcher"]:
            level_bonus = (self.level - 1) * 0.3  # 30% per level above 1
            base_damage = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("damage", 10)
            
            # Apply research bonus
            research_bonus = 1.0
            if self.game_engine and hasattr(self.game_engine, 'research_system'):
                research_bonus = self.game_engine.research_system.get_bonus("turret_damage_multiplier")
                
            return base_damage * (1.0 + level_bonus) * research_bonus
        return 0
    
    def get_effective_mining_rate(self):
        """Get mining rate with level and research bonuses applied"""
        if self.building_type == "miner":
            level_bonus = (self.level - 1) * 0.2  # 20% per level above 1
            base_rate = 2.0  # Base mining rate
            
            # Apply research bonus
            research_bonus = 1.0
            if self.game_engine and hasattr(self.game_engine, 'research_system'):
                research_bonus = self.game_engine.research_system.get_bonus("mining_rate_multiplier")
                
            return base_rate * (1.0 + level_bonus) * research_bonus
        return 0
    
    def get_effective_energy_generation(self):
        """Get energy generation with level and research bonuses applied"""
        if self.building_type == "solar":
            level_bonus = (self.level - 1) * 0.5  # 50% per level above 1
            base_generation = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_rate", 0.1)
            
            # Apply research bonus
            research_bonus = 1.0
            if self.game_engine and hasattr(self.game_engine, 'research_system'):
                research_bonus = self.game_engine.research_system.get_bonus("solar_power_multiplier")
                
            return base_generation * (1.0 + level_bonus) * research_bonus
        elif self.building_type == "nuclear":
            level_bonus = (self.level - 1) * 0.5  # 50% per level above 1
            base_generation = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_rate", 25.0)
            
            # Apply research bonus
            research_bonus = 1.0
            if self.game_engine and hasattr(self.game_engine, 'research_system'):
                research_bonus = self.game_engine.research_system.get_bonus("nuclear_power_multiplier")
                
            return base_generation * (1.0 + level_bonus) * research_bonus
        return self.power_generation
    
    def get_effective_energy_capacity(self):
        """Get energy capacity with level bonuses applied"""
        if self.building_type == "battery":
            level_bonus = (self.level - 1) * 1.0  # 100% per level above 1
            base_capacity = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_storage", 150)
            return base_capacity * (1.0 + level_bonus)
        elif self.building_type == "solar":
            level_bonus = (self.level - 1) * 0.5  # 50% per level above 1 for solar panels too
            base_capacity = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_storage", 50)
            return base_capacity * (1.0 + level_bonus)
        return self.energy_storage
    
    def get_effective_mining_energy_cost(self):
        """Get mining energy cost per zap with level bonuses applied"""
        if self.building_type == "miner":
            level_bonus = (self.level - 1) * 0.2  # 20% per level above 1
            base_cost = 1.0  # Base energy cost per zap
            
            # Apply research bonuses
            research_multiplier = 1.0
            if self.game_engine and hasattr(self.game_engine, 'research_system'):
                research_multiplier = self.game_engine.research_system.get_bonus("mining_energy_multiplier")
            
            return base_cost * (1.0 + level_bonus) * research_multiplier
        return 1.0
        
    def get_effective_max_connections(self):
        """Get max connections with research bonuses applied"""
        base_connections = self.max_connections
        
        # Apply research bonuses
        general_bonus = 0
        building_specific_bonus = 0
        
        if self.game_engine and hasattr(self.game_engine, 'research_system'):
            # General max connections bonus (affects all buildings)
            general_bonus = self.game_engine.research_system.get_bonus("max_connections_bonus")
            
            # Special bonus for miners
            if self.building_type == "miner":
                building_specific_bonus = self.game_engine.research_system.get_bonus("miner_max_connections_bonus")
        
        return int(base_connections + general_bonus + building_specific_bonus)
        
    def get_effective_connection_range(self):
        """Get connection range with research bonuses applied"""
        base_range = self.connection_range
        
        # Apply research bonuses
        research_multiplier = 1.0
        if self.game_engine and hasattr(self.game_engine, 'research_system'):
            research_multiplier = self.game_engine.research_system.get_bonus("connection_range_multiplier")
        
        return base_range * research_multiplier 
    
    def _update_turret_combat(self, dt: float):
        """Update turret combat - search for enemies and fire"""
        import time
        
        if not hasattr(self, 'game_engine') or not self.game_engine:
            return
            
        current_time = time.time()
        
        # Check fire rate cooldown
        fire_rate = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("fire_rate", 2.0)
        # Laser turrets fire in bursts - much faster fire rate
        if self.building_type in ["laser", "superlaser"]:
            fire_rate *= 3.0  # 3x faster for continuous beam effect
        
        fire_cooldown = 1.0 / fire_rate  # Convert to seconds between shots
        
        if current_time - self.last_fire_time < fire_cooldown:
            return
            
        # Find nearest enemy in range
        turret_range = self.get_effective_range()
        nearest_enemy = None
        nearest_distance = turret_range + 1
        
        if hasattr(self.game_engine, 'enemies'):
            for enemy in self.game_engine.enemies:
                if not enemy.is_alive():
                    continue
                    
                distance = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2)**0.5
                if distance <= turret_range and distance < nearest_distance:
                    nearest_enemy = enemy
                    nearest_distance = distance
        
        # Fire at nearest enemy
        if nearest_enemy:
            self._fire_at_enemy(nearest_enemy)
            self.last_fire_time = current_time
    
    def _fire_at_enemy(self, enemy):
        """Fire weapon at target enemy"""
        try:
            # Check resource requirements before firing
            if not self._can_afford_to_fire():
                return
            
            # Get turret stats
            damage = self.get_effective_damage()
            
            if self.building_type == "missile_launcher":
                # Fire homing missile (consumes minerals)
                if self._consume_firing_resources():
                    self._fire_missile(enemy, damage)
            elif self.building_type == "turret":
                # Fire bullet projectile (no additional cost beyond energy)
                self._fire_bullet(enemy, damage)
            else:
                # Fire laser (instant hit) for laser and superlaser (consumes energy)
                if self._consume_firing_resources():
                    self._fire_laser(enemy, damage)
            
        except Exception as e:
            print(f"Error in turret fire: {e}")
            
    def _can_afford_to_fire(self):
        """Check if building can afford to fire its weapon"""
        try:
            if not self.game_engine or not hasattr(self.game_engine, 'building_system'):
                return True
                
            if self.building_type == "missile_launcher":
                # Missiles cost minerals per shot
                mineral_cost = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("mineral_cost", 0)
                return self.game_engine.building_system.minerals >= mineral_cost
            elif self.building_type in ["laser", "superlaser"]:
                # Lasers cost energy per shot  
                energy_cost = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_cost", 0)
                return self.game_engine.energy >= energy_cost
            else:
                # Regular turrets have no firing cost
                return True
                
        except Exception as e:
            print(f"Error checking firing affordability: {e}")
            return True
    
    def _consume_firing_resources(self):
        """Consume resources for firing and return success"""
        try:
            if not self.game_engine or not hasattr(self.game_engine, 'building_system'):
                return True
                
            if self.building_type == "missile_launcher":
                # Consume minerals for missile
                mineral_cost = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("mineral_cost", 0)
                if self.game_engine.building_system.minerals >= mineral_cost:
                    self.game_engine.building_system.minerals -= mineral_cost
                    return True
                return False
            elif self.building_type in ["laser", "superlaser"]:
                # Consume energy for laser
                energy_cost = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_cost", 0)
                if self.game_engine.energy >= energy_cost:
                    self.game_engine.energy -= energy_cost
                    return True
                return False
            else:
                # Regular turrets have no firing cost
                return True
                
        except Exception as e:
            print(f"Error consuming firing resources: {e}")
            return True
    
    def _fire_missile(self, target_enemy, damage):
        """Fire a homing missile at target"""
        try:
            from .projectile import Missile
            
            # Create missile
            missile = Missile(
                x=self.x,
                y=self.y,
                damage=damage,
                max_range=self.get_effective_range(),
                speed=150,  # Missile speed
                owner=self,
                game_engine=self.game_engine
            )
            
            # Add missile to game engine projectiles
            if hasattr(self.game_engine, 'projectiles'):
                self.game_engine.projectiles.append(missile)
            
            print(f"🚀 {self.building_type.title()} launched missile (damage: {damage:.1f})")
            
        except Exception as e:
            print(f"Error firing missile: {e}")
    
    def _fire_bullet(self, target_enemy, damage):
        """Fire a bullet projectile at target"""
        try:
            from .projectile import Projectile, ProjectileType
            
            # Create bullet projectile
            bullet = Projectile(
                projectile_type=ProjectileType.BULLET,
                x=self.x,
                y=self.y,
                target_x=target_enemy.x,
                target_y=target_enemy.y,
                speed=300,  # Fast bullet speed
                damage=damage,
                max_range=self.get_effective_range(),
                owner=self,
                game_engine=self.game_engine
            )
            
            # Add bullet to game engine projectiles
            if hasattr(self.game_engine, 'projectiles'):
                self.game_engine.projectiles.append(bullet)
            
            print(f"🔫 {self.building_type.title()} fired bullet (damage: {damage:.1f})")
            
        except Exception as e:
            print(f"Error firing bullet: {e}")
    
    def _fire_laser(self, target_enemy, damage):
        """Fire a laser beam at target (instant hit with continuous beam effect)"""
        try:
            # Instant damage to enemy
            target_enemy.take_damage(damage)
            
            # Create visual laser beam effect
            if hasattr(self, 'game_engine') and self.game_engine:
                scene_manager = getattr(self.game_engine, 'scene_manager', None)
                if scene_manager and hasattr(scene_manager, 'entity_visualizer'):
                    scene_manager.entity_visualizer.create_turret_attack_effect(
                        self.x, self.y, target_enemy.x, target_enemy.y, self.building_type
                    )
                    # Add laser impact particle effect at target location
                    scene_manager.entity_visualizer.create_laser_impact_effect(
                        target_enemy.x, target_enemy.y
                    )
            
            print(f"⚡ {self.building_type.title()} hit {target_enemy.enemy_type} for {damage:.1f} damage")
            
        except Exception as e:
            print(f"Error firing laser: {e}")
            
    def _update_repair_logic(self, dt: float):
        """Update repair building - heal nearby damaged buildings"""
        import time
        
        if not hasattr(self, 'game_engine') or not self.game_engine:
            return
            
        current_time = time.time()
        
        # Check repair cooldown (heal every 2 seconds)
        if not hasattr(self, 'last_repair_time'):
            self.last_repair_time = 0
        
        repair_cooldown = 2.0  # 2 seconds between repair cycles
        if current_time - self.last_repair_time < repair_cooldown:
            return
            
        # Check if we have energy to repair (with research bonuses)
        base_energy_cost = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("energy_cost", 0.15)
        
        # Apply research cost reduction
        cost_multiplier = 1.0
        if self.game_engine and hasattr(self.game_engine, 'research_system'):
            cost_multiplier = self.game_engine.research_system.get_bonus("repair_cost_multiplier")
        
        energy_cost = base_energy_cost * cost_multiplier
        if self.game_engine.energy < energy_cost:
            return
            
        # Find nearby damaged buildings
        repair_range = self.get_effective_range()
        damaged_buildings = []
        
        for building in self.game_engine.building_system.buildings.values():
            if building.building_id == self.building_id:
                continue  # Don't heal self
                
            # Only heal buildings that are damaged
            if building.current_health >= building.max_health:
                continue
                
            # Calculate distance
            distance = math.sqrt((building.x - self.x)**2 + (building.y - self.y)**2)
            if distance <= repair_range:
                damaged_buildings.append((distance, building))
        
        # Sort by distance and heal up to 3 closest buildings
        damaged_buildings.sort(key=lambda x: x[0])
        max_heal_targets = 3
        healed_count = 0
        
        for distance, building in damaged_buildings[:max_heal_targets]:
            # Consume energy per heal
            if self.game_engine.energy >= energy_cost:
                self.game_engine.energy -= energy_cost
                
                # Apply healing with research bonuses
                base_repair_rate = self.config.buildings.get("building_types", {}).get(self.building_type, {}).get("repair_rate", 0.15)
                
                # Apply research bonuses
                repair_multiplier = 1.0
                if self.game_engine and hasattr(self.game_engine, 'research_system'):
                    repair_multiplier = self.game_engine.research_system.get_bonus("repair_rate_multiplier")
                
                effective_repair_rate = base_repair_rate * repair_multiplier
                heal_amount = effective_repair_rate * building.max_health  # Heal as percentage of max health
                
                old_health = building.current_health
                building.repair(int(heal_amount))
                healed_amount = building.current_health - old_health
                
                if healed_amount > 0:
                    print(f"🩹 Repair Node healed {building.building_type} for {healed_amount:.1f} HP ({building.current_health:.1f}/{building.max_health})")
                    healed_count += 1
                    
                    # Create visual healing effect
                    if hasattr(self.game_engine, 'scene_manager'):
                        self.game_engine.scene_manager.entity_visualizer.create_healing_effect(building.x, building.y)
            else:
                break  # Not enough energy for more healing
        
        if healed_count > 0:
            self.last_repair_time = current_time

