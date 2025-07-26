"""
Arcade game logic system.
"""

import arcade
import random
import math
from typing import List, Tuple, Dict, Any, Set, Optional
from collections import defaultdict, deque

class SpatialGrid:
    """Spatial partitioning grid for efficient collision detection."""
    
    def __init__(self, world_width: int, world_height: int, cell_size: int = 200):
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = cell_size
        self.cols = world_width // cell_size + 1
        self.rows = world_height // cell_size + 1
        self.grid: Dict[Tuple[int, int], List] = defaultdict(list)
    
    def clear(self):
        """Clear all entities from the grid."""
        self.grid.clear()
    
    def add_entity(self, entity, entity_type: str):
        """Add an entity to the spatial grid."""
        cell_x = int(entity.x // self.cell_size)
        cell_y = int(entity.y // self.cell_size)
        cell_x = max(0, min(self.cols - 1, cell_x))
        cell_y = max(0, min(self.rows - 1, cell_y))
        self.grid[(cell_x, cell_y)].append((entity, entity_type))
    
    def get_nearby_entities(self, x: float, y: float, radius: float) -> List[Tuple]:
        """Get entities near a position within a radius."""
        entities = []
        cell_radius = int(radius // self.cell_size) + 1
        center_x = int(x // self.cell_size)
        center_y = int(y // self.cell_size)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell_x = center_x + dx
                cell_y = center_y + dy
                if 0 <= cell_x < self.cols and 0 <= cell_y < self.rows:
                    entities.extend(self.grid[(cell_x, cell_y)])
        
        return entities

class PowerNetwork:
    """Manages power network connections and blocks."""
    
    def __init__(self):
        self.blocks: List[Set] = []  # List of connected power blocks
        self.node_to_block: Dict = {}  # Maps node ID to block index
        self.block_stats: List[Dict] = []  # Power stats for each block
        
    def clear(self):
        """Clear all network data."""
        self.blocks.clear()
        self.node_to_block.clear()
        self.block_stats.clear()
    
    def add_node(self, node_id: int, x: float, y: float):
        """Add a power node to the network."""
        # Create new block for isolated node
        new_block = {node_id}
        self.blocks.append(new_block)
        self.node_to_block[node_id] = len(self.blocks) - 1
        self.block_stats.append({
            'power_generation': 0,
            'power_capacity': 0,
            'power_stored': 0,
            'power_consumption': 0
        })
    
    def connect_nodes(self, node1_id: int, node2_id: int):
        """Connect two nodes, merging their blocks if different."""
        if node1_id not in self.node_to_block or node2_id not in self.node_to_block:
            return False
        
        block1_idx = self.node_to_block[node1_id]
        block2_idx = self.node_to_block[node2_id]
        
        if block1_idx == block2_idx:
            return True  # Already connected
        
        # Merge blocks
        block1 = self.blocks[block1_idx]
        block2 = self.blocks[block2_idx]
        
        # Merge smaller block into larger
        if len(block1) < len(block2):
            block1, block2 = block2, block1
            block1_idx, block2_idx = block2_idx, block1_idx
        
        # Move all nodes from block2 to block1
        for node_id in block2:
            self.node_to_block[node_id] = block1_idx
        block1.update(block2)
        
        # Merge block stats
        stats1 = self.block_stats[block1_idx]
        stats2 = self.block_stats[block2_idx]
        stats1['power_generation'] += stats2['power_generation']
        stats1['power_capacity'] += stats2['power_capacity']
        stats1['power_stored'] += stats2['power_stored']
        
        # Remove empty block
        del self.blocks[block2_idx]
        del self.block_stats[block2_idx]
        
        # Update block indices for all nodes
        for node_id, block_idx in self.node_to_block.items():
            if block_idx > block2_idx:
                self.node_to_block[node_id] = block_idx - 1
        
        return True
    
    def remove_node(self, node_id: int):
        """Remove a node and potentially split its block."""
        if node_id not in self.node_to_block:
            return
        
        block_idx = self.node_to_block[node_id]
        block = self.blocks[block_idx]
        block.remove(node_id)
        del self.node_to_block[node_id]
        
        if not block:
            # Empty block, remove it
            del self.blocks[block_idx]
            del self.block_stats[block_idx]
            # Update indices
            for nid, bidx in self.node_to_block.items():
                if bidx > block_idx:
                    self.node_to_block[nid] = bidx - 1
    
    def get_block_for_node(self, node_id: int) -> Optional[int]:
        """Get block index for a node."""
        return self.node_to_block.get(node_id)
    
    def get_block_power(self, block_idx: int) -> Dict:
        """Get power stats for a block."""
        if 0 <= block_idx < len(self.block_stats):
            return self.block_stats[block_idx]
        return {'power_generation': 0, 'power_capacity': 0, 'power_stored': 0, 'power_consumption': 0}
    
    def update_block_stats(self, block_idx: int, generation: float, capacity: float, consumption: float):
        """Update power stats for a block."""
        if 0 <= block_idx < len(self.block_stats):
            stats = self.block_stats[block_idx]
            stats['power_generation'] = generation
            stats['power_capacity'] = capacity
            stats['power_consumption'] = consumption
    
    def consume_power(self, block_idx: int, amount: float) -> bool:
        """Try to consume power from a block. Returns True if successful."""
        if 0 <= block_idx < len(self.block_stats):
            stats = self.block_stats[block_idx]
            if stats['power_stored'] >= amount:
                stats['power_stored'] -= amount
                return True
        return False
    
    def update_power_generation(self, dt: float):
        """Update power generation for all blocks."""
        for stats in self.block_stats:
            generation_rate = stats['power_generation'] * dt
            stats['power_stored'] = min(stats['power_capacity'], 
                                      stats['power_stored'] + generation_rate)

class Projectile:
    """Projectile entity for combat system."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: float, speed: float = 400.0, owner_type: str = "player", projectile_type: str = "bullet"):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.owner_type = owner_type
        self.projectile_type = projectile_type
        self.size = 4 if projectile_type == "missile" else 3
        self.lifetime = 8.0 if projectile_type == "laser" else 5.0
        self.age = 0.0
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.vel_x = (dx / distance) * speed
            self.vel_y = (dy / distance) * speed
        else:
            self.vel_x = 0
            self.vel_y = 0
    
    def update(self, dt: float):
        """Update projectile position."""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.age += dt
    
    def is_expired(self) -> bool:
        """Check if projectile should be removed."""
        return self.age >= self.lifetime
    
    def get_collision_radius(self) -> float:
        """Get collision radius for projectile."""
        return self.size
    
    def draw(self, camera):
        """Draw projectile."""
        screen_x = (self.x - camera.x) * camera.zoom + camera.width // 2
        screen_y = (self.y - camera.y) * camera.zoom + camera.height // 2
        scaled_size = self.size * camera.zoom
        
        if 0 <= screen_x <= camera.width and 0 <= screen_y <= camera.height:
            if self.projectile_type == "missile":
                color = arcade.color.ORANGE if self.owner_type == "player" else arcade.color.RED_ORANGE
                # Draw missile with trail
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size, color)
                arcade.draw_circle_outline(screen_x, screen_y, scaled_size + 1, arcade.color.YELLOW, 1)
            elif self.projectile_type == "laser":
                color = arcade.color.LIME_GREEN if self.owner_type == "player" else arcade.color.RED
                # Draw laser beam
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size, color)
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size * 2, (*color[:3], 50))
            else:  # bullet
                color = arcade.color.CYAN if self.owner_type == "player" else arcade.color.RED
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size, color)

class Entity:
    """Base class for game entities."""
    def __init__(self, x: float, y: float, size: float, color: tuple):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.health = 100
        self.max_health = 100
        self.last_damage_time = 0
        self.invulnerable_duration = 0.5
    
    def take_damage(self, damage: float, current_time: float) -> bool:
        """Take damage if not invulnerable. Returns True if damage was taken."""
        if current_time - self.last_damage_time > self.invulnerable_duration:
            self.health -= damage
            self.last_damage_time = current_time
            return True
        return False
    
    def is_alive(self) -> bool:
        """Check if entity is alive."""
        return self.health > 0
    
    def get_collision_radius(self) -> float:
        """Get collision radius for this entity."""
        return self.size
    
    def collides_with(self, other, distance_threshold: float = None) -> bool:
        """Check collision with another entity."""
        if distance_threshold is None:
            distance_threshold = self.get_collision_radius() + other.get_collision_radius()
        
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < distance_threshold
    
    def draw(self, camera):
        """Draw the entity."""
        screen_x = (self.x - camera.x) * camera.zoom + camera.width // 2
        screen_y = (self.y - camera.y) * camera.zoom + camera.height // 2
        scaled_size = self.size * camera.zoom
        
        if 0 <= screen_x <= camera.width and 0 <= screen_y <= camera.height:
            # Flash red if recently damaged
            if hasattr(self, '_current_time') and self._current_time - self.last_damage_time < 0.2:
                flash_color = (255, 100, 100)
            else:
                flash_color = self.color
            
            arcade.draw_circle_filled(screen_x, screen_y, scaled_size, flash_color)
            # Health bar
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = scaled_size * 2
                bar_height = 4 * camera.zoom
                bar_left = screen_x - bar_width // 2
                bar_right = screen_x + bar_width // 2
                bar_top = screen_y + scaled_size + 10
                bar_bottom = bar_top - bar_height
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, (255, 0, 0))
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_left + bar_width * health_ratio, bar_bottom, bar_top, (0, 255, 0))

class Building(Entity):
    """Base building class with power network integration."""
    
    # Building type definitions with costs and stats
    BUILDING_TYPES = {
        "starting_base": {
            "size": 60, "color": arcade.color.BLUE, "health": 2000,
            "cost_minerals": 0, "cost_energy": 0, "construction_time": 0,
            "power_generation": 25, "power_capacity": 100, "power_consumption": 0,
            "is_power_node": True, "max_connections": 6
        },
        "power_node": {
            "size": 15, "color": arcade.color.ELECTRIC_BLUE, "health": 50,
            "cost_minerals": 20, "cost_energy": 10, "construction_time": 3.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "is_power_node": True, "max_connections": 6
        },
        "power_plant": {
            "size": 35, "color": arcade.color.YELLOW, "health": 150,
            "cost_minerals": 80, "cost_energy": 40, "construction_time": 8.0,
            "power_generation": 20, "power_capacity": 0, "power_consumption": 0,
            "is_power_node": True, "max_connections": 6
        },
        "battery": {
            "size": 25, "color": arcade.color.LIME_GREEN, "health": 100,
            "cost_minerals": 60, "cost_energy": 30, "construction_time": 6.0,
            "power_generation": 0, "power_capacity": 200, "power_consumption": 0,
            "is_power_node": True, "max_connections": 6
        },
        "missile_turret": {
            "size": 30, "color": arcade.color.RED, "health": 200,
            "cost_minerals": 100, "cost_energy": 50, "construction_time": 10.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "attack_range": 200, "attack_damage": 50, "attack_cooldown": 2.0,
            "energy_per_shot": 10, "projectile_type": "missile"
        },
        "laser_turret": {
            "size": 28, "color": arcade.color.GREEN, "health": 180,
            "cost_minerals": 120, "cost_energy": 60, "construction_time": 12.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "attack_range": 180, "attack_damage": 40, "attack_cooldown": 1.5,
            "energy_per_shot": 8, "projectile_type": "laser"
        },
        "repair_node": {
            "size": 25, "color": arcade.color.CYAN, "health": 120,
            "cost_minerals": 90, "cost_energy": 45, "construction_time": 9.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "repair_range": 100, "repair_rate": 20, "energy_per_repair": 5,
            "is_power_node": True, "max_connections": 6
        },
        "hangar_node": {
            "size": 40, "color": arcade.color.PURPLE, "health": 250,
            "cost_minerals": 150, "cost_energy": 75, "construction_time": 15.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "is_power_node": True, "max_connections": 6
        },
        "long_range_laser": {
            "size": 35, "color": arcade.color.LIME_GREEN, "health": 300,
            "cost_minerals": 200, "cost_energy": 100, "construction_time": 20.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "attack_range": 400, "attack_damage": 80, "attack_cooldown": 3.0,
            "energy_per_shot": 20, "projectile_type": "laser"
        },
        "long_range_missile": {
            "size": 38, "color": arcade.color.DARK_RED, "health": 320,
            "cost_minerals": 250, "cost_energy": 125, "construction_time": 25.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "attack_range": 450, "attack_damage": 100, "attack_cooldown": 4.0,
            "energy_per_shot": 25, "projectile_type": "missile"
        },
        "wall": {
            "size": 12, "color": arcade.color.GRAY, "health": 500,
            "cost_minerals": 15, "cost_energy": 5, "construction_time": 2.0,
            "power_generation": 0, "power_capacity": 0, "power_consumption": 0,
            "is_wall": True, "max_connections": 6
        }
    }
    
    def __init__(self, x: float, y: float, building_type: str, building_id: int):
        self.building_type = building_type
        self.building_id = building_id
        self.connections = set()  # Connected building IDs
        
        # Get building stats
        stats = self.BUILDING_TYPES.get(building_type, self.BUILDING_TYPES["power_node"])
        
        super().__init__(x, y, stats["size"], stats["color"])
        self.health = stats["health"]
        self.max_health = stats["health"]
        
        # Construction
        self.is_constructed = False
        self.construction_time = stats["construction_time"]
        self.construction_progress = 0.0
        self.cost_minerals = stats["cost_minerals"]
        self.cost_energy = stats["cost_energy"]
        
        # Power network
        self.is_power_node = stats.get("is_power_node", False)
        self.is_wall = stats.get("is_wall", False)
        self.max_connections = stats.get("max_connections", 0)
        self.power_generation = stats["power_generation"]
        self.power_capacity = stats["power_capacity"]
        self.power_consumption = stats["power_consumption"]
        
        # Combat
        self.attack_range = stats.get("attack_range", 0)
        self.attack_damage = stats.get("attack_damage", 0)
        self.attack_cooldown = stats.get("attack_cooldown", 1.0)
        self.energy_per_shot = stats.get("energy_per_shot", 0)
        self.projectile_type = stats.get("projectile_type", "bullet")
        self.last_attack_time = 0
        
        # Special abilities
        self.repair_range = stats.get("repair_range", 0)
        self.repair_rate = stats.get("repair_rate", 0)
        self.energy_per_repair = stats.get("energy_per_repair", 0)
        self.mining_range = stats.get("mining_range", 0)
        self.mining_rate = stats.get("mining_rate", 0)
        self.energy_per_mine = stats.get("energy_per_mine", 0)
        
        self.last_repair_time = 0
        self.last_mining_time = 0
        self.connected_to_power = False
        self.power_block_id = None
    
    def update_construction(self, dt: float) -> bool:
        """Update construction progress. Returns True when complete."""
        if not self.is_constructed:
            # Construction requires energy
            if self.cost_energy > 0 and self.connected_to_power:
                energy_rate = min(self.cost_energy / self.construction_time, self.power_network.get_block_power(self.power_block_id)['power_stored'] / dt)
                self.power_network.consume_power(self.power_block_id, energy_rate * dt)
                self.construction_progress += energy_rate * dt
                if self.construction_progress >= self.construction_time:
                    self.is_constructed = True
                    return True
            elif self.cost_energy == 0:
                self.construction_progress += dt
                if self.construction_progress >= self.construction_time:
                    self.is_constructed = True
                    return True
        return self.is_constructed
    
    def can_connect_to(self, other_building) -> bool:
        """Check if this building can connect to another."""
        if not self.is_constructed or not other_building.is_constructed:
            return False
        
        # Check connection limits
        if len(self.connections) >= self.max_connections:
            return False
        if len(other_building.connections) >= other_building.max_connections:
            return False
        
        # Check types can connect
        if self.is_wall and other_building.is_wall:
            return True  # Walls connect to walls
        if (self.is_power_node or self.building_type == "starting_base") and (other_building.is_power_node or other_building.building_type == "starting_base"):
            return True  # Power nodes connect to power nodes
        
        return False
    
    def connect_to(self, other_building):
        """Connect to another building."""
        if self.can_connect_to(other_building):
            self.connections.add(other_building.building_id)
            other_building.connections.add(self.building_id)
            return True
        return False
    
    def disconnect_from(self, other_building):
        """Disconnect from another building."""
        self.connections.discard(other_building.building_id)
        other_building.connections.discard(self.building_id)
    
    def can_attack(self, current_time: float) -> bool:
        """Check if building can attack."""
        return (self.is_constructed and 
                self.connected_to_power and
                self.attack_range > 0 and 
                current_time - self.last_attack_time >= self.attack_cooldown)
    
    def can_repair(self, current_time: float) -> bool:
        """Check if building can repair."""
        return (self.is_constructed and 
                self.connected_to_power and
                self.repair_range > 0 and 
                current_time - self.last_repair_time >= 1.0)
    
    def attack(self, target_x: float, target_y: float, current_time: float, network: PowerNetwork) -> Optional[Projectile]:
        """Create an attack projectile if energy available."""
        if self.can_attack(current_time) and self.power_block_id is not None:
            if network.consume_power(self.power_block_id, self.energy_per_shot):
                self.last_attack_time = current_time
                return Projectile(self.x, self.y, target_x, target_y, self.attack_damage, 
                               projectile_type=self.projectile_type, owner_type="player")
        return None
    
    def repair_nearby(self, buildings: List, current_time: float, network: PowerNetwork) -> int:
        """Repair nearby damaged buildings. Returns amount repaired."""
        if not self.can_repair(current_time) or self.power_block_id is None:
            return 0
        
        repairs_made = 0
        for building in buildings:
            if (building != self and building.is_alive() and building.is_constructed and
                building.health < building.max_health):
                
                dx = building.x - self.x
                dy = building.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= self.repair_range:
                    if network.consume_power(self.power_block_id, self.energy_per_repair):
                        repair_amount = min(self.repair_rate, building.max_health - building.health)
                        building.health += repair_amount
                        repairs_made += repair_amount
                        self.last_repair_time = current_time
                        break  # One repair per update
        
        return repairs_made
    
    def get_collision_radius(self) -> float:
        """Buildings have larger collision radius."""
        return self.size * 1.2
    
    def draw(self, camera):
        """Draw building with construction progress and connections."""
        screen_x = (self.x - camera.x) * camera.zoom + camera.width // 2
        screen_y = (self.y - camera.y) * camera.zoom + camera.height // 2
        scaled_size = self.size * camera.zoom
        
        if 0 <= screen_x <= camera.width and 0 <= screen_y <= camera.height:
            # Flash red if recently damaged
            if hasattr(self, '_current_time') and self._current_time - self.last_damage_time < 0.2:
                building_color = (255, 100, 100)
            else:
                # Dim if not connected to power (except walls and starting base)
                if (not self.connected_to_power and 
                    self.building_type not in ["wall", "starting_base"] and 
                    self.is_constructed):
                    building_color = tuple(c // 2 for c in self.color[:3])
                else:
                    building_color = self.color
            
            # Draw building based on type
            if self.building_type == "starting_base":
                # Draw starting base as a large hexagon
                points = []
                for i in range(6):
                    angle = i * 60 * math.pi / 180
                    px = screen_x + scaled_size * math.cos(angle)
                    py = screen_y + scaled_size * math.sin(angle)
                    points.append((px, py))
                
                arcade.draw_polygon_filled(points, building_color)
                arcade.draw_polygon_outline(points, arcade.color.WHITE, 3)
                # Central core
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size * 0.3, arcade.color.CYAN)
                
            elif self.is_power_node:
                # Draw power nodes as circles with connection points
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size, building_color)
                arcade.draw_circle_outline(screen_x, screen_y, scaled_size, arcade.color.WHITE, 2)
                # Connection points
                for i in range(6):
                    angle = i * 60 * math.pi / 180
                    px = screen_x + (scaled_size + 3) * math.cos(angle)
                    py = screen_y + (scaled_size + 3) * math.sin(angle)
                    arcade.draw_circle_filled(px, py, 2, arcade.color.WHITE)
                    
            elif self.building_type in ["missile_turret", "laser_turret", "long_range_laser", "long_range_missile"]:
                # Draw turrets as squares with barrels
                left = screen_x - scaled_size
                right = screen_x + scaled_size
                top = screen_y + scaled_size
                bottom = screen_y - scaled_size
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, building_color)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)
                # Barrel
                barrel_length = scaled_size * 0.8
                arcade.draw_line(screen_x, screen_y, screen_x + barrel_length, screen_y, arcade.color.DARK_GRAY, 4)
                
            elif self.building_type == "wall":
                # Draw walls as small rectangles
                left = screen_x - scaled_size
                right = screen_x + scaled_size
                top = screen_y + scaled_size
                bottom = screen_y - scaled_size
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, building_color)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.BLACK, 1)
                
            else:
                # Draw other buildings as rectangles
                left = screen_x - scaled_size
                right = screen_x + scaled_size
                top = screen_y + scaled_size
                bottom = screen_y - scaled_size
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, building_color)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)
            
            # Construction progress bar
            if not self.is_constructed:
                progress = self.construction_progress / self.construction_time
                bar_width = scaled_size * 2
                bar_height = 6 * camera.zoom
                bar_left = screen_x - bar_width // 2
                bar_right = screen_x + bar_width // 2
                bar_top = screen_y - scaled_size - 15
                bar_bottom = bar_top - bar_height
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, (100, 100, 100))
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_left + bar_width * progress, bar_bottom, bar_top, (0, 255, 0))
            
            # Range indicators for special buildings
            if self.is_constructed and self.attack_range > 0 and self.connected_to_power:
                range_radius = self.attack_range * camera.zoom
                color = (0, 255, 0, 30) if self.projectile_type == "laser" else (255, 165, 0, 30)
                arcade.draw_circle_outline(screen_x, screen_y, range_radius, color, 1)
            elif self.is_constructed and self.repair_range > 0 and self.connected_to_power:
                range_radius = self.repair_range * camera.zoom
                arcade.draw_circle_outline(screen_x, screen_y, range_radius, (0, 255, 255, 30), 1)
            
            # Health bar
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = scaled_size * 2
                bar_height = 4 * camera.zoom
                bar_left = screen_x - bar_width // 2
                bar_right = screen_x + bar_width // 2
                bar_top = screen_y + scaled_size + 15
                bar_bottom = bar_top - bar_height
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, (255, 0, 0))
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_left + bar_width * health_ratio, bar_bottom, bar_top, (0, 255, 0))

class Enemy(Entity):
    """Enemy entity."""
    def __init__(self, x: float, y: float, enemy_type: str = "basic"):
        self.enemy_type = enemy_type
        if enemy_type == "fast":
            super().__init__(x, y, 15, arcade.color.RED)
            self.speed = 150
            self.attack_damage = 15
            self.attack_range = 80
            self.health = 50
            self.max_health = 50
        elif enemy_type == "tank":
            super().__init__(x, y, 30, arcade.color.DARK_RED)
            self.speed = 80
            self.attack_damage = 40
            self.attack_range = 100
            self.health = 200
            self.max_health = 200
        else:  # basic
            super().__init__(x, y, 20, arcade.color.RED)
            self.speed = 100
            self.attack_damage = 20
            self.attack_range = 90
        
        self.last_attack_time = 0
        self.attack_cooldown = 2.0
        self.target = None
        self.state = "moving"
    
    def can_attack(self, current_time: float) -> bool:
        """Check if enemy can attack."""
        return current_time - self.last_attack_time >= self.attack_cooldown
    
    def attack(self, target_x: float, target_y: float, current_time: float) -> Optional[Projectile]:
        """Create an attack projectile."""
        if self.can_attack(current_time):
            self.last_attack_time = current_time
            return Projectile(self.x, self.y, target_x, target_y, self.attack_damage, owner_type="enemy")
        return None
    
    def update_ai(self, starting_base, buildings, dt: float):
        """Update enemy AI behavior - target starting base or buildings."""
        if not self.is_alive():
            self.state = "dead"
            return
        
        # Find nearest target (prioritize starting base)
        targets = [starting_base] if starting_base else []
        targets.extend([b for b in buildings if b.is_alive() and b.is_constructed])
        if not targets:
            return
        
        nearest_target = min(targets, key=lambda t: math.sqrt((t.x - self.x)**2 + (t.y - self.y)**2))
        self.target = nearest_target
        
        # Calculate distance to target
        dx = nearest_target.x - self.x
        dy = nearest_target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.attack_range:
            self.state = "attacking"
        elif distance > 0:
            self.state = "moving"
            # Move towards target
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt

class Asteroid(Entity):
    """Asteroid entity with 8-sided polygon shape."""
    def __init__(self, x: float, y: float, size: float = None):
        if size is None:
            size = random.randint(15, 40)
        super().__init__(x, y, size, arcade.color.GRAY)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.mineral_value = int(size * 2)
        self.health = size * 3
        self.max_health = self.health
        
        # Generate 8-sided polygon vertices for more realistic asteroid shape
        self.vertices = []
        for i in range(8):
            angle = i * 45  # 8 sides = 45 degree increments
            # Add some randomness to make it look more natural
            radius_variation = random.uniform(0.7, 1.3)
            vertex_radius = self.size * radius_variation
            self.vertices.append((angle, vertex_radius))
    
    def get_collision_radius(self) -> float:
        """Asteroids have collision radius based on their size."""
        return self.size * 0.8
    
    def draw(self, camera):
        """Draw asteroid as an 8-sided polygon with rotation."""
        screen_x = (self.x - camera.x) * camera.zoom + camera.width // 2
        screen_y = (self.y - camera.y) * camera.zoom + camera.height // 2
        scaled_size = self.size * camera.zoom
        
        if 0 <= screen_x <= camera.width and 0 <= screen_y <= camera.height:
            # Flash red if recently damaged
            if hasattr(self, '_current_time') and self._current_time - self.last_damage_time < 0.2:
                asteroid_color = (255, 150, 150)
                outline_color = (255, 100, 100)
            else:
                asteroid_color = self.color
                outline_color = arcade.color.DARK_GRAY
            
            # Create 8-sided polygon with rotation and size scaling
            points = []
            for angle_offset, vertex_radius in self.vertices:
                # Apply rotation and screen scaling
                angle_rad = (angle_offset + self.rotation) * math.pi / 180
                scaled_radius = vertex_radius * camera.zoom
                px = screen_x + scaled_radius * math.cos(angle_rad)
                py = screen_y + scaled_radius * math.sin(angle_rad)
                points.append((px, py))
            
            # Draw filled polygon
            arcade.draw_polygon_filled(points, asteroid_color)
            
            # Draw outline for better definition
            arcade.draw_polygon_outline(points, outline_color, 2)
            
            # Add some surface detail for larger asteroids
            if scaled_size > 30:
                # Draw a few small details on the surface
                for i in range(3):
                    detail_angle = (self.rotation + i * 120) * math.pi / 180
                    detail_radius = scaled_size * 0.3
                    detail_x = screen_x + detail_radius * math.cos(detail_angle)
                    detail_y = screen_y + detail_radius * math.sin(detail_angle)
                    arcade.draw_circle_filled(detail_x, detail_y, 2, outline_color)
            
            # Health bar for damaged asteroids
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = scaled_size * 1.8
                bar_height = 4 * camera.zoom
                bar_left = screen_x - bar_width // 2
                bar_right = screen_x + bar_width // 2
                bar_top = screen_y + scaled_size + 12
                bar_bottom = bar_top - bar_height
                
                # Background
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, (50, 50, 50))
                # Health fill
                arcade.draw_lrbt_rectangle_filled(bar_left, bar_left + bar_width * health_ratio, bar_bottom, bar_top, (150, 150, 150))
                # Border
                arcade.draw_lrbt_rectangle_outline(bar_left, bar_right, bar_bottom, bar_top, arcade.color.WHITE, 1)

class ArcadeGameLogic:
    """Game logic system for base defense RTS with power networks."""
    
    def __init__(self, camera):
        self.camera = camera
        self.starting_base = None
        self.buildings = []
        self.enemies = []
        self.asteroids = []
        self.projectiles = []
        self.next_building_id = 1
        
        # Power network system
        self.power_network = PowerNetwork()
        
        # Resources
        self.minerals = 150  # Starting minerals
        self.energy = 100    # Starting energy
        
        # Game state
        self.score = 0
        self.game_time = 0
        self.wave = 1
        self.enemies_per_wave = 3
        self.wave_complete = False
        self.wave_delay = 15.0
        self.next_wave_time = 0
        
        # Construction
        self.selected_building_type = None
        self.construction_mode = False
        
        # Spatial partitioning
        self.spatial_grid = SpatialGrid(4800, 2700, 200)
        
    def setup(self):
        """Initialize game logic."""
        # Create starting base at world center
        center_x, center_y = 2400, 1350  # Exact world center
        self.starting_base = Building(center_x, center_y, "starting_base", 0)
        self.starting_base.is_constructed = True
        self.power_network.add_node(0, center_x, center_y)
        
        # Create some initial structures around the starting base
        initial_buildings = [
            Building(center_x - 100, center_y, "power_plant", 1),
            Building(center_x + 100, center_y, "battery", 2),
            Building(center_x - 50, center_y - 50, "power_node", 3),
            Building(center_x + 50, center_y - 50, "missile_turret", 4)
        ]
        
        for building in initial_buildings:
            building.is_constructed = True
            self.buildings.append(building)
            if building.is_power_node:
                self.power_network.add_node(building.building_id, building.x, building.y)
        
        self.next_building_id = 5
        
        # Connect initial power network
        self._auto_connect_nearby_nodes()
        self._update_power_network()
        
        # Create clustered asteroids around the map
        self._spawn_asteroid_clusters()
        
        # Schedule first wave
        self.next_wave_time = self.game_time + 20.0
        
        print("Advanced base defense with power networks setup complete")
    
    def _auto_connect_nearby_nodes(self):
        """Automatically connect nearby power nodes."""
        connection_range = 120  # Maximum connection distance
        
        all_nodes = [self.starting_base] + [b for b in self.buildings if b.is_power_node and b.is_constructed]
        
        for i, node1 in enumerate(all_nodes):
            for node2 in all_nodes[i+1:]:
                dx = node1.x - node2.x
                dy = node1.y - node2.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= connection_range and node1.can_connect_to(node2):
                    node1.connect_to(node2)
                    # Update power network
                    if hasattr(node1, 'building_id') and hasattr(node2, 'building_id'):
                        self.power_network.connect_nodes(node1.building_id, node2.building_id)
                    elif hasattr(node1, 'building_id'):
                        self.power_network.connect_nodes(node1.building_id, 0)
                    elif hasattr(node2, 'building_id'):
                        self.power_network.connect_nodes(0, node2.building_id)
    
    def _update_power_network(self):
        """Update power network blocks and connectivity."""
        # Clear and rebuild power network
        self.power_network.clear()
        
        # Add all power nodes
        if self.starting_base and self.starting_base.is_alive():
            self.power_network.add_node(0, self.starting_base.x, self.starting_base.y)
        
        for building in self.buildings:
            if building.is_alive() and building.is_constructed and building.is_power_node:
                self.power_network.add_node(building.building_id, building.x, building.y)
        
        # Rebuild connections
        all_nodes = [self.starting_base] + [b for b in self.buildings if b.is_power_node and b.is_constructed and b.is_alive()]
        
        for node in all_nodes:
            for connected_id in node.connections:
                if connected_id == 0:
                    continue
                connected_node = next((b for b in self.buildings if b.building_id == connected_id and b.is_alive()), None)
                if connected_node:
                    if hasattr(node, 'building_id'):
                        self.power_network.connect_nodes(node.building_id, connected_id)
                    else:
                        self.power_network.connect_nodes(0, connected_id)
        
        # Update block stats and connectivity
        for block_idx in range(len(self.power_network.blocks)):
            generation = 0
            capacity = 0
            consumption = 0
            
            for node_id in self.power_network.blocks[block_idx]:
                if node_id == 0:  # Starting base
                    generation += self.starting_base.power_generation
                    capacity += self.starting_base.power_capacity
                    consumption += self.starting_base.power_consumption
                else:
                    building = next((b for b in self.buildings if b.building_id == node_id), None)
                    if building and building.is_alive() and building.is_constructed:
                        generation += building.power_generation
                        capacity += building.power_capacity
                        consumption += building.power_consumption
            
            self.power_network.update_block_stats(block_idx, generation, capacity, consumption)
        
        # Update building connectivity status
        for building in self.buildings:
            if building.is_alive() and building.is_constructed:
                if building.is_power_node:
                    building.power_block_id = self.power_network.get_block_for_node(building.building_id)
                    building.connected_to_power = building.power_block_id is not None
                else:
                    # Non-power buildings need to be connected to a power node
                    building.connected_to_power = False
                    building.power_block_id = None
                    
                    # Check if any nearby power node is connected
                    for power_building in [self.starting_base] + [b for b in self.buildings if b.is_power_node and b.is_alive() and b.is_constructed]:
                        dx = building.x - power_building.x
                        dy = building.y - power_building.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        if distance <= 80:  # Connection range for non-power buildings
                            if hasattr(power_building, 'building_id'):
                                building.power_block_id = self.power_network.get_block_for_node(power_building.building_id)
                            else:
                                building.power_block_id = self.power_network.get_block_for_node(0)
                            building.connected_to_power = building.power_block_id is not None
                            break
        
        # Update starting base
        if self.starting_base and self.starting_base.is_alive():
            self.starting_base.power_block_id = self.power_network.get_block_for_node(0)
            self.starting_base.connected_to_power = self.starting_base.power_block_id is not None
    
    def _is_safe_spawn_location(self, x: float, y: float, min_distance: float = 150) -> bool:
        """Check if a location is safe for spawning."""
        # Check distance to starting base
        if self.starting_base:
            dx = x - self.starting_base.x
            dy = y - self.starting_base.y
            if math.sqrt(dx*dx + dy*dy) < min_distance:
                return False
        
        # Check distance to buildings
        for building in self.buildings:
            dx = x - building.x
            dy = y - building.y
            if math.sqrt(dx*dx + dy*dy) < min_distance:
                return False
        
        return True
    
    def _spawn_wave(self):
        """Spawn a wave of enemies."""
        enemies_to_spawn = self.enemies_per_wave + (self.wave - 1) * 2
        
        for _ in range(enemies_to_spawn):
            # Spawn enemies at the edges of the world
            if random.choice([True, False]):
                x = random.choice([100, 4700])
                y = random.randint(100, 2600)
            else:
                x = random.randint(100, 4700)
                y = random.choice([100, 2600])
            
            # Choose enemy type based on wave
            if self.wave >= 4:
                enemy_type = random.choice(["basic", "fast", "tank", "tank"])
            elif self.wave >= 3:
                enemy_type = random.choice(["basic", "fast", "tank"])
            elif self.wave >= 2:
                enemy_type = random.choice(["basic", "fast"])
            else:
                enemy_type = "basic"
            
            enemy = Enemy(x, y, enemy_type)
            self.enemies.append(enemy)
        
        self.wave_complete = False
        print(f"Wave {self.wave} spawned with {enemies_to_spawn} enemies!")
    
    def _spawn_asteroid_clusters(self):
        """Spawn asteroids in clusters around the map as 8-sided polygons."""
        cluster_centers = [
            (1000, 800), (3800, 800),    # Bottom clusters
            (800, 1350), (4000, 1350),   # Side clusters  
            (1200, 1900), (3600, 1900),  # Top clusters
            (2400, 500), (2400, 2200),   # Vertical clusters
            (1800, 1100), (3000, 1600)   # Diagonal clusters
        ]
        
        for center_x, center_y in cluster_centers:
            # Create 8-12 asteroids per cluster
            cluster_size = random.randint(8, 12)
            cluster_radius = random.randint(150, 250)
            
            for _ in range(cluster_size):
                # Random position within cluster radius
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(30, cluster_radius)
                
                asteroid_x = center_x + distance * math.cos(angle)
                asteroid_y = center_y + distance * math.sin(angle)
                
                # Ensure asteroid stays within world bounds
                asteroid_x = max(100, min(4700, asteroid_x))
                asteroid_y = max(100, min(2600, asteroid_y))
                
                # Avoid spawning too close to starting base
                dx = asteroid_x - 2400
                dy = asteroid_y - 1350
                if math.sqrt(dx*dx + dy*dy) > 300:  # Minimum distance from base
                    asteroid_size = random.randint(20, 50)
                    self.asteroids.append(Asteroid(asteroid_x, asteroid_y, asteroid_size))
        
        print(f"Spawned {len(self.asteroids)} asteroids in {len(cluster_centers)} clusters")
    
    def update(self, dt: float):
        """Update game logic."""
        self.game_time += dt
        
        # Update current time for damage flashing
        entities = [self.starting_base] + self.buildings + self.enemies + self.asteroids
        for entity in entities:
            if entity:
                entity._current_time = self.game_time
        
        # Update power network
        self._update_power_network()
        self.power_network.update_power_generation(dt)
        
        # Update spatial grid
        self._update_spatial_grid()
        
        # Update building construction
        self._update_construction(dt)
        
        # Update building operations
        self._update_building_operations()
        
        # Update enemies
        self._update_enemies(dt)
        
        # Update projectiles
        self._update_projectiles(dt)
        
        # Update asteroids
        self._update_asteroids(dt)
        
        # Handle collisions
        self._handle_collisions()
        
        # Check wave timing
        self._check_wave_timing()
        
        # Remove dead entities
        self._cleanup_dead_entities()
    
    def _update_spatial_grid(self):
        """Update the spatial partitioning grid."""
        self.spatial_grid.clear()
        
        # Add all entities to spatial grid
        if self.starting_base and self.starting_base.is_alive():
            self.spatial_grid.add_entity(self.starting_base, "starting_base")
        
        for building in self.buildings:
            if building.is_alive():
                self.spatial_grid.add_entity(building, "building")
        
        for enemy in self.enemies:
            if enemy.is_alive():
                self.spatial_grid.add_entity(enemy, "enemy")
        
        for asteroid in self.asteroids:
            if asteroid.is_alive():
                self.spatial_grid.add_entity(asteroid, "asteroid")
        
        for projectile in self.projectiles:
            self.spatial_grid.add_entity(projectile, "projectile")
    
    def _update_construction(self, dt: float):
        """Update building construction progress."""
        for building in self.buildings:
            if not building.is_constructed:
                # Construction requires energy
                if building.cost_energy > 0 and self.energy > 0:
                    energy_rate = min(building.cost_energy / building.construction_time, self.energy / dt)
                    self.energy -= energy_rate * dt
                    building.update_construction(dt)
                elif building.cost_energy == 0:
                    building.update_construction(dt)
    
    def _update_building_operations(self):
        """Update building special operations."""
        for building in self.buildings:
            if not building.is_alive() or not building.is_constructed or not building.connected_to_power:
                continue
            
            # Repair operations
            if building.repair_range > 0:
                all_buildings = [self.starting_base] + self.buildings
                building.repair_nearby(all_buildings, self.game_time, self.power_network)
            
            # Turret attacks
            if building.attack_range > 0:
                self._handle_turret_attack(building)
    
    def _handle_turret_attack(self, turret):
        """Handle automatic turret attacks."""
        if not turret.can_attack(self.game_time):
            return
        
        # Find nearest enemy in range
        nearest_enemy = None
        nearest_distance = float('inf')
        
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            dx = enemy.x - turret.x
            dy = enemy.y - turret.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= turret.attack_range and distance < nearest_distance:
                nearest_enemy = enemy
                nearest_distance = distance
        
        # Attack nearest enemy
        if nearest_enemy:
            projectile = turret.attack(nearest_enemy.x, nearest_enemy.y, self.game_time, self.power_network)
            if projectile:
                self.projectiles.append(projectile)
    
    def _update_enemies(self, dt: float):
        """Update enemy AI and behavior."""
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            enemy.update_ai(self.starting_base, self.buildings, dt)
            
            # Enemy attacks
            if enemy.state == "attacking" and enemy.can_attack(self.game_time) and enemy.target:
                projectile = enemy.attack(enemy.target.x, enemy.target.y, self.game_time)
                if projectile:
                    self.projectiles.append(projectile)
    
    def _update_projectiles(self, dt: float):
        """Update all projectiles."""
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            
            # Remove expired projectiles
            if projectile.is_expired():
                self.projectiles.remove(projectile)
    
    def _update_asteroids(self, dt: float):
        """Update asteroid rotation."""
        for asteroid in self.asteroids:
            asteroid.rotation += asteroid.rotation_speed * dt
    
    def _handle_collisions(self):
        """Handle all collision detection and resolution."""
        # Projectile collisions
        for projectile in self.projectiles[:]:
            nearby_entities = self.spatial_grid.get_nearby_entities(
                projectile.x, projectile.y, 50
            )
            
            for entity, entity_type in nearby_entities:
                if entity == projectile:
                    continue
                
                # Check collision distance
                dx = projectile.x - entity.x
                dy = projectile.y - entity.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < entity.get_collision_radius():
                    hit = False
                    
                    if projectile.owner_type == "player":
                        # Player projectiles hit enemies
                        if entity_type == "enemy":
                            if entity.take_damage(projectile.damage, self.game_time):
                                hit = True
                                if not entity.is_alive():
                                    self.score += 25 * self.wave
                                    self.minerals += 10  # Reward for killing enemies
                    
                    elif projectile.owner_type == "enemy":
                        # Enemy projectiles hit starting base and buildings
                        if entity_type in ["starting_base", "building"]:
                            if entity.take_damage(projectile.damage, self.game_time):
                                hit = True
                    
                    if hit:
                        self.projectiles.remove(projectile)
                        break
    
    def _check_wave_timing(self):
        """Check wave spawning timing."""
        living_enemies = [e for e in self.enemies if e.is_alive()]
        
        if len(living_enemies) == 0 and not self.wave_complete:
            self.wave_complete = True
            self.wave += 1
            self.next_wave_time = self.game_time + self.wave_delay
        
        # Spawn next wave after delay
        if self.wave_complete and self.game_time >= self.next_wave_time:
            self._spawn_wave()
    
    def _cleanup_dead_entities(self):
        """Remove dead entities from the game."""
        self.enemies = [e for e in self.enemies if e.is_alive()]
        self.buildings = [b for b in self.buildings if b.is_alive()]
        self.asteroids = [a for a in self.asteroids if a.is_alive()]
    
    def handle_build_request(self, building_type: str, x: float, y: float) -> bool:
        """Handle building construction request."""
        if building_type not in Building.BUILDING_TYPES:
            return False
        
        stats = Building.BUILDING_TYPES[building_type]
        
        # Check if we can afford it
        if (self.minerals >= stats["cost_minerals"] and 
            self.energy >= stats["cost_energy"]):
            
            # Check if location is valid
            min_distance = 60 if building_type == "wall" else 80
            if self._is_safe_spawn_location(x, y, min_distance):
                # Deduct resources
                self.minerals -= stats["cost_minerals"]
                self.energy -= stats["cost_energy"]
                
                # Create building
                new_building = Building(x, y, building_type, self.next_building_id)
                self.buildings.append(new_building)
                
                # Add to power network if it's a power node
                if new_building.is_power_node:
                    self.power_network.add_node(self.next_building_id, x, y)
                
                self.next_building_id += 1
                
                # Auto-connect to nearby nodes
                self._auto_connect_nearby_nodes()
                
                return True
        
        return False
    
    def render(self, camera):
        """Render all game entities."""
        # Draw power connections first (behind everything)
        self._draw_power_connections(camera)
        
        # Draw asteroids
        for asteroid in self.asteroids:
            if asteroid.is_alive():
                asteroid.draw(camera)
        
        # Draw starting base
        if self.starting_base and self.starting_base.is_alive():
            self.starting_base.draw(camera)
        
        # Draw buildings
        for building in self.buildings:
            if building.is_alive():
                building.draw(camera)
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.draw(camera)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(camera)
    
    def _draw_power_connections(self, camera):
        """Draw enhanced power network connections with better visibility."""
        connection_range = 120
        all_nodes = [self.starting_base] + [b for b in self.buildings if b.is_power_node and b.is_alive() and b.is_constructed]
        
        # Draw connections between all connected power nodes
        for node in all_nodes:
            node_screen_x = (node.x - camera.x) * camera.zoom + camera.width // 2
            node_screen_y = (node.y - camera.y) * camera.zoom + camera.height // 2
            
            for connected_id in node.connections:
                if connected_id == 0 or (hasattr(node, 'building_id') and connected_id <= node.building_id):
                    continue  # Avoid drawing duplicate lines
                
                connected_node = None
                if connected_id == 0:
                    connected_node = self.starting_base
                else:
                    connected_node = next((b for b in self.buildings if b.building_id == connected_id and b.is_alive()), None)
                
                if connected_node:
                    # Calculate screen positions
                    connected_screen_x = (connected_node.x - camera.x) * camera.zoom + camera.width // 2
                    connected_screen_y = (connected_node.y - camera.y) * camera.zoom + camera.height // 2
                    
                    # Check if line is visible on screen
                    if ((0 <= node_screen_x <= camera.width or 0 <= connected_screen_x <= camera.width) and 
                        (0 <= node_screen_y <= camera.height or 0 <= connected_screen_y <= camera.height)):
                        
                        # Color and thickness based on power status
                        if node.connected_to_power and connected_node.connected_to_power:
                            color = (0, 255, 255, 200)  # Bright cyan for powered
                            thickness = 3
                        else:
                            color = (100, 100, 100, 150)  # Gray for unpowered
                            thickness = 2
                        
                        # Draw main connection line
                        arcade.draw_line(node_screen_x, node_screen_y, 
                                       connected_screen_x, connected_screen_y, color, thickness)
                        
                        # Add energy flow animation for powered connections
                        if node.connected_to_power and connected_node.connected_to_power:
                            # Calculate flow animation offset
                            flow_offset = (self.game_time * 100) % 30
                            
                            # Draw flowing energy dots
                            line_length = math.sqrt((connected_screen_x - node_screen_x)**2 + 
                                                  (connected_screen_y - node_screen_y)**2)
                            if line_length > 0:
                                for i in range(0, int(line_length), 30):
                                    if (i + flow_offset) < line_length:
                                        progress = (i + flow_offset) / line_length
                                        dot_x = node_screen_x + progress * (connected_screen_x - node_screen_x)
                                        dot_y = node_screen_y + progress * (connected_screen_y - node_screen_y)
                                        arcade.draw_circle_filled(dot_x, dot_y, 2, (255, 255, 0, 180))
        
        # Draw connections from non-power buildings to nearby power nodes
        for building in self.buildings:
            if (building.is_alive() and building.is_constructed and 
                not building.is_power_node and building.connected_to_power):
                
                building_screen_x = (building.x - camera.x) * camera.zoom + camera.width // 2
                building_screen_y = (building.y - camera.y) * camera.zoom + camera.height // 2
                
                # Find nearest connected power node
                nearest_power_node = None
                nearest_distance = float('inf')
                
                for power_node in [self.starting_base] + [b for b in self.buildings if b.is_power_node and b.is_alive() and b.is_constructed]:
                    dx = building.x - power_node.x
                    dy = building.y - power_node.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance <= 80 and distance < nearest_distance:  # Connection range for non-power buildings
                        nearest_power_node = power_node
                        nearest_distance = distance
                
                if nearest_power_node:
                    power_screen_x = (nearest_power_node.x - camera.x) * camera.zoom + camera.width // 2
                    power_screen_y = (nearest_power_node.y - camera.y) * camera.zoom + camera.height // 2
                    
                    # Check if connection line is visible
                    if ((0 <= building_screen_x <= camera.width or 0 <= power_screen_x <= camera.width) and 
                        (0 <= building_screen_y <= camera.height or 0 <= power_screen_y <= camera.height)):
                        
                        # Draw dashed connection line for non-power buildings
                        color = (150, 255, 150, 150)  # Light green for building connections
                        
                        # Draw dashed line
                        line_dx = power_screen_x - building_screen_x
                        line_dy = power_screen_y - building_screen_y
                        line_length = math.sqrt(line_dx*line_dx + line_dy*line_dy)
                        
                        if line_length > 0:
                            dash_length = 10
                            num_dashes = int(line_length / (dash_length * 2))
                            
                            for i in range(num_dashes):
                                start_progress = (i * 2 * dash_length) / line_length
                                end_progress = ((i * 2 + 1) * dash_length) / line_length
                                
                                start_x = building_screen_x + start_progress * line_dx
                                start_y = building_screen_y + start_progress * line_dy
                                end_x = building_screen_x + end_progress * line_dx
                                end_y = building_screen_y + end_progress * line_dy
                                
                                arcade.draw_line(start_x, start_y, end_x, end_y, color, 2)
    
    def get_starting_base_position(self) -> Tuple[float, float]:
        """Get starting base position."""
        if self.starting_base:
            return (self.starting_base.x, self.starting_base.y)
        return (2400, 1350)
    
    def get_game_data(self) -> Dict[str, Any]:
        """Get current game data for UI."""
        # Calculate total power stats
        total_generation = 0
        total_capacity = 0
        total_stored = 0
        total_consumption = 0
        
        for stats in self.power_network.block_stats:
            total_generation += stats['power_generation']
            total_capacity += stats['power_capacity']
            total_stored += stats['power_stored']
            total_consumption += stats['power_consumption']
        
        return {
            'score': self.score,
            'game_time': self.game_time,
            'starting_base_health': self.starting_base.health if self.starting_base else 0,
            'starting_base_max_health': self.starting_base.max_health if self.starting_base else 2000,
            'minerals': self.minerals,
            'energy': self.energy,
            'power_generated': total_generation,
            'power_capacity': total_capacity,
            'power_stored': total_stored,
            'power_consumption': total_consumption,
            'enemies_count': len([e for e in self.enemies if e.is_alive()]),
            'buildings_count': len([b for b in self.buildings if b.is_alive()]),
            'wave': self.wave,
            'projectiles_count': len(self.projectiles),
            'next_wave_in': max(0, self.next_wave_time - self.game_time) if self.wave_complete else 0,
            'power_blocks': len(self.power_network.blocks)
        } 