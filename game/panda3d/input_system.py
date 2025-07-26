"""
Panda3D Input System - Phase 1 Basic Implementation
Handles user input and key bindings for the game
"""

from direct.showbase.DirectObject import DirectObject

class Panda3DInputSystem(DirectObject):
    """Handles input events and key bindings"""
    
    def __init__(self, base, game_engine):
        DirectObject.__init__(self)
        self.base = base
        self.game_engine = game_engine
        
        # Input state
        self.keys_pressed = set()
        self.mouse_x = 0
        self.mouse_y = 0
        
        self.setup_input()
        
    def setup_input(self):
        """Set up input event handlers"""
        print("Setting up input system...")
        
        # Basic control keys for Phase 1
        self.accept('escape', self.quit_game)
        self.accept('space', self.toggle_game_state)
        self.accept('p', self.pause_game)
        
        # Key press/release tracking (for Phase 2 camera movement)
        self.accept('w', self.on_key_press, ['w'])
        self.accept('w-up', self.on_key_release, ['w'])
        self.accept('a', self.on_key_press, ['a'])
        self.accept('a-up', self.on_key_release, ['a'])
        self.accept('s', self.on_key_press, ['s'])
        self.accept('s-up', self.on_key_release, ['s'])
        self.accept('d', self.on_key_press, ['d'])
        self.accept('d-up', self.on_key_release, ['d'])
        
        # Mouse tracking (for Phase 2 building placement)
        self.accept('mouse1', self.on_mouse_click, ['left'])
        self.accept('mouse3', self.on_mouse_click, ['right'])
        
        # Enable mouse tracking
        if self.base.mouseWatcherNode.hasMouse():
            self.track_mouse_task = self.base.taskMgr.add(self.track_mouse, "track_mouse")
        
        print("✓ Input system setup complete")
        print("  Controls:")
        print("    ESC - Quit game")
        print("    SPACE - Start/Toggle game")
        print("    P - Pause/Resume")
        print("    WASD - Camera movement (Phase 2+)")
        
    def update(self, dt):
        """Update input system"""
        # In Phase 2, this will handle continuous input like camera movement
        # For Phase 1, just track basic state
        pass
        
    def on_key_press(self, key):
        """Handle key press events"""
        self.keys_pressed.add(key)
        # print(f"Key pressed: {key}")  # Debug output
        
    def on_key_release(self, key):
        """Handle key release events"""
        self.keys_pressed.discard(key)
        # print(f"Key released: {key}")  # Debug output
        
    def on_mouse_click(self, button):
        """Handle mouse click events"""
        if self.base.mouseWatcherNode.hasMouse():
            mouse_x = self.base.mouseWatcherNode.getMouseX()
            mouse_y = self.base.mouseWatcherNode.getMouseY()
            print(f"Mouse {button} click at: ({mouse_x:.2f}, {mouse_y:.2f})")
            
            # In Phase 2, this will handle building placement
            # For Phase 1, just log the click
            
    def track_mouse(self, task):
        """Track mouse position continuously"""
        if self.base.mouseWatcherNode.hasMouse():
            self.mouse_x = self.base.mouseWatcherNode.getMouseX()
            self.mouse_y = self.base.mouseWatcherNode.getMouseY()
            
        return task.cont
        
    def quit_game(self):
        """Quit the application"""
        print("Quit requested by user")
        self.base.userExit()
        
    def toggle_game_state(self):
        """Toggle between menu and playing state"""
        current_state = self.game_engine.state
        
        if current_state == "menu":
            print("Starting game...")
            self.game_engine.start_game()
        elif current_state == "playing":
            print("Returning to menu...")
            self.game_engine.state = "menu"
        elif current_state == "game_over":
            print("Restarting game...")
            self.game_engine.start_game()
        else:
            print(f"Current state: {current_state}")
            
    def pause_game(self):
        """Pause/resume the game"""
        self.game_engine.pause_game()
        
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        return key in self.keys_pressed
        
    def get_mouse_world_position(self):
        """Get mouse position in world coordinates (for Phase 2+)"""
        # Convert screen mouse coordinates to world coordinates
        # Will be implemented properly in Phase 2 with camera transforms
        return self.mouse_x * 100, self.mouse_y * 100
        
    def cleanup(self):
        """Clean up input system"""
        print("Cleaning up input system...")
        
        # Remove all event handlers
        self.ignoreAll()
        
        # Remove mouse tracking task
        if hasattr(self, 'track_mouse_task'):
            self.base.taskMgr.remove(self.track_mouse_task)
            
        print("✓ Input system cleanup complete") 