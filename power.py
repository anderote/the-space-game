"""
Power grid and connection logic for Space Game Clone.
Simplified system: nodes automatically connect to nearby nodes.
"""
from collections import deque
import math

class PowerGrid:
    def __init__(self, buildings, base_pos, power_range=150):
        self.buildings = buildings
        self.base_pos = base_pos
        self.power_range = power_range
        self.connections = []  # List of (building1, building2) tuples
        self.building_connections = {}  # Building id -> list of connected building objects
        self.last_full_update = 0  # Frame counter for periodic full updates
        self.full_update_interval = 300  # Recalculate every 5 seconds (at 60fps)
        
    def get_building_id(self, building):
        """Get a unique ID for a building (using memory address)."""
        return id(building)
    
    def get_connection_limit(self, building):
        """Get the maximum number of connections for a building type."""
        # Defense and mining nodes have only 1 connection
        if building.type in ['turret', 'laser', 'superlaser', 'miner', 'missile_launcher']:
            return 1
        # Hangars can have 4 connections (need more power for ship operations)
        elif building.type == 'hangar':
            return 4
        # All other nodes can have up to 6 connections
        return 6
    
    def can_connect(self, building1, building2):
        """Check if two buildings can be connected."""
        # Calculate distance
        distance = math.sqrt((building1.x - building2.x) ** 2 + (building1.y - building2.y) ** 2)
        if distance > self.power_range:
            return False
        
        # Check connection limits
        building1_id = self.get_building_id(building1)
        building2_id = self.get_building_id(building2)
        
        current_connections_1 = len(self.building_connections.get(building1_id, []))
        current_connections_2 = len(self.building_connections.get(building2_id, []))
        
        limit_1 = self.get_connection_limit(building1)
        limit_2 = self.get_connection_limit(building2)
        
        return current_connections_1 < limit_1 and current_connections_2 < limit_2
    
    def add_connection(self, building1, building2):
        """Add a connection between two buildings if possible."""
        if self.can_connect(building1, building2):
            building1_id = self.get_building_id(building1)
            building2_id = self.get_building_id(building2)
            
            # Initialize connection lists if they don't exist
            if building1_id not in self.building_connections:
                self.building_connections[building1_id] = []
            if building2_id not in self.building_connections:
                self.building_connections[building2_id] = []
            
            # Check if already connected
            if building2 not in self.building_connections[building1_id]:
                self.building_connections[building1_id].append(building2)
                self.building_connections[building2_id].append(building1)
                self.connections.append((building1, building2))
                return True
        return False
    
    def remove_connection(self, building1, building2):
        """Remove a connection between two buildings."""
        building1_id = self.get_building_id(building1)
        building2_id = self.get_building_id(building2)
        
        if (building1_id in self.building_connections and 
            building2 in self.building_connections[building1_id]):
            self.building_connections[building1_id].remove(building2)
            self.building_connections[building2_id].remove(building1)
            # Remove from connections list
            self.connections = [(b1, b2) for b1, b2 in self.connections 
                              if not ((b1 == building1 and b2 == building2) or 
                                     (b1 == building2 and b2 == building1))]
    
    def remove_building(self, building):
        """Remove a building and all its connections."""
        building_id = self.get_building_id(building)
        
        # Remove all connections involving this building
        if building_id in self.building_connections:
            connected_buildings = self.building_connections[building_id].copy()
            for connected in connected_buildings:
                self.remove_connection(building, connected)
            
            # Remove from building_connections
            del self.building_connections[building_id]
    
    def auto_connect_all(self):
        """Automatically connect all buildings that can be connected."""
        # First, try to connect connectors to everything they can reach
        connectors = [b for b in self.buildings if b.type == 'connector']
        other_buildings = [b for b in self.buildings if b.type != 'connector']
        
        # Connect connectors to nearby buildings first (they have 6 connection capacity)
        for connector in connectors:
            connector_id = self.get_building_id(connector)
            current_connections = len(self.building_connections.get(connector_id, []))
            
            if current_connections < self.get_connection_limit(connector):
                # Find nearby buildings to connect to
                nearby_buildings = []
                for building in self.buildings:
                    if building != connector:
                        distance = math.sqrt((connector.x - building.x) ** 2 + (connector.y - building.y) ** 2)
                        if distance <= self.power_range:
                            building_id = self.get_building_id(building)
                            
                            # Check if already connected
                            already_connected = (connector_id in self.building_connections and 
                                               building in self.building_connections[connector_id])
                            
                            # Check if the other building has room for connections
                            other_current_connections = len(self.building_connections.get(building_id, []))
                            other_limit = self.get_connection_limit(building)
                            
                            if not already_connected and other_current_connections < other_limit:
                                nearby_buildings.append((distance, building))
                
                # Sort by distance and connect to closest buildings first
                nearby_buildings.sort(key=lambda x: x[0])
                connections_to_make = min(
                    len(nearby_buildings), 
                    self.get_connection_limit(connector) - current_connections
                )
                
                for i in range(connections_to_make):
                    _, building = nearby_buildings[i]
                    self.add_connection(connector, building)
        
        # Then, connect other buildings to each other if they have capacity
        for i, building1 in enumerate(other_buildings):
            for j, building2 in enumerate(other_buildings):
                if i < j:  # Avoid duplicate connections
                    # Check if they're within range and both have capacity
                    distance = math.sqrt((building1.x - building2.x) ** 2 + (building1.y - building2.y) ** 2)
                    if distance <= self.power_range:
                        building1_id = self.get_building_id(building1)
                        building2_id = self.get_building_id(building2)
                        
                        # Check if already connected
                        already_connected = (building1_id in self.building_connections and 
                                           building2 in self.building_connections[building1_id])
                        
                        if not already_connected:
                            # Check if both buildings have room for more connections
                            b1_connections = len(self.building_connections.get(building1_id, []))
                            b2_connections = len(self.building_connections.get(building2_id, []))
                            b1_limit = self.get_connection_limit(building1)
                            b2_limit = self.get_connection_limit(building2)
                            
                            if b1_connections < b1_limit and b2_connections < b2_limit:
                                self.add_connection(building1, building2)

    def update(self):
        """Update the power grid connections and propagate power."""
        self.last_full_update += 1
        
        # Perform full recalculation periodically to ensure connectivity
        if self.last_full_update >= self.full_update_interval:
            self.last_full_update = 0
            self.full_recalculate()
        else:
            # Regular maintenance update
            self.incremental_update()
        
        # Always propagate power after connections are updated
        self.propagate_power()
    
    def incremental_update(self):
        """Perform quick incremental updates."""
        # Clean up connections for buildings that no longer exist
        valid_buildings = self.buildings
        
        # Remove connections to non-existent buildings
        self.connections = [(b1, b2) for b1, b2 in self.connections 
                          if b1 in valid_buildings and b2 in valid_buildings]
        
        # Clean up building_connections dict
        valid_building_ids = {self.get_building_id(b) for b in valid_buildings}
        
        building_ids_to_remove = []
        for building_id in list(self.building_connections.keys()):
            if building_id not in valid_building_ids:
                building_ids_to_remove.append(building_id)
            else:
                # Clean up this building's connection list
                self.building_connections[building_id] = [b for b in self.building_connections[building_id] 
                                                        if b in valid_buildings]
        
        for building_id in building_ids_to_remove:
            del self.building_connections[building_id]
        
        # Auto-connect all buildings that can be connected
        self.auto_connect_all()
    
    def full_recalculate(self):
        """Perform complete recalculation of all connections."""
        print("🔌 Performing full power grid recalculation...")
        
        # Clear all existing connections
        self.connections = []
        self.building_connections = {}
        
        # Rebuild all connections from scratch
        self.auto_connect_all()
    
    def propagate_power(self):
        """Propagate power through the network using BFS."""
        # First, set all buildings to unpowered
        for building in self.buildings:
            building.powered = False
        
        # Start BFS from power sources (solar panels and batteries)
        queue = deque()
        powered_buildings = []
        
        for building in self.buildings:
            if building.type in ['solar', 'battery']:
                building.powered = True
                powered_buildings.append(building)
                queue.append(building)
        
        # Propagate power through connections
        while queue:
            current_building = queue.popleft()
            current_building_id = self.get_building_id(current_building)
            
            # Power all connected buildings
            if current_building_id in self.building_connections:
                for connected_building in self.building_connections[current_building_id]:
                    if connected_building not in powered_buildings:
                        connected_building.powered = True
                        powered_buildings.append(connected_building)
                        queue.append(connected_building)

    def get_powered_buildings(self):
        """Get list of all powered buildings."""
        return [b for b in self.buildings if b.powered]

    def get_connections(self):
        """Returns list of (x1, y1, x2, y2) for drawing connections."""
        return [(b1.x, b1.y, b2.x, b2.y) for b1, b2 in self.connections]
    
    def get_building_info(self, building):
        """Get connection info for a building."""
        building_id = self.get_building_id(building)
        connections = len(self.building_connections.get(building_id, []))
        limit = self.get_connection_limit(building)
        connected_buildings = self.building_connections.get(building_id, [])
        return {
            'connections': connections,
            'limit': limit,
            'powered': building.powered,
            'connected_to': [b.type for b in connected_buildings]
        } 