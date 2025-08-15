"""
Projectile System - Bullets, lasers, and other projectiles
"""

import time
import math
from enum import Enum
from typing import Optional

class ProjectileType(Enum):
    """Types of projectiles"""
    BULLET = "bullet"
    LASER = "laser"
    MISSILE = "missile"

class Projectile:
    """Base projectile class for bullets, lasers, etc."""
    
    def __init__(self, projectile_type: ProjectileType, x: float, y: float, 
                 target_x: float, target_y: float, speed: float, damage: float,
                 max_range: float = 200, owner=None, game_engine=None):
        # Core properties
        self.projectile_type = projectile_type
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.speed = speed
        self.damage = damage
        self.max_range = max_range
        self.owner = owner
        self.game_engine = game_engine
        
        # Calculate direction and velocity
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        else:
            self.velocity_x = 0
            self.velocity_y = 0
        
        # State
        self.active = True
        self.travel_distance = 0
        
        # Visual representation
        self.visual_node = None
        self.create_visual()
    
    def update(self, dt: float):
        """Update projectile position and check for collisions"""
        if not self.active:
            return
            
        # Update position
        old_x, old_y = self.x, self.y
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update travel distance
        distance_moved = math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
        self.travel_distance += distance_moved
        
        # Check max range
        if self.travel_distance >= self.max_range:
            self.destroy()
            return
        
        # Update visual position
        if self.visual_node:
            self.visual_node.setPos(self.x, self.y, 4)  # Slightly below enemies
        
        # Check for collisions
        self.check_collisions()
    
    def check_collisions(self):
        """Check for collisions with targets"""
        if not self.game_engine or not self.active:
            return
            
        # Check collision with buildings (if fired by enemy)
        if hasattr(self.owner, 'enemy_type'):  # Enemy projectile
            for building in self.game_engine.building_system.buildings.values():
                if self.check_collision_with_building(building):
                    building.take_damage(self.damage)
                    self.destroy()
                    return
        
        # Check collision with enemies (if fired by player/buildings)
        else:  # Player projectile
            for enemy in self.game_engine.enemies:
                if self.check_collision_with_enemy(enemy):
                    enemy.take_damage(self.damage)
                    
                    # Create impact effect based on projectile type
                    self.create_impact_effect(enemy.x, enemy.y)
                    
                    self.destroy()
                    return
    
    def check_collision_with_building(self, building):
        """Check if projectile collides with a building"""
        distance = math.sqrt((self.x - building.x)**2 + (self.y - building.y)**2)
        return distance < building.radius
    
    def check_collision_with_enemy(self, enemy):
        """Check if projectile collides with an enemy"""
        distance = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
        return distance < enemy.radius
    
    def destroy(self):
        """Destroy the projectile"""
        self.active = False
        if self.visual_node:
            self.visual_node.removeNode()
            self.visual_node = None
    
    def create_visual(self):
        """Create visual representation of the projectile"""
        if self.game_engine and hasattr(self.game_engine, 'scene_manager'):
            scene_manager = self.game_engine.scene_manager
            if hasattr(scene_manager, 'entity_visualizer'):
                self.visual_node = scene_manager.entity_visualizer.create_projectile_visual(
                    self.projectile_type.value, self.x, self.y
                )
    
    def is_active(self):
        """Check if projectile is still active"""
        return self.active
    
    def create_impact_effect(self, impact_x, impact_y):
        """Create visual impact effect at collision point"""
        try:
            if self.game_engine and hasattr(self.game_engine, 'scene_manager'):
                scene_manager = self.game_engine.scene_manager
                if hasattr(scene_manager, 'entity_visualizer'):
                    if self.projectile_type == ProjectileType.BULLET:
                        # Create bullet impact sparks
                        scene_manager.entity_visualizer.create_bullet_impact_effect(impact_x, impact_y)
                    elif self.projectile_type == ProjectileType.LASER:
                        # Create laser impact glow (smaller explosion-like effect)
                        scene_manager.entity_visualizer.create_explosion_effect(impact_x, impact_y)
                        
        except Exception as e:
            print(f"Error creating impact effect: {e}")

class Laser:
    """Special laser projectile for instant hit"""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float, 
                 damage: float, max_range: float = 120, owner=None, game_engine=None):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage
        self.max_range = max_range
        self.owner = owner
        self.game_engine = game_engine
        
        # Visual representation
        self.visual_node = None
        self.active = True
        self.duration = 0.1  # Laser beam duration in seconds
        self.time_remaining = self.duration
        
        # Create visual representation
        self.create_visual()
        
        # Check if target is in range
        distance = math.sqrt((target_x - x)**2 + (target_y - y)**2)
        if distance <= max_range:
            self.hit_target()
    
    def hit_target(self):
        """Apply laser damage instantly"""
        if not self.game_engine:
            return
            
        # Check what we hit
        if hasattr(self.owner, 'enemy_type'):  # Enemy laser
            # Find buildings near target point
            for building in self.game_engine.building_system.buildings.values():
                distance = math.sqrt((self.target_x - building.x)**2 + (self.target_y - building.y)**2)
                if distance < building.radius:
                    building.take_damage(self.damage)
                    break
        else:  # Player laser
            # Find enemies near target point
            for enemy in self.game_engine.enemies:
                distance = math.sqrt((self.target_x - enemy.x)**2 + (self.target_y - enemy.y)**2)
                if distance < enemy.radius:
                    enemy.take_damage(self.damage)
                    break
    
    def update(self, dt: float):
        """Update laser visual (fades out)"""
        if not self.active:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.destroy()
    
    def destroy(self):
        """Remove laser visual"""
        self.active = False
        if self.visual_node:
            self.visual_node.removeNode()
            self.visual_node = None
    
    def create_visual(self):
        """Create visual representation of the laser beam"""
        if self.game_engine and hasattr(self.game_engine, 'scene_manager'):
            scene_manager = self.game_engine.scene_manager
            if hasattr(scene_manager, 'entity_visualizer'):
                self.visual_node = scene_manager.entity_visualizer.create_laser_beam_visual(
                    self.x, self.y, self.target_x, self.target_y
                )
    
    def is_active(self):
        """Check if laser is still active"""
        return self.active


class Missile:
    """Homing missile projectile class with intelligent targeting"""
    
    def __init__(self, x: float, y: float, damage: float, max_range: float = 400, 
                 speed: float = 150, owner=None, game_engine=None):
        self.x = x
        self.y = y
        self.damage = damage
        self.max_range = max_range
        self.speed = speed
        self.owner = owner
        self.game_engine = game_engine
        
        # Missile properties
        self.max_lifetime = 12.0  # 12 seconds flight time
        self.lifetime = 0.0
        self.active = True
        
        # Targeting system
        self.target_enemy = None
        self.retarget_timer = 0.0
        self.retarget_interval = 0.5  # Retarget every 0.5 seconds
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.turn_rate = 3.0  # Radians per second turning speed
        
        # Visual
        self.visual_node = None
        self.trail_nodes = []  # For missile trail effect
        
        # Initialize
        self.find_target()
        self.create_visual()
    
    def find_target(self):
        """Find the nearest enemy to target"""
        if not self.game_engine or not hasattr(self.game_engine, 'enemies'):
            return
            
        nearest_enemy = None
        nearest_distance = float('inf')
        
        for enemy in self.game_engine.enemies:
            if not enemy.is_alive():
                continue
                
            distance = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2)**0.5
            if distance < nearest_distance and distance <= self.max_range:
                nearest_enemy = enemy
                nearest_distance = distance
        
        if nearest_enemy != self.target_enemy:
            self.target_enemy = nearest_enemy
            if self.target_enemy:
                print(f"🚀 Missile targeting {self.target_enemy.enemy_type} at ({self.target_enemy.x:.0f}, {self.target_enemy.y:.0f})")
    
    def update(self, dt: float):
        """Update missile position and targeting"""
        if not self.active:
            return
            
        # Update lifetime
        self.lifetime += dt
        if self.lifetime >= self.max_lifetime:
            print("🚀 Missile expired after 12 seconds")
            self.destroy()
            return
        
        # Update retargeting timer
        self.retarget_timer += dt
        if self.retarget_timer >= self.retarget_interval:
            # Check if current target is still alive
            if self.target_enemy and not self.target_enemy.is_alive():
                self.target_enemy = None
                
            # Find new target if needed
            if not self.target_enemy:
                self.find_target()
                
            self.retarget_timer = 0.0
        
        # Update movement toward target
        if self.target_enemy:
            self.update_homing_movement(dt)
        else:
            # No target - continue in current direction
            self.update_straight_movement(dt)
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update visual
        self.update_visual()
        
        # Check for collisions
        self.check_collisions()
    
    def update_homing_movement(self, dt: float):
        """Update velocity to home in on target"""
        if not self.target_enemy:
            return
            
        # Calculate direction to target
        target_dx = self.target_enemy.x - self.x
        target_dy = self.target_enemy.y - self.y
        target_distance = (target_dx**2 + target_dy**2)**0.5
        
        if target_distance < 5.0:  # Very close to target
            # Direct hit
            self.velocity_x = target_dx * 10  # Fast final approach
            self.velocity_y = target_dy * 10
            return
        
        # Normalize target direction
        target_dx /= target_distance
        target_dy /= target_distance
        
        # Current velocity direction
        current_speed = (self.velocity_x**2 + self.velocity_y**2)**0.5
        if current_speed > 0:
            current_dx = self.velocity_x / current_speed
            current_dy = self.velocity_y / current_speed
        else:
            # Initial velocity toward target
            self.velocity_x = target_dx * self.speed
            self.velocity_y = target_dy * self.speed
            return
        
        # Calculate angular difference
        import math
        current_angle = math.atan2(current_dy, current_dx)
        target_angle = math.atan2(target_dy, target_dx)
        
        # Calculate shortest angular distance
        angle_diff = target_angle - current_angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Limit turn rate
        max_turn = self.turn_rate * dt
        if abs(angle_diff) <= max_turn:
            new_angle = target_angle
        else:
            new_angle = current_angle + math.copysign(max_turn, angle_diff)
        
        # Update velocity
        self.velocity_x = math.cos(new_angle) * self.speed
        self.velocity_y = math.sin(new_angle) * self.speed
    
    def update_straight_movement(self, dt: float):
        """Continue in current direction when no target"""
        # Maintain current velocity, or default forward if no velocity
        current_speed = (self.velocity_x**2 + self.velocity_y**2)**0.5
        if current_speed < 10:  # Very slow or stationary
            self.velocity_x = self.speed  # Default: move right
            self.velocity_y = 0
    
    def check_collisions(self):
        """Check for collisions with enemies"""
        if not self.active or not self.game_engine:
            return
            
        for enemy in self.game_engine.enemies:
            if not enemy.is_alive():
                continue
                
            distance = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2)**0.5
            if distance <= enemy.radius + 5:  # Hit detection
                # Direct hit
                enemy.take_damage(self.damage)
                print(f"💥 Missile hit {enemy.enemy_type} for {self.damage:.1f} damage")
                
                # Create explosion effect
                self.create_explosion_effect()
                
                # Apply splash damage to nearby enemies
                self.apply_splash_damage()
                
                self.destroy()
                return
    
    def apply_splash_damage(self):
        """Apply splash damage to enemies near impact point"""
        if not self.game_engine:
            return
            
        splash_radius = 60  # From config
        splash_damage = self.damage * 0.5  # 50% splash damage
        
        for enemy in self.game_engine.enemies:
            if not enemy.is_alive():
                continue
                
            distance = ((enemy.x - self.x)**2 + (enemy.y - self.y)**2)**0.5
            if distance <= splash_radius:
                # Apply reduced damage based on distance
                damage_multiplier = 1.0 - (distance / splash_radius)
                final_damage = splash_damage * damage_multiplier
                
                if final_damage > 0.1:  # Minimum damage threshold
                    enemy.take_damage(final_damage)
                    print(f"💥 Missile splash hit {enemy.enemy_type} for {final_damage:.1f} damage")
    
    def create_explosion_effect(self):
        """Create visual explosion effect at impact point"""
        if self.game_engine and hasattr(self.game_engine, 'scene_manager'):
            scene_manager = self.game_engine.scene_manager
            if hasattr(scene_manager, 'entity_visualizer'):
                scene_manager.entity_visualizer.create_explosion_effect(self.x, self.y)
    
    def create_visual(self):
        """Create visual representation of missile"""
        if self.game_engine and hasattr(self.game_engine, 'scene_manager'):
            scene_manager = self.game_engine.scene_manager
            if hasattr(scene_manager, 'entity_visualizer'):
                self.visual_node = scene_manager.entity_visualizer.create_missile_visual(self.x, self.y)
    
    def update_visual(self):
        """Update missile visual position"""
        if self.visual_node:
            self.visual_node.setPos(self.x, self.y, 3)  # Slightly elevated
    
    def destroy(self):
        """Remove missile and clean up"""
        if self.visual_node:
            self.visual_node.removeNode()
            self.visual_node = None
            
        # Clean up trail nodes
        for trail_node in self.trail_nodes:
            if trail_node:
                trail_node.removeNode()
        self.trail_nodes.clear()
        
        self.active = False
    
    def is_active(self):
        """Check if missile is still active"""
        return self.active
