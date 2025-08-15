"""
Enemy Entity System - Basic Implementation
Core enemy classes that integrate with the wave system
"""

import time
import math
from enum import Enum
from typing import Dict, Optional
from .projectile import Projectile, Laser, ProjectileType

class EnemyState(Enum):
    """Enemy operational states"""
    SPAWNING = "spawning"
    MOVING = "moving"
    ATTACKING = "attacking"
    DESTROYED = "destroyed"

class Enemy:
    """Basic enemy entity"""
    
    def __init__(self, enemy_type: str, x: float, y: float, config, game_engine=None):
        # Core identity
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.config = config
        self.game_engine = game_engine
        
        # Get enemy configuration
        enemy_config = config.enemies.get("enemy_types", {}).get(enemy_type, {})
        
        # Basic properties
        base_health = enemy_config.get("base_health", 24)
        # Handle "calculated" or string values
        if isinstance(base_health, str) or base_health == "calculated":
            self.max_health = 24.0  # Default health
        else:
            self.max_health = float(base_health)
        self.current_health = self.max_health
        self.speed = enemy_config.get("speed", 0.5) * 60  # Convert to pixels per second
        self.radius = enemy_config.get("radius", 8)
        self.points = enemy_config.get("points", 1)
        
        # State and movement
        self.state = EnemyState.MOVING
        self.target_x = 2400  # Initial target - world center (player base)
        self.target_y = 1350
        self.velocity_x = 0
        self.velocity_y = 0
        self.target_building = None  # Current target building
        self.retarget_timer = 0  # Timer to update targets
        
        # Visual representation
        self.visual_node = None
        
        # Weapon systems
        self.weapon_cooldown = 0
        self.max_weapon_cooldown = self.get_weapon_cooldown()
        self.weapon_range = self.get_weapon_range()
        
        # Calculate initial direction toward target
        self.update_movement_direction()
        
    def update_movement_direction(self):
        """Update movement direction toward target"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize and scale by speed
            self.velocity_x = (dx / distance) * self.speed
            self.velocity_y = (dy / distance) * self.speed
    
    def update(self, dt: float):
        """Update enemy state and position"""
        if self.state == EnemyState.DESTROYED:
            return
            
        # Update weapon cooldown
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= dt
        
        # Update retargeting timer
        self.retarget_timer += dt
        if self.retarget_timer >= 2.0:  # Retarget every 2 seconds
            self.find_nearest_target()
            self.retarget_timer = 0
            
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update visual position if exists
        if self.visual_node:
            self.visual_node.setPos(self.x, self.y, 5)
        
        # Check for targets to attack
        self.check_and_attack_targets()
        
        # Check if reached current target
        distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        if distance_to_target < 30:  # Close to target
            if self.target_building:
                self.state = EnemyState.ATTACKING
                # Attack the building directly
                if self.weapon_cooldown <= 0:
                    self.fire_weapon(self.target_building.x, self.target_building.y)
            else:
                # Reached base area, look for nearby buildings to attack
                self.find_nearest_target()
                if not self.target_building:
                    # No buildings found, deal damage to base (TODO: implement base damage)
                    self.state = EnemyState.ATTACKING
    
    def take_damage(self, amount: float):
        """Apply damage to enemy"""
        self.current_health = max(0, self.current_health - amount)
        if self.current_health <= 0:
            self.destroy()
    
    def destroy(self):
        """Destroy enemy and award points"""
        self.state = EnemyState.DESTROYED
        if self.game_engine:
            self.game_engine.score += self.points
        
        # Remove visual representation
        if self.visual_node:
            self.visual_node.removeNode()
            self.visual_node = None
    
    def get_position(self):
        """Get enemy position as tuple"""
        return (self.x, self.y)
    
    def is_alive(self):
        """Check if enemy is still alive"""
        return self.state != EnemyState.DESTROYED
    
    def get_weapon_cooldown(self):
        """Get weapon cooldown based on enemy type"""
        enemy_config = self.config.enemies.get("enemy_types", {}).get(self.enemy_type, {})
        if self.enemy_type == "basic":
            return 1.0  # Fighters fire every 1 second
        elif self.enemy_type == "mothership":
            return 2.0  # Motherships fire every 2 seconds
        else:
            return enemy_config.get("laser_cooldown", 60) / 60.0  # Convert from game ticks to seconds
    
    def get_weapon_range(self):
        """Get weapon range based on enemy type"""
        enemy_config = self.config.enemies.get("enemy_types", {}).get(self.enemy_type, {})
        if self.enemy_type == "basic":
            return 120  # Short range laser
        elif self.enemy_type == "mothership":
            return 200  # Longer range bullets
        else:
            return enemy_config.get("laser_range", 120)
    
    def find_nearest_target(self):
        """Find the nearest building to target"""
        if not self.game_engine:
            return
            
        nearest_building = None
        nearest_distance = float('inf')
        
        for building in self.game_engine.building_system.buildings.values():
            # Skip asteroid buildings - focus on player structures
            if building.building_type == "asteroid":
                continue
                
            distance = math.sqrt((building.x - self.x)**2 + (building.y - self.y)**2)
            if distance < nearest_distance:
                nearest_building = building
                nearest_distance = distance
        
        if nearest_building != self.target_building:
            self.target_building = nearest_building
            if self.target_building:
                self.target_x = self.target_building.x
                self.target_y = self.target_building.y
                self.update_movement_direction()
                
                # Update visual direction when retargeting
                if hasattr(self, 'visual_node') and self.visual_node and self.game_engine:
                    scene_manager = getattr(self.game_engine, 'scene_manager', None)
                    if scene_manager and hasattr(scene_manager, 'entity_visualizer'):
                        new_visual = scene_manager.entity_visualizer.update_enemy_visual_direction(
                            self.visual_node, self.enemy_type, self.radius, 
                            self.velocity_x, self.velocity_y
                        )
                        if new_visual:
                            self.visual_node = new_visual
                
                print(f"Enemy retargeting {self.target_building.building_type} at ({self.target_x:.0f}, {self.target_y:.0f})")
    
    def check_and_attack_targets(self):
        """Check for targets in range and attack if possible"""
        if not self.game_engine or self.weapon_cooldown > 0:
            return
            
        # Find nearest building in weapon range
        nearest_building = None
        nearest_distance = float('inf')
        
        for building in self.game_engine.building_system.buildings.values():
            if building.building_type == "asteroid":  # Skip asteroids
                continue
                
            distance = math.sqrt((building.x - self.x)**2 + (building.y - self.y)**2)
            if distance <= self.weapon_range and distance < nearest_distance:
                nearest_building = building
                nearest_distance = distance
        
        if nearest_building:
            self.fire_weapon(nearest_building.x, nearest_building.y)
    
    def fire_weapon(self, target_x: float, target_y: float):
        """Fire weapon at target"""
        if self.weapon_cooldown > 0:
            return
            
        if self.enemy_type == "basic":
            # Fighter fires short-range laser
            laser = Laser(
                self.x, self.y, target_x, target_y,
                damage=5.0, max_range=self.weapon_range,
                owner=self, game_engine=self.game_engine
            )
            if self.game_engine:
                self.game_engine.projectiles.append(laser)
                
        elif self.enemy_type == "mothership":
            # Mothership fires bullets
            bullet = Projectile(
                ProjectileType.BULLET,
                self.x, self.y, target_x, target_y,
                speed=300.0, damage=10.0, max_range=self.weapon_range,
                owner=self, game_engine=self.game_engine
            )
            if self.game_engine:
                self.game_engine.projectiles.append(bullet)
        
        # Reset weapon cooldown
        self.weapon_cooldown = self.max_weapon_cooldown
        
        print(f"{self.enemy_type} enemy fired weapon at ({target_x:.0f}, {target_y:.0f})")
