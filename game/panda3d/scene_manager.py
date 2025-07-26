"""
Panda3D Scene Manager - Phase 1 Basic Implementation
Sets up basic lighting and scene for the game world
"""

from panda3d.core import AmbientLight, DirectionalLight, Vec3

class SceneManager:
    """Manages the 3D scene setup and lighting"""
    
    def __init__(self, base):
        self.base = base
        self.lights = {}
        
        # Set up the basic scene
        self.setup_scene()
        
    def setup_scene(self):
        """Set up the basic 3D scene"""
        print("Setting up 3D scene...")
        
        # Set background color to space-like dark
        self.base.setBackgroundColor(0.05, 0.05, 0.1, 1)
        
        # Set up lighting
        self.setup_basic_lighting()
        
        # Set up coordinate system
        # Panda3D uses Y-forward, Z-up by default
        # We'll work in X-right, Y-up, Z-forward for top-down view
        
        print("✓ Scene setup complete")
        
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
        
    def create_test_objects(self):
        """Create some test objects to verify the scene (Phase 1 testing)"""
        # In Phase 2, we'll replace this with actual game entities
        # For Phase 1, we can add simple objects to test the scene
        
        # Create a simple cube at world center for testing
        from panda3d.core import CardMaker
        
        card = CardMaker("test_ground")
        card.setFrame(-100, 100, -100, 100)
        test_ground = self.base.render.attachNewNode(card.generate())
        test_ground.setPos(2400, 1350, 0)  # World center from config
        test_ground.setColor(0.2, 0.3, 0.2, 1)  # Dark green
        
        print("✓ Test ground plane created at world center")
        
        return test_ground
        
    def update_lighting_for_game_state(self, game_state):
        """Update lighting based on game state (for future phases)"""
        # Phase 4 will implement dynamic lighting based on:
        # - Power network state
        # - Combat effects
        # - Building states
        pass
        
    def cleanup(self):
        """Clean up scene resources"""
        print("Cleaning up scene...")
        
        # Remove all lights
        for light_name, light_np in self.lights.items():
            self.base.render.clearLight(light_np)
            light_np.removeNode()
            
        self.lights.clear()
        print("✓ Scene cleanup complete") 