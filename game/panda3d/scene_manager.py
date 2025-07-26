"""
Panda3D Scene Manager - Phase 3 Implementation
Manages the 3D scene, lighting, starfield background, and entity visualization
"""

from panda3d.core import AmbientLight, DirectionalLight, Vec3
from .entity_visualizer import EntityVisualizer
from .starfield import StarfieldSystem

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
        
        self.setup_scene()
        
    def setup_scene(self):
        """Set up the complete 3D scene"""
        print("Setting up Phase 3 scene...")
        
        self.setup_background()
        self.setup_basic_lighting()
        
        # Create test entities for Phase 2 visualization (will be replaced by real buildings)
        # self.entity_visualizer.create_test_entities()
        
        print("✓ Phase 3 scene setup complete")
        
    def setup_background(self):
        """Set up the scene background"""
        # Set background color to dark space (15, 15, 32) normalized to 0-1
        self.base.setBackgroundColor(15/255, 15/255, 32/255, 1.0)
        print("✓ Background color set to dark space")
        
    def setup_basic_lighting(self):
        """Set up basic lighting for visibility"""
        print("Setting up lighting...")
        
        # Ambient light for general visibility
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.3, 0.3, 0.4, 1))  # Slightly blue ambient
        ambient_np = self.base.render.attachNewNode(ambient_light)
        self.base.render.setLight(ambient_np)
        self.lights['ambient'] = ambient_np
        
        # Directional light for depth and shadows
        directional_light = DirectionalLight('directional_light')
        directional_light.setDirection(Vec3(-1, -1, -1))  # From top-right
        directional_light.setColor((0.7, 0.7, 0.6, 1))   # Warm white
        directional_np = self.base.render.attachNewNode(directional_light)
        self.base.render.setLight(directional_np)
        self.lights['directional'] = directional_np
        
        print("✓ Basic lighting setup complete")
        print("  - Ambient light: Blue-tinted for space atmosphere")
        print("  - Directional light: Warm white from top-right")
        
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
        
    def cleanup(self):
        """Clean up scene resources"""
        print("Cleaning up scene...")
        
        # Clean up starfield
        if hasattr(self, 'starfield') and self.starfield:
            self.starfield.cleanup()
        
        # Clean up entity visualizer
        self.entity_visualizer.cleanup()
        
        # Clean up lights
        for light_name, light_np in self.lights.items():
            self.base.render.clearLight(light_np)
            light_np.removeNode()
        self.lights.clear()
        
        print("✓ Scene cleanup complete") 