"""
Panda3D Entity Visualizer - Phase 2 Implementation
Creates simple 3D representations of game entities
"""

from panda3d.core import CardMaker, CullFaceAttrib
from direct.actor.Actor import Actor
import math

class EntityVisualizer:
    """Creates and manages 3D visual representations of game entities"""
    
    def __init__(self, base):
        self.base = base
        self.entity_nodes = {}
        self.test_entities = []
        
        # Colors for different entity types
        self.building_colors = {
            'starting_base': (0.2, 0.4, 0.8, 1.0),    # Blue
            'solar': (1.0, 0.8, 0.0, 1.0),           # Yellow
            'connector': (0.0, 0.8, 1.0, 1.0),       # Cyan
            'battery': (0.0, 1.0, 0.0, 1.0),         # Green
            'miner': (0.6, 0.4, 0.2, 1.0),           # Brown
            'turret': (1.0, 0.2, 0.2, 1.0),          # Red
            'laser': (1.0, 0.4, 0.4, 1.0),           # Light Red
            'superlaser': (1.0, 0.0, 1.0, 1.0),      # Magenta
            'repair': (0.0, 1.0, 0.5, 1.0),          # Light Green
            'hangar': (0.4, 0.6, 1.0, 1.0),          # Light Blue
            'force_field': (0.0, 0.8, 1.0, 1.0),     # Cyan
            'missile_launcher': (0.8, 0.4, 0.0, 1.0), # Orange
            'converter': (1.0, 0.6, 0.0, 1.0)        # Orange-Yellow
        }
        
        self.enemy_colors = {
            'basic': (0.8, 0.8, 0.8, 1.0),           # Light Gray
            'kamikaze': (1.0, 0.2, 0.2, 1.0),        # Red
            'large': (0.0, 0.4, 1.0, 1.0),           # Blue
            'assault': (0.6, 0.3, 0.0, 1.0),         # Brown
            'stealth': (0.4, 0.0, 0.6, 1.0),         # Purple
            'cruiser': (0.3, 0.3, 0.5, 1.0),         # Gray-Blue
            'mothership': (0.5, 0.0, 0.5, 1.0)       # Purple
        }
        
    def create_test_entities(self):
        """Create some test entities to verify rendering works"""
        print("Creating test entities for Phase 2...")
        
        # Create test buildings around the world center
        world_center_x = 2400
        world_center_y = 1350
        
        test_buildings = [
            ('starting_base', world_center_x, world_center_y, 40),
            ('solar', world_center_x - 100, world_center_y - 100, 25),
            ('connector', world_center_x + 100, world_center_y - 100, 20),
            ('turret', world_center_x - 100, world_center_y + 100, 28),
            ('miner', world_center_x + 100, world_center_y + 100, 25),
        ]
        
        for building_type, x, y, radius in test_buildings:
            entity = self.create_building_visual(building_type, x, y, radius)
            if entity:
                self.test_entities.append(entity)
                
        # Create test enemies
        test_enemies = [
            ('basic', world_center_x - 200, world_center_y, 8),
            ('large', world_center_x + 200, world_center_y, 15),
            ('stealth', world_center_x, world_center_y - 200, 8),
        ]
        
        for enemy_type, x, y, radius in test_enemies:
            entity = self.create_enemy_visual(enemy_type, x, y, radius)
            if entity:
                self.test_entities.append(entity)
                
        # Create test asteroids
        test_asteroids = [
            (world_center_x - 300, world_center_y - 200, 30),
            (world_center_x + 300, world_center_y - 200, 25),
            (world_center_x - 300, world_center_y + 200, 35),
            (world_center_x + 300, world_center_y + 200, 20),
        ]
        
        for x, y, radius in test_asteroids:
            entity = self.create_asteroid_visual(x, y, radius)
            if entity:
                self.test_entities.append(entity)
                
        print(f"✓ Created {len(self.test_entities)} test entities")
        
    def create_building_visual(self, building_type, x, y, radius):
        """Create a 3D visual representation of a building"""
        try:
            # Create basic geometry based on building type
            if building_type == 'starting_base':
                # Large hexagonal base
                node = self.create_hexagon(radius, self.building_colors[building_type])
            elif building_type in ['solar', 'battery']:
                # Rectangular panels
                node = self.create_rectangle(radius * 1.5, radius, self.building_colors[building_type])
            elif building_type == 'connector':
                # Small circle hub
                node = self.create_circle(radius, self.building_colors[building_type])
            elif building_type in ['turret', 'laser', 'superlaser']:
                # Square with a smaller square on top (turret)
                node = self.create_turret(radius, self.building_colors[building_type])
            else:
                # Default square
                node = self.create_square(radius, self.building_colors.get(building_type, (0.5, 0.5, 0.5, 1.0)))
            
            if node:
                node.setPos(x, y, 0)
                node.reparentTo(self.base.render)
                return node
                
        except Exception as e:
            print(f"Error creating building visual for {building_type}: {e}")
            
        return None
        
    def create_enemy_visual(self, enemy_type, x, y, radius):
        """Create a 3D visual representation of an enemy"""
        try:
            color = self.enemy_colors.get(enemy_type, (0.8, 0.8, 0.8, 1.0))
            
            if enemy_type in ['basic', 'kamikaze', 'stealth']:
                # Small triangular ships
                node = self.create_triangle(radius, color)
            elif enemy_type in ['large', 'cruiser']:
                # Larger diamond shapes
                node = self.create_diamond(radius, color)
            elif enemy_type == 'mothership':
                # Large hexagon
                node = self.create_hexagon(radius, color)
            else:
                # Default triangle
                node = self.create_triangle(radius, color)
            
            if node:
                node.setPos(x, y, 5)  # Slightly elevated
                node.reparentTo(self.base.render)
                return node
                
        except Exception as e:
            print(f"Error creating enemy visual for {enemy_type}: {e}")
            
        return None
        
    def create_asteroid_visual(self, x, y, radius):
        """Create a 3D visual representation of an asteroid"""
        try:
            # Irregular octagon for asteroids
            node = self.create_octagon(radius, (0.4, 0.3, 0.2, 1.0))  # Brown color
            
            if node:
                node.setPos(x, y, 0)
                node.reparentTo(self.base.render)
                return node
                
        except Exception as e:
            print(f"Error creating asteroid visual: {e}")
            
        return None
        
    def create_square(self, size, color):
        """Create a square card"""
        card = CardMaker("square")
        card.setFrame(-size/2, size/2, -size/2, size/2)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        return node
        
    def create_rectangle(self, width, height, color):
        """Create a rectangular card"""
        card = CardMaker("rectangle")
        card.setFrame(-width/2, width/2, -height/2, height/2)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        return node
        
    def create_circle(self, radius, color):
        """Create a circular approximation using a card"""
        card = CardMaker("circle")
        card.setFrame(-radius, radius, -radius, radius)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        # TODO: In Phase 4, replace with actual circular geometry
        return node
        
    def create_triangle(self, size, color):
        """Create a triangle approximation using a card"""
        card = CardMaker("triangle")
        card.setFrame(-size, size, -size, size)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        # TODO: In Phase 4, replace with actual triangular geometry
        return node
        
    def create_diamond(self, size, color):
        """Create a diamond approximation using a card"""
        card = CardMaker("diamond")
        card.setFrame(-size, size, -size, size)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        # TODO: In Phase 4, replace with actual diamond geometry  
        return node
        
    def create_hexagon(self, radius, color):
        """Create a hexagon approximation using a card"""
        card = CardMaker("hexagon")
        card.setFrame(-radius, radius, -radius, radius)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        # TODO: In Phase 4, replace with actual hexagonal geometry
        return node
        
    def create_octagon(self, radius, color):
        """Create an octagon approximation using a card"""
        card = CardMaker("octagon")
        card.setFrame(-radius, radius, -radius, radius)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setBillboardAxis()  # Face camera
        # TODO: In Phase 4, replace with actual octagonal geometry
        return node
        
    def create_turret(self, radius, color):
        """Create a turret approximation with base and barrel"""
        # Create base
        base_card = CardMaker("turret_base")
        base_card.setFrame(-radius, radius, -radius, radius)
        base_node = self.base.render.attachNewNode(base_card.generate())
        base_node.setColor(*color)
        base_node.setBillboardAxis()
        
        # Create barrel (smaller square on top)
        barrel_card = CardMaker("turret_barrel")
        barrel_size = radius * 0.3
        barrel_card.setFrame(-barrel_size, barrel_size, 0, radius)
        barrel_node = base_node.attachNewNode(barrel_card.generate())
        barrel_node.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])  # Darker
        barrel_node.setPos(0, 0, 0.1)  # Slightly above base
        
        return base_node
        
    def create_range_indicator(self, radius, color=(1, 1, 1, 0.3)):
        """Create a range indicator circle for building placement"""
        card = CardMaker("range_circle")
        card.setFrame(-radius, radius, -radius, radius)
        node = self.base.render.attachNewNode(card.generate())
        node.setColor(*color)
        node.setTransparency(True)
        node.setBillboardAxis()
        return node
        
    def cleanup_test_entities(self):
        """Remove all test entities"""
        for entity in self.test_entities:
            if entity:
                entity.removeNode()
        self.test_entities.clear()
        print("✓ Test entities cleaned up")
        
    def cleanup(self):
        """Clean up all visual entities"""
        self.cleanup_test_entities()
        
        # Clean up any remaining entity nodes
        for entity_id, node in self.entity_nodes.items():
            if node:
                node.removeNode()
        self.entity_nodes.clear()
        
        print("✓ Entity visualizer cleanup complete") 