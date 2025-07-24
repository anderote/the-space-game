"""
Game state management system.
Handles transitions between different game states (menu, playing, paused, etc.)
"""

from enum import Enum
from abc import ABC, abstractmethod
import pygame


class GameStateType(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameState(ABC):
    """Abstract base class for game states."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.active = False
    
    @abstractmethod
    def enter(self):
        """Called when entering this state."""
        self.active = True
    
    @abstractmethod
    def exit(self):
        """Called when exiting this state."""
        self.active = False
    
    @abstractmethod
    def update(self, dt):
        """Update the state logic."""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """Handle input events."""
        pass
    
    @abstractmethod
    def render(self, surface):
        """Render the state."""
        pass


class MenuState(GameState):
    """Main menu state."""
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.show_menu = True
    
    def enter(self):
        super().enter()
        self.show_menu = True
    
    def exit(self):
        super().exit()
        self.show_menu = False
    
    def update(self, dt):
        pass
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Start new game
                self.state_manager.change_state(GameStateType.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit game
        return True
    
    def render(self, surface):
        # Menu rendering will be handled by UI system
        pass


class PlayingState(GameState):
    """Main gameplay state."""
    
    def __init__(self, state_manager, game_systems):
        super().__init__(state_manager)
        self.game_systems = game_systems
        self.game_speed = 1.0
    
    def enter(self):
        super().enter()
        # Reset game when entering playing state
        if 'game_logic' in self.game_systems:
            self.game_systems['game_logic'].reset_game()
    
    def exit(self):
        super().exit()
    
    def update(self, dt):
        if self.game_speed > 0:
            # Apply game speed multiplier
            scaled_dt = dt * self.game_speed
            
            # Update all game systems
            for system in self.game_systems.values():
                if hasattr(system, 'update'):
                    system.update(scaled_dt)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.state_manager.change_state(GameStateType.PAUSED)
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameStateType.MENU)
            elif event.key == pygame.K_1:
                self.game_speed = 0.0  # Pause
            elif event.key == pygame.K_2:
                self.game_speed = 1.0  # Normal
            elif event.key == pygame.K_3:
                self.game_speed = 2.0  # 2x speed
            elif event.key == pygame.K_4:
                self.game_speed = 3.0  # 3x speed
        
        # Forward events to game systems
        for system in self.game_systems.values():
            if hasattr(system, 'handle_event'):
                system.handle_event(event)
        
        return True
    
    def render(self, surface):
        # Rendering handled by render system
        pass


class PausedState(GameState):
    """Paused game state."""
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
    
    def enter(self):
        super().enter()
    
    def exit(self):
        super().exit()
    
    def update(self, dt):
        # No updates while paused
        pass
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.state_manager.change_state(GameStateType.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameStateType.MENU)
        return True
    
    def render(self, surface):
        # Pause overlay rendering handled by UI system
        pass


class GameOverState(GameState):
    """Game over state."""
    
    def __init__(self, state_manager, final_score=0, high_score=0):
        super().__init__(state_manager)
        self.final_score = final_score
        self.high_score = high_score
    
    def enter(self):
        super().enter()
    
    def exit(self):
        super().exit()
    
    def update(self, dt):
        pass
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.state_manager.change_state(GameStateType.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameStateType.MENU)
        return True
    
    def render(self, surface):
        # Game over screen rendering handled by UI system
        pass


class StateManager:
    """Manages game state transitions."""
    
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.running = True
    
    def add_state(self, state_type, state):
        """Add a state to the manager."""
        self.states[state_type] = state
    
    def change_state(self, state_type):
        """Change to a different state."""
        if self.current_state:
            self.current_state.exit()
        
        self.current_state = self.states.get(state_type)
        if self.current_state:
            self.current_state.enter()
    
    def update(self, dt):
        """Update the current state."""
        if self.current_state and self.current_state.active:
            self.current_state.update(dt)
    
    def handle_event(self, event):
        """Handle events in the current state."""
        if self.current_state and self.current_state.active:
            return self.current_state.handle_event(event)
        return True
    
    def render(self, surface):
        """Render the current state."""
        if self.current_state and self.current_state.active:
            self.current_state.render(surface)
    
    def quit(self):
        """Signal that the game should quit."""
        self.running = False 