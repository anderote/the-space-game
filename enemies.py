"""
Enemy and wave logic for Space Game Clone.
"""
import numpy as np
import random
import pygame
import math
from settings import *

class Enemy:
    def __init__(self, x, y, health, speed=0.5, enemy_type="basic"):  # Reduced by 50% (was 1.0)
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
        self.orbit_speed = 0.01  # Reduced by 80% (was 0.05)
        self.movement_angle = 0  # Direction of movement for triangle shape
        self.is_orbiting = False
        self.enemy_type = enemy_type
        self.last_shot_time = 0  # For laser timing
        self.laser_target = None  # For visual laser effects
        self.points = 1  # Default point value for basic enemies
    
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
                
                # Basic laser firing for small red ships
                current_time = pygame.time.get_ticks()
                laser_cooldown = 60  # 1 second at 60fps
                laser_range = 120    # Shorter range than larger ships
                laser_damage = 5    # Reduced by 50% (was 10)
                
                if current_time - self.last_shot_time > laser_cooldown:
                    # Check if target is within laser range (only fire when orbiting and close)
                    if dist <= laser_range and not isinstance(self.target, dict):
                        # Fire laser at building target
                        if hasattr(self.target, 'take_damage'):
                            self.target.take_damage(laser_damage)
                            self.last_shot_time = current_time
                            # Store laser target for visual effects
                            self.laser_target = self.target
                        else:
                            self.laser_target = None
                    else:
                        self.laser_target = None

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
        
        # Health bar if damaged (only show when not at full health, 50% opacity)
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = 40 * camera.zoom  # 2x larger
            bar_height = 8 * camera.zoom  # 2x larger
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - screen_size - 8 * camera.zoom
            
            # Create semi-transparent health bar
            health_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            health_surface.fill((200, 0, 0, 127))  # Red background with 50% alpha
            surface.blit(health_surface, (bar_x, bar_y))
            
            # Only create green surface if there's actual health to show
            green_width = max(1, int(bar_width * health_ratio))
            if green_width > 0:
                green_surface = pygame.Surface((green_width, bar_height), pygame.SRCALPHA)
                green_surface.fill((0, 200, 0, 127))  # Green with 50% alpha
                surface.blit(green_surface, (bar_x, bar_y))

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
        
        # Health bar if damaged (only show when not at full health, 50% opacity)
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = 60 * camera.zoom  # 2x larger than before
            bar_height = 12 * camera.zoom  # 2x larger than before
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - screen_size - 12 * camera.zoom
            
            # Create semi-transparent health bar
            health_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            health_surface.fill((200, 0, 0, 127))  # Red background with 50% alpha
            surface.blit(health_surface, (bar_x, bar_y))
            
            # Only create green surface if there's actual health to show
            green_width = max(1, int(bar_width * health_ratio))
            if green_width > 0:
                green_surface = pygame.Surface((green_width, bar_height), pygame.SRCALPHA)
                green_surface.fill((0, 200, 0, 127))  # Green with 50% alpha
                surface.blit(green_surface, (bar_x, bar_y))

class MothershipMissile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = MISSILE_SPEED
        self.alive = True
        self.splash_radius = MISSILE_SPLASH_RADIUS
        self.flash_timer = 0  # For flashing effect
        
    # Using simple particle effects instead of images
    
    def update(self):
        if not self.target or not hasattr(self.target, 'x'):
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
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
        
        # Point-based wave generation
        self.wave_points = self.calculate_wave_points()
        self.enemies_to_spawn = self.generate_enemy_composition()
        self.spawn_timer = 0
        
        # Set up formations for larger waves
        total_enemies = len(self.enemies_to_spawn)
        if total_enemies >= FORMATION_SIZE_THRESHOLD:
            num_formations = min(MAX_FORMATIONS, max(2, total_enemies // 8))
            self.enemies_per_formation = total_enemies // num_formations
            
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
            self.enemies_per_formation = total_enemies

    def calculate_wave_points(self):
        """Calculate total points for this wave using exponential growth"""
        if self.wave <= 3:
            # First 3 waves: only basic enemies (1 point each) - 3x larger starting size
            base_points = (3 + self.wave) * 3  # Waves 1-3: 12,15,18 points (was 4,5,6)
            return min(base_points, 24)
        else:
            # Exponential growth after wave 3 - 30% slower growth
            base_points = 24  # Starting from wave 4
            growth_factor = 1.4 * 0.7  # 30% slower growth = 0.98
            return int(base_points * (growth_factor ** (self.wave - 3)))
    
    def generate_enemy_composition(self):
        """Generate list of enemy types to spawn based on wave points"""
        enemies_to_spawn = []
        remaining_points = self.wave_points
        
        if self.wave <= 3:
            # Waves 1-3: Only basic enemies
            while remaining_points >= 1:
                enemies_to_spawn.append("basic")
                remaining_points -= 1
        else:
            # Later waves: Balanced composition with 50% basic fighters minimum
            total_basic_points = max(remaining_points // 2, remaining_points - 30)  # At least 50% basic
            
            # Add basic fighters first (50% of total points)
            basic_count = 0
            while total_basic_points > 0 and remaining_points > 0:
                enemies_to_spawn.append("basic")
                remaining_points -= 1
                total_basic_points -= 1
                basic_count += 1
            
            # Fill remaining points with varied ship types
            ship_types = [
                ("kamikaze", 2),    # Fast suicide ships
                ("assault", 3),     # Machine gun ships  
                ("stealth", 4),     # EMP cloaking ships
                ("large", 5),       # Laser battleships
                ("cruiser", 6),     # Heavy plasma cruisers
            ]
            
            # Distribute remaining points among ship types
            attempts = 0
            while remaining_points > 0 and attempts < 100:  # Prevent infinite loops
                attempts += 1
                
                # Prefer smaller ships early, larger ships in later waves
                if self.wave <= 7:
                    # Early waves: favor smaller ships
                    weights = [0.4, 0.3, 0.15, 0.1, 0.05]
                elif self.wave <= 12:
                    # Mid waves: balanced mix
                    weights = [0.25, 0.25, 0.2, 0.2, 0.1]
                else:
                    # Late waves: favor larger ships
                    weights = [0.15, 0.2, 0.25, 0.25, 0.15]
                
                # Choose ship type based on weights and available points
                available_ships = [(ship, cost) for ship, cost in ship_types if cost <= remaining_points]
                if not available_ships:
                    # Fill remaining points with basic fighters
                    while remaining_points > 0:
                        enemies_to_spawn.append("basic")
                        remaining_points -= 1
                    break
                
                # Weighted random selection
                ship_weights = []
                for i, (ship, cost) in enumerate(ship_types):
                    if cost <= remaining_points:
                        ship_weights.append(weights[i])
                    else:
                        ship_weights.append(0)
                
                if sum(ship_weights) == 0:
                    break
                
                # Normalize weights
                total_weight = sum(ship_weights)
                ship_weights = [w / total_weight for w in ship_weights]
                
                # Select ship type
                rand_val = random.random()
                cumulative = 0
                selected_ship = None
                selected_cost = 0
                
                for i, (ship, cost) in enumerate(ship_types):
                    cumulative += ship_weights[i]
                    if rand_val <= cumulative and cost <= remaining_points:
                        selected_ship = ship
                        selected_cost = cost
                        break
                
                if selected_ship:
                    enemies_to_spawn.append(selected_ship)
                    remaining_points -= selected_cost
                else:
                    # Fallback to basic fighter
                    if remaining_points >= 1:
                        enemies_to_spawn.append("basic")
                        remaining_points -= 1
                    else:
                        break
        
        # Shuffle to randomize spawn order while maintaining composition
        random.shuffle(enemies_to_spawn)
        return enemies_to_spawn
    
    def get_spawn_position(self):
        """Get spawn position based on formation or single spawn"""
        if self.formations:
            # Enhanced grid formation spawning
            formation_x, formation_y = self.formations[self.current_formation]
            
            # Create grid positions within each formation
            if not hasattr(self, 'formation_grid_positions'):
                self.formation_grid_positions = {}
                self.formation_spawn_counts = {}
            
            if self.current_formation not in self.formation_grid_positions:
                # Create a 3x3 or 4x4 grid for this formation
                grid_size = 3 if self.enemies_per_formation <= 9 else 4
                spacing = 60  # Distance between ships in grid
                
                grid_positions = []
                start_offset = -(grid_size - 1) * spacing / 2
                
                for row in range(grid_size):
                    for col in range(grid_size):
                        offset_x = start_offset + col * spacing
                        offset_y = start_offset + row * spacing
                        grid_positions.append((formation_x + offset_x, formation_y + offset_y))
                
                # Shuffle to make spawning less predictable but maintain formation
                random.shuffle(grid_positions)
                self.formation_grid_positions[self.current_formation] = grid_positions
                self.formation_spawn_counts[self.current_formation] = 0
            
            # Get next position from grid
            spawn_count = self.formation_spawn_counts[self.current_formation]
            grid_positions = self.formation_grid_positions[self.current_formation]
            
            if spawn_count < len(grid_positions):
                x, y = grid_positions[spawn_count]
                self.formation_spawn_counts[self.current_formation] += 1
            else:
                # Fallback if we need more ships than grid positions
                x = formation_x + random.uniform(-100, 100)
                y = formation_y + random.uniform(-100, 100)
            
            # Keep within world bounds
            x = max(50, min(self.world_w - 50, x))
            y = max(50, min(self.world_h - 50, y))
            
            # Move to next formation after spawning enough enemies
            if self.formation_spawn_counts[self.current_formation] >= self.enemies_per_formation:
                self.current_formation = (self.current_formation + 1) % len(self.formations)
            
            return x, y
        else:
            # Traditional single-point spawning for small waves
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                return 0, random.randint(0, self.world_h)
            elif side == 'right':
                return self.world_w, random.randint(0, self.world_h)
            elif side == 'top':
                return random.randint(0, self.world_w), 0
            else:
                return random.randint(0, self.world_w), self.world_h

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
            if self.enemies_to_spawn:
                if self.spawn_timer <= 0:
                    # Get spawn position
                    x, y = self.get_spawn_position()
                    
                    # Spawn the next enemy type in the list
                    enemy_type = self.enemies_to_spawn.pop(0)
                    
                    if enemy_type == "basic":
                        health = ENEMY_HEALTH_BASE * self.wave
                        if self.wave >= 3 and random.random() < MOTHERSHIP_SPAWN_CHANCE:
                            # Spawn mothership with higher health
                            mothership_health = health * MOTHERSHIP_HEALTH_MULTIPLIER
                            self.enemies.append(Mothership(x, y, mothership_health))
                        else:
                            # Spawn regular enemy
                            self.enemies.append(Enemy(x, y, health))
                    elif enemy_type == "large":
                        self.enemies.append(LargeShip(x, y))
                    elif enemy_type == "kamikaze":
                        self.enemies.append(KamikazeShip(x, y))
                    elif enemy_type == "assault":
                        self.enemies.append(AssaultShip(x, y))
                    elif enemy_type == "stealth":
                        self.enemies.append(StealthShip(x, y))
                    elif enemy_type == "cruiser":
                        self.enemies.append(HeavyCruiser(x, y))
                    
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

# New enemy types with point values
class LargeShip(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=200, speed=0.25, enemy_type="large")  # Reduced by 50% (was 0.5)
        self.radius = 15
        self.size = 25
        self.laser_range = 200
        self.laser_damage = 7  # Reduced by 50% (was 15)
        self.shot_cooldown = 90  # 1.5 seconds at 60fps
        self.points = 5  # Point value for wave generation
        
    def update(self, buildings, base_pos):
        super().update(buildings, base_pos)
        # Check if we can shoot at buildings
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown:
            # Find nearest building in range
            nearest_building = None
            min_dist = float('inf')
            
            for building in buildings:
                dist = math.hypot(building.x - self.x, building.y - self.y)
                if dist <= self.laser_range and dist < min_dist:
                    min_dist = dist
                    nearest_building = building
            
            if nearest_building:
                # Deal damage to building
                nearest_building.take_damage(self.laser_damage)
                self.last_shot_time = current_time
                # Store laser target for visual effects
                self.laser_target = nearest_building
            else:
                self.laser_target = None
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # Draw large blue rectangle ship
            rect_width = int(self.size * camera.zoom)
            rect_height = int(self.size * 0.6 * camera.zoom)
            rect = pygame.Rect(screen_x - rect_width//2, screen_y - rect_height//2, rect_width, rect_height)
            pygame.draw.rect(surface, (0, 100, 255), rect)  # Blue color
            pygame.draw.rect(surface, (0, 150, 255), rect, 2)  # Lighter blue border
            
            # Health bar
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = max(40, int(self.size * camera.zoom * 2))  # 2x larger
                bar_height = max(4, int(6 * camera.zoom))  # 2x larger
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - self.size - 8
                
                pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

class KamikazeShip(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=30, speed=1.25, enemy_type="kamikaze")  # Reduced by 50% (was 2.5)
        self.radius = 6
        self.size = 10
        self.damage = 50  # Reduced by 50% (was 100)
        self.points = 2  # Point value for wave generation
        self.has_exploded = False
        
    def update(self, buildings, base_pos):
        # Move toward nearest target aggressively
        if not self.target:
            self.find_nearest_target(buildings, base_pos)
        
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)
            
            if distance < 20 and not self.has_exploded:  # Close enough to explode
                self.explode_on_target()
            else:
                # Move toward target at high speed
                if distance > 0:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed
    
    def explode_on_target(self):
        """Explode and damage the target"""
        if self.target and hasattr(self.target, 'take_damage'):
            self.target.take_damage(self.damage)
        self.has_exploded = True
        self.health = 0  # Dies after explosion
        
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # Draw small red triangle (aggressive look)
            points = []
            for i in range(3):
                angle = i * 2 * math.pi / 3 + self.movement_angle
                px = screen_x + self.size * camera.zoom * math.cos(angle)
                py = screen_y + self.size * camera.zoom * math.sin(angle)
                points.append((px, py))
            
            pygame.draw.polygon(surface, (255, 50, 50), points)  # Bright red
            pygame.draw.polygon(surface, (255, 100, 100), points, 2)  # Lighter red border

class AssaultShip(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=120, speed=0.75, enemy_type="assault")
        self.radius = 12
        self.size = 18
        self.machine_gun_range = 150
        self.machine_gun_damage = 4  # Reduced by 50% (was 8)
        self.shot_cooldown = 30  # 0.5 seconds at 60fps - rapid fire
        self.points = 3  # Point value for wave generation
        self.burst_count = 0
        self.max_burst = 5  # Fire 5 shots per burst
        self.burst_pause = 120  # 2 second pause between bursts
        
    def update(self, buildings, base_pos):
        super().update(buildings, base_pos)
        # Rapid fire machine gun behavior
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown:
            # Find nearest building in range
            nearest_building = None
            min_dist = float('inf')
            
            for building in buildings:
                dist = math.hypot(building.x - self.x, building.y - self.y)
                if dist <= self.machine_gun_range and dist < min_dist:
                    min_dist = dist
                    nearest_building = building
            
            if nearest_building and self.burst_count < self.max_burst:
                # Deal damage to building
                nearest_building.take_damage(self.machine_gun_damage)
                self.last_shot_time = current_time
                self.laser_target = nearest_building
                self.burst_count += 1
            elif self.burst_count >= self.max_burst:
                # Reset burst after pause
                if current_time - self.last_shot_time > self.burst_pause:
                    self.burst_count = 0
                self.laser_target = None
            else:
                self.laser_target = None
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        screen_size = self.size * camera.zoom
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # Draw hexagonal assault ship (military look)
            points = []
            for i in range(6):
                angle = i * math.pi / 3 + self.movement_angle
                px = screen_x + self.size * camera.zoom * math.cos(angle)
                py = screen_y + self.size * camera.zoom * math.sin(angle)
                points.append((px, py))
            
            pygame.draw.polygon(surface, (150, 75, 0), points)  # Dark orange
            pygame.draw.polygon(surface, (200, 100, 0), points, 2)  # Orange border
            
            # Health bar
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = 40 * camera.zoom  # 2x larger
                bar_height = 8 * camera.zoom  # 2x larger
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - screen_size - 8 * camera.zoom
                
                # Create semi-transparent health bar
                health_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
                health_surface.fill((200, 0, 0, 127))
                surface.blit(health_surface, (bar_x, bar_y))
                
                green_width = max(1, int(bar_width * health_ratio))
                if green_width > 0:
                    green_surface = pygame.Surface((green_width, bar_height), pygame.SRCALPHA)
                    green_surface.fill((0, 200, 0, 127))
                    surface.blit(green_surface, (bar_x, bar_y))

class StealthShip(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=80, speed=1.0, enemy_type="stealth")
        self.radius = 8
        self.size = 12
        self.emp_range = 100
        self.emp_damage = 12  # Reduced by 50% (was 25) - Disables buildings temporarily
        self.shot_cooldown = 180  # 3 seconds between EMP bursts
        self.points = 4  # Point value for wave generation
        self.stealth_timer = 0
        self.is_cloaked = False
        self.cloak_duration = 120  # 2 seconds cloaked
        self.decloak_duration = 180  # 3 seconds visible
        
    def update(self, buildings, base_pos):
        super().update(buildings, base_pos)
        
        # Stealth cloaking behavior
        self.stealth_timer += 1
        if self.is_cloaked:
            if self.stealth_timer >= self.cloak_duration:
                self.is_cloaked = False
                self.stealth_timer = 0
        else:
            if self.stealth_timer >= self.decloak_duration:
                self.is_cloaked = True
                self.stealth_timer = 0
        
        # EMP weapon behavior
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown and not self.is_cloaked:
            # Find multiple buildings in range for EMP blast
            targets = []
            for building in buildings:
                dist = math.hypot(building.x - self.x, building.y - self.y)
                if dist <= self.emp_range:
                    targets.append(building)
            
            if targets:
                # Deal damage to all buildings in range
                for building in targets:
                    building.take_damage(self.emp_damage)
                self.last_shot_time = current_time
                self.laser_target = targets[0] if targets else None
            else:
                self.laser_target = None
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # Only draw if not fully cloaked
            alpha = 50 if self.is_cloaked else 255
            
            # Draw diamond-shaped stealth ship
            points = [
                (screen_x, screen_y - self.size * camera.zoom),
                (screen_x + self.size * camera.zoom * 0.7, screen_y),
                (screen_x, screen_y + self.size * camera.zoom),
                (screen_x - self.size * camera.zoom * 0.7, screen_y)
            ]
            
            if self.is_cloaked:
                # Semi-transparent when cloaked
                stealth_surface = pygame.Surface((self.size * 2 * camera.zoom, self.size * 2 * camera.zoom), pygame.SRCALPHA)
                adjusted_points = [(p[0] - screen_x + self.size * camera.zoom, p[1] - screen_y + self.size * camera.zoom) for p in points]
                pygame.draw.polygon(stealth_surface, (100, 0, 150, alpha), adjusted_points)
                surface.blit(stealth_surface, (screen_x - self.size * camera.zoom, screen_y - self.size * camera.zoom))
            else:
                pygame.draw.polygon(surface, (100, 0, 150), points)  # Purple
                pygame.draw.polygon(surface, (150, 50, 200), points, 2)  # Light purple border

class HeavyCruiser(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=300, speed=0.4, enemy_type="cruiser")
        self.radius = 18
        self.size = 30
        self.plasma_range = 250
        self.plasma_damage = 15  # Reduced by 50% (was 30)
        self.shot_cooldown = 150  # 2.5 seconds between shots
        self.points = 6  # Point value for wave generation
        self.charge_time = 90  # 1.5 seconds to charge plasma
        self.is_charging = False
        self.charge_start = 0
        
    def update(self, buildings, base_pos):
        super().update(buildings, base_pos)
        # Heavy plasma cannon behavior
        current_time = pygame.time.get_ticks()
        
        if not self.is_charging and current_time - self.last_shot_time > self.shot_cooldown:
            # Start charging if target in range
            nearest_building = None
            min_dist = float('inf')
            
            for building in buildings:
                dist = math.hypot(building.x - self.x, building.y - self.y)
                if dist <= self.plasma_range and dist < min_dist:
                    min_dist = dist
                    nearest_building = building
            
            if nearest_building:
                self.is_charging = True
                self.charge_start = current_time
                self.laser_target = nearest_building
        
        elif self.is_charging:
            if current_time - self.charge_start >= self.charge_time:
                # Fire charged plasma shot
                if self.laser_target and hasattr(self.laser_target, 'take_damage'):
                    self.laser_target.take_damage(self.plasma_damage)
                self.last_shot_time = current_time
                self.is_charging = False
                self.laser_target = None
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # Draw large rectangular cruiser
            rect_width = int(self.size * camera.zoom)
            rect_height = int(self.size * 0.6 * camera.zoom)
            
            # Main hull
            rect = pygame.Rect(screen_x - rect_width//2, screen_y - rect_height//2, rect_width, rect_height)
            pygame.draw.rect(surface, (80, 80, 120), rect)  # Dark blue-gray
            pygame.draw.rect(surface, (120, 120, 180), rect, 3)  # Light blue-gray border
            
            # Charging effect
            if self.is_charging:
                current_time = pygame.time.get_ticks()
                charge_progress = min(1.0, (current_time - self.charge_start) / self.charge_time)
                glow_size = int(rect_width * (0.5 + 0.5 * charge_progress))
                glow_color = (int(255 * charge_progress), int(100 * charge_progress), int(255 * charge_progress))
                pygame.draw.circle(surface, glow_color, (int(screen_x), int(screen_y)), glow_size, 2)
            
            # Health bar
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = max(60, int(self.size * camera.zoom * 2))  # 2x larger
                bar_height = max(6, int(8 * camera.zoom))  # 2x larger
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - self.size - 10
                
                pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height)) 