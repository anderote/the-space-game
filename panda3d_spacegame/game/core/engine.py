"""
Panda3D Game Engine - Adapter for existing game logic
Preserves all game mechanics while adapting to Panda3D rendering
"""

import sys
import os

# Import Panda3D systems
from game.panda3d.camera_controller import Panda3DCamera
from game.panda3d.scene_manager import SceneManager
from game.panda3d.input_system import Panda3DInputSystem

class Panda3DGameEngine:
    """
    Main game engine that preserves existing game logic
    while adapting to Panda3D rendering pipeline
    """
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Game state
        self.state = "menu"  # menu, playing, paused, game_over
        self.game_time = 0.0
        
        print("Initializing game systems...")
        
        # Initialize systems
        self.init_core_systems()
        self.init_panda3d_systems()
        
    def init_core_systems(self):
        """Initialize core game systems (preserve existing logic)"""
        # For Phase 1, we'll create stub systems that will be replaced
        # with the actual implementations in later phases
        
        # Placeholder for core game systems
        self.minerals = 600  # Starting minerals from config
        self.energy = 50     # Starting energy from config
        self.wave_number = 1
        self.score = 0
        
        # These will be replaced with actual systems in Phase 3
        self.buildings = []
        self.enemies = []
        self.projectiles = []
        
        print("✓ Core game systems initialized (Phase 1 stubs)")
        
    def init_panda3d_systems(self):
        """Initialize Panda3D-specific systems"""
        try:
            # Scene management and lighting
            self.scene_manager = SceneManager(self.base)
            print("✓ Scene manager initialized")
            
            # Camera system
            self.camera = Panda3DCamera(self.base, self.config)
            print("✓ Camera system initialized")
            
            # Input handling
            self.input_system = Panda3DInputSystem(self.base, self)
            print("✓ Input system initialized")
            
        except Exception as e:
            print(f"✗ Error initializing Panda3D systems: {e}")
            raise
        
    def update(self, dt):
        """Main update loop - preserves existing game logic"""
        self.game_time += dt
        
        if self.state == "playing":
            # Update core game systems (Phase 1: minimal updates)
            self.update_game_logic(dt)
            
            # Update Panda3D systems
            self.camera.update(dt)
            self.input_system.update(dt)
            
        elif self.state == "menu":
            # Handle menu state
            self.input_system.update(dt)
            
    def update_game_logic(self, dt):
        """Update core game logic (Phase 1: placeholder)"""
        # In Phase 3, this will contain the full game logic
        # For now, just basic state management
        pass
            
    def start_game(self):
        """Start a new game"""
        print("Starting new game...")
        self.state = "playing"
        
        # Reset game state (preserve existing logic structure)
        self.minerals = 600
        self.energy = 50
        self.wave_number = 1
        self.score = 0
        self.game_time = 0.0
        
        # Clear entities
        self.buildings = []
        self.enemies = []
        self.projectiles = []
        
        # In Phase 3, we'll create the starting base here
        # For now, just log the game start
        print(f"✓ Game started! State: {self.state}")
        
    def pause_game(self):
        """Pause the game"""
        if self.state == "playing":
            self.state = "paused"
            print("Game paused")
        elif self.state == "paused":
            self.state = "playing"
            print("Game resumed")
            
    def end_game(self):
        """End the current game"""
        self.state = "game_over"
        print(f"Game over! Final score: {self.score}, Wave: {self.wave_number}")
        
    def get_game_data(self):
        """Get current game state data for UI"""
        return {
            "state": self.state,
            "minerals": self.minerals,
            "energy": self.energy,
            "wave": self.wave_number,
            "score": self.score,
            "game_time": self.game_time,
            "buildings_count": len(self.buildings),
            "enemies_count": len(self.enemies)
        }
        
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up game engine...")
        
        # Clean up Panda3D systems
        if hasattr(self, 'scene_manager'):
            self.scene_manager.cleanup()
            
        if hasattr(self, 'input_system'):
            self.input_system.cleanup()
            
        print("✓ Game engine cleanup complete") 