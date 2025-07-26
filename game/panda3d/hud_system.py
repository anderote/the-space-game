"""
Panda3D HUD System - Phase 2 Implementation
Basic on-screen text display for game state information
"""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

class HUDSystem:
    """Manages on-screen display of game information"""
    
    def __init__(self, base, game_engine):
        self.base = base
        self.game_engine = game_engine
        
        # HUD elements
        self.hud_elements = {}
        
        self.setup_hud()
        
    def setup_hud(self):
        """Set up basic HUD elements"""
        print("Setting up Phase 2 HUD...")
        
        # Resource display (top-left)
        self.hud_elements['minerals'] = OnscreenText(
            text="Minerals: 600",
            pos=(-1.8, 0.9),
            scale=0.06,
            fg=(1, 1, 0, 1),  # Yellow
            align=TextNode.ALeft,
            mayChange=True
        )
        
        self.hud_elements['energy'] = OnscreenText(
            text="Energy: 50",
            pos=(-1.8, 0.8),
            scale=0.06,
            fg=(0, 1, 1, 1),  # Cyan
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Game state (top-center)
        self.hud_elements['game_state'] = OnscreenText(
            text="Press SPACE to start",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),  # White
            align=TextNode.ACenter,
            mayChange=True
        )
        
        # Camera info (top-right)
        self.hud_elements['camera_info'] = OnscreenText(
            text="Camera: (2400, 1350) Zoom: 1.0x",
            pos=(1.8, 0.9),
            scale=0.05,
            fg=(0.8, 0.8, 0.8, 1),  # Light gray
            align=TextNode.ARight,
            mayChange=True
        )
        
        # Controls help (bottom-left)
        self.hud_elements['controls'] = OnscreenText(
            text="WASD: Move | Wheel: Zoom | C: Center | R: Reset Zoom",
            pos=(-1.8, -0.9),
            scale=0.04,
            fg=(0.7, 0.7, 0.7, 1),  # Gray
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Building selection (bottom-right)
        self.hud_elements['building_hint'] = OnscreenText(
            text="Buildings: Q-Solar E-Connector B-Battery M-Miner T-Turret L-Laser",
            pos=(1.8, -0.9),
            scale=0.04,
            fg=(0.7, 0.7, 0.7, 1),  # Gray
            align=TextNode.ARight,
            mayChange=True
        )
        
        # Construction mode indicator (center-bottom)
        self.hud_elements['construction'] = OnscreenText(
            text="",
            pos=(0, -0.8),
            scale=0.06,
            fg=(1, 0.5, 0, 1),  # Orange
            align=TextNode.ACenter,
            mayChange=True
        )
        
        print("✓ HUD setup complete")
        
    def update(self, dt):
        """Update HUD elements with current game state"""
        game_data = self.game_engine.get_game_data()
        
        # Update resources
        self.hud_elements['minerals']['text'] = f"Minerals: {game_data['minerals']}"
        self.hud_elements['energy']['text'] = f"Energy: {game_data['energy']}"
        
        # Update game state
        state_text = self.get_state_text(game_data)
        self.hud_elements['game_state']['text'] = state_text
        
        # Update camera info
        cam_x, cam_y = game_data['camera_x'], game_data['camera_y']
        zoom = game_data['camera_zoom']
        self.hud_elements['camera_info']['text'] = f"Camera: ({cam_x:.0f}, {cam_y:.0f}) Zoom: {zoom:.1f}x"
        
        # Update construction mode
        construction_text = self.get_construction_text()
        self.hud_elements['construction']['text'] = construction_text
        
    def get_state_text(self, game_data):
        """Get appropriate text for current game state"""
        state = game_data['state']
        paused = game_data['paused']
        
        if state == "menu":
            return "Press SPACE to start | ESC to quit"
        elif state == "playing":
            if paused:
                return "PAUSED - Press P to resume"
            else:
                wave = game_data['wave_number']
                score = game_data['score']
                return f"Wave {wave} | Score: {score} | P to pause"
        elif state == "game_over":
            return "GAME OVER - Press SPACE to restart"
        else:
            return f"State: {state}"
            
    def get_construction_text(self):
        """Get text for construction mode"""
        input_system = self.game_engine.input_system
        
        if input_system.construction_mode and input_system.selected_building_type:
            cost = self.game_engine.get_building_cost(input_system.selected_building_type)
            minerals_cost = cost.get('minerals', 0)
            energy_cost = cost.get('energy', 0)
            
            can_afford = self.game_engine.can_afford_building(input_system.selected_building_type)
            afford_text = "✓" if can_afford else "✗"
            
            return f"Building: {input_system.selected_building_type.title()} | Cost: {minerals_cost}M {energy_cost}E {afford_text} | Left-click to place, Right-click to cancel"
        else:
            return ""
            
    def show_message(self, message, duration=3.0, color=(1, 1, 1, 1)):
        """Show a temporary message"""
        # For Phase 2, just update the game state text
        # Phase 3 can implement proper temporary messages
        self.hud_elements['game_state']['text'] = message
        
    def hide_hud(self):
        """Hide all HUD elements"""
        for element in self.hud_elements.values():
            element.hide()
            
    def show_hud(self):
        """Show all HUD elements"""
        for element in self.hud_elements.values():
            element.show()
            
    def toggle_hud(self):
        """Toggle HUD visibility"""
        # Check if first element is hidden to determine current state
        if self.hud_elements['minerals'].isHidden():
            self.show_hud()
            print("HUD shown")
        else:
            self.hide_hud()
            print("HUD hidden")
            
    def cleanup(self):
        """Clean up HUD elements"""
        print("Cleaning up HUD...")
        
        for name, element in self.hud_elements.items():
            element.destroy()
            
        self.hud_elements.clear()
        
        print("✓ HUD cleanup complete") 