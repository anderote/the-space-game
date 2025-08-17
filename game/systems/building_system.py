"""
Building System - Phase 3 Implementation
Manages building construction, power networks, and visual integration
"""

import time
from typing import Dict, List, Optional, Tuple
from ..entities.building import Building, BuildingState
from ..panda3d.entity_visualizer import EntityVisualizer

class BuildingSystem:
    """Manages all buildings, construction, and power networks"""
    
    def __init__(self, base, config, scene_manager, game_engine=None):
        self.base = base
        self.config = config
        self.scene_manager = scene_manager
        self.game_engine = game_engine  # Reference to game engine for resource management
        
        # Building storage
        self.buildings: Dict[str, Building] = {}
        self.buildings_by_type: Dict[str, List[Building]] = {}
        
        # Construction state
        self.selected_building_type = None
        self.preview_building = None
        self.construction_mode = False
        
        # Preview visual elements
        self.preview_visual = None
        self.preview_range_indicator = None
        self.preview_radius_indicators = {}  # Store multiple radius indicators
        
        # Selection tracking
        self.selected_building = None
        self.selected_building_indicators = {}
        
        # Connection healing system
        self.last_heal_time = 0
        self.heal_interval = 5.0  # 5 seconds
        
        # Power network (will be expanded later)
        self.power_network = []
        
    def start_construction(self, building_type: str) -> bool:
        """Start construction mode for a building type"""
        # Check if building type exists in config
        building_types = self.config.buildings.get("building_types", {})
        if building_type not in building_types:
            print(f"✗ Unknown building type: {building_type}")
            return False
            
        self.selected_building_type = building_type
        self.construction_mode = True
        
        # Get cost using the helper method
        cost = self.get_building_cost(building_type)
        minerals_cost = cost.get("minerals", 0)
        energy_cost = cost.get("energy", 0)
        
        print(f"✓ Construction mode: {building_type.title()}")
        print(f"  Cost: {minerals_cost} minerals, {energy_cost} energy")
        
        return True
        
    def cancel_construction(self):
        """Cancel construction mode"""
        if self.preview_building:
            # Remove preview visual
            if self.preview_building.visual_node:
                self.preview_building.visual_node.removeNode()
            self.preview_building = None
            
        # Remove preview visuals
        self._clear_preview_visuals()
            
        self.construction_mode = False
        self.selected_building_type = None
        print("✓ Construction cancelled")
        
    def _clear_preview_visuals(self):
        """Clear building placement preview visuals"""
        if self.preview_visual:
            self.preview_visual.removeNode()
            self.preview_visual = None
            
        if self.preview_range_indicator:
            self.preview_range_indicator.removeNode()
            self.preview_range_indicator = None
            
        # Clear all preview radius indicators
        for indicator in self.preview_radius_indicators.values():
            indicator.removeNode()
        self.preview_radius_indicators.clear()
    
    def _update_power_network_visualization(self):
        """Update power network visualization after building changes"""
        if hasattr(self.scene_manager, 'update_power_network'):
            buildings_list = list(self.buildings.values())
            self.scene_manager.update_power_network(buildings_list)
    
    def _on_building_completed(self, building_type: str):
        """Callback when a building completes construction"""
        print(f"Building completion callback for {building_type}")
        # Update power network visualization when buildings become operational
        self._update_power_network_visualization()
        
        # Add dynamic lighting for completed buildings
        self._add_building_lighting(building_type)
        
        # Force health bar update for all buildings to clean up construction progress bars
        for building in self.buildings.values():
            self._update_building_health_bar(building)
    
    def _add_building_lighting(self, building_type: str):
        """Add dynamic lighting for a specific building type that just completed"""
        # TEMPORARILY DISABLED - dynamic lighting has API compatibility issues
        print(f"✓ Skipping dynamic lighting for {building_type} (temporarily disabled)")
        return
        
        # Find the most recently completed building of this type
        for building in self.buildings.values():
            if (building.building_type == building_type and 
                building.state == BuildingState.OPERATIONAL and 
                not hasattr(building, 'dynamic_light_id')):
                
                # Add dynamic lighting if scene manager supports it
                if (hasattr(self.scene_manager, 'dynamic_lighting') and 
                    self.scene_manager.dynamic_lighting):
                    
                    light_id = self.scene_manager.dynamic_lighting.create_building_light(
                        building.x, building.y, 10, building.building_type, building.state.name
                    )
                    
                    if light_id is not None:
                        building.dynamic_light_id = light_id
                        print(f"✓ Added dynamic lighting to {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
                
                break  # Only light the first matching building
        
    def can_afford_building(self, building_type: str, minerals: int, energy: int) -> bool:
        """Check if player can afford to build"""
        cost = self.get_building_cost(building_type)
        
        minerals_cost = cost.get("minerals", 0)
        energy_cost = cost.get("energy", 0)
        
        return minerals >= minerals_cost and energy >= energy_cost
        
    def get_building_cost(self, building_type: str) -> Dict[str, int]:
        """Get building construction cost"""
        building_config = self.config.buildings.get("building_types", {}).get(building_type, {})
        cost_config = building_config.get("cost", 50)
        
        if isinstance(cost_config, dict):
            return cost_config
        else:
            # Simple number cost means minerals only
            return {"minerals": cost_config, "energy": 0}
        
    def can_place_building(self, building_type: str, x: float, y: float) -> Tuple[bool, str]:
        """Check if building can be placed at position"""
        # Check basic placement validation
        building_config = self.config.buildings.get("building_types", {}).get(building_type, {})
        radius = building_config.get("radius", 25)
        
        # Very permissive placement - only prevent significant overlap
        # Allow buildings to be placed very close to each other and asteroids
        for building in self.buildings.values():
            distance = ((x - building.x) ** 2 + (y - building.y) ** 2) ** 0.5
            # Only prevent significant overlap - allow buildings to nearly touch
            required_distance = (radius + building.radius) * 0.6  # Allow 40% overlap
            
            if distance < required_distance:
                return False, f"Too much overlap with {building.building_type}"
                
        # Check world bounds
        world_width = self.config.game.get("display", {}).get("world_width", 4800)
        world_height = self.config.game.get("display", {}).get("world_height", 2700)
        
        if x < radius or x > world_width - radius or y < radius or y > world_height - radius:
            return False, "Outside world bounds"
            
        return True, "Valid placement"
        
    def place_building(self, building_type: str, x: float, y: float, game_engine) -> Optional[Building]:
        """Place a building at the specified position"""
        # Validate placement
        can_place, reason = self.can_place_building(building_type, x, y)
        if not can_place:
            print(f"✗ Cannot place {building_type}: {reason}")
            return None
            
        # Check affordability
        if not self.can_afford_building(building_type, game_engine.minerals, game_engine.energy):
            print(f"✗ Cannot afford {building_type}")
            return None
            
        # Deduct costs
        cost = self.get_building_cost(building_type)
        game_engine.minerals -= cost.get("minerals", 0)
        game_engine.energy -= cost.get("energy", 0)
        
        # Create the building instance with completion callback
        building = Building(
            building_type=building_type,
            x=x, y=y, 
            config=self.config,
            completion_callback=self._on_building_completed,
            game_engine=game_engine
        )
        
        # Create visual representation
        building.visual_node = self.scene_manager.entity_visualizer.create_building_visual(
            building_type, x, y, building.radius
        )
        
        # Store building
        self.buildings[building.building_id] = building
        
        # Add to type index
        if building_type not in self.buildings_by_type:
            self.buildings_by_type[building_type] = []
        self.buildings_by_type[building_type].append(building)
        
        # Auto-connect to nearby power buildings if this building can connect
        connections_made = 0
        max_connections = building.max_connections
        if max_connections > 0:
            # Find all nearby buildings within connection range
            nearby_buildings = []
            for other_building in self.buildings.values():
                if other_building.building_id != building.building_id:
                    distance = ((building.x - other_building.x) ** 2 + (building.y - other_building.y) ** 2) ** 0.5
                    if distance <= min(building.connection_range, other_building.connection_range):
                        nearby_buildings.append(other_building)
            
            # Sort by distance (closest first)
            nearby_buildings.sort(key=lambda b: ((building.x - b.x) ** 2 + (building.y - b.y) ** 2) ** 0.5)
            
            # Connect to as many as possible within limits
            for other_building in nearby_buildings:
                if connections_made >= max_connections:
                    break
                    
                if building.can_connect_to(other_building):
                    building.connect_to(other_building)
                    connections_made += 1
                    print(f"✓ Connected {building.building_type} to {other_building.building_type}")
            
            if connections_made > 0:
                print(f"  ✓ Auto-connected to {connections_made} nearby buildings")
        
        # Update power network visualization
        self._update_power_network_visualization()
        
        print(f"✓ Placed {building.building_type} at ({x:.0f}, {y:.0f}) - Cost: {building.cost}")
        
        # Create placement effect
        if hasattr(self.scene_manager, 'entity_visualizer'):
            self.scene_manager.entity_visualizer.create_building_placement_effect(x, y)
        
        # End construction mode
        self.cancel_construction()
        
        return building
    
    def get_buildings_under_construction(self) -> List:
        """Get list of buildings currently under construction"""
        from game.entities.building import BuildingState
        return [building for building in self.buildings.values() 
                if building.state == BuildingState.UNDER_CONSTRUCTION]
        
    def _auto_connect_building(self, new_building: Building):
        """Automatically connect new building to nearby compatible buildings"""
        if new_building.max_connections <= 0:
            return
            
        connected_count = 0
        
        # Find nearby buildings within connection range
        for building in self.buildings.values():
            if building == new_building:
                continue
                
            if new_building.can_connect_to(building) and building.can_connect_to(new_building):
                if new_building.connect_to(building):
                    connected_count += 1
                    
                    # Stop if we've reached max connections
                    if connected_count >= new_building.max_connections:
                        break
                        
        if connected_count > 0:
            print(f"  ✓ Auto-connected to {connected_count} nearby buildings")
            
    def update_construction_preview(self, mouse_world_x: float, mouse_world_y: float, 
                                   minerals: int = 600, energy: int = 50):
        """Update building placement preview with visual feedback"""
        if not self.construction_mode or not self.selected_building_type:
            self._clear_preview_visuals()
            return
            
        # Check if placement is valid
        can_place, reason = self.can_place_building(self.selected_building_type, mouse_world_x, mouse_world_y)
        can_afford = self.can_afford_building(self.selected_building_type, minerals, energy)
        
        valid_placement = can_place and can_afford
        
        # Get building configuration
        building_config = self.config.buildings.get("building_types", {}).get(self.selected_building_type, {})
        radius = building_config.get("radius", 25)
        
        # Clear old preview
        self._clear_preview_visuals()
        
        # Create new preview visual
        self.preview_visual = self.scene_manager.entity_visualizer.create_building_visual(
            self.selected_building_type, mouse_world_x, mouse_world_y, radius
        )
        
        if self.preview_visual:
            # Make it semi-transparent and colored based on validity
            if valid_placement:
                self.preview_visual.setColor(0.0, 1.0, 0.0, 0.6)  # Green if valid
            else:
                self.preview_visual.setColor(1.0, 0.0, 0.0, 0.6)  # Red if invalid
                
            self.preview_visual.setTransparency(True)
            
        # Create radius indicators for this building type
        self.preview_radius_indicators = self.scene_manager.entity_visualizer.create_building_radius_indicators(
            self.selected_building_type, building_config, mouse_world_x, mouse_world_y
        )
        
        # Attach indicators to render
        for indicator_type, indicator in self.preview_radius_indicators.items():
            if indicator:
                indicator.reparentTo(self.base.render)
        
        return valid_placement, reason
        
    def update(self, dt):
        """Update all buildings and their logic"""
        # Update all buildings
        for building in self.buildings.values():
            building.update(dt)
            self._update_building_health_bar(building)
        
        # Heal power network connections periodically
        current_time = time.time()
        if current_time - self.last_heal_time >= self.heal_interval:
            self.heal_power_connections()
            self.last_heal_time = current_time

    def heal_power_connections(self):
        """Periodically recalculate and heal power network connections"""
        print("🔧 Healing power network connections...")
        
        # Simple healing: connect buildings that are close to each other
        operational_buildings = [b for b in self.buildings.values() if b.state == BuildingState.OPERATIONAL]
        
        for building in operational_buildings:
            # Skip if already at max connections
            if len(building.connections) >= building.max_connections:
                continue
                
            # Find nearby buildings to connect to
            for other_building in operational_buildings:
                if (other_building.building_id != building.building_id and
                    other_building.building_id not in building.connections and
                    len(other_building.connections) < other_building.max_connections):
                    
                    # Check distance
                    distance = ((building.x - other_building.x)**2 + (building.y - other_building.y)**2)**0.5
                    if distance <= building.connection_range:
                        # Create bidirectional connection
                        building.connections.add(other_building.building_id)
                        other_building.connections.add(building.building_id)
                        print(f"  ✓ Connected {building.building_type} to {other_building.building_type}")
                        
                        # Break if we've reached max connections
                        if len(building.connections) >= building.max_connections:
                            break
        
        # Update power network visualization after healing
        self.scene_manager.update_power_network(list(self.buildings.values()))
        
    def _update_building_health_bar(self, building):
        """Update building health bar visibility and progress"""
        should_show = building.should_show_health_bar()
        
        # Create health bar if needed and not exists
        if should_show and not building.health_bar:
            building.health_bar = self.scene_manager.entity_visualizer.create_health_bar()
            if building.health_bar:
                # Position at bottom of the building using radius offset
                building.health_bar.reparentTo(self.base.render)
                # Get building radius for proper positioning
                building_config = self.config.buildings.get("building_types", {}).get(building.building_type, {})
                building_radius = building_config.get("radius", 20)
                # Position below the building at its bottom edge (radius distance down)
                health_bar_y_offset = building_radius + 10  # Add small gap below building
                building.health_bar.setPos(building.x, building.y - health_bar_y_offset, 1)  # Slightly above ground
                building.health_bar.setScale(1.0)  # Ensure proper scale
        
        # Update health bar progress and visibility
        if building.health_bar:
            if should_show:
                progress = building.get_health_progress()
                is_construction = building.is_construction_progress()
                self.scene_manager.entity_visualizer.update_health_bar(
                    building.health_bar, progress, is_construction
                )
                building.health_bar.show()
            else:
                # Hide health bar when it shouldn't be shown (full health, asteroids, etc.)
                building.health_bar.hide()
        
        # Update building visual effects for construction
        if building.visual_node:
            if building.is_construction_progress():
                # Add flashing gray effect during construction
                self._add_construction_flashing(building)
            else:
                # Remove flashing effect when construction complete
                self._remove_construction_flashing(building)
        
        # Hide health bar if not needed
        elif building.health_bar and not should_show:
            building.health_bar.hide()
        
    def _add_construction_flashing(self, building):
        """Add flashing gray effect to building under construction"""
        if building.visual_node and not hasattr(building, '_flashing_task'):
            import time
            from direct.task import Task
            
            # Create a flashing effect
            def flash_task(task):
                if building.visual_node:
                    # Slow flash between normal color and gray
                    flash_phase = (time.time() * 2) % 2  # 2-second cycle
                    if flash_phase < 1:
                        # Normal phase - slightly gray
                        building.visual_node.setColorScale(0.7, 0.7, 0.7, 1.0)
                    else:
                        # Flash phase - more gray
                        building.visual_node.setColorScale(0.4, 0.4, 0.4, 1.0)
                return task.cont if building.is_construction_progress() else task.done
            
            # Start the flashing task
            building._flashing_task = self.base.taskMgr.add(flash_task, f"flash_{building.building_id}")
    
    def _remove_construction_flashing(self, building):
        """Remove flashing effect from completed building"""
        if hasattr(building, '_flashing_task'):
            self.base.taskMgr.remove(building._flashing_task)
            delattr(building, '_flashing_task')
            
        # Restore normal color
        if building.visual_node:
            building.visual_node.setColorScale(1.0, 1.0, 1.0, 1.0)
            
    def select_building(self, building: 'Building'):
        """Select a building and show its radius indicators"""
        # Clear previous selection first
        if self.selected_building:
            self.clear_building_selection()
        
        self.selected_building = building
        
        # Show building info in HUD
        if hasattr(self, 'hud_system') and self.hud_system:
            self.hud_system.show_building_info(building)
        
        # Create radius indicators using effective ranges
        building_config = self.config.buildings.get("building_types", {}).get(building.building_type, {})
        self.selected_building_indicators = self.scene_manager.entity_visualizer.create_building_radius_indicators(
            building.building_type, building_config, building.x, building.y, building
        )
        
        # Attach indicators to render
        for indicator_type, indicator in self.selected_building_indicators.items():
            if indicator:
                indicator.reparentTo(self.base.render)
    
    def clear_building_selection(self):
        """Clear building selection and hide info panel"""
        if self.selected_building:
            self.selected_building.selected = False
        
        # Clear selection indicators
        if self.selected_building_indicators:
            for indicator_type, indicator in self.selected_building_indicators.items():
                if indicator:
                    indicator.removeNode()
            self.selected_building_indicators = {}
        
        self.selected_building = None
        
        # Hide building info in HUD
        if hasattr(self, 'hud_system') and self.hud_system:
            self.hud_system.hide_building_info()
    
    def get_building_at_position(self, x: float, y: float, tolerance: float = 30.0) -> Optional[Building]:
        """Find a building at the given position within tolerance"""
        for building in self.buildings.values():
            distance = ((building.x - x) ** 2 + (building.y - y) ** 2) ** 0.5
            if distance <= tolerance:
                return building
        return None
        
    def get_selected_building(self) -> Optional[Building]:
        """Get currently selected building"""
        for building in self.buildings.values():
            if building.selected:
                return building
        return None
        
    def remove_building(self, building_id: str) -> bool:
        """Remove a building from the system"""
        if building_id not in self.buildings:
            return False
            
        building = self.buildings[building_id]
        
        # Disconnect from all connected buildings
        for connected_id in building.connections.copy():
            if connected_id in self.buildings:
                building.disconnect_from(self.buildings[connected_id])
                
        # Remove visual
        if building.visual_node:
            building.visual_node.removeNode()
            building.visual_node = None
            
        # Clean up flashing task
        if hasattr(building, '_flashing_task'):
            self.base.taskMgr.remove(building._flashing_task)
            delattr(building, '_flashing_task')
            
        # Clean up health bar
        if building.health_bar:
            building.health_bar.removeNode()
            building.health_bar = None
                
        # Remove from storage
        del self.buildings[building_id]
        
        # Remove from type index
        if building.building_type in self.buildings_by_type:
            self.buildings_by_type[building.building_type].remove(building)
            
        print(f"✓ Removed {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
        return True
        
    def get_buildings_in_radius(self, x: float, y: float, radius: float) -> List[Building]:
        """Get all buildings within a radius of a position"""
        buildings_in_range = []
        
        for building in self.buildings.values():
            distance = ((x - building.x) ** 2 + (y - building.y) ** 2) ** 0.5
            if distance <= radius:
                buildings_in_range.append(building)
                
        return buildings_in_range
        
    def get_buildings_by_type(self, building_type: str) -> List[Building]:
        """Get all buildings of a specific type"""
        return self.buildings_by_type.get(building_type, [])
        
    def get_total_power_generation(self) -> int:
        """Get total power generation from all buildings"""
        total = 0
        for building in self.buildings.values():
            if building.state == BuildingState.OPERATIONAL and building.powered:
                total += building.power_generation
        return total
        
    def get_total_power_consumption(self) -> int:
        """Get total power consumption from all buildings"""
        total = 0
        for building in self.buildings.values():
            if building.state == BuildingState.OPERATIONAL:
                total += building.power_consumption
        return total
        
    def get_building_count(self) -> int:
        """Get total number of buildings"""
        return len(self.buildings)
        
    def cleanup(self):
        """Clean up all buildings and visual elements"""
        print("Cleaning up building system...")
        
        # Clear preview visuals
        self._clear_preview_visuals()
        
        # Clear building selection
        self.clear_building_selection()
        
        # Remove all buildings and their visuals
        for building in list(self.buildings.values()):
            if building.visual_node:
                building.visual_node.removeNode()
                building.visual_node = None
            
            # Clean up health bar
            if building.health_bar:
                building.health_bar.removeNode()
                building.health_bar = None
                
            print(f"✓ Removed {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
        
        # Clear all storage
        self.buildings.clear()
        self.buildings_by_type.clear()
        
        print("✓ Building system cleanup complete") 

    def recycle_building(self, building) -> bool:
        """Recycle a building for 75% resource refund"""
        if not building or not building.can_be_recycled():
            print("Cannot recycle: Building is destroyed")
            return False
        
        # Calculate recycle value
        recycle_value = building.get_recycle_value()
        
        # If building is under construction, also refund consumed energy partially
        energy_refund = 0
        if building.state == BuildingState.UNDER_CONSTRUCTION:
            # Refund unconsumed energy for construction/upgrade
            energy_remaining = building.total_construction_energy - building.construction_energy_consumed
            energy_refund = energy_remaining * 0.75  # 75% of remaining energy
            
            if building.is_upgrading:
                print(f"♻️ Cancelled upgrade and recycled {building.building_type} (Level {building.level})")
            else:
                print(f"♻️ Cancelled construction and recycled {building.building_type}")
        else:
            print(f"♻️ Recycled {building.building_type} (Level {building.level})")
        
        # Apply refunds
        self.game_engine.minerals += recycle_value.get("minerals", 0)
        if energy_refund > 0:
            self.game_engine.energy += energy_refund
            print(f"  Refunded: {recycle_value.get('minerals', 0)} minerals, {energy_refund:.1f} energy")
        else:
            print(f"  Refunded: {recycle_value.get('minerals', 0)} minerals")
        
        # Remove building from system
        if building.building_id in self.buildings:
            del self.buildings[building.building_id]
        
        # Remove from type index
        if building.building_type in self.buildings_by_type:
            if building in self.buildings_by_type[building.building_type]:
                self.buildings_by_type[building.building_type].remove(building)
        
        # Remove visual representation including health bar
        if hasattr(building, 'visual_node') and building.visual_node:
            building.visual_node.removeNode()
        if hasattr(building, 'health_bar') and building.health_bar:
            building.health_bar.removeNode()
        
        # Use the game engine's remove_building method for proper cleanup
        self.game_engine.remove_building(building)
        
        # Update power network visualization
        self.scene_manager.update_power_network(list(self.buildings.values()))
        
        return True

    def disable_building(self, building) -> bool:
        """Toggle building disable state"""
        if not building:
            return False
        
        return building.toggle_disable()

    def upgrade_building(self, building) -> bool:
        """Upgrade a building to the next level"""
        if not building or building.level >= 5:
            print("Cannot upgrade: Building is already at max level")
            return False
            
        # Calculate upgrade costs
        building_config = self.config.buildings.get("building_types", {}).get(building.building_type, {})
        base_costs = building_config.get('cost', {'minerals': 50, 'energy': 0})
        
        if isinstance(base_costs, dict):
            base_mineral_cost = base_costs.get('minerals', 50)
        else:
            base_mineral_cost = base_costs
            
        mineral_cost = base_mineral_cost * building.level
        energy_cost = (base_mineral_cost * building.level) // 4
        
        # Check if player can afford the minerals (energy will be consumed over time)
        if self.game_engine.minerals < mineral_cost:
            print(f"Cannot upgrade: Need {mineral_cost} minerals (have {self.game_engine.minerals})")
            return False
        
        # Only consume minerals upfront, energy will be consumed during upgrade construction
        self.game_engine.minerals -= mineral_cost
        
        # Store upgrade info for gradual energy consumption
        old_level = building.level
        old_max_health = building.max_health
        old_current_health = building.current_health
        
        # Apply level increase
        building.level += 1
        
        # Calculate new health and scale current health proportionally
        new_max_health = building.get_effective_health()
        health_scale_factor = new_max_health / old_max_health if old_max_health > 0 else 1.0
        building.max_health = new_max_health
        building.current_health = old_current_health * health_scale_factor
        
        # Update energy-related stats for immediate effect after upgrade completes
        if building.building_type == "solar":
            building.power_generation = building.get_effective_energy_generation()
            building.energy_storage = building.get_effective_energy_capacity()
        elif building.building_type == "battery":
            building.energy_storage = building.get_effective_energy_capacity()
        
        # Set up upgrade construction process
        building.state = BuildingState.UNDER_CONSTRUCTION
        building.construction_progress = 0.0
        building.construction_energy_consumed = 0.0
        building.total_construction_energy = energy_cost  # Energy to be consumed over time
        building.is_upgrading = True  # Flag to track upgrade vs new construction
        
        print(f"✓ Started upgrade of {building.building_type} from Level {old_level} to Level {building.level}")
        print(f"  Cost: {mineral_cost} minerals, {energy_cost} energy (will be consumed over time)")
        print(f"  New stats - Health: {building.current_health:.0f}/{new_max_health:.0f}, Range: {building.get_effective_range():.0f}")
        
        if building.building_type == "miner":
            print(f"  Mining rate: {building.get_effective_mining_rate():.1f}, Energy/zap: {building.get_effective_mining_energy_cost():.1f}")
        elif building.building_type == "solar":
            print(f"  Energy generation: {building.get_effective_energy_generation():.1f}")
        
        return True 