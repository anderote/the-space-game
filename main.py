#!/usr/bin/env python3
"""
Space Game Clone - Refactored Version
Main entry point for the game.
"""

import sys
import traceback
from game.core.engine import GameEngine


def main():
    """Main entry point for the Space Game Clone."""
    engine = None
    
    try:
        # Create and initialize the game engine
        engine = GameEngine()
        engine.initialize()
        
        # Run the game
        engine.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"Fatal error occurred: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Ensure cleanup happens
        if engine:
            try:
                engine._shutdown()
            except:
                pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 