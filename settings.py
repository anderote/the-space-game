"""
Constants and configuration for Space Game Clone.
"""

# Screen settings
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

# World settings (3x bigger than screen, increased by 15%)
WORLD_WIDTH = int(SCREEN_WIDTH * 3 * 1.15)  # Increased by 15%
WORLD_HEIGHT = int(SCREEN_HEIGHT * 3 * 1.15)  # Increased by 15%

# Camera settings
CAMERA_SPEED = 10
ZOOM_MIN = 0.5
ZOOM_MAX = 5.0  # Increased for full map view
ZOOM_SPEED = 0.1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

# Font settings
FONT_FAMILY = "Arial"  # Changed to Arial for thinner appearance
FONT_WEIGHT = "light"  # Prefer light weight

# Base configuration
BASE_RADIUS = 40
BASE_HEALTH = 450
BASE_MAX_ENERGY = 100

# Resource configuration
STARTING_MINERALS = 600  # Decreased by 30% (was 1200)
STARTING_ENERGY = 50
STARTING_MAX_ENERGY = 200

# Building costs
BUILD_COSTS = {
    'solar': 50,
    'connector': 30,
    'battery': 80,
    'miner': 100,
    'turret': 150,
    'laser': 200,
    'superlaser': 500,  # New expensive long-range laser
    'repair': 120,
    'converter': 90,
    'hangar': 250  # Hangar for friendly attack ships
}

# Building stats
SOLAR_ENERGY_RATE = 0.1  # per level per frame
MINER_RATE = 3.0  # minerals per level per zap
MINER_ZAP_INTERVAL = 180  # frames (~3 sec at 60fps)
MINER_ZAP_ENERGY_COST = 5
BATTERY_STORAGE = 120  # per level
TURRET_DAMAGE = 10  # per level
TURRET_RANGE = 350  # base range
TURRET_COOLDOWN = 180  # base cooldown in frames (40% slower than previous, was 120)
TURRET_ENERGY_COST = 4  # energy per shot
TURRET_MINERAL_COST = 3  # minerals per shot
LASER_DAMAGE = 0.35  # per level per frame
LASER_COST = 0.18  # energy per level per frame
LASER_RANGE = 220  # base range
SUPERLASER_DAMAGE = 0.95  # per level per frame - much higher damage
SUPERLASER_COST = 1.2  # energy per level per frame - much higher cost
SUPERLASER_RANGE = 600  # much longer range
REPAIR_RATE = 0.15  # per level per frame
REPAIR_ENERGY_COST = 0.05  # energy per frame
REPAIR_RANGE = 250  # base range
CONVERTER_ENERGY_COST = 100
CONVERTER_MINERAL_RATE = 2  # minerals per conversion
CONVERTER_INTERVAL = 120  # frames between conversions

# Hangar stats
HANGAR_ENERGY_COST = 0.5  # energy per frame to maintain
HANGAR_LAUNCH_COOLDOWN = 300  # frames between ship launches (5 seconds)
HANGAR_MAX_SHIPS = 4  # maximum ships per hangar
HANGAR_SHIP_RANGE = 500  # range within which ships will engage
HANGAR_RECALL_RANGE = 600  # range beyond which ships return
HANGAR_REGEN_COOLDOWN = 1200  # frames between ship regeneration (20 seconds)

# Power grid
POWER_RANGE = 150
MAX_CONNECTIONS = 6

# Enemy configuration
ENEMY_SPAWN_BASE = 15  # Increased by 3x (was 5)
ENEMY_SPEED = 0.7  # Reduced from 1.0
ENEMY_HEALTH_BASE = 24  # per wave (increased by 20%)
ENEMY_LASER_RANGE = 120  # Increased from 100
ENEMY_LASER_DAMAGE = 0.1  # per frame
ENEMY_LASER_WIDTH = 2  # thinner beam width
ENEMY_CONTACT_DAMAGE = 10 / 60  # per frame
ENEMY_ORBIT_RADIUS = 50
ENEMY_ORBIT_SPEED = 0.05  # radians per frame

# Mothership enemy configuration
MOTHERSHIP_HEALTH_MULTIPLIER = 5  # 5x health of regular enemies
MOTHERSHIP_SIZE = 25  # larger than regular enemies (15)
MOTHERSHIP_SPEED = 0.6  # slower than regular enemies
MOTHERSHIP_MISSILE_RANGE = 400  # long range missiles
MOTHERSHIP_MISSILE_DAMAGE = 15  # stronger missiles
MOTHERSHIP_MISSILE_COOLDOWN = 120  # 2 seconds between shots
MOTHERSHIP_SPAWN_CHANCE = 0.15  # 15% chance per enemy to be mothership (for waves 3+)

# Wave configuration
WAVE_WAIT_TIME = 120  # frames between waves
SPAWN_INTERVAL = 30  # frames between enemy spawns
INITIAL_WAIT = 6600  # frames before first wave (110 seconds at 60fps) - added 30 seconds
WAVE_GROWTH_FACTOR = 2.16  # Increased by 20% from 1.8 (faster wave growth)
FORMATION_SIZE_THRESHOLD = 15  # Start using formations when wave has this many enemies
MAX_FORMATIONS = 4  # Maximum number of formations per wave

# Combat configuration
MISSILE_SPEED = 1.5  # Reduced by 50% from 3 for more strategic gameplay
MISSILE_SIZE = 2.4  # Reduced by 60% (was 4)
MISSILE_RANGE = 300
MISSILE_SPLASH_RADIUS = 48  # Increased by 20% (was 40)
XP_PER_KILL = 20
XP_TO_LEVEL_BASE = 600  # Increased by 6x (was 100)
TURRET_XP_MODIFIER = 0.7  # 30% slower XP gain for turrets
MAX_LEVEL = 10

# Scoring
SCORE_PER_KILL = 10
SCORE_PER_WAVE = 50
MINERALS_PER_KILL = 10

# Powerups
POWERUP_COST = 50
POWERUP_DURATION = 600  # frames (10 sec)

# Asteroid configuration
ASTEROID_CLUMPS_MIN = 4  # minimum number of asteroid clusters (reduced by 30%)
ASTEROID_CLUMPS_MAX = 8  # maximum number of asteroid clusters (reduced by 30%)
ASTEROIDS_PER_CLUMP = 4
ASTEROID_MIN_DIST = 100
ASTEROID_BASE_MINERALS = 2000
ASTEROID_MINERAL_PER_RADIUS = 20
ASTEROID_MIN_RADIUS = 20
ASTEROID_MAX_RADIUS = 50

# Mining configuration
MINER_RANGE = 80  # range for mining asteroids
MINER_MAX_TARGETS = 5  # maximum asteroids to mine simultaneously
MINING_CLOCK_INTERVAL = 180  # global mining clock interval (3 seconds at 60fps)
MINING_RATE_SINGLE = 3.0  # mining rate when targeting single asteroid
MINING_RATE_MULTI = 2.0   # mining rate per asteroid when targeting multiple

# Upgrade configuration
UPGRADE_COST_FACTOR = 1.2
HEALTH_PER_UPGRADE = 20

# UI Font sizes (smaller)
FONT_SIZE_LARGE = 48  # was 64
FONT_SIZE_MEDIUM = 24  # was 32
FONT_SIZE_SMALL = 18   # was 24 