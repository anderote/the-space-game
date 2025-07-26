"""
Arcade render system for handling game rendering.
"""

import arcade
import arcade.gl as gl
from typing import Optional
import random


class Star:
    def __init__(self, x, y, brightness, size):
        self.x = x
        self.y = y
        self.brightness = brightness
        self.size = size

class ArcadeRenderSystem:
    """Render system for Arcade implementation."""
    
    def __init__(self, ctx, width: int, height: int):
        self.ctx = ctx
        self.width = width
        self.height = height
        # Starfield layers (increased density by 50%)
        self.background_stars_deep = []
        self.background_stars_far = []
        self.background_stars_near = []
        self.background_stars_close = []  # New closest layer
        self.starfield_initialized = False
        # World size for star distribution
        self.world_width = 4800
        self.world_height = 2700
    
    def setup(self):
        """Initialize the render system."""
        self._generate_background_stars()
        print("Arcade render system setup complete")
    
    def _generate_background_stars(self):
        """Generate parallax background stars for four layers."""
        # Deep stars (tiny, very dim, barely move) - increased from 300 to 450
        self.background_stars_deep = [
            Star(
                random.randint(0, self.world_width),
                random.randint(0, self.world_height),
                random.randint(30, 70),
                1
            ) for _ in range(450)
        ]
        # Far stars (small, dim, move slowly) - increased from 200 to 300
        self.background_stars_far = [
            Star(
                random.randint(0, self.world_width),
                random.randint(0, self.world_height),
                random.randint(50, 100),
                1
            ) for _ in range(300)
        ]
        # Near stars (larger, brighter, move faster) - increased from 100 to 150
        self.background_stars_near = [
            Star(
                random.randint(0, self.world_width),
                random.randint(0, self.world_height),
                random.randint(100, 200),
                random.randint(1, 2)
            ) for _ in range(150)
        ]
        # Close stars (largest, brightest, move fastest) - new layer
        self.background_stars_close = [
            Star(
                random.randint(0, self.world_width),
                random.randint(0, self.world_height),
                random.randint(150, 255),
                random.randint(2, 3)
            ) for _ in range(75)
        ]
        self.starfield_initialized = True
    
    def render_background(self, camera=None):
        """Render background starfield with parallax layers."""
        if not self.starfield_initialized:
            self._generate_background_stars()
        
        if not camera:
            return  # Can't render without camera
        
        # Get camera position for parallax calculation
        cam_x = camera.x
        cam_y = camera.y
        cam_zoom = camera.zoom
        screen_w = camera.width
        screen_h = camera.height
        
        # Define parallax factors for each layer (closer = more movement)
        layers = [
            (self.background_stars_deep, 0.05, 0.8),    # Far stars, minimal parallax, dim
            (self.background_stars_far, 0.2, 1.0),      # Mid-distance stars
            (self.background_stars_near, 0.5, 1.2),     # Near stars, more parallax
            (self.background_stars_close, 1.0, 1.5)     # Closest stars, full parallax, bright
        ]
        
        for stars, parallax_factor, brightness_mult in layers:
            for star in stars:
                # Calculate parallax offset
                parallax_x = (star.x - cam_x * parallax_factor) * cam_zoom + screen_w // 2
                parallax_y = (star.y - cam_y * parallax_factor) * cam_zoom + screen_h // 2
                
                # Only draw stars visible on screen (with some margin)
                margin = 50
                if (-margin <= parallax_x <= screen_w + margin and 
                    -margin <= parallax_y <= screen_h + margin):
                    
                    # Adjust brightness and size based on layer
                    brightness = int(star.brightness * brightness_mult)
                    brightness = min(255, max(50, brightness))
                    
                    size = star.size * cam_zoom * brightness_mult
                    size = max(0.5, min(3.0, size))
                    
                    # Draw star
                    color = (brightness, brightness, brightness)
                    arcade.draw_circle_filled(parallax_x, parallax_y, size, color)
    
    def resize(self, width: int, height: int):
        """Handle window resize."""
        pass 