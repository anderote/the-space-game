"""
Panda3D Input System - Phase 2 Implementation
Handles camera movement, mouse interaction, and building placement
"""

from direct.showbase.DirectObject import DirectObject

class Panda3DInputSystem(DirectObject):
    """Handles input events, camera controls, and mouse interaction"""
    
    def __init__(self, base, game_engine):
        DirectObject.__init__(self)
        self.base = base
        self.game_engine = game_engine
        
        # Input state
        self.keys_pressed = set()
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Building placement state (for Phase 3)
        self.selected_building_type = None
        self.construction_mode = False
        self.valid_placement = False
        
        self.setup_input()
        
    def setup_input(self):
        """Set up input event handlers"""
        print("Setting up enhanced input system...")
        
        # Basic control keys
        self.accept('escape', self.quit_game)
        self.accept('space', self.toggle_game_state)
        self.accept('p', self.pause_game)
        
        # Camera movement keys (WASD)
        self.accept('w', self.on_key_press, ['w'])
        self.accept('w-up', self.on_key_release, ['w'])
        self.accept('a', self.on_key_press, ['a'])
        self.accept('a-up', self.on_key_release, ['a'])
        self.accept('s', self.on_key_press, ['s'])
        self.accept('s-up', self.on_key_release, ['s'])
        self.accept('d', self.on_key_press, ['d'])
        self.accept('d-up', self.on_key_release, ['d'])
        
        # Arrow keys for camera movement (alternative)
        self.accept('arrow_up', self.on_key_press, ['up'])
        self.accept('arrow_up-up', self.on_key_release, ['up'])
        self.accept('arrow_down', self.on_key_press, ['down'])
        self.accept('arrow_down-up', self.on_key_release, ['down'])
        self.accept('arrow_left', self.on_key_press, ['left'])
        self.accept('arrow_left-up', self.on_key_release, ['left'])
        self.accept('arrow_right', self.on_key_press, ['right'])
        self.accept('arrow_right-up', self.on_key_release, ['right'])
        
        # Zoom controls
        self.accept('wheel_up', self.zoom_in)
        self.accept('wheel_down', self.zoom_out)
        self.accept('=', self.zoom_in)  # Plus key
        self.accept('-', self.zoom_out)  # Minus key
        self.accept('r', self.reset_zoom)  # Reset zoom
        
        # Mouse controls
        self.accept('mouse1', self.on_mouse_click, ['left'])
        self.accept('mouse3', self.on_mouse_click, ['right'])
        
        # Center camera on base
        self.accept('c', self.center_on_base)
        
        # HUD toggle
        self.accept('tab', self.toggle_hud)
        
        # Building hotkeys (for Phase 3, but we'll set them up now)
        building_hotkeys = {
            'q': 'solar',           # Solar panel
            'e': 'connector',       # Power connector  
            'b': 'battery',         # Battery
            'm': 'miner',           # Miner
            't': 'turret',          # Turret
            'l': 'laser',           # Laser turret
            'y': 'repair',          # Repair node
            'h': 'hangar',          # Hangar
            'f': 'force_field',     # Force field
            'x': 'superlaser',      # Super laser
            'z': 'missile_launcher', # Missile launcher
            'v': 'converter'        # Converter
        }
        
        for key, building_type in building_hotkeys.items():
            self.accept(key, self.select_building_type, [building_type])
        
        # Enable mouse tracking
        if self.base.mouseWatcherNode.hasMouse():
            self.track_mouse_task = self.base.taskMgr.add(self.track_mouse, "track_mouse")
        
        print("✓ Enhanced input system setup complete")
        print("  Camera Controls:")
        print("    WASD/Arrow Keys - Pan camera")
        print("    Mouse Wheel/+/- - Zoom in/out")
        print("    R - Reset zoom")
        print("    C - Center on base")
        print("    TAB - Toggle HUD")
        print("  Building Hotkeys: Q,E,B,M,T,L,Y,H,F,X,Z,V")
        
    def update(self, dt):
        """Update input system - handle continuous input like camera movement"""
        # Handle camera movement based on pressed keys
        camera = self.game_engine.camera
        
        # Calculate movement direction
        dx = 0
        dy = 0
        
        # WASD movement
        if 'w' in self.keys_pressed or 'up' in self.keys_pressed:
            dy += 1  # Move up
        if 's' in self.keys_pressed or 'down' in self.keys_pressed:
            dy -= 1  # Move down
        if 'a' in self.keys_pressed or 'left' in self.keys_pressed:
            dx -= 1  # Move left
        if 'd' in self.keys_pressed or 'right' in self.keys_pressed:
            dx += 1  # Move right
        
        # Apply camera movement if any keys are pressed
        if dx != 0 or dy != 0:
            camera.move_camera(dx, dy, dt)
        
        # Update mouse world position for building placement
        if self.construction_mode:
            self.update_building_preview()
        
    def on_key_press(self, key):
        """Handle key press events"""
        self.keys_pressed.add(key)
        
    def on_key_release(self, key):
        """Handle key release events"""
        self.keys_pressed.discard(key)
        
    def on_mouse_click(self, button):
        """Handle mouse click events"""
        if not self.base.mouseWatcherNode.hasMouse():
            return
            
        # Get mouse position in screen coordinates
        mouse_x = self.base.mouseWatcherNode.getMouseX()
        mouse_y = self.base.mouseWatcherNode.getMouseY()
        
        # Convert to screen pixel coordinates
        screen_x = (mouse_x + 1) * self.game_engine.camera.screen_width / 2
        screen_y = (1 - mouse_y) * self.game_engine.camera.screen_height / 2
        
        # Convert to world coordinates
        world_x, world_y = self.game_engine.camera.screen_to_world(screen_x, screen_y)
        
        print(f"Mouse {button} click at screen: ({screen_x:.0f}, {screen_y:.0f}) world: ({world_x:.0f}, {world_y:.0f})")
        
        if button == 'left':
            self.handle_left_click(world_x, world_y)
        elif button == 'right':
            self.handle_right_click(world_x, world_y)
            
    def handle_left_click(self, world_x, world_y):
        """Handle left mouse click for building placement or selection"""
        if self.game_engine.state != "playing":
            return
            
        # Check if we're in construction mode
        construction_info = self.game_engine.get_construction_info()
        if construction_info['active']:
            # Try to place building
            success = self.game_engine.place_building_at_cursor(world_x, world_y)
            if success:
                print(f"✓ Building placed successfully")
            else:
                print(f"✗ Cannot place building at this location")
        else:
            # Try to select existing building
            selected_building = self.game_engine.select_building_at(world_x, world_y)
            if selected_building:
                print(f"✓ Selected {selected_building.building_type}")
            else:
                print(f"No building at ({world_x:.0f}, {world_y:.0f})")
            
    def handle_right_click(self, world_x, world_y):
        """Handle right mouse click for canceling actions"""
        if self.game_engine.state != "playing":
            return
            
        construction_info = self.game_engine.get_construction_info()
        if construction_info['active']:
            self.game_engine.cancel_building_construction()
        else:
            print(f"Right click at ({world_x:.0f}, {world_y:.0f})")
            
    def track_mouse(self, task):
        """Track mouse position continuously"""
        if self.base.mouseWatcherNode.hasMouse():
            self.mouse_x = self.base.mouseWatcherNode.getMouseX()
            self.mouse_y = self.base.mouseWatcherNode.getMouseY()
            
        return task.cont
        
    def zoom_in(self):
        """Handle zoom in input"""
        self.game_engine.camera.zoom_in(0.2)
        
    def zoom_out(self):
        """Handle zoom out input"""
        self.game_engine.camera.zoom_out(0.2)
        
    def reset_zoom(self):
        """Reset camera zoom to default"""
        if not self.construction_mode:  # Don't reset zoom during construction
            self.game_engine.camera.reset_zoom()
            print("Camera zoom reset")
        
    def center_on_base(self):
        """Center camera on the player's base"""
        # For Phase 3, this will center on the actual starting base
        # For now, center on world center
        world_center_x = self.game_engine.camera.world_width / 2
        world_center_y = self.game_engine.camera.world_height / 2
        self.game_engine.camera.center_on_position(world_center_x, world_center_y)
        print("Camera centered on base")
        
    def toggle_hud(self):
        """Toggle HUD visibility"""
        self.game_engine.toggle_hud()
        
    def select_building_type(self, building_type):
        """Select a building type for construction"""
        if self.game_engine.state != "playing":
            return
            
        success = self.game_engine.start_building_construction(building_type)
        if success:
            print("Move mouse to position, left-click to place, right-click to cancel")
        
    def cancel_construction(self):
        """Cancel building construction mode"""
        self.game_engine.cancel_building_construction()
        
    def update_building_preview(self):
        """Update building placement preview"""
        if not self.base.mouseWatcherNode.hasMouse():
            return
            
        # Convert mouse position to world coordinates
        screen_x = (self.mouse_x + 1) * self.game_engine.camera.screen_width / 2
        screen_y = (1 - self.mouse_y) * self.game_engine.camera.screen_height / 2
        world_x, world_y = self.game_engine.camera.screen_to_world(screen_x, screen_y)
        
        # Validate placement using building system
        construction_info = self.game_engine.get_construction_info()
        if construction_info['active']:
            can_place, reason = self.game_engine.building_system.can_place_building(
                construction_info['building_type'], world_x, world_y
            )
            self.valid_placement = can_place and construction_info['can_afford']
        
    def get_mouse_world_position(self):
        """Get current mouse position in world coordinates"""
        if not self.base.mouseWatcherNode.hasMouse():
            return None, None
            
        # Convert mouse position to world coordinates
        screen_x = (self.mouse_x + 1) * self.game_engine.camera.screen_width / 2
        screen_y = (1 - self.mouse_y) * self.game_engine.camera.screen_height / 2
        world_x, world_y = self.game_engine.camera.screen_to_world(screen_x, screen_y)
        
        return world_x, world_y
        
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
        
    def cleanup(self):
        """Clean up input system"""
        print("Cleaning up input system...")
        
        # Remove all event handlers
        self.ignoreAll()
        
        # Remove mouse tracking task
        if hasattr(self, 'track_mouse_task'):
            self.base.taskMgr.remove(self.track_mouse_task)
            
        print("✓ Enhanced input system cleanup complete") 