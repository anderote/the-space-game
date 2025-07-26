"""
Panda3D Power Network Renderer - Phase 3 Implementation
Visualizes power connections between buildings with animated flow effects
"""

from panda3d.core import (
    NodePath, LineSegs, TransparencyAttrib, Vec3
)
from direct.showbase.DirectObject import DirectObject
import math

class PowerNetworkRenderer(DirectObject):
    """Manages visual representation of power networks and connections"""
    
    def __init__(self, base):
        self.base = base
        self.connection_lines = {}  # {(building1_id, building2_id): line_node}
        self.power_flow_effects = {}  # {connection_id: particle_effect}
        
        # Create root node for all power connections
        self.connection_root = self.base.render.attachNewNode("power_connections")
        
        # Connection colors based on state
        self.connection_colors = {
            'powered': (0.2, 0.8, 0.5, 0.9),     # Green for powered connections
            'unpowered': (0.3, 0.3, 0.3, 0.5),   # Gray for unpowered
            'generating': (1.0, 1.0, 0.0, 0.9),  # Yellow for power generators
        }

    def create_thin_rectangle_line(self, start_x, start_y, end_x, end_y, thickness=2.0, color=(1.0, 1.0, 1.0, 1.0), name="power_line"):
        """Create a thin rectangle that acts as a zoom-aware power connection line"""
        try:
            from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, Geom, GeomTriangles, GeomNode
            
            # Calculate line properties
            dx = end_x - start_x
            dy = end_y - start_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length < 0.001:  # Avoid division by zero
                return None
                
            # Normalize direction vector
            dir_x = dx / length
            dir_y = dy / length
            
            # Calculate perpendicular vector for width
            perp_x = -dir_y * thickness / 2
            perp_y = dir_x * thickness / 2
            
            # Create vertex data
            format = GeomVertexFormat.getV3()
            vdata = GeomVertexData(name, format, Geom.UHStatic)
            vdata.setNumRows(4)
            vertex = GeomVertexWriter(vdata, 'vertex')
            
            # Add vertices for rectangle corners (draw behind buildings at z=-0.5)
            vertex.addData3f(start_x + perp_x, start_y + perp_y, -0.5)  # Bottom-left
            vertex.addData3f(start_x - perp_x, start_y - perp_y, -0.5)  # Top-left
            vertex.addData3f(end_x - perp_x, end_y - perp_y, -0.5)     # Top-right
            vertex.addData3f(end_x + perp_x, end_y + perp_y, -0.5)     # Bottom-right
            
            # Create geometry
            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)
            
            # Add triangles (two triangles make a rectangle)
            tris.addVertices(0, 1, 2)  # First triangle
            tris.addVertices(0, 2, 3)  # Second triangle
            
            geom.addPrimitive(tris)
            
            # Create node and attach to render
            geom_node = GeomNode(name)
            geom_node.addGeom(geom)
            node_path = NodePath(geom_node)
            
            # Set color and transparency
            node_path.setColor(*color)
            if color[3] < 1.0:
                node_path.setTransparency(TransparencyAttrib.MAlpha)
            
            return node_path
            
        except Exception as e:
            print(f"Error creating power connection rectangle: {e}")
            return None 

    def update_power_network(self, buildings):
        """Update all power network visualizations based on current building state"""
        # Clear existing connections
        self.clear_all_connections()
        
        # Create a lookup dictionary for buildings by ID
        building_lookup = {building.building_id: building for building in buildings}
        
        # Create connections for all buildings
        processed_pairs = set()
        
        for building in buildings:
            for connected_building_id in building.connections:
                # Look up the connected building object
                connected_building = building_lookup.get(connected_building_id)
                if connected_building is None:
                    print(f"✗ Warning: Connection to unknown building ID: {connected_building_id}")
                    continue
                
                # Avoid duplicate lines (A->B and B->A)
                pair = tuple(sorted([building.building_id, connected_building.building_id]))
                if pair not in processed_pairs:
                    self.create_connection_line(building, connected_building)
                    processed_pairs.add(pair)
        
        print(f"✓ Updated power network visualization: {len(processed_pairs)} connections")
    
    def create_connection_line(self, building1, building2):
        """Create a zoom-aware power connection line using thin rectangles"""
        try:
            # Generate unique connection ID
            connection_id = f"{building1.building_id}_{building2.building_id}"
            
            # Check if both buildings are powered
            both_powered = (building1.is_connected_to_power and 
                          building2.is_connected_to_power and
                          building1.state.name == "OPERATIONAL" and 
                          building2.state.name == "OPERATIONAL")
            
            # Determine connection state and color
            if both_powered:
                color = (0.2, 0.8, 0.5, 0.9)  # Green for powered connections
                thickness = 3.0
            else:
                color = (0.6, 0.6, 0.6, 0.8)  # Gray for unpowered connections
                thickness = 2.0
            
            # Create main connection line using thin rectangle
            line_node = self.create_thin_rectangle_line(
                building1.x, building1.y, building2.x, building2.y,
                thickness=thickness, color=color, name=f"connection_{connection_id}"
            )
            
            if not line_node:
                return None
                
            line_node.reparentTo(self.connection_root)
            
            # Add glow effect for powered connections
            if both_powered:
                glow_node = self.create_thin_rectangle_line(
                    building1.x, building1.y, building2.x, building2.y,
                    thickness=thickness + 2.0, color=(0.1, 0.6, 0.4, 0.3), name=f"glow_{connection_id}"
                )
                if glow_node:
                    glow_node.reparentTo(line_node)
            
            # Store connection
            self.connection_lines[connection_id] = {
                'node': line_node,
                'building1': building1,
                'building2': building2
            }
            
            return line_node
            
        except Exception as e:
            print(f"✗ Error creating connection line: {e}")
            return None
    
    def clear_all_connections(self):
        """Remove all existing connection visualizations"""
        # Clear connection lines
        for connection_data in self.connection_lines.values():
            if connection_data['node']:
                connection_data['node'].removeNode()
        
        # Clear power flow effects
        for effect in self.power_flow_effects.values():
            if effect:
                effect.removeNode()
        
        # Reset storage
        self.connection_lines.clear()
        self.power_flow_effects.clear()
        
        # Clear all children from connection root
        self.connection_root.getChildren().detach()
    
    def cleanup(self):
        """Clean up all power network visualizations"""
        print("Cleaning up power network renderer...")
        
        # Remove all visual elements
        self.clear_all_connections()
        
        # Remove root node
        if self.connection_root:
            self.connection_root.removeNode()
        
        print("✓ Power network renderer cleanup complete") 