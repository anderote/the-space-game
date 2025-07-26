"""
Panda3D Game Engine - Phase 3 Implementation
Integrates core building system with enhanced camera controls and entity visualization
"""

from ..panda3d.scene_manager import SceneManager
from ..panda3d.camera_controller import Panda3DCamera
from ..panda3d.input_system import Panda3DInputSystem
from ..panda3d.hud_system import HUDSystem
from ..systems.building_system import BuildingSystem

class Panda3DGameEngine:
    """Game engine that integrates building system with Panda3D visualization"""
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Game state
        self.state = "menu"
        self.paused = False
        
        # Initialize Panda3D systems
        self.init_panda3d_systems()
        
        # Initialize core game systems
        self.init_core_systems()
        
        print("✓ Panda3D Game Engine initialized (Phase 3)")
        
    def init_panda3d_systems(self):
        """Initialize Panda3D-specific rendering and interaction systems"""
        print("Initializing Panda3D systems...")
        
        # Scene manager (handles lighting, visuals, entity rendering)
        self.scene_manager = SceneManager(self.base, self.config)
        
        # Camera controller (handles movement, zoom, coordinate conversion)
        self.camera = Panda3DCamera(self.base, self.config, self.scene_manager)
        
        # Input system (handles user input, camera controls, building placement)
        self.input_system = Panda3DInputSystem(self.base, self)
        
        # HUD system (handles on-screen information display)
        self.hud_system = HUDSystem(self.base, self)
        
        print("✓ Panda3D systems initialized")
        
    def init_core_systems(self):
        """Initialize core game systems with real functionality"""
        print("Initializing core game systems...")
        
        # Resource management
        game_config = self.config.game.get("resources", {})
        self.minerals = game_config.get("starting_minerals", 600)
        self.energy = game_config.get("starting_energy", 50)
        
        # Game progression
        self.wave_number = 1
        self.score = 0
        
        # Initialize building system (Phase 3)
        self.building_system = BuildingSystem(self.base, self.config, self.scene_manager)
        
        # Entity collections (Phase 3 - building system manages buildings now)
        self.enemies = []
        self.projectiles = []
        self.asteroids = []
        
        # Create starting base
        self._create_starting_base()
        
        print("✓ Core game systems initialized (Phase 3)")
        print(f"  Starting resources: {self.minerals} minerals, {self.energy} energy")
        
    def _create_starting_base(self):
        """Create the starting base at world center"""
        world_center_x = self.config.game.get("display", {}).get("world_width", 4800) / 2
        world_center_y = self.config.game.get("display", {}).get("world_height", 2700) / 2
        
        # Place starting base (free, instant construction)
        base_building = self.building_system.place_building("starting_base", world_center_x, world_center_y, self)
        if base_building:
            # Import BuildingState to fix the reference
            from ..entities.building import BuildingState
            # Make starting base instantly operational
            base_building.state = BuildingState.OPERATIONAL
            base_building.construction_progress = 1.0
            base_building.powered = True  # Starting base is always powered
            print(f"✓ Starting base established at ({world_center_x:.0f}, {world_center_y:.0f})")
        
    def update(self, dt):
        """Main game loop update"""
        # Update Panda3D systems
        self.camera.update(dt)
        self.input_system.update(dt)
        self.scene_manager.update(dt)
        self.hud_system.update(dt)
        
        # Game logic updates
        if self.state == "playing" and not self.paused:
            self.update_game_logic(dt)
            
    def update_game_logic(self, dt):
        """Update core game logic (Phase 3 implementation)"""
        # Update building system
        self.building_system.update(dt)
        
        # TODO: Update other systems (enemies, combat, etc.) in later parts of Phase 3
        
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
        
        print(f"Game started with {self.minerals} minerals and {self.energy} energy")
        print("Use WASD to move camera, mouse wheel to zoom")
        print("Press building hotkeys (Q,E,B,M,T,L,etc.) to build structures")
        
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
        
    def start_building_construction(self, building_type: str) -> bool:
        """Start construction mode for a building type"""
        if self.state != "playing":
            print("Cannot build - game not in playing state")
            return False
            
        return self.building_system.start_construction(building_type)
        
    def cancel_building_construction(self):
        """Cancel building construction mode"""
        self.building_system.cancel_construction()
        
    def place_building_at_cursor(self, world_x: float, world_y: float) -> bool:
        """Attempt to place building at cursor position"""
        if not self.building_system.construction_mode:
            return False
            
        building = self.building_system.place_building(
            self.building_system.selected_building_type, 
            world_x, 
            world_y, 
            self
        )
        
        return building is not None
        
    def select_building_at(self, world_x: float, world_y: float):
        """Select building at world coordinates"""
        return self.building_system.select_building_at(world_x, world_y)
        
    def get_selected_building(self):
        """Get currently selected building"""
        return self.building_system.get_selected_building()
        
    def get_building_cost(self, building_type: str):
        """Get the cost of a building type"""
        return self.building_system.get_building_cost(building_type)
        
    def can_afford_building(self, building_type: str):
        """Check if player can afford a building"""
        return self.building_system.can_afford_building(building_type, self.minerals, self.energy)
        
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
        
    def get_construction_info(self):
        """Get current construction mode information"""
        if self.building_system.construction_mode:
            return {
                'active': True,
                'building_type': self.building_system.selected_building_type,
                'cost': self.get_building_cost(self.building_system.selected_building_type),
                'can_afford': self.can_afford_building(self.building_system.selected_building_type)
            }
        return {'active': False}
        
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
            'building_count': self.building_system.get_building_count(),
            'enemy_count': len(self.enemies),
            'power_generation': self.building_system.get_total_power_generation(),
            'power_consumption': self.building_system.get_total_power_consumption()
        }
        
    def cleanup(self):
        """Clean up all game systems"""
        print("Cleaning up game engine...")
        
        # Clean up game systems
        if hasattr(self, 'building_system'):
            self.building_system.cleanup()
            
        # Clean up Panda3D systems
        if hasattr(self, 'hud_system'):
            self.hud_system.cleanup()
        if hasattr(self, 'input_system'):
            self.input_system.cleanup()
        if hasattr(self, 'scene_manager'):
            self.scene_manager.cleanup()
            
        # Clear game state
        self.enemies.clear()
        self.projectiles.clear()
        self.asteroids.clear()
        
        print("✓ Game engine cleanup complete") 