"""
Panda3D HUD System - Phase 2 Implementation
Enhanced resource display with transparent background and energy bar
"""

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode, CardMaker, NodePath
from game.entities.building import BuildingState
import random

class HUDSystem:
    """Manages on-screen display of game information"""
    
    def __init__(self, base, game_engine):
        self.base = base
        self.game_engine = game_engine
        
        # HUD elements
        self.hud_elements = {}
        self.enemy_info_panel = None
        self.building_menu = None
        self.building_buttons = []
        self.research_buttons = []
        self.current_tab = "buildings"  # "buildings" or "research"
        self.tab_buttons = []
        
        # Wave preview UI
        self.wave_preview_panel = None
        self.wave_preview_text = None
        self.start_wave_button = None
        
        # Minimap
        self.minimap_panel = None
        self.minimap_elements = []
        
        self.setup_hud()
        
    def setup_hud(self):
        """Set up enhanced HUD elements with transparent resource panel"""
        print("Setting up enhanced HUD with resource panel...")
        
        # Create transparent background panel for resources (moved more to the right)
        self.resource_panel = DirectFrame(
            frameSize=(-1.75, -0.45, 0.58, 0.97),
            frameColor=(0, 0, 0, 0.3),  # Semi-transparent black
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        
        # Resource text displays with better formatting (moved more to the right)
        self.hud_elements['minerals'] = OnscreenText(
            text="Minerals: 600.0",
            pos=(-1.70, 0.87),
            scale=0.05,
            fg=(0, 0.8, 1, 1),  # Blue (swapped from yellow)
            align=TextNode.ALeft,
            parent=self.base.aspect2d
        )
        
        self.hud_elements['minerals_rate'] = OnscreenText(
            text="Minerals/sec: 0.0",
            pos=(-1.70, 0.82),
            scale=0.04,
            fg=(0.5, 0.6, 0.8, 1),  # Dim blue (swapped from dim yellow)
            align=TextNode.ALeft,
            parent=self.base.aspect2d
        )
        
        self.hud_elements['energy'] = OnscreenText(
            text="Energy: 50.0 / 100.0",
            pos=(-1.70, 0.76),
            scale=0.05,
            fg=(1, 1, 0, 1),  # Yellow (swapped from blue)
            align=TextNode.ALeft,
            parent=self.base.aspect2d
        )
        
        self.hud_elements['energy_rate'] = OnscreenText(
            text="Energy/sec: +0.2",
            pos=(-1.70, 0.71),
            scale=0.04,
            fg=(0.8, 0.8, 0.5, 1),  # Dim yellow (swapped from dim blue)
            align=TextNode.ALeft,
            parent=self.base.aspect2d
        )
        
        # Create energy bar background (adjusted positioning)
        self.energy_bar_bg = self.create_energy_bar_background()
        
        # Create energy bar foreground (will be updated dynamically)
        self.energy_bar_fg = self.create_energy_bar_foreground(1.0)  # Start full
        
        # Building selection panel (initially hidden) - More compact dimensions
        self.building_panel = DirectFrame(
            frameSize=(-1.98, -1.3, -0.30, 0.25),  # Slightly taller to accommodate health bar
            frameColor=(0, 0, 0, 0.4),  # Semi-transparent black
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        self.building_panel.hide()
        
        # Health bar background
        self.health_bar_bg = DirectFrame(
            frameSize=(-1.96, -1.32, 0.08, 0.12),
            frameColor=(0.3, 0.0, 0.0, 0.8),  # Dark red background
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        self.health_bar_bg.hide()
        
        # Health bar foreground (will be updated dynamically)
        self.health_bar_fg = DirectFrame(
            frameSize=(-1.96, -1.32, 0.08, 0.12),
            frameColor=(0.0, 0.8, 0.0, 0.9),  # Green foreground
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        self.health_bar_fg.hide()
        
        # Building info elements (initially empty) - More compact layout with smaller fonts
        posx = -1.7
        self.building_info = {
            
            'name': OnscreenText(text="", pos=(posx, 0.20), scale=0.04, fg=(1, 1, 1, 1), align=TextNode.ALeft, parent=self.base.aspect2d),  # Moved from -1.9 to -1.6
            'health': OnscreenText(text="", pos=(posx, 0.15), scale=0.03, fg=(0.8, 1, 0.8, 1), align=TextNode.ALeft, parent=self.base.aspect2d),  # Moved from -1.9 to -1.6
            'level': OnscreenText(text="", pos=(posx, 0.11), scale=0.03, fg=(1, 1, 0, 1), align=TextNode.ALeft, parent=self.base.aspect2d),  # Moved from -1.9 to -1.6
            'stats': OnscreenText(text="", pos=(posx, 0.05), scale=0.03, fg=(0.9, 0.9, 0.9, 1), align=TextNode.ALeft, parent=self.base.aspect2d),  # Moved from -1.9 to -1.6
            'powered': OnscreenText(text="", pos=(posx, -0.01), scale=0.03, fg=(0.5, 1, 1, 1), align=TextNode.ALeft, parent=self.base.aspect2d),  # Moved from -1.9 to -1.6
            'actions': OnscreenText(text="", pos=(posx, -0.05), scale=0.025, fg=(1, 1, 0.5, 1), align=TextNode.ALeft, parent=self.base.aspect2d)  # Moved from -1.9 to -1.6
        }
        
        # Hide building info initially
        for element in self.building_info.values():
            element.hide()
        
        # Game state (top-center)
        self.hud_elements['game_state'] = OnscreenText(
            text="Press SPACE to start",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),  # White
            align=TextNode.ACenter,
            mayChange=True
        )
        
        # Camera info (top-right)
        self.hud_elements['camera_info'] = OnscreenText(
            text="Camera: (2400, 1350) Zoom: 1.0x",
            pos=(1.8, 0.9),
            scale=0.05,
            fg=(0.8, 0.8, 0.8, 1),  # Light gray
            align=TextNode.ARight,
            mayChange=True
        )
        
        # Hide keyboard controls (set visible to False)
        self.controls_visible = False
        
        # Setup interactive building menu
        self.setup_building_menu()
        
        # Setup wave preview UI
        self.setup_wave_preview()
        
        # Setup minimap
        self.setup_minimap()
        
        # Construction mode indicator (center-bottom)
        self.hud_elements['construction'] = OnscreenText(
            text="",
            pos=(0, -0.8),
            scale=0.06,
            fg=(1, 0.5, 0, 1),  # Orange
            align=TextNode.ACenter,
            mayChange=True
        )
        
        print("✓ HUD setup complete")
        
    def create_energy_bar_background(self):
        """Create energy bar background"""
        bg_card = CardMaker("energy_bar_bg")
        bg_card.setFrame(-1.70, -0.57, 0.635, 0.655)  # Moved to match new positioning
        bg_node = NodePath(bg_card.generate())
        bg_node.setColor(0.2, 0.2, 0.4, 0.8)  # Dark blue background
        bg_node.reparentTo(self.base.aspect2d)
        return bg_node
    
    def create_energy_bar_foreground(self, progress):
        """Create energy bar foreground based on energy percentage"""
        if hasattr(self, 'energy_bar_fg') and self.energy_bar_fg:
            self.energy_bar_fg.removeNode()
            
        bar_width = 1.13 * progress  # Same width calculation
        
        fg_card = CardMaker("energy_bar_fg")
        fg_card.setFrame(-1.70, -1.70 + bar_width, 0.635, 0.655)  # Moved to match new positioning
        fg_node = NodePath(fg_card.generate())
        
        # Color based on energy level (red to blue gradient)
        if progress > 0.6:
            fg_node.setColor(0.2, 0.6, 1.0, 0.9)  # Blue when high
        elif progress > 0.3:
            fg_node.setColor(0.8, 0.8, 0.2, 0.9)  # Yellow when medium  
        else:
            fg_node.setColor(1.0, 0.3, 0.2, 0.9)  # Red when low
            
        fg_node.reparentTo(self.base.aspect2d)
        return fg_node
        
    def update(self, dt):
        """Update HUD elements with current game state"""
        game_data = self.game_engine.get_game_data()
        
        # Update resources with enhanced formatting
        self.hud_elements['minerals']['text'] = f"Minerals: {game_data['minerals']:.1f}"
        
        # Update building menu affordability
        self.update_building_menu()
        
        # Update wave preview
        self.update_wave_preview()
        
        # Update minimap (less frequently to avoid performance issues)
        if hasattr(self, '_minimap_update_timer'):
            self._minimap_update_timer += dt
        else:
            self._minimap_update_timer = 0
            
        if self._minimap_update_timer >= 0.5:  # Update every 0.5 seconds
            self.update_minimap()
            self._minimap_update_timer = 0
        
        # Calculate mineral generation rate from active miners
        mineral_rate = self.calculate_mining_rate()
        self.hud_elements['minerals_rate']['text'] = f"Minerals/sec: +{mineral_rate:.1f}"
        
        # Update energy with capacity and rate
        energy = game_data['energy']
        max_energy = getattr(self.game_engine, 'max_energy', 100)
        energy_rate = self.game_engine.get_power_generation_rate()
        
        self.hud_elements['energy']['text'] = f"Energy: {energy:.1f} / {max_energy:.1f}"
        self.hud_elements['energy_rate']['text'] = f"Energy/sec: +{energy_rate:.1f}"
        
        # Update energy bar
        energy_progress = energy / max_energy if max_energy > 0 else 0
        self.energy_bar_fg = self.create_energy_bar_foreground(energy_progress)
        
        # Update game state
        state_text = self.get_state_text(game_data)
        self.hud_elements['game_state']['text'] = state_text
        
        # Update camera info
        cam_x, cam_y = game_data['camera_x'], game_data['camera_y']
        zoom = game_data['camera_zoom']
        self.hud_elements['camera_info']['text'] = f"Camera: ({cam_x:.0f}, {cam_y:.0f}) Zoom: {zoom:.1f}x"
        
        # Update construction mode
        construction_text = self.get_construction_text()
        self.hud_elements['construction']['text'] = construction_text
        
    def get_state_text(self, game_data):
        """Get appropriate text for current game state"""
        state = game_data['state']
        paused = game_data['paused']
        
        if state == "menu":
            return "Press SPACE to start | ESC to quit"
        elif state == "playing":
            if paused:
                return "PAUSED - Press P to resume"
            else:
                wave = game_data['wave_number']
                score = game_data['score']
                return f"Wave {wave} | Score: {score} | P to pause"
        elif state == "game_over":
            return "GAME OVER - Press SPACE to restart"
        else:
            return f"State: {state}"
            
    def get_construction_text(self):
        """Get text for construction mode and progress"""
        construction_info = self.game_engine.get_construction_info()
        
        if construction_info['active']:
            building_type = construction_info['building_type']
            cost = construction_info['cost']
            can_afford = construction_info['can_afford']
            
            minerals_cost = cost.get('minerals', 0)
            energy_cost = cost.get('energy', 0)
            
            # Calculate construction energy requirement (100 minerals = 50 energy)
            construction_energy = (minerals_cost / 100.0) * 50.0
            
            afford_text = "✓" if can_afford else "✗"
            
            return f"Building: {building_type.title()} | Cost: {minerals_cost}M {energy_cost}E | Construction: {construction_energy:.1f}E {afford_text} | Left-click to place, Right-click to cancel"
        else:
            return ""
            
    def show_message(self, message, duration=3.0, color=(1, 1, 1, 1)):
        """Show a temporary message"""
        # For Phase 2, just update the game state text
        # Phase 3 can implement proper temporary messages
        self.hud_elements['game_state']['text'] = message
        
    def hide_hud(self):
        """Hide all HUD elements"""
        for element in self.hud_elements.values():
            element.hide()
            
    def show_hud(self):
        """Show all HUD elements"""
        for element in self.hud_elements.values():
            element.show()
            
    def toggle_hud(self):
        """Toggle HUD visibility"""
        # Check if first element is hidden to determine current state
        if self.hud_elements['minerals'].isHidden():
            self.show_hud()
            print("HUD shown")
        else:
            self.hide_hud()
            print("HUD hidden")
            
    def show_building_info(self, building):
        """Show building information panel for selected building"""
        if not building:
            self.hide_building_info()
            return
            
        self.building_panel.show()
        for element in self.building_info.values():
            element.show()
        
        # Show and update health bar
        self.health_bar_bg.show()
        self.health_bar_fg.show()
            
        # Get building configuration
        building_config = self.game_engine.config.buildings.get("building_types", {}).get(building.building_type, {})
        
        # Building name and level - show unique name
        level = getattr(building, 'level', 1)
        building_name = getattr(building, 'building_name', f"SS-U-{random.randint(1000,9999)}")
        formal_name = building_config.get('name', building.building_type.title())
        self.building_info['name']['text'] = f"{building_name} - {formal_name}"
        self.building_info['level']['text'] = f"Level: {level}"
        
        # Health information
        health = building.health
        max_health = building.max_health
        health_percent = (health / max_health * 100) if max_health > 0 else 0
        self.building_info['health']['text'] = f"Health: {health:.0f}/{max_health:.0f} ({health_percent:.0f}%)"
        
        # Update health bar
        self.update_health_bar(health_percent / 100.0)
        
        # Building stats
        stats_text = ""
        if building_config.get('power_generation', 0) > 0:
            stats_text += f"Energy: +{building_config['power_generation']:.1f}/s\n"
        if building_config.get('attack_damage', 0) > 0:
            stats_text += f"Damage: {building_config['attack_damage']:.0f}\n"
            stats_text += f"Range: {building_config.get('attack_range', 0):.0f}\n"
        if building_config.get('energy_capacity', 0) > 0:
            stats_text += f"Storage: {building_config['energy_capacity']:.0f}\n"
        
        self.building_info['stats']['text'] = stats_text.rstrip()
        
        # Powered status
        if building.state == BuildingState.UNDER_CONSTRUCTION:
            power_status = "CONSTRUCTING"
        elif building.is_connected_to_power:
            power_status = "POWERED"
        else:
            power_status = "NO POWER"
            
        if building.disabled:
            power_status = "DISABLED"
            
        self.building_info['powered']['text'] = f"Status: {power_status}"
        
        # Action shortcuts with updated recycle percentage
        if level < 5:
            # Get the mineral cost from the building configuration properly
            building_costs = building_config.get('cost', {'minerals': 50, 'energy': 0})
            if isinstance(building_costs, dict):
                mineral_cost = building_costs.get('minerals', 50)
            else:
                mineral_cost = building_costs  # Fallback if it's just a number
            upgrade_cost = mineral_cost * level
            actions_text = f"[DELETE] Recycle 75%\n[G] Disable\n[U] UPGRADE ({upgrade_cost}m, {upgrade_cost//4}e)"
        else:
            actions_text = f"[DELETE] Recycle 75%\n[G] Disable\nMAX LEVEL"
        self.building_info['actions']['text'] = actions_text
        
    def update_health_bar(self, health_ratio):
        """Update the health bar display based on health ratio (0.0 to 1.0)"""
        if not hasattr(self, 'health_bar_fg'):
            return
            
        # Calculate bar width based on health ratio
        bar_left = -1.96
        bar_right = -1.32
        bar_width = bar_right - bar_left
        new_right = bar_left + (bar_width * health_ratio)
        
        # Update health bar frame size
        self.health_bar_fg['frameSize'] = (bar_left, new_right, 0.08, 0.12)
        
        # Update color based on health level
        if health_ratio > 0.7:
            color = (0.0, 0.8, 0.0, 0.9)  # Green
        elif health_ratio > 0.3:
            color = (1.0, 1.0, 0.0, 0.9)  # Yellow
        else:
            color = (1.0, 0.2, 0.0, 0.9)  # Red
            
        self.health_bar_fg['frameColor'] = color

    def hide_building_info(self):
        """Hide building information panel"""
        self.building_panel.hide()
        self.health_bar_bg.hide()
        self.health_bar_fg.hide()
        for element in self.building_info.values():
            element.hide()
    
    def setup_wave_preview(self):
        """Setup wave preview UI"""
        try:
            # Wave preview panel (top center)
            self.wave_preview_panel = DirectFrame(
                frameSize=(-0.4, 0.4, 0.75, 0.95),
                frameColor=(0.1, 0.1, 0.2, 0.8),
                pos=(0, 0, 0),
                parent=self.base.aspect2d
            )
            
            # Wave preview text
            self.wave_preview_text = OnscreenText(
                text="Wave 1 starting in 45s...",
                pos=(0, 0.88),
                scale=0.04,
                fg=(1, 1, 0.5, 1),
                align=TextNode.ACenter,
                parent=self.base.aspect2d
            )
            
            # Start wave button
            self.start_wave_button = DirectButton(
                text="START NEXT WAVE",
                scale=0.04,
                pos=(0, 0, 0.78),
                frameSize=(-2.5, 2.5, -0.6, 0.6),
                frameColor=(0.6, 0.2, 0.2, 1.0),
                text_fg=(1, 1, 1, 1),
                command=self.start_next_wave,
                parent=self.base.aspect2d
            )
            
        except Exception as e:
            print(f"Error setting up wave preview: {e}")
    
    def setup_minimap(self):
        """Setup minimap in bottom left corner"""
        try:
            # Minimap panel (bottom left corner)
            minimap_size = 0.3
            self.minimap_panel = DirectFrame(
                frameSize=(-1.0, -1.0 + minimap_size, -1.0, -1.0 + minimap_size),
                frameColor=(0.0, 0.0, 0.0, 0.9),
                pos=(0, 0, 0),
                parent=self.base.aspect2d
            )
            
            # Minimap border
            self.minimap_border = DirectFrame(
                frameSize=(-1.02, -1.0 + minimap_size + 0.02, -1.02, -1.0 + minimap_size + 0.02),
                frameColor=(0.3, 0.3, 0.3, 1.0),
                pos=(0, 0, 0),
                parent=self.base.aspect2d
            )
            
            # Minimap title
            self.minimap_title = OnscreenText(
                text="MINIMAP",
                pos=(-0.85, -0.75),
                scale=0.03,
                fg=(1, 1, 1, 1),
                align=TextNode.ACenter,
                parent=self.base.aspect2d
            )
            
        except Exception as e:
            print(f"Error setting up minimap: {e}")
    
    def start_next_wave(self):
        """Start the next wave manually"""
        try:
            if hasattr(self.game_engine, 'wave_system'):
                success = self.game_engine.wave_system.start_next_wave_manually()
                if success:
                    print("✓ Next wave started manually")
                else:
                    print("✗ Cannot start next wave yet")
        except Exception as e:
            print(f"Error starting next wave: {e}")
    
    def update_wave_preview(self):
        """Update wave preview text and button"""
        try:
            if not hasattr(self.game_engine, 'wave_system') or not self.wave_preview_text:
                return
                
            wave_system = self.game_engine.wave_system
            
            if wave_system.wave_active:
                # Wave is active
                progress = wave_system.get_wave_progress()
                self.wave_preview_text.setText(f"Wave {wave_system.current_wave} - {progress['enemies_remaining']}/{progress['total_enemies']} enemies remaining")
                self.start_wave_button.hide()
            else:
                # Between waves
                preview = wave_system.get_next_wave_preview()
                time_until_auto = wave_system.get_time_until_auto_wave()
                
                if preview and time_until_auto > 0:
                    self.wave_preview_text.setText(f"{preview['preview_text']} - Auto start in {time_until_auto:.0f}s")
                    if wave_system.can_start_next_wave():
                        self.start_wave_button.show()
                    else:
                        self.start_wave_button.hide()
                elif preview:
                    self.wave_preview_text.setText(preview['preview_text'])
                    if wave_system.can_start_next_wave():
                        self.start_wave_button.show()
                    else:
                        self.start_wave_button.hide()
                else:
                    self.wave_preview_text.setText("Preparing next wave...")
                    self.start_wave_button.hide()
                    
        except Exception as e:
            print(f"Error updating wave preview: {e}")
    
    def update_minimap(self):
        """Update minimap with current game state"""
        try:
            if not self.minimap_panel:
                return
                
            # Clear existing minimap elements
            for element in self.minimap_elements:
                if element:
                    element.destroy()
            self.minimap_elements.clear()
            
            # Get world bounds for scaling
            world_width = 4800
            world_height = 2700
            minimap_size = 0.3
            
            # Scale factors
            scale_x = minimap_size / world_width
            scale_y = minimap_size / world_height
            
            # Minimap offset (lower left corner)
            offset_x = -1.0
            offset_y = -1.0
            
            # Draw buildings (green dots)
            if hasattr(self.game_engine, 'building_system'):
                for building in self.game_engine.building_system.buildings.values():
                    if building.building_type != "asteroid":  # Skip asteroids for buildings
                        x = offset_x + (building.x * scale_x)
                        y = offset_y + (building.y * scale_y)
                        
                        dot = OnscreenText(
                            text="o",
                            pos=(x, y),
                            scale=0.015,
                            fg=(0, 1, 0, 1),  # Green
                            align=TextNode.ACenter,
                            parent=self.base.aspect2d
                        )
                        self.minimap_elements.append(dot)
            
            # Draw asteroids (brown dots)
            if hasattr(self.game_engine, 'building_system'):
                for building in self.game_engine.building_system.buildings.values():
                    if building.building_type == "asteroid":
                        x = offset_x + (building.x * scale_x)
                        y = offset_y + (building.y * scale_y)
                        
                        dot = OnscreenText(
                            text=".",
                            pos=(x, y),
                            scale=0.020,
                            fg=(0.6, 0.4, 0.2, 1),  # Brown
                            align=TextNode.ACenter,
                            parent=self.base.aspect2d
                        )
                        self.minimap_elements.append(dot)
            
            # Draw enemies (red dots)
            if hasattr(self.game_engine, 'enemies'):
                for enemy in self.game_engine.enemies:
                    if enemy.is_alive():
                        x = offset_x + (enemy.x * scale_x)
                        y = offset_y + (enemy.y * scale_y)
                        
                        dot = OnscreenText(
                            text="X",
                            pos=(x, y),
                            scale=0.018,
                            fg=(1, 0, 0, 1),  # Red
                            align=TextNode.ACenter,
                            parent=self.base.aspect2d
                        )
                        self.minimap_elements.append(dot)
                        
        except Exception as e:
            print(f"Error updating minimap: {e}")
            
    def cleanup(self):
        """Clean up HUD resources"""
        print("Cleaning up HUD...")
        
        # Clean up resource display elements
        if hasattr(self, 'resource_panel'):
            self.resource_panel.removeNode()
        
        for element_name, element in self.hud_elements.items():
            if element:
                element.removeNode()
        
        # Clean up building info elements
        if hasattr(self, 'building_info'):
            for info_element in self.building_info.values():
                if info_element:
                    info_element.removeNode()
        
        # Clean up building selection panel
        if hasattr(self, 'building_panel'):
            self.building_panel.removeNode()
            
        # Clean up building menu elements
        if hasattr(self, 'building_menu_panel'):
            self.building_menu_panel.removeNode()
        if hasattr(self, 'building_menu_title'):
            self.building_menu_title.removeNode()
        if hasattr(self, 'building_menu_items'):
            for item in self.building_menu_items:
                if item:
                    item.removeNode()
        
        self.hud_elements.clear()
        print("✓ HUD cleanup complete")

    def calculate_mining_rate(self):
        """Calculate approximate mineral generation rate from active miners and converters"""
        if not hasattr(self.game_engine, 'building_system'):
            return 0.0
            
        total_rate = 0.0
        
        for building in self.game_engine.building_system.buildings.values():
            if (building.state == BuildingState.OPERATIONAL and 
                not building.disabled and 
                building.is_connected_to_power):
                
                # Mining rate from miners
                if building.building_type == "miner":
                    building_config = self.game_engine.config.buildings.get("building_types", {}).get("miner", {})
                    mining_rate = building_config.get("mining_rate", 2.3)
                    mining_interval = building_config.get("mining_interval", 240) / 100.0
                    
                    if mining_interval > 0:
                        minerals_per_second = mining_rate / mining_interval
                        total_rate += minerals_per_second
                
                # Conversion rate from converters
                elif building.building_type == "converter":
                    building_config = self.game_engine.config.buildings.get("building_types", {}).get("converter", {})
                    mineral_generation = building_config.get("mineral_generation", 1.0)
                    conversion_interval = building_config.get("conversion_interval", 100) / 100.0
                    
                    if conversion_interval > 0:
                        minerals_per_second = mineral_generation / conversion_interval
                        total_rate += minerals_per_second
                    
        return total_rate
    
    def show_enemy_info(self, enemy):
        """Display enemy information panel"""
        try:
            # Hide any existing enemy info
            self.hide_enemy_info()
            
            # Create enemy info panel
            panel_width = 0.5
            panel_height = 0.3
            
            self.enemy_info_panel = DirectFrame(
                frameSize=(0, panel_width, -panel_height, 0),
                frameColor=(0.1, 0.1, 0.1, 0.9),
                pos=(0.5, 0, 0.5),
                parent=self.base.aspect2d
            )
            
            # Enemy type and name
            enemy_title = OnscreenText(
                text=f"{enemy.enemy_type.title()} Enemy",
                pos=(panel_width/2, -0.05),
                scale=0.06,
                fg=(1, 1, 1, 1),
                align=TextNode.ACenter,
                parent=self.enemy_info_panel
            )
            
            # Health bar background
            health_bg = DirectFrame(
                frameSize=(0.05, panel_width-0.05, -0.12, -0.08),
                frameColor=(0.3, 0.1, 0.1, 1.0),
                parent=self.enemy_info_panel
            )
            
            # Health bar (green/yellow/red based on health percentage)
            health_percentage = enemy.current_health / enemy.max_health
            health_width = (panel_width - 0.1) * health_percentage
            
            if health_percentage > 0.6:
                health_color = (0.2, 0.8, 0.2, 1.0)  # Green
            elif health_percentage > 0.3:
                health_color = (0.8, 0.8, 0.2, 1.0)  # Yellow
            else:
                health_color = (0.8, 0.2, 0.2, 1.0)  # Red
            
            health_bar = DirectFrame(
                frameSize=(0.05, 0.05 + health_width, -0.12, -0.08),
                frameColor=health_color,
                parent=self.enemy_info_panel
            )
            
            # Health text
            health_text = OnscreenText(
                text=f"Health: {enemy.current_health:.1f}/{enemy.max_health:.1f}",
                pos=(panel_width/2, -0.18),
                scale=0.04,
                fg=(1, 1, 1, 1),
                align=TextNode.ACenter,
                parent=self.enemy_info_panel
            )
            
            # Enemy position
            pos_text = OnscreenText(
                text=f"Position: ({enemy.x:.0f}, {enemy.y:.0f})",
                pos=(panel_width/2, -0.24),
                scale=0.035,
                fg=(0.8, 0.8, 0.8, 1),
                align=TextNode.ACenter,
                parent=self.enemy_info_panel
            )
            
        except Exception as e:
            print(f"Error showing enemy info: {e}")
    
    def hide_enemy_info(self):
        """Hide enemy information panel"""
        try:
            if self.enemy_info_panel:
                self.enemy_info_panel.destroy()
                self.enemy_info_panel = None
        except Exception as e:
            print(f"Error hiding enemy info: {e}")
    
    def setup_building_menu(self):
        """Create interactive building/research selection menu with tabs"""
        try:
            # Shift menu 10% to the left to avoid edge clipping
            menu_x_offset = -0.1
            
            # Main menu panel (right side, shifted left)
            self.building_menu_panel = DirectFrame(
                frameSize=(1.05 + menu_x_offset, 1.85 + menu_x_offset, -0.95, 0.95),
                frameColor=(0.1, 0.1, 0.1, 0.8),
                pos=(0, 0, 0),
                parent=self.base.aspect2d
            )
            
            # Tab buttons at the top
            tab_y = 0.85
            tab_width = 0.35
            buildings_tab_x = 1.25 + menu_x_offset
            research_tab_x = 1.60 + menu_x_offset
            
            self.buildings_tab_button = DirectButton(
                text="BUILDINGS",
                scale=0.04,
                pos=(buildings_tab_x, 0, tab_y),
                frameSize=(-tab_width/2, tab_width/2, -0.05, 0.05),
                frameColor=(0.3, 0.6, 0.3, 1.0),
                text_fg=(1, 1, 1, 1),
                command=self.switch_to_buildings_tab,
                parent=self.base.aspect2d
            )
            
            self.research_tab_button = DirectButton(
                text="RESEARCH",
                scale=0.04,
                pos=(research_tab_x, 0, tab_y),
                frameSize=(-tab_width/2, tab_width/2, -0.05, 0.05),
                frameColor=(0.6, 0.3, 0.6, 1.0),
                text_fg=(1, 1, 1, 1),
                command=self.switch_to_research_tab,
                parent=self.base.aspect2d
            )
            
            # Create vertical scrollable frame
            self.building_scroll_frame = DirectScrolledFrame(
                frameSize=(1.07 + menu_x_offset, 1.83 + menu_x_offset, -0.9, 0.75),
                canvasSize=(1.07 + menu_x_offset, 1.83 + menu_x_offset, -3.0, 0.75),  # Vertical canvas
                frameColor=(0, 0, 0, 0),  # Transparent
                scrollBarWidth=0.04,
                verticalScroll_frameColor=(0.3, 0.3, 0.3, 0.8),
                verticalScroll_thumb_frameColor=(0.6, 0.6, 0.6, 1.0),
                parent=self.base.aspect2d
            )
            
            # Initialize with buildings tab
            self.switch_to_buildings_tab()
                
        except Exception as e:
            print(f"Error setting up building menu: {e}")
    
    def switch_to_buildings_tab(self):
        """Switch to buildings tab"""
        self.current_tab = "buildings"
        self.update_tab_appearance()
        self.populate_current_tab()
    
    def switch_to_research_tab(self):
        """Switch to research tab"""
        self.current_tab = "research"
        self.update_tab_appearance()
        self.populate_current_tab()
    
    def update_tab_appearance(self):
        """Update tab button appearance based on current tab"""
        if self.current_tab == "buildings":
            self.buildings_tab_button['frameColor'] = (0.3, 0.8, 0.3, 1.0)  # Bright green
            self.research_tab_button['frameColor'] = (0.4, 0.2, 0.4, 1.0)   # Dark purple
        else:
            self.buildings_tab_button['frameColor'] = (0.2, 0.4, 0.2, 1.0)  # Dark green
            self.research_tab_button['frameColor'] = (0.6, 0.3, 0.8, 1.0)   # Bright purple
    
    def populate_current_tab(self):
        """Populate the current tab with appropriate content"""
        # Clear existing buttons
        for button in self.building_buttons + self.research_buttons:
            if button:
                button.destroy()
        self.building_buttons.clear()
        self.research_buttons.clear()
        
        if self.current_tab == "buildings":
            self.populate_buildings_tab()
        else:
            self.populate_research_tab()
    
    def populate_buildings_tab(self):
        """Populate buildings tab with building buttons"""
        building_configs = self.get_building_configurations()
        
        if building_configs:
            menu_x_offset = -0.1
            button_width = 0.7
            button_height = 0.08
            y_start = 0.65
            
            for i, (building_type, config) in enumerate(building_configs):
                y_pos = y_start - (i * (button_height + 0.02))
                self.create_building_button(building_type, config, y_pos, menu_x_offset, button_width, button_height)
    
    def populate_research_tab(self):
        """Populate research tab with research buttons"""
        if not hasattr(self.game_engine, 'research_system'):
            return
            
        research_system = self.game_engine.research_system
        available_research = research_system.get_available_research()
        
        if available_research:
            menu_x_offset = -0.1
            button_width = 0.7
            button_height = 0.08
            y_start = 0.65
            
            for i, tech in enumerate(available_research):
                y_pos = y_start - (i * (button_height + 0.02))
                self.create_research_button(tech, y_pos, menu_x_offset, button_width, button_height)
        else:
            # Add fallback text if no research available
            fallback_text = OnscreenText(
                text="No research available\n(Prerequisites not met)",
                pos=(1.45, 0.5),
                scale=0.04,
                fg=(0.7, 0.7, 0.7, 1),
                align=TextNode.ACenter,
                parent=self.building_scroll_frame.getCanvas()
            )
            self.research_buttons.append(fallback_text)
    
    def get_building_configurations(self):
        """Get building configurations from game engine config"""
        try:
            if not hasattr(self.game_engine, 'config') or not hasattr(self.game_engine.config, 'buildings'):
                return []
            
            buildings_config = self.game_engine.config.buildings.get("building_types", {})
            
            # Order buildings logically for the menu
            building_order = [
                "solar", "nuclear", "connector", "battery", 
                "miner", "converter", "turret", "laser", 
                "superlaser", "missile_launcher", "repair", 
                "hangar", "force_field"
            ]
            
            configurations = []
            for building_type in building_order:
                if building_type in buildings_config:
                    configurations.append((building_type, buildings_config[building_type]))
            
            return configurations
            
        except Exception as e:
            print(f"Error getting building configurations: {e}")
            return []
    
    def create_building_button(self, building_type, config, y_pos, menu_x_offset=-0.1, button_width=0.7, button_height=0.08):
        """Create a clickable button for a building type"""
        try:
            # Get building costs
            mineral_cost = config.get("cost", 0)
            energy_cost = config.get("energy_cost", 0)
            
            # Calculate button position
            button_x_start = 1.15 + menu_x_offset
            button_x_end = button_x_start + button_width
            
            # Building button
            button = DirectButton(
                frameSize=(button_x_start, button_x_end, y_pos - button_height/2, y_pos + button_height/2),
                frameColor=(0.2, 0.2, 0.3, 0.8),
                text="",
                command=self.on_building_button_click,
                extraArgs=[building_type],
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Building name with hotkey
            hotkey = config.get("hotkey", "").upper()
            name_with_hotkey = config.get("name", building_type.title())
            if hotkey:
                name_with_hotkey += f" [{hotkey}]"
                
            name_text = OnscreenText(
                text=name_with_hotkey,
                pos=(button_x_start + 0.02, y_pos + 0.02),
                scale=0.035,
                fg=(1, 1, 1, 1),
                align=TextNode.ALeft,
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Building cost
            cost_text = f"{mineral_cost}m"
            if energy_cost > 0:
                cost_text += f" {energy_cost}e"
            
            cost_display = OnscreenText(
                text=cost_text,
                pos=(button_x_end - 0.02, y_pos + 0.02),
                scale=0.035,
                fg=(0.5, 1, 1, 1),
                align=TextNode.ARight,
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Building description
            desc_text = OnscreenText(
                text=config.get("description", ""),
                pos=(button_x_start + 0.02, y_pos - 0.02),
                scale=0.025,
                fg=(0.8, 0.8, 0.8, 1),
                align=TextNode.ALeft,
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Store button references
            self.building_buttons.append({
                'button': button,
                'name_text': name_text,
                'cost_text': cost_display,
                'desc_text': desc_text,
                'building_type': building_type
            })
            
        except Exception as e:
            print(f"Error creating building button for {building_type}: {e}")
    
    def create_research_button(self, tech, y_pos, menu_x_offset=-0.1, button_width=0.7, button_height=0.08):
        """Create a clickable button for a research technology"""
        try:
            # Calculate button position
            button_x_start = 1.15 + menu_x_offset
            button_x_end = button_x_start + button_width
            
            # Research button
            button = DirectButton(
                frameSize=(button_x_start, button_x_end, y_pos - button_height/2, y_pos + button_height/2),
                frameColor=(0.3, 0.2, 0.4, 0.8),
                text="",
                command=self.on_research_button_click,
                extraArgs=[tech.tech_id],
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Research name
            name_text = OnscreenText(
                text=tech.name,
                pos=(button_x_start + 0.02, y_pos + 0.02),
                scale=0.035,
                fg=(1, 1, 1, 1),
                align=TextNode.ALeft,
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Research cost
            cost_text = f"{tech.cost}m {tech.energy_cost}e"
            
            cost_display = OnscreenText(
                text=cost_text,
                pos=(button_x_end - 0.02, y_pos + 0.02),
                scale=0.035,
                fg=(0.8, 0.5, 1, 1),
                align=TextNode.ARight,
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Research description
            desc_text = OnscreenText(
                text=tech.description,
                pos=(button_x_start + 0.02, y_pos - 0.02),
                scale=0.025,
                fg=(0.8, 0.8, 0.8, 1),
                align=TextNode.ALeft,
                parent=self.building_scroll_frame.getCanvas()
            )
            
            # Store button references
            self.research_buttons.append({
                'button': button,
                'name_text': name_text,
                'cost_text': cost_display,
                'desc_text': desc_text,
                'tech_id': tech.tech_id
            })
            
        except Exception as e:
            print(f"Error creating research button for {tech.tech_id}: {e}")
    
    def on_research_button_click(self, tech_id):
        """Handle research button click"""
        try:
            print(f"Research button clicked: {tech_id}")
            if hasattr(self.game_engine, 'research_system'):
                success = self.game_engine.research_system.start_research(
                    tech_id, 
                    self.game_engine.minerals, 
                    self.game_engine.energy
                )
                if success:
                    # Deduct costs
                    tech = self.game_engine.research_system.technologies[tech_id]
                    self.game_engine.minerals -= tech.cost
                    self.game_engine.energy -= tech.energy_cost
                    print(f"✓ Started research: {tech.name}")
                    # Refresh the research tab
                    if self.current_tab == "research":
                        self.populate_research_tab()
        except Exception as e:
            print(f"Error handling research button click: {e}")
    
    def on_building_button_click(self, building_type):
        """Handle building button click"""
        try:
            print(f"Building button clicked: {building_type}")
            
            # Start building construction through game engine
            if hasattr(self.game_engine, 'start_building_construction'):
                success = self.game_engine.start_building_construction(building_type)
                if success:
                    print(f"✓ Started construction mode for {building_type}")
                else:
                    print(f"✗ Failed to start construction for {building_type}")
            
        except Exception as e:
            print(f"Error handling building button click: {e}")
    
    def update_building_menu(self):
        """Update building menu button states based on resources"""
        try:
            if not self.building_buttons:
                return
            
            current_minerals = getattr(self.game_engine, 'minerals', 0)
            current_energy = getattr(self.game_engine, 'energy', 0)
            
            for button_data in self.building_buttons:
                building_type = button_data['building_type']
                
                # Get building config
                building_config = self.game_engine.config.buildings.get("building_types", {}).get(building_type, {})
                mineral_cost = building_config.get("cost", 0)
                energy_cost = building_config.get("energy_cost", 0)
                
                # Check if player can afford this building
                can_afford = current_minerals >= mineral_cost and current_energy >= energy_cost
                
                # Update button appearance
                if can_afford:
                    button_data['button']['frameColor'] = (0.2, 0.4, 0.2, 0.8)  # Green tint
                    button_data['cost_text']['fg'] = (0.5, 1, 1, 1)  # Bright cyan
                else:
                    button_data['button']['frameColor'] = (0.4, 0.2, 0.2, 0.8)  # Red tint
                    button_data['cost_text']['fg'] = (1, 0.5, 0.5, 1)  # Red
                    
        except Exception as e:
            print(f"Error updating building menu: {e}") 