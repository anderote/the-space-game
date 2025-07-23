"""
Power grid and connection logic for Space Game Clone.
"""
from collections import deque, defaultdict

class PowerGrid:
    def __init__(self, buildings, base_pos, power_range=150, max_connections=6):
        self.buildings = buildings
        self.base_pos = base_pos
        self.power_range = power_range
        self.max_connections = max_connections
        self.connections = []

    def update(self):
        # Build graph using indices instead of objects
        graph = defaultdict(list)
        self.connections = []
        
        for i, connector in enumerate(self.buildings):
            if connector.type == 'connector':
                others = sorted([j for j, ob in enumerate(self.buildings) if j != i], 
                              key=lambda j: ((connector.x - self.buildings[j].x) ** 2 + (connector.y - self.buildings[j].y) ** 2))[:self.max_connections]
                for j in others:
                    ob = self.buildings[j]
                    dist2 = (connector.x - ob.x) ** 2 + (connector.y - ob.y) ** 2
                    if dist2 < self.power_range ** 2:
                        graph[i].append(j)
                        graph[j].append(i)
                        # Store building objects, not indices
                        self.connections.append((connector, ob))
        
        # Power propagation using indices
        queue = deque()
        powered_indices = set()
        
        # First, set all buildings to unpowered
        for b in self.buildings:
            b.powered = False
        
        # Then power up solars and batteries
        for i, b in enumerate(self.buildings):
            if b.type in ['solar', 'battery']:
                b.powered = True
                powered_indices.add(i)
                queue.append(i)
        
        # Propagate power through connections
        while queue:
            current_idx = queue.popleft()
            for neighbor_idx in graph[current_idx]:
                if neighbor_idx not in powered_indices:
                    neighbor = self.buildings[neighbor_idx]
                    neighbor.powered = True
                    powered_indices.add(neighbor_idx)
                    queue.append(neighbor_idx)

    def get_powered_buildings(self):
        return [b for b in self.buildings if b.powered]

    def get_connections(self):
        # Returns list of (x1, y1, x2, y2) for drawing
        return [(a.x, a.y, b.x, b.y) for a, b in self.connections] 