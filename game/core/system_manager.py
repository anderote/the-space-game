"""
Central system manager that coordinates all game systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class System(ABC):
    """Abstract base class for all game systems."""
    
    def __init__(self, name: str):
        self.name = name
        self.active = True
    
    @abstractmethod
    def initialize(self):
        """Initialize the system."""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Update the system."""
        pass
    
    def shutdown(self):
        """Shutdown the system (optional override)."""
        pass
    
    def handle_event(self, event):
        """Handle input events (optional override)."""
        pass


class SystemManager:
    """Manages all game systems and their lifecycle."""
    
    def __init__(self):
        self.systems: Dict[str, System] = {}
        self.system_order = []  # Order of system updates
        self.initialized = False
    
    def add_system(self, system: System, priority: int = 0):
        """Add a system to be managed.
        
        Args:
            system: The system to add
            priority: Update priority (lower numbers update first)
        """
        self.systems[system.name] = system
        
        # Insert system in priority order
        inserted = False
        for i, (existing_system, existing_priority) in enumerate(self.system_order):
            if priority < existing_priority:
                self.system_order.insert(i, (system, priority))
                inserted = True
                break
        
        if not inserted:
            self.system_order.append((system, priority))
    
    def get_system(self, name: str) -> System:
        """Get a system by name."""
        return self.systems.get(name)
    
    def remove_system(self, name: str):
        """Remove a system."""
        if name in self.systems:
            system = self.systems[name]
            system.shutdown()
            del self.systems[name]
            
            # Remove from order list
            self.system_order = [(s, p) for s, p in self.system_order if s.name != name]
    
    def initialize_all(self):
        """Initialize all systems."""
        if self.initialized:
            return
        
        for system, _ in self.system_order:
            try:
                system.initialize()
                print(f"Initialized system: {system.name}")
            except Exception as e:
                print(f"Failed to initialize system {system.name}: {e}")
                raise
        
        self.initialized = True
    
    def update_all(self, dt: float):
        """Update all active systems in priority order."""
        for system, _ in self.system_order:
            if system.active:
                try:
                    system.update(dt)
                except Exception as e:
                    print(f"Error updating system {system.name}: {e}")
                    # Continue with other systems
    
    def handle_event_all(self, event):
        """Send event to all systems that handle events."""
        for system, _ in self.system_order:
            if system.active and hasattr(system, 'handle_event'):
                try:
                    system.handle_event(event)
                except Exception as e:
                    print(f"Error handling event in system {system.name}: {e}")
    
    def shutdown_all(self):
        """Shutdown all systems."""
        for system, _ in reversed(self.system_order):  # Shutdown in reverse order
            try:
                system.shutdown()
                print(f"Shutdown system: {system.name}")
            except Exception as e:
                print(f"Error shutting down system {system.name}: {e}")
        
        self.systems.clear()
        self.system_order.clear()
        self.initialized = False
    
    def set_system_active(self, name: str, active: bool):
        """Enable or disable a system."""
        if name in self.systems:
            self.systems[name].active = active
    
    def get_system_status(self) -> Dict[str, bool]:
        """Get the active status of all systems."""
        return {name: system.active for name, system in self.systems.items()} 