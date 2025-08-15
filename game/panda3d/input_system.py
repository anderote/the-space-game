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
        self.valid_placement = False
        
        self.setup_input()
        
    def setup_input(self):
        """Set up input event handlers"""
        print("Setting up enhanced input system...")
        
        # Basic control keys - '=' for quit, ESC for cancel
        self.accept('equal', self.quit_game)  # '=' key to quit game
        self.accept('space', self.toggle_game_state)
        self.accept('p', self.pause_game)
        
        # ESC key - Cancel modes (construction/selection)
        self.accept("escape", self.cancel_current_mode)
        
        # Building interaction shortcuts (when building is selected)
        self.accept("delete", self.recycle_selected_building)  # DELETE key for recycle
        self.accept("backspace", self.recycle_selected_building)  # BACKSPACE as alternative
        self.accept("g", self.toggle_disable_selected_building)  # G key for disable
        self.accept("u", self.upgrade_selected_building)        # U key for upgrade
        
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
            'k': 'superlaser',      # Super laser (changed from X to avoid conflict)
            'j': 'missile_launcher', # Missile launcher (changed from Z to avoid conflict)
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
        print("  Building Hotkeys: Q,E,B,M,T,L,Y,H,F,K,J,V")
        print("  Building Management: U=Upgrade, G=Disable, DELETE=Recycle")
        
    def update(self, dt):
        """Update input system - handle continuous input like camera movement"""
        # Handle camera movement based on pressed keys
        camera = self.game_engine.camera
        
        # Calculate movement direction
        dx = 0
        dy = 0
        
        # WASD movement - standard top-down controls
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
        construction_info = self.game_engine.get_construction_info()
        if construction_info['active']:
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
        print(f"  Mouse normalized: ({mouse_x:.3f}, {mouse_y:.3f})")
        print(f"  Camera position: ({self.game_engine.camera.x:.0f}, {self.game_engine.camera.y:.0f}) zoom: {self.game_engine.camera.zoom:.2f}")
        
        if button == 'left':
            self.handle_left_click(world_x, world_y)
        elif button == 'right':
            self.handle_right_click(world_x, world_y)
            
    def handle_left_click(self, world_x, world_y):
        """Handle left mouse click for building placement and selection"""
        # Get mouse position for debug output
        if self.base.mouseWatcherNode.hasMouse():
            mouse_x = self.base.mouseWatcherNode.getMouseX()
            mouse_y = self.base.mouseWatcherNode.getMouseY()
            
            # Debug output
            screen_x = (mouse_x + 1) / 2 * 1600  # Convert to screen coordinates
            screen_y = (1 - mouse_y) / 2 * 900
            cam_pos = (self.game_engine.camera.x, self.game_engine.camera.y)
            cam_zoom = self.game_engine.camera.zoom
            print(f"Mouse left click at screen: ({screen_x:.0f}, {screen_y:.0f}) world: ({world_x:.0f}, {world_y:.0f})")
            print(f"  Mouse normalized: ({mouse_x:.3f}, {mouse_y:.3f})")
            print(f"  Camera position: ({cam_pos[0]:.0f}, {cam_pos[1]:.0f}) zoom: {cam_zoom:.2f}")
        
        # Check for asteroid click first
        asteroid_clicked = self.check_asteroid_click(world_x, world_y)
        if asteroid_clicked:
            return
        
        # Handle construction mode
        construction_info = self.game_engine.get_construction_info()
        if construction_info['active']:
            # Place building
            success = self.game_engine.place_building_at_cursor(world_x, world_y)
            return
        
        # Handle building selection first
        building = self.game_engine.get_building_at_position(world_x, world_y)
        if building:
            self.game_engine.select_building_at(world_x, world_y)
            # Clear enemy selection when selecting building
            if hasattr(self.game_engine, 'selected_enemy'):
                self.game_engine.selected_enemy = None
                self.game_engine.hud_system.hide_enemy_info()
        else:
            # Check for enemy selection
            enemy = self.get_enemy_at_position(world_x, world_y)
            if enemy:
                # Clear building selection when selecting enemy
                self.game_engine.clear_building_selection()
                # Select enemy
                self.game_engine.selected_enemy = enemy
                self.game_engine.hud_system.show_enemy_info(enemy)
                print(f"✓ Selected {enemy.enemy_type} enemy")
            else:
                # Clear all selections if clicking empty space
                self.game_engine.clear_building_selection()
                if hasattr(self.game_engine, 'selected_enemy'):
                    self.game_engine.selected_enemy = None
                    self.game_engine.hud_system.hide_enemy_info()
            
    def check_asteroid_click(self, world_x, world_y, tolerance=50.0):
        """Check if click is on an asteroid and show mineral info"""
        # Get asteroid nodes from scene manager
        if hasattr(self.game_engine, 'scene_manager') and hasattr(self.game_engine.scene_manager, 'asteroid_nodes'):
            for asteroid_node in self.game_engine.scene_manager.asteroid_nodes:
                if not asteroid_node:
                    continue
                    
                # Get asteroid position and radius
                position = asteroid_node.getPythonTag("position")
                radius = asteroid_node.getPythonTag("radius")
                
                if position and radius:
                    ast_x, ast_y = position
                    # Check if click is within asteroid bounds
                    distance = ((world_x - ast_x) ** 2 + (world_y - ast_y) ** 2) ** 0.5
                    if distance <= radius + tolerance:
                        # Show asteroid mineral information
                        current_minerals = asteroid_node.getPythonTag("minerals")
                        max_minerals = asteroid_node.getPythonTag("max_minerals")
                        
                        if current_minerals is not None and max_minerals is not None:
                            print(f"🪨 Asteroid: {current_minerals}/{max_minerals} minerals")
                            return True
        return False
    
    def get_enemy_at_position(self, world_x, world_y, tolerance=15.0):
        """Find enemy at the given world position"""
        if not hasattr(self.game_engine, 'enemies') or not self.game_engine.enemies:
            return None
            
        for enemy in self.game_engine.enemies:
            distance = ((world_x - enemy.x) ** 2 + (world_y - enemy.y) ** 2) ** 0.5
            if distance <= enemy.radius + tolerance:
                return enemy
        return None
        
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
        construction_info = self.game_engine.get_construction_info()
        if not construction_info['active']:  # Don't reset zoom during construction
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
        """Update building placement preview with visual feedback"""
        if not self.base.mouseWatcherNode.hasMouse():
            return
            
        # Convert mouse position to world coordinates
        world_x, world_y = self.get_mouse_world_position()
        if world_x is None or world_y is None:
            return
        
        # Update building system preview with current resources
        valid_placement, reason = self.game_engine.building_system.update_construction_preview(
            world_x, world_y, self.game_engine.minerals, self.game_engine.energy
        )
        
        self.valid_placement = valid_placement
        
    def get_mouse_world_position(self):
        """Get current mouse position in world coordinates"""
        if not self.base.mouseWatcherNode.hasMouse():
            return None, None
            
        # Get current mouse position from mouse watcher
        mouse_x = self.base.mouseWatcherNode.getMouseX()
        mouse_y = self.base.mouseWatcherNode.getMouseY()
        
        # Convert normalized mouse coordinates (-1 to 1) to screen coordinates
        screen_x = (mouse_x + 1) * self.game_engine.camera.screen_width / 2
        screen_y = (1 - mouse_y) * self.game_engine.camera.screen_height / 2
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

    def cancel_current_mode(self):
        """Cancel current mode (construction or selection)"""
        # Cancel construction mode
        if self.game_engine.get_construction_info()['active']:
            self.game_engine.cancel_building_construction()  # Fixed method name
            print("✓ Construction cancelled")
        # Cancel building selection
        elif hasattr(self.game_engine, 'building_system') and self.game_engine.building_system.selected_building:
            self.game_engine.building_system.clear_building_selection()
            print("✓ Building selection cleared")
        else:
            print("No active mode to cancel")
            
    def recycle_selected_building(self):
        """Recycle the currently selected building"""
        print("🗑️ Recycle key pressed!")
        if hasattr(self.game_engine, 'building_system') and self.game_engine.building_system.selected_building:
            building = self.game_engine.building_system.selected_building
            print(f"🗑️ Attempting to recycle {building.building_type} at ({building.x}, {building.y})")
            success = self.game_engine.building_system.recycle_building(building)
            if success:
                # Clear selection since building was removed
                self.game_engine.building_system.clear_building_selection()
                print("✓ Building recycled successfully")
            else:
                print("✗ Failed to recycle building")
        else:
            print("No building selected to recycle")
            
    def toggle_disable_selected_building(self):
        """Toggle disable state of selected building"""
        if hasattr(self.game_engine, 'building_system') and self.game_engine.building_system.selected_building:
            building = self.game_engine.building_system.selected_building
            if building.toggle_disable():
                status = "disabled" if building.disabled else "enabled"
                print(f"✓ Building {status}")
            else:
                print("✗ Cannot disable building in current state")
        else:
            print("No building selected to disable")
            
    def upgrade_selected_building(self):
        """Upgrade the currently selected building"""
        if hasattr(self.game_engine, 'building_system') and self.game_engine.building_system.selected_building:
            building = self.game_engine.building_system.selected_building
            success = self.game_engine.building_system.upgrade_building(building)
            if success:
                print(f"✓ Upgrading {building.building_type} to Level {building.level}")
            else:
                print(f"✗ Failed to upgrade {building.building_type}")
        else:
            print("No building selected for upgrade") 