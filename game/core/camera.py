"""
Arcade camera system for handling view transformations and zoom.
"""

import arcade
import arcade.gl as gl
from typing import Tuple
import math


class ArcadeCamera:
    """Camera system for Arcade implementation with zoom and pan support."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Camera position and zoom
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 5.0
        
        # Camera movement
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_zoom = 1.0
        self.camera_speed = 10.0
        self.zoom_speed = 0.1
        
        # View matrices
        self.view_matrix = None
        self.projection_matrix = None
        self._update_matrices()
        
    def _update_matrices(self):
        """Update view and projection matrices."""
        # Create projection matrix (orthographic)
        half_width = self.width / (2.0 * self.zoom)
        half_height = self.height / (2.0 * self.zoom)
        
        self.projection_matrix = arcade.create_orthogonal_projection(
            -half_width, half_width,
            -half_height, half_height,
            -1, 1
        )
        
        # Create view matrix (translation)
        self.view_matrix = arcade.create_translation_matrix(
            -self.x, -self.y, 0
        )
        
    def update(self, delta_time: float):
        """Update camera position and zoom with smooth interpolation."""
        # Smooth camera movement
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dz = self.target_zoom - self.zoom
        
        move_speed = self.camera_speed * delta_time
        zoom_speed = self.zoom_speed * delta_time
        
        if abs(dx) > 0.1:
            self.x += dx * move_speed
        if abs(dy) > 0.1:
            self.y += dy * move_speed
        if abs(dz) > 0.01:
            self.zoom += dz * zoom_speed
            
        # Clamp zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
        
        # Update matrices
        self._update_matrices()
        
    def apply(self):
        """Apply camera transformation to the current context."""
        if self.projection_matrix and self.view_matrix:
            # Set projection matrix
            arcade.gl.glMatrixMode(arcade.gl.GL_PROJECTION)
            arcade.gl.glLoadMatrixf(self.projection_matrix)
            
            # Set view matrix
            arcade.gl.glMatrixMode(arcade.gl.GL_MODELVIEW)
            arcade.gl.glLoadMatrixf(self.view_matrix)
            
    def reset(self):
        """Reset camera to identity transformation for UI rendering."""
        arcade.gl.glMatrixMode(arcade.gl.GL_PROJECTION)
        arcade.gl.glLoadIdentity()
        arcade.gl.glOrtho(0, self.width, 0, self.height, -1, 1)
        
        arcade.gl.glMatrixMode(arcade.gl.GL_MODELVIEW)
        arcade.gl.glLoadIdentity()
        
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
        self._update_matrices()
        
    def set_target_position(self, x: float, y: float):
        """Set target camera position for smooth movement."""
        self.target_x = x
        self.target_y = y
        
    def set_zoom(self, zoom: float):
        """Set camera zoom level."""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        self.target_zoom = self.zoom
        self._update_matrices()
        
    def set_target_zoom(self, zoom: float):
        """Set target zoom level for smooth zooming."""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
    def zoom_in(self, factor: float = 1.2):
        """Zoom in by the given factor."""
        self.set_target_zoom(self.zoom * factor)
        
    def zoom_out(self, factor: float = 1.2):
        """Zoom out by the given factor."""
        self.set_target_zoom(self.zoom / factor)
        
    def resize(self, width: int, height: int):
        """Handle window resize."""
        self.width = width
        self.height = height
        self._update_matrices()
        
    def is_visible(self, x: float, y: float, radius: float) -> bool:
        """Check if a world object is visible in the camera view."""
        screen_x, screen_y = self.world_to_screen(x, y)
        screen_radius = radius * self.zoom
        
        return (screen_x + screen_radius >= 0 and 
                screen_x - screen_radius <= self.width and
                screen_y + screen_radius >= 0 and 
                screen_y - screen_radius <= self.height) 