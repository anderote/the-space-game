"""
Main game loop and entry point for Space Game Clone.
"""
import pygame
import sys
from settings import *
from resources import ResourceManager
from asteroids import Asteroid, DamageNumber
from buildings import Solar, Connector, Battery, Miner, Turret, Laser, Repair, Converter, Building
from power import PowerGrid
from enemies import WaveManager, MothershipMissile
import random
import numpy as np
import math
from PIL import Image, ImageFilter, ImageEnhance
import pygame_gui

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Game Clone")
clock = pygame.time.Clock()

# Load asteroid images
try:
    asteroid_small_image = pygame.image.load("images/asteroid_small.png").convert_alpha()
    asteroid_medium_image = pygame.image.load("images/asteroid_medium.png").convert_alpha()
    asteroid_medium_2_image = pygame.image.load("images/asteroid_medium_2.png").convert_alpha()
    print("Asteroid images loaded successfully")
except pygame.error as e:
    print(f"Could not load asteroid images: {e}")
    # Fallback asteroid images
    asteroid_small_image = pygame.Surface((40, 40))
    asteroid_small_image.fill((100, 100, 100))
    asteroid_medium_image = pygame.Surface((60, 60))
    asteroid_medium_image.fill((100, 100, 100))
    asteroid_medium_2_image = pygame.Surface((60, 60))
    asteroid_medium_2_image.fill((120, 120, 120))

# Updated font sizes with lighter weight
font = pygame.font.SysFont(FONT_FAMILY, FONT_SIZE_LARGE)
hud_font = pygame.font.SysFont(FONT_FAMILY, FONT_SIZE_MEDIUM)
small_font = pygame.font.SysFont(FONT_FAMILY, FONT_SIZE_SMALL)

# Set asteroid images
from asteroids import Asteroid
Asteroid.asteroid_images = {
    'small': asteroid_small_image,
    'medium': [asteroid_medium_image, asteroid_medium_2_image],
    'large': asteroid_medium_image  # Use medium image for large asteroids since large images were removed
}

# Camera system
class Camera:
    def __init__(self):
        self.x = WORLD_WIDTH // 2  # Start at world center
        self.y = WORLD_HEIGHT // 2
        self.zoom = 1.0

    def update(self, keys):
        # Arrow key panning
        if keys[pygame.K_LEFT]:
            self.x -= CAMERA_SPEED / self.zoom
        if keys[pygame.K_RIGHT]:
            self.x += CAMERA_SPEED / self.zoom
        if keys[pygame.K_UP]:
            self.y -= CAMERA_SPEED / self.zoom
        if keys[pygame.K_DOWN]:
            self.y += CAMERA_SPEED / self.zoom

        # Keep camera within world bounds
        self.x = max(0, min(WORLD_WIDTH, self.x))
        self.y = max(0, min(WORLD_HEIGHT, self.y))

    def zoom_in(self):
        self.zoom = min(ZOOM_MAX, self.zoom + ZOOM_SPEED)

    def zoom_out(self):
        self.zoom = max(ZOOM_MIN, self.zoom - ZOOM_SPEED)

    def world_to_screen(self, world_x, world_y):
        screen_x = (world_x - self.x) * self.zoom + SCREEN_WIDTH // 2
        screen_y = (world_y - self.y) * self.zoom + SCREEN_HEIGHT // 2
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        world_x = (screen_x - SCREEN_WIDTH // 2) / self.zoom + self.x
        world_y = (screen_y - SCREEN_HEIGHT // 2) / self.zoom + self.y
        return world_x, world_y

camera = Camera()

# Initialize resources
resources = ResourceManager()

# Base node - position in world coordinates
BASE_POS = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

def spawn_asteroids():
    asteroids = []
    # Random number of clumps between 6-12
    num_clumps = random.randint(ASTEROID_CLUMPS_MIN, ASTEROID_CLUMPS_MAX)

    # Always spawn 2 clusters near base
    base_clusters = []
    for i in range(2):
        angle = i * np.pi + random.uniform(-0.5, 0.5)  # Opposite sides of base
        distance = random.randint(150, 250)  # Close to base
        cx = BASE_POS[0] + distance * np.cos(angle)
        cy = BASE_POS[1] + distance * np.sin(angle)
        # Keep within bounds
        cx = max(ASTEROID_MIN_DIST, min(WORLD_WIDTH - ASTEROID_MIN_DIST, cx))
        cy = max(ASTEROID_MIN_DIST, min(WORLD_HEIGHT - ASTEROID_MIN_DIST, cy))
        base_clusters.append((cx, cy))

    # Add remaining clusters randomly
    remaining_clusters = num_clumps - 2
    for _ in range(remaining_clusters):
        cx = random.randint(ASTEROID_MIN_DIST, WORLD_WIDTH - ASTEROID_MIN_DIST)
        cy = random.randint(ASTEROID_MIN_DIST, WORLD_HEIGHT - ASTEROID_MIN_DIST)
        base_clusters.append((cx, cy))

    # Generate asteroids in clusters
    for cx, cy in base_clusters:
        for _ in range(ASTEROIDS_PER_CLUMP):
            # Try multiple times to find a position that doesn't collide with base
            for attempt in range(10):
                offset_x = random.gauss(0, 80)
                offset_y = random.gauss(0, 80)
                asteroid_x = cx + offset_x
                asteroid_y = cy + offset_y
                
                # Check distance from base
                distance_from_base = ((asteroid_x - BASE_POS[0]) ** 2 + (asteroid_y - BASE_POS[1]) ** 2) ** 0.5
                if distance_from_base > (BASE_RADIUS + 50):  # 50 pixel buffer from base
                    asteroids.append(Asteroid(asteroid_x, asteroid_y))
                    break

    # Fill up to at least 15 asteroids
    while len(asteroids) < 15:
        cx, cy = random.choice(base_clusters)
        # Try multiple times to find a position that doesn't collide with base
        for attempt in range(10):
            offset_x = random.gauss(0, 80)
            offset_y = random.gauss(0, 80)
            asteroid_x = cx + offset_x
            asteroid_y = cy + offset_y
            
            # Check distance from base
            distance_from_base = ((asteroid_x - BASE_POS[0]) ** 2 + (asteroid_y - BASE_POS[1]) ** 2) ** 0.5
            if distance_from_base > (BASE_RADIUS + 50):  # 50 pixel buffer from base
                asteroids.append(Asteroid(asteroid_x, asteroid_y))
                break

    return asteroids

def draw_base(surface, pos, radius, health, max_health, camera):
    screen_x, screen_y = camera.world_to_screen(pos[0], pos[1])
    screen_radius = radius * camera.zoom

    # Don't draw if off screen
    if (screen_x < -screen_radius or screen_x > SCREEN_WIDTH + screen_radius or
        screen_y < -screen_radius or screen_y > SCREEN_HEIGHT + screen_radius):
        return

    # Shield glow effect when healthy
    health_ratio = health / max_health
    if health_ratio > 0.5:
        glow_time = pygame.time.get_ticks() / 1000.0
        glow_intensity = 0.3 + 0.4 * (0.5 + 0.5 * math.sin(glow_time * 1.5))
        glow_radius = int(screen_radius + 8 * glow_intensity)
        shield_color = (int(100 * glow_intensity), int(150 * glow_intensity), int(255 * glow_intensity))
        pygame.draw.circle(surface, shield_color, (int(screen_x), int(screen_y)), glow_radius)

    # Draw base as a large hexagon with enhanced appearance
    points = []
    for i in range(6):
        angle = i * 2 * np.pi / 6
        px = screen_x + screen_radius * np.cos(angle)
        py = screen_y + screen_radius * np.sin(angle)
        points.append((px, py))
    
    # Base color based on health
    if health_ratio > 0.7:
        base_color = (200, 200, 255)  # Light blue
    elif health_ratio > 0.3:
        base_color = (255, 255, 200)  # Light yellow
    else:
        base_color = (255, 200, 200)  # Light red
    
    pygame.draw.polygon(surface, base_color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, max(3, int(4 * camera.zoom)))
    
    # Health bar
    bar_width = screen_radius * 2
    pygame.draw.rect(surface, RED, (screen_x - bar_width/2, screen_y - screen_radius - 15*camera.zoom, bar_width, 8*camera.zoom))
    pygame.draw.rect(surface, GREEN, (screen_x - bar_width/2, screen_y - screen_radius - 15*camera.zoom, bar_width * health_ratio, 8*camera.zoom))

def draw_controls_ui(surface):
    # Controls bar background
    pygame.draw.rect(surface, (40, 40, 40), (0, 80, SCREEN_WIDTH, 50))  # Smaller height
    pygame.draw.rect(surface, (80, 80, 80), (0, 80, SCREEN_WIDTH, 2))

    # Building controls
    controls = [
        ('S - Solar', 'solar', BUILD_COSTS['solar']),
        ('C - Connector', 'connector', BUILD_COSTS['connector']),
        ('B - Battery', 'battery', BUILD_COSTS['battery']),
        ('M - Miner', 'miner', BUILD_COSTS['miner']),
        ('T - Turret', 'turret', BUILD_COSTS['turret']),
        ('L - Laser', 'laser', BUILD_COSTS['laser']),
        ('R - Repair', 'repair', BUILD_COSTS['repair']),
        ('V - Converter', 'converter', BUILD_COSTS['converter'])
    ]

    x_start = 10
    for i, (text, build_type, cost) in enumerate(controls):
        x = x_start + i * 190
        # Highlight if selected
        if selected_build == build_type:
            pygame.draw.rect(surface, (100, 100, 150), (x - 5, 82, 185, 46))

        # Text (smaller)
        control_text = small_font.render(text, True, WHITE)
        cost_text = small_font.render(f"Cost: {cost}", True, YELLOW)
        surface.blit(control_text, (x, 85))
        surface.blit(cost_text, (x, 105))

def draw_range_indicator(surface, world_x, world_y, range_val, camera, color=(255, 255, 255, 100)):
    screen_x, screen_y = camera.world_to_screen(world_x, world_y)
    screen_range = range_val * camera.zoom

    # Draw range circle
    if screen_range > 5:  # Only draw if visible
        pygame.draw.circle(surface, color[:3], (int(screen_x), int(screen_y)), int(screen_range), 2)

def draw_game_menu(surface):
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    # Menu box
    menu_width, menu_height = 400, 300
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    pygame.draw.rect(surface, (60, 60, 60), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(surface, WHITE, (menu_x, menu_y, menu_width, menu_height), 3)

    # Menu text
    title_text = font.render("Game Menu", True, WHITE)
    surface.blit(title_text, (menu_x + (menu_width - title_text.get_width()) // 2, menu_y + 50))

    # Menu options
    restart_text = hud_font.render("R - Restart Game", True, WHITE)
    surface.blit(restart_text, (menu_x + 50, menu_y + 120))

    resume_text = hud_font.render("ESC - Resume Game", True, WHITE)
    surface.blit(resume_text, (menu_x + 50, menu_y + 160))

    quit_text = hud_font.render("Q - Quit Game", True, WHITE)
    surface.blit(quit_text, (menu_x + 50, menu_y + 200))

# Game state
class Missile:
    def __init__(self, x, y, target, damage, splash_radius=MISSILE_SPLASH_RADIUS):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.splash_radius = splash_radius
        self.speed = MISSILE_SPEED
        self.alive = True
        self.angle = 0  # Track movement angle for rotation
        self.flash_timer = 0  # For flashing effect
        
    # Class variable for missile image
    missile_image = None

    def update(self):
        if not self.target or not hasattr(self.target, 'x'):
            self.alive = False
            return
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
        
        # Calculate angle for image rotation (missile points toward target)
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
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            # Flashing red dot - cycles between bright and dark red
            flash_cycle = (self.flash_timer // 4) % 2  # Flash every 4 frames
            if flash_cycle == 0:
                color = (255, 80, 80)  # Bright red
                glow_color = (255, 120, 120)
            else:
                color = (180, 0, 0)   # Dark red
                glow_color = (220, 60, 60)
            
            radius = max(3, int(MISSILE_SIZE * camera.zoom * 1.2))
            
            # Draw glow effect
            pygame.draw.circle(surface, glow_color, (int(screen_x), int(screen_y)), radius + 1)
            # Draw main projectile
            pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), radius)

# No missile image needed - using simple geometry

class Particle:
    def __init__(self, x, y, color, vx, vy, lifetime, size):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.size = size
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), max(1, int(self.size * camera.zoom)))

# Game variables
asteroids = spawn_asteroids()
base_health = BASE_HEALTH
buildings = []
build_types = {
    'solar': Solar,
    'connector': Connector,
    'battery': Battery,
    'miner': Miner,
    'turret': Turret,
    'laser': Laser,
    'repair': Repair,
    'converter': Converter
}
build_keys = {
    pygame.K_s: 'solar',
    pygame.K_c: 'connector',
    pygame.K_b: 'battery',
    pygame.K_m: 'miner',
    pygame.K_t: 'turret',
    pygame.K_l: 'laser',
    pygame.K_r: 'repair',
    pygame.K_v: 'converter'
}
selected_build = None
selected_building = None

missiles = []
particles = []
enemy_lasers = []
damage_numbers = []
kill_count = 0  # Track total kills
global_mining_clock = 0  # Global clock for synchronized mining
mothership_missiles = []  # Track mothership missiles

powerups = {
    'slow_time': {'name': 'Slow Time', 'active': False, 'timer': 0},
    'speed_mining': {'name': 'Speed Mining', 'active': False, 'timer': 0},
    'speed_shooting': {'name': 'Speed Shooting', 'active': False, 'timer': 0}
}
powerup_buttons = {}
powerup_keys = list(powerups.keys())
for i, key in enumerate(powerup_keys):
    rect = pygame.Rect(SCREEN_WIDTH // 2 - 180 + i * 120, SCREEN_HEIGHT - 60, 110, 40)  # Smaller
    powerup_buttons[key] = rect

game_over = False
show_menu = False
max_buildings_ever = 0
score = 0
high_score = 0

def reset_game():
    global buildings, asteroids, wave_manager, base_health, resources, missiles, particles, damage_numbers, selected_building, selected_build, game_over, max_buildings_ever, score, powerups, camera, kill_count, global_mining_clock, mothership_missiles
    buildings.clear()
    asteroids[:] = spawn_asteroids()
    wave_manager.wave = 1
    wave_manager.enemies.clear()
    wave_manager.wait_timer = WAVE_WAIT_TIME
    wave_manager.wave_active = False
    base_health = BASE_HEALTH
    resources.reset()
    missiles.clear()
    particles.clear()
    damage_numbers.clear()
    mothership_missiles.clear()
    selected_building = None
    selected_build = None
    game_over = False
    max_buildings_ever = 0
    score = 0
    kill_count = 0
    global_mining_clock = 0
    camera.x = WORLD_WIDTH // 2
    camera.y = WORLD_HEIGHT // 2
    camera.zoom = 1.0
    for pu in powerups.values():
        pu['active'] = False
        pu['timer'] = 0

power_grid = PowerGrid(buildings, BASE_POS)
wave_manager = WaveManager(WORLD_WIDTH, WORLD_HEIGHT, BASE_POS)

# No image assignments needed - using simple geometry

running = True
paused = False

while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_ESCAPE:
                if selected_build:  # Exit build mode if in build mode
                    selected_build = None
                else:
                    show_menu = not show_menu
            elif show_menu:
                if event.key == pygame.K_r:
                    reset_game()
                    show_menu = False
                elif event.key == pygame.K_q:
                    running = False
            else:
                if event.key in build_keys:
                    selected_build = build_keys[event.key]
                if event.key == pygame.K_u and selected_building:
                    cost = selected_building.upgrade_cost(BUILD_COSTS[selected_building.type])
                    if resources.minerals >= cost and selected_building.level < MAX_LEVEL:
                        resources.spend_minerals(cost)
                        selected_building.upgrade()
                if event.key == pygame.K_x and selected_building:  # X key for sell
                    # Sell for (0.5 + level) * build_cost
                    sell_price = int((0.5 + selected_building.level) * BUILD_COSTS[selected_building.type])
                    resources.add_minerals(sell_price)
                    buildings.remove(selected_building)
                    selected_building = None
                if event.key == pygame.K_n and wave_manager.can_start_next_wave:  # N key for next wave
                    wave_manager.force_next_wave()
        elif event.type == pygame.MOUSEWHEEL:
            # Zoom with mouse wheel
            if event.y > 0:
                camera.zoom_in()
            else:
                camera.zoom_out()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_menu:
                continue
            if selected_build and not paused and not game_over:
                mx, my = pygame.mouse.get_pos()
                world_x, world_y = camera.screen_to_world(mx, my)
                # Keep within world bounds
                if 0 <= world_x <= WORLD_WIDTH and 0 <= world_y <= WORLD_HEIGHT:
                    cost = BUILD_COSTS[selected_build]
                    if resources.minerals >= cost:
                        # Check for collisions with existing buildings
                        building_collision = False
                        new_building = build_types[selected_build](world_x, world_y)
                        for existing in buildings:
                            distance = ((world_x - existing.x) ** 2 + (world_y - existing.y) ** 2) ** 0.5
                            if distance < (new_building.radius + existing.radius + 1.4):  # 30% smaller buffer
                                building_collision = True
                                break
                        
                        # Check for collisions with asteroids (70% smaller zone)
                        asteroid_collision = False
                        for asteroid in asteroids:
                            distance = ((world_x - asteroid.x) ** 2 + (world_y - asteroid.y) ** 2) ** 0.5
                            if distance < (new_building.radius + asteroid.radius + 0.6):  # 70% smaller buffer
                                asteroid_collision = True
                                break
                        
                        # Check collision with base
                        base_distance = ((world_x - BASE_POS[0]) ** 2 + (world_y - BASE_POS[1]) ** 2) ** 0.5
                        base_collision = base_distance < (new_building.radius + BASE_RADIUS + 2)
                        
                        # Only place if no collisions
                        if not building_collision and not asteroid_collision and not base_collision:
                            buildings.append(new_building)
                            resources.spend_minerals(cost)
                            selected_build = None
            elif not paused and not game_over:
                # Select building or click asteroid
                mx, my = pygame.mouse.get_pos()
                world_x, world_y = camera.screen_to_world(mx, my)
                selected_building = None

                # Check buildings first
        for b in buildings:
                    if (b.x - world_x) ** 2 + (b.y - world_y) ** 2 < (b.radius * 2) ** 2:
                        selected_building = b
                        break

                # If no building selected, check asteroids
                if not selected_building:
                    for a in asteroids:
                        if (a.x - world_x) ** 2 + (a.y - world_y) ** 2 < (a.radius * 1.5) ** 2:
                            a.clicked()
                            break
                # Powerup buttons
                for key, rect in powerup_buttons.items():
                    if rect.collidepoint(mx, my) and not powerups[key]['active'] and resources.energy >= POWERUP_COST:
                        resources.spend_energy(POWERUP_COST)
                        powerups[key]['active'] = True
                        powerups[key]['timer'] = POWERUP_DURATION
            if game_over:
                mx, my = pygame.mouse.get_pos()
                restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 40, 160, 50)
                if restart_rect.collidepoint(mx, my):
                    reset_game()

    if not paused and not game_over and not show_menu:
        # Update camera
        camera.update(keys)

        # Update power grid
        power_grid.buildings = buildings
        power_grid.update()
        # Set selected status
        for b in buildings:
            b.selected = (b is selected_building)
        # Update enemy waves
        wave_manager.update(buildings)
        wave_manager.update_enemies(buildings)

        # Mothership missile attacks
        for enemy in wave_manager.enemies:
            if hasattr(enemy, 'is_mothership') and enemy.is_mothership:
                if enemy.fire_missile():
                    # Find target for missile
                    if isinstance(enemy.target, dict) and enemy.target['type'] == 'base':
                        target = type('obj', (object,), {'x': BASE_POS[0], 'y': BASE_POS[1]})()
            else:
                        target = enemy.target
                    mothership_missiles.append(MothershipMissile(enemy.x, enemy.y, target, MOTHERSHIP_MISSILE_DAMAGE))

        # Update mothership missiles
        for m in mothership_missiles[:]:
            m.update()
            if not m.alive:
                # Splash damage to buildings
                for b in buildings:
                    if (b.x - m.x) ** 2 + (b.y - m.y) ** 2 < m.splash_radius ** 2:
                        b.health -= m.damage
                        damage_numbers.append(DamageNumber(b.x, b.y - 15, -m.damage, (255, 0, 0)))
                # Damage to base
                if (BASE_POS[0] - m.x) ** 2 + (BASE_POS[1] - m.y) ** 2 < m.splash_radius ** 2:
                    base_health -= m.damage
                    damage_numbers.append(DamageNumber(BASE_POS[0], BASE_POS[1] - 20, -m.damage, (255, 0, 0)))
                # Explosion particles
                for _ in range(15):
                    particles.append(Particle(m.x, m.y, random.choice([YELLOW,ORANGE,RED]), random.uniform(-4,4), random.uniform(-4,4), random.randint(20,40), random.randint(3,6)))
                mothership_missiles.remove(m)
        else:
                # Remove if out of bounds
                if not (0 <= m.x <= WORLD_WIDTH and 0 <= m.y <= WORLD_HEIGHT):
                    mothership_missiles.remove(m)

        # Enemy attacks
        enemy_lasers.clear()
        for enemy in wave_manager.enemies:
            # Target info
            if isinstance(enemy.target, dict) and enemy.target['type'] == 'base':
                tx, ty = BASE_POS
                t_radius = BASE_RADIUS
            else:
                tx, ty = enemy.target.x, enemy.target.y
                t_radius = enemy.target.radius
            dist = ((enemy.x - tx) ** 2 + (enemy.y - ty) ** 2) ** 0.5
            # Laser attack
            if dist < ENEMY_LASER_RANGE:
                # Store laser for drawing
                enemy_lasers.append((enemy.x, enemy.y, tx, ty))
                # Damage
                if isinstance(enemy.target, dict) and enemy.target['type'] == 'base':
                    base_health -= ENEMY_LASER_DAMAGE
                    base_health = max(base_health, 0)
                else:
                    enemy.target.health -= ENEMY_LASER_DAMAGE
            # Contact damage
            if dist < enemy.radius + t_radius:
                if isinstance(enemy.target, dict) and enemy.target['type'] == 'base':
                    base_health -= ENEMY_CONTACT_DAMAGE
                    base_health = max(base_health, 0)
                else:
                    enemy.target.health -= ENEMY_CONTACT_DAMAGE

        # Powerup effects
        enemy_speed_mult = 0.5 if powerups['slow_time']['active'] else 1
        mining_mult = 2 if powerups['speed_mining']['active'] else 1
        shooting_mult = 0.5 if powerups['speed_shooting']['active'] else 1

        # Turrets fire missiles
        for b in buildings:
            if (b.type == 'turret' and b.powered and
                resources.energy >= TURRET_ENERGY_COST and
                resources.minerals >= TURRET_MINERAL_COST):
                if not hasattr(b, 'cooldown_timer'):
                    b.cooldown_timer = 0
                if b.cooldown_timer > 0:
                    b.cooldown_timer -= 1
                else:
                    # Find nearest enemy in range
                    nearest = None
                    min_dist = float('inf')
                    for e in wave_manager.enemies:
                        d = (b.x - e.x) ** 2 + (b.y - e.y) ** 2
                        if d < b.fire_range ** 2 and d < min_dist:
                            nearest = e
                            min_dist = d
                    if nearest:
                        missiles.append(Missile(b.x, b.y, nearest, b.damage))
                        resources.spend_energy(TURRET_ENERGY_COST)
                        resources.spend_minerals(TURRET_MINERAL_COST)
                        b.cooldown_timer = int(b.cooldown_time * shooting_mult)
        # Lasers deal continuous damage
        for b in buildings:
            laser_cost = LASER_COST * b.level
            if b.type == 'laser' and b.powered and resources.energy >= laser_cost:
                # Find nearest enemy in range
                nearest = None
                min_dist = float('inf')
                for e in wave_manager.enemies:
                    d = (b.x - e.x) ** 2 + (b.y - e.y) ** 2
                    if d < b.fire_range ** 2 and d < min_dist:
                        nearest = e
                        min_dist = d
                if nearest:
                    damage_dealt = b.damage_per_frame * (2 if powerups['speed_shooting']['active'] else 1)
                    resources.spend_energy(laser_cost)
                    nearest.health -= damage_dealt

                    # Add damage counter at enemy location
                    damage_numbers.append(DamageNumber(nearest.x, nearest.y - 15, -damage_dealt, (255, 100, 100)))

                    # Store laser for visual drawing (will be drawn in render section)
                    if not hasattr(b, 'laser_target'):
                        b.laser_target = None
                    b.laser_target = nearest

                    # Laser particles at enemy location
                    for _ in range(2):
                        particles.append(Particle(nearest.x + random.uniform(-8, 8), nearest.y + random.uniform(-8, 8), CYAN, random.uniform(-1,1), random.uniform(-1,1), 10, 2))
                else:
                    if hasattr(b, 'laser_target'):
                        b.laser_target = None
        # Update missiles
        for m in missiles[:]:
            m.update()
            if not m.alive:
                # Splash damage
                for e in wave_manager.enemies:
                    if (e.x - m.x) ** 2 + (e.y - m.y) ** 2 < m.splash_radius ** 2:
                        e.health -= m.damage

                        # Add damage counter at enemy location
                        damage_numbers.append(DamageNumber(e.x, e.y - 15, -m.damage, (255, 150, 0)))

                        # XP gain for turret (reduced rate)
                        for b in buildings:
                            if b.type == 'turret' and hasattr(b, 'cooldown_timer'):
                                if hasattr(b, 'xp'):
                                    b.gain_xp(XP_PER_KILL * TURRET_XP_MODIFIER)
                        if e.health <= 0:
                            # Score, minerals, particles
                            score += SCORE_PER_KILL
                            kill_count += 1  # Increment kill counter
                            resources.add_minerals(MINERALS_PER_KILL)
                            for _ in range(20):
                                particles.append(Particle(e.x, e.y, random.choice([YELLOW,ORANGE,RED]), random.uniform(-3,3), random.uniform(-3,3), random.randint(15,30), random.randint(2,4)))
                missiles.remove(m)
            else:
                # Remove if out of bounds
                if not (0 <= m.x <= WORLD_WIDTH and 0 <= m.y <= WORLD_HEIGHT):
                missiles.remove(m)
        # Remove dead enemies
        for e in wave_manager.enemies[:]:
            if e.health <= 0:
                score += SCORE_PER_KILL
                kill_count += 1  # Increment kill counter for all enemy deaths
                resources.add_minerals(MINERALS_PER_KILL)
                for _ in range(20):
                    particles.append(Particle(e.x, e.y, random.choice([YELLOW,ORANGE,RED]), random.uniform(-3,3), random.uniform(-3,3), random.randint(15,30), random.randint(2,4)))
                wave_manager.enemies.remove(e)
        # Score for wave
        if not wave_manager.wave_active and not wave_manager.enemies:
            score += SCORE_PER_WAVE * (wave_manager.wave-1)
        # Update particles
        for p in particles[:]:
            p.update()
            if p.lifetime <= 0:
                particles.remove(p)

        # Update damage numbers
        for dn in damage_numbers[:]:
            dn.update()
            if dn.lifetime <= 0:
                damage_numbers.remove(dn)
        # Remove destroyed buildings
        buildings[:] = [b for b in buildings if b.health > 0]
        # Energy production from solars
        prod = sum(b.prod_rate for b in buildings if b.type == 'solar' and b.powered)
        resources.add_energy(prod)
        # Max energy from batteries
        resources.max_energy = BASE_MAX_ENERGY + sum(b.storage for b in buildings if b.type == 'battery' and b.powered)
        # Synchronized Mining System
        global_mining_clock += 1
        if global_mining_clock >= MINING_CLOCK_INTERVAL:
            global_mining_clock = 0  # Reset clock

            # Track which asteroids are being mined and by how many miners
            asteroid_miners = {}  # asteroid -> list of miners
            asteroid_total_mined = {}  # asteroid -> total amount mined

            # First pass: identify all miner-asteroid relationships
            for b in buildings:
                if b.type == 'miner' and b.powered and resources.energy >= MINER_ZAP_ENERGY_COST:
                    # Find asteroids in range
                    nearby_asteroids = []
                    for a in asteroids:
                        d = (b.x - a.x) ** 2 + (b.y - a.y) ** 2
                        if d < MINER_RANGE ** 2 and a.minerals > 0:
                            nearby_asteroids.append((d, a))

                    # Sort by distance and take up to 3
                    nearby_asteroids.sort(key=lambda x: x[0])
                    target_asteroids = [a for _, a in nearby_asteroids[:MINER_MAX_TARGETS]]

                    # Register this miner for each target asteroid
                    for asteroid in target_asteroids:
                        if asteroid not in asteroid_miners:
                            asteroid_miners[asteroid] = []
                            asteroid_total_mined[asteroid] = 0
                        asteroid_miners[asteroid].append(b)

            # Second pass: calculate mining amounts and apply effects
            miners_that_worked = []  # Changed from set to list
            for asteroid, miners in asteroid_miners.items():
                if asteroid.minerals <= 0:
                    continue

                total_mined_from_asteroid = 0
                for miner in miners:
                    # Determine mining rate based on how many asteroids this miner targets
                    miner_target_count = sum(1 for a in asteroid_miners.keys() if miner in asteroid_miners[a])
                    if miner_target_count == 1:
                        mining_rate = MINING_RATE_SINGLE * miner.level * mining_mult
                    else:
                        mining_rate = MINING_RATE_MULTI * miner.level * mining_mult

                    # Mine from this asteroid
                    mine_amount = min(mining_rate, asteroid.minerals - total_mined_from_asteroid)
                    if mine_amount > 0:
                        resources.add_minerals(mine_amount)
                        total_mined_from_asteroid += mine_amount
                        if miner not in miners_that_worked:  # Avoid duplicates
                            miners_that_worked.append(miner)

                        # Create particle effects from miner
                        for _ in range(2):  # Fewer particles per miner
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(1, 3)
                            particles.append(Particle(
                                miner.x + random.uniform(-5, 5),
                                miner.y + random.uniform(-5, 5),
                                GREEN,
                                speed * math.cos(angle),
                                speed * math.sin(angle),
                                15,
                                random.randint(2, 4)
                            ))

                # Update asteroid minerals and create single damage counter
                if total_mined_from_asteroid > 0:
                    asteroid.minerals -= total_mined_from_asteroid
                    damage_numbers.append(DamageNumber(asteroid.x, asteroid.y - 20, total_mined_from_asteroid))

            # Consume energy from miners that worked
            for miner in miners_that_worked:
                resources.spend_energy(MINER_ZAP_ENERGY_COST)
        # Repair nodes
        for b in buildings:
            if b.type == 'repair' and b.powered and resources.energy >= REPAIR_ENERGY_COST:
                repair_used = False
                for other in buildings:
                    if other != b and (b.x - other.x) ** 2 + (b.y - other.y) ** 2 < b.heal_range ** 2 and other.health < other.max_health:
                        other.health = min(other.health + b.heal_rate, other.max_health)
                        repair_used = True
                if (b.x - BASE_POS[0]) ** 2 + (b.y - BASE_POS[1]) ** 2 < b.heal_range ** 2 and base_health < BASE_HEALTH:
                    base_health = min(base_health + b.heal_rate, BASE_HEALTH)
                    repair_used = True
                if repair_used:
                    resources.spend_energy(REPAIR_ENERGY_COST)
        # Converter logic
        for b in buildings:
            if b.type == 'converter' and b.powered:
                if not hasattr(b, 'convert_timer'):
                    b.convert_timer = b.conversion_interval
                b.convert_timer -= 1
                if b.convert_timer <= 0 and resources.energy >= b.energy_cost:
                    resources.spend_energy(b.energy_cost)
                    resources.add_minerals(b.conversion_rate)
                    b.convert_timer = b.conversion_interval
                    # Visual effect
                    for _ in range(5):
                        particles.append(Particle(b.x, b.y, YELLOW, random.uniform(-2,2), random.uniform(-2,2), 20, 3))
        # Remove depleted asteroids
        asteroids[:] = [a for a in asteroids if a.minerals > 0]
        max_buildings_ever = max(max_buildings_ever, len(buildings))
        # Game over conditions
        if base_health <= 0 or (len(buildings) == 0 and max_buildings_ever > 0):
            game_over = True
            high_score = max(high_score, score)
        # Update missiles
        for m in missiles[:]:
            m.update()
            if not m.alive:
                # Splash damage
                for e in wave_manager.enemies:
                    if (e.x - m.x) ** 2 + (e.y - m.y) ** 2 < m.splash_radius ** 2:
                        e.health -= m.damage
                        # XP gain for turret
                        for b in buildings:
                            if b.type == 'turret' and hasattr(b, 'cooldown_timer'):
                                if hasattr(b, 'xp'):
                                    b.gain_xp(XP_PER_KILL)
                        if e.health <= 0:
                            # Score, minerals, particles
                            score += SCORE_PER_KILL
                            resources.add_minerals(MINERALS_PER_KILL)
                            for _ in range(20):
                                particles.append(Particle(e.x, e.y, random.choice([YELLOW,ORANGE,RED]), random.uniform(-3,3), random.uniform(-3,3), random.randint(15,30), random.randint(2,4)))
                missiles.remove(m)
            else:
                # Remove if out of bounds
                if not (0 <= m.x <= WORLD_WIDTH and 0 <= m.y <= WORLD_HEIGHT):
                    missiles.remove(m)
        # Converter logic
        for b in buildings:
            if b.type == 'converter' and b.powered:
                if not hasattr(b, 'convert_timer'):
                    b.convert_timer = b.conversion_interval
                b.convert_timer -= 1
                if b.convert_timer <= 0 and resources.energy >= b.energy_cost:
                    resources.spend_energy(b.energy_cost)
                    resources.add_minerals(b.conversion_rate)
                    b.convert_timer = b.conversion_interval
                    # Visual effect
                    for _ in range(5):
                        particles.append(Particle(b.x, b.y, YELLOW, random.uniform(-2,2), random.uniform(-2,2), 20, 3))
        # Remove depleted asteroids
        asteroids[:] = [a for a in asteroids if a.minerals > 0]
        max_buildings_ever = max(max_buildings_ever, len(buildings))
        # Game over conditions
        if base_health <= 0 or (len(buildings) == 0 and max_buildings_ever > 0):
            game_over = True
            high_score = max(high_score, score)

    # Powerup timers
        for pu in powerups.values():
        if pu['active']:
            pu['timer'] -= 1
            if pu['timer'] <= 0:
                pu['active'] = False

    # Drawing
    screen.fill((10, 10, 30))  # Dark space background

    # Draw asteroids first (bottom layer)
    for asteroid in asteroids:
        asteroid.draw(screen, camera.x, camera.y, camera.zoom)

    # Draw power connections with glow effect
    glow_time = pygame.time.get_ticks() / 1000.0  # Time-based glow
    for x1, y1, x2, y2 in power_grid.get_connections():
        screen_x1, screen_y1 = camera.world_to_screen(x1, y1)
        screen_x2, screen_y2 = camera.world_to_screen(x2, y2)
        
        # Calculate glow intensity (oscillates between 0.3 and 0.8)
        glow_intensity = 0.3 + 0.5 * (0.5 + 0.5 * math.sin(glow_time * 2))
        
        # Dark orange base color
        base_color = (180, 90, 20)  # Darker orange
        glow_color = (int(255 * glow_intensity), int(140 * glow_intensity), int(40 * glow_intensity))
        
        line_width = max(1, int(3 * camera.zoom))
        
        # Make lines thinner
        line_width = max(1, int(2 * camera.zoom))  # Reduced from 3
        
        # Draw glow layers with white center line
        pygame.draw.line(screen, glow_color, (screen_x1, screen_y1), (screen_x2, screen_y2), line_width + 2)
        pygame.draw.line(screen, base_color, (screen_x1, screen_y1), (screen_x2, screen_y2), line_width)
        # Thin white center line
        pygame.draw.line(screen, (255, 255, 255), (screen_x1, screen_y1), (screen_x2, screen_y2), max(1, int(1 * camera.zoom)))

    # Draw base
    draw_base(screen, BASE_POS, BASE_RADIUS, base_health, BASE_HEALTH, camera)

    # Draw buildings (powered glow removed)
    for building in buildings:
        building.draw(screen, camera.x, camera.y, camera.zoom)

    # Draw range for selected defensive buildings
    if selected_building:
        if selected_building.type == 'turret':
            draw_range_indicator(screen, selected_building.x, selected_building.y, selected_building.fire_range, camera, (255, 0, 0, 100))
        elif selected_building.type == 'laser':
            draw_range_indicator(screen, selected_building.x, selected_building.y, selected_building.fire_range, camera, (100, 200, 255, 100))
        elif selected_building.type == 'repair':
            draw_range_indicator(screen, selected_building.x, selected_building.y, selected_building.heal_range, camera, (0, 255, 255, 100))
        elif selected_building.type == 'miner':
            draw_range_indicator(screen, selected_building.x, selected_building.y, MINER_RANGE, camera, (0, 255, 0, 100))

    # Draw laser beams from laser turrets
    for building in buildings:
        if building.type == 'laser' and hasattr(building, 'laser_target') and building.laser_target:
            screen_x1, screen_y1 = camera.world_to_screen(building.x, building.y)
            screen_x2, screen_y2 = camera.world_to_screen(building.laser_target.x, building.laser_target.y)
            pygame.draw.line(screen, WHITE, (screen_x1, screen_y1), (screen_x2, screen_y2), max(1, int(5 * camera.zoom)))
            pygame.draw.line(screen, CYAN, (screen_x1, screen_y1), (screen_x2, screen_y2), max(1, int(2 * camera.zoom)))

    # Draw range indicator when placing building
    if selected_build:
        mx, my = pygame.mouse.get_pos()
        world_x, world_y = camera.screen_to_world(mx, my)
        if selected_build == 'turret':
            draw_range_indicator(screen, world_x, world_y, TURRET_RANGE, camera, (255, 0, 0, 100))
        elif selected_build == 'repair':
            draw_range_indicator(screen, world_x, world_y, REPAIR_RANGE, camera, (0, 255, 255, 100))
        elif selected_build == 'laser':
            draw_range_indicator(screen, world_x, world_y, LASER_RANGE, camera, (100, 200, 255, 100))
        elif selected_build == 'connector':
            draw_range_indicator(screen, world_x, world_y, POWER_RANGE, camera, (255, 255, 0, 100))
        elif selected_build == 'miner':
            draw_range_indicator(screen, world_x, world_y, MINER_RANGE, camera, (0, 255, 0, 100))

    # Draw enemies
    wave_manager.draw_enemies(screen, camera)

    # Draw enemy lasers
    for x1, y1, x2, y2 in enemy_lasers:
        # Multi-layered laser effect with camera transform (smaller beam width)
        screen_x1, screen_y1 = camera.world_to_screen(x1, y1)
        screen_x2, screen_y2 = camera.world_to_screen(x2, y2)
        beam_width = max(1, int(ENEMY_LASER_WIDTH * camera.zoom))
        pygame.draw.line(screen, (255, 100, 100), (screen_x1, screen_y1), (screen_x2, screen_y2), beam_width)
        pygame.draw.line(screen, (255, 180, 40), (screen_x1, screen_y1), (screen_x2, screen_y2), max(1, beam_width - 1))
        pygame.draw.line(screen, (255, 255, 100), (screen_x1, screen_y1), (screen_x2, screen_y2), max(1, beam_width - 2))
        # Add damage particles at target perimeter
        angle = math.atan2(y2 - y1, x2 - x1)
        # Find target radius for perimeter calculation
        target_radius = BASE_RADIUS if isinstance(enemy_lasers, dict) else 25  # Default building radius
        perimeter_x = x2 - target_radius * math.cos(angle)
        perimeter_y = y2 - target_radius * math.sin(angle)
        for _ in range(3):
            particles.append(Particle(perimeter_x + random.uniform(-10, 10), perimeter_y + random.uniform(-10, 10), (255,100,100), random.uniform(-1,1), random.uniform(-1,1), 8, 2))

    # Draw missiles
        for m in missiles:
        m.draw(screen, camera)

    # Draw mothership missiles
    for m in mothership_missiles:
        m.draw(screen, camera)

    # Draw particles
    for p in particles:
        p.draw(screen, camera)

    # Draw damage numbers
    for dn in damage_numbers:
        dn.draw(screen, camera)

    # UI elements drawn on top
    title_text = small_font.render("Space Game Clone", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))

    # Draw controls UI on top
    draw_controls_ui(screen)

    # HUD: Minerals, Energy, Wave, Score, High Score, Kill Count (smaller)
    pygame.draw.rect(screen, (30, 30, 30), (10, 10, 600, 50))
    minerals_text = small_font.render(f"Minerals: {int(resources.minerals)}", True, YELLOW)
    energy_text = small_font.render(f"Energy: {int(resources.energy)} / {int(resources.max_energy)}", True, CYAN)
    wave_text = small_font.render(f"Wave: {wave_manager.wave}", True, RED)
    score_text = small_font.render(f"Score: {score}", True, WHITE)
    high_score_text = small_font.render(f"High: {high_score}", True, WHITE)
    kill_text = small_font.render(f"Kills: {kill_count}", True, (255, 100, 100))
    screen.blit(minerals_text, (15, 15))
    screen.blit(energy_text, (15, 35))
    screen.blit(wave_text, (150, 15))
    screen.blit(score_text, (220, 15))
    screen.blit(high_score_text, (320, 15))
    screen.blit(kill_text, (SCREEN_WIDTH - kill_text.get_width() - 10, 15))

    # Camera controls hint
    camera_text = small_font.render("Arrows: Pan | Scroll: Zoom", True, WHITE)
    screen.blit(camera_text, (SCREEN_WIDTH - camera_text.get_width() - 10, 35))

    # Show selected build type
    if selected_build:
        sel_text = small_font.render(f"Placing: {selected_build.capitalize()} (Click to place)", True, (255, 255, 180))
        screen.blit(sel_text, (400, 135))

    # Next wave button
    if wave_manager.can_start_next_wave and not game_over:
        next_wave_text = small_font.render(f"N - Start Wave {wave_manager.wave} ({wave_manager.wait_timer // 60 + 1}s)", True, (255, 255, 100))
        screen.blit(next_wave_text, (SCREEN_WIDTH // 2 - next_wave_text.get_width() // 2, 220))

    # Show selected building stats in bottom left panel
        if selected_building:
        panel_width = 250
        panel_height = 150
        panel_x = 10
        panel_y = SCREEN_HEIGHT - panel_height - 10
        
        # Draw panel background
        pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 100), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Building info
        y_offset = panel_y + 10
        title_text = small_font.render(f"{selected_building.type.capitalize()}", True, WHITE)
        screen.blit(title_text, (panel_x + 10, y_offset))
        
        y_offset += 20
        level_text = small_font.render(f"Level: {selected_building.level}/{MAX_LEVEL}", True, WHITE)
        screen.blit(level_text, (panel_x + 10, y_offset))
        
        y_offset += 18
        health_text = small_font.render(f"Health: {int(selected_building.health)}/{int(selected_building.max_health)}", True, WHITE)
        screen.blit(health_text, (panel_x + 10, y_offset))
        
        # Type-specific stats
        y_offset += 18
        if selected_building.type == 'turret':
            damage_text = small_font.render(f"Damage: {selected_building.damage}", True, WHITE)
            screen.blit(damage_text, (panel_x + 10, y_offset))
            y_offset += 18
            range_text = small_font.render(f"Range: {int(selected_building.fire_range)}", True, WHITE)
            screen.blit(range_text, (panel_x + 10, y_offset))
        elif selected_building.type == 'laser':
            damage_text = small_font.render(f"DPS: {selected_building.damage_per_frame * 60:.1f}", True, WHITE)
            screen.blit(damage_text, (panel_x + 10, y_offset))
            y_offset += 18
            range_text = small_font.render(f"Range: {int(selected_building.fire_range)}", True, WHITE)
            screen.blit(range_text, (panel_x + 10, y_offset))
        elif selected_building.type == 'solar':
            energy_text = small_font.render(f"Energy/sec: {selected_building.prod_rate * 60:.1f}", True, WHITE)
            screen.blit(energy_text, (panel_x + 10, y_offset))
        elif selected_building.type == 'battery':
            storage_text = small_font.render(f"Storage: {selected_building.storage}", True, WHITE)
            screen.blit(storage_text, (panel_x + 10, y_offset))
        elif selected_building.type == 'miner':
            rate_text = small_font.render(f"Mine Rate: {selected_building.mine_rate}", True, WHITE)
            screen.blit(rate_text, (panel_x + 10, y_offset))
        elif selected_building.type == 'repair':
            heal_text = small_font.render(f"Heal/sec: {selected_building.heal_rate * 60:.1f}", True, WHITE)
            screen.blit(heal_text, (panel_x + 10, y_offset))
            y_offset += 18
            range_text = small_font.render(f"Range: {int(selected_building.heal_range)}", True, WHITE)
            screen.blit(range_text, (panel_x + 10, y_offset))
        elif selected_building.type == 'converter':
            rate_text = small_font.render(f"Convert Rate: {selected_building.conversion_rate}", True, WHITE)
            screen.blit(rate_text, (panel_x + 10, y_offset))
        
        # Sell and Upgrade buttons at bottom of panel
        sell_price = int((0.5 + selected_building.level) * BUILD_COSTS[selected_building.type])
        upgrade_cost = selected_building.upgrade_cost(BUILD_COSTS[selected_building.type])
        
        sell_text = small_font.render(f"X - Sell: {sell_price}", True, (255, 200, 200))
        screen.blit(sell_text, (panel_x + 10, panel_y + panel_height - 35))
        
        if selected_building.level < MAX_LEVEL:
            upgrade_text = small_font.render(f"U - Upgrade: {upgrade_cost}", True, (200, 255, 200))
            screen.blit(upgrade_text, (panel_x + 10, panel_y + panel_height - 18))
        else:
            max_text = small_font.render("Max Level", True, (150, 150, 150))
            screen.blit(max_text, (panel_x + 10, panel_y + panel_height - 18))

    # Draw powerup buttons (smaller)
    for i, key in enumerate(powerup_keys):
        rect = powerup_buttons[key]
        color = (0, 200, 0) if powerups[key]['active'] else ((100, 100, 100) if resources.energy < POWERUP_COST else (0, 120, 255))
        pygame.draw.rect(screen, color, rect)
        text = small_font.render(powerups[key]['name'], True, WHITE)
        screen.blit(text, (rect.x + 5, rect.y + 8))
        if powerups[key]['active']:
            timer_text = small_font.render(str(powerups[key]['timer'] // 60), True, (255, 80, 80))
            screen.blit(timer_text, (rect.x + 80, rect.y + 8))

    if paused:
        pause_text = font.render("Paused", True, YELLOW)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))

    # Game over screen
    if game_over:
        if base_health <= 0:
            go_text = font.render("Base destroyed! Restart?", True, (255, 80, 80))
        else:
            go_text = font.render("All nodes destroyed! Restart?", True, (255, 80, 80))
        screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 40, 160, 50)
        pygame.draw.rect(screen, (100, 100, 100), restart_rect)
        restart_text = hud_font.render("Restart", True, WHITE)
        screen.blit(restart_text, (restart_rect.x + 30, restart_rect.y + 12))
        hs_text = hud_font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(hs_text, (SCREEN_WIDTH // 2 - hs_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

    # Game menu (drawn on top of everything)
    if show_menu:
        draw_game_menu(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()