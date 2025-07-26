"""
Arcade HUD system for user interface.
"""

import arcade
from typing import Dict, Any


class ArcadeHUD:
    """HUD system for Arcade implementation."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
    def setup(self):
        """Initialize the HUD system."""
        print("Arcade HUD system setup complete")
        
    def render(self, game_data: Dict[str, Any]):
        """Render the HUD."""
        # Placeholder: draw some basic UI elements
        arcade.draw_text(f"Score: {game_data.get('score', 0)}", 10, self.height - 30, arcade.color.WHITE, 16)
        arcade.draw_text(f"Energy: {game_data.get('energy', 0)}/{game_data.get('max_energy', 200)}", 10, self.height - 50, arcade.color.WHITE, 16)
        arcade.draw_text(f"Minerals: {game_data.get('minerals', 0)}", 10, self.height - 70, arcade.color.WHITE, 16)
        arcade.draw_text(f"Wave: {game_data.get('wave', 1)}", 10, self.height - 90, arcade.color.WHITE, 16)
        
    def render_menu(self):
        """Render the main menu."""
        arcade.draw_text("SPACE GAME - ARCADE EDITION", self.width // 2, self.height // 2 + 50, arcade.color.WHITE, 32, anchor_x="center")
        arcade.draw_text("Press SPACE to start", self.width // 2, self.height // 2, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Press ESC to quit", self.width // 2, self.height // 2 - 30, arcade.color.WHITE, 16, anchor_x="center")
        
    def render_pause_overlay(self):
        """Render pause overlay."""
        # Semi-transparent overlay
        arcade.draw_rectangle_filled(self.width // 2, self.height // 2, self.width, self.height, (0, 0, 0, 128))
        arcade.draw_text("PAUSED", self.width // 2, self.height // 2 + 20, arcade.color.WHITE, 32, anchor_x="center")
        arcade.draw_text("Press ESC to resume", self.width // 2, self.height // 2 - 20, arcade.color.WHITE, 16, anchor_x="center")
        
    def resize(self, width: int, height: int):
        """Handle window resize."""
        self.width = width
        self.height = height 