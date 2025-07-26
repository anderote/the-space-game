"""
Panda3D Scene Manager - Phase 3 Implementation
Manages the 3D scene, lighting, starfield background, and entity visualization
"""

from panda3d.core import AmbientLight, DirectionalLight, Vec3
from .entity_visualizer import EntityVisualizer
from .starfield import StarfieldSystem
from .power_network_renderer import PowerNetworkRenderer

class SceneManager:
    """Manages the 3D scene and visual elements"""
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        self.lights = {}
        
        # Initialize starfield system
        self.starfield = StarfieldSystem(base, config)
        
        # Initialize entity visualizer
        self.entity_visualizer = EntityVisualizer(base)
        
        # Initialize power network renderer
        self.power_network_renderer = PowerNetworkRenderer(base)
        
        self.setup_scene()
        
    def setup_scene(self):
        """Set up the complete 3D scene"""
        print("Setting up Phase 3 scene...")
        
        self.setup_background()
        self.setup_basic_lighting()
        
        # Create test entities for Phase 2 visualization (will be replaced by real buildings)
        # self.entity_visualizer.create_test_entities()
        
        # Asteroids are now generated as buildings by the game engine
        self.asteroid_nodes = []
        
        print("✓ Phase 3 scene setup complete")
        
    def setup_background(self):
        """Set up the scene background"""
        # Set background color to dark space (15, 15, 32) normalized to 0-1
        self.base.setBackgroundColor(15/255, 15/255, 32/255, 1.0)
        print("✓ Background color set to dark space")
        
    def setup_basic_lighting(self):
        """Set up basic lighting for visibility"""
        print("Setting up lighting...")
        
        # Ambient light for general visibility (darker for more contrast)
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.2, 0.2, 0.3, 1))  # Darker blue ambient
        ambient_np = self.base.render.attachNewNode(ambient_light)
        self.base.render.setLight(ambient_np)
        self.lights['ambient'] = ambient_np
        
        # Primary directional light for depth and shadows
        directional_light = DirectionalLight('directional_light')
        directional_light.setDirection(Vec3(-1, -1, -1))  # From top-right
        directional_light.setColor((0.9, 0.9, 0.8, 1))   # Bright warm white
        directional_np = self.base.render.attachNewNode(directional_light)
        self.base.render.setLight(directional_np)
        self.lights['directional'] = directional_np
        
        # Secondary directional light from opposite side for fill lighting
        fill_light = DirectionalLight('fill_light')
        fill_light.setDirection(Vec3(1, 1, -0.5))  # From bottom-left, less steep
        fill_light.setColor((0.3, 0.3, 0.4, 1))   # Dimmer blue fill
        fill_np = self.base.render.attachNewNode(fill_light)
        self.base.render.setLight(fill_np)
        self.lights['fill'] = fill_np
        
        print("✓ Basic lighting setup complete")
        print("  - Ambient light: Blue-tinted for space atmosphere")
        print("  - Directional light: Warm white from top-right")
        
    def setup_asteroid_fields(self):
        """Generate enhanced asteroid fields around the starting base"""
        # Get world dimensions and base position from config
        display_config = self.config.game.get("display", {})
        world_width = display_config.get("world_width", 4800)
        world_height = display_config.get("world_height", 2700)
        
        # Base is at world center
        base_x = world_width / 2
        base_y = world_height / 2
        
        # Generate enhanced asteroid fields with more clusters and mineral values
        self.asteroid_nodes = self.entity_visualizer.generate_enhanced_asteroid_fields(
            base_x, base_y, world_width, world_height
        )
        
    def add_entity_visual(self, entity_type, entity_id, x, y, radius=20):
        """Add a visual representation of a game entity"""
        if entity_type == 'building':
            return self.entity_visualizer.create_building_visual(entity_id, x, y, radius)
        elif entity_type == 'enemy':
            return self.entity_visualizer.create_enemy_visual(entity_id, x, y, radius)
        elif entity_type == 'asteroid':
            return self.entity_visualizer.create_asteroid_visual(x, y, radius)
        return None
        
    def remove_entity_visual(self, visual_node):
        """Remove a visual entity from the scene"""
        if visual_node:
            visual_node.removeNode()
            
    def create_range_indicator(self, radius, color=(1, 1, 1, 0.3)):
        """Create a range indicator for building placement"""
        return self.entity_visualizer.create_range_indicator(radius, color)
        
    def update(self, dt):
        """Update scene elements"""
        # Starfield parallax is updated by camera system
        pass
        
    def update_starfield_parallax(self, camera_x, camera_y):
        """Update starfield parallax based on camera position"""
        if self.starfield:
            self.starfield.update_parallax(camera_x, camera_y)
            
    def set_starfield_camera_position(self, camera_x, camera_y):
        """Set initial starfield camera position"""
        if self.starfield:
            self.starfield.set_camera_position(camera_x, camera_y)
    
    def update_power_network(self, buildings):
        """Update power network visualization"""
        if hasattr(self, 'power_network_renderer'):
            self.power_network_renderer.update_power_network(buildings)
        
    def cleanup(self):
        """Clean up scene resources"""
        print("Cleaning up scene...")
        
        # Clean up starfield
        if hasattr(self, 'starfield') and self.starfield:
            self.starfield.cleanup()
        
        # Clean up asteroids
        if hasattr(self, 'asteroid_nodes'):
            for asteroid in self.asteroid_nodes:
                asteroid.removeNode()
            self.asteroid_nodes.clear()
        
        # Clean up power network renderer
        if hasattr(self, 'power_network_renderer'):
            self.power_network_renderer.cleanup()
        
        # Clean up entity visualizer
        self.entity_visualizer.cleanup()
        
        # Clean up lights
        for light_name, light_np in self.lights.items():
            self.base.render.clearLight(light_np)
            light_np.removeNode()
        self.lights.clear()
        
        print("✓ Scene cleanup complete") 