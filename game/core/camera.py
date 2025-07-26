"""
Arcade camera system for handling view transformations and zoom.
"""

import arcade
from typing import Tuple
import math


class ArcadeCamera:
    """Camera system for Arcade implementation with zoom and pan support."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # World bounds
        self.world_width = 4800
        self.world_height = 2700
        
        # Camera position and zoom - start at world center
        self.x = 2400.0  # Center of world width
        self.y = 1350.0  # Center of world height
        self.zoom = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        
        # Camera movement smoothing
        self.target_x = self.x
        self.target_y = self.y
        self.target_zoom = 1.0
        self.camera_speed = 8.0
        self.zoom_speed = 0.15
        
        print(f"Camera initialized at ({self.x}, {self.y}) with zoom {self.zoom}")
        
    def update(self, dt: float):
        """Update camera with smooth interpolation."""
        # Smooth camera movement
        lerp_factor = min(1.0, self.camera_speed * dt)
        
        old_x, old_y = self.x, self.y
        
        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor
        self.zoom += (self.target_zoom - self.zoom) * lerp_factor
        
        # Clamp zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
        
        # Clamp position to world bounds
        half_width = self.width / (2 * self.zoom)
        half_height = self.height / (2 * self.zoom)
        
        self.x = max(half_width, min(self.world_width - half_width, self.x))
        self.y = max(half_height, min(self.world_height - half_height, self.y))
        
        # Update targets to match clamped values
        self.target_x = self.x
        self.target_y = self.y
        self.target_zoom = self.zoom
        
        # Debug camera movement
        if abs(old_x - self.x) > 1 or abs(old_y - self.y) > 1:
            print(f"Camera moved to ({self.x:.1f}, {self.y:.1f})")
    
    def follow_target(self, x: float, y: float):
        """Set camera to follow a target position."""
        self.target_x = x
        self.target_y = y
    
    def set_zoom(self, zoom: float):
        """Set target zoom level."""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, zoom))
    
    def zoom_in(self, amount: float = 0.1):
        """Zoom in by amount."""
        self.set_zoom(self.zoom + amount)
    
    def zoom_out(self, amount: float = 0.1):
        """Zoom out by amount."""
        self.set_zoom(self.zoom - amount)
        
    def apply(self):
        """Apply camera transformation (no-op for now, we'll handle translation manually)."""
        # For now, we'll handle camera translation in each render call
        # This avoids complex OpenGL projection matrix issues
        pass
            
    def reset(self):
        """Reset camera transformation (no-op for now)."""
        # No-op since we're handling translation manually
        pass
        
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        screen_x = (world_x - self.x) * self.zoom + self.width / 2
        screen_y = (world_y - self.y) * self.zoom + self.height / 2
        return screen_x, screen_y
        
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = (screen_x - self.width / 2) / self.zoom + self.x
        world_y = (screen_y - self.height / 2) / self.zoom + self.y
        return world_x, world_y
        
    def set_position(self, x: float, y: float):
        """Set camera position."""
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        print(f"Camera position set to ({self.x}, {self.y})")
        
    def get_position(self) -> Tuple[float, float]:
        """Get current camera position."""
        return self.x, self.y
    
    def resize(self, width: int, height: int):
        """Handle window resize."""
        self.width = width
        self.height = height
        print(f"Camera resized to {width}x{height}") 