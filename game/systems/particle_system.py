import pygame
import math
import random
from typing import List, Tuple, Optional
from enum import Enum

class ParticleType(Enum):
    """Types of particles with different behaviors."""
    SPARK = "spark"
    EXPLOSION = "explosion"
    SMOKE = "smoke"
    ENERGY = "energy"
    DEBRIS = "debris"
    GLOW = "glow"
    TRAIL = "trail"

class Particle:
    """Enhanced particle with multiple types and behaviors."""
    
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, 
                 lifetime: int, color: Tuple[int, int, int], 
                 particle_type: ParticleType = ParticleType.SPARK,
                 size: float = 2.0):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.original_color = color
        self.particle_type = particle_type
        self.size = size
        self.original_size = size
        
        # Physics properties
        self.gravity = 0.1 if particle_type in [ParticleType.DEBRIS, ParticleType.SPARK] else 0.05
        self.friction = 0.98 if particle_type == ParticleType.SMOKE else 0.95
        
        # Visual properties
        self.alpha = 255
        self.glow_radius = size * 2 if particle_type == ParticleType.GLOW else 0
        self.pulse_phase = random.uniform(0, math.pi * 2)
        
    def update(self) -> bool:
        """Update particle physics and return True if still alive."""
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Apply physics based on particle type
        if self.particle_type == ParticleType.SMOKE:
            # Smoke rises and disperses
            self.vel_y -= 0.02
            self.vel_x *= self.friction
            self.vel_y *= self.friction
            self.size += 0.05  # Smoke expands
        elif self.particle_type == ParticleType.EXPLOSION:
            # Explosion particles slow down quickly
            self.vel_x *= 0.9
            self.vel_y *= 0.9
            self.vel_y += self.gravity * 0.5
        elif self.particle_type == ParticleType.DEBRIS:
            # Debris affected by gravity
            self.vel_y += self.gravity
            self.vel_x *= self.friction
        elif self.particle_type == ParticleType.ENERGY:
            # Energy particles have pulsing behavior
            pulse = math.sin(self.pulse_phase + pygame.time.get_ticks() * 0.01) * 0.2 + 0.8
            self.size = self.original_size * pulse
            self.vel_x *= 0.96
            self.vel_y *= 0.96
        elif self.particle_type == ParticleType.GLOW:
            # Glow particles fade and pulse
            pulse = math.sin(self.pulse_phase + pygame.time.get_ticks() * 0.005) * 0.3 + 0.7
            self.glow_radius = self.original_size * 3 * pulse
            self.vel_x *= 0.98
            self.vel_y *= 0.98
        elif self.particle_type == ParticleType.TRAIL:
            # Trail particles fade quickly and have minimal physics
            self.vel_x *= 0.95
            self.vel_y *= 0.95
        
        # Update lifetime and alpha
        self.lifetime -= 1
        life_ratio = self.lifetime / self.max_lifetime
        
        # Different fade patterns for different particle types
        if self.particle_type == ParticleType.EXPLOSION:
            self.alpha = int(255 * life_ratio * life_ratio)  # Quick fade
        elif self.particle_type == ParticleType.SMOKE:
            self.alpha = int(255 * life_ratio * 0.7)  # Gradual fade, semi-transparent
        elif self.particle_type == ParticleType.ENERGY:
            self.alpha = int(255 * life_ratio)  # Linear fade
        elif self.particle_type == ParticleType.GLOW:
            self.alpha = int(255 * life_ratio * 0.6)  # Soft fade
        else:
            self.alpha = int(255 * life_ratio)
        
        # Update color intensity
        fade = life_ratio
        self.color = (
            int(self.original_color[0] * fade),
            int(self.original_color[1] * fade),
            int(self.original_color[2] * fade)
        )
        
        return self.lifetime > 0
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float, camera_zoom: float):
        """Draw the particle with various visual effects."""
        screen_x = int((self.x - camera_x) * camera_zoom)
        screen_y = int((self.y - camera_y) * camera_zoom)
        screen_size = max(1, int(self.size * camera_zoom))
        
        # Skip if off-screen (with margin)
        if (screen_x < -50 or screen_x > surface.get_width() + 50 or
            screen_y < -50 or screen_y > surface.get_height() + 50):
            return
        
        color_with_alpha = (*self.color, self.alpha)
        
        try:
            if self.particle_type == ParticleType.GLOW:
                # Draw glow effect
                glow_size = max(1, int(self.glow_radius * camera_zoom))
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                
                # Create radial gradient
                for r in range(glow_size, 0, -2):
                    alpha = int(self.alpha * (1 - r / glow_size) * 0.3)
                    if alpha > 0:
                        glow_color = (*self.color, min(255, alpha))
                        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), r)
                
                surface.blit(glow_surf, (screen_x - glow_size, screen_y - glow_size))
                
            elif self.particle_type == ParticleType.ENERGY:
                # Draw energy particle with inner glow
                if screen_size > 1:
                    # Outer glow
                    glow_surf = pygame.Surface((screen_size * 4, screen_size * 4), pygame.SRCALPHA)
                    outer_color = (*self.color, self.alpha // 4)
                    pygame.draw.circle(glow_surf, outer_color, (screen_size * 2, screen_size * 2), screen_size * 2)
                    surface.blit(glow_surf, (screen_x - screen_size * 2, screen_y - screen_size * 2))
                
                # Core
                core_color = (*self.color, self.alpha)
                pygame.draw.circle(surface, core_color, (screen_x, screen_y), screen_size)
                
            elif self.particle_type == ParticleType.SMOKE:
                # Draw semi-transparent smoke
                if screen_size > 1:
                    smoke_surf = pygame.Surface((screen_size * 2, screen_size * 2), pygame.SRCALPHA)
                    smoke_color = (*self.color, self.alpha)
                    pygame.draw.circle(smoke_surf, smoke_color, (screen_size, screen_size), screen_size)
                    surface.blit(smoke_surf, (screen_x - screen_size, screen_y - screen_size))
                    
            elif self.particle_type == ParticleType.EXPLOSION:
                # Draw bright explosion particle
                if screen_size > 1:
                    # Bright core
                    bright_color = (
                        min(255, self.color[0] + 50),
                        min(255, self.color[1] + 30),
                        min(255, self.color[2])
                    )
                    pygame.draw.circle(surface, bright_color, (screen_x, screen_y), screen_size)
                    
                    # Outer glow
                    if screen_size > 2:
                        glow_surf = pygame.Surface((screen_size * 3, screen_size * 3), pygame.SRCALPHA)
                        glow_color = (*self.color, self.alpha // 3)
                        pygame.draw.circle(glow_surf, glow_color, (screen_size * 3 // 2, screen_size * 3 // 2), screen_size * 3 // 2)
                        surface.blit(glow_surf, (screen_x - screen_size * 3 // 2, screen_y - screen_size * 3 // 2))
                        
            else:
                # Default particle drawing (spark, debris, trail)
                if screen_size > 1:
                    pygame.draw.circle(surface, self.color, (screen_x, screen_y), screen_size)
                else:
                    surface.set_at((screen_x, screen_y), self.color)
                    
        except (pygame.error, ValueError):
            # Fallback for any drawing errors
            if screen_size > 0:
                pygame.draw.circle(surface, self.color, (screen_x, screen_y), max(1, screen_size))

class ParticleSystem:
    """Enhanced particle system manager."""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 1000  # Limit for performance
        
    def add_particles(self, x: float, y: float, count: int, 
                     color: Tuple[int, int, int], 
                     particle_type: ParticleType = ParticleType.SPARK,
                     speed_range: Tuple[float, float] = (1.0, 3.0),
                     lifetime_range: Tuple[int, int] = (30, 60),
                     size_range: Tuple[float, float] = (1.0, 3.0)):
        """Add multiple particles at once."""
        for _ in range(count):
            # Random velocity
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(*speed_range)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Random properties
            lifetime = random.randint(*lifetime_range)
            size = random.uniform(*size_range)
            
            # Color variation
            color_var = (
                max(0, min(255, color[0] + random.randint(-20, 20))),
                max(0, min(255, color[1] + random.randint(-20, 20))),
                max(0, min(255, color[2] + random.randint(-20, 20)))
            )
            
            particle = Particle(x, y, vel_x, vel_y, lifetime, color_var, particle_type, size)
            self.particles.append(particle)
        
        # Limit total particles for performance
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
    
    def add_explosion(self, x: float, y: float, intensity: float = 1.0):
        """Create a complex explosion effect."""
        base_count = int(20 * intensity)
        
        # Core explosion - bright and fast
        self.add_particles(
            x, y, base_count,
            (255, 200, 100),  # Bright orange-yellow
            ParticleType.EXPLOSION,
            speed_range=(3 * intensity, 8 * intensity),
            lifetime_range=(15, 30),
            size_range=(2, 5)
        )
        
        # Outer sparks
        self.add_particles(
            x, y, base_count // 2,
            (255, 150, 50),  # Orange
            ParticleType.SPARK,
            speed_range=(1 * intensity, 5 * intensity),
            lifetime_range=(20, 40),
            size_range=(1, 3)
        )
        
        # Debris
        self.add_particles(
            x, y, base_count // 3,
            (100, 100, 100),  # Gray debris
            ParticleType.DEBRIS,
            speed_range=(0.5 * intensity, 3 * intensity),
            lifetime_range=(30, 80),
            size_range=(1, 2)
        )
        
        # Smoke
        self.add_particles(
            x, y, base_count // 4,
            (60, 60, 60),  # Dark gray smoke
            ParticleType.SMOKE,
            speed_range=(0.2 * intensity, 1 * intensity),
            lifetime_range=(60, 120),
            size_range=(3, 8)
        )
        
        # Energy glow
        self.add_particles(
            x, y, 3,
            (255, 255, 200),  # Bright white-yellow
            ParticleType.GLOW,
            speed_range=(0.1, 0.5),
            lifetime_range=(20, 40),
            size_range=(10, 20)
        )
    
    def add_laser_impact(self, x: float, y: float, color: Tuple[int, int, int]):
        """Create laser impact effect."""
        # Sparks
        self.add_particles(
            x, y, 8,
            color,
            ParticleType.SPARK,
            speed_range=(1, 4),
            lifetime_range=(10, 25),
            size_range=(1, 2)
        )
        
        # Energy glow
        self.add_particles(
            x, y, 2,
            color,
            ParticleType.ENERGY,
            speed_range=(0.1, 0.5),
            lifetime_range=(15, 30),
            size_range=(5, 10)
        )
    
    def add_building_construction(self, x: float, y: float):
        """Create building construction effect."""
        # Construction sparks
        self.add_particles(
            x, y, 15,
            (100, 200, 255),  # Blue sparks
            ParticleType.ENERGY,
            speed_range=(0.5, 2),
            lifetime_range=(20, 40),
            size_range=(1, 3)
        )
        
        # Glow effect
        self.add_particles(
            x, y, 3,
            (150, 220, 255),  # Light blue glow
            ParticleType.GLOW,
            speed_range=(0.1, 0.3),
            lifetime_range=(30, 50),
            size_range=(8, 15)
        )
    
    def add_engine_trail(self, x: float, y: float, direction_x: float, direction_y: float, 
                        color: Tuple[int, int, int]):
        """Create engine exhaust trail."""
        # Trail particles in opposite direction of movement
        for i in range(3):
            offset_x = -direction_x * (i + 1) * 5 + random.uniform(-2, 2)
            offset_y = -direction_y * (i + 1) * 5 + random.uniform(-2, 2)
            
            self.add_particles(
                x + offset_x, y + offset_y, 1,
                color,
                ParticleType.TRAIL,
                speed_range=(0.1, 0.5),
                lifetime_range=(10, 20),
                size_range=(1, 2)
            )
    
    def add_power_pulse(self, x: float, y: float):
        """Create power connection pulse effect."""
        self.add_particles(
            x, y, 5,
            (100, 255, 100),  # Green energy
            ParticleType.ENERGY,
            speed_range=(0.2, 1),
            lifetime_range=(15, 30),
            size_range=(2, 4)
        )
    
    def update(self):
        """Update all particles and remove dead ones."""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float, camera_zoom: float):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y, camera_zoom)
    
    def get_particle_count(self) -> int:
        """Get current number of active particles."""
        return len(self.particles)
    
    def clear(self):
        """Remove all particles."""
        self.particles.clear() 