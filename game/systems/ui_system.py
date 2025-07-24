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
            "Press O to toggle menu | Press P to quit",
            "",
            "Controls:",
            "S/C/B/M/T/L/R/V/H - Select building type",
            "ESC - Cancel building selection",
            "Mouse - Place/select buildings",
            "Right-click - Cancel/deselect",
            "U - Upgrade selected building",
            "X - Sell selected building",
            "Arrow keys - Pan camera",
            "Mouse wheel - Zoom",
            "1/2/3/4 - Game speed (0.5x/1x/2x/3x)",
            "Space - Pause/Resume"
        ]
        
        y_offset = 300
        for instruction in instructions:
            text = self.render_system.hud_font.render(instruction, True, WHITE)
            text_x = (SCREEN_WIDTH - text.get_width()) // 2
            self.render_system.screen.blit(text, (text_x, y_offset))
            y_offset += 30
    
    def draw_building_info_panel(self, building, resources):
        """Draw detailed building information panel."""
        # Panel properties
        panel_width = 280
        panel_height = 200
        panel_x = 10
        panel_y = 100
        
        # Use glass panel effect
        self.render_system.draw_glass_panel(panel_x, panel_y, panel_width, panel_height, alpha=200)
        
        # Title
        title_text = self.render_system.font.render(f"{building.type.upper()} INFO", True, (200, 220, 255))
        title_x = panel_x + (panel_width - title_text.get_width()) // 2
        self.render_system.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # Building stats
        y_offset = panel_y + 40
        line_height = 18
        
        # Basic info
        level_text = self.render_system.small_font.render(f"Level: {building.level}", True, WHITE)
        self.render_system.screen.blit(level_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Health bar and text
        health_ratio = building.health / building.max_health
        health_text = self.render_system.small_font.render(f"Health: {int(building.health)}/{int(building.max_health)}", True, WHITE)
        self.render_system.screen.blit(health_text, (panel_x + 10, y_offset))
        
        # Health bar
        bar_width = panel_width - 30
        bar_height = 8
        bar_x = panel_x + 15
        bar_y = y_offset + 15
        self.render_system.draw_gradient_health_bar(bar_x, bar_y, bar_width, bar_height, health_ratio)
        y_offset += line_height + 15
        
        # Power status
        power_status = "⚡ Powered" if building.powered else "❌ No Power"
        power_color = (100, 255, 100) if building.powered else (255, 100, 100)
        power_text = self.render_system.small_font.render(power_status, True, power_color)
        self.render_system.screen.blit(power_text, (panel_x + 10, y_offset))
        y_offset += line_height + 5
        
        # Disabled status and toggle button
        if hasattr(building, 'disabled'):
            status_text = "🔴 Disabled" if building.disabled else "🟢 Enabled"
            status_color = (255, 100, 100) if building.disabled else (100, 255, 100)
            status_display = self.render_system.small_font.render(status_text, True, status_color)
            self.render_system.screen.blit(status_display, (panel_x + 10, y_offset))
            
            # Toggle button
            toggle_text = "D - Enable" if building.disabled else "D - Disable"
            toggle_display = self.render_system.small_font.render(toggle_text, True, (200, 200, 255))
            self.render_system.screen.blit(toggle_display, (panel_x + 10, y_offset + 15))
            y_offset += line_height * 2 + 5
        
        # Building-specific stats
        self._draw_building_specific_stats(building, panel_x + 10, y_offset, line_height)
        
        # Action buttons at bottom
        button_y = panel_y + panel_height - 45
        
        # Upgrade button
        if building.level < MAX_LEVEL:
            upgrade_cost = building.upgrade_cost(BUILD_COSTS[building.type])
            can_upgrade = resources.minerals >= upgrade_cost
            upgrade_color = (100, 255, 100) if can_upgrade else (150, 150, 150)
            upgrade_text = self.render_system.small_font.render(f"U - Upgrade: {upgrade_cost}", True, upgrade_color)
            self.render_system.screen.blit(upgrade_text, (panel_x + 10, button_y))
        else:
            max_text = self.render_system.small_font.render("MAX LEVEL", True, (255, 215, 0))
            self.render_system.screen.blit(max_text, (panel_x + 10, button_y))
        
        # Sell button
        sell_price = int(0.5 * BUILD_COSTS[building.type])
        sell_text = self.render_system.small_font.render(f"X - Sell: {sell_price}", True, (255, 200, 200))
        self.render_system.screen.blit(sell_text, (panel_x + 10, button_y + 15))
    
    def _draw_building_specific_stats(self, building, x, y, line_height):
        """Draw building-type specific statistics."""
        if building.type == "solar":
            prod_text = self.render_system.small_font.render(f"Energy/s: {building.prod_rate:.1f}", True, (255, 255, 100))
            self.render_system.screen.blit(prod_text, (x, y))
            
        elif building.type == "battery":
            storage_text = self.render_system.small_font.render(f"Storage: {building.storage}", True, (255, 255, 100))
            self.render_system.screen.blit(storage_text, (x, y))
            
        elif building.type == "miner":
            mine_text = self.render_system.small_font.render(f"Mine Rate: {building.mine_rate:.1f}/s", True, (255, 255, 100))
            self.render_system.screen.blit(mine_text, (x, y))
            
        elif building.type == "turret":
            damage_text = self.render_system.small_font.render(f"Damage: {building.damage}", True, (255, 255, 100))
            range_text = self.render_system.small_font.render(f"Range: {building.fire_range:.0f}", True, (255, 255, 100))
            self.render_system.screen.blit(damage_text, (x, y))
            self.render_system.screen.blit(range_text, (x, y + line_height))
            
        elif building.type == "laser":
            damage_text = self.render_system.small_font.render(f"DPS: {building.damage_per_frame * 60:.1f}", True, (255, 255, 100))
            range_text = self.render_system.small_font.render(f"Range: {building.fire_range:.0f}", True, (255, 255, 100))
            self.render_system.screen.blit(damage_text, (x, y))
            self.render_system.screen.blit(range_text, (x, y + line_height))
            
        elif building.type == "superlaser":
            damage_text = self.render_system.small_font.render(f"DPS: {building.damage_per_frame * 60:.1f}", True, (255, 255, 100))
            range_text = self.render_system.small_font.render(f"Range: {building.fire_range:.0f}", True, (255, 255, 100))
            self.render_system.screen.blit(damage_text, (x, y))
            self.render_system.screen.blit(range_text, (x, y + line_height))
            
        elif building.type == "repair":
            heal_text = self.render_system.small_font.render(f"Heal Rate: {building.heal_rate:.1f}/s", True, (255, 255, 100))
            range_text = self.render_system.small_font.render(f"Range: {building.heal_range:.0f}", True, (255, 255, 100))
            self.render_system.screen.blit(heal_text, (x, y))
            self.render_system.screen.blit(range_text, (x, y + line_height))
            
        elif building.type == "converter":
            convert_text = self.render_system.small_font.render(f"Rate: {building.conversion_rate:.1f}/s", True, (255, 255, 100))
            energy_text = self.render_system.small_font.render(f"Energy Cost: {building.energy_cost:.1f}/s", True, (255, 255, 100))
            self.render_system.screen.blit(convert_text, (x, y))
            self.render_system.screen.blit(energy_text, (x, y + line_height))
            
        elif building.type == "hangar":
            ships_text = self.render_system.small_font.render(f"Ships: {len(building.deployed_ships)}/{building.max_ships}", True, (255, 255, 100))
            range_text = self.render_system.small_font.render(f"Range: {building.ship_range}", True, (255, 255, 100))
            self.render_system.screen.blit(ships_text, (x, y))
            self.render_system.screen.blit(range_text, (x, y + line_height))
    
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
    
    def draw_hud(self, resources, wave_manager, score, kill_count, selected_building, energy_ratio, energy_production=0.0, solar_count=0, solar_levels=0, research_system=None):
        """Draw the main game HUD."""
        # Resource panel with glass effect (made wider for enhanced energy display)
        self.render_system.draw_glass_panel(10, 45, 380, 35, alpha=160)
        
        minerals_text = self.render_system.font.render(f"⛏ {int(resources.minerals)}", True, (255, 215, 0))
        energy_text = self.render_system.font.render(f"⚡ {int(resources.energy)}/{int(resources.max_energy)}", True, (100, 200, 255))
        # Enhanced energy production display with solar panel details
        if solar_count > 0:
            avg_level = solar_levels / solar_count if solar_count > 0 else 0
            energy_prod_text = self.render_system.small_font.render(f"⚡/s: {energy_production:.1f} ({solar_count}☀ L{avg_level:.1f})", True, (150, 255, 150))
        else:
            energy_prod_text = self.render_system.small_font.render(f"⚡/s: {energy_production:.1f} (No solar panels)", True, (255, 100, 100))
        
        self.render_system.screen.blit(minerals_text, (20, 53))
        self.render_system.screen.blit(energy_text, (130, 53))
        self.render_system.screen.blit(energy_prod_text, (20, 67))
        
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
        
        # Draw next wave preview
        try:
            next_wave_num, ship_counts = wave_manager.get_next_wave_preview()
            if not wave_manager.wave_active and ship_counts:
                # Wave preview panel
                preview_y = 85
                preview_width = 250
                preview_height = min(120, 25 + len(ship_counts) * 15)
                self.render_system.draw_glass_panel(stats_x, preview_y, preview_width, preview_height, alpha=140)
                
                preview_title = self.render_system.small_font.render(f"Next Wave {next_wave_num}:", True, (255, 255, 150))
                self.render_system.screen.blit(preview_title, (stats_x + 10, preview_y + 5))
                
                y_offset = preview_y + 20
                for ship_type, count in ship_counts.items():
                    if count > 0:
                        preview_text = self.render_system.small_font.render(f"  {ship_type}: {count}", True, (200, 200, 200))
                        self.render_system.screen.blit(preview_text, (stats_x + 10, y_offset))
                        y_offset += 12
                        
                # Show 'n' key hint
                skip_hint = self.render_system.small_font.render("Press 'N' to start wave", True, (150, 255, 150))
                self.render_system.screen.blit(skip_hint, (stats_x + 10, y_offset + 5))
        except Exception as e:
            # Fallback if preview fails
            pass
        
        # Controls panel at bottom with glass effect
        controls_width = SCREEN_WIDTH - 200
        self.render_system.draw_glass_panel(0, SCREEN_HEIGHT - 60, controls_width, 60, alpha=160)
        
        camera_text = self.render_system.hud_font.render("🎯 Arrows: Pan | Scroll: Zoom | ESC: Cancel | N: Next Wave", True, (200, 220, 255))
        speed_text = self.render_system.hud_font.render("⏯ Speed: 1-0.5x 2-1x 3-2x 4-3x | Space: Pause", True, (200, 220, 255))
        
        self.render_system.screen.blit(camera_text, (10, SCREEN_HEIGHT - 52))
        self.render_system.screen.blit(speed_text, (10, SCREEN_HEIGHT - 32))
        
        # Building info panel
        if selected_building:
            self.draw_building_info_panel(selected_building, resources)
        
        # Research panel
        if research_system:
            self.draw_research_panel(research_system, resources)
    
    def draw_building_panel(self, selected_build, resources):
        """Draw the building selection panel."""
        panel_width = 180  # Reduced width to make room for research panel
        panel_x = SCREEN_WIDTH - 380  # Moved left to make room for research panel
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
            ('Converter', 'converter', BUILD_COSTS['converter'], 'V'),
            ('Hangar', 'hangar', BUILD_COSTS['hangar'], 'H'),
            ('Missile', 'missile_launcher', BUILD_COSTS['missile_launcher'], 'G'),
            ('Force Field', 'force_field', BUILD_COSTS['force_field'], 'F')
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
    
    def draw_research_panel(self, research_system, resources):
        """Draw the research panel."""
        panel_width = 200
        panel_x = SCREEN_WIDTH - panel_width
        panel_height = SCREEN_HEIGHT
        
        # Use glass panel effect
        self.render_system.draw_glass_panel(panel_x, 0, panel_width, panel_height, alpha=200)
        
        # Title
        title_text = self.render_system.title_font.render("RESEARCH", True, (255, 200, 100))
        title_x = (panel_width - title_text.get_width()) // 2
        self.render_system.screen.blit(title_text, (panel_x + title_x, 20))
        
        # Scrollable research list
        available_research = research_system.get_available_research()
        completed_research = [research_system.research_nodes[node_id] for node_id in research_system.completed_research]
        
        button_height = 60
        button_margin = 5
        start_y = 60
        max_visible = (SCREEN_HEIGHT - start_y - 20) // (button_height + button_margin)
        
        # Get mouse position for hover effects
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Show available research first
        y_offset = start_y
        
        if available_research:
            # Available research header
            header_text = self.render_system.small_font.render("Available:", True, (100, 255, 100))
            self.render_system.screen.blit(header_text, (panel_x + 10, y_offset))
            y_offset += 25
            
            for research in available_research[:max_visible // 2]:
                if y_offset + button_height > SCREEN_HEIGHT - 20:
                    break
                self._draw_research_button(research, panel_x + 10, y_offset, panel_width - 20, button_height, resources, mouse_x, mouse_y, True)
                y_offset += button_height + button_margin
        
        # Show completed research
        if completed_research and y_offset < SCREEN_HEIGHT - 100:
            y_offset += 10
            header_text = self.render_system.small_font.render("Completed:", True, (100, 100, 255))
            self.render_system.screen.blit(header_text, (panel_x + 10, y_offset))
            y_offset += 25
            
            for research in completed_research:
                if y_offset + button_height > SCREEN_HEIGHT - 20:
                    break
                self._draw_research_button(research, panel_x + 10, y_offset, panel_width - 20, button_height, resources, mouse_x, mouse_y, False)
                y_offset += button_height + button_margin
    
    def _draw_research_button(self, research, x, y, width, height, resources, mouse_x, mouse_y, can_research):
        """Draw a single research button."""
        # Check if mouse is hovering
        hovering = x <= mouse_x <= x + width and y <= mouse_y <= y + height
        
        # Button colors
        if research.completed:
            bg_color = (0, 100, 0, 120)  # Green for completed
            border_color = (0, 200, 0)
        elif can_research and resources.minerals >= research.cost:
            bg_color = (100, 100, 0, 120) if not hovering else (150, 150, 0, 150)  # Yellow for available
            border_color = (255, 255, 0) if not hovering else (255, 255, 100)
        else:
            bg_color = (100, 0, 0, 120)  # Red for unavailable
            border_color = (200, 0, 0)
        
        # Draw button background
        button_rect = pygame.Rect(x, y, width, height)
        self.render_system.draw_glass_panel(x, y, width, height, alpha=120)
        pygame.draw.rect(self.render_system.screen, border_color, button_rect, 2)
        
        # Research name
        name_text = self.render_system.small_font.render(research.name, True, (255, 255, 255))
        name_width = name_text.get_width()
        if name_width > width - 10:
            # Truncate if too long
            truncated_name = research.name[:int(len(research.name) * (width - 10) / name_width)] + "..."
            name_text = self.render_system.small_font.render(truncated_name, True, (255, 255, 255))
        self.render_system.screen.blit(name_text, (x + 5, y + 5))
        
        # Cost
        cost_color = (255, 100, 100) if resources.minerals < research.cost else (255, 255, 100)
        if research.completed:
            cost_text = self.render_system.small_font.render("DONE", True, (100, 255, 100))
        else:
            cost_text = self.render_system.small_font.render(f"⛏ {research.cost}", True, cost_color)
        self.render_system.screen.blit(cost_text, (x + 5, y + 25))
        
        # Category icon
        category_icons = {
            "combat": "⚔",
            "defense": "🛡",
            "economy": "⛏",
            "energy": "⚡",
            "support": "🔧"
        }
        icon = category_icons.get(research.category, "🔬")
        icon_text = self.render_system.small_font.render(icon, True, (200, 200, 200))
        self.render_system.screen.blit(icon_text, (x + width - 25, y + 5))
        
        # Description (truncated)
        desc_text = research.description
        if len(desc_text) > 25:
            desc_text = desc_text[:22] + "..."
        desc_render = self.render_system.small_font.render(desc_text, True, (200, 200, 200))
        self.render_system.screen.blit(desc_render, (x + 5, y + 40)) 