"""
Enemy and wave logic for Space Game Clone.
"""
import numpy as np
import random
import pygame
import math
from settings import *

class Enemy:
    def __init__(self, x, y, health, speed=1.0):
        self.x = x
        self.y = y
        self.radius = 8
        self.size = 15
        self.health = health
        self.max_health = health
        self.speed = speed
        self.target = None
        self.orbit_angle = 0  # Angle for orbiting
        self.orbit_radius = 50
        self.orbit_speed = 0.05
        self.movement_angle = 0  # Direction of movement for triangle shape
        self.is_orbiting = False
    
    # Class variable for spaceship image (will be set from main.py)
    spaceship_image = None

    def find_nearest_target(self, buildings, base_pos):
        if buildings:
            # Separate buildings into damage-dealing and non-damage-dealing
            damage_buildings = [b for b in buildings if b.type in ['turret', 'laser']]
            other_buildings = [b for b in buildings if b.type not in ['turret', 'laser']]
            
            # Prefer damage-dealing buildings if they exist
            if damage_buildings:
                self.target = min(damage_buildings, key=lambda b: (self.x - b.x) ** 2 + (self.y - b.y) ** 2)
            else:
                self.target = min(other_buildings, key=lambda b: (self.x - b.x) ** 2 + (self.y - b.y) ** 2)
        else:
            self.target = {'x': base_pos[0], 'y': base_pos[1], 'type': 'base'}

    def update(self, buildings, base_pos):
        # Check if current target still exists
        if self.target and not isinstance(self.target, dict):
            if self.target not in buildings:
                self.target = None
        
        # Find new target if needed
        if not self.target:
            self.find_nearest_target(buildings, base_pos)
            
        if self.target:
            tx, ty = (self.target['x'], self.target['y']) if isinstance(self.target, dict) else (self.target.x, self.target.y)
            
            # Adjust orbit radius based on target size
            target_radius = 50 if isinstance(self.target, dict) else self.target.radius
            self.orbit_radius = target_radius + 30
            
            dist = np.hypot(self.x - tx, self.y - ty)
            
            if dist > self.orbit_radius + 10:  # Moving towards target
                self.is_orbiting = False
                dx = tx - self.x
                dy = ty - self.y
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                # Movement angle points toward target
                self.movement_angle = math.atan2(dy, dx)
            else:  # Orbiting target
                if not self.is_orbiting:
                    # Initialize orbit angle when starting to orbit
                    self.orbit_angle = math.atan2(self.y - ty, self.x - tx)
                    self.is_orbiting = True
                
                # Smooth orbital movement
                self.orbit_angle += self.orbit_speed
                self.x = tx + self.orbit_radius * np.cos(self.orbit_angle)
                self.y = ty + self.orbit_radius * np.sin(self.orbit_angle)
                
                # Triangle points in the direction of orbital movement (tangent to circle)
                self.movement_angle = self.orbit_angle + math.pi / 2

    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        screen_size = self.size * camera.zoom
        
        # Don't draw if off screen
        if (screen_x < -screen_size or screen_x > surface.get_width() + screen_size or
            screen_y < -screen_size or screen_y > surface.get_height() + screen_size):
            return
        
        # Enhanced red triangle with engine glow effect
        points = []
        # Triangle vertices relative to center (scaled by zoom)
        triangle_points = [(10 * camera.zoom, 0), (-8 * camera.zoom, -6 * camera.zoom), (-8 * camera.zoom, 6 * camera.zoom)]
        
        # Create glow points for engine effect
        glow_points = []
        engine_glow_points = [(-12 * camera.zoom, -4 * camera.zoom), (-12 * camera.zoom, 4 * camera.zoom), (-8 * camera.zoom, 0)]
        
        for px, py in triangle_points:
            # Rotate by movement angle
            rotated_x = px * math.cos(self.movement_angle) - py * math.sin(self.movement_angle)
            rotated_y = px * math.sin(self.movement_angle) + py * math.cos(self.movement_angle)
            points.append((screen_x + rotated_x, screen_y + rotated_y))
        
        for px, py in engine_glow_points:
            # Rotate by movement angle
            rotated_x = px * math.cos(self.movement_angle) - py * math.sin(self.movement_angle)
            rotated_y = px * math.sin(self.movement_angle) + py * math.cos(self.movement_angle)
            glow_points.append((screen_x + rotated_x, screen_y + rotated_y))
        
        # Draw engine glow
        pygame.draw.polygon(surface, (100, 50, 0), glow_points)
        
        # Draw main ship
        pygame.draw.polygon(surface, (255, 0, 0), points)
        pygame.draw.polygon(surface, (0, 0, 0), points, max(1, int(2 * camera.zoom)))
        
        # Health bar if damaged
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = 20 * camera.zoom
            bar_height = 4 * camera.zoom
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - screen_size - 8 * camera.zoom
            pygame.draw.rect(surface, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

class Mothership(Enemy):
    def __init__(self, x, y, health):
        super().__init__(x, y, health, MOTHERSHIP_SPEED)
        self.size = MOTHERSHIP_SIZE
        self.radius = 12
        self.missile_cooldown = 0
        self.attack_range = MOTHERSHIP_MISSILE_RANGE
        self.is_mothership = True
        self.stop_distance = self.attack_range // 2  # Stop at half attack range
        
    # Class variable for mothership image (will be set from main.py)
    mothership_image = None
    
    def update(self, buildings, base_pos):
        # Check if current target still exists
        if self.target and not isinstance(self.target, dict):
            if self.target not in buildings:
                self.target = None
        
        # Find new target if needed
        if not self.target:
            self.find_nearest_target(buildings, base_pos)
            
        if self.target:
            tx, ty = (self.target['x'], self.target['y']) if isinstance(self.target, dict) else (self.target.x, self.target.y)
            dist = np.hypot(self.x - tx, self.y - ty)
            
            # Move towards target until within stop distance
            if dist > self.stop_distance:
                dx = tx - self.x
                dy = ty - self.y
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self.movement_angle = math.atan2(dy, dx)
            else:
                # Stop and face target for missile attacks
                dx = tx - self.x
                dy = ty - self.y
                self.movement_angle = math.atan2(dy, dx)
        
        # Update missile cooldown
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
    
    def can_attack(self):
        if not self.target or self.missile_cooldown > 0:
            return False
        tx, ty = (self.target['x'], self.target['y']) if isinstance(self.target, dict) else (self.target.x, self.target.y)
        dist = np.hypot(self.x - tx, self.y - ty)
        return dist <= self.attack_range
    
    def fire_missile(self):
        if self.can_attack():
            self.missile_cooldown = MOTHERSHIP_MISSILE_COOLDOWN
            return True
        return False
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        screen_size = self.size * camera.zoom
        
        # Don't draw if off screen
        if (screen_x < -screen_size or screen_x > surface.get_width() + screen_size or
            screen_y < -screen_size or screen_y > surface.get_height() + screen_size):
            return
        
        # Enhanced green mothership with energy core
        rect_width = 20 * camera.zoom
        rect_height = 15 * camera.zoom
        
        # Create rectangle points for rotation
        rect_points = [
            (-rect_width/2, -rect_height/2),
            (rect_width/2, -rect_height/2),
            (rect_width/2, rect_height/2),
            (-rect_width/2, rect_height/2)
        ]
        
        points = []
        for px, py in rect_points:
            # Rotate by movement angle
            rotated_x = px * math.cos(self.movement_angle) - py * math.sin(self.movement_angle)
            rotated_y = px * math.sin(self.movement_angle) + py * math.cos(self.movement_angle)
            points.append((screen_x + rotated_x, screen_y + rotated_y))
        
        # Draw energy core glow
        core_radius = max(4, int(8 * camera.zoom))
        pygame.draw.circle(surface, (50, 255, 50), (int(screen_x), int(screen_y)), core_radius + 2)
        pygame.draw.circle(surface, (150, 255, 150), (int(screen_x), int(screen_y)), core_radius)
        
        pygame.draw.polygon(surface, (0, 255, 0), points)
        pygame.draw.polygon(surface, (0, 100, 0), points, max(1, int(2 * camera.zoom)))
        
        # Health bar if damaged
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = 30 * camera.zoom  # Wider health bar
            bar_height = 6 * camera.zoom  # Taller health bar
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - screen_size - 12 * camera.zoom
            pygame.draw.rect(surface, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

class MothershipMissile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = MISSILE_SPEED
        self.alive = True
        self.splash_radius = MISSILE_SPLASH_RADIUS
        self.angle = 0  # Track movement angle for rotation
        self.flash_timer = 0  # For flashing effect
        
    # Class variable for missile image (will be set from main.py)
    missile_image = None
    
    def update(self):
        if not self.target or not hasattr(self.target, 'x'):
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
        # Calculate angle for image rotation
        self.angle = math.atan2(dy, dx)
        self.flash_timer += 1  # Increment flash timer
        
        if dist < self.speed:
            self.x, self.y = self.target.x, self.target.y
            self.alive = False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if 0 <= screen_x <= surface.get_width() and 0 <= screen_y <= surface.get_height():
            # Flashing red dot - larger and more intense than regular missiles
            flash_cycle = (self.flash_timer // 3) % 2  # Flash every 3 frames (faster than regular missiles)
            if flash_cycle == 0:
                color = (255, 120, 120)  # Bright orange-red
                glow_color = (255, 160, 120)
            else:
                color = (200, 40, 40)   # Dark red
                glow_color = (240, 80, 80)
            
            radius = max(4, int(MISSILE_SIZE * camera.zoom * 1.5))  # Larger than regular missiles
            
            # Draw glow effect
            pygame.draw.circle(surface, glow_color, (int(screen_x), int(screen_y)), radius + 2)
            # Draw main projectile
            pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), radius)

class WaveManager:
    def __init__(self, world_w, world_h, base_pos):
        self.world_w = world_w
        self.world_h = world_h
        self.base_pos = base_pos
        self.wave = 1
        self.enemies = []
        self.wait_timer = INITIAL_WAIT
        self.spawn_timer = 0
        self.spawn_count = 0
        self.wave_active = False
        self.formations = []  # List of formation spawn points
        self.current_formation = 0
        self.enemies_per_formation = 0
        self.can_start_next_wave = False  # For manual wave starting

    def start_wave(self):
        self.wave_active = True
        self.can_start_next_wave = False
        # Faster wave growth
        self.spawn_count = int(ENEMY_SPAWN_BASE * (WAVE_GROWTH_FACTOR ** (self.wave - 1)))
        self.spawn_timer = 0
        
        # Set up formations for larger waves
        if self.spawn_count >= FORMATION_SIZE_THRESHOLD:
            num_formations = min(MAX_FORMATIONS, max(2, self.spawn_count // 8))
            self.enemies_per_formation = self.spawn_count // num_formations
            
            # Create formation spawn points around the map edges
            self.formations = []
            for i in range(num_formations):
                # Distribute formations around the map perimeter
                side = i % 4
                if side == 0:  # Top
                    x = random.randint(self.world_w // 4, 3 * self.world_w // 4)
                    y = 0
                elif side == 1:  # Right
                    x = self.world_w
                    y = random.randint(self.world_h // 4, 3 * self.world_h // 4)
                elif side == 2:  # Bottom
                    x = random.randint(self.world_w // 4, 3 * self.world_w // 4)
                    y = self.world_h
                else:  # Left
                    x = 0
                    y = random.randint(self.world_h // 4, 3 * self.world_h // 4)
                
                self.formations.append((x, y))
            
            self.current_formation = 0
        else:
            # Small waves use single spawn points
            self.formations = []
            self.enemies_per_formation = self.spawn_count

    def force_next_wave(self):
        """Manually start the next wave"""
        if self.can_start_next_wave:
            self.wait_timer = 0

    def update(self, buildings):
        if not self.wave_active:
            if self.wait_timer > 0:
                self.wait_timer -= 1
                self.can_start_next_wave = True  # Allow manual wave start
            else:
                self.start_wave()
        else:
            if self.spawn_count > 0:
                if self.spawn_timer <= 0:
                    if self.formations:
                        # Formation spawning
                        formation_x, formation_y = self.formations[self.current_formation]
                        # Add some spread within the formation
                        spread = 50
                        x = formation_x + random.uniform(-spread, spread)
                        y = formation_y + random.uniform(-spread, spread)
                        # Keep within world bounds
                        x = max(0, min(self.world_w, x))
                        y = max(0, min(self.world_h, y))
                        
                        # Move to next formation after spawning enough enemies
                        enemies_spawned_in_formation = self.enemies_per_formation - (self.spawn_count % self.enemies_per_formation)
                        if enemies_spawned_in_formation >= self.enemies_per_formation:
                            self.current_formation = (self.current_formation + 1) % len(self.formations)
                    else:
                        # Traditional single-point spawning for small waves
                        side = random.choice(['left', 'right', 'top', 'bottom'])
                        if side == 'left':
                            x, y = 0, random.randint(0, self.world_h)
                        elif side == 'right':
                            x, y = self.world_w, random.randint(0, self.world_h)
                        elif side == 'top':
                            x, y = random.randint(0, self.world_w), 0
                        else:
                            x, y = random.randint(0, self.world_w), self.world_h
                    
                    health = ENEMY_HEALTH_BASE * self.wave
                    
                    # Spawn mothership or regular enemy
                    if self.wave >= 3 and random.random() < MOTHERSHIP_SPAWN_CHANCE:
                        # Spawn mothership with higher health
                        mothership_health = health * MOTHERSHIP_HEALTH_MULTIPLIER
                        self.enemies.append(Mothership(x, y, mothership_health))
                    else:
                        # Spawn regular enemy
                        self.enemies.append(Enemy(x, y, health))
                    
                    self.spawn_count -= 1
                    self.spawn_timer = SPAWN_INTERVAL
                else:
                    self.spawn_timer -= 1
            elif not self.enemies:
                self.wave_active = False
                self.wave += 1
                self.wait_timer = WAVE_WAIT_TIME

    def update_enemies(self, buildings):
        for e in self.enemies:
            e.update(buildings, self.base_pos)
        self.enemies = [e for e in self.enemies if e.health > 0]

    def draw_enemies(self, surface, camera):
        for e in self.enemies:
            e.draw(surface, camera) 