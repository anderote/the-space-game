"""
Game logic system that manages core gameplay mechanics.
"""

import pygame
import random
import math
from game.core.system_manager import System
from game.core.event_system import EventType, event_system
from game.utils.math_utils import distance_squared

# Import original game components
from settings import *
from resources import ResourceManager
from asteroids import Asteroid, DamageNumber
from buildings import Solar, Connector, Battery, Miner, Turret, Laser, SuperLaser, Repair, Converter, Hangar, Building, FriendlyShip
from power import PowerGrid
from enemies import WaveManager, MothershipMissile, LargeShip, KamikazeShip

# Additional constants that might be missing
try:
    MINING_RATE_SINGLE
except NameError:
    MINING_RATE_SINGLE = 3.0


class Particle:
    """Particle for visual effects."""
    def __init__(self, x, y, vx, vy, color, lifetime, size=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.original_color = color
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        # Fade out over time
        fade_ratio = self.lifetime / self.max_lifetime
        self.color = (
            int(self.original_color[0] * fade_ratio),
            int(self.original_color[1] * fade_ratio), 
            int(self.original_color[2] * fade_ratio)
        )
    
    def draw(self, surface, camera):
        if self.lifetime > 0:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
                pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), int(self.size))


class LaserBeam:
    """Laser beam effect for combat lasers."""
    def __init__(self, start_x, start_y, target_x, target_y, color, duration=10):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.width = 3
        
    def update(self):
        self.duration -= 1
        return self.duration > 0
    
    def draw(self, surface, camera):
        if self.duration <= 0:
            return
            
        # Calculate screen positions
        start_screen_x, start_screen_y = camera.world_to_screen(self.start_x, self.start_y)
        target_screen_x, target_screen_y = camera.world_to_screen(self.target_x, self.target_y)
        
        # Fade effect based on remaining duration
        fade_ratio = self.duration / self.max_duration
        
        # Draw laser beam with glow effect
        beam_width = max(1, int(self.width * fade_ratio * camera.zoom))
        
        if beam_width > 0:
            # Outer glow
            glow_color = (*self.color, int(100 * fade_ratio))
            pygame.draw.line(surface, self.color, 
                           (start_screen_x, start_screen_y), 
                           (target_screen_x, target_screen_y), 
                           beam_width + 4)
            
            # Main beam
            main_color = (*self.color, int(200 * fade_ratio))
            pygame.draw.line(surface, self.color, 
                           (start_screen_x, start_screen_y), 
                           (target_screen_x, target_screen_y), 
                           beam_width)
            
            # Core beam (brighter)
            core_color = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
            pygame.draw.line(surface, core_color, 
                           (start_screen_x, start_screen_y), 
                           (target_screen_x, target_screen_y), 
                           max(1, beam_width // 2))


class MiningLaser:
    """Mining laser effect."""
    def __init__(self, start_x, start_y, target_x, target_y, duration=30):
        self.start_x = start_x
        self.start_y = start_y
        # Add small random offset to target position
        offset_radius = 15
        angle = random.uniform(0, 2 * math.pi)
        self.target_x = target_x + math.cos(angle) * random.uniform(0, offset_radius)
        self.target_y = target_y + math.sin(angle) * random.uniform(0, offset_radius)
        self.duration = duration
        self.max_duration = duration
        self.width = random.uniform(2, 4)  # Random beam width
        
    def update(self):
        self.duration -= 1
        return self.duration > 0
    
    def draw(self, surface, camera):
        if self.duration <= 0:
            return
            
        # Calculate screen positions
        start_screen_x, start_screen_y = camera.world_to_screen(self.start_x, self.start_y)
        target_screen_x, target_screen_y = camera.world_to_screen(self.target_x, self.target_y)
        
        # Fade effect based on remaining duration
        fade_ratio = self.duration / self.max_duration
        
        # Draw multiple beam layers for glow effect
        beam_width = int(self.width * fade_ratio * camera.zoom)
        if beam_width > 0:
            # Outer glow (wider, more transparent)
            glow_color = (50, 255, 150)
            pygame.draw.line(surface, glow_color, 
                           (start_screen_x, start_screen_y), 
                           (target_screen_x, target_screen_y), 
                           max(1, beam_width + 4))
            
            # Main beam
            main_color = (0, 255, 100)
            pygame.draw.line(surface, main_color, 
                           (start_screen_x, start_screen_y), 
                           (target_screen_x, target_screen_y), 
                           max(1, beam_width))
            
            # Inner core (brighter)
            core_color = (150, 255, 200)
            pygame.draw.line(surface, core_color, 
                           (start_screen_x, start_screen_y), 
                           (target_screen_x, target_screen_y), 
                           max(1, beam_width // 2))


class Missile:
    """Missile projectile."""
    def __init__(self, x, y, target, damage, splash_radius=MISSILE_SPLASH_RADIUS):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.splash_radius = splash_radius
        self.speed = MISSILE_SPEED
        self.alive = True
        self.flash_timer = 0
        
    def update(self, game_logic):
        if not self.target or not hasattr(self.target, 'x'):
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
        self.flash_timer += 1
        
        if dist < self.speed:
            self.x, self.y = self.target.x, self.target.y
            self.alive = False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            # Add trail particles
            if random.random() < 0.3:
                game_logic.add_particles(self.x, self.y, 1, (255, 200, 100), speed_range=(0.2, 0.8), lifetime_range=(8, 15))
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        if not (-50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50):
            return
        
        # Draw missile as a glowing circle with flash effect
        base_color = (255, 100, 0)  # Orange
        if self.flash_timer % 10 < 5:  # Flash effect
            color = (255, 200, 100)  # Brighter
        else:
            color = base_color
        
        size = max(1, int(MISSILE_SIZE * camera.zoom))
        pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), size)


class GameLogicSystem(System):
    """Main game logic system that manages all gameplay mechanics."""
    
    def __init__(self, camera):
        super().__init__("GameLogicSystem")
        self.camera = camera
        
        # Game state
        self.resources = ResourceManager()
        self.asteroids = []
        self.buildings = []
        self.missiles = []
        self.particles = []
        self.mining_lasers = []
        self.laser_beams = []
        self.damage_numbers = []
        self.enemy_lasers = []
        self.mothership_missiles = []
        self.friendly_ships = []  # Ships launched from hangars
        
        # Game objects
        self.power_grid = None
        self.wave_manager = None
        
        # Game state
        self.base_health = BASE_HEALTH
        self.base_pos = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.selected_building = None
        self.selected_build = None
        self.score = 0
        self.kill_count = 0
        self.global_mining_clock = 0
        self.game_over = False
        self.max_buildings_ever = 0
        
        # Building types
        self.build_types = {
            'solar': Solar,
            'connector': Connector,
            'battery': Battery,
            'miner': Miner,
            'turret': Turret,
            'laser': Laser,
            'superlaser': SuperLaser,
            'repair': Repair,
            'converter': Converter,
            'hangar': Hangar
        }
    
    def initialize(self):
        """Initialize the game logic system."""
        # Load asteroid images
        self._load_asteroid_images()
        
        # Initialize asteroids
        self.asteroids = self.spawn_asteroids()
        
        # Initialize power grid and wave manager
        self.power_grid = PowerGrid(self.buildings, self.base_pos)
        self.wave_manager = WaveManager(WORLD_WIDTH, WORLD_HEIGHT, self.base_pos)
        
        # Subscribe to events
        event_system.subscribe(EventType.BUILDING_PLACED, self._handle_building_event)
        
        print("Game logic system initialized!")
    
    def _load_asteroid_images(self):
        """Load asteroid images from the images folder."""
        import os
        
        # Load asteroid images organized by size type
        asteroid_images = {
            'small': [],
            'medium': [],
            'large': []
        }
        images_path = "images"
        
        if os.path.exists(images_path):
            for i in range(1, 5):  # asteroid_1.png to asteroid_4.png
                filename = f"asteroid_{i}.png"
                filepath = os.path.join(images_path, filename)
                if os.path.exists(filepath):
                    try:
                        base_image = pygame.image.load(filepath).convert_alpha()
                        
                        # Create different sizes and add to respective lists
                        small_image = pygame.transform.scale(base_image, (40, 40))
                        medium_image = pygame.transform.scale(base_image, (60, 60))
                        large_image = pygame.transform.scale(base_image, (80, 80))
                        
                        asteroid_images['small'].append(small_image)
                        asteroid_images['medium'].append(medium_image)
                        asteroid_images['large'].append(large_image)
                        
                        print(f"Loaded asteroid image: {filename}")
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")
        
        # Set the loaded images on the Asteroid class
        if any(asteroid_images.values()):
            Asteroid.asteroid_images = asteroid_images
            print(f"Loaded asteroid images - Small: {len(asteroid_images['small'])}, Medium: {len(asteroid_images['medium'])}, Large: {len(asteroid_images['large'])}")
        else:
            print("No asteroid images found, using default rendering")
    
    def update(self, dt):
        """Update all game logic."""
        if self.game_over:
            return
        
        # Update power grid
        self.power_grid.buildings = self.buildings
        self.power_grid.update()
        
        # Set selected status
        for b in self.buildings:
            b.selected = (b is self.selected_building)
        
        # Update wave manager
        self.wave_manager.update(self.buildings)
        self.wave_manager.update_enemies(self.buildings)
        
        # Update missiles
        self._update_missiles()
        
        # Update particles and effects
        self._update_particles()
        self._update_mining_lasers()
        self._update_laser_beams()
        self._update_damage_numbers()
        
        # Update mining system
        self._update_mining()
        
        # Update building systems
        self._update_building_systems()
        
        # Update friendly ships
        self._update_friendly_ships()
        
        # Remove destroyed buildings
        self._update_buildings()
        
        # Check game over conditions
        self._check_game_over()
        
        # Update max buildings counter
        self.max_buildings_ever = max(self.max_buildings_ever, len(self.buildings))
    
    def spawn_asteroids(self):
        """Spawn asteroids in the world."""
        asteroids = []
        
        # Create asteroid network centered around base
        base_distance = 200
        chain_length = 3
        num_chains = 8
        
        for chain in range(num_chains):
            base_angle = (chain / num_chains) * 2 * math.pi
            
            for cluster_idx in range(chain_length):
                distance = base_distance + (cluster_idx * 150)
                angle_variation = random.uniform(-0.3, 0.3)
                distance_variation = random.uniform(-50, 50)
                
                angle = base_angle + angle_variation
                actual_distance = distance + distance_variation
                
                cx = self.base_pos[0] + actual_distance * math.cos(angle)
                cy = self.base_pos[1] + actual_distance * math.sin(angle)
                
                cx = max(50, min(WORLD_WIDTH - 50, cx))
                cy = max(50, min(WORLD_HEIGHT - 50, cy))
                
                asteroids_per_cluster = random.randint(2, 3)
                for _ in range(asteroids_per_cluster):
                    ax = cx + random.uniform(-30, 30)
                    ay = cy + random.uniform(-30, 30)
                    
                    # Use radius instead of size string, assign image variant
                    radius = random.randint(20, 40)
                    minerals = random.randint(200, 800)
                    asteroid = Asteroid(ax, ay, radius, minerals)
                    # Image variant will be set automatically based on available images
                    asteroids.append(asteroid)
        
        # Add distant clumps
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(400, 600)
            cx = self.base_pos[0] + distance * math.cos(angle)
            cy = self.base_pos[1] + distance * math.sin(angle)
            
            cx = max(50, min(WORLD_WIDTH - 50, cx))
            cy = max(50, min(WORLD_HEIGHT - 50, cy))
            
            clump_size = random.randint(3, 5)
            for _ in range(clump_size):
                ax = cx + random.uniform(-40, 40)
                ay = cy + random.uniform(-40, 40)
                radius = random.randint(25, 45)
                minerals = random.randint(300, 1000)
                asteroid = Asteroid(ax, ay, radius, minerals)
                # Image variant will be set automatically based on available images
                asteroids.append(asteroid)
        
        return asteroids
    
    def add_particles(self, x, y, count, color, speed_range=(1, 3), lifetime_range=(30, 60)):
        """Add particles at a position with random velocities."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(*lifetime_range)
            size = random.uniform(1, 3)
            self.particles.append(Particle(x, y, vx, vy, color, lifetime, size))
    
    def _handle_building_event(self, event):
        """Handle building-related events."""
        data = event.data
        
        if data['type'] == 'place':
            self._place_building(data['building_type'], data['x'], data['y'])
        elif data['type'] == 'select':
            self.selected_build = data['building_type']
        elif data['type'] == 'select_at':
            self._select_building_at(data['x'], data['y'])
        elif data['type'] == 'upgrade' and data.get('building'):
            self._upgrade_building(data['building'])
        elif data['type'] == 'sell' and data.get('building'):
            self._sell_building(data['building'])
    
    def _place_building(self, build_type, x, y):
        """Place a building at the specified location."""
        if build_type not in self.build_types:
            print(f"Unknown building type: {build_type}")
            return
        
        cost = BUILD_COSTS[build_type]
        print(f"Attempting to place {build_type} at ({x:.0f}, {y:.0f}) - Cost: {cost}, Available: {self.resources.minerals}")
        
        if not self.resources.spend_minerals(cost):
            print(f"Not enough minerals! Need {cost}, have {self.resources.minerals}")
            return
        
        # Check for collisions
        new_building = self.build_types[build_type](x, y)
        
        # Check distance to other buildings
        can_place = True
        conflict_reason = ""
        
        for existing in self.buildings:
            distance = math.sqrt((x - existing.x) ** 2 + (y - existing.y) ** 2)
            min_distance = new_building.radius + existing.radius + 1.0  # Reduced buffer by 50% for easier placement
            if distance < min_distance:
                can_place = False
                conflict_reason = f"Too close to {existing.type} (distance: {distance:.1f}, needed: {min_distance:.1f})"
                break
        
        # Check distance to base
        if can_place:
            base_distance = math.sqrt((x - self.base_pos[0]) ** 2 + (y - self.base_pos[1]) ** 2)
            min_base_distance = new_building.radius + BASE_RADIUS + 1.0  # Reduced buffer by 50% for easier placement
            if base_distance < min_base_distance:
                can_place = False
                conflict_reason = f"Too close to base (distance: {base_distance:.1f}, needed: {min_base_distance:.1f})"
        
        if can_place:
            self.buildings.append(new_building)
            # Update power grid immediately after adding a building
            self.power_grid.buildings = self.buildings
            self.selected_build = None
            print(f"✅ Placed {build_type} at ({x:.0f}, {y:.0f})")
        else:
            # Refund cost
            self.resources.add_minerals(cost)
            print(f"❌ Cannot place {build_type}: {conflict_reason}")
    
    def _select_building_at(self, x, y):
        """Select a building at the specified world coordinates."""
        for building in self.buildings:
            distance = math.sqrt((x - building.x) ** 2 + (y - building.y) ** 2)
            if distance < building.radius:
                self.selected_building = building
                # Notify input system about selection change for hotkey handling
                event_system.emit(EventType.BUILDING_PLACED, {
                    'type': 'selection_changed', 
                    'building': building
                })
                return
        self.selected_building = None
        # Notify input system about deselection
        event_system.emit(EventType.BUILDING_PLACED, {
            'type': 'selection_changed', 
            'building': None
        })
    
    def _upgrade_building(self, building):
        """Upgrade the specified building."""
        if building.level >= MAX_LEVEL:
            return
        
        upgrade_cost = building.upgrade_cost(BUILD_COSTS[building.type])
        if self.resources.spend_minerals(upgrade_cost):
            building.level += 1
            building.max_health *= 1.2
            building.health = building.max_health
    
    def _sell_building(self, building):
        """Sell the specified building for 50% of its base cost."""
        if building in self.buildings:
            # Calculate sell price (50% of base cost)
            sell_price = int(0.5 * BUILD_COSTS[building.type])
            
            # Add minerals back to resources
            self.resources.add_minerals(sell_price)
            
            # Remove building from power grid
            self.power_grid.remove_building(building)
            
            # Remove from buildings list
            self.buildings.remove(building)
            
            # Clear selection if this was the selected building
            if self.selected_building == building:
                self.selected_building = None
            
            print(f"💰 Sold {building.type} for {sell_price} minerals")
    
    def _update_missiles(self):
        """Update all missiles."""
        for m in self.missiles[:]:
            m.update(self)
            if not m.alive:
                # Handle explosion
                self._handle_missile_explosion(m)
                self.missiles.remove(m)
            elif not (0 <= m.x <= WORLD_WIDTH and 0 <= m.y <= WORLD_HEIGHT):
                self.missiles.remove(m)
    
    def _handle_missile_explosion(self, missile):
        """Handle missile explosion damage."""
        # Explosion particles
        self.add_particles(missile.x, missile.y, 15, (255, 150, 0), speed_range=(2, 5), lifetime_range=(20, 35))
        
        # Splash damage to enemies
        for enemy in self.wave_manager.enemies:
            distance = math.sqrt((enemy.x - missile.x) ** 2 + (enemy.y - missile.y) ** 2)
            if distance < missile.splash_radius:
                enemy.health -= missile.damage
                if enemy.health <= 0:
                    self.score += SCORE_PER_KILL
                    self.kill_count += 1
                    self.resources.add_minerals(MINERALS_PER_KILL)
                    self.add_particles(enemy.x, enemy.y, 20, (255, 150, 0), speed_range=(1, 3), lifetime_range=(15, 30))
    
    def _update_particles(self):
        """Update all particles."""
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)
    
    def _update_mining_lasers(self):
        """Update mining laser effects."""
        for laser in self.mining_lasers[:]:
            if not laser.update():
                self.mining_lasers.remove(laser)
    
    def _update_laser_beams(self):
        """Update combat laser beam effects."""
        for beam in self.laser_beams[:]:
            if not beam.update():
                self.laser_beams.remove(beam)
    
    def _update_damage_numbers(self):
        """Update damage numbers."""
        for dn in self.damage_numbers[:]:
            dn.update()
            if dn.lifetime <= 0:
                self.damage_numbers.remove(dn)
    
    def _update_mining(self):
        """Update the mining system."""
        self.global_mining_clock += 1
        if self.global_mining_clock >= MINING_CLOCK_INTERVAL:
            self.global_mining_clock = 0
            
            # Mining logic (simplified version)
            for miner in [b for b in self.buildings if b.type == 'miner' and b.powered]:
                if self.resources.energy >= MINER_ZAP_ENERGY_COST:
                    # Find nearby asteroids
                    nearby_asteroids = []
                    for asteroid in self.asteroids:
                        if asteroid.minerals > 0:
                            dist_sq = (miner.x - asteroid.x) ** 2 + (miner.y - asteroid.y) ** 2
                            if dist_sq < MINER_RANGE ** 2:
                                nearby_asteroids.append((dist_sq, asteroid))
                    
                    # Sort by distance and take up to 5
                    nearby_asteroids.sort(key=lambda x: x[0])
                    target_asteroids = [a for _, a in nearby_asteroids[:MINER_MAX_TARGETS]]
                    
                    if target_asteroids:
                        self.resources.spend_energy(MINER_ZAP_ENERGY_COST)
                        
                        for asteroid in target_asteroids:
                            # Create mining laser
                            laser = MiningLaser(miner.x, miner.y, asteroid.x, asteroid.y, duration=45)
                            self.mining_lasers.append(laser)
                            
                            # Mine from asteroid
                            mining_rate = MINING_RATE_SINGLE * miner.level
                            mine_amount = min(mining_rate, asteroid.minerals)
                            
                            if mine_amount > 0:
                                self.resources.add_minerals(mine_amount)
                                asteroid.minerals -= mine_amount
                                
                                # Visual effects
                                self.add_particles(miner.x, miner.y, 3, (0, 255, 0), speed_range=(1, 3), lifetime_range=(12, 20))
                                self.add_particles(asteroid.x, asteroid.y, 2, (100, 200, 100), speed_range=(0.5, 2), lifetime_range=(10, 18))
                                self.add_particles(laser.target_x, laser.target_y, 5, (255, 255, 100), speed_range=(2, 4), lifetime_range=(20, 30))
                                
                                # Damage number
                                self.damage_numbers.append(DamageNumber(asteroid.x, asteroid.y - 20, mine_amount))
    
    def _update_building_systems(self):
        """Update building systems like repair and energy production."""
        # Energy production
        energy_prod = sum(b.prod_rate for b in self.buildings if b.type == 'solar' and b.powered)
        self.resources.add_energy(energy_prod)
        
        # Max energy from batteries and solar
        self.resources.max_energy = BASE_MAX_ENERGY + sum(
            b.storage for b in self.buildings 
            if b.type in ['battery', 'solar'] and b.powered
        )
        
        # Repair system
        for repair_building in [b for b in self.buildings if b.type == 'repair' and b.powered]:
            if self.resources.energy >= REPAIR_ENERGY_COST:
                repair_used = False
                
                # Repair other buildings
                for other in self.buildings:
                    if other != repair_building and other.health < other.max_health:
                        distance = math.sqrt((repair_building.x - other.x) ** 2 + (repair_building.y - other.y) ** 2)
                        if distance < repair_building.heal_range:
                            other.health = min(other.health + repair_building.heal_rate, other.max_health)
                            repair_used = True
                
                # Repair base
                if self.base_health < BASE_HEALTH:
                    distance = math.sqrt((repair_building.x - self.base_pos[0]) ** 2 + (repair_building.y - self.base_pos[1]) ** 2)
                    if distance < repair_building.heal_range:
                        self.base_health = min(self.base_health + repair_building.heal_rate, BASE_HEALTH)
                        repair_used = True
                
                if repair_used:
                    self.resources.spend_energy(REPAIR_ENERGY_COST)
        
        # Turret and laser systems
        self._update_combat_buildings()
        
        # Hangar systems
        self._update_hangars()
    
    def _update_combat_buildings(self):
        """Update turrets and lasers."""
        for building in self.buildings:
            if building.type == 'turret' and building.powered:
                self._update_turret(building)
            elif building.type in ['laser', 'superlaser'] and building.powered:
                self._update_laser(building)
    
    def _update_turret(self, turret):
        """Update turret behavior."""
        if not hasattr(turret, 'cooldown_timer'):
            turret.cooldown_timer = 0
        
        turret.cooldown_timer -= 1
        
        if turret.cooldown_timer <= 0:
            # Find target
            target = None
            min_distance = float('inf')
            
            for enemy in self.wave_manager.enemies:
                distance = math.sqrt((turret.x - enemy.x) ** 2 + (turret.y - enemy.y) ** 2)
                if distance < turret.fire_range and distance < min_distance:
                    target = enemy
                    min_distance = distance
            
            if target and self.resources.energy >= TURRET_ENERGY_COST and self.resources.minerals >= TURRET_MINERAL_COST:
                self.resources.spend_energy(TURRET_ENERGY_COST)
                self.resources.spend_minerals(TURRET_MINERAL_COST)
                
                # Create missile
                missile = Missile(turret.x, turret.y, target, TURRET_DAMAGE * turret.level)
                self.missiles.append(missile)
                
                turret.cooldown_timer = TURRET_COOLDOWN
    
    def _update_laser(self, laser_building):
        """Update laser behavior."""
        if self.resources.energy >= (LASER_COST if laser_building.type == 'laser' else SUPERLASER_COST) * laser_building.level:
            # Find target
            target = None
            min_distance = float('inf')
            
            for enemy in self.wave_manager.enemies:
                distance = math.sqrt((laser_building.x - enemy.x) ** 2 + (laser_building.y - enemy.y) ** 2)
                range_limit = LASER_RANGE if laser_building.type == 'laser' else SUPERLASER_RANGE
                if distance < range_limit and distance < min_distance:
                    target = enemy
                    min_distance = distance
            
            if target:
                energy_cost = (LASER_COST if laser_building.type == 'laser' else SUPERLASER_COST) * laser_building.level
                damage = (LASER_DAMAGE if laser_building.type == 'laser' else SUPERLASER_DAMAGE) * laser_building.level
                
                self.resources.spend_energy(energy_cost)
                target.health -= damage
                
                # Create laser beam effect
                if laser_building.type == 'laser':
                    laser_effect = LaserBeam(laser_building.x, laser_building.y, target.x, target.y, 
                                           (0, 150, 255), duration=8)  # Blue laser
                else:
                    laser_effect = LaserBeam(laser_building.x, laser_building.y, target.x, target.y, 
                                           (255, 50, 255), duration=12)  # Purple superlaser
                
                self.laser_beams.append(laser_effect)
                
                # Impact particles
                self.add_particles(target.x, target.y, 5, 
                                 (0, 0, 255) if laser_building.type == 'laser' else (255, 0, 255), 
                                 speed_range=(0.5, 1.5), lifetime_range=(10, 20))
    
    def _update_hangars(self):
        """Update hangar systems and ship launching."""
        import pygame
        current_time = pygame.time.get_ticks()
        
        for hangar in [b for b in self.buildings if b.type == 'hangar' and b.powered]:
            if self.resources.energy >= HANGAR_ENERGY_COST:
                self.resources.spend_energy(HANGAR_ENERGY_COST)
                
                # Initialize timers if they don't exist
                if not hasattr(hangar, 'launch_timer'):
                    hangar.launch_timer = 0
                if not hasattr(hangar, 'regen_timer'):
                    hangar.regen_timer = 0
                
                # Update timers
                hangar.launch_timer -= 1
                hangar.regen_timer -= 1
                
                # Check for ship regeneration (when ships have been destroyed)
                if (hangar.regen_timer <= 0 and 
                    len(hangar.deployed_ships) < hangar.max_ships):
                    
                    # Regenerate a ship
                    ship = FriendlyShip(hangar.x, hangar.y, hangar)
                    hangar.deployed_ships.append(ship)
                    self.friendly_ships.append(ship)
                    hangar.regen_timer = hangar.regen_cooldown
                    
                    # Regeneration particles (different color to show it's regeneration)
                    self.add_particles(hangar.x, hangar.y, 12, (0, 255, 150), 
                                     speed_range=(2, 4), lifetime_range=(30, 60))
                
                # Try to launch a ship if conditions are met (for initial deployment)
                elif (hangar.launch_timer <= 0 and 
                      len(hangar.deployed_ships) < hangar.max_ships and
                      len(self.wave_manager.enemies) > 0):  # Only launch if there are enemies
                    
                    # Check if there are enemies within engagement range
                    enemies_in_range = any(
                        math.sqrt((e.x - hangar.x)**2 + (e.y - hangar.y)**2) <= hangar.ship_range
                        for e in self.wave_manager.enemies
                    )
                    
                    if enemies_in_range:
                        # Launch a new ship
                        ship = FriendlyShip(hangar.x, hangar.y, hangar)
                        hangar.deployed_ships.append(ship)
                        self.friendly_ships.append(ship)
                        hangar.launch_timer = hangar.launch_cooldown
                        
                        # Launch particles
                        self.add_particles(hangar.x, hangar.y, 8, (100, 150, 255), 
                                         speed_range=(1, 3), lifetime_range=(20, 40))
    
    def _update_friendly_ships(self):
        """Update all friendly ships launched from hangars."""
        import pygame
        current_time = pygame.time.get_ticks()
        
        # Update each ship
        active_ships = []
        for ship in self.friendly_ships:
            # Check if ship is still alive and active
            still_active = ship.update(self.wave_manager.enemies, current_time)
            
            if still_active and ship.health > 0:
                active_ships.append(ship)
            else:
                # Ship was destroyed or returned to hangar
                if ship in ship.hangar.deployed_ships:
                    ship.hangar.deployed_ships.remove(ship)
                    
                if ship.health <= 0:
                    # Ship destroyed - add explosion particles
                    self.add_particles(ship.x, ship.y, 12, (255, 100, 0), 
                                     speed_range=(2, 5), lifetime_range=(20, 40))
                    
                    # Start regeneration timer if not already running
                    if ship.hangar.regen_timer <= 0:
                        ship.hangar.regen_timer = ship.hangar.regen_cooldown
        
        self.friendly_ships = active_ships
    
    def _update_buildings(self):
        """Update and remove destroyed buildings."""
        # Remove destroyed buildings
        destroyed_buildings = [b for b in self.buildings if b.health <= 0]
        for building in destroyed_buildings:
            self.add_particles(building.x, building.y, 20, (255, 100, 0), speed_range=(2, 6), lifetime_range=(30, 50))
            # Remove building from power grid
            self.power_grid.remove_building(building)
        
        self.buildings[:] = [b for b in self.buildings if b.health > 0]
        
        # Update power grid buildings list
        self.power_grid.buildings = self.buildings
        
        # Remove depleted asteroids
        self.asteroids[:] = [a for a in self.asteroids if a.minerals > 0]
    
    def _check_game_over(self):
        """Check for game over conditions."""
        if self.base_health <= 0 or (len(self.buildings) == 0 and self.max_buildings_ever > 0):
            self.game_over = True
            event_system.emit(EventType.GAME_OVER, {'score': self.score, 'kill_count': self.kill_count})
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.resources.reset()
        self.asteroids = self.spawn_asteroids()
        self.buildings.clear()
        self.missiles.clear()
        self.particles.clear()
        self.mining_lasers.clear()
        self.laser_beams.clear()
        self.damage_numbers.clear()
        self.friendly_ships.clear()
        
        self.wave_manager.wave = 1
        self.wave_manager.enemies.clear()
        self.wave_manager.wait_timer = WAVE_WAIT_TIME
        self.wave_manager.wave_active = False
        
        self.base_health = BASE_HEALTH
        self.selected_building = None
        self.selected_build = None
        self.score = 0
        self.kill_count = 0
        self.global_mining_clock = 0
        self.game_over = False
        self.max_buildings_ever = 0
        
        print("Game reset!")
    
    def draw_world_objects(self, render_system):
        """Draw all world objects using the render system."""
        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw(render_system.screen, render_system.camera.x, render_system.camera.y, render_system.camera.zoom)
        
        # Draw base
        render_system.draw_base(self.base_pos, BASE_RADIUS, self.base_health, BASE_HEALTH)
        
        # Draw power grid connections
        render_system.draw_power_connections(self.power_grid)
        
        # Draw building placement preview range
        if self.selected_build:
            mouse_x, mouse_y = render_system.camera.screen_to_world(*pygame.mouse.get_pos())
            self._draw_building_placement_range(render_system, self.selected_build, mouse_x, mouse_y)
        
        # Draw buildings with selection glow
        for building in self.buildings:
            # Draw selection glow for selected building
            if building is self.selected_building:
                screen_x, screen_y = render_system.camera.world_to_screen(building.x, building.y)
                glow_radius = int((building.radius + 10) * render_system.camera.zoom)
                
                # Pulsing glow effect
                pulse = (pygame.time.get_ticks() / 500) % 2
                pulse_intensity = 0.5 + 0.3 * abs(pulse - 1)
                
                # Create glow surface
                glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                glow_color = (100, 200, 255, int(100 * pulse_intensity))
                
                # Draw multiple glow rings
                for i in range(3):
                    ring_radius = glow_radius - i * 3
                    ring_alpha = int(glow_color[3] * (1 - i * 0.3))
                    if ring_radius > 0:
                        pygame.draw.circle(glow_surface, (*glow_color[:3], ring_alpha), 
                                         (glow_radius + 5, glow_radius + 5), ring_radius, 2 + i)
                
                render_system.screen.blit(glow_surface, (screen_x - glow_radius - 5, screen_y - glow_radius - 5))
            
            building.draw(render_system.screen, render_system.camera.x, render_system.camera.y, render_system.camera.zoom)
        
        # Draw range for selected building
        if self.selected_building:
            if self.selected_building.type == 'turret':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 self.selected_building.fire_range, (255, 0, 0, 100))
            elif self.selected_building.type == 'laser':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 self.selected_building.fire_range, (100, 200, 255, 100))
            elif self.selected_building.type == 'superlaser':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 self.selected_building.fire_range, (255, 100, 255, 100))
            elif self.selected_building.type == 'repair':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 self.selected_building.heal_range, (0, 255, 255, 100))
            elif self.selected_building.type == 'miner':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 MINER_RANGE, (0, 255, 0, 100))
            elif self.selected_building.type == 'hangar':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 self.selected_building.ship_range, (120, 120, 255, 100))
        
        # Draw enemies
        for enemy in self.wave_manager.enemies:
            enemy.draw(render_system.screen, render_system.camera)
        
        # Draw friendly ships
        for ship in self.friendly_ships:
            ship.draw(render_system.screen, render_system.camera)
        
        # Draw missiles
        for missile in self.missiles:
            missile.draw(render_system.screen, render_system.camera)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(render_system.screen, render_system.camera)
        
        # Draw mining lasers
        for laser in self.mining_lasers:
            laser.draw(render_system.screen, render_system.camera)
        
        # Draw combat laser beams
        for beam in self.laser_beams:
            beam.draw(render_system.screen, render_system.camera)
        
        # Draw damage numbers
        for dn in self.damage_numbers:
            dn.draw(render_system.screen, render_system.camera)
        
        # Draw minimap
        render_system.draw_minimap(self.asteroids, self.buildings, self.wave_manager.enemies, 
                                 self.base_pos, render_system.camera)
    
    def _draw_building_placement_range(self, render_system, build_type, x, y):
        """Draw range indicator for building being placed."""
        # Define ranges and colors for different building types
        building_ranges = {
            'turret': (TURRET_RANGE, (255, 0, 0, 100)),      # Red for turrets
            'laser': (LASER_RANGE, (100, 200, 255, 100)),    # Blue for lasers
            'superlaser': (SUPERLASER_RANGE, (255, 100, 255, 100)),  # Purple for superlasers
            'repair': (REPAIR_RANGE, (0, 255, 255, 100)),    # Cyan for repair
            'miner': (MINER_RANGE, (0, 255, 0, 100)),        # Green for miners
            'connector': (POWER_RANGE, (255, 255, 0, 100)),  # Yellow for connectors
            'hangar': (HANGAR_SHIP_RANGE, (120, 120, 255, 100)),  # Light blue for hangars
        }
        
        if build_type in building_ranges:
            range_val, color = building_ranges[build_type]
            render_system.draw_range_indicator(x, y, range_val, color) 