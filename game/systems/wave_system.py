"""
Wave System - Enemy spawning and wave management
"""

import time
import math
import random
from typing import List, Dict, Optional
from ..entities.enemy import Enemy

class WaveSystem:
    """Manages enemy wave spawning and progression"""
    
    def __init__(self, config, game_engine, scene_manager):
        self.config = config
        self.game_engine = game_engine
        self.scene_manager = scene_manager
        
        # Wave state
        self.current_wave = 1
        self.wave_active = False
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.wave_start_time = 0
        self.last_wave_complete_time = 0
        self.manual_wave_start = False  # Allow manual wave starting
        self.next_wave_preview = None  # Preview of next wave
        self.total_enemies_in_wave = 0  # Total enemies in current wave
        
        # Timing configuration
        wave_timing = config.waves.get("wave_timing", {})
        self.initial_wait = 45.0  # Start first wave at 45 seconds
        self.spawn_interval = 0.1  # Time between individual enemy spawns in a cluster (2x faster spawning)
        self.cluster_interval = 2.0  # Time between clusters within a wave
        self.wave_interval = 30.0  # Time between waves (gets shorter over time)
        self.max_wave_duration = 240.0  # Maximum wave duration (4 minutes)a
        self.growth_factor = 1.3  # Geometric growth factor for difficulty (reduced by half)
        
        # Game start time
        self.game_start_time = time.time()
        self.first_wave_spawned = False
        
        # Spawn points (around the edges of the map)
        world_width = config.game.get("display", {}).get("world_width", 4800)
        world_height = config.game.get("display", {}).get("world_height", 2700)
        
        # Extended spawn points for multi-directional waves
        self.all_spawn_points = [
            # Left edge spawn points
            (0, world_height // 4),              # Left-top
            (0, world_height // 2),              # Left-center
            (0, 3 * world_height // 4),          # Left-bottom
            
            # Right edge spawn points
            (world_width, world_height // 4),    # Right-top
            (world_width, world_height // 2),    # Right-center
            (world_width, 3 * world_height // 4), # Right-bottom
            
            # Top edge spawn points
            (world_width // 4, 0),               # Top-left
            (world_width // 2, 0),               # Top-center
            (3 * world_width // 4, 0),           # Top-right
            
            # Bottom edge spawn points
            (world_width // 4, world_height),    # Bottom-left
            (world_width // 2, world_height),    # Bottom-center
            (3 * world_width // 4, world_height) # Bottom-right
        ]
    
    def get_spawn_points_for_wave(self, wave_number: int) -> List[tuple]:
        """Get spawn points based on wave number - more points for harder waves"""
        if wave_number <= 3:
            # Early waves: single spawn point (center left)
            return [self.all_spawn_points[1]]  # Left-center
        elif wave_number <= 6:
            # Medium waves: two opposite spawn points
            return [self.all_spawn_points[1], self.all_spawn_points[4]]  # Left-center, Right-center
        elif wave_number <= 10:
            # Harder waves: four spawn points (cardinal directions)
            return [self.all_spawn_points[1], self.all_spawn_points[4], 
                   self.all_spawn_points[7], self.all_spawn_points[10]]  # Left, Right, Top, Bottom centers
        elif wave_number <= 15:
            # Very hard waves: six spawn points
            return [self.all_spawn_points[0], self.all_spawn_points[1], self.all_spawn_points[2],  # Left edge
                   self.all_spawn_points[3], self.all_spawn_points[4], self.all_spawn_points[5]]   # Right edge
        else:
            # Extreme waves: all spawn points
            return self.all_spawn_points
        
    def update(self, dt: float):
        """Update wave system"""
        current_time = time.time()
        game_time = current_time - self.game_start_time
        
        # Check if it's time to start the first wave
        if not self.first_wave_spawned and game_time >= self.initial_wait:
            self.start_wave(1)
            self.first_wave_spawned = True
            print(f"🌊 Wave {self.current_wave} starting!")
        
        # Spawn enemies based on their individual spawn delays
        if self.wave_active and self.enemies_to_spawn:
            wave_time = current_time - self.wave_start_time
            
            # Check if next enemy should spawn
            while (self.enemies_to_spawn and 
                   wave_time >= self.enemies_to_spawn[0].get("spawn_delay", 0)):
                self.spawn_next_enemy()
        
        # Check if wave is complete
        if self.wave_active:
            wave_duration = current_time - self.wave_start_time
            
            # Complete wave if all enemies spawned and defeated
            if not self.enemies_to_spawn and len(self.game_engine.enemies) == 0:
                self.complete_wave()
            # Force complete wave after maximum duration (4 minutes)
            elif wave_duration >= self.max_wave_duration:
                print(f"⏰ Wave {self.current_wave} auto-completed after {self.max_wave_duration/60:.1f} minutes")
                self.force_complete_wave()
        
        # Check if it's time for next wave (after wave complete + interval)
        elif (not self.wave_active and self.last_wave_complete_time > 0 and 
              current_time - self.last_wave_complete_time >= self.get_current_wave_interval()):
            self.start_wave(self.current_wave + 1)
    
    def start_wave(self, wave_number: int):
        """Start a new wave"""
        self.current_wave = wave_number
        self.wave_active = True
        self.wave_start_time = time.time()
        
        # Generate enemies for this wave
        self.enemies_to_spawn = self.generate_wave_enemies(wave_number)
        self.total_enemies_in_wave = len(self.enemies_to_spawn)
        
        print(f"Wave {wave_number} - {len(self.enemies_to_spawn)} enemies incoming!")
        
        # Update game engine wave number
        self.game_engine.wave_number = wave_number
    
    def generate_wave_enemies(self, wave_number: int) -> List[Dict]:
        """Generate enemy list for a wave with clusters"""
        enemies = []
        
        # Geometric scaling of difficulty
        base_enemies_per_cluster = max(2, int(2 * (self.growth_factor ** (wave_number - 1))))
        num_clusters = max(1, wave_number + 1)  # More clusters as waves progress (faster scaling)
        
        print(f"🌊 Wave {wave_number}: {num_clusters} clusters, ~{base_enemies_per_cluster} enemies per cluster")
        
        # Enemy types based on wave progression
        available_types = self.get_available_enemy_types(wave_number)
        
        cluster_delay = 0.0
        for cluster in range(num_clusters):
            # Each cluster spawns from a different edge  
            spawn_point = self.all_spawn_points[cluster % len(self.all_spawn_points)]
            
            # Cluster size varies (±25% of base)
            cluster_size = max(1, base_enemies_per_cluster + random.randint(-1, 2))
            
            # Add some randomness to spawn position within cluster
            cluster_spread = 100  # Pixels
            
            for i in range(cluster_size):
                enemy_type = self.choose_enemy_type(available_types, wave_number)
                
                # Spread enemies in cluster
                offset_x = random.uniform(-cluster_spread, cluster_spread)
                offset_y = random.uniform(-cluster_spread, cluster_spread)
                
                enemies.append({
                    "type": enemy_type,
                    "x": spawn_point[0] + offset_x,
                    "y": spawn_point[1] + offset_y,
                    "spawn_delay": cluster_delay + (i * self.spawn_interval)  # Stagger spawning within cluster
                })
            
            # Next cluster spawns after current cluster + interval
            cluster_delay += (cluster_size * self.spawn_interval) + self.cluster_interval
        
        # Sort by spawn delay so they spawn in order
        enemies.sort(key=lambda x: x.get("spawn_delay", 0))
        
        return enemies
    
    def get_available_enemy_types(self, wave_number: int) -> List[str]:
        """Get available enemy types for a wave"""
        types = ["basic"]
        if wave_number >= 3:
            types.append("kamikaze")
        if wave_number >= 5:
            types.append("stealth") 
        if wave_number >= 8:
            types.append("large")
        if wave_number >= 12:
            types.append("assault")
        if wave_number >= 15:
            types.append("cruiser")
        if wave_number >= 20:
            types.append("mothership")
        return types
    
    def choose_enemy_type(self, available_types: List[str], wave_number: int) -> str:
        """Choose an enemy type with weighted probability"""
        # Basic enemies are common early, rarer later
        weights = []
        for enemy_type in available_types:
            if enemy_type == "basic":
                weights.append(max(1, 10 - wave_number))  # Gets rarer
            elif enemy_type == "kamikaze":
                weights.append(3)
            elif enemy_type == "stealth":
                weights.append(2)
            elif enemy_type in ["large", "assault"]:
                weights.append(2)
            elif enemy_type == "cruiser":
                weights.append(1)
            elif enemy_type == "mothership":
                weights.append(1 if wave_number >= 25 else 0)
            else:
                weights.append(1)
        
        return random.choices(available_types, weights=weights)[0]
    
    def spawn_next_enemy(self):
        """Spawn the next enemy in the queue"""
        if not self.enemies_to_spawn:
            return
        
        enemy_data = self.enemies_to_spawn.pop(0)
        
        # Create enemy with wave scaling
        enemy = Enemy(
            enemy_data["type"],
            enemy_data["x"],
            enemy_data["y"],
            self.config,
            self.game_engine,
            self.current_wave
        )
        
        # Create visual representation with velocity information
        enemy.visual_node = self.scene_manager.entity_visualizer.create_enemy_visual(
            enemy_data["type"], enemy_data["x"], enemy_data["y"], enemy.radius, 
            enemy.velocity_x, enemy.velocity_y
        )
        
        # Add dynamic lighting for enemy (TEMPORARILY DISABLED)
        # Dynamic lighting has API compatibility issues with current Panda3D version
        print(f"✓ Skipping dynamic lighting for {enemy_data['type']} enemy (temporarily disabled)")
        
        # if (hasattr(self.scene_manager, 'dynamic_lighting') and 
        #     self.scene_manager.dynamic_lighting):
        #     
        #     light_id = self.scene_manager.dynamic_lighting.create_enemy_light(
        #         enemy_data["x"], enemy_data["y"], 5, enemy_data["type"]
        #     )
        #     
        #     if light_id is not None:
        #         enemy.dynamic_light_id = light_id
        
        # Add to game engine
        self.game_engine.enemies.append(enemy)
        
        print(f"Spawned {enemy_data['type']} enemy at ({enemy_data['x']}, {enemy_data['y']})")
    
    def get_current_wave_interval(self) -> float:
        """Get the interval before next wave (gets shorter over time)"""
        # Wave interval decreases but never goes below 15 seconds
        return max(15.0, self.wave_interval - (self.current_wave * 2))
    
    def complete_wave(self):
        """Complete the current wave and prepare for next"""
        self.wave_active = False
        self.last_wave_complete_time = time.time()
        next_wave_delay = self.get_current_wave_interval()
        
        print(f"✓ Wave {self.current_wave} complete!")
        print(f"  Next wave in {next_wave_delay:.0f} seconds...")
    
    def force_complete_wave(self):
        """Force complete the current wave due to timeout"""
        # Clear any remaining enemies to spawn
        self.enemies_to_spawn.clear()
        
        # NOTE: Do NOT clear existing enemies - they should continue attacking
        # Enemies are independent once spawned and will be removed when destroyed
        
        # Complete the wave normally
        self.complete_wave()
        
        # Award bonus points  
        self.game_engine.score += self.current_wave * 10
        
        # Generate preview for next wave
        self.generate_next_wave_preview()
    
    def generate_next_wave_preview(self):
        """Generate preview information for the next wave"""
        next_wave = self.current_wave + 1
        enemies = self.generate_wave_enemies(next_wave)
        
        # Count enemy types
        enemy_counts = {}
        for enemy in enemies:
            enemy_type = enemy['type']
            enemy_counts[enemy_type] = enemy_counts.get(enemy_type, 0) + 1
        
        # Create preview text
        preview_parts = []
        for enemy_type, count in enemy_counts.items():
            preview_parts.append(f"{count} {enemy_type}")
        
        self.next_wave_preview = {
            'wave_number': next_wave,
            'total_enemies': len(enemies),
            'enemy_breakdown': enemy_counts,
            'preview_text': f"Wave {next_wave}: " + ", ".join(preview_parts)
        }
    
    def can_start_next_wave(self) -> bool:
        """Check if the next wave can be started manually"""
        return not self.wave_active and self.last_wave_complete_time > 0
    
    def start_next_wave_manually(self):
        """Start the next wave manually"""
        if self.can_start_next_wave():
            self.start_wave(self.current_wave + 1)
            return True
        return False
    
    def get_next_wave_preview(self) -> Optional[Dict]:
        """Get preview information for the next wave"""
        if not self.next_wave_preview:
            self.generate_next_wave_preview()
        return self.next_wave_preview
    
    def get_time_until_auto_wave(self) -> float:
        """Get time remaining until automatic wave start"""
        if self.wave_active or self.last_wave_complete_time == 0:
            return 0
        
        elapsed = time.time() - self.last_wave_complete_time
        next_wave_delay = self.get_current_wave_interval()
        return max(0, next_wave_delay - elapsed)
    
    def get_wave_progress(self) -> Dict:
        """Get current wave progress information"""
        if not self.wave_active:
            return {"enemies_remaining": 0, "total_enemies": 0, "enemies_alive": 0}
        
        # Count alive enemies in the game
        enemies_alive = len([e for e in self.game_engine.enemies if e.is_alive()])
        enemies_remaining = len(self.enemies_to_spawn) + enemies_alive
        
        return {
            "enemies_remaining": enemies_remaining,
            "total_enemies": self.total_enemies_in_wave,
            "enemies_alive": enemies_alive,
            "enemies_to_spawn": len(self.enemies_to_spawn)
        }
    
    def cleanup(self):
        """Clean up wave system"""
        self.enemies_to_spawn.clear()
        self.wave_active = False
