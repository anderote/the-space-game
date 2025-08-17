"""
Panda3D Game Engine - Phase 3 Implementation
Integrates core building system with enhanced camera controls and entity visualization
"""

from ..panda3d.scene_manager import SceneManager
from ..panda3d.camera_controller import Panda3DCamera
from ..panda3d.input_system import Panda3DInputSystem
from ..panda3d.hud_system import HUDSystem
from ..systems.building_system import BuildingSystem
from ..systems.wave_system import WaveSystem
from ..systems.research_system import ResearchSystem
from ..entities.building import BuildingState

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
        self.max_energy = 100  # Starting base capacity
        
        # Game progression
        self.wave_number = 1
        self.score = 0
        
        # Initialize building system (Phase 3)
        self.building_system = BuildingSystem(self.base, self.config, self.scene_manager, self)
        
        # Initialize research system
        self.research_system = ResearchSystem(self.config)
        
        # Refresh research menu now that research system is available
        if hasattr(self, 'hud_system') and self.hud_system:
            self.hud_system.refresh_research_menu()
        
        # Initialize wave system
        self.wave_system = WaveSystem(self.config, self, self.scene_manager)
        
        # Connect HUD system to building system for UI updates
        self.building_system.hud_system = self.hud_system
        
        # Entity collections (Phase 3 - building system manages buildings now)
        self.enemies = []
        self.projectiles = []
        self.asteroids = []
        
        # Create starting base
        self._create_starting_base()
        
        # Generate asteroids as buildings
        self.create_asteroid_fields()
        
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
            # Note: powered is now computed automatically based on building_type
            print(f"✓ Starting base established at ({world_center_x:.0f}, {world_center_y:.0f})")
        
    def create_asteroid_fields(self):
        """Generate asteroid fields as buildings through the building system"""
        # Get world dimensions and base position from config
        display_config = self.config.game.get("display", {})
        world_width = display_config.get("world_width", 4800)
        world_height = display_config.get("world_height", 2700)
        
        # Base is at world center
        base_x = world_width / 2
        base_y = world_height / 2
        
        # Generate asteroid data
        asteroid_data = self.scene_manager.entity_visualizer.generate_enhanced_asteroid_fields(
            base_x, base_y, world_width, world_height
        )
        
        # Create each asteroid as a building
        for data in asteroid_data:
            # Create building with custom properties for asteroid
            from ..entities.building import Building, BuildingState
            asteroid = Building(
                building_type="asteroid",
                x=data['x'], 
                y=data['y'], 
                config=self.config,
                completion_callback=None,  # Asteroids don't construct
                game_engine=self
            )
            
            # Override properties for asteroid
            asteroid.radius = data['radius']
            asteroid._operational_health = data['health']
            asteroid.base_max_health = data['health']  # Store original health
            asteroid.mineral_value = data['minerals']
            asteroid.state = BuildingState.OPERATIONAL  # Asteroids are always "operational"
            
            # Create visual representation using asteroid visual
            asteroid.visual_node = self.scene_manager.entity_visualizer.create_3d_asteroid(
                data['x'], data['y'], data['radius']
            )
            
            # Store in building system
            self.building_system.buildings[asteroid.building_id] = asteroid
            
            # Add to type index
            if "asteroid" not in self.building_system.buildings_by_type:
                self.building_system.buildings_by_type["asteroid"] = []
            self.building_system.buildings_by_type["asteroid"].append(asteroid)
        
        print(f"✓ Generated {len(asteroid_data)} asteroids as buildings")
        
    def remove_building(self, building):
        """Remove a building from the game (used for depleted asteroids)"""
        if hasattr(self.building_system, 'remove_building'):
            self.building_system.remove_building(building)
        else:
            # Manual removal if building system doesn't have the method
            if building.building_id in self.building_system.buildings:
                del self.building_system.buildings[building.building_id]
            
            # Remove from type index
            if building.building_type in self.building_system.buildings_by_type:
                if building in self.building_system.buildings_by_type[building.building_type]:
                    self.building_system.buildings_by_type[building.building_type].remove(building)
            
            # Remove visual
            if hasattr(building, 'visual_node') and building.visual_node:
                building.visual_node.removeNode()
                
            print(f"✓ Removed {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
        
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
        # Update power generation from buildings
        self.update_power_generation(dt)
        
        # Update energy capacity when buildings change
        self.update_energy_capacity()
        
        # Update building system
        self.building_system.update(dt)
        
        # Update research system
        self.research_system.update(dt)
        
        # Update wave system and enemies
        self.wave_system.update(dt)
        self.update_enemies(dt)
        
        # Update projectiles
        self.update_projectiles(dt)
        
        # Periodically cleanup destroyed buildings
        self.cleanup_destroyed_buildings()
        
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
        
    def select_building_at(self, x: float, y: float) -> bool:
        """Select building at the given position"""
        building = self.building_system.get_building_at_position(x, y)
        if building:
            self.building_system.select_building(building)
            print(f"✓ Selected {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
            return True
        return False
        
    def clear_building_selection(self):
        """Clear current building selection"""
        if self.building_system.selected_building:
            print(f"Cleared selection of {self.building_system.selected_building.building_type}")
        self.building_system.clear_building_selection()
        
    def get_building_at_position(self, x: float, y: float):
        """Get building at the given position"""
        return self.building_system.get_building_at_position(x, y)
        
    def get_selected_building(self):
        """Get currently selected building"""
        return self.building_system.get_selected_building()
        
    def get_building_cost(self, building_type: str):
        """Get the cost of a building type"""
        return self.building_system.get_building_cost(building_type)
        
    def can_afford_building(self, building_type: str):
        """Check if player can afford a building"""
        return self.building_system.can_afford_building(building_type, self.minerals, self.energy)
    
    def consume_energy(self, amount: float) -> bool:
        """Consume energy from the power network. Returns True if successful."""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def generate_energy(self, amount: float):
        """Generate energy to the power network"""
        self.energy += amount
    
    def get_current_resources(self) -> dict:
        """Get current resource levels"""
        return {
            "minerals": self.minerals,
            "energy": self.energy
        }
        
    def get_power_generation_rate(self) -> float:
        """Calculate total power generation from all buildings"""
        total_generation = 0.0
        for building in self.building_system.buildings.values():
            if building.state == BuildingState.OPERATIONAL and not building.disabled:  # Only operational and enabled buildings generate power
                # Use the building's effective energy generation (which includes level bonuses)
                if building.building_type in ["solar", "nuclear"]:
                    power_gen = building.get_effective_energy_generation()
                elif building.building_type == "starting_base":
                    power_gen = 0.2  # Base power rate from starting base
                else:
                    # For other buildings, use config value
                    building_config = self.config.buildings.get("building_types", {}).get(building.building_type, {})
                    power_gen = building_config.get("power_generation", 0.0)
                
                total_generation += power_gen
        return total_generation
    
    def get_total_energy_capacity(self) -> float:
        """Calculate total energy storage capacity from all buildings"""
        total_capacity = 100  # Starting base provides 100 base capacity
        for building in self.building_system.buildings.values():
            if building.state == BuildingState.OPERATIONAL and not building.disabled:  # Only operational and enabled buildings provide capacity
                # Use the building's effective energy capacity (which includes level bonuses)
                if building.building_type in ["solar", "battery"]:
                    capacity = building.get_effective_energy_capacity()
                else:
                    # For other buildings, use config value
                    building_config = self.config.buildings.get("building_types", {}).get(building.building_type, {})
                    capacity = building_config.get("energy_capacity", 0.0)
                
                total_capacity += capacity
        return total_capacity
    
    def update_energy_capacity(self):
        """Update maximum energy based on operational buildings"""
        self.max_energy = self.get_total_energy_capacity()  # Already includes starting base minimum
        # Cap current energy to max capacity
        if self.energy > self.max_energy:
            self.energy = self.max_energy
    
    def update_power_generation(self, dt: float):
        """Update power generation from buildings"""
        generation_rate = self.get_power_generation_rate()
        if generation_rate > 0:
            energy_generated = generation_rate * dt
            self.generate_energy(energy_generated)
    
    def update_enemies(self, dt: float):
        """Update all enemies"""
        # Update each enemy
        for enemy in self.enemies[:]:  # Use slice to avoid modification during iteration
            old_x, old_y = enemy.x, enemy.y
            enemy.update(dt)
            
            # Update dynamic lighting position if enemy moved (TEMPORARILY DISABLED)
            # Dynamic lighting has API compatibility issues with current Panda3D version
            # if (hasattr(enemy, 'dynamic_light_id') and 
            #     hasattr(self.scene_manager, 'dynamic_lighting') and
            #     self.scene_manager.dynamic_lighting and
            #     (enemy.x != old_x or enemy.y != old_y)):
            #     
            #     self.scene_manager.dynamic_lighting.update_light_position(
            #         enemy.dynamic_light_id, enemy.x, enemy.y, 5
            #     )
            
            # Remove destroyed enemies
            if not enemy.is_alive():
                # Clean up dynamic lighting (TEMPORARILY DISABLED)
                # Dynamic lighting has API compatibility issues with current Panda3D version
                # if (hasattr(enemy, 'dynamic_light_id') and 
                #     hasattr(self.scene_manager, 'dynamic_lighting') and
                #     self.scene_manager.dynamic_lighting):
                #     
                #     self.scene_manager.dynamic_lighting.remove_light(enemy.dynamic_light_id)
                
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
    
    def update_projectiles(self, dt: float):
        """Update all projectiles"""
        # Update each projectile
        for projectile in self.projectiles[:]:  # Use slice to avoid modification during iteration
            projectile.update(dt)
            
            # Remove inactive projectiles
            if not projectile.is_active():
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
        
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
    
    def cleanup_destroyed_buildings(self):
        """Remove buildings that have zero health and are not under construction"""
        import time
        
        # Only run cleanup every 5 seconds to avoid performance issues
        if not hasattr(self, '_last_building_cleanup'):
            self._last_building_cleanup = 0
            
        current_time = time.time()
        if current_time - self._last_building_cleanup < 5.0:
            return
            
        self._last_building_cleanup = current_time
        
        # Get buildings that need to be removed
        buildings_to_remove = []
        for building_id, building in self.building_system.buildings.items():
            # Remove buildings with zero health that are not under construction
            if (building.current_health <= 0 and 
                building.state != BuildingState.UNDER_CONSTRUCTION and
                building.state != BuildingState.DESTROYED):
                buildings_to_remove.append(building_id)
        
        # Remove the buildings
        for building_id in buildings_to_remove:
            building = self.building_system.buildings[building_id]
            print(f"🗑️ Removing destroyed {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
            
            # Mark as destroyed first
            building.state = BuildingState.DESTROYED
            
            # Remove from building system
            self.building_system.remove_building(building_id)
            
            # Remove visual representation
            if hasattr(self, 'scene_manager') and self.scene_manager.entity_visualizer:
                self.scene_manager.entity_visualizer.remove_building_visual(building_id)
        
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
            
        # Clean up wave system
        if hasattr(self, 'wave_system'):
            self.wave_system.cleanup()
        
        # Clear game state
        self.enemies.clear()
        self.projectiles.clear()
        self.asteroids.clear()
        
        print("✓ Game engine cleanup complete") 