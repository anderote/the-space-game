"""
Panda3D HUD System - Phase 2 Implementation
Enhanced resource display with transparent background and energy bar
"""

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import TextNode, CardMaker, NodePath
from game.entities.building import BuildingState

class HUDSystem:
    """Manages on-screen display of game information"""
    
    def __init__(self, base, game_engine):
        self.base = base
        self.game_engine = game_engine
        
        # HUD elements
        self.hud_elements = {}
        
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
            frameSize=(-1.98, -1.3, -0.25, 0.25),  # Much smaller: width reduced from -0.2 to -1.3, height reduced from ±0.4 to ±0.25
            frameColor=(0, 0, 0, 0.4),  # Semi-transparent black
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        self.building_panel.hide()
        
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
        
        # Building menu panel (right side) - Command & Conquer style - 50% narrower
        self.building_menu_panel = DirectFrame(
            frameSize=(1.49, 1.98, -0.95, 0.95),  # Reduced width from (1.0, 1.98) to (1.49, 1.98) - 50% narrower
            frameColor=(0.1, 0.1, 0.1, 0.6),  # Dark semi-transparent background
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        
        # Building menu title
        self.building_menu_title = OnscreenText(
            text="BUILD MENU",
            pos=(1.735, 0.85),  # Adjusted center position for narrower panel
            scale=0.045,
            fg=(1, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.base.aspect2d
        )
        
        # Building menu items
        self.building_menu_items = []
        building_types = [
            ("Q - Solar", "50m", "Power Generation"),
            ("E - Connector", "30m", "Power Distribution"), 
            ("B - Battery", "80m", "Energy Storage"),
            ("M - Miner", "100m", "Resource Collection"),
            ("T - Turret", "150m", "Base Defense"),
            ("L - Laser", "200m", "Heavy Defense"),
            ("Y - Superlaser", "400m", "Ultimate Defense"),
            ("H - Repair", "120m", "Building Repair"),
            ("F - Force Field", "250m", "Area Protection"),
            ("X - Missile", "180m", "Long Range Defense"),
            ("Z - Hangar", "300m", "Unit Production"),
            ("V - Converter", "200m", "Energy to Minerals")
        ]
        
        y_start = 0.75
        for i, (name, cost, desc) in enumerate(building_types):
            y_pos = y_start - (i * 0.14)  # Spacing between items
            
            # Building name and hotkey
            name_text = OnscreenText(
                text=name,
                pos=(1.4, y_pos),  # Moved from 1.05 to 1.52 for narrower panel
                scale=0.04,
                fg=(1, 1, 1, 1),
                align=TextNode.ALeft,
                parent=self.base.aspect2d
            )
            
            # Building cost
            cost_text = OnscreenText(
                text=cost,
                pos=(1.85, y_pos),  # Moved from 1.65 to 1.85 for narrower panel
                scale=0.04,
                fg=(0.5, 1, 1, 1),
                align=TextNode.ALeft,
                parent=self.base.aspect2d
            )
            
            # Building description
            desc_text = OnscreenText(
                text=desc,
                pos=(1.5, y_pos - 0.03),  # Moved from 1.05 to 1.52 for narrower panel
                scale=0.03,
                fg=(0.8, 0.8, 0.8, 1),
                align=TextNode.ALeft,
                parent=self.base.aspect2d
            )
            
            self.building_menu_items.extend([name_text, cost_text, desc_text])
        
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
            
        # Get building configuration
        building_config = self.game_engine.config.buildings.get("building_types", {}).get(building.building_type, {})
        
        # Building name and level
        level = getattr(building, 'level', 1)
        self.building_info['name']['text'] = f"{building_config.get('name', building.building_type.title())}"
        self.building_info['level']['text'] = f"Level: {level}"
        
        # Health information
        health = building.health
        max_health = building.max_health
        health_percent = (health / max_health * 100) if max_health > 0 else 0
        self.building_info['health']['text'] = f"Health: {health:.0f}/{max_health:.0f} ({health_percent:.0f}%)"
        
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
        
        # Action shortcuts
        if level < 5:
            # Fix: Get the mineral cost from the building configuration properly
            building_costs = building_config.get('cost', {'minerals': 50, 'energy': 0})
            if isinstance(building_costs, dict):
                mineral_cost = building_costs.get('minerals', 50)
            else:
                mineral_cost = building_costs  # Fallback if it's just a number
            upgrade_cost = mineral_cost * level
            actions_text = f"[X] Recycle 50%\n[Z] Disable\n[U] Upgrade ({upgrade_cost}m)"
        else:
            actions_text = f"[X] Recycle 50%\n[Z] Disable\nMAX LEVEL"
        self.building_info['actions']['text'] = actions_text
        
    def hide_building_info(self):
        """Hide building information panel"""
        self.building_panel.hide()
        for element in self.building_info.values():
            element.hide()
            
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