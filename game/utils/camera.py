"""
Camera system for handling viewport and world-to-screen transformations.
"""

import pygame
from settings import *


class Camera:
    """Camera system for handling viewport transformations."""
    
    def __init__(self):
        self.x = WORLD_WIDTH // 2  # Start at world center
        self.y = WORLD_HEIGHT // 2
        self.zoom = 1.0

    def update(self, keys):
        """Update camera position based on input."""
        # Arrow key panning
        if keys[pygame.K_LEFT]:
            self.x -= CAMERA_SPEED / self.zoom
        if keys[pygame.K_RIGHT]:
            self.x += CAMERA_SPEED / self.zoom
        if keys[pygame.K_UP]:
            self.y -= CAMERA_SPEED / self.zoom
        if keys[pygame.K_DOWN]:
            self.y += CAMERA_SPEED / self.zoom

        # Keep camera within world bounds
        self.x = max(0, min(WORLD_WIDTH, self.x))
        self.y = max(0, min(WORLD_HEIGHT, self.y))

    def zoom_in(self):
        """Zoom in the camera."""
        self.zoom = min(ZOOM_MAX, self.zoom + ZOOM_SPEED)

    def zoom_out(self):
        """Zoom out the camera."""
        self.zoom = max(ZOOM_MIN, self.zoom - ZOOM_SPEED)

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates."""
        screen_x = (world_x - self.x) * self.zoom + SCREEN_WIDTH // 2
        screen_y = (world_y - self.y) * self.zoom + SCREEN_HEIGHT // 2
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates."""
        world_x = (screen_x - SCREEN_WIDTH // 2) / self.zoom + self.x
        world_y = (screen_y - SCREEN_HEIGHT // 2) / self.zoom + self.y
        return world_x, world_y

    def is_visible(self, world_x, world_y, radius=0):
        """Check if a world position is visible on screen."""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        screen_radius = radius * self.zoom
        
        return (-screen_radius <= screen_x <= SCREEN_WIDTH + screen_radius and
                -screen_radius <= screen_y <= SCREEN_HEIGHT + screen_radius) 