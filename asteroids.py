"""
Asteroid class for Space Game Clone.
"""
import numpy as np
import pygame
import random
import noise
from settings import ASTEROID_BASE_MINERALS, ASTEROID_MINERAL_PER_RADIUS, ASTEROID_MIN_RADIUS, ASTEROID_MAX_RADIUS

class DamageNumber:
    def __init__(self, x, y, amount, color=(255, 255, 0)):
        self.x = x
        self.y = y
        self.amount = amount
        self.color = color
        self.lifetime = 72  # 1.2 seconds at 60fps
        self.max_lifetime = 180
        self.vy = -1  # Float upward
    
    def update(self):
        self.y += self.vy
        self.lifetime -= 1
    
    def draw(self, surface, camera):
        if self.lifetime <= 0:
            return
        
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Create a surface with per-pixel alpha for the text
        font = pygame.font.SysFont("Arial", max(16, int(20 * camera.zoom)))
        text_surface = font.render(f"+{int(self.amount)}" if self.amount > 0 else f"{int(self.amount)}", True, self.color[:3])
        
        # Create a new surface with alpha
        faded_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        faded_surface.fill((*self.color[:3], alpha))
        faded_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Blit to main surface
        surface.blit(faded_surface, (screen_x - faded_surface.get_width()//2, screen_y - faded_surface.get_height()//2))

class Asteroid:
    def __init__(self, x, y, radius=None, minerals=None):
        self.x = x
        self.y = y
        self.radius = radius if radius is not None else random.randint(ASTEROID_MIN_RADIUS, ASTEROID_MAX_RADIUS)
        self.minerals = minerals if minerals is not None else ASTEROID_BASE_MINERALS + self.radius * ASTEROID_MINERAL_PER_RADIUS
        self.points = self.generate_points()
        self.show_resources = False  # Only show when clicked
        self.show_timer = 0
        
        # Determine asteroid type based on size for image selection
        if self.radius < 30:
            self.size_type = 'small'
        elif self.radius < 45:
            self.size_type = 'medium'
        else:
            self.size_type = 'large'
        
        # Select random image variant for this asteroid
        self.image_variant = 0
        if hasattr(Asteroid, 'asteroid_images') and Asteroid.asteroid_images:
            if isinstance(Asteroid.asteroid_images[self.size_type], list):
                self.image_variant = random.randint(0, len(Asteroid.asteroid_images[self.size_type]) - 1)
    
    # Class variable for asteroid images (will be set from main.py)
    asteroid_images = None

    def generate_points(self, num_points=10):
        # Use Perlin noise for irregular polygon
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points = []
        seed = random.random() * 1000
        for i, angle in enumerate(angles):
            r = self.radius * (0.8 + 0.4 * noise.pnoise1(seed + i * 0.2))
            px = self.x + r * np.cos(angle)
            py = self.y + r * np.sin(angle)
            points.append((px, py))
        return points
    
    def clicked(self):
        """Call this when asteroid is clicked to show resources temporarily"""
        self.show_resources = True
        self.show_timer = 300  # Show for 5 seconds

    def draw(self, surface, camera_x, camera_y, zoom):
        # Transform world coordinates to screen coordinates
        screen_x = (self.x - camera_x) * zoom + surface.get_width() // 2
        screen_y = (self.y - camera_y) * zoom + surface.get_height() // 2
        screen_radius = self.radius * zoom
        
        # Don't draw if completely off screen
        if (screen_x < -screen_radius or screen_x > surface.get_width() + screen_radius or
            screen_y < -screen_radius or screen_y > surface.get_height() + screen_radius):
            return
        
        # Use asteroid image if available
        if (hasattr(Asteroid, 'asteroid_images') and Asteroid.asteroid_images and 
            self.size_type in Asteroid.asteroid_images):
            
            # Get the appropriate image
            image_source = Asteroid.asteroid_images[self.size_type]
            if isinstance(image_source, list):
                asteroid_image = image_source[self.image_variant]
            else:
                asteroid_image = image_source
            
            # Scale image to match asteroid size
            target_size = int(screen_radius * 1.8)  # Reduced from 2.2 to remove ~10px border
            scaled_image = pygame.transform.scale(asteroid_image, (target_size, target_size))
            
            # Center the image
            image_rect = scaled_image.get_rect(center=(int(screen_x), int(screen_y)))
            surface.blit(scaled_image, image_rect)
        else:
            # Fallback to original polygon drawing
            screen_points = []
            for px, py in self.points:
                screen_point_x = (px - camera_x) * zoom + surface.get_width() // 2
                screen_point_y = (py - camera_y) * zoom + surface.get_height() // 2
                screen_points.append((screen_point_x, screen_point_y))
            
            color = (100, 100, 100)
            pygame.draw.polygon(surface, color, screen_points)
        
        # Update show timer
        if self.show_timer > 0:
            self.show_timer -= 1
            if self.show_timer <= 0:
                self.show_resources = False
        
        # Show mineral amount when clicked or zoomed in close
        if self.show_resources or zoom > 1.2:
            font = pygame.font.SysFont("Arial", max(12, int(18 * zoom)))
            text = font.render(str(int(self.minerals)), True, (200, 200, 0))
            surface.blit(text, (screen_x - text.get_width()//2, screen_y - text.get_height()//2)) 