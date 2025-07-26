"""
Arcade input system for handling user input.
"""

import arcade
from typing import Dict, Any
import math


class ArcadeInputSystem:
    """Input system for RTS-style base defense game."""
    
    def __init__(self, camera, game_logic):
        self.camera = camera
        self.game_logic = game_logic
        self.keys_pressed = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        
        # Camera controls
        self.camera_speed = 500.0  # Increased speed for better responsiveness
        
        # Building placement
        self.selected_building_type = None
        self.construction_mode = False
        self.valid_placement = False
        
    def setup(self):
        """Initialize the input system."""
        print("RTS input system setup complete")
    
    def update(self, dt: float):
        """Update input handling - camera panning and UI updates."""
        # Handle camera panning with WASD - Fixed key handling
        camera_moved = False
        
        if arcade.key.W in self.keys_pressed or arcade.key.UP in self.keys_pressed:
            self.camera.y += self.camera_speed * dt
            camera_moved = True
        if arcade.key.S in self.keys_pressed or arcade.key.DOWN in self.keys_pressed:
            self.camera.y -= self.camera_speed * dt
            camera_moved = True
        if arcade.key.A in self.keys_pressed or arcade.key.LEFT in self.keys_pressed:
            self.camera.x -= self.camera_speed * dt
            camera_moved = True
        if arcade.key.D in self.keys_pressed or arcade.key.RIGHT in self.keys_pressed:
            self.camera.x += self.camera_speed * dt
            camera_moved = True
        
        # Only clamp camera if it moved to avoid unnecessary constraints
        if camera_moved:
            # Clamp camera to world bounds with some padding
            padding = 300
            half_screen_w = self.camera.width / (2 * self.camera.zoom)
            half_screen_h = self.camera.height / (2 * self.camera.zoom)
            
            self.camera.x = max(half_screen_w - padding, 
                               min(self.camera.world_width - half_screen_w + padding, self.camera.x))
            self.camera.y = max(half_screen_h - padding, 
                               min(self.camera.world_height - half_screen_h + padding, self.camera.y))
        
        # Update building placement preview
        if self.construction_mode and self.selected_building_type:
            world_x, world_y = self.get_mouse_world_position()
            min_distance = 60 if self.selected_building_type == "wall" else 80
            self.valid_placement = self.game_logic._is_safe_spawn_location(world_x, world_y, min_distance)
    
    def on_key_press(self, key: int, modifiers: int):
        """Handle key press events."""
        self.keys_pressed.add(key)
        
        # Camera zoom controls
        if key == arcade.key.EQUAL or key == arcade.key.PLUS:
            self.camera.zoom_in(0.2)
        elif key == arcade.key.MINUS:
            self.camera.zoom_out(0.2)
        elif key == arcade.key.R and not self.construction_mode:  # Avoid conflict with repair node
            self.camera.set_zoom(1.0)  # Reset zoom
        
        # Building hotkeys
        elif key == arcade.key.T:
            self.select_building_type("missile_turret")
        elif key == arcade.key.L:
            self.select_building_type("laser_turret")
        elif key == arcade.key.N:
            self.select_building_type("power_node")
        elif key == arcade.key.P:
            self.select_building_type("power_plant")
        elif key == arcade.key.B:
            self.select_building_type("battery")
        elif key == arcade.key.R:
            self.select_building_type("repair_node")
        elif key == arcade.key.H:
            self.select_building_type("hangar_node")
        elif key == arcade.key.W:
            self.select_building_type("wall")
        elif key == arcade.key.X:
            self.select_building_type("long_range_laser")
        elif key == arcade.key.Z:
            self.select_building_type("long_range_missile")
        
        # Cancel construction
        elif key == arcade.key.ESCAPE and self.construction_mode:
            self.cancel_construction()
        
        # Center camera on starting base
        elif key == arcade.key.SPACE:
            center_x, center_y = self.game_logic.get_starting_base_position()
            self.camera.x = center_x
            self.camera.y = center_y
    
    def on_key_release(self, key: int, modifiers: int):
        """Handle key release events."""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Handle mouse motion."""
        self.mouse_x = x
        self.mouse_y = y
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse press."""
        self.mouse_pressed = True
        self.mouse_x = x
        self.mouse_y = y
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.construction_mode and self.selected_building_type:
                # Try to place building
                world_x, world_y = self.get_mouse_world_position()
                if self.game_logic.handle_build_request(self.selected_building_type, world_x, world_y):
                    print(f"Built {self.selected_building_type} at ({world_x:.0f}, {world_y:.0f})")
                    # Stay in construction mode for repeated building
                else:
                    print(f"Cannot build {self.selected_building_type} at that location")
            else:
                # Regular click - could select units/buildings in the future
                world_x, world_y = self.get_mouse_world_position()
                print(f"Clicked at world position: ({world_x:.0f}, {world_y:.0f})")
        
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            # Right click cancels construction
            if self.construction_mode:
                self.cancel_construction()
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse release."""
        self.mouse_pressed = False
    
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """Handle mouse scroll for zoom."""
        if scroll_y > 0:
            self.camera.zoom_in(0.1)
        elif scroll_y < 0:
            self.camera.zoom_out(0.1)
    
    def select_building_type(self, building_type: str):
        """Select a building type for construction."""
        self.selected_building_type = building_type
        self.construction_mode = True
        print(f"Selected {building_type} for construction")
    
    def cancel_construction(self):
        """Cancel construction mode."""
        self.construction_mode = False
        self.selected_building_type = None
        self.valid_placement = False
        print("Construction cancelled")
    
    def get_mouse_world_position(self) -> tuple:
        """Convert mouse screen position to world position."""
        screen_w = self.camera.width
        screen_h = self.camera.height
        world_x = (self.mouse_x - screen_w // 2) / self.camera.zoom + self.camera.x
        world_y = (self.mouse_y - screen_h // 2) / self.camera.zoom + self.camera.y
        return (world_x, world_y)
    
    def draw_construction_preview(self, camera):
        """Draw construction preview with range indicators if in construction mode."""
        if not self.construction_mode or not self.selected_building_type:
            return
        
        world_x, world_y = self.get_mouse_world_position()
        screen_x = (world_x - camera.x) * camera.zoom + camera.width // 2
        screen_y = (world_y - camera.y) * camera.zoom + camera.height // 2
        
        # Get building info from the new system
        from game.systems.game_logic import Building
        if self.selected_building_type in Building.BUILDING_TYPES:
            info = Building.BUILDING_TYPES[self.selected_building_type]
            scaled_size = info["size"] * camera.zoom
            
            # Choose color based on valid placement
            if self.valid_placement:
                color = (*info["color"][:3], 128)  # Semi-transparent
                outline_color = arcade.color.GREEN
                range_color = (0, 255, 0, 100)  # Green range indicator
            else:
                color = (255, 100, 100, 128)  # Red semi-transparent
                outline_color = arcade.color.RED
                range_color = (255, 0, 0, 100)  # Red range indicator
            
            # Draw range indicators first (behind the building)
            connection_range = 120  # Standard connection range for power nodes
            
            # Connection range for power nodes
            if info.get("is_power_node", False) or self.selected_building_type == "starting_base":
                range_radius = connection_range * camera.zoom
                arcade.draw_circle_outline(screen_x, screen_y, range_radius, range_color, 2)
                # Add text label
                arcade.draw_text("Connection Range", screen_x - 60, screen_y + range_radius + 10, 
                               range_color[:3], 10)
            
            # Attack range for turrets
            if info.get("attack_range", 0) > 0:
                attack_range_radius = info["attack_range"] * camera.zoom
                arcade.draw_circle_outline(screen_x, screen_y, attack_range_radius, range_color, 2)
                # Add text label
                arcade.draw_text("Attack Range", screen_x - 40, screen_y + attack_range_radius + 10, 
                               range_color[:3], 10)
            
            # Repair range for repair nodes
            if info.get("repair_range", 0) > 0:
                repair_range_radius = info["repair_range"] * camera.zoom
                arcade.draw_circle_outline(screen_x, screen_y, repair_range_radius, range_color, 2)
                # Add text label
                arcade.draw_text("Repair Range", screen_x - 40, screen_y + repair_range_radius + 10, 
                               range_color[:3], 10)
            
            # Draw preview based on building type
            if self.selected_building_type == "starting_base":
                # Draw starting base as hexagon
                points = []
                for i in range(6):
                    angle = i * 60 * math.pi / 180
                    px = screen_x + scaled_size * math.cos(angle)
                    py = screen_y + scaled_size * math.sin(angle)
                    points.append((px, py))
                arcade.draw_polygon_filled(points, color)
                arcade.draw_polygon_outline(points, outline_color, 3)
            elif info.get("is_power_node", False):
                # Draw power nodes as circles
                arcade.draw_circle_filled(screen_x, screen_y, scaled_size, color)
                arcade.draw_circle_outline(screen_x, screen_y, scaled_size, outline_color, 3)
                # Connection points
                for i in range(6):
                    angle = i * 60 * math.pi / 180
                    px = screen_x + (scaled_size + 3) * math.cos(angle)
                    py = screen_y + (scaled_size + 3) * math.sin(angle)
                    arcade.draw_circle_filled(px, py, 2, outline_color)
            elif self.selected_building_type in ["missile_turret", "laser_turret", "long_range_laser", "long_range_missile"]:
                # Draw turrets as squares with barrels
                left = screen_x - scaled_size
                right = screen_x + scaled_size
                top = screen_y + scaled_size
                bottom = screen_y - scaled_size
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, outline_color, 3)
                # Barrel
                barrel_length = scaled_size * 0.8
                arcade.draw_line(screen_x, screen_y, screen_x + barrel_length, screen_y, outline_color, 4)
            elif self.selected_building_type == "wall":
                # Draw walls as small rectangles
                left = screen_x - scaled_size
                right = screen_x + scaled_size
                top = screen_y + scaled_size
                bottom = screen_y - scaled_size
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, outline_color, 2)
            else:
                # Draw other buildings as rectangles
                left = screen_x - scaled_size
                right = screen_x + scaled_size
                top = screen_y + scaled_size
                bottom = screen_y - scaled_size
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, outline_color, 3) 