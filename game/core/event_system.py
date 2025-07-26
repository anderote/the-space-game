"""
Centralized event system for handling input and game events.
"""

import pygame
from enum import Enum
from typing import Dict, List, Callable, Any
from dataclasses import dataclass


class EventType(Enum):
    """Custom game event types."""
    BUILDING_PLACED = "building_placed"
    BUILDING_DESTROYED = "building_destroyed"
    ENEMY_KILLED = "enemy_killed"
    WAVE_STARTED = "wave_started"
    WAVE_COMPLETED = "wave_completed"
    RESOURCE_CHANGED = "resource_changed"
    POWER_GRID_UPDATED = "power_grid_updated"
    GAME_OVER = "game_over"
    GAME_STATE_CHANGE = "game_state_change"
    UI_ACTION = "ui_action"


@dataclass
class GameEvent:
    """Custom game event."""
    event_type: EventType
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class EventSystem:
    """Centralized event handling system."""
    
    def __init__(self):
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.input_handlers: List[Callable] = []
        self.event_queue: List[GameEvent] = []
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to a game event type.
        
        Args:
            event_type: The type of event to listen for
            handler: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from a game event type."""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
    
    def subscribe_input(self, handler: Callable):
        """Subscribe to raw pygame input events."""
        self.input_handlers.append(handler)
    
    def unsubscribe_input(self, handler: Callable):
        """Unsubscribe from raw pygame input events."""
        if handler in self.input_handlers:
            self.input_handlers.remove(handler)
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None):
        """Emit a game event.
        
        Args:
            event_type: Type of event to emit
            data: Optional event data
        """
        event = GameEvent(event_type, data)
        self.event_queue.append(event)
    
    def process_pygame_events(self):
        """Process pygame events and distribute to handlers."""
        events = pygame.event.get()
        
        for event in events:
            # Send to input handlers
            for handler in self.input_handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in input handler: {e}")
        
        return events
    
    def process_game_events(self):
        """Process queued game events."""
        while self.event_queue:
            event = self.event_queue.pop(0)
            
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        print(f"Error in event handler for {event.event_type}: {e}")
    
    def clear_handlers(self):
        """Clear all event handlers."""
        self.event_handlers.clear()
        self.input_handlers.clear()
    
    def clear_queue(self):
        """Clear the event queue."""
        self.event_queue.clear()


# Global event system instance
event_system = EventSystem() 