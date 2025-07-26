"""
Panda3D Game Engine - Phase 2 Implementation
Integrates enhanced camera controls, entity visualization, and interactive systems
"""

from ..panda3d.scene_manager import SceneManager
from ..panda3d.camera_controller import Panda3DCamera
from ..panda3d.input_system import Panda3DInputSystem
from ..panda3d.hud_system import HUDSystem

class Panda3DGameEngine:
    """Game engine that preserves existing logic while integrating Panda3D"""
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Game state
        self.state = "menu"
        self.paused = False
        
        # Initialize Panda3D systems
        self.init_panda3d_systems()
        
        # Initialize core game systems (Phase 1 stubs, Phase 3 will implement)
        self.init_core_systems()
        
        print("✓ Panda3D Game Engine initialized (Phase 2)")
        
    def init_panda3d_systems(self):
        """Initialize Panda3D-specific rendering and interaction systems"""
        print("Initializing Panda3D systems...")
        
        # Scene manager (handles lighting, visuals, entity rendering)
        self.scene_manager = SceneManager(self.base, self.config)
        
        # Camera controller (handles movement, zoom, coordinate conversion)
        self.camera = Panda3DCamera(self.base, self.config)
        
        # Input system (handles user input, camera controls, building placement)
        self.input_system = Panda3DInputSystem(self.base, self)
        
        # HUD system (handles on-screen information display)
        self.hud_system = HUDSystem(self.base, self)
        
        print("✓ Panda3D systems initialized")
        
    def init_core_systems(self):
        """Initialize core game systems (preserve existing logic)"""
        # For Phase 2, we'll keep the stub systems from Phase 1
        # Phase 3 will replace these with actual implementations
        
        # Resource management
        game_config = self.config.game.get("resources", {})
        self.minerals = game_config.get("starting_minerals", 600)
        self.energy = game_config.get("starting_energy", 50)
        
        # Game progression
        self.wave_number = 1
        self.score = 0
        
        # Entity collections (Phase 3 will populate these)
        self.buildings = []
        self.enemies = []
        self.projectiles = []
        self.asteroids = []
        
        print("✓ Core game systems initialized (Phase 2 stubs)")
        print(f"  Starting resources: {self.minerals} minerals, {self.energy} energy")
        
    def update(self, dt):
        """Main game loop update"""
        # Update Panda3D systems
        self.camera.update(dt)
        self.input_system.update(dt)
        self.scene_manager.update(dt)
        self.hud_system.update(dt)
        
        # Game logic updates (Phase 3 will implement)
        if self.state == "playing" and not self.paused:
            self.update_game_logic(dt)
            
    def update_game_logic(self, dt):
        """Update core game logic (Phase 3 will implement)"""
        # For Phase 2, this is mostly empty
        # Phase 3 will implement:
        # - Building updates
        # - Enemy AI and movement
        # - Combat systems
        # - Wave spawning
        # - Resource collection
        pass
        
    def start_game(self):
        """Start a new game"""
        print("=== STARTING GAME ===")
        
        self.state = "playing"
        self.paused = False
        
        # Reset game state
        self.wave_number = 1
        self.score = 0
        
        # Reset resources
        game_config = self.config.game.get("resources", {})
        self.minerals = game_config.get("starting_minerals", 600)
        self.energy = game_config.get("starting_energy", 50)
        
        # Phase 3 will create the starting base and initial setup
        print(f"Game started with {self.minerals} minerals and {self.energy} energy")
        print("Use WASD to move camera, mouse wheel to zoom")
        print("Press building hotkeys (Q,E,B,M,T,L,etc.) to test building selection")
        
    def pause_game(self):
        """Pause/resume the game"""
        if self.state == "playing":
            self.paused = not self.paused
            status = "PAUSED" if self.paused else "RESUMED"
            print(f"Game {status}")
        else:
            print("Cannot pause - game not in playing state")
            
    def end_game(self):
        """End the current game"""
        print("=== GAME ENDED ===")
        self.state = "game_over"
        self.paused = False
        
    def add_building(self, building_type, x, y):
        """Add a building to the game (Phase 3 implementation)"""
        # Placeholder for Phase 3
        print(f"Would add {building_type} building at ({x}, {y})")
        
    def remove_building(self, building_id):
        """Remove a building from the game (Phase 3 implementation)"""
        # Placeholder for Phase 3
        print(f"Would remove building {building_id}")
        
    def get_buildings_at_position(self, x, y, radius=10):
        """Get buildings near a position (Phase 3 implementation)"""
        # Placeholder for Phase 3
        return []
        
    def can_place_building(self, building_type, x, y):
        """Check if a building can be placed at position (Phase 3 implementation)"""
        # Placeholder for Phase 3 - always return True for now
        return True
        
    def get_building_cost(self, building_type):
        """Get the cost of a building type"""
        building_config = self.config.buildings.get("building_types", {}).get(building_type)
        if building_config:
            return building_config.get("cost", {})
        return {"minerals": 0, "energy": 0}
        
    def can_afford_building(self, building_type):
        """Check if player can afford a building"""
        cost = self.get_building_cost(building_type)
        return (self.minerals >= cost.get("minerals", 0) and 
                self.energy >= cost.get("energy", 0))
        
    def get_camera_position(self):
        """Get current camera position"""
        return self.camera.x, self.camera.y
        
    def get_camera_zoom(self):
        """Get current camera zoom level"""
        return self.camera.zoom
        
    def get_mouse_world_position(self):
        """Get mouse position in world coordinates"""
        return self.input_system.get_mouse_world_position()
        
    def is_position_visible(self, x, y, margin=0):
        """Check if a position is visible in current camera view"""
        return self.camera.is_position_visible(x, y, margin)
        
    def toggle_hud(self):
        """Toggle HUD visibility"""
        self.hud_system.toggle_hud()
        
    def get_game_data(self):
        """Get current game state data"""
        return {
            'state': self.state,
            'paused': self.paused,
            'minerals': self.minerals,
            'energy': self.energy,
            'wave_number': self.wave_number,
            'score': self.score,
            'camera_x': self.camera.x,
            'camera_y': self.camera.y,
            'camera_zoom': self.camera.zoom,
            'building_count': len(self.buildings),
            'enemy_count': len(self.enemies)
        }
        
    def cleanup(self):
        """Clean up all game systems"""
        print("Cleaning up game engine...")
        
        # Clean up Panda3D systems
        if hasattr(self, 'hud_system'):
            self.hud_system.cleanup()
        if hasattr(self, 'input_system'):
            self.input_system.cleanup()
        if hasattr(self, 'scene_manager'):
            self.scene_manager.cleanup()
            
        # Clear game state
        self.buildings.clear()
        self.enemies.clear()
        self.projectiles.clear()
        self.asteroids.clear()
        
        print("✓ Game engine cleanup complete") 