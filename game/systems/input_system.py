"""
Input system for handling keyboard and mouse input.
"""

import pygame
from game.core.system_manager import System
from game.core.event_system import EventType, event_system
from settings import *


class InputSystem(System):
    """System responsible for handling input events."""
    
    def __init__(self, camera):
        super().__init__("InputSystem")
        self.camera = camera
        self.keys = pygame.key.get_pressed()
        
        # Building selection
        self.build_keys = {
            pygame.K_s: 'solar',
            pygame.K_c: 'connector',
            pygame.K_b: 'battery',
            pygame.K_m: 'miner',
            pygame.K_t: 'turret',
            pygame.K_l: 'laser',
            pygame.K_k: 'superlaser',
            pygame.K_r: 'repair',
            pygame.K_v: 'converter',
            pygame.K_h: 'hangar',
            pygame.K_g: 'missile_launcher',
            pygame.K_f: 'force_field'
        }
        
        self.selected_build = None
        self.selected_building = None
    
    def initialize(self):
        """Initialize the input system."""
        # Subscribe to pygame events through event system
        event_system.subscribe_input(self._handle_pygame_event)
        # Subscribe to building events to track selections
        event_system.subscribe(EventType.BUILDING_PLACED, self._handle_building_event)
    
    def update(self, dt):
        """Update input state."""
        # Update key states
        self.keys = pygame.key.get_pressed()
        
        # Update camera based on arrow keys
        self.camera.update(self.keys)
    
    def _handle_pygame_event(self, event):
        """Handle raw pygame events."""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.button, event.pos)
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mouse_wheel(event.y)
    
    def _handle_keydown(self, key):
        """Handle keyboard input."""
        from game.core.event_system import event_system, EventType
        
        # Building selection
        if key in self.build_keys:
            build_type = self.build_keys[key]
            self.selected_build = build_type
            event_system.emit(EventType.BUILDING_PLACED, {'type': 'select', 'building_type': build_type})
        
        # Upgrade building
        elif key == pygame.K_u:
            if self.selected_building:
                event_system.emit(EventType.BUILDING_PLACED, {'type': 'upgrade', 'building': self.selected_building})
        
        # Sell building
        elif key == pygame.K_x:
            if self.selected_building:
                event_system.emit(EventType.BUILDING_PLACED, {'type': 'sell', 'building': self.selected_building})
        
        # Toggle building disabled state
        elif key == pygame.K_d:
            if self.selected_building and hasattr(self.selected_building, 'disabled'):
                event_system.emit(EventType.BUILDING_PLACED, {'type': 'toggle_disabled', 'building': self.selected_building})
        
        # Game speed controls
        elif key == pygame.K_1:
            event_system.emit(EventType.GAME_STATE_CHANGE, {'type': 'speed', 'value': 0.5})
        elif key == pygame.K_2:
            event_system.emit(EventType.GAME_STATE_CHANGE, {'type': 'speed', 'value': 1.0})
        elif key == pygame.K_3:
            event_system.emit(EventType.GAME_STATE_CHANGE, {'type': 'speed', 'value': 2.0})
        elif key == pygame.K_4:
            event_system.emit(EventType.GAME_STATE_CHANGE, {'type': 'speed', 'value': 3.0})
        elif key == pygame.K_SPACE:
            event_system.emit(EventType.GAME_STATE_CHANGE, {'type': 'toggle_pause'})
        
        # ESC key functionality - cancel building selection only
        elif key == pygame.K_ESCAPE:
            if self.selected_build:
                # Cancel building placement mode
                self.selected_build = None
                # Notify game logic system to cancel building selection
                event_system.emit(EventType.BUILDING_PLACED, {'type': 'cancel_selection'})
                print("🚫 Cancelled building selection")
            # No longer toggles menu - ESC only cancels building selection
        
        # Wave control
        elif key == pygame.K_n:
            event_system.emit(EventType.BUILDING_PLACED, {'type': 'skip_wave'})
            print("⏭ Skipping to next wave...")
        
        # Menu and quit controls
        # 'O' key now handled by UI system for popup menu
        elif key == pygame.K_p:
            event_system.emit(EventType.GAME_STATE_CHANGE, {'type': 'quit'})
    
    def _handle_mouse_click(self, button, pos):
        """Handle mouse clicks."""
        if button == 1:  # Left click
            # Check for research panel clicks first (right side of screen)
            if pos[0] >= SCREEN_WIDTH - 200:  # Research panel area
                self._handle_research_click(pos)
                return
            
            # Check for building panel clicks (middle-right of screen)
            elif pos[0] >= SCREEN_WIDTH - 380 and pos[0] < SCREEN_WIDTH - 200:  # Building panel area
                # Building panel click handling would go here
                pass
            
            # World interaction
            else:
                world_x, world_y = self.camera.screen_to_world(pos[0], pos[1])
                
                if self.selected_build:
                    # Place building
                    event_system.emit(EventType.BUILDING_PLACED, {
                        'type': 'place',
                        'building_type': self.selected_build,
                        'x': world_x,
                        'y': world_y
                    })
                else:
                    # Select building
                    event_system.emit(EventType.BUILDING_PLACED, {
                        'type': 'select_at',
                        'x': world_x,
                        'y': world_y
                    })
                    # Store selected building reference in input system for hotkey usage
                    # This will be updated by the game logic system after selection
        
        elif button == 3:  # Right click
            # Cancel building placement or deselect
            if self.selected_build:
                self.selected_build = None
            else:
                self.selected_building = None
    
    def _handle_research_click(self, pos):
        """Handle clicks in the research panel."""
        # Calculate which research button was clicked
        panel_x = SCREEN_WIDTH - 200
        start_y = 60
        button_height = 60
        button_margin = 5
        
        # Check if click is in research area
        if pos[0] < panel_x + 10 or pos[0] > SCREEN_WIDTH - 10:
            return
        
        # Skip header area
        if pos[1] < start_y + 25:
            return
        
        # Calculate button index based on Y position
        relative_y = pos[1] - (start_y + 25)  # Account for header
        button_index = relative_y // (button_height + button_margin)
        
        # Emit research event - the game logic system will handle validation
        event_system.emit(EventType.BUILDING_PLACED, {
            'type': 'research_click',
            'button_index': button_index,
            'pos': pos
        })
    
    def _handle_mouse_wheel(self, y):
        """Handle mouse wheel for zooming."""
        if y > 0:
            self.camera.zoom_in()
        elif y < 0:
            self.camera.zoom_out()
    
    def get_mouse_world_pos(self):
        """Get current mouse position in world coordinates."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.camera.screen_to_world(mouse_x, mouse_y)
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed."""
        return self.keys[key]
    
    def _handle_building_event(self, event):
        """Handle building events to track selections."""
        data = event.data
        if data['type'] == 'selection_changed':
            self.selected_building = data['building'] 