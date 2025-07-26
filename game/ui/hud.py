"""
Arcade HUD system for user interface.
"""

import arcade
from typing import Dict, Any
import math


class ArcadeHUD:
    """HUD system for Arcade implementation."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.text_objects = {}
        
    def setup(self):
        """Initialize HUD text objects."""
        # Create persistent text objects for better performance
        self.text_objects = {
            'title': arcade.Text("SPACE GAME", self.width // 2, self.height // 2 + 50, 
                                arcade.color.WHITE, 48, anchor_x="center"),
            'subtitle': arcade.Text("Press SPACE to start", self.width // 2, self.height // 2, 
                                   arcade.color.WHITE, 24, anchor_x="center"),
            'controls': arcade.Text("WASD: Move | Mouse Wheel: Zoom | ESC: Pause", 
                                   self.width // 2, self.height // 2 - 50, 
                                   arcade.color.GRAY, 16, anchor_x="center"),
            'paused': arcade.Text("PAUSED", self.width // 2, self.height // 2 + 20, 
                                 arcade.color.WHITE, 32, anchor_x="center"),
            'resume': arcade.Text("Press ESC to resume", self.width // 2, self.height // 2 - 20, 
                                 arcade.color.WHITE, 16, anchor_x="center"),
            'quit': arcade.Text("Press Q to quit", self.width // 2, self.height // 2 - 50, 
                               arcade.color.WHITE, 16, anchor_x="center")
        }
        print("Arcade HUD system setup complete")
    
    def render(self, state: str, game_data: Dict[str, Any] = None):
        """Render HUD based on game state."""
        if state == "menu":
            self.render_menu()
        elif state == "playing":
            self.render_game_hud(game_data or {})
    
    def render_menu(self):
        """Render main menu."""
        self.text_objects['title'].draw()
        self.text_objects['subtitle'].draw()
        self.text_objects['controls'].draw()
    
    def render_game_hud(self, game_data: Dict[str, Any]):
        """Render in-game HUD for base defense RTS with power networks."""
        # Starting Base Health bar
        health_ratio = game_data.get('starting_base_health', 2000) / game_data.get('starting_base_max_health', 2000)
        bar_width = 250
        bar_height = 25
        left = 20
        right = left + bar_width
        top = self.height - 30
        bottom = top - bar_height
        
        # Starting base health bar
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (50, 50, 50))
        arcade.draw_lrbt_rectangle_filled(left, left + bar_width * health_ratio, bottom, top, (0, 150, 255))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)
        
        # Starting base health text
        health_text = f"Starting Base: {int(game_data.get('starting_base_health', 2000))}/{int(game_data.get('starting_base_max_health', 2000))}"
        arcade.draw_text(health_text, left, top + 5, arcade.color.WHITE, 14)
        
        # Resources section
        resource_x = 20
        resource_y = self.height - 80
        
        # Minerals
        minerals_text = f"Minerals: {game_data.get('minerals', 0)}"
        arcade.draw_text(minerals_text, resource_x, resource_y, arcade.color.CYAN, 16)
        
        # Energy
        energy_text = f"Energy: {game_data.get('energy', 0)}"
        arcade.draw_text(energy_text, resource_x, resource_y - 25, arcade.color.YELLOW, 16)
        
        # Power system
        power_gen = game_data.get('power_generated', 0)
        power_stored = game_data.get('power_stored', 0)
        power_capacity = game_data.get('power_capacity', 0)
        power_blocks = game_data.get('power_blocks', 0)
        
        if power_capacity > 0:
            power_ratio = power_stored / power_capacity
            power_text = f"Power: {int(power_stored)}/{int(power_capacity)} ({power_gen}/s)"
        else:
            power_ratio = 0
            power_text = f"Power: {int(power_stored)} ({power_gen}/s)"
        
        power_color = arcade.color.GREEN if power_stored > 10 else arcade.color.RED
        arcade.draw_text(power_text, resource_x, resource_y - 50, power_color, 14)
        
        # Power bar
        if power_capacity > 0:
            power_bar_width = 150
            power_bar_height = 8
            power_left = resource_x + 120
            power_right = power_left + power_bar_width
            power_top = resource_y - 45
            power_bottom = power_top - power_bar_height
            
            arcade.draw_lrbt_rectangle_filled(power_left, power_right, power_bottom, power_top, (50, 50, 50))
            arcade.draw_lrbt_rectangle_filled(power_left, power_left + power_bar_width * power_ratio, 
                                            power_bottom, power_top, power_color)
            arcade.draw_lrbt_rectangle_outline(power_left, power_right, power_bottom, power_top, arcade.color.WHITE, 1)
        
        # Power blocks info
        blocks_text = f"Power Networks: {power_blocks}"
        arcade.draw_text(blocks_text, resource_x, resource_y - 75, arcade.color.ELECTRIC_BLUE, 12)
        
        # Game stats (top right)
        stats_x = self.width - 220
        stats_y = self.height - 30
        
        # Score
        score_text = f"Score: {game_data.get('score', 0)}"
        arcade.draw_text(score_text, stats_x, stats_y, arcade.color.WHITE, 16)
        
        # Wave info
        wave_text = f"Wave: {game_data.get('wave', 1)}"
        arcade.draw_text(wave_text, stats_x, stats_y - 25, arcade.color.YELLOW, 16)
        
        # Next wave countdown
        next_wave = game_data.get('next_wave_in', 0)
        if next_wave > 0:
            wave_countdown = f"Next wave in: {int(next_wave)}s"
            arcade.draw_text(wave_countdown, stats_x, stats_y - 50, arcade.color.ORANGE, 14)
        
        # Enemies and buildings count
        enemies_text = f"Enemies: {game_data.get('enemies_count', 0)}"
        arcade.draw_text(enemies_text, stats_x, stats_y - 75, arcade.color.RED, 14)
        
        buildings_text = f"Buildings: {game_data.get('buildings_count', 0)}"
        arcade.draw_text(buildings_text, stats_x, stats_y - 95, arcade.color.GREEN, 14)
        
        # Building construction panel (bottom)
        panel_height = 140
        panel_y = panel_height
        
        # Panel background
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, panel_height, (30, 30, 30, 200))
        arcade.draw_lrbt_rectangle_outline(0, self.width, 0, panel_height, arcade.color.WHITE, 2)
        
        # Building buttons - Split into two rows
        button_width = 120
        button_height = 55
        button_spacing = 130
        start_x = 30
        row1_y = 75
        row2_y = 15
        
        # Row 1: Power and Defense
        row1_buildings = [
            {"key": "N", "name": "Power Node", "cost_minerals": 20, "cost_energy": 10, "color": arcade.color.ELECTRIC_BLUE},
            {"key": "P", "name": "Power Plant", "cost_minerals": 80, "cost_energy": 40, "color": arcade.color.YELLOW},
            {"key": "B", "name": "Battery", "cost_minerals": 60, "cost_energy": 30, "color": arcade.color.LIME_GREEN},
            {"key": "T", "name": "Missile Turret", "cost_minerals": 100, "cost_energy": 50, "color": arcade.color.RED},
            {"key": "L", "name": "Laser Turret", "cost_minerals": 120, "cost_energy": 60, "color": arcade.color.GREEN},
            {"key": "W", "name": "Wall", "cost_minerals": 15, "cost_energy": 5, "color": arcade.color.GRAY}
        ]
        
        # Row 2: Special and Advanced
        row2_buildings = [
            {"key": "R", "name": "Repair Node", "cost_minerals": 90, "cost_energy": 45, "color": arcade.color.CYAN},
            {"key": "H", "name": "Hangar Node", "cost_minerals": 150, "cost_energy": 75, "color": arcade.color.PURPLE},
            {"key": "X", "name": "Long Range Laser", "cost_minerals": 200, "cost_energy": 100, "color": arcade.color.LIME_GREEN},
            {"key": "Z", "name": "Long Range Missile", "cost_minerals": 250, "cost_energy": 125, "color": arcade.color.DARK_RED}
        ]
        
        current_minerals = game_data.get('minerals', 0)
        current_energy = game_data.get('energy', 0)
        
        # Draw row 1
        for i, building in enumerate(row1_buildings):
            x = start_x + i * button_spacing
            self._draw_building_button(building, x, row1_y, button_width, button_height, current_minerals, current_energy)
        
        # Draw row 2
        for i, building in enumerate(row2_buildings):
            x = start_x + i * button_spacing
            self._draw_building_button(building, x, row2_y, button_width, button_height, current_minerals, current_energy)
        
        # Controls and instructions
        controls_y = self.height - 170
        arcade.draw_text("WASD: Move Camera | Mouse Wheel: Zoom | Space: Center on Base", 
                        20, controls_y, arcade.color.GRAY, 11)
        arcade.draw_text("Power Network: Buildings need power connections to operate | Cyan lines = powered connections", 
                        20, controls_y - 15, arcade.color.GRAY, 11)
        
        # Debug info
        if game_data.get('projectiles_count', 0) > 0:
            debug_text = f"Projectiles: {game_data.get('projectiles_count', 0)}"
            arcade.draw_text(debug_text, 20, 145, arcade.color.GRAY, 10)
    
    def _draw_building_button(self, building: Dict, x: int, y: int, width: int, height: int, minerals: int, energy: int):
        """Draw a building button with icon, name, and costs."""
        # Check if affordable
        can_afford = (minerals >= building["cost_minerals"] and 
                     energy >= building["cost_energy"])
        
        # Button background
        if can_afford:
            button_color = (*building["color"][:3], 120)
            text_color = arcade.color.WHITE
        else:
            button_color = (80, 80, 80, 120)
            text_color = arcade.color.GRAY
        
        arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, button_color)
        arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, arcade.color.WHITE, 1)
        
        # Building icon
        icon_x = x + 15
        icon_y = y + height - 20
        icon_size = 8
        
        if building["name"] == "Power Node":
            # Circle with connection points
            arcade.draw_circle_filled(icon_x, icon_y, icon_size, building["color"])
            for i in range(6):
                angle = i * 60 * math.pi / 180
                px = icon_x + (icon_size + 2) * math.cos(angle)
                py = icon_y + (icon_size + 2) * math.sin(angle)
                arcade.draw_circle_filled(px, py, 1, arcade.color.WHITE)
        elif "Turret" in building["name"]:
            # Square with barrel
            arcade.draw_lrbt_rectangle_filled(icon_x - icon_size, icon_x + icon_size, 
                                            icon_y - icon_size, icon_y + icon_size, building["color"])
            arcade.draw_line(icon_x, icon_y, icon_x + icon_size + 2, icon_y, arcade.color.DARK_GRAY, 2)
        elif building["name"] == "Wall":
            # Small rectangle
            arcade.draw_lrbt_rectangle_filled(icon_x - icon_size//2, icon_x + icon_size//2, 
                                            icon_y - icon_size//2, icon_y + icon_size//2, building["color"])
        else:
            # Regular rectangle for other buildings
            arcade.draw_lrbt_rectangle_filled(icon_x - icon_size, icon_x + icon_size, 
                                            icon_y - icon_size, icon_y + icon_size, building["color"])
        
        # Hotkey
        arcade.draw_text(building["key"], x + 5, y + height - 12, text_color, 11, bold=True)
        
        # Building name (shortened)
        name = building["name"]
        if len(name) > 12:
            name = name[:10] + ".."
        arcade.draw_text(name, x + 35, y + height - 15, text_color, 9)
        
        # Costs
        cost_text = f"M{building['cost_minerals']}"
        if building["cost_energy"] > 0:
            cost_text += f" E{building['cost_energy']}"
        arcade.draw_text(cost_text, x + 5, y + 25, text_color, 8)
        
        # Description/stats (very brief)
        if "Turret" in building["name"]:
            if "Long Range" in building["name"]:
                desc = "Long range"
            else:
                desc = "Defense"
        elif building["name"] == "Power Plant":
            desc = "+20 power/s"
        elif building["name"] == "Battery":
            desc = "200 storage"
        elif building["name"] == "Power Node":
            desc = "6 connections"
        elif building["name"] == "Repair Node":
            desc = "Repairs nearby"
        elif building["name"] == "Wall":
            desc = "500 HP barrier"
        else:
            desc = "Special"
        
        arcade.draw_text(desc, x + 5, y + 5, text_color, 7)
    
    def render_pause_overlay(self):
        """Render pause overlay."""
        # Semi-transparent overlay
        left = 0
        right = self.width
        bottom = 0
        top = self.height
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, 128))
        
        # Pause text
        self.text_objects['paused'].draw()
        self.text_objects['resume'].draw()
        self.text_objects['quit'].draw()
    
    def resize(self, width: int, height: int):
        """Handle window resize."""
        self.width = width
        self.height = height
        
        # Update text positions
        self.text_objects['title'].x = width // 2
        self.text_objects['title'].y = height // 2 + 50
        self.text_objects['subtitle'].x = width // 2
        self.text_objects['subtitle'].y = height // 2
        self.text_objects['controls'].x = width // 2
        self.text_objects['controls'].y = height // 2 - 50
        self.text_objects['paused'].x = width // 2
        self.text_objects['paused'].y = height // 2 + 20
        self.text_objects['resume'].x = width // 2
        self.text_objects['resume'].y = height // 2 - 20
        self.text_objects['quit'].x = width // 2
        self.text_objects['quit'].y = height // 2 - 50 