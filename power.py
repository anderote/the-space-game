"""
Power grid and connection logic for Space Game Clone.
"""
from collections import deque, defaultdict
import math

class PowerGrid:
    def __init__(self, buildings, base_pos, power_range=150):
        self.buildings = buildings
        self.base_pos = base_pos
        self.power_range = power_range
        self.connections = []  # List of (building1, building2) tuples
        self.building_connections = defaultdict(list)  # Building -> list of connected buildings
        
        # Connection limits per building type
        self.connection_limits = {
            'connector': 6,
            'turret': 1,      # defense nodes
            'laser': 1,       # defense nodes  
            'superlaser': 1,  # defense nodes
            'miner': 1,       # mining nodes
            'solar': 4,       # other nodes
            'battery': 4,     # other nodes
            'repair': 4,      # other nodes
            'converter': 4    # other nodes
        }

    def get_connection_limit(self, building):
        """Get the maximum number of connections for a building type."""
        return self.connection_limits.get(building.type, 4)
    
    def can_connect(self, building1, building2):
        """Check if two buildings can be connected."""
        # Calculate distance
        distance = math.sqrt((building1.x - building2.x) ** 2 + (building1.y - building2.y) ** 2)
        if distance > self.power_range:
            return False
        
        # Check connection limits
        current_connections_1 = len(self.building_connections[building1])
        current_connections_2 = len(self.building_connections[building2])
        
        limit_1 = self.get_connection_limit(building1)
        limit_2 = self.get_connection_limit(building2)
        
        return current_connections_1 < limit_1 and current_connections_2 < limit_2
    
    def add_connection(self, building1, building2):
        """Add a connection between two buildings if possible."""
        if self.can_connect(building1, building2):
            # Check if already connected
            if building2 not in self.building_connections[building1]:
                self.building_connections[building1].append(building2)
                self.building_connections[building2].append(building1)
                self.connections.append((building1, building2))
                return True
        return False
    
    def remove_connection(self, building1, building2):
        """Remove a connection between two buildings."""
        if building2 in self.building_connections[building1]:
            self.building_connections[building1].remove(building2)
            self.building_connections[building2].remove(building1)
            # Remove from connections list
            self.connections = [(b1, b2) for b1, b2 in self.connections 
                              if not ((b1 == building1 and b2 == building2) or 
                                     (b1 == building2 and b2 == building1))]
    
    def remove_building(self, building):
        """Remove a building and all its connections."""
        # Remove all connections involving this building
        connected_buildings = self.building_connections[building].copy()
        for connected in connected_buildings:
            self.remove_connection(building, connected)
        
        # Remove from building_connections
        if building in self.building_connections:
            del self.building_connections[building]
    
    def find_nearest_connections(self, new_building):
        """Find the best connections for a new building."""
        # Get all potential connections within range
        potential_connections = []
        
        for existing in self.buildings:
            if existing != new_building:
                distance = math.sqrt((new_building.x - existing.x) ** 2 + (new_building.y - existing.y) ** 2)
                if distance <= self.power_range:
                    potential_connections.append((distance, existing))
        
        # Sort by distance
        potential_connections.sort(key=lambda x: x[0])
        
        # Try to connect to the nearest buildings, respecting connection limits
        new_building_limit = self.get_connection_limit(new_building)
        connections_made = 0
        
        for distance, existing in potential_connections:
            if connections_made >= new_building_limit:
                break
            
            if self.can_connect(new_building, existing):
                self.add_connection(new_building, existing)
                connections_made += 1
                
                # Prioritize connecting to powered buildings
                if existing.powered:
                    break

    def update(self):
        """Update the power grid connections and propagate power."""
        # Clean up connections for buildings that no longer exist
        valid_buildings = set(self.buildings)
        
        # Remove connections to non-existent buildings
        self.connections = [(b1, b2) for b1, b2 in self.connections 
                          if b1 in valid_buildings and b2 in valid_buildings]
        
        # Clean up building_connections dict
        buildings_to_remove = []
        for building in self.building_connections:
            if building not in valid_buildings:
                buildings_to_remove.append(building)
            else:
                # Clean up this building's connection list
                self.building_connections[building] = [b for b in self.building_connections[building] 
                                                     if b in valid_buildings]
        
        for building in buildings_to_remove:
            del self.building_connections[building]
        
        # Auto-connect new buildings that don't have connections yet
        for building in self.buildings:
            if building not in self.building_connections or len(self.building_connections[building]) == 0:
                self.find_nearest_connections(building)
        
        # Power propagation
        self.propagate_power()
    
    def propagate_power(self):
        """Propagate power through the network using BFS."""
        # First, set all buildings to unpowered
        for building in self.buildings:
            building.powered = False
        
        # Start BFS from power sources (solar panels and batteries)
        queue = deque()
        powered_buildings = set()
        
        for building in self.buildings:
            if building.type in ['solar', 'battery']:
                building.powered = True
                powered_buildings.add(building)
                queue.append(building)
        
        # Propagate power through connections
        while queue:
            current_building = queue.popleft()
            
            # Power all connected buildings
            for connected_building in self.building_connections[current_building]:
                if connected_building not in powered_buildings:
                    connected_building.powered = True
                    powered_buildings.add(connected_building)
                    queue.append(connected_building)

    def get_powered_buildings(self):
        """Get list of all powered buildings."""
        return [b for b in self.buildings if b.powered]

    def get_connections(self):
        """Returns list of (x1, y1, x2, y2) for drawing connections."""
        return [(b1.x, b1.y, b2.x, b2.y) for b1, b2 in self.connections]
    
    def get_building_info(self, building):
        """Get connection info for a building."""
        connections = len(self.building_connections[building])
        limit = self.get_connection_limit(building)
        return {
            'connections': connections,
            'limit': limit,
            'powered': building.powered,
            'connected_to': [b.type for b in self.building_connections[building]]
        } 