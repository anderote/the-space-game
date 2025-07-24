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
    
    def take_damage(self, damage):
        """Take damage and reduce health"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0

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
        
        # Enhanced building drawing with 3D effects and animations
        import time
        current_time = time.time()
        
        # Draw different shapes based on building type with enhanced visuals
        if self.type == "connector":
            self._draw_connector_enhanced(surface, screen_x, screen_y, screen_radius, current_time)
            # Selection indicators removed
        
        elif self.type == "miner":
            self._draw_miner_enhanced(surface, screen_x, screen_y, screen_radius, current_time)
            # Selection indicators removed
        
        elif self.type == "turret":
            self._draw_turret_enhanced(surface, screen_x, screen_y, screen_radius, current_time)
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
        
        # Enhanced health bar with gradient
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = screen_radius * 2
            bar_height = 5 * zoom
            bar_x = screen_x - bar_width/2
            bar_y = screen_y - screen_radius - 10*zoom
            
            # Background
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
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
            health_width = int(bar_width * health_ratio)
            if health_width > 0:
                pygame.draw.rect(surface, (r, g, b), (bar_x, bar_y, health_width, bar_height))
            
            # Glass effect on health bar
            pygame.draw.rect(surface, (255, 255, 255, 100), (bar_x, bar_y, bar_width, bar_height//2))
            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)
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
    
    def _draw_connector_enhanced(self, surface, screen_x, screen_y, screen_radius, current_time):
        """Draw enhanced connector with 3D effects and energy flow animation."""
        # Shadow effect
        shadow_offset = max(2, screen_radius // 6)
        pygame.draw.circle(surface, (40, 40, 0), 
                         (int(screen_x + shadow_offset), int(screen_y + shadow_offset)), int(screen_radius))
        
        if self.powered:
            # Multi-layer pulsing glow effect
            pulse = 0.5 + 0.5 * math.sin(current_time * 4)  # Faster pulse for energy
            for i in range(3):
                glow_alpha = int(60 * pulse / (i + 1))
                glow_radius = int(screen_radius + (6 - i * 2) * pulse)
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 200, 0, glow_alpha), 
                                 (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
        
        # Main body with gradient
        main_color = (255, 255, 0) if self.powered else (100, 100, 0)
        pygame.draw.circle(surface, main_color, (int(screen_x), int(screen_y)), int(screen_radius))
        
        # Highlight for 3D effect
        highlight_offset = screen_radius * 0.3
        pygame.draw.circle(surface, (255, 255, 180), 
                         (int(screen_x - highlight_offset), int(screen_y - highlight_offset)), 
                         max(1, int(screen_radius * 0.4)))
        
        # Animated energy core
        if self.powered:
            core_pulse = 0.3 + 0.2 * math.sin(current_time * 6)
            core_radius = int(screen_radius * core_pulse)
            pygame.draw.circle(surface, (255, 255, 255), (int(screen_x), int(screen_y)), core_radius)
        
        # Border
        border_color = (255, 255, 255) if self.powered else (150, 150, 150)
        pygame.draw.circle(surface, border_color, (int(screen_x), int(screen_y)), 
                         int(screen_radius), 2)

    def _draw_miner_enhanced(self, surface, screen_x, screen_y, screen_radius, current_time):
        """Draw enhanced miner with 3D effects and mining beam animation."""
        # Triangle points
        points = []
        shadow_points = []
        shadow_offset = max(2, screen_radius // 6)
        
        for i in range(3):
            angle = i * 2 * np.pi / 3 - np.pi / 2  # Point upward
            px = screen_x + screen_radius * np.cos(angle)
            py = screen_y + screen_radius * np.sin(angle)
            points.append((px, py))
            shadow_points.append((px + shadow_offset, py + shadow_offset))
        
        # Shadow
        pygame.draw.polygon(surface, (20, 40, 20), shadow_points)
        
        # Mining energy effect when powered and active
        if self.powered and hasattr(self, 'zap_timer') and self.zap_timer > 0:
            # Animated energy waves
            wave_intensity = math.sin(current_time * 8) * 0.5 + 0.5
            for wave in range(3):
                wave_size = screen_radius + (wave * 4) + (wave_intensity * 6)
                wave_alpha = int(80 * (1 - wave * 0.3) * wave_intensity)
                wave_surface = pygame.Surface((wave_size * 2, wave_size * 2), pygame.SRCALPHA)
                
                wave_points = []
                for i in range(3):
                    angle = i * 2 * np.pi / 3 - np.pi / 2
                    px = wave_size + wave_size * np.cos(angle)
                    py = wave_size + wave_size * np.sin(angle)
                    wave_points.append((px, py))
                
                pygame.draw.polygon(wave_surface, (0, 255, 0, wave_alpha), wave_points)
                surface.blit(wave_surface, (screen_x - wave_size, screen_y - wave_size))
        
        # Main body with gradient
        main_color = (0, 255, 0) if self.powered else (0, 100, 0)
        pygame.draw.polygon(surface, main_color, points)
        
        # Highlight for 3D effect
        highlight_points = []
        for i in range(3):
            angle = i * 2 * np.pi / 3 - np.pi / 2
            px = screen_x + screen_radius * 0.6 * np.cos(angle) - screen_radius * 0.2
            py = screen_y + screen_radius * 0.6 * np.sin(angle) - screen_radius * 0.2
            highlight_points.append((px, py))
        pygame.draw.polygon(surface, (100, 255, 100), highlight_points)
        
        # Border
        border_color = (255, 255, 255) if self.powered else (150, 150, 150)
        pygame.draw.polygon(surface, border_color, points, 2)

    def _draw_turret_enhanced(self, surface, screen_x, screen_y, screen_radius, current_time):
        """Draw enhanced turret with 3D effects and targeting animation."""
        # Pentagon points
        points = []
        shadow_points = []
        shadow_offset = max(2, screen_radius // 6)
        
        for i in range(5):
            angle = i * 2 * np.pi / 5 - np.pi / 2  # Point upward
            px = screen_x + screen_radius * np.cos(angle)
            py = screen_y + screen_radius * np.sin(angle)
            points.append((px, py))
            shadow_points.append((px + shadow_offset, py + shadow_offset))
        
        # Shadow
        pygame.draw.polygon(surface, (40, 20, 20), shadow_points)
        
        # Targeting glow when powered
        if self.powered:
            # Rotating targeting scanner effect
            scanner_angle = current_time * 2
            for beam in range(4):
                beam_angle = scanner_angle + (beam * np.pi / 2)
                beam_length = screen_radius * 1.8
                beam_end_x = screen_x + beam_length * np.cos(beam_angle)
                beam_end_y = screen_y + beam_length * np.sin(beam_angle)
                
                # Draw scanning beam
                beam_alpha = int(40 * (math.sin(current_time * 3 + beam) + 1) / 2)
                if beam_alpha > 0:
                    pygame.draw.line(surface, (255, 100, 100), 
                                   (int(screen_x), int(screen_y)), 
                                   (int(beam_end_x), int(beam_end_y)), 1)
        
        # Main body with gradient
        main_color = (255, 0, 0) if self.powered else (100, 0, 0)
        pygame.draw.polygon(surface, main_color, points)
        
        # Highlight for 3D effect
        highlight_points = []
        for i in range(5):
            angle = i * 2 * np.pi / 5 - np.pi / 2
            px = screen_x + screen_radius * 0.6 * np.cos(angle) - screen_radius * 0.2
            py = screen_y + screen_radius * 0.6 * np.sin(angle) - screen_radius * 0.2
            highlight_points.append((px, py))
        pygame.draw.polygon(surface, (255, 100, 100), highlight_points)
        
        # Central core
        if self.powered:
            core_pulse = 0.4 + 0.2 * math.sin(current_time * 5)
            core_radius = int(screen_radius * core_pulse * 0.3)
            pygame.draw.circle(surface, (255, 255, 0), (int(screen_x), int(screen_y)), core_radius)
        
        # Border
        border_color = (255, 255, 255) if self.powered else (150, 150, 150)
        pygame.draw.polygon(surface, border_color, points, 2)

class Solar(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 120, 255), 25)
        self.type = "solar"
    @property
    def prod_rate(self):
        return SOLAR_ENERGY_RATE * self.level
    @property
    def storage(self):
        return 50 * self.level  # 50 base capacity per level

class Connector(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 180, 40), 5)  # Reduced radius from 10 to 5 (50% smaller)
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

class Hangar(Building):
    def __init__(self, x, y):
        super().__init__(x, y, (120, 120, 255), 20)
        self.type = "hangar"
        self.launch_timer = 0
        self.deployed_ships = []  # List of friendly ships launched from this hangar
        self.max_ships = 3  # Maximum number of ships this hangar can deploy
        
    @property
    def launch_cooldown(self):
        return 300  # 5 seconds at 60fps
        
    @property
    def ship_range(self):
        return 500  # Range within which ships will engage enemies
        
    @property
    def recall_range(self):
        return 600  # Range beyond which ships will return to hangar


class FriendlyShip:
    """Friendly attack ship launched from hangars"""
    def __init__(self, x, y, hangar):
        self.x = x
        self.y = y
        self.hangar = hangar  # Reference to parent hangar
        self.health = 30
        self.max_health = 30
        self.speed = 2.0
        self.damage = 15
        self.fire_range = 80
        self.last_shot_time = 0
        self.fire_cooldown = 60  # 1 second at 60fps
        self.target = None
        self.state = "seeking"  # "seeking", "attacking", "returning"
        self.size = 8
        
    def update(self, enemies, current_time):
        """Update ship behavior"""
        if self.health <= 0:
            return False  # Ship destroyed
            
        # Find distance to hangar
        hangar_dist = math.sqrt((self.x - self.hangar.x)**2 + (self.y - self.hangar.y)**2)
        
        # Check if we should return to hangar
        if hangar_dist > self.hangar.recall_range:
            self.state = "returning"
            self.target = None
        elif not enemies or not any(self._distance_to(e) <= self.hangar.ship_range for e in enemies):
            # No enemies in range, return to hangar
            self.state = "returning"
            self.target = None
        else:
            # Find nearest enemy within range
            closest_enemy = None
            closest_dist = float('inf')
            
            for enemy in enemies:
                dist = self._distance_to(enemy)
                if dist <= self.hangar.ship_range and dist < closest_dist:
                    closest_enemy = enemy
                    closest_dist = dist
                    
            if closest_enemy:
                self.target = closest_enemy
                self.state = "attacking"
            else:
                self.state = "returning"
                self.target = None
        
        # Move based on state
        if self.state == "attacking" and self.target:
            self._move_towards(self.target.x, self.target.y)
            # Try to attack if in range
            if self._distance_to(self.target) <= self.fire_range:
                if current_time - self.last_shot_time >= self.fire_cooldown:
                    self.target.take_damage(self.damage)
                    self.last_shot_time = current_time
        elif self.state == "returning":
            self._move_towards(self.hangar.x, self.hangar.y)
            # Check if we've returned to hangar
            if hangar_dist < 30:
                return False  # Ship has returned, remove from active list
        else:  # seeking
            # Patrol around hangar
            patrol_radius = 100
            patrol_x = self.hangar.x + patrol_radius * math.cos(current_time * 0.01)
            patrol_y = self.hangar.y + patrol_radius * math.sin(current_time * 0.01)
            self._move_towards(patrol_x, patrol_y)
            
        return True  # Ship still active
        
    def _distance_to(self, target):
        """Calculate distance to target"""
        return math.sqrt((self.x - target.x)**2 + (self.y - target.y)**2)
        
    def _move_towards(self, target_x, target_y):
        """Move towards target position"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            # Normalize and apply speed
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            
    def take_damage(self, damage):
        """Take damage from enemy attacks"""
        self.health -= damage
        
    def draw(self, surface, camera):
        """Draw the friendly ship"""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        screen_size = self.size * camera.zoom
        
        if 0 <= screen_x <= surface.get_width() and 0 <= screen_y <= surface.get_height():
            # Draw as a small blue triangle pointing towards movement direction
            if hasattr(self, 'target') and self.target:
                # Point towards target
                dx = self.target.x - self.x
                dy = self.target.y - self.y
            else:
                # Point towards hangar
                dx = self.hangar.x - self.x
                dy = self.hangar.y - self.y
                
            angle = math.atan2(dy, dx)
            
            # Triangle points
            points = []
            for i in range(3):
                point_angle = angle + (i * 2 * math.pi / 3)
                px = screen_x + screen_size * math.cos(point_angle)
                py = screen_y + screen_size * math.sin(point_angle)
                points.append((px, py))
                
            # Draw blue triangle
            pygame.draw.polygon(surface, (100, 150, 255), points)
            pygame.draw.polygon(surface, (50, 100, 200), points, 2)
            
            # Draw health bar if damaged
            if self.health < self.max_health:
                health_ratio = self.health / self.max_health
                bar_width = 15 * camera.zoom
                bar_height = 3 * camera.zoom
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - screen_size - 8 * camera.zoom
                
                # Background
                pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                # Health
                health_width = int(bar_width * health_ratio)
                if health_width > 0:
                    pygame.draw.rect(surface, (0, 150, 0), (bar_x, bar_y, health_width, bar_height))