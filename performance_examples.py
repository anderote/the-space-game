"""
Practical performance optimization examples for Space Game.
These can be integrated into your existing codebase for immediate improvements.
"""

import pygame
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# 1. SPATIAL PARTITIONING SYSTEM
class SpatialGrid:
    """
    Spatial partitioning system to optimize collision detection and range queries.
    Replaces O(n²) operations with O(n) for most cases.
    """
    def __init__(self, world_width: int, world_height: int, cell_size: int = 200):
        self.cell_size = cell_size
        self.world_width = world_width
        self.world_height = world_height
        self.grid: Dict[Tuple[int, int], List] = defaultdict(list)
        
    def clear(self):
        """Clear all entities from the grid."""
        self.grid.clear()
        
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get the grid cell for given coordinates."""
        cell_x = max(0, min(self.world_width // self.cell_size - 1, int(x // self.cell_size)))
        cell_y = max(0, min(self.world_height // self.cell_size - 1, int(y // self.cell_size)))
        return (cell_x, cell_y)
        
    def add_entity(self, entity, x: float, y: float):
        """Add an entity to the spatial grid."""
        cell = self._get_cell(x, y)
        self.grid[cell].append(entity)
        
    def get_nearby_entities(self, x: float, y: float, radius: float) -> List:
        """Get all entities within radius of the given position."""
        entities = []
        cell_radius = int(radius // self.cell_size) + 1
        center_cell = self._get_cell(x, y)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    entities.extend(self.grid[cell])
                    
        return entities
        
    def get_entities_in_range(self, x: float, y: float, radius: float) -> List:
        """Get entities within exact radius (with distance check)."""
        nearby = self.get_nearby_entities(x, y, radius)
        in_range = []
        radius_sq = radius * radius
        
        for entity in nearby:
            dx = entity.x - x
            dy = entity.y - y
            if dx * dx + dy * dy <= radius_sq:
                in_range.append(entity)
                
        return in_range


# 2. OPTIMIZED PARTICLE SYSTEM WITH NUMPY
class OptimizedParticleSystem:
    """
    Hardware-accelerated particle system using NumPy for batch operations.
    Can handle 10,000+ particles efficiently.
    """
    def __init__(self, max_particles: int = 10000):
        self.max_particles = max_particles
        self.particle_count = 0
        
        # Use NumPy arrays for vectorized operations
        self.positions = np.zeros((max_particles, 2), dtype=np.float32)
        self.velocities = np.zeros((max_particles, 2), dtype=np.float32)
        self.colors = np.zeros((max_particles, 3), dtype=np.uint8)
        self.sizes = np.zeros(max_particles, dtype=np.float32)
        self.life = np.zeros(max_particles, dtype=np.float32)
        self.max_life = np.zeros(max_particles, dtype=np.float32)
        self.active = np.zeros(max_particles, dtype=bool)
        
    def emit(self, x: float, y: float, vel_x: float, vel_y: float, 
             color: Tuple[int, int, int], size: float, lifetime: float):
        """Emit a new particle."""
        if self.particle_count < self.max_particles:
            idx = self.particle_count
            self.positions[idx] = [x, y]
            self.velocities[idx] = [vel_x, vel_y]
            self.colors[idx] = color
            self.sizes[idx] = size
            self.life[idx] = lifetime
            self.max_life[idx] = lifetime
            self.active[idx] = True
            self.particle_count += 1
            
    def emit_explosion(self, x: float, y: float, count: int = 50):
        """Emit an explosion effect."""
        for _ in range(count):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(50, 200)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            color = (
                np.random.randint(200, 255),
                np.random.randint(100, 200),
                np.random.randint(0, 100)
            )
            
            size = np.random.uniform(2, 8)
            lifetime = np.random.uniform(0.5, 2.0)
            
            self.emit(x, y, vel_x, vel_y, color, size, lifetime)
            
    def update(self, dt: float):
        """Update all particles using vectorized operations."""
        if self.particle_count == 0:
            return
            
        # Get active particles mask
        active_mask = self.active
        
        # Update positions (vectorized)
        self.positions[active_mask] += self.velocities[active_mask] * dt
        
        # Update life (vectorized)
        self.life[active_mask] -= dt
        
        # Apply gravity/drag (vectorized)
        self.velocities[active_mask] *= 0.98  # Drag
        
        # Deactivate dead particles
        dead_mask = self.life <= 0
        self.active[dead_mask] = False
        
        # Compact particle array (remove inactive particles)
        self._compact_particles()
        
    def _compact_particles(self):
        """Remove inactive particles to maintain performance."""
        if self.particle_count == 0:
            return
            
        active_indices = np.where(self.active[:self.particle_count])[0]
        new_count = len(active_indices)
        
        if new_count < self.particle_count:
            # Move active particles to the front
            self.positions[:new_count] = self.positions[active_indices]
            self.velocities[:new_count] = self.velocities[active_indices]
            self.colors[:new_count] = self.colors[active_indices]
            self.sizes[:new_count] = self.sizes[active_indices]
            self.life[:new_count] = self.life[active_indices]
            self.max_life[:new_count] = self.max_life[active_indices]
            self.active[:new_count] = True
            self.active[new_count:self.particle_count] = False
            self.particle_count = new_count
            
    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float, zoom: float):
        """Draw particles with camera transformation."""
        if self.particle_count == 0:
            return
            
        # Get screen dimensions
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Vectorized camera transformation
        screen_positions = np.zeros((self.particle_count, 2), dtype=np.int32)
        screen_positions[:, 0] = ((self.positions[:self.particle_count, 0] - camera_x) * zoom + screen_width // 2).astype(np.int32)
        screen_positions[:, 1] = ((self.positions[:self.particle_count, 1] - camera_y) * zoom + screen_height // 2).astype(np.int32)
        
        # Only draw visible particles
        visible_mask = (
            (screen_positions[:, 0] >= -50) & (screen_positions[:, 0] <= screen_width + 50) &
            (screen_positions[:, 1] >= -50) & (screen_positions[:, 1] <= screen_height + 50)
        )
        
        visible_indices = np.where(visible_mask)[0]
        
        # Draw particles
        for i in visible_indices:
            if i < self.particle_count and self.active[i]:
                x, y = screen_positions[i]
                color = tuple(self.colors[i])
                size = max(1, int(self.sizes[i] * zoom))
                
                # Alpha based on remaining life
                alpha = self.life[i] / self.max_life[i]
                if alpha > 0:
                    # Create temporary surface for alpha blending
                    temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    adjusted_color = (*color, int(255 * alpha))
                    pygame.draw.circle(temp_surface, adjusted_color, (size, size), size)
                    surface.blit(temp_surface, (x - size, y - size), special_flags=pygame.BLEND_ALPHA_SDL2)


# 3. OPTIMIZED COLLISION DETECTION
class OptimizedCollisionSystem:
    """
    Optimized collision detection using spatial partitioning and early termination.
    """
    def __init__(self, spatial_grid: SpatialGrid):
        self.spatial_grid = spatial_grid
        
    def check_circle_collisions(self, entities: List, radius_getter=lambda e: e.radius) -> List[Tuple]:
        """
        Optimized circle-circle collision detection.
        Returns list of (entity1, entity2) collision pairs.
        """
        collisions = []
        
        # Build spatial grid
        self.spatial_grid.clear()
        for entity in entities:
            self.spatial_grid.add_entity(entity, entity.x, entity.y)
            
        # Check collisions using spatial partitioning
        checked_pairs = set()
        
        for entity in entities:
            radius = radius_getter(entity)
            nearby = self.spatial_grid.get_nearby_entities(entity.x, entity.y, radius * 2)
            
            for other in nearby:
                if entity is other:
                    continue
                    
                # Avoid duplicate checks
                pair = tuple(sorted([id(entity), id(other)]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                # Check actual collision
                dx = entity.x - other.x
                dy = entity.y - other.y
                distance_sq = dx * dx + dy * dy
                radius_sum = radius + radius_getter(other)
                
                if distance_sq <= radius_sum * radius_sum:
                    collisions.append((entity, other))
                    
        return collisions
        
    def find_entities_in_range(self, source_x: float, source_y: float, 
                              range_val: float, entities: List) -> List:
        """Find all entities within range of a point."""
        return self.spatial_grid.get_entities_in_range(source_x, source_y, range_val)


# 4. OPTIMIZED GAME LOGIC INTEGRATION
class OptimizedGameLogicSystem:
    """
    Drop-in replacement for your existing GameLogicSystem with optimizations.
    """
    def __init__(self, world_width: int, world_height: int):
        self.spatial_grid = SpatialGrid(world_width, world_height, cell_size=200)
        self.collision_system = OptimizedCollisionSystem(self.spatial_grid)
        self.particle_system = OptimizedParticleSystem(max_particles=20000)
        
        # Cache for expensive calculations
        self._range_cache = {}
        self._frame_count = 0
        
    def update_optimized(self, dt: float, buildings: List, enemies: List, missiles: List):
        """Optimized update loop with spatial partitioning."""
        self._frame_count += 1
        
        # Update particles
        self.particle_system.update(dt)
        
        # Clear spatial grid
        self.spatial_grid.clear()
        
        # Add all entities to spatial grid
        all_entities = buildings + enemies + missiles
        for entity in all_entities:
            self.spatial_grid.add_entity(entity, entity.x, entity.y)
            
        # Optimized turret targeting
        self._update_turret_targeting_optimized(buildings, enemies)
        
        # Optimized collision detection
        self._handle_collisions_optimized(enemies, missiles)
        
    def _update_turret_targeting_optimized(self, buildings: List, enemies: List):
        """Optimized turret targeting using spatial partitioning."""
        for building in buildings:
            if hasattr(building, 'range') and hasattr(building, 'target'):
                # Use spatial grid instead of checking all enemies
                nearby_enemies = self.spatial_grid.get_entities_in_range(
                    building.x, building.y, building.range
                )
                
                if nearby_enemies:
                    # Find closest enemy
                    closest_enemy = min(nearby_enemies, 
                                      key=lambda e: (e.x - building.x)**2 + (e.y - building.y)**2)
                    building.target = closest_enemy
                else:
                    building.target = None
                    
    def _handle_collisions_optimized(self, enemies: List, missiles: List):
        """Optimized collision handling."""
        # Check missile-enemy collisions
        missile_collisions = self.collision_system.check_circle_collisions(
            missiles + enemies,
            lambda e: getattr(e, 'radius', 10)
        )
        
        for entity1, entity2 in missile_collisions:
            # Handle collision logic here
            if hasattr(entity1, 'damage') and hasattr(entity2, 'health'):
                entity2.health -= entity1.damage
                # Emit explosion particle effect
                self.particle_system.emit_explosion(entity1.x, entity1.y, count=30)


# 5. PERFORMANCE PROFILER
class PerformanceProfiler:
    """
    Simple performance profiler to identify bottlenecks.
    """
    def __init__(self):
        self.timers = {}
        self.frame_times = []
        
    def start_timer(self, name: str):
        """Start timing a section."""
        import time
        self.timers[name] = time.perf_counter()
        
    def end_timer(self, name: str) -> float:
        """End timing and return duration."""
        import time
        if name in self.timers:
            duration = time.perf_counter() - self.timers[name]
            del self.timers[name]
            return duration
        return 0.0
        
    def profile_frame(self, frame_time: float):
        """Record frame time for FPS tracking."""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 300:  # Keep last 5 seconds at 60 FPS
            self.frame_times.pop(0)
            
    def get_average_fps(self) -> float:
        """Get average FPS over recent frames."""
        if not self.frame_times:
            return 0.0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
        
    def print_stats(self):
        """Print performance statistics."""
        avg_fps = self.get_average_fps()
        print(f"Average FPS: {avg_fps:.1f}")
        if self.frame_times:
            min_fps = 1.0 / max(self.frame_times)
            max_fps = 1.0 / min(self.frame_times)
            print(f"FPS Range: {min_fps:.1f} - {max_fps:.1f}")


# USAGE EXAMPLE:
"""
# In your main game loop, replace existing systems with optimized versions:

# Initialize optimized systems
optimized_logic = OptimizedGameLogicSystem(WORLD_WIDTH, WORLD_HEIGHT)
profiler = PerformanceProfiler()

# In your game loop:
def game_loop():
    dt = clock.tick(60) / 1000.0
    
    profiler.start_timer("update")
    optimized_logic.update_optimized(dt, buildings, enemies, missiles)
    update_time = profiler.end_timer("update")
    
    profiler.start_timer("render")
    # Your existing render code
    render_time = profiler.end_timer("render")
    
    profiler.profile_frame(dt)
    
    # Print stats every 60 frames
    if frame_count % 60 == 0:
        profiler.print_stats()
        print(f"Update: {update_time*1000:.1f}ms, Render: {render_time*1000:.1f}ms")
""" 