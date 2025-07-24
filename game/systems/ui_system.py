"""
UI system for handling all user interface elements.
"""

import pygame
from game.core.system_manager import System
from game.core.state_manager import GameStateType
from settings import *


class UISystem(System):
    """System responsible for all user interface rendering and interactions."""
    
    def __init__(self, render_system):
        super().__init__("UISystem")
        self.render_system = render_system
        self.current_state = None
    
    def initialize(self):
        """Initialize the UI system."""
        pass
    
    def update(self, dt):
        """Update UI system."""
        pass
    
    def set_current_state(self, state_type):
        """Set the current game state for UI rendering."""
        self.current_state = state_type
    
    def draw_menu(self):
        """Draw the main menu."""
        self.render_system.clear_screen()
        
        # Title
        title_text = self.render_system.title_font.render("SPACE GAME CLONE", True, WHITE)
        title_x = (SCREEN_WIDTH - title_text.get_width()) // 2
        self.render_system.screen.blit(title_text, (title_x, 200))
        
        # Instructions
        instructions = [
            "Press R to start a new game",
            "Press ESC to quit",
            "",
            "Controls:",
            "S/C/B/M/T/L/R/V - Select building type",
            "Mouse - Place/select buildings",
            "U - Upgrade selected building",
            "Arrow keys - Pan camera",
            "Mouse wheel - Zoom",
            "1/2/3/4 - Game speed (Pause/Normal/2x/3x)"
        ]
        
        y_offset = 300
        for instruction in instructions:
            text = self.render_system.hud_font.render(instruction, True, WHITE)
            text_x = (SCREEN_WIDTH - text.get_width()) // 2
            self.render_system.screen.blit(text, (text_x, y_offset))
            y_offset += 30
    
    def draw_pause_overlay(self):
        """Draw pause overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.render_system.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.render_system.title_font.render("PAUSED", True, WHITE)
        text_x = (SCREEN_WIDTH - pause_text.get_width()) // 2
        text_y = (SCREEN_HEIGHT - pause_text.get_height()) // 2
        self.render_system.screen.blit(pause_text, (text_x, text_y))
        
        # Instructions
        instruction_text = self.render_system.hud_font.render("Press P to resume or ESC for menu", True, WHITE)
        inst_x = (SCREEN_WIDTH - instruction_text.get_width()) // 2
        self.render_system.screen.blit(instruction_text, (inst_x, text_y + 60))
    
    def draw_game_over(self, final_score, high_score):
        """Draw game over screen."""
        self.render_system.clear_screen()
        
        # Game Over title
        title_text = self.render_system.title_font.render("GAME OVER", True, RED)
        title_x = (SCREEN_WIDTH - title_text.get_width()) // 2
        self.render_system.screen.blit(title_text, (title_x, 250))
        
        # Scores
        score_text = self.render_system.large_font.render(f"Final Score: {final_score}", True, WHITE)
        score_x = (SCREEN_WIDTH - score_text.get_width()) // 2
        self.render_system.screen.blit(score_text, (score_x, 320))
        
        high_score_text = self.render_system.large_font.render(f"High Score: {high_score}", True, YELLOW)
        high_x = (SCREEN_WIDTH - high_score_text.get_width()) // 2
        self.render_system.screen.blit(high_score_text, (high_x, 360))
        
        # Instructions
        restart_text = self.render_system.hud_font.render("Press R to restart or ESC for menu", True, WHITE)
        restart_x = (SCREEN_WIDTH - restart_text.get_width()) // 2
        self.render_system.screen.blit(restart_text, (restart_x, 450))
    
    def draw_hud(self, resources, wave_manager, score, kill_count, selected_building, energy_ratio):
        """Draw the main game HUD."""
        # Resource panel with glass effect
        self.render_system.draw_glass_panel(10, 45, 350, 35, alpha=160)
        
        minerals_text = self.render_system.font.render(f"⛏ {int(resources.minerals)}", True, (255, 215, 0))
        energy_text = self.render_system.font.render(f"⚡ {int(resources.energy)}/{int(resources.max_energy)}", True, (100, 200, 255))
        self.render_system.screen.blit(minerals_text, (20, 53))
        self.render_system.screen.blit(energy_text, (130, 53))
        
        # Enhanced energy bar with gradient
        energy_bar_width = 100
        energy_bar_x = 260
        self.render_system.draw_gradient_health_bar(energy_bar_x, 57, energy_bar_width, 8, energy_ratio)
        
        # Stats panel with glass effect
        stats_x = SCREEN_WIDTH - 510
        self.render_system.draw_glass_panel(stats_x, 45, 300, 35, alpha=160)
        
        wave_text = self.render_system.font.render(f"Wave {wave_manager.wave}", True, (255, 100, 100))
        score_text = self.render_system.font.render(f"Score: {score}", True, (200, 220, 255))
        kill_text = self.render_system.font.render(f"Kills: {kill_count}", True, (255, 150, 100))
        
        self.render_system.screen.blit(wave_text, (stats_x + 10, 53))
        self.render_system.screen.blit(score_text, (stats_x + 100, 53))
        self.render_system.screen.blit(kill_text, (stats_x + 200, 53))
        
        # Controls panel at bottom with glass effect
        controls_width = SCREEN_WIDTH - 200
        self.render_system.draw_glass_panel(0, SCREEN_HEIGHT - 60, controls_width, 60, alpha=160)
        
        camera_text = self.render_system.hud_font.render("🎯 Arrows: Pan | Scroll: Zoom", True, (200, 220, 255))
        speed_text = self.render_system.hud_font.render("⏯ Speed: 1-Pause 2-Normal 3-2x 4-3x", True, (200, 220, 255))
        
        self.render_system.screen.blit(camera_text, (10, SCREEN_HEIGHT - 52))
        self.render_system.screen.blit(speed_text, (10, SCREEN_HEIGHT - 32))
        
        # Show selected building info
        if selected_building:
            info_text = self.render_system.small_font.render(
                f"Selected: {selected_building.type.capitalize()} (Level {selected_building.level}) - "
                f"Health: {int(selected_building.health)}/{int(selected_building.max_health)}", 
                True, WHITE
            )
            self.render_system.screen.blit(info_text, (400, 135))
    
    def draw_building_panel(self, selected_build, resources):
        """Draw the building selection panel."""
        panel_width = 200
        panel_x = SCREEN_WIDTH - panel_width
        panel_height = SCREEN_HEIGHT
        
        # Use glass panel effect
        self.render_system.draw_glass_panel(panel_x, 0, panel_width, panel_height, alpha=200)
        
        # Title
        title_text = self.render_system.title_font.render("BUILDINGS", True, (200, 220, 255))
        title_x = (panel_width - title_text.get_width()) // 2
        self.render_system.screen.blit(title_text, (panel_x + title_x, 20))
        
        # Building buttons
        building_types = [
            ('Solar', 'solar', BUILD_COSTS['solar'], 'S'),
            ('Connector', 'connector', BUILD_COSTS['connector'], 'C'),
            ('Battery', 'battery', BUILD_COSTS['battery'], 'B'),
            ('Miner', 'miner', BUILD_COSTS['miner'], 'M'),
            ('Turret', 'turret', BUILD_COSTS['turret'], 'T'),
            ('Laser', 'laser', BUILD_COSTS['laser'], 'L'),
            ('SuperLaser', 'superlaser', BUILD_COSTS['superlaser'], 'K'),
            ('Repair', 'repair', BUILD_COSTS['repair'], 'R'),
            ('Converter', 'converter', BUILD_COSTS['converter'], 'V')
        ]
        
        button_height = 50
        button_margin = 8
        start_y = 60
        
        # Get mouse position for hover effects
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, (name, build_type, cost, hotkey) in enumerate(building_types):
            button_y = start_y + i * (button_height + button_margin)
            button_x = panel_x + 10
            button_width = panel_width - 20
            
            # Check states
            is_hovered = (button_x <= mouse_x <= button_x + button_width and 
                         button_y <= mouse_y <= button_y + button_height)
            is_active = (selected_build == build_type)
            is_affordable = (resources.minerals >= cost)
            
            # Glass button background
            button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            
            if is_active:
                base_color = (80, 120, 160, 200)
                highlight_color = (100, 140, 180, 220)
            elif is_hovered and is_affordable:
                base_color = (60, 100, 140, 200)  
                highlight_color = (80, 120, 160, 220)
            elif is_affordable:
                base_color = (40, 60, 100, 180)
                highlight_color = (60, 80, 120, 200)
            else:
                base_color = (30, 35, 45, 160)
                highlight_color = (40, 45, 55, 180)
            
            # Main button background
            button_surface.fill(base_color)
            
            # Top highlight for glass effect
            pygame.draw.rect(button_surface, highlight_color, (0, 0, button_width, button_height//3))
            
            # Border with glow for hovered buttons
            border_color = (120, 160, 200, 220) if is_hovered else (80, 100, 140, 180)
            pygame.draw.rect(button_surface, border_color, (0, 0, button_width, button_height), 2)
            
            # Hover glow effect
            if is_hovered and is_affordable:
                glow_surface = pygame.Surface((button_width + 6, button_height + 6), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (100, 150, 255, 40), (0, 0, button_width + 6, button_height + 6), 3)
                self.render_system.screen.blit(glow_surface, (button_x - 3, button_y - 3))
            
            self.render_system.screen.blit(button_surface, (button_x, button_y))
            
            # Text elements
            hotkey_text = self.render_system.small_font.render(hotkey, True, (255, 255, 100))
            self.render_system.screen.blit(hotkey_text, (button_x + 5, button_y + 5))
            
            name_color = (255, 255, 255) if is_affordable else (150, 150, 150)
            name_text = self.render_system.hud_font.render(name, True, name_color)
            self.render_system.screen.blit(name_text, (button_x + 25, button_y + 8))
            
            cost_color = (255, 255, 100) if is_affordable else (200, 150, 150)
            cost_text = self.render_system.small_font.render(f"Cost: {cost}", True, cost_color)
            self.render_system.screen.blit(cost_text, (button_x + 25, button_y + 28)) 