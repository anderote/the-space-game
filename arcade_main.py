#!/usr/bin/env python3
"""
Space Game - Arcade Implementation
Main entry point for the Arcade version with shader support.
"""

import arcade
import sys
from game.core.window import SpaceGameWindow


def main():
    """Main entry point for the Arcade Space Game."""
    try:
        # Create and run the game window
        window = SpaceGameWindow(1600, 900, "Space Game - Arcade Edition")
        window.setup()
        arcade.run()
        
    except Exception as e:
        print(f"Fatal error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 