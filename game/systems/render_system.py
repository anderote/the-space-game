"""
Render system that handles all drawing and visual effects.
"""

import pygame
import math
import random
from game.core.system_manager import System
from game.utils.camera import Camera
from settings import *


class RenderSystem(System):
    """System responsible for all rendering operations."""
    
    def __init__(self, screen, camera):
        super().__init__("RenderSystem")
        self.screen = screen
        self.camera = camera
        
        # Background stars for parallax
        self.background_stars_deep = []
        self.background_stars_far = []
        self.background_stars_near = []
        
        # Fonts
        self.font = None
        self.hud_font = None
        self.small_font = None
        self.title_font = None
        self.large_font = None
    
    def initialize(self):
        """Initialize the render system."""
        # Initialize fonts
        self.font = pygame.font.SysFont("Arial", 22, bold=False)
        self.hud_font = pygame.font.SysFont("Arial", 18, bold=False)
        self.small_font = pygame.font.SysFont("Arial", 14, bold=False)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        # Generate background stars
        self._generate_background_stars()
    
    def _generate_background_stars(self):
        """Generate parallax background stars."""
        # Deep stars (tiny, very dim, barely move)
        for _ in range(300):
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            brightness = random.randint(30, 70)
            size = 1
            self.background_stars_deep.append((x, y, brightness, size))

        # Far stars (small, dim, move slowly)
        for _ in range(200):
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            brightness = random.randint(50, 100)
            size = 1
            self.background_stars_far.append((x, y, brightness, size))

        # Near stars (larger, brighter, move faster)  
        for _ in range(100):
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            brightness = random.randint(100, 200)
            size = random.randint(1, 2)
            self.background_stars_near.append((x, y, brightness, size))
    
    def update(self, dt):
        """Update render system (minimal updates needed)."""
        pass
    
    def clear_screen(self):
        """Clear the screen with background color."""
        self.screen.fill(BLACK)
    
    def draw_background_stars(self):
        """Draw parallax background stars."""
        # Deep stars (slowest movement)
        for x, y, brightness, size in self.background_stars_deep:
            screen_x, screen_y = self.camera.world_to_screen(x, y)
            # Move at 0.1x camera speed for deep parallax
            offset_x = (self.camera.x - WORLD_WIDTH // 2) * 0.1
            offset_y = (self.camera.y - WORLD_HEIGHT // 2) * 0.1
            screen_x -= offset_x * self.camera.zoom
            screen_y -= offset_y * self.camera.zoom
            
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), size)

        # Far stars (medium movement)
        for x, y, brightness, size in self.background_stars_far:
            screen_x, screen_y = self.camera.world_to_screen(x, y)
            # Move at 0.3x camera speed
            offset_x = (self.camera.x - WORLD_WIDTH // 2) * 0.3
            offset_y = (self.camera.y - WORLD_HEIGHT // 2) * 0.3
            screen_x -= offset_x * self.camera.zoom
            screen_y -= offset_y * self.camera.zoom
            
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), size)

        # Near stars (normal movement)
        for x, y, brightness, size in self.background_stars_near:
            screen_x, screen_y = self.camera.world_to_screen(x, y)
            
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), size)
    
    def draw_base(self, base_pos, base_radius, base_health, max_health):
        """Draw the main base."""
        screen_x, screen_y = self.camera.world_to_screen(base_pos[0], base_pos[1])
        screen_radius = base_radius * self.camera.zoom
        
        if not self.camera.is_visible(base_pos[0], base_pos[1], base_radius):
            return
        
        # Base circle
        pygame.draw.circle(self.screen, BLUE, (int(screen_x), int(screen_y)), int(screen_radius))
        pygame.draw.circle(self.screen, WHITE, (int(screen_x), int(screen_y)), int(screen_radius), max(2, int(4 * self.camera.zoom)))
        
        # Health bar
        if base_health < max_health:
            health_ratio = base_health / max_health
            bar_width = screen_radius * 2
            bar_height = 8 * self.camera.zoom
            bar_x = screen_x - bar_width/2
            bar_y = screen_y - screen_radius - 15*self.camera.zoom
            
            self.draw_gradient_health_bar(bar_x, bar_y, bar_width, bar_height, health_ratio)
    
    def draw_gradient_health_bar(self, x, y, width, height, health_ratio):
        """Draw a health bar with red-to-green gradient."""
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height))
        
        # Calculate gradient colors based on health ratio
        if health_ratio > 0.6:
            # Green to yellow
            r = int(255 * (1 - health_ratio) * 2.5)
            g = 255
            b = 0
        elif health_ratio > 0.3:
            # Yellow to orange  
            r = 255
            g = int(255 * ((health_ratio - 0.3) / 0.3))
            b = 0
        else:
            # Orange to red
            r = 255
            g = int(255 * (health_ratio / 0.3) * 0.5)
            b = 0
        
        # Draw the health bar with gradient
        health_width = int(width * health_ratio)
        if health_width > 0:
            pygame.draw.rect(self.screen, (r, g, b), (x, y, health_width, height))
        
        # Glass effect on health bar
        pygame.draw.rect(self.screen, (255, 255, 255, 100), (x, y, width, height//2))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, width, height), 1)
    
    def draw_glass_panel(self, x, y, width, height, alpha=180):
        """Draw a glass-like panel with transparency and subtle highlights."""
        # Create the main panel surface
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Main glass background with transparency
        panel_surface.fill((20, 25, 35, alpha))
        
        # Subtle gradient effect - lighter at top
        for i in range(height // 3):
            alpha_gradient = min(255, max(0, alpha + (30 - i)))
            r = min(255, max(0, 30 + i//2))
            g = min(255, max(0, 35 + i//2))
            b = min(255, max(0, 45 + i//2))
            gradient_color = (r, g, b, alpha_gradient)
            pygame.draw.rect(panel_surface, gradient_color, (0, i, width, 1))
        
        # Glass highlight on top edge
        pygame.draw.rect(panel_surface, (60, 80, 120, 200), (0, 0, width, 2))
        
        # Subtle side highlights
        pygame.draw.rect(panel_surface, (40, 60, 100, 150), (0, 0, 2, height))
        pygame.draw.rect(panel_surface, (40, 60, 100, 150), (width-2, 0, 2, height))
        
        # Bottom shadow
        pygame.draw.rect(panel_surface, (10, 15, 25, 200), (0, height-2, width, 2))
        
        # Outer glass border
        pygame.draw.rect(panel_surface, (80, 100, 140, 180), (0, 0, width, height), 2)
        
        self.screen.blit(panel_surface, (x, y))
        return panel_surface
    
    def draw_range_indicator(self, world_x, world_y, range_val, color=(255, 255, 255, 100)):
        """Draw a range indicator circle."""
        screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
        screen_range = range_val * self.camera.zoom

        # Draw range circle
        if screen_range > 5:  # Only draw if visible
            pygame.draw.circle(self.screen, color[:3], (int(screen_x), int(screen_y)), int(screen_range), 2)
    
    def draw_power_connections(self, power_grid):
        """Draw power grid connections."""
        connections = power_grid.get_connections()
        
        for x1, y1, x2, y2 in connections:
            screen_x1, screen_y1 = self.camera.world_to_screen(x1, y1)
            screen_x2, screen_y2 = self.camera.world_to_screen(x2, y2)
            
            # Check if connection is visible on screen
            if ((-50 <= screen_x1 <= SCREEN_WIDTH + 50 and -50 <= screen_y1 <= SCREEN_HEIGHT + 50) or
                (-50 <= screen_x2 <= SCREEN_WIDTH + 50 and -50 <= screen_y2 <= SCREEN_HEIGHT + 50)):
                
                # Draw connection line with slight glow effect
                line_width = max(1, int(3 * self.camera.zoom))
                
                # Outer glow
                pygame.draw.line(self.screen, (50, 150, 255), 
                               (int(screen_x1), int(screen_y1)), 
                               (int(screen_x2), int(screen_y2)), 
                               line_width + 2)
                
                # Main line
                pygame.draw.line(self.screen, (100, 200, 255), 
                               (int(screen_x1), int(screen_y1)), 
                               (int(screen_x2), int(screen_y2)), 
                               line_width)
    
    def draw_minimap(self, asteroids, buildings, enemies, base_pos, camera):
        """Draw minimap in lower left corner."""
        minimap_size = 150
        minimap_x = 10
        minimap_y = self.screen.get_height() - minimap_size - 10
        
        # Create minimap surface with alpha
        minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        
        # Background with glass effect
        bg_color = (20, 20, 40, 180)
        pygame.draw.rect(minimap_surface, bg_color, (0, 0, minimap_size, minimap_size))
        pygame.draw.rect(minimap_surface, (100, 100, 150, 100), (0, 0, minimap_size, minimap_size), 2)
        
        # Define world bounds for minimap scaling
        world_size = 4000  # Approximate world size
        scale = minimap_size / world_size
        center_offset = world_size / 2
        
        # Draw asteroids as small gray dots with size variation
        for asteroid in asteroids:
            map_x = int((asteroid.x + center_offset) * scale)
            map_y = int((asteroid.y + center_offset) * scale)
            if 0 <= map_x < minimap_size and 0 <= map_y < minimap_size:
                # Size based on asteroid radius
                dot_size = max(1, min(3, int(asteroid.radius / 20)))
                color = (120, 120, 120) if asteroid.minerals > 0 else (80, 80, 80)
                pygame.draw.circle(minimap_surface, color, (map_x, map_y), dot_size)
        
        # Draw buildings with type-specific colors
        building_colors = {
            'connector': (255, 255, 0),    # Yellow
            'solar': (0, 200, 255),        # Cyan  
            'battery': (180, 0, 180),      # Purple
            'miner': (0, 255, 0),          # Green
            'turret': (255, 100, 0),       # Orange
            'laser': (100, 150, 255),      # Light Blue
            'superlaser': (255, 50, 255),  # Magenta
            'repair': (0, 255, 255),       # Cyan
            'converter': (255, 255, 100)   # Light Yellow
        }
        
        for building in buildings:
            map_x = int((building.x + center_offset) * scale)
            map_y = int((building.y + center_offset) * scale)
            if 0 <= map_x < minimap_size and 0 <= map_y < minimap_size:
                base_color = building_colors.get(building.type, (255, 255, 255))
                # Dim color if not powered
                if not building.powered:
                    color = tuple(c // 2 for c in base_color)
                else:
                    color = base_color
                
                # Size based on building importance
                if building.type in ['turret', 'laser', 'superlaser']:
                    size = 3  # Combat buildings larger
                elif building.type in ['solar', 'battery']:
                    size = 2  # Power buildings medium
                else:
                    size = 2  # Other buildings medium
                
                pygame.draw.circle(minimap_surface, color, (map_x, map_y), size)
        
        # Draw base with pulsing effect
        base_map_x = int((base_pos[0] + center_offset) * scale)
        base_map_y = int((base_pos[1] + center_offset) * scale)
        import time
        pulse = 0.8 + 0.2 * math.sin(time.time() * 3)  # Pulse between 0.8 and 1.0
        base_size = int(4 * pulse)
        pygame.draw.circle(minimap_surface, (0, 200, 255), (base_map_x, base_map_y), base_size)
        pygame.draw.circle(minimap_surface, (255, 255, 255), (base_map_x, base_map_y), 2)
        
        # Draw enemies with type-specific colors and sizes
        enemy_colors = {
            'basic': (255, 0, 0),      # Red
            'large': (255, 100, 0),    # Orange
            'kamikaze': (255, 50, 150) # Pink
        }
        
        for enemy in enemies:
            map_x = int((enemy.x + center_offset) * scale)
            map_y = int((enemy.y + center_offset) * scale)
            if 0 <= map_x < minimap_size and 0 <= map_y < minimap_size:
                enemy_type = getattr(enemy, 'enemy_type', 'basic')
                color = enemy_colors.get(enemy_type, (255, 0, 0))
                
                # Size based on enemy type
                if hasattr(enemy, 'is_mothership'):
                    size = 4  # Motherships largest
                elif enemy_type == 'large':
                    size = 3  # Large ships bigger
                elif enemy_type == 'kamikaze':
                    size = 1  # Kamikaze smallest
                else:
                    size = 2  # Basic enemies medium
                
                pygame.draw.circle(minimap_surface, color, (map_x, map_y), size)
        
        # Draw camera view area
        cam_size = 800 * scale  # Approximate camera view size
        cam_x = int((camera.x + center_offset) * scale - cam_size / 2)
        cam_y = int((camera.y + center_offset) * scale - cam_size / 2)
        pygame.draw.rect(minimap_surface, (255, 255, 0, 100), 
                        (cam_x, cam_y, cam_size, cam_size), 1)
        
        # Blit minimap to screen
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))

    def present(self):
        """Present the rendered frame to the screen."""
        pygame.display.flip() 