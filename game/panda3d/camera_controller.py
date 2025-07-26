"""
Panda3D Camera Controller - Phase 2 Implementation
Supports WASD movement, mouse zoom, and smooth camera transitions
"""

from panda3d.core import OrthographicLens
import math

class Panda3DCamera:
    """Camera controller for top-down view with interactive controls"""
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Camera state
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_x = 0
        self.target_y = 0
        self.target_zoom = 1.0
        
        # Movement parameters
        self.camera_speed = 500.0  # pixels per second (increased from Phase 1)
        self.zoom_speed = 2.0      # zoom changes per second
        self.smooth_factor = 8.0   # smoothing interpolation factor
        
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
        
        # Camera bounds padding (how close camera can get to world edge)
        self.padding = 200
        
        self.setup_camera()
        
    def setup_camera(self):
        """Set up orthographic top-down camera"""
        print("Setting up interactive camera...")
        
        # Create orthographic lens for 2D top-down view
        self.lens = OrthographicLens()
        
        # Set up lens dimensions based on screen size
        self.update_lens_size()
        self.lens.setNearFar(-1000, 1000)
        
        # Apply the lens to the camera
        self.base.cam.node().setLens(self.lens)
        
        # Position camera above the world center
        world_center_x = self.world_width / 2
        world_center_y = self.world_height / 2
        
        # Set initial position
        self.x = world_center_x
        self.y = world_center_y
        self.target_x = world_center_x
        self.target_y = world_center_y
        
        self.update_camera_position()
        
        print(f"✓ Interactive camera setup at world center: ({world_center_x}, {world_center_y})")
        print(f"✓ Camera bounds: {self.world_width} x {self.world_height}")
        print("✓ WASD movement and mouse zoom enabled")
        
    def update_lens_size(self):
        """Update the orthographic lens size based on zoom"""
        # Orthographic lens size affects the viewing area
        film_width = self.screen_width / self.zoom
        film_height = self.screen_height / self.zoom
        self.lens.setFilmSize(film_width, film_height)
        
    def update(self, dt):
        """Update camera with smooth interpolation"""
        # Smooth interpolation towards target position
        lerp_factor = min(1.0, self.smooth_factor * dt)
        
        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor
        self.zoom += (self.target_zoom - self.zoom) * lerp_factor
        
        # Update camera position
        self.update_camera_position()
        
    def update_camera_position(self):
        """Update the actual Panda3D camera position"""
        camera_height = 100
        
        # Update lens for new zoom level
        self.update_lens_size()
        
        # Position camera
        self.base.camera.setPos(self.x, self.y, camera_height)
        self.base.camera.lookAt(self.x, self.y, 0)
        
    def move_camera(self, dx, dy, dt):
        """Move camera by delta amounts with bounds checking"""
        # Apply speed and delta time
        move_x = dx * self.camera_speed * dt / self.zoom  # Zoom affects movement speed
        move_y = dy * self.camera_speed * dt / self.zoom
        
        # Update target position
        self.target_x += move_x
        self.target_y += move_y
        
        # Clamp to world bounds with padding
        view_width = self.screen_width / (2 * self.zoom)
        view_height = self.screen_height / (2 * self.zoom)
        
        self.target_x = max(view_width + self.padding, 
                           min(self.world_width - view_width - self.padding, self.target_x))
        self.target_y = max(view_height + self.padding,
                           min(self.world_height - view_height - self.padding, self.target_y))
        
    def set_zoom(self, zoom_delta):
        """Adjust zoom level"""
        self.target_zoom = max(self.zoom_min, min(self.zoom_max, self.target_zoom + zoom_delta))
        
    def zoom_in(self, amount=0.1):
        """Zoom in by specified amount"""
        self.set_zoom(amount)
        
    def zoom_out(self, amount=0.1):
        """Zoom out by specified amount"""
        self.set_zoom(-amount)
        
    def center_on_position(self, x, y):
        """Instantly center camera on a world position"""
        self.target_x = x
        self.target_y = y
        
        # Apply bounds checking
        view_width = self.screen_width / (2 * self.zoom)
        view_height = self.screen_height / (2 * self.zoom)
        
        self.target_x = max(view_width + self.padding,
                           min(self.world_width - view_width - self.padding, self.target_x))
        self.target_y = max(view_height + self.padding,
                           min(self.world_height - view_height - self.padding, self.target_y))
        
    def reset_zoom(self):
        """Reset zoom to default level"""
        self.target_zoom = 1.0
        
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        # Calculate relative position from camera center
        rel_x = (world_x - self.x) * self.zoom
        rel_y = (world_y - self.y) * self.zoom
        
        # Convert to screen coordinates (center of screen is 0,0)
        screen_x = rel_x + (self.screen_width / 2)
        screen_y = rel_y + (self.screen_height / 2)
        
        return screen_x, screen_y
        
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        # Convert from screen coordinates (relative to screen center)
        rel_x = screen_x - (self.screen_width / 2)
        rel_y = screen_y - (self.screen_height / 2)
        
        # Apply zoom and camera position
        world_x = (rel_x / self.zoom) + self.x
        world_y = (rel_y / self.zoom) + self.y
        
        return world_x, world_y
        
    def get_camera_bounds(self):
        """Get the current camera view bounds in world coordinates"""
        # Calculate view area in world coordinates
        view_width = self.screen_width / (2 * self.zoom)
        view_height = self.screen_height / (2 * self.zoom)
        
        left = self.x - view_width
        right = self.x + view_width
        top = self.y - view_height
        bottom = self.y + view_height
        
        return left, right, top, bottom
        
    def is_position_visible(self, world_x, world_y, margin=0):
        """Check if a world position is visible in the current camera view"""
        left, right, top, bottom = self.get_camera_bounds()
        
        return (left - margin <= world_x <= right + margin and 
                top - margin <= world_y <= bottom + margin) 