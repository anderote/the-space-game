"""
Panda3D Camera Controller - Phase 1 Basic Implementation
Sets up top-down orthographic camera for the game
"""

from panda3d.core import OrthographicLens

class Panda3DCamera:
    """Camera controller for top-down view matching the original game"""
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Camera state
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        
        # Get world dimensions from config
        display_config = config.game.get("display", {})
        self.world_width = display_config.get("world_width", 4800)
        self.world_height = display_config.get("world_height", 2700)
        self.screen_width = display_config.get("screen_width", 1600)
        self.screen_height = display_config.get("screen_height", 900)
        
        # Camera configuration
        camera_config = config.game.get("camera", {})
        self.zoom_min = camera_config.get("zoom_min", 0.5)
        self.zoom_max = camera_config.get("zoom_max", 5.0)
        
        self.setup_camera()
        
    def setup_camera(self):
        """Set up orthographic top-down camera"""
        print("Setting up orthographic camera...")
        
        # Create orthographic lens for 2D top-down view
        lens = OrthographicLens()
        
        # Set up lens dimensions based on screen size
        # This creates a top-down view similar to the original Pygame version
        lens.setFilmSize(self.screen_width, self.screen_height)
        lens.setNearFar(-1000, 1000)
        
        # Apply the lens to the camera
        self.base.cam.node().setLens(lens)
        
        # Position camera above the world center
        world_center_x = self.world_width / 2
        world_center_y = self.world_height / 2
        camera_height = 100
        
        self.base.camera.setPos(world_center_x, world_center_y, camera_height)
        self.base.camera.lookAt(world_center_x, world_center_y, 0)
        
        # Set initial camera position
        self.x = world_center_x
        self.y = world_center_y
        
        print(f"✓ Camera positioned at world center: ({world_center_x}, {world_center_y})")
        print(f"✓ World dimensions: {self.world_width} x {self.world_height}")
        
    def update(self, dt):
        """Update camera (Phase 1: basic placeholder)"""
        # In Phase 2, this will handle smooth camera movement and zoom
        # For Phase 1, camera stays fixed at world center
        pass
        
    def set_position(self, x, y):
        """Set camera position (for Phase 2+)"""
        self.x = x
        self.y = y
        # Will implement smooth camera movement in Phase 2
        
    def set_zoom(self, zoom):
        """Set camera zoom (for Phase 2+)"""
        self.zoom = max(self.zoom_min, min(self.zoom_max, zoom))
        # Will implement zoom functionality in Phase 2
        
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        # Basic conversion for Phase 1
        # Will be enhanced in Phase 2 with proper camera transforms
        screen_x = world_x - self.x + (self.screen_width / 2)
        screen_y = world_y - self.y + (self.screen_height / 2)
        return screen_x, screen_y
        
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        # Basic conversion for Phase 1
        # Will be enhanced in Phase 2 with proper camera transforms
        world_x = screen_x - (self.screen_width / 2) + self.x
        world_y = screen_y - (self.screen_height / 2) + self.y
        return world_x, world_y 