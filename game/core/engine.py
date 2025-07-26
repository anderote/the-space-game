"""
Arcade game engine that manages all game systems and logic.
"""

import arcade
import arcade.gl as gl
from typing import Optional, List, Dict
from .camera import ArcadeCamera
from ..systems.render_system import ArcadeRenderSystem
from ..systems.particle_system import ArcadeParticleSystem
from ..systems.input_system import ArcadeInputSystem
from ..systems.game_logic import ArcadeGameLogic
from ..ui.hud import ArcadeHUD


class ArcadeGameEngine:
    """Main game engine for Arcade implementation."""
    
    def __init__(self, ctx, width: int, height: int):
        """Initialize the game engine with Arcade systems."""
        self.ctx = ctx
        self.state = "menu"
        
        # Initialize camera centered on world center where starting base will be
        self.camera = ArcadeCamera(width, height)
        self.camera.world_width = 4800
        self.camera.world_height = 2700
        self.camera.x = 2400  # Center of world width
        self.camera.y = 1350  # Center of world height
        self.camera.zoom = 1.0
        
        # Initialize all systems with context
        self.render_system = ArcadeRenderSystem(ctx, width, height)
        self.particle_system = ArcadeParticleSystem(ctx, self.camera)
        self.game_logic = ArcadeGameLogic(self.camera)
        self.input_system = ArcadeInputSystem(self.camera, self.game_logic)
        self.hud = ArcadeHUD(width, height)
        
        # Game state
        self.delta_time = 0.0
        
    def setup(self):
        """Setup all systems."""
        print("Setting up Arcade game engine...")
        self.render_system.setup()
        self.particle_system.setup()
        self.input_system.setup()
        self.game_logic.setup()
        self.hud.setup()
        print("Arcade game engine setup complete!")
    
    def update(self, dt: float):
        """Update the game engine based on current state."""
        self.delta_time = dt
        
        # Update camera
        self.camera.update(dt)
        
        # Update input system
        self.input_system.update(dt)
        
        # Update based on state
        if self.state == "playing":
            self.game_logic.update(dt)
            self.particle_system.update(dt)
        elif self.state == "menu":
            pass  # Menu doesn't need game logic updates
        elif self.state == "paused":
            pass  # Paused state doesn't update game logic
    
    def render(self):
        """Render the current game state."""
        if self.state == "menu":
            self._render_menu()
        elif self.state == "playing":
            self._render_playing()
        elif self.state == "paused":
            self._render_playing()  # Still show the game
            self._render_pause_overlay()
    
    def _render_menu(self):
        """Render the main menu."""
        self.hud.render_menu()
    
    def _render_playing(self):
        """Render the playing state."""
        # Apply camera transformation for world rendering
        self.camera.apply()
        
        # Render background with camera
        self.render_system.render_background(self.camera)
        
        # Render game entities (these are in world space)
        self.game_logic.render(self.camera)
        
        # Render particles
        self.particle_system.render(self.camera)
        
        # Render construction preview (in world space)
        self.input_system.draw_construction_preview(self.camera)
        
        # Reset camera transformation for UI rendering
        self.camera.reset()
        
        # Render HUD (in screen space)
        game_data = self.game_logic.get_game_data()
        game_data['camera_zoom'] = self.camera.zoom
        self.hud.render("playing", game_data)
    
    def _render_paused(self):
        """Render the paused state."""
        # Render the game state first
        self._render_playing()
        
        # Then render pause overlay
        self.hud.render_pause_overlay()
    
    def _render_pause_overlay(self):
        """Render pause overlay on top of the game."""
        self.hud.render_pause_overlay()
    
    def on_key_press(self, key: int, modifiers: int):
        """Handle key press events."""
        if self.state == "menu":
            if key == arcade.key.SPACE:
                self.state = "playing"
        elif self.state == "playing":
            if key == arcade.key.ESCAPE:
                self.state = "paused"
            else:
                self.input_system.on_key_press(key, modifiers)
        elif self.state == "paused":
            if key == arcade.key.ESCAPE:
                self.state = "playing"
            elif key == arcade.key.Q:
                arcade.close_window()
    
    def on_key_release(self, key: int, modifiers: int):
        """Handle key release events."""
        if self.state == "playing":
            self.input_system.on_key_release(key, modifiers)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Handle mouse motion."""
        if self.state == "playing":
            self.input_system.on_mouse_motion(x, y, dx, dy)
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse press."""
        if self.state == "playing":
            self.input_system.on_mouse_press(x, y, button, modifiers)
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse release."""
        if self.state == "playing":
            self.input_system.on_mouse_release(x, y, button, modifiers)
    
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """Handle mouse scroll."""
        if self.state == "playing":
            self.input_system.on_mouse_scroll(x, y, scroll_x, scroll_y)
            
    def on_resize(self, width: int, height: int):
        """Handle window resize events."""
        if self.camera:
            self.camera.resize(width, height)
        if self.hud:
            self.hud.resize(width, height)
        if self.render_system:
            self.render_system.resize(width, height)
            
    def change_game_state(self, new_state: str):
        """Change the current game state."""
        old_state = self.game_state
        self.game_state = new_state
        
        # Handle state transitions
        if new_state == "playing" and old_state == "menu":
            self.game_logic.start_new_game()
        elif new_state == "menu" and old_state == "playing":
            self.game_logic.reset_game()
            
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        return {
            "fps": 1.0 / (self.update_time + self.render_time) if (self.update_time + self.render_time) > 0 else 0,
            "update_time": self.update_time * 1000,  # Convert to milliseconds
            "render_time": self.render_time * 1000,
            "frame_count": self.frame_count
        } 