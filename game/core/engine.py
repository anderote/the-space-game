"""
Main game engine that orchestrates all systems and manages the game loop.
"""

import pygame
import sys
from game.core.system_manager import SystemManager
from game.core.state_manager import (
    StateManager, GameStateType, MenuState, PlayingState, 
    PausedState, GameOverState
)
from game.core.event_system import event_system
from game.systems.render_system import RenderSystem
from game.systems.ui_system import UISystem
from game.systems.input_system import InputSystem
from game.systems.game_logic_system import GameLogicSystem
from game.systems.audio_system import AudioSystem
from game.systems.particle_system import ParticleSystem
from game.utils.camera import Camera
from settings import *


class GameEngine:
    """Main game engine that manages all systems and the game loop."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Game Clone - Refactored")
        self.clock = pygame.time.Clock()
        
        # Initialize core systems
        self.camera = Camera()
        self.system_manager = SystemManager()
        self.state_manager = StateManager()
        
        # Initialize game systems
        self.render_system = None
        self.ui_system = None
        self.input_system = None
        self.game_logic_system = None
        self.audio_system = None
        self.particle_system = None
        
        # Game state
        self.running = True
        self.high_score = 0
    
    def initialize(self):
        """Initialize the game engine and all systems."""
        print("Initializing Space Game Clone...")
        
        # Create and add systems in priority order
        # Audio and particles first (lowest priority - updated last)
        self.audio_system = AudioSystem()
        self.particle_system = ParticleSystem()
        
        self.game_logic_system = GameLogicSystem(self.camera, self.audio_system, self.particle_system)
        self.system_manager.add_system(self.game_logic_system, priority=5)
        
        self.input_system = InputSystem(self.camera)
        self.system_manager.add_system(self.input_system, priority=10)
        
        self.render_system = RenderSystem(self.screen, self.camera)
        self.system_manager.add_system(self.render_system, priority=30)
        
        self.ui_system = UISystem(self.render_system)
        self.system_manager.add_system(self.ui_system, priority=40)
        
        # Initialize all systems
        self.system_manager.initialize_all()
        
        # Create and setup game states
        self._setup_states()
        
        # Start with menu state
        self.state_manager.change_state(GameStateType.MENU)
        
        print("Game engine initialized successfully!")
    
    def _setup_states(self):
        """Setup all game states."""
        # Create game systems dict for playing state
        game_systems = {
            'game_logic': self.game_logic_system,
            'render': self.render_system,
            'ui': self.ui_system,
            'input': self.input_system,
            'audio': self.audio_system
        }
        
        # Create states
        menu_state = MenuState(self.state_manager)
        playing_state = PlayingState(self.state_manager, game_systems)
        paused_state = PausedState(self.state_manager)
        game_over_state = GameOverState(self.state_manager)
        
        # Add states to manager
        self.state_manager.add_state(GameStateType.MENU, menu_state)
        self.state_manager.add_state(GameStateType.PLAYING, playing_state)
        self.state_manager.add_state(GameStateType.PAUSED, paused_state)
        self.state_manager.add_state(GameStateType.GAME_OVER, game_over_state)
    
    def run(self):
        """Main game loop."""
        print("Starting game loop...")
        
        while self.running and self.state_manager.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Process events
            self._handle_events()
            
            # Update current state
            self.state_manager.update(dt)
            
            # Update particle system
            self.particle_system.update()
            
            # Update systems
            self.system_manager.update_all(dt)
            
            # Process game events
            event_system.process_game_events()
            
            # Render
            self._render()
        
        self._shutdown()
    
    def _handle_events(self):
        """Handle pygame events."""
        pygame_events = event_system.process_pygame_events()
        
        for event in pygame_events:
            if event.type == pygame.QUIT:
                self.running = False
            else:
                # Let state manager handle the event
                if not self.state_manager.handle_event(event):
                    self.running = False
    
    def _render(self):
        """Render the current frame."""
        current_state = self.state_manager.current_state
        
        if not current_state:
            return
        
        # Clear screen
        self.render_system.clear_screen()
        
        # Render based on current state
        if isinstance(current_state, MenuState):
            self.ui_system.draw_menu()
        
        elif isinstance(current_state, PlayingState):
            # Draw game world
            self.render_system.draw_background_stars()
            
            # Draw all game objects
            self.game_logic_system.draw_world_objects(self.render_system)
            
            # Draw particles
            self.particle_system.draw(self.render_system.screen, 
                                    self.render_system.camera.x, 
                                    self.render_system.camera.y, 
                                    self.render_system.camera.zoom)
            
            # Draw UI overlay
            energy_ratio = self.game_logic_system.resources.energy / self.game_logic_system.resources.max_energy
            self.ui_system.draw_hud(
                self.game_logic_system.resources,
                self.game_logic_system.wave_manager,
                self.game_logic_system.score,
                self.game_logic_system.kill_count,
                self.game_logic_system.selected_building,
                energy_ratio,
                self.game_logic_system.current_energy_production,
                self.game_logic_system.solar_panel_count,
                self.game_logic_system.solar_panel_levels,
                self.game_logic_system.research_system
            )
            self.ui_system.draw_building_panel(
                self.game_logic_system.selected_build,
                self.game_logic_system.resources
            )
        
        elif isinstance(current_state, PausedState):
            # Draw game world (frozen)
            self.render_system.draw_background_stars()
            self.game_logic_system.draw_world_objects(self.render_system)
            
            # Draw UI overlay
            energy_ratio = self.game_logic_system.resources.energy / self.game_logic_system.resources.max_energy
            self.ui_system.draw_hud(
                self.game_logic_system.resources,
                self.game_logic_system.wave_manager,
                self.game_logic_system.score,
                self.game_logic_system.kill_count,
                self.game_logic_system.selected_building,
                energy_ratio,
                self.game_logic_system.current_energy_production,
                self.game_logic_system.solar_panel_count,
                self.game_logic_system.solar_panel_levels
            )
            self.ui_system.draw_building_panel(
                self.game_logic_system.selected_build,
                self.game_logic_system.resources
            )
            
            # Draw pause overlay
            self.ui_system.draw_pause_overlay()
        
        elif isinstance(current_state, GameOverState):
            self.ui_system.draw_game_over(current_state.final_score, self.high_score)
        
        # Present the frame
        self.render_system.present()
    
    def _shutdown(self):
        """Cleanup and shutdown."""
        print("Shutting down game engine...")
        
        # Shutdown systems
        self.system_manager.shutdown_all()
        
        # Shutdown audio system
        if self.audio_system:
            self.audio_system.shutdown()
        
        # Clear event system
        event_system.clear_handlers()
        event_system.clear_queue()
        
        # Quit pygame
        pygame.quit()
        
        print("Game engine shutdown complete!")
    
    def get_system(self, name):
        """Get a system by name."""
        return self.system_manager.get_system(name) 