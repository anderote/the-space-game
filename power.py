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
        
    def get_building_id(self, building):
        """Get a unique ID for a building (using memory address)."""
        return id(building)
    
    def get_connection_limit(self, building):
        """Get the maximum number of connections for a building type."""
        # Defense and mining nodes have limited connections
        if building.type in ['turret', 'laser', 'superlaser', 'miner']:
            return 2
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
        # Try to connect every building to every other nearby building
        for i, building1 in enumerate(self.buildings):
            for j, building2 in enumerate(self.buildings):
                if i < j:  # Avoid duplicate connections
                    # Check if they're within range and not already connected
                    distance = math.sqrt((building1.x - building2.x) ** 2 + (building1.y - building2.y) ** 2)
                    if distance <= self.power_range:
                        building1_id = self.get_building_id(building1)
                        building2_id = self.get_building_id(building2)
                        
                        # Check if already connected
                        already_connected = (building1_id in self.building_connections and 
                                           building2 in self.building_connections[building1_id])
                        
                        if not already_connected:
                            self.add_connection(building1, building2)

    def update(self):
        """Update the power grid connections and propagate power."""
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
        
        # Power propagation
        self.propagate_power()
    
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