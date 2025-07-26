"""
Building System - Phase 3 Implementation
Manages building construction, power networks, and visual integration
"""

from typing import Dict, List, Optional, Tuple
from ..entities.building import Building, BuildingState
from ..panda3d.entity_visualizer import EntityVisualizer

class BuildingSystem:
    """Manages all buildings, construction, and power networks"""
    
    def __init__(self, base, config, scene_manager):
        self.base = base
        self.config = config
        self.scene_manager = scene_manager
        
        # Building storage
        self.buildings: Dict[str, Building] = {}
        self.buildings_by_type: Dict[str, List[Building]] = {}
        
        # Construction state
        self.selected_building_type = None
        self.preview_building = None
        self.construction_mode = False
        
        # Power network (will be expanded later)
        self.power_blocks = []
        
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
            
        self.construction_mode = False
        self.selected_building_type = None
        print("✓ Construction cancelled")
        
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
        
        # Check distance from other buildings
        min_distance = radius + 15  # Buffer space
        
        for building in self.buildings.values():
            distance = ((x - building.x) ** 2 + (y - building.y) ** 2) ** 0.5
            required_distance = min_distance + building.radius
            
            if distance < required_distance:
                return False, f"Too close to {building.building_type}"
                
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
        
        # Create building
        building = Building(building_type, x, y, self.config)
        
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
        
        # Auto-connect to nearby buildings if possible
        self._auto_connect_building(building)
        
        print(f"✓ Placed {building_type} at ({x:.0f}, {y:.0f}) - Cost: {cost}")
        
        # End construction mode
        self.cancel_construction()
        
        return building
        
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
            
    def update_construction_preview(self, mouse_world_x: float, mouse_world_y: float):
        """Update building placement preview"""
        if not self.construction_mode or not self.selected_building_type:
            return
            
        # Check if placement is valid
        can_place, reason = self.can_place_building(self.selected_building_type, mouse_world_x, mouse_world_y)
        
        # Update preview visual (placeholder for now)
        # In Phase 4, this will show a semi-transparent building preview
        # For Phase 3, we'll just track the validity
        
        return can_place, reason
        
    def select_building_at(self, x: float, y: float) -> Optional[Building]:
        """Select building at world coordinates"""
        for building in self.buildings.values():
            distance = ((x - building.x) ** 2 + (y - building.y) ** 2) ** 0.5
            if distance <= building.radius:
                # Deselect other buildings
                for b in self.buildings.values():
                    b.selected = False
                    
                # Select this building
                building.selected = True
                print(f"✓ Selected {building.building_type} - {building.get_info()}")
                return building
                
        # Deselect all if no building found
        for building in self.buildings.values():
            building.selected = False
            
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
            
        # Remove from storage
        del self.buildings[building_id]
        
        # Remove from type index
        if building.building_type in self.buildings_by_type:
            self.buildings_by_type[building.building_type].remove(building)
            
        print(f"✓ Removed {building.building_type} at ({building.x:.0f}, {building.y:.0f})")
        return True
        
    def update(self, dt: float):
        """Update all buildings"""
        for building in list(self.buildings.values()):
            building.update(dt)
            
            # Remove destroyed buildings
            if building.state == BuildingState.DESTROYED:
                self.remove_building(building.building_id)
                
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
        """Clean up building system"""
        print("Cleaning up building system...")
        
        # Remove all buildings
        for building in list(self.buildings.values()):
            self.remove_building(building.building_id)
            
        self.buildings.clear()
        self.buildings_by_type.clear()
        
        print("✓ Building system cleanup complete") 