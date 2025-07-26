#!/usr/bin/env python3
"""
Panda3D Space Game Clone - Main Entry Point
Phase 1: Basic application setup with ShowBase
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_loader import GameConfig
from game.core.engine import Panda3DGameEngine

class SpaceGameApp(ShowBase):
    """Main Panda3D application class"""
    
    def __init__(self):
        # Initialize Panda3D ShowBase
        ShowBase.__init__(self)
        
        print("Initializing Panda3D Space Game Clone...")
        
        # Load configuration
        try:
            self.config = GameConfig("config/")
            print("✓ Configuration loaded successfully")
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            return
        
        # Set up window
        self.setup_window()
        
        # Initialize game engine
        try:
            self.game_engine = Panda3DGameEngine(self, self.config)
            print("✓ Game engine initialized")
        except Exception as e:
            print(f"✗ Error initializing game engine: {e}")
            return
        
        # Start the game loop
        self.setup_tasks()
        print("✓ Phase 1 setup complete!")
        print("Controls: ESC = Quit, SPACE = Start Game")
        
    def setup_window(self):
        """Configure the Panda3D window"""
        try:
            display_config = self.config.game.get("display", {})
            
            # Set window title and size
            from panda3d.core import WindowProperties
            props = WindowProperties()
            props.setTitle("Space Game Clone - Panda3D Edition (Phase 1)")
            props.setSize(display_config.get("screen_width", 1600), display_config.get("screen_height", 900))
            self.win.requestProperties(props)
            
            # Disable default mouse camera control
            self.disableMouse()
            
            print(f"✓ Window configured: {display_config.get('screen_width', 1600)}x{display_config.get('screen_height', 900)}")
            
        except Exception as e:
            print(f"✗ Error setting up window: {e}")
        
    def setup_tasks(self):
        """Set up main game loop tasks"""
        # Main game update task
        self.taskMgr.add(self.game_update_task, "game_update")
        
    def game_update_task(self, task):
        """Main game update loop"""
        dt = globalClock.getDt()
        
        # Update game engine
        if hasattr(self, 'game_engine'):
            self.game_engine.update(dt)
            
        return task.cont
        
    def cleanup(self):
        """Clean up resources on exit"""
        print("Cleaning up resources...")
        if hasattr(self, 'game_engine'):
            self.game_engine.cleanup()

def main():
    """Application entry point"""
    print("=== Panda3D Space Game Clone - Phase 1 ===")
    try:
        app = SpaceGameApp()
        app.run()
        return 0
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if 'app' in locals():
            app.cleanup()

if __name__ == "__main__":
    sys.exit(main()) 