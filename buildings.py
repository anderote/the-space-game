"""
Building classes for Space Game Clone.
"""
import pygame
import numpy as np
import math
from dataclasses import dataclass, field
from typing import Tuple
from settings import *

HEX_POINTS = 6

def draw_selection_indicator(surface, x, y, radius, shape='circle'):
    """Draw a semi-transparent yellow selection indicator"""
    # Create a temporary surface with per-pixel alpha
    temp_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
    color_with_alpha = (255, 255, 0, 77)  # 30% opacity (255 * 0.3 = 77)
    
    if shape == 'circle':
        pygame.draw.circle(temp_surface, color_with_alpha, (radius + 5, radius + 5), radius, 2)
    elif shape == 'polygon':
        # For polygon shapes, draw a circle for simplicity
        pygame.draw.circle(temp_surface, color_with_alpha, (radius + 5, radius + 5), radius, 2)
    
    # Blit the semi-transparent surface to the main surface
    surface.blit(temp_surface, (x - radius - 5, y - radius - 5))

@dataclass
class Building:
    x: float
    y: float
    color: Tuple[int, int, int]
    radius: int
    level: int = 1
    health: float = 100
    max_health: float = 100
    powered: bool = False
    xp: float = 0
    type: str = "building"
    selected: bool = False
    
    # Class variables for images (will be set from main.py)
    solar_image = None
    turret_image = None
    connector_image = None
    miner_image = None
    battery_image = None
    hospital_image = None

    def draw(self, surface, camera_x=0, camera_y=0, zoom=1.0):
        # Calculate screen position with camera offset and zoom
        screen_x = (self.x - camera_x) * zoom + SCREEN_WIDTH // 2
        screen_y = (self.y - camera_y) * zoom + SCREEN_HEIGHT // 2
        screen_radius = self.radius * zoom
        
        # Don't draw if off screen
        if (screen_x < -screen_radius or screen_x > SCREEN_WIDTH + screen_radius or
            screen_y < -screen_radius or screen_y > SCREEN_HEIGHT + screen_radius):
            return
        
        color = self.color if self.powered else (100, 100, 100)
        
        # Draw different shapes based on building type
        if self.type == "connector":
            # Yellow circle with enhanced glow when powered
            if self.powered:
                # Pulsing glow effect
                import time
                pulse = 0.5 + 0.3 * math.sin(time.time() * 3)  # Faster pulse
                glow_radius = int(screen_radius + 4 * pulse)
                pygame.draw.circle(surface, (100, 100, 0), (int(screen_x), int(screen_y)), glow_radius)
            
            pygame.draw.circle(surface, (255, 255, 0), (int(screen_x), int(screen_y)), int(screen_radius))
            pygame.draw.circle(surface, (0, 0, 0), (int(screen_x), int(screen_y)), int(screen_radius), max(2, int(3 * zoom)))
            # Selection indicators removed
        
        elif self.type == "miner":
            # Green triangle with mining beam effect when powered
            points = []
            for i in range(3):
                angle = i * 2 * np.pi / 3 - np.pi / 2  # Point upward
                px = screen_x + screen_radius * np.cos(angle)
                py = screen_y + screen_radius * np.sin(angle)
                points.append((px, py))
            
            # Add mining energy effect when powered
            if self.powered and hasattr(self, 'zap_timer') and self.zap_timer > 0:
                # Mining beam glow
                glow_points = []
                for i in range(3):
                    angle = i * 2 * np.pi / 3 - np.pi / 2
                    px = screen_x + (screen_radius + 3) * np.cos(angle)
                    py = screen_y + (screen_radius + 3) * np.sin(angle)
                    glow_points.append((px, py))
                pygame.draw.polygon(surface, (50, 100, 50), glow_points)
            
            pygame.draw.polygon(surface, (0, 255, 0), points)
            pygame.draw.polygon(surface, (0, 0, 0), points, max(2, int(3 * zoom)))
            # Selection indicators removed
        
        elif self.type == "turret":
            # Red pentagon with enhanced border and glow effect when powered
            points = []
            for i in range(5):
                angle = i * 2 * np.pi / 5 - np.pi / 2  # Point upward
                px = screen_x + screen_radius * np.cos(angle)
                py = screen_y + screen_radius * np.sin(angle)
                points.append((px, py))
            
            # Add glow effect when powered
            if self.powered:
                glow_points = []
                for i in range(5):
                    angle = i * 2 * np.pi / 5 - np.pi / 2
                    px = screen_x + (screen_radius + 3) * np.cos(angle)
                    py = screen_y + (screen_radius + 3) * np.sin(angle)
                    glow_points.append((px, py))
                pygame.draw.polygon(surface, (100, 30, 30), glow_points)
            
            pygame.draw.polygon(surface, (255, 0, 0), points)
            pygame.draw.polygon(surface, (0, 0, 0), points, max(2, int(3 * zoom)))
            # Selection indicators removed
        
        elif self.type == "laser":
            # White circle with black border and blue rectangle on it
            pygame.draw.circle(surface, (255, 255, 255), (int(screen_x), int(screen_y)), int(screen_radius))
            pygame.draw.circle(surface, (0, 0, 0), (int(screen_x), int(screen_y)), int(screen_radius), max(2, int(3 * zoom)))
            # Blue rectangle on top
            rect_width = screen_radius * 0.8
            rect_height = screen_radius * 0.4
            rect = pygame.Rect(screen_x - rect_width/2, screen_y - rect_height/2, rect_width, rect_height)
            pygame.draw.rect(surface, (0, 0, 255), rect)
            # Selection indicators removed
        
        elif self.type == "repair":
            # White square with blue cross and black square border
            square_size = screen_radius * 1.4
            rect = pygame.Rect(screen_x - square_size/2, screen_y - square_size/2, square_size, square_size)
            pygame.draw.rect(surface, (255, 255, 255), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, max(2, int(3 * zoom)))
            # Draw blue cross
            cross_size = screen_radius * 0.6
            pygame.draw.line(surface, (0, 0, 255), (screen_x - cross_size, screen_y), (screen_x + cross_size, screen_y), max(3, int(4 * zoom)))
            pygame.draw.line(surface, (0, 0, 255), (screen_x, screen_y - cross_size), (screen_x, screen_y + cross_size), max(3, int(4 * zoom)))
            # Selection indicators removed
        
        elif self.type == "solar":
            # Blue square with white grid lines and black square border
            square_size = screen_radius * 1.4
            rect = pygame.Rect(screen_x - square_size/2, screen_y - square_size/2, square_size, square_size)
            pygame.draw.rect(surface, (0, 0, 255), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, max(2, int(3 * zoom)))
            # Draw white gridlines
            grid_color = (255, 255, 255)
            for i in range(1, 3):  # 2 vertical lines
                x = screen_x - square_size/2 + i * square_size/3
                pygame.draw.line(surface, grid_color, (x, screen_y - square_size/2), (x, screen_y + square_size/2), max(1, int(2 * zoom)))
            for i in range(1, 3):  # 2 horizontal lines
                y = screen_y - square_size/2 + i * square_size/3
                pygame.draw.line(surface, grid_color, (screen_x - square_size/2, y), (screen_x + square_size/2, y), max(1, int(2 * zoom)))
            # Selection indicators removed
        
        elif self.type == "battery":
            # Keep original design - Red oval on white circle for battery
            pygame.draw.circle(surface, (255, 255, 255), (int(screen_x), int(screen_y)), int(screen_radius))
            # Draw oval (ellipse)
            oval_rect = pygame.Rect(screen_x - screen_radius*0.6, screen_y - screen_radius*0.4, screen_radius*1.2, screen_radius*0.8)
            pygame.draw.ellipse(surface, color, oval_rect)
            # Selection indicators removed
        
        elif self.type == "converter":
            # Default hexagon for converter (keep existing)
            points = []
            for i in range(HEX_POINTS):
                angle = i * 2 * np.pi / HEX_POINTS
                px = screen_x + screen_radius * np.cos(angle)
                py = screen_y + screen_radius * np.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(surface, color, points)
            # Selection indicators removed
        
        else:
            # Default hexagon for unknown types
            points = []
            for i in range(HEX_POINTS):
                angle = i * 2 * np.pi / HEX_POINTS
                px = screen_x + screen_radius * np.cos(angle)
                py = screen_y + screen_radius * np.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(surface, color, points)
            # Selection indicators removed
        
        # Health bar
        # Health bar only if damaged (50% opacity)
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = screen_radius * 2
            bar_height = 5 * zoom
            bar_x = screen_x - bar_width/2
            bar_y = screen_y - screen_radius - 10*zoom
            
            # Create semi-transparent health bar
            health_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            health_surface.fill((200, 0, 0, 127))  # Red background with 50% alpha
            surface.blit(health_surface, (bar_x, bar_y))
            
            # Only create green surface if there's actual health to show
            green_width = max(1, int(bar_width * health_ratio))
            if green_width > 0:
                green_surface = pygame.Surface((green_width, bar_height), pygame.SRCALPHA)
                green_surface.fill((0, 200, 0, 127))  # Green with 50% alpha
                surface.blit(green_surface, (bar_x, bar_y))
        # Level text removed - stats will be shown in bottom left panel when selected

    def upgrade_cost(self, base_cost):
        return int(base_cost * (UPGRADE_COST_FACTOR ** (self.level - 1)))

    def upgrade(self):
        if self.level < MAX_LEVEL:
            self.level += 1
            self.max_health += HEALTH_PER_UPGRADE
            self.health = self.max_health

    def gain_xp(self, amount):
        if self.xp >= 0 and self.level < MAX_LEVEL:
            self.xp += amount
            xp_needed = XP_TO_LEVEL_BASE * self.level
            if self.xp >= xp_needed:
                self.xp -= xp_needed
                self.upgrade()

class Solar(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 120, 255), 25)
        self.type = "solar"
    @property
    def prod_rate(self):
        return SOLAR_ENERGY_RATE * self.level

class Connector(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 180, 40), 10)
        self.type = "connector"

class Battery(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (120, 0, 180), 15)
        self.type = "battery"
    @property
    def storage(self):
        return BATTERY_STORAGE * self.level

class Miner(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 200, 80), 10)
        self.type = "miner"
        self.zap_timer = 0
    @property
    def mine_rate(self):
        return MINER_RATE * self.level

class Turret(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (200, 40, 40), 15)
        self.type = "turret"
        self.xp = 0
        self.cooldown = 0
    @property
    def damage(self):
        return TURRET_DAMAGE * self.level
    @property
    def fire_range(self):
        return TURRET_RANGE * (1 + 0.1 * (self.level - 1))
    @property
    def cooldown_time(self):
        return max(10, TURRET_COOLDOWN // self.level)

class Laser(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (100, 200, 255), 15)
        self.type = "laser"
        self.xp = 0
    @property
    def damage_per_frame(self):
        return LASER_DAMAGE * self.level
    @property
    def fire_range(self):
        return LASER_RANGE * (1 + 0.1 * (self.level - 1))

class SuperLaser(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 100, 255), 18)  # Purple, larger
        self.type = "superlaser"
        self.xp = 0
    @property
    def damage_per_frame(self):
        return SUPERLASER_DAMAGE * self.level
    @property
    def fire_range(self):
        return SUPERLASER_RANGE * (1 + 0.1 * (self.level - 1))

class Repair(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 255), 15)
        self.type = "repair"
    @property
    def heal_rate(self):
        return REPAIR_RATE * self.level
    @property
    def heal_range(self):
        return REPAIR_RANGE * (1 + 0.1 * (self.level - 1))

class Converter(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 255, 80), 12)
        self.type = "converter"
        self.convert_timer = 0
    @property
    def conversion_rate(self):
        return CONVERTER_MINERAL_RATE * self.level
    @property
    def energy_cost(self):
        return CONVERTER_ENERGY_COST
    @property
    def conversion_interval(self):
        return CONVERTER_INTERVAL