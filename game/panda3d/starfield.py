"""
Starfield System - Phase 3 Implementation
Creates a multi-layer parallax starfield background
"""

import random
import numpy as np
from panda3d.core import (
    CardMaker, GeomNode, Geom, GeomVertexFormat, GeomVertexData,
    GeomVertexWriter, GeomPoints, GeomLines, RenderState, ColorAttrib,
    TransparencyAttrib, NodePath
)

class StarfieldSystem:
    """Multi-layer parallax starfield for space atmosphere"""
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Get world dimensions
        display_config = config.game.get("display", {})
        self.world_width = display_config.get("world_width", 4800)
        self.world_height = display_config.get("world_height", 2700)
        
        # Starfield layers
        self.layers = []
        self.star_nodes = []
        
        # Camera reference for parallax
        self.last_camera_x = 0
        self.last_camera_y = 0
        
        self.setup_starfield()
        print("✓ Three-layer parallax starfield created")
        
    def setup_starfield(self):
        """Create three layers of stars with different parallax speeds"""
        
        # Layer configurations: (star_count, size, brightness, parallax_factor, color)
        # Increased density by 30%
        layer_configs = [
            (520, 1.0, 0.3, 0.1, (0.4, 0.4, 0.6, 0.3)),  # Far background - dim blue
            (325, 1.5, 0.6, 0.3, (0.7, 0.7, 0.9, 0.6)),  # Middle layer - brighter
            (195, 2.0, 1.0, 0.7, (1.0, 1.0, 1.0, 1.0))   # Foreground - bright white
        ]
        
        for i, (star_count, size, brightness, parallax_factor, color) in enumerate(layer_configs):
            layer_node = self.create_star_layer(
                f"starfield_layer_{i}", 
                star_count, 
                size, 
                brightness, 
                parallax_factor, 
                color
            )
            
            # Attach to render at appropriate depth
            layer_node.reparentTo(self.base.render)
            layer_node.setZ(-10 - i * 2)  # Further back layers have much lower Z
            
            # Store layer info
            self.layers.append({
                'node': layer_node,
                'parallax_factor': parallax_factor,
                'original_stars': []  # Will store original positions if needed
            })
            
            self.star_nodes.append(layer_node)
            
    def create_star_layer(self, name, star_count, size, brightness, parallax_factor, color):
        """Create a single layer of stars"""
        
        # Create vertex format for points
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData(name, format, Geom.UHStatic)
        vdata.setNumRows(star_count)
        vertex = GeomVertexWriter(vdata, "vertex")
        
        # Generate random star positions across extended area for parallax
        # Make the star field larger than the world to accommodate camera movement
        margin = 1000  # Extra space around world bounds
        
        for _ in range(star_count):
            x = random.uniform(-margin, self.world_width + margin)
            y = random.uniform(-margin, self.world_height + margin)
            z = -5  # Place stars behind game objects
            vertex.addData3f(x, y, z)
            
        # Create geometry
        geom = Geom(vdata)
        points = GeomPoints(Geom.UHStatic)
        points.addConsecutiveVertices(0, star_count)
        geom.addPrimitive(points)
        
        # Create node
        geom_node = GeomNode(name)
        geom_node.addGeom(geom)
        node_path = NodePath(geom_node)
        
        # Apply visual properties
        node_path.setRenderModeThickness(size)
        node_path.setColor(color[0], color[1], color[2], color[3])
        
        # Set transparency for layered effect
        node_path.setTransparency(TransparencyAttrib.MAlpha)
        
        return node_path
        
    def update_parallax(self, camera_x, camera_y):
        """Update starfield positions based on camera movement for parallax effect"""
        
        # Calculate camera movement delta
        delta_x = camera_x - self.last_camera_x
        delta_y = camera_y - self.last_camera_y
        
        # Update each layer with different parallax factors
        for layer in self.layers:
            parallax_factor = layer['parallax_factor']
            
            # Move layer in opposite direction of camera, scaled by parallax factor
            current_x = layer['node'].getX()
            current_y = layer['node'].getY()
            
            new_x = current_x - (delta_x * parallax_factor)
            new_y = current_y - (delta_y * parallax_factor)
            
            layer['node'].setPos(new_x, new_y, layer['node'].getZ())
            
        # Update last camera position
        self.last_camera_x = camera_x
        self.last_camera_y = camera_y
        
    def set_camera_position(self, camera_x, camera_y):
        """Set the camera position for parallax calculations"""
        self.last_camera_x = camera_x
        self.last_camera_y = camera_y
        
        # Initialize layer positions
        for layer in self.layers:
            parallax_factor = layer['parallax_factor']
            # Position layers based on initial camera position
            layer['node'].setPos(-camera_x * parallax_factor, -camera_y * parallax_factor, layer['node'].getZ())
        
    def cleanup(self):
        """Clean up starfield resources"""
        print("Cleaning up starfield...")
        
        for node in self.star_nodes:
            if node:
                node.removeNode()
                
        self.layers.clear()
        self.star_nodes.clear()
        
        print("✓ Starfield cleanup complete") 