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
from buildings import Solar, Connector, Battery, Miner, Turret, Laser, SuperLaser, Repair, Converter, Hangar, MissileLauncher, ForceFieldGenerator, Building, FriendlyShip
from research import ResearchSystem
from power import PowerGrid
from enemies import WaveManager, MothershipMissile, LargeShip, KamikazeShip

# Additional constants that might be missing
try:
    MINING_RATE_SINGLE
except NameError:
    MINING_RATE_SINGLE = 3.0





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
    """Missile projectile with smart targeting and lifetime."""
    def __init__(self, x, y, target, damage, splash_radius=MISSILE_SPLASH_RADIUS):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.splash_radius = splash_radius
        self.speed = MISSILE_SPEED
        self.alive = True
        self.flash_timer = 0
        self.lifetime = 1800  # 30 seconds at 60fps
        self.retarget_cooldown = 0
        
    def update(self, game_logic):
        # Decrease lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            return
            
        # Decrease retarget cooldown
        if self.retarget_cooldown > 0:
            self.retarget_cooldown -= 1
        
        # Check if current target is still valid
        if (not self.target or 
            not hasattr(self.target, 'x') or 
            not hasattr(self.target, 'health') or 
            self.target.health <= 0):
            # Try to find new target if cooldown is over
            if self.retarget_cooldown <= 0:
                self._find_new_target(game_logic)
                self.retarget_cooldown = 30  # 0.5 second cooldown between retargets
        
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
    
    def _find_new_target(self, game_logic):
        """Find a new target within reasonable range."""
        max_retarget_range = 300  # Don't chase targets too far away
        closest_enemy = None
        closest_dist = float('inf')
        
        for enemy in game_logic.wave_manager.enemies:
            if hasattr(enemy, 'health') and enemy.health > 0:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < max_retarget_range and dist < closest_dist:
                    closest_enemy = enemy
                    closest_dist = dist
        
        if closest_enemy:
            self.target = closest_enemy
    
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


class HeavyMissile:
    """Heavy missile with splash damage."""
    def __init__(self, x, y, target_x, target_y, damage, splash_damage, splash_radius):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage
        self.splash_damage = splash_damage
        self.splash_radius = splash_radius
        self.speed = MISSILE_SPEED * 0.8  # Slower than regular missiles
        self.alive = True
        self.flash_timer = 0
        
    def update(self, game_logic):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        self.flash_timer += 1
        
        if dist < self.speed:
            # Explode at target location
            self.x, self.y = self.target_x, self.target_y
            self.alive = False
            
            # Deal splash damage to all enemies in radius
            for enemy in game_logic.wave_manager.enemies:
                enemy_dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if enemy_dist <= self.splash_radius:
                    # Direct hit does full damage, splash does splash_damage
                    damage_to_deal = self.damage if enemy_dist < 10 else self.splash_damage
                    enemy.health -= damage_to_deal
            
            # Missile explosion particles removed
            
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            # Heavy missile trail particles removed
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        if not (-50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50):
            return
        
        # Draw heavy missile as a larger glowing circle
        base_color = (255, 150, 0)  # Orange-yellow
        if self.flash_timer % 8 < 4:  # Flash effect
            color = (255, 255, 100)  # Bright yellow
        else:
            color = base_color
        
        size = max(2, int(MISSILE_SIZE * camera.zoom * 1.5))  # 50% larger than regular missiles
        pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), size)
        # Add outer glow
        if size > 2:
            pygame.draw.circle(surface, (255, 200, 100, 100), (int(screen_x), int(screen_y)), size + 2, 1)


class GameLogicSystem(System):
    """Main game logic system that manages all gameplay mechanics."""
    
    def __init__(self, camera, audio_system=None, particle_system=None):
        super().__init__("GameLogicSystem")
        self.camera = camera
        self.audio_system = audio_system
        self.particle_system = particle_system
        
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
        
        # Research system
        self.research_system = ResearchSystem()
        
        # Game objects
        self.power_grid = None
        self.wave_manager = None
        
        # Energy production tracking
        self.current_energy_production = 0.0
        self.solar_panel_count = 0
        self.solar_panel_levels = 0
        
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
            'hangar': Hangar,
            'missile_launcher': MissileLauncher,
            'force_field': ForceFieldGenerator
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
        self.wave_manager.update_enemies(self.buildings, self.friendly_ships)
        
        # Handle mothership missile attacks
        self._update_mothership_attacks()
        
        # Update missiles
        self._update_missiles()
        self._update_mothership_missiles()
        
        # Particle updates now handled by ParticleSystem
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
    
    def add_particles(self, x, y, count, color, speed_range=(0.1, 0.3), lifetime_range=(30, 60)):
        """Add particles at a position with random velocities."""
        if self.particle_system:
            self.particle_system.add_particles(x, y, count, color, speed_range, lifetime_range)
        else:
            # Fallback to old system if particle system not available
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
        elif data['type'] == 'cancel_selection':
            self.selected_build = None
            # Play cancel sound
            if self.audio_system:
                self.audio_system.play_ui_sound('button_click', 0.5)
        elif data['type'] == 'skip_wave':
            # Force the next wave to start immediately
            if self.wave_manager.can_start_next_wave:
                self.wave_manager.force_next_wave()
        elif data['type'] == 'select_at':
            self._select_building_at(data['x'], data['y'])
        elif data['type'] == 'upgrade' and data.get('building'):
            self._upgrade_building(data['building'])
        elif data['type'] == 'sell' and data.get('building'):
            self._sell_building(data['building'])
        elif data['type'] == 'toggle_disabled' and data.get('building'):
            self._toggle_building_disabled(data['building'])
        elif data['type'] == 'research' and data.get('research_id'):
            self._research_technology(data['research_id'])
        elif data['type'] == 'research_click':
            self._handle_research_click(data)
    
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
        
        # Apply research multipliers to new building
        self._apply_research_to_building(new_building)
        
        # Check distance to other buildings
        can_place = True
        conflict_reason = ""
        
        for existing in self.buildings:
            distance = math.sqrt((x - existing.x) ** 2 + (y - existing.y) ** 2)
            min_distance = new_building.radius + existing.radius + 0.5  # Reduced buffer by 75% for easier placement
            if distance < min_distance:
                can_place = False
                conflict_reason = f"Too close to {existing.type} (distance: {distance:.1f}, needed: {min_distance:.1f})"
                break
        
        # Check distance to base
        if can_place:
            base_distance = math.sqrt((x - self.base_pos[0]) ** 2 + (y - self.base_pos[1]) ** 2)
            min_base_distance = new_building.radius + BASE_RADIUS + 0.5  # Reduced buffer by 75% for easier placement
            if base_distance < min_base_distance:
                can_place = False
                conflict_reason = f"Too close to base (distance: {base_distance:.1f}, needed: {min_base_distance:.1f})"
        
        if can_place:
            self.buildings.append(new_building)
            # Update power grid immediately after adding a building
            self.power_grid.buildings = self.buildings
            self.selected_build = None
            
            # Play construction sound
            if self.audio_system:
                self.audio_system.play_ui_sound('place_building', 0.7)
            
            # Add construction effects
            if self.particle_system:
                self.particle_system.add_building_construction(x, y)
            else:
                # Fallback construction particles
                self.add_particles(x, y, 8, (100, 200, 255), speed_range=(1, 3), lifetime_range=(20, 40))
            
            print(f"✅ Placed {build_type} at ({x:.0f}, {y:.0f})")
        else:
            # Refund cost
            self.resources.add_minerals(cost)
            
            # Play error sound
            if self.audio_system:
                self.audio_system.play_ui_sound('error', 0.5)
            
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
    
    def _toggle_building_disabled(self, building):
        """Toggle the disabled state of a building."""
        if hasattr(building, 'disabled'):
            building.disabled = not building.disabled
            status = "disabled" if building.disabled else "enabled"
            print(f"🔄 {building.type.title()} {status}")
    
    def _research_technology(self, research_id):
        """Research a technology if possible."""
        success, cost = self.research_system.research(research_id, self.resources.minerals)
        if success:
            self.resources.minerals -= cost
            node = self.research_system.research_nodes[research_id]
            print(f"🔬 Researched: {node.name} (-{cost} minerals)")
            
            # Apply research effects to existing buildings
            self._apply_research_effects()
        else:
            node = self.research_system.research_nodes.get(research_id)
            if node:
                if self.resources.minerals < node.cost:
                    print(f"❌ Not enough minerals for {node.name}! Need {node.cost}, have {int(self.resources.minerals)}")
                else:
                    print(f"❌ Prerequisites not met for {node.name}")
    
    def _apply_research_effects(self):
        """Apply research effects to existing buildings and game state."""
        # Apply effects to all existing buildings
        for building in self.buildings:
            self._apply_research_to_building(building)
    
    def _apply_research_to_building(self, building):
        """Apply research effects to a specific building."""
        # Apply health multipliers
        health_multiplier = self.research_system.get_global_multiplier("building_health")
        if health_multiplier > 1.0:
            old_max_health = building.max_health
            building.max_health = old_max_health * health_multiplier
            # Scale current health proportionally if building is damaged
            if building.health < old_max_health:
                health_ratio = building.health / old_max_health
                building.health = building.max_health * health_ratio
            else:
                building.health = building.max_health
        
        # Apply hangar capacity bonuses (additive)
        if building.type == "hangar":
            capacity_bonus = self.research_system.get_building_multiplier("hangar", "capacity")
            # This is handled in the max_ships property dynamically
        
        # Apply miner max asteroids bonuses (additive)
        if building.type == "miner":
            max_asteroids_bonus = self.research_system.get_building_multiplier("miner", "max_asteroids")
            # This is handled dynamically in the mining logic
        
        # Apply connector connection bonuses (additive)
        if building.type == "connector":
            connections_bonus = self.research_system.get_building_multiplier("connector", "connections")
            # This is handled in the power grid system dynamically
    
    def _handle_research_click(self, data):
        """Handle research panel clicks to start research."""
        button_index = data.get('button_index', -1)
        available_research = self.research_system.get_available_research()
        
        if 0 <= button_index < len(available_research):
            research = available_research[button_index]
            self._research_technology(research.id)
    
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
        # Play explosion sound
        if self.audio_system:
            self.audio_system.play_explosion(0.8)
        
        # Enhanced explosion effects
        # Missile explosion particles removed
        
        # Splash damage to enemies
        for enemy in self.wave_manager.enemies:
            distance = math.sqrt((enemy.x - missile.x) ** 2 + (enemy.y - missile.y) ** 2)
            if distance < missile.splash_radius:
                enemy.health -= missile.damage
                if enemy.health <= 0:
                    self.score += SCORE_PER_KILL
                    self.kill_count += 1
                    self.resources.add_minerals(MINERALS_PER_KILL)
                    
                    # Enhanced death effects
                    if self.particle_system:
                        self.particle_system.add_explosion(enemy.x, enemy.y, intensity=0.7)
                    else:
                        self.add_particles(enemy.x, enemy.y, 20, (255, 150, 0), speed_range=(1, 3), lifetime_range=(15, 30))
    
    def _update_mothership_attacks(self):
        """Handle mothership missile attacks."""
        for enemy in self.wave_manager.enemies:
            if hasattr(enemy, 'is_mothership') and enemy.is_mothership:
                if enemy.fire_missile():
                    # Find target for missile
                    if isinstance(enemy.target, dict) and enemy.target.get('type') == 'base':
                        # Create a target object for the base
                        target = type('BaseTarget', (), {
                            'x': self.base_pos[0], 
                            'y': self.base_pos[1],
                            'health': 1  # Dummy health so missile doesn't retarget
                        })()
                    else:
                        target = enemy.target
                    
                    if target:
                        missile = MothershipMissile(enemy.x, enemy.y, target, MOTHERSHIP_MISSILE_DAMAGE)
                        self.mothership_missiles.append(missile)
    
    def _update_mothership_missiles(self):
        """Update mothership missiles."""
        for missile in self.mothership_missiles[:]:
            missile.update()
            if not missile.alive:
                # Handle explosion damage
                self._handle_mothership_missile_explosion(missile)
                self.mothership_missiles.remove(missile)
            elif not (0 <= missile.x <= WORLD_WIDTH and 0 <= missile.y <= WORLD_HEIGHT):
                # Remove if out of bounds
                self.mothership_missiles.remove(missile)
    
    def _handle_mothership_missile_explosion(self, missile):
        """Handle mothership missile explosion damage."""
        # Play explosion sound
        if self.audio_system:
            self.audio_system.play_explosion(0.8)
        
        # Splash damage to buildings
        for building in self.buildings:
            distance = math.sqrt((building.x - missile.x) ** 2 + (building.y - missile.y) ** 2)
            if distance < missile.splash_radius:
                building.take_damage(missile.damage)
                # Add damage number
                self.damage_numbers.append(DamageNumber(building.x, building.y - 15, -missile.damage, (255, 0, 0)))
        
        # Damage to base
        base_distance = math.sqrt((self.base_pos[0] - missile.x) ** 2 + (self.base_pos[1] - missile.y) ** 2)
        if base_distance < missile.splash_radius:
            self.base_health -= missile.damage
            self.damage_numbers.append(DamageNumber(self.base_pos[0], self.base_pos[1] - 20, -missile.damage, (255, 0, 0)))
        
        # Explosion particles
        if self.particle_system:
            self.particle_system.add_explosion(missile.x, missile.y, intensity=0.8)
        else:
            self.add_particles(missile.x, missile.y, 15, (255, 150, 0), speed_range=(2, 4), lifetime_range=(20, 40))
    
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
            for miner in [b for b in self.buildings if b.type == 'miner' and b.powered and not b.disabled]:
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
                            
                            # Mine from asteroid with research multipliers
                            base_mining_rate = MINING_RATE_SINGLE * miner.level
                            mining_rate_multiplier = self.research_system.get_building_multiplier("miner", "mining_rate")
                            mineral_income_multiplier = self.research_system.get_global_multiplier("mineral_income")
                            final_mining_rate = base_mining_rate * mining_rate_multiplier * mineral_income_multiplier
                            mine_amount = min(final_mining_rate, asteroid.minerals)
                            
                            if mine_amount > 0:
                                self.resources.add_minerals(mine_amount)
                                asteroid.minerals -= mine_amount
                                
                                # Minimal visual effects - just a few sparks at the laser hit point
                                if random.random() < 0.3:  # Only 30% chance for particles
                                    self.add_particles(laser.target_x, laser.target_y, 2, (255, 255, 100), speed_range=(0.015, 0.04), lifetime_range=(8, 12))
                                
                                # No damage numbers for mining
    
    def _update_building_systems(self):
        """Update building systems like repair and energy production."""
        # Energy production with visual effects and research multipliers
        energy_producing_buildings = [b for b in self.buildings if b.type == 'solar' and b.powered]
        
        # Apply research multipliers to energy production
        base_energy_prod = sum(b.prod_rate for b in energy_producing_buildings)
        solar_production_multiplier = self.research_system.get_building_multiplier("solar", "production")
        final_energy_prod = base_energy_prod * solar_production_multiplier
        
        self.current_energy_production = final_energy_prod * 60  # Convert to per-second rate
        
        # Store detailed solar panel information for UI
        self.solar_panel_count = len(energy_producing_buildings)
        self.solar_panel_levels = sum(b.level for b in energy_producing_buildings) if energy_producing_buildings else 0
        
        self.resources.add_energy(final_energy_prod)
        
        # Add passive mineral income from trade networks research
        passive_income = self.research_system.get_global_multiplier("passive_income")
        if passive_income > 1.0:
            # Convert passive_income from multiplier to actual income rate
            passive_rate = passive_income - 1.0  # Remove the base 1.0 multiplier
            self.resources.add_minerals(passive_rate / 60.0)  # Convert to per-frame rate
        
        # Add power pulse effects to producing solar panels
        if self.particle_system and energy_producing_buildings:
            # Occasionally show power generation effects
            import random
            for solar in energy_producing_buildings:
                if random.random() < 0.05:  # 5% chance per frame
                    self.particle_system.add_power_pulse(solar.x, solar.y)
        
        # Max energy from batteries and solar
        self.resources.max_energy = BASE_MAX_ENERGY + sum(
            b.storage for b in self.buildings 
            if b.type in ['battery', 'solar'] and b.powered
        )
        
        # Repair system
        for repair_building in [b for b in self.buildings if b.type == 'repair' and b.powered and not b.disabled]:
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
            if building.type == 'turret' and building.powered and not building.disabled:
                self._update_turret(building)
            elif building.type in ['laser', 'superlaser'] and building.powered and not building.disabled:
                self._update_laser(building)
            elif building.type == 'missile_launcher' and building.powered and not building.disabled:
                self._update_missile_launcher(building)
    
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
                
                # Calculate damage with research multipliers
                base_damage = turret.damage  # This uses the building's property
                damage_multiplier = self.research_system.get_global_multiplier("weapon_damage")
                turret_damage_multiplier = self.research_system.get_building_multiplier("turret", "damage")
                final_damage = base_damage * damage_multiplier * turret_damage_multiplier
                
                # Create missile
                missile = Missile(turret.x, turret.y, target, final_damage)
                self.missiles.append(missile)
                
                # Missile launch sound removed to prevent audio errors
                
                # Calculate cooldown with research multipliers
                base_cooldown = TURRET_COOLDOWN
                fire_rate_multiplier = self.research_system.get_building_multiplier("turret", "fire_rate")
                final_cooldown = base_cooldown / fire_rate_multiplier if fire_rate_multiplier > 0 else base_cooldown
                turret.cooldown_timer = final_cooldown
    
    def _update_laser(self, laser_building):
        """Update laser behavior."""
        if self.resources.energy >= (LASER_COST if laser_building.type == 'laser' else SUPERLASER_COST) * laser_building.level:
            # Find target
            target = None
            min_distance = float('inf')
            
            for enemy in self.wave_manager.enemies:
                distance = math.sqrt((laser_building.x - enemy.x) ** 2 + (laser_building.y - enemy.y) ** 2)
                # Use building's fire_range property which can be modified by research
                range_multiplier = self.research_system.get_building_multiplier("laser" if laser_building.type == "laser" else "superlaser", "range")
                base_range = LASER_RANGE if laser_building.type == 'laser' else SUPERLASER_RANGE
                effective_range = base_range * range_multiplier
                if distance < effective_range and distance < min_distance:
                    target = enemy
                    min_distance = distance
            
            if target:
                energy_cost = (LASER_COST if laser_building.type == 'laser' else SUPERLASER_COST) * laser_building.level
                
                # Calculate damage with research multipliers
                base_damage = laser_building.damage_per_frame  # This uses the building's property
                damage_multiplier = self.research_system.get_global_multiplier("weapon_damage")
                laser_damage_multiplier = self.research_system.get_building_multiplier("laser" if laser_building.type == "laser" else "superlaser", "damage")
                final_damage = base_damage * damage_multiplier * laser_damage_multiplier
                
                self.resources.spend_energy(energy_cost)
                target.health -= final_damage
                
                # Create laser beam effect
                if laser_building.type == 'laser':
                    laser_effect = LaserBeam(laser_building.x, laser_building.y, target.x, target.y, 
                                           (0, 150, 255), duration=8)  # Blue laser
                else:
                    laser_effect = LaserBeam(laser_building.x, laser_building.y, target.x, target.y, 
                                           (255, 50, 255), duration=12)  # Purple superlaser
                
                self.laser_beams.append(laser_effect)
                
                # Laser sound removed to prevent audio errors
                
                # Enhanced particle effects
                if self.particle_system:
                    laser_color = (0, 150, 255) if laser_building.type == 'laser' else (255, 50, 255)
                    self.particle_system.add_laser_impact(target.x, target.y, laser_color)
                else:
                    # Fallback to old particles
                    self.add_particles(target.x, target.y, 5, 
                                     (0, 0, 255) if laser_building.type == 'laser' else (255, 0, 255), 
                                     speed_range=(0.5, 1.5), lifetime_range=(10, 20))
    
    def _update_missile_launcher(self, launcher):
        """Update missile launcher behavior."""
        import pygame
        current_time = pygame.time.get_ticks()
        
        # Check if we can fire (cooldown and mineral cost)
        if (current_time - launcher.last_shot_time > launcher.fire_cooldown and 
            self.resources.minerals >= launcher.mineral_cost_per_shot):
            
            # Find target
            target = None
            min_distance = float('inf')
            
            for enemy in self.wave_manager.enemies:
                distance = math.hypot(enemy.x - launcher.x, enemy.y - launcher.y)
                if distance <= launcher.fire_range and distance < min_distance:
                    min_distance = distance
                    target = enemy
            
            if target:
                # Spend minerals
                self.resources.minerals -= launcher.mineral_cost_per_shot
                
                # Create heavy missile
                self.missiles.append(HeavyMissile(launcher.x, launcher.y, target.x, target.y, launcher.damage, launcher.splash_damage, launcher.splash_radius))
                launcher.last_shot_time = current_time
                
                # Missile launch sound removed to prevent audio errors
                
                # Missile launcher particles removed
    
    def _update_hangars(self):
        """Update hangar systems and ship launching."""
        import pygame
        current_time = pygame.time.get_ticks()
        
        for hangar in [b for b in self.buildings if b.type == 'hangar' and b.powered and not b.disabled]:
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
                
                # Calculate effective max ships with research multipliers
                base_max_ships = hangar.max_ships
                capacity_bonus = self.research_system.get_building_multiplier("hangar", "capacity")
                effective_max_ships = int(base_max_ships + capacity_bonus)
                
                # Check for ship regeneration (when ships have been destroyed)
                if (hangar.regen_timer <= 0 and 
                    len(hangar.deployed_ships) < effective_max_ships):
                    
                    # Regenerate a ship
                    ship = FriendlyShip(hangar.x, hangar.y, hangar)
                    hangar.deployed_ships.append(ship)
                    self.friendly_ships.append(ship)
                    hangar.regen_timer = hangar.regen_cooldown
                    
                    # Regeneration particles (different color to show it's regeneration)
                    self.add_particles(hangar.x, hangar.y, 12, (0, 255, 150), 
                                     speed_range=(2, 4), lifetime_range=(30, 60))
                
                # Try to launch ships if conditions are met (for initial deployment)
                elif (hangar.launch_timer <= 0 and 
                      len(hangar.deployed_ships) < effective_max_ships and
                      len(self.wave_manager.enemies) > 0):  # Only launch if there are enemies
                    
                    # Check if there are enemies within engagement range
                    enemies_in_range = any(
                        math.sqrt((e.x - hangar.x)**2 + (e.y - hangar.y)**2) <= hangar.ship_range
                        for e in self.wave_manager.enemies
                    )
                    
                    if enemies_in_range:
                        # Launch all available ships at once in formation
                        ships_to_launch = hangar.max_ships - len(hangar.deployed_ships)
                        
                        # Formation positions around hangar
                        formation_radius = 30
                        for i in range(ships_to_launch):
                            angle = (i / max(1, ships_to_launch)) * 2 * math.pi
                            offset_x = formation_radius * math.cos(angle)
                            offset_y = formation_radius * math.sin(angle)
                            
                            ship = FriendlyShip(hangar.x + offset_x, hangar.y + offset_y, hangar)
                            hangar.deployed_ships.append(ship)
                            self.friendly_ships.append(ship)
                        
                        hangar.launch_timer = hangar.launch_cooldown
                        
                        # Launch particles for all ships
                        self.add_particles(hangar.x, hangar.y, ships_to_launch * 4, (100, 150, 255), 
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
                    # Ship destroyed - add explosion effects
                    if self.particle_system:
                        self.particle_system.add_explosion(ship.x, ship.y, intensity=0.5)
                    else:
                        self.add_particles(ship.x, ship.y, 12, (255, 100, 0), 
                                         speed_range=(2, 5), lifetime_range=(20, 40))
                    
                    # Play explosion sound for ship destruction
                    if self.audio_system:
                        self.audio_system.play_explosion(0.4)
                    
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
            elif self.selected_building.type == 'missile_launcher':
                render_system.draw_range_indicator(self.selected_building.x, self.selected_building.y, 
                                                 self.selected_building.fire_range, (255, 150, 0, 100))
        
        # Draw enemies
        for enemy in self.wave_manager.enemies:
            enemy.draw(render_system.screen, render_system.camera)
        
        # Draw friendly ships
        for ship in self.friendly_ships:
            ship.draw(render_system.screen, render_system.camera)
        
        # Draw missiles
        for missile in self.missiles:
            missile.draw(render_system.screen, render_system.camera)
        
        # Draw mothership missiles
        for missile in self.mothership_missiles:
            missile.draw(render_system.screen, render_system.camera)
        
        # Old particle drawing removed - now using ParticleSystem
        
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
            'missile_launcher': (500, (255, 150, 0, 100)),  # Orange for missile launchers
        }
        
        if build_type in building_ranges:
            range_val, color = building_ranges[build_type]
            render_system.draw_range_indicator(x, y, range_val, color) 