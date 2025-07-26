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
    
    def __init__(self, window):
        self.window = window
        self.ctx = window.ctx
        
        # Core systems
        self.camera: Optional[ArcadeCamera] = None
        self.render_system: Optional[ArcadeRenderSystem] = None
        self.particle_system: Optional[ArcadeParticleSystem] = None
        self.input_system: Optional[ArcadeInputSystem] = None
        self.game_logic: Optional[ArcadeGameLogic] = None
        self.hud: Optional[ArcadeHUD] = None
        
        # Game state
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.running = True
        
        # Performance tracking
        self.frame_count = 0
        self.update_time = 0.0
        self.render_time = 0.0
        
    def setup(self):
        """Initialize all game systems."""
        print("Setting up Arcade game engine...")
        
        # Create camera
        self.camera = ArcadeCamera(self.window.width, self.window.height)
        
        # Create systems
        self.render_system = ArcadeRenderSystem(self.ctx, self.camera)
        self.particle_system = ArcadeParticleSystem(self.ctx, self.camera, self.window.particle_shader)
        self.input_system = ArcadeInputSystem(self.camera)
        self.game_logic = ArcadeGameLogic(self.camera, self.particle_system)
        self.hud = ArcadeHUD(self.window.width, self.window.height)
        
        # Setup systems
        self.render_system.setup()
        self.particle_system.setup()
        self.input_system.setup()
        self.game_logic.setup()
        self.hud.setup()
        
        print("Arcade game engine setup complete!")
        
    def update(self, delta_time: float):
        """Update all game systems."""
        import time
        start_time = time.perf_counter()
        
        # Update based on game state
        if self.game_state == "playing":
            self._update_playing(delta_time)
        elif self.game_state == "menu":
            self._update_menu(delta_time)
        elif self.game_state == "paused":
            self._update_paused(delta_time)
            
        self.update_time = time.perf_counter() - start_time
        self.frame_count += 1
        
    def _update_playing(self, delta_time: float):
        """Update game systems during gameplay."""
        # Update input
        self.input_system.update(delta_time)
        
        # Update game logic
        self.game_logic.update(delta_time)
        
        # Update particles
        self.particle_system.update(delta_time)
        
        # Update camera
        self.camera.update(delta_time)
        
    def _update_menu(self, delta_time: float):
        """Update systems during menu state."""
        self.input_system.update(delta_time)
        
    def _update_paused(self, delta_time: float):
        """Update systems during paused state."""
        self.input_system.update(delta_time)
        
    def render(self):
        """Render all game content."""
        import time
        start_time = time.perf_counter()
        
        # Clear the screen
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Render based on game state
        if self.game_state == "playing":
            self._render_playing()
        elif self.game_state == "menu":
            self._render_menu()
        elif self.game_state == "paused":
            self._render_paused()
            
        self.render_time = time.perf_counter() - start_time
        
    def _render_playing(self):
        """Render game content during gameplay."""
        # Set up camera view
        self.camera.apply()
        
        # Render background stars
        self.render_system.render_background()
        
        # Render game objects
        self.game_logic.render(self.render_system)
        
        # Render particles
        self.particle_system.render()
        
        # Reset camera for UI
        self.camera.reset()
        
        # Render UI
        self.hud.render(self.game_logic.get_game_data())
        
    def _render_menu(self):
        """Render menu content."""
        self.hud.render_menu()
        
    def _render_paused(self):
        """Render paused game with overlay."""
        # Render the game world first
        self._render_playing()
        
        # Render pause overlay
        self.hud.render_pause_overlay()
        
    def on_key_press(self, key: int, modifiers: int):
        """Handle key press events."""
        if self.input_system:
            self.input_system.on_key_press(key, modifiers)
            
        # Global key handling
        if key == arcade.key.ESCAPE:
            if self.game_state == "playing":
                self.game_state = "paused"
            elif self.game_state == "paused":
                self.game_state = "playing"
            elif self.game_state == "menu":
                self.running = False
                
    def on_key_release(self, key: int, modifiers: int):
        """Handle key release events."""
        if self.input_system:
            self.input_system.on_key_release(key, modifiers)
            
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse press events."""
        if self.input_system:
            self.input_system.on_mouse_press(x, y, button, modifiers)
            
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse release events."""
        if self.input_system:
            self.input_system.on_mouse_release(x, y, button, modifiers)
            
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Handle mouse motion events."""
        if self.input_system:
            self.input_system.on_mouse_motion(x, y, dx, dy)
            
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """Handle mouse scroll events."""
        if self.input_system:
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