"""
Panda3D Entity Visualizer - Phase 2 Implementation
Creates simple 3D representations of game entities
"""

from panda3d.core import (
    GeomNode, Geom, GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, GeomPoints, GeomLines, NodePath, TransparencyAttrib, 
    LineSegs, Vec3, CardMaker, VBase4
)
from direct.actor.Actor import Actor
import math
from panda3d.core import LineSegs

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
            'basic': (1.0, 0.0, 0.0, 1.0),           # Red (Fighter)
            'kamikaze': (1.0, 0.2, 0.2, 1.0),        # Red
            'large': (0.0, 0.4, 1.0, 1.0),           # Blue
            'assault': (0.6, 0.3, 0.0, 1.0),         # Brown
            'stealth': (0.4, 0.0, 0.6, 1.0),         # Purple
            'cruiser': (0.3, 0.3, 0.5, 1.0),         # Gray-Blue
            'mothership': (1.0, 1.0, 0.0, 1.0)       # Yellow (Mothership)
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
            # Get color for building type
            color = self.building_colors.get(building_type, (0.5, 0.5, 0.5, 1.0))
            
            # Create 3D geometry based on building type
            if building_type == 'starting_base':
                # Large blue hexagonal base (taller for prominence)
                node = self.create_3d_hexagon(radius * 2, 25, (0.2, 0.4, 0.8, 1.0))
            elif building_type == 'solar':
                # Black solar panel with white grid lines
                node = self.create_3d_solar_panel(radius * 2, color)
            elif building_type == 'nuclear':
                # Large green nuclear reactor with glowing core
                node = self.create_3d_nuclear_reactor(radius * 1.5, (0.0, 1.0, 0.4, 1.0))
            elif building_type == 'battery':
                # Tall rectangular battery (fallback to 2D for now)
                node = self.create_rectangle(radius, radius * 1.2, color)
            elif building_type == 'connector':
                # Yellow circle (flat disk instead of sphere)
                node = self.create_3d_circle(radius * 0.8, (1.0, 1.0, 0.0, 1.0))
                # Add orange circular outline
                if node:
                    outline = self.create_circular_outline(radius * 0.8, (1.0, 0.5, 0.0, 1.0))  # Orange
                    if outline:
                        outline.reparentTo(node)
            elif building_type == 'turret':
                # Red pentagon with depth (taller for better 3D visibility) - no outline
                node = self.create_3d_pentagon(radius * 1.2, 20, (0.8, 0.2, 0.2, 1.0))
            elif building_type == 'laser':
                # White hexagon (taller for better 3D visibility)
                node = self.create_3d_hexagon(radius * 1.1, 15, (1.0, 1.0, 1.0, 1.0))
            elif building_type == 'superlaser':
                # Larger white hexagon (taller for better 3D visibility)
                node = self.create_3d_hexagon(radius * 1.3, 18, (1.0, 1.0, 1.0, 1.0))
            elif building_type == 'missile_launcher':
                # Orange octagon (missile launcher)
                node = self.create_3d_octagon(radius * 1.2, 20, (0.8, 0.4, 0.0, 1.0))
            elif building_type == 'miner':
                # Green diamond
                node = self.create_3d_diamond(radius * 1.2, (0.2, 0.8, 0.2, 1.0))
            else:
                # Default square for other types
                node = self.create_square(radius * 2, color)
            
            if node:
                # Position the building in the XY plane (Z=0 for 2D game)
                node.setPos(x, y, 0)
                node.reparentTo(self.base.render)
                
                # Set building to render in main layer above background (power connections and asteroids)
                node.setBin("opaque", 50)  # Main game objects layer
                
                # Make sure it's visible and properly scaled
                node.setScale(1.0)
                node.show()
                
                # Buildings are placed with no rotation for clean appearance
                # This prevents jiggling during placement preview
                
                # Ensure proper rendering state for 2D visibility
                node.setTwoSided(True)  # Make cards visible from both sides
                
                return node
            else:
                print(f"✗ Failed to create node for {building_type}")
                return None
                
        except Exception as e:
            print(f"✗ Error creating building visual for {building_type}: {e}")
            import traceback
            traceback.print_exc()
            
        return None
        
    def create_enemy_visual(self, enemy_type, x, y, radius, velocity_x=0, velocity_y=0):
        """Create a 3D visual representation of an enemy"""
        try:
            color = self.enemy_colors.get(enemy_type, (0.8, 0.8, 0.8, 1.0))
            
            if enemy_type in ['basic', 'kamikaze', 'stealth']:
                # Fighter ships - narrow directional triangles
                node = self.create_directional_triangle(radius, color, velocity_x, velocity_y)
            elif enemy_type == 'mothership':
                # Mothership - yellow oval
                node = self.create_oval(radius, color)
            elif enemy_type in ['large', 'cruiser']:
                # Larger diamond shapes  
                node = self.create_diamond(radius, color)
            else:
                # Default directional triangle for fighters
                node = self.create_directional_triangle(radius, color, velocity_x, velocity_y)
            
            if node:
                node.setPos(x, y, 5)  # Slightly elevated
                node.reparentTo(self.base.render)
                return node
                
        except Exception as e:
            print(f"Error creating enemy visual for {enemy_type}: {e}")
            
        return None
    
    def update_enemy_visual_direction(self, enemy_visual_node, enemy_type, radius, velocity_x, velocity_y):
        """Update enemy visual to face movement direction"""
        try:
            if not enemy_visual_node or enemy_type not in ['basic', 'kamikaze', 'stealth']:
                return  # Only update directional triangles
            
            # Get position and parent
            pos = enemy_visual_node.getPos()
            parent = enemy_visual_node.getParent()
            
            # Remove old visual
            enemy_visual_node.removeNode()
            
            # Create new directional triangle
            color = self.enemy_colors.get(enemy_type, (0.8, 0.8, 0.8, 1.0))
            new_node = self.create_directional_triangle(radius, color, velocity_x, velocity_y)
            
            if new_node:
                new_node.setPos(pos)
                new_node.reparentTo(parent)
                return new_node
                
        except Exception as e:
            print(f"Error updating enemy visual direction: {e}")
            
        return enemy_visual_node  # Return original if update failed
    
    def create_projectile_visual(self, projectile_type, x, y):
        """Create a visual representation of a projectile"""
        try:
            if projectile_type == "bullet":
                # Enhanced bullet with glow effect
                node = self.create_enhanced_bullet_visual(x, y)
            elif projectile_type == "laser":
                # Enhanced laser projectile (though lasers are usually beams)
                node = self.create_enhanced_laser_projectile_visual(x, y)
            else:
                # Default projectile
                node = self.create_circle(1, (1.0, 1.0, 1.0, 1.0))  # White
                if node:
                    node.setPos(x, y, 4)
                    node.reparentTo(self.base.render)
            
            return node
                
        except Exception as e:
            print(f"Error creating projectile visual: {e}")
        
        return None
    
    def create_enhanced_bullet_visual(self, x, y):
        """Create bullet with glow effect"""
        try:
            # Main bullet core - bright yellow
            main_bullet = self.create_circle(2, (1.0, 1.0, 0.2, 1.0))
            if not main_bullet:
                return None
                
            main_bullet.setPos(x, y, 4)
            main_bullet.reparentTo(self.base.render)
            
            # Outer glow
            glow = self.create_circle(4, (1.0, 0.8, 0.0, 0.4))
            if glow:
                glow.reparentTo(main_bullet)
                
            # Inner bright core
            core = self.create_circle(1, (1.0, 1.0, 1.0, 1.0))
            if core:
                core.reparentTo(main_bullet)
            
            return main_bullet
            
        except Exception as e:
            print(f"Error creating enhanced bullet visual: {e}")
            return None
    
    def create_enhanced_laser_projectile_visual(self, x, y):
        """Create glowing laser projectile"""
        try:
            # Main laser core - bright blue/white
            main_laser = self.create_circle(1.5, (0.8, 0.9, 1.0, 1.0))
            if not main_laser:
                return None
                
            main_laser.setPos(x, y, 4)
            main_laser.reparentTo(self.base.render)
            
            # Outer glow - blue tint
            glow = self.create_circle(3.5, (0.3, 0.6, 1.0, 0.3))
            if glow:
                glow.reparentTo(main_laser)
                
            # Inner bright core - pure white
            core = self.create_circle(0.5, (1.0, 1.0, 1.0, 1.0))
            if core:
                core.reparentTo(main_laser)
            
            return main_laser
            
        except Exception as e:
            print(f"Error creating enhanced laser projectile visual: {e}")
            return None
    
    def create_laser_beam_visual(self, start_x, start_y, end_x, end_y):
        """Create an enhanced glowing laser beam from start to end"""
        try:
            # Create enhanced laser beam with multiple layers for glow effect
            laser_effect = self.create_enhanced_laser_beam(start_x, start_y, end_x, end_y)
            if laser_effect:
                laser_effect.reparentTo(self.base.render)
                return laser_effect
            
            # Fallback to simple line if enhanced version fails
            line_segs = LineSegs()
            line_segs.setThickness(2.0)
            line_segs.setColor(1.0, 0.0, 0.0, 1.0)  # Red laser
            line_segs.moveTo(start_x, start_y, 4)
            line_segs.drawTo(end_x, end_y, 4)
            
            line_node = line_segs.create()
            node_path = self.base.render.attachNewNode(line_node)
            return node_path
            
        except Exception as e:
            print(f"Error creating laser beam visual: {e}")
        
        return None
    
    def create_enhanced_laser_beam(self, start_x, start_y, end_x, end_y):
        """Create a multi-layered glowing laser beam"""
        try:
            from panda3d.core import NodePath
            
            # Create main container node
            laser_container = NodePath("laser_beam")
            
            # Outer glow layer (thick, transparent)
            outer_glow = LineSegs()
            outer_glow.setThickness(8.0)
            outer_glow.setColor(1.0, 0.3, 0.3, 0.3)  # Thick red glow
            outer_glow.moveTo(start_x, start_y, 4)
            outer_glow.drawTo(end_x, end_y, 4)
            outer_node = laser_container.attachNewNode(outer_glow.create())
            
            # Middle layer (medium thickness)
            middle_layer = LineSegs()
            middle_layer.setThickness(4.0)
            middle_layer.setColor(1.0, 0.6, 0.6, 0.7)  # Medium red
            middle_layer.moveTo(start_x, start_y, 4.1)
            middle_layer.drawTo(end_x, end_y, 4.1)
            middle_node = laser_container.attachNewNode(middle_layer.create())
            
            # Inner core (bright, thin)
            inner_core = LineSegs()
            inner_core.setThickness(1.5)
            inner_core.setColor(1.0, 1.0, 1.0, 1.0)  # Bright white core
            inner_core.moveTo(start_x, start_y, 4.2)
            inner_core.drawTo(end_x, end_y, 4.2)
            inner_node = laser_container.attachNewNode(inner_core.create())
            
            return laser_container
            
        except Exception as e:
            print(f"Error creating enhanced laser beam: {e}")
            return None
    
    def create_turret_attack_effect(self, start_x, start_y, target_x, target_y, turret_type):
        """Create visual attack effect for player turrets"""
        try:
            # Different effects for different turret types
            if turret_type == "laser":
                # Bright blue laser beam with glow effect
                effect = self.create_turret_laser_effect(start_x, start_y, target_x, target_y, 
                                                       color=(0.2, 0.8, 1.0, 0.9), thickness=4.0)
            elif turret_type == "superlaser":
                # Thicker, brighter laser with different color
                effect = self.create_turret_laser_effect(start_x, start_y, target_x, target_y,
                                                       color=(1.0, 0.9, 0.2, 1.0), thickness=6.0)
            else:
                # Default laser effect
                effect = self.create_turret_laser_effect(start_x, start_y, target_x, target_y,
                                                       color=(0.8, 0.8, 1.0, 0.8), thickness=3.0)
            
            if effect:
                # Schedule removal after short duration
                def remove_effect():
                    try:
                        effect.removeNode()
                    except:
                        pass
                
                # Remove after 0.2 seconds
                from direct.task import Task
                self.base.taskMgr.doMethodLater(0.2, lambda task: remove_effect(), 'remove_attack_effect')
                
            return effect
            
        except Exception as e:
            print(f"Error creating turret attack effect: {e}")
            return None
    
    def create_turret_laser_effect(self, start_x, start_y, end_x, end_y, color=(0.2, 0.8, 1.0, 0.9), thickness=4.0):
        """Create a turret laser beam with glow effect"""
        try:
            # Create main laser beam using thin rectangle
            laser_path = self.create_thin_rectangle_line(
                start_x, start_y, end_x, end_y, 
                thickness=thickness, color=color, name="turret_laser_main"
            )
            
            if not laser_path:
                return None
                
            laser_path.reparentTo(self.base.render)
            
            # Create outer glow layer
            glow_color = (color[0] * 0.5, color[1] * 0.5, color[2] * 0.5, color[3] * 0.4)
            outer_path = self.create_thin_rectangle_line(
                start_x, start_y, end_x, end_y,
                thickness=thickness * 2.0, color=glow_color, name="turret_laser_glow"
            )
            if outer_path:
                outer_path.reparentTo(laser_path)
            
            # Create inner bright core
            core_color = (min(1.0, color[0] * 1.5), min(1.0, color[1] * 1.5), min(1.0, color[2] * 1.5), 1.0)
            inner_path = self.create_thin_rectangle_line(
                start_x, start_y, end_x, end_y,
                thickness=thickness * 0.3, color=core_color, name="turret_laser_core"
            )
            if inner_path:
                inner_path.reparentTo(laser_path)
            
            return laser_path
            
        except Exception as e:
            print(f"Error creating turret laser effect: {e}")
            return None
    
    def create_missile_visual(self, x, y):
        """Create visual representation of a missile"""
        try:
            # Create small orange diamond for missile
            node = self.create_diamond(3, (1.0, 0.5, 0.0, 1.0))  # Orange
            if node:
                node.setPos(x, y, 3)  # Elevated
                node.reparentTo(self.base.render)
                return node
                
        except Exception as e:
            print(f"Error creating missile visual: {e}")
            
        return None
    
    def create_explosion_effect(self, x, y):
        """Create visual explosion effect"""
        try:
            # Create expanding orange circle for explosion
            explosion_node = self.create_circle(15, (1.0, 0.3, 0.0, 0.8))  # Orange explosion
            if explosion_node:
                explosion_node.setPos(x, y, 4)  # Elevated
                explosion_node.reparentTo(self.base.render)
                
                # Scale up the explosion over time
                from direct.interval.IntervalGlobal import LerpScaleInterval, Sequence, Func
                
                # Scale from small to large, then remove
                scale_up = LerpScaleInterval(explosion_node, 0.3, (3, 3, 1), (0.5, 0.5, 1))
                remove_func = Func(explosion_node.removeNode)
                explosion_sequence = Sequence(scale_up, remove_func)
                explosion_sequence.start()
                
                return explosion_node
                
        except Exception as e:
            print(f"Error creating explosion effect: {e}")
            
        return None
    
    def create_bullet_impact_effect(self, x, y):
        """Create particle effect when bullet hits enemy"""
        try:
            # Create multiple small particles that spread out
            impact_container = NodePath("bullet_impact")
            impact_container.setPos(x, y, 4)
            impact_container.reparentTo(self.base.render)
            
            # Create several small sparks
            spark_colors = [
                (1.0, 1.0, 0.0, 1.0),  # Yellow
                (1.0, 0.5, 0.0, 1.0),  # Orange
                (1.0, 0.8, 0.2, 1.0),  # Yellow-orange
            ]
            
            import random
            for i in range(6):  # 6 sparks
                spark = self.create_circle(1, random.choice(spark_colors))
                if spark:
                    # Random offset for each spark
                    offset_x = random.uniform(-8, 8)
                    offset_y = random.uniform(-8, 8)
                    spark.setPos(offset_x, offset_y, 0)
                    spark.reparentTo(impact_container)
                    
                    # Animate sparks flying outward and fading
                    try:
                        from direct.interval.IntervalGlobal import LerpPosInterval, LerpColorScaleInterval, Parallel, Sequence, Func
                        
                        # Move outward
                        move_out = LerpPosInterval(spark, 0.3, 
                                                 (offset_x * 2, offset_y * 2, 0), 
                                                 (offset_x, offset_y, 0))
                        
                        # Fade out
                        fade_out = LerpColorScaleInterval(spark, 0.3, 
                                                        (1, 1, 1, 0), 
                                                        (1, 1, 1, 1))
                        
                        # Run both animations in parallel
                        spark_anim = Parallel(move_out, fade_out)
                        spark_anim.start()
                        
                    except Exception as anim_error:
                        print(f"Error animating spark: {anim_error}")
            
            # Remove the entire impact effect after animation
            def cleanup_impact():
                try:
                    impact_container.removeNode()
                except:
                    pass
            
            self.base.taskMgr.doMethodLater(0.5, lambda task: cleanup_impact(), 'cleanup_bullet_impact')
            
            return impact_container
            
        except Exception as e:
            print(f"Error creating bullet impact effect: {e}")
            return None
    
    def create_3d_nuclear_reactor(self, radius, color):
        """Create a nuclear reactor with glowing core"""
        try:
            # Main reactor container
            reactor = self.create_3d_hexagon(radius, 20, color)
            
            # Inner glowing core
            core = self.create_3d_circle(radius * 0.6, (0.0, 1.0, 0.8, 0.8))
            if core:
                core.reparentTo(reactor)
                core.setPos(0, 0, 2)
                
            # Outer glow ring
            glow = self.create_3d_circle(radius * 0.8, (0.0, 0.8, 0.4, 0.4))
            if glow:
                glow.reparentTo(reactor)
                glow.setPos(0, 0, 1)
            
            return reactor
            
        except Exception as e:
            print(f"Error creating nuclear reactor visual: {e}")
            return self.create_3d_hexagon(radius, 20, color)
        
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
        """Create a square card for orthographic 2D view"""
        card = CardMaker("square")
        card.setFrame(-size/2, size/2, -size/2, size/2)
        # Create a detached node that can be positioned later
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # For orthographic 2D view, orient the card to face the camera (looking down Z-axis)
        # The card should be in the XY plane
        node_path.setP(-90)  # Rotate 90 degrees around X axis to lay flat in XY plane
        
        return node_path
        
    def create_rectangle(self, width, height, color):
        """Create a rectangular card for orthographic 2D view"""
        card = CardMaker("rectangle")
        card.setFrame(-width/2, width/2, -height/2, height/2)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_circle(self, radius, color):
        """Create a circular approximation using a card for orthographic 2D view"""
        card = CardMaker("circle")
        card.setFrame(-radius, radius, -radius, radius)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_triangle(self, size, color):
        """Create a triangle approximation using a card for orthographic 2D view"""
        card = CardMaker("triangle")
        card.setFrame(-size, size, -size, size)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
    
    def create_directional_triangle(self, size, color, velocity_x, velocity_y):
        """Create a narrow triangle that points in the direction of movement"""
        try:
            from panda3d.core import GeomNode, Geom, GeomVertexFormat, GeomVertexData, GeomVertexWriter
            from panda3d.core import GeomTriangles, GeomPoints, GeomLines, RenderState
            import math
            
            # Calculate direction angle from velocity
            if velocity_x == 0 and velocity_y == 0:
                angle = 0  # Default facing right
            else:
                angle = math.atan2(velocity_y, velocity_x)
            
            # Create narrow triangle vertices (pointing right initially)
            # Make it narrow and pointed for a fighter ship look
            width = size * 0.4  # Narrow width
            length = size * 1.2  # Longer length for pointy look
            
            # Triangle vertices (pointing right)
            vertices = [
                (length, 0),      # Tip (front)
                (-length*0.5, width),   # Back left
                (-length*0.5, -width)   # Back right
            ]
            
            # Rotate vertices by the direction angle
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rotated_vertices = []
            for x, y in vertices:
                new_x = x * cos_a - y * sin_a
                new_y = x * sin_a + y * cos_a
                rotated_vertices.append((new_x, new_y))
            
            # Create geometry
            format = GeomVertexFormat.getV3()
            vdata = GeomVertexData('triangle', format, Geom.UHStatic)
            vdata.setNumRows(3)
            vertex = GeomVertexWriter(vdata, 'vertex')
            
            # Add vertices
            for x, y in rotated_vertices:
                vertex.addData3(x, y, 0)
            
            # Create triangle primitive
            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)
            tris.addVertices(0, 1, 2)
            geom.addPrimitive(tris)
            
            # Create node
            geom_node = GeomNode('directional_triangle')
            geom_node.addGeom(geom)
            node_path = NodePath(geom_node)
            node_path.setColor(*color)
            
            return node_path
            
        except Exception as e:
            print(f"Error creating directional triangle: {e}")
            # Fallback to regular triangle
            return self.create_triangle(size, color)
        
    def create_diamond(self, size, color):
        """Create a diamond approximation using a card for orthographic 2D view"""
        card = CardMaker("diamond")
        card.setFrame(-size, size, -size, size)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_hexagon(self, radius, color):
        """Create a hexagon approximation using a card for orthographic 2D view"""
        card = CardMaker("hexagon")
        card.setFrame(-radius, radius, -radius, radius)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_oval(self, radius, color):
        """Create an oval/ellipse approximation using a card for orthographic 2D view"""
        card = CardMaker("oval")
        # Make oval slightly wider than tall
        card.setFrame(-radius * 1.2, radius * 1.2, -radius * 0.8, radius * 0.8)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_circle(self, radius, color):
        """Create a circle approximation using a card for orthographic 2D view"""
        card = CardMaker("circle")
        card.setFrame(-radius, radius, -radius, radius)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_octagon(self, radius, color):
        """Create an octagon approximation using a card for orthographic 2D view"""
        card = CardMaker("octagon")
        card.setFrame(-radius, radius, -radius, radius)
        node_path = NodePath(card.generate())
        node_path.setColor(*color)
        
        # Orient for orthographic 2D view
        node_path.setP(-90)  # Rotate to lay flat in XY plane
        
        return node_path
        
    def create_turret(self, radius, color):
        """Create a turret approximation with base and barrel for orthographic 2D view"""
        # Create base
        base_card = CardMaker("turret_base")
        base_card.setFrame(-radius, radius, -radius, radius)
        base_node = NodePath(base_card.generate())
        base_node.setColor(*color)
        
        # Orient for orthographic 2D view
        base_node.setP(-90)  # Rotate to lay flat in XY plane
        
        # Create barrel (smaller square on top)
        barrel_card = CardMaker("turret_barrel")
        barrel_size = radius * 0.3
        barrel_card.setFrame(-barrel_size, barrel_size, 0, radius)
        barrel_node = base_node.attachNewNode(barrel_card.generate())
        barrel_node.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])  # Darker
        barrel_node.setPos(0, 0, 0.1)  # Slightly above base in Z
        
        return base_node
        
    def create_range_indicator(self, radius, color=(1.0, 1.0, 1.0, 0.3)):
        """Create a circular range indicator using thin rectangles"""
        try:
            import math
            
            # Create root node for the circle
            from panda3d.core import PandaNode
            circle_root = NodePath(PandaNode("range_circle"))
            
            # Draw circle using multiple small rectangle segments
            num_segments = 60
            segment_angle = 2 * math.pi / num_segments
            
            for i in range(num_segments):
                # Calculate segment endpoints
                angle1 = i * segment_angle
                angle2 = (i + 1) * segment_angle
                
                x1 = radius * math.cos(angle1)
                y1 = radius * math.sin(angle1)
                x2 = radius * math.cos(angle2)
                y2 = radius * math.sin(angle2)
                
                # Create thin rectangle for this segment
                segment = self.create_thin_rectangle_line(
                    x1, y1, x2, y2,
                    thickness=1.0,  # Thin line
                    color=color,
                    name=f"range_segment_{i}"
                )
                
                if segment:
                    segment.reparentTo(circle_root)
            
            # Set transparency
            from panda3d.core import TransparencyAttrib
            circle_root.setTransparency(TransparencyAttrib.MAlpha)
            circle_root.setTwoSided(True)  # Ensure visibility from both sides
            
            return circle_root
            
        except Exception as e:
            print(f"Error creating range indicator: {e}")
            return None
    
    def create_connection_radius_indicator(self, radius):
        """Create yellow connection range indicator"""
        return self.create_range_indicator(radius, (1.0, 1.0, 0.0, 0.4))  # Yellow
    
    def create_attack_radius_indicator(self, radius):
        """Create red attack range indicator"""
        return self.create_range_indicator(radius, (1.0, 0.2, 0.2, 0.5))  # Red
    
    def create_heal_radius_indicator(self, radius):
        """Create teal healing range indicator"""
        return self.create_range_indicator(radius, (0.0, 0.8, 0.8, 0.4))  # Teal
    
    def create_building_radius_indicators(self, building_type, building_config, x, y):
        """Create all appropriate radius indicators for a building"""
        indicators = {}
        
        try:
            # Connection radius (for all buildings that can connect)
            connection_range = building_config.get("connection_range", 0)
            if connection_range > 0:
                connection_indicator = self.create_connection_radius_indicator(connection_range)
                if connection_indicator:
                    connection_indicator.setPos(x, y, 0.1)
                    indicators['connection'] = connection_indicator
            
            # Attack radius (for defensive buildings)
            attack_range = building_config.get("range", 0)  # Using 'range' for attack range
            is_defensive = building_type in ['turret', 'laser', 'superlaser', 'missile_launcher']
            if attack_range > 0 and is_defensive:
                attack_indicator = self.create_attack_radius_indicator(attack_range)
                if attack_indicator:
                    attack_indicator.setPos(x, y, 0.1)
                    indicators['attack'] = attack_indicator
            
            # Healing radius (for repair buildings)
            heal_range = building_config.get("repair_range", 0)
            is_repair = building_type in ['repair']
            if heal_range > 0 and is_repair:
                heal_indicator = self.create_heal_radius_indicator(heal_range)
                if heal_indicator:
                    heal_indicator.setPos(x, y, 0.1)
                    indicators['heal'] = heal_indicator
            
            return indicators
            
        except Exception as e:
            print(f"✗ Error creating building radius indicators: {e}")
            return {}
        
    def create_circular_outline(self, radius, color):
        """Create a circular outline for connectors"""
        try:
            line_segs = LineSegs()
            line_segs.setColor(*color)
            line_segs.setThickness(4.0)
            
            # Draw circle outline
            num_segments = 24
            for i in range(num_segments + 1):
                angle = (i / num_segments) * 2 * math.pi
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                
                if i == 0:
                    line_segs.moveTo(x, y, 0.05)
                else:
                    line_segs.drawTo(x, y, 0.05)
            
            outline_node = self.base.render.attachNewNode(line_segs.create())
            outline_node.setTwoSided(True)
            outline_node.setTransparency(TransparencyAttrib.MAlpha)
            
            return outline_node
            
        except Exception as e:
            print(f"Error creating circular outline: {e}")
            return None
    
    def create_pentagon_outline(self, radius, color):
        """Create a pentagon outline for turrets"""
        try:
            line_segs = LineSegs()
            line_segs.setColor(*color)
            line_segs.setThickness(4.0)
            
            # Draw pentagon outline
            num_sides = 5
            for i in range(num_sides + 1):
                angle = (i / num_sides) * 2 * math.pi - math.pi / 2  # Start from top
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                
                if i == 0:
                    line_segs.moveTo(x, y, 0.05)
                else:
                    line_segs.drawTo(x, y, 0.05)
            
            outline_node = self.base.render.attachNewNode(line_segs.create())
            outline_node.setTwoSided(True)
            outline_node.setTransparency(TransparencyAttrib.MAlpha)
            
            return outline_node
            
        except Exception as e:
            print(f"Error creating pentagon outline: {e}")
            return None
        
    def create_health_bar(self, width=40, height=4):
        """Create a health/progress bar visual element"""
        try:
            # Reduce width by 30% as requested
            width = width * 0.7
            
            # Create background (red for low health/empty progress)
            bg_card = CardMaker("health_bg")
            bg_card.setFrame(-width/2, width/2, -height/2, height/2)
            bg_node = NodePath(bg_card.generate())
            bg_node.setColor(0.3, 0.0, 0.0, 0.8)  # Dark red background
            
            # Create foreground (green for health/construction progress)
            fg_card = CardMaker("health_fg")
            fg_card.setFrame(-width/2, width/2, -height/2, height/2)
            fg_node = NodePath(fg_card.generate())
            fg_node.setColor(0.0, 0.8, 0.0, 0.9)  # Green foreground
            fg_node.reparentTo(bg_node)
            
            # Set up transparency and rendering
            bg_node.setTransparency(TransparencyAttrib.MAlpha)
            bg_node.setTwoSided(True)
            bg_node.setBillboardPointEye()  # Always face camera
            
            # Ensure health bar renders on top of buildings
            bg_node.setBin("fixed", 100)  # Render in front of other objects
            bg_node.setDepthTest(False)   # Don't use depth testing
            bg_node.setDepthWrite(False)  # Don't write to depth buffer
            
            # Store references using setPythonTag (proper Panda3D way)
            bg_node.setPythonTag("fg_node", fg_node)
            bg_node.setPythonTag("width", width)
            
            return bg_node
            
        except Exception as e:
            print(f"Error creating health bar: {e}")
            return None
    
    def update_health_bar(self, health_bar_node, progress, is_construction=False):
        """Update health bar progress (0.0 to 1.0)"""
        if not health_bar_node:
            return
            
        try:
            # Get stored references using getPythonTag
            fg_node = health_bar_node.getPythonTag("fg_node")
            width = health_bar_node.getPythonTag("width")
            
            if not fg_node or width is None:
                print("Error: Missing health bar components")
                return
            
            # Update foreground width based on progress
            progress = max(0.0, min(1.0, progress))  # Clamp to 0-1
            new_width = width * progress
            
            # Remove old foreground geometry
            fg_node.removeNode()
            
            # Create new foreground card with updated width
            fg_card = CardMaker("health_fg")
            # Set frame from left edge to progress point
            fg_card.setFrame(-width/2, -width/2 + new_width, -2, 2)
            
            # Create new foreground node
            fg_node = NodePath(fg_card.generate())
            
            # Set color based on type and progress
            if is_construction:
                # Construction: Blue to green gradient
                blue_component = 1.0 - progress * 0.3  # Start blue, less blue as progress increases
                green_component = 0.6 + progress * 0.4  # Start medium green, get brighter
                fg_node.setColor(0.2, green_component, blue_component, 0.9)
            else:
                # Health: Red to green gradient based on progress
                red = 1.0 - progress    # Full red at 0%, no red at 100%
                green = progress        # No green at 0%, full green at 100%
                fg_node.setColor(red, green, 0.0, 0.9)
            
            # Attach to health bar and set properties
            fg_node.reparentTo(health_bar_node)
            fg_node.setTransparency(TransparencyAttrib.MAlpha)
            fg_node.setTwoSided(True)
            
            # Update stored reference using setPythonTag
            health_bar_node.setPythonTag("fg_node", fg_node)
            
        except Exception as e:
            print(f"Error updating health bar: {e}")
    
    def create_3d_diamond(self, size, color):
        """Create a 3D diamond shape for mining buildings"""
        # Create geometry
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('diamond', format, Geom.UHStatic)
        vdata.setNumRows(6)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        # Diamond vertices (6 points)
        half_size = size / 2
        height = size * 0.8
        
        # Top point
        vertex.addData3f(0, 0, height)
        # Middle ring (4 points)
        vertex.addData3f(half_size, 0, 0)
        vertex.addData3f(0, half_size, 0)
        vertex.addData3f(-half_size, 0, 0)
        vertex.addData3f(0, -half_size, 0)
        # Bottom point
        vertex.addData3f(0, 0, -height)
        
        # Create triangles
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)
        
        # Top pyramid (4 triangles)
        for i in range(4):
            tris.addVertices(0, i + 1, ((i + 1) % 4) + 1)
        
        # Bottom pyramid (4 triangles)
        for i in range(4):
            tris.addVertices(5, ((i + 1) % 4) + 1, i + 1)
        
        tris.closePrimitive()
        geom.addPrimitive(tris)
        
        # Create node
        geom_node = GeomNode('diamond')
        geom_node.addGeom(geom)
        node_path = NodePath(geom_node)
        node_path.setColor(*color)
        
        return node_path
        
    def create_3d_pentagon(self, size, height, color):
        """Create a 3D pentagon prism for turret buildings"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('pentagon', format, Geom.UHStatic)
        vdata.setNumRows(10)  # 5 top + 5 bottom
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        # Pentagon vertices
        radius = size / 2
        
        # Top pentagon
        for i in range(5):
            angle = i * 2 * math.pi / 5
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertex.addData3f(x, y, height/2)
        
        # Bottom pentagon
        for i in range(5):
            angle = i * 2 * math.pi / 5
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertex.addData3f(x, y, -height/2)
        
        # Create triangles
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)
        
        # Top pentagon (fan triangulation)
        for i in range(3):
            tris.addVertices(0, i + 1, i + 2)
        
        # Bottom pentagon (fan triangulation)  
        for i in range(3):
            tris.addVertices(5, 5 + i + 2, 5 + i + 1)
        
        # Side faces
        for i in range(5):
            next_i = (i + 1) % 5
            # Two triangles per side
            tris.addVertices(i, i + 5, next_i)
            tris.addVertices(next_i, i + 5, next_i + 5)
        
        tris.closePrimitive()
        geom.addPrimitive(tris)
        
        # Create node
        geom_node = GeomNode('pentagon')
        geom_node.addGeom(geom)
        node_path = NodePath(geom_node)
        node_path.setColor(*color)
        
        return node_path
        
    def create_3d_circle(self, radius, color):
        """Create a flat circular disk"""
        try:
            format = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData('circle', format, Geom.UHStatic)
            
            # Calculate number of segments for smooth circle
            num_segments = 24
            vdata.setNumRows(num_segments + 2)  # Center + rim + first rim point again
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            
            # Center vertex
            vertex.addData3f(0, 0, 0)
            normal.addData3f(0, 0, 1)
            
            # Rim vertices
            for i in range(num_segments + 1):
                angle = (i / num_segments) * 2 * math.pi
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                vertex.addData3f(x, y, 0)
                normal.addData3f(0, 0, 1)
            
            # Create geometry
            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)
            
            # Create triangles from center to rim
            for i in range(num_segments):
                tris.addVertex(0)  # Center
                tris.addVertex(i + 1)  # Current rim point
                tris.addVertex(i + 2)  # Next rim point
                tris.closePrimitive()
            
            geom.addPrimitive(tris)
            
            # Create node
            gnode = GeomNode('circle')
            gnode.addGeom(geom)
            node = NodePath(gnode)
            node.setColor(*color)
            
            return node
            
        except Exception as e:
            print(f"Error creating 3D circle: {e}")
            return None
        
    def create_3d_sphere(self, radius, color):
        """Create a 3D sphere for connector buildings"""
        # Use a simple icosphere approximation
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('sphere', format, Geom.UHStatic)
        
        # Simple sphere using subdivided octahedron
        vertices = []
        # Octahedron vertices
        vertices.extend([
            (0, 0, radius), (0, 0, -radius),  # top, bottom
            (radius, 0, 0), (-radius, 0, 0),  # front, back
            (0, radius, 0), (0, -radius, 0)   # right, left
        ])
        
        vdata.setNumRows(len(vertices))
        vertex = GeomVertexWriter(vdata, 'vertex')
        for v in vertices:
            vertex.addData3f(*v)
        
        # Create triangles
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)
        
        # Octahedron faces
        faces = [
            (0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2),  # top
            (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)   # bottom
        ]
        
        for face in faces:
            tris.addVertices(*face)
        
        tris.closePrimitive()
        geom.addPrimitive(tris)
        
        # Create node
        geom_node = GeomNode('sphere')
        geom_node.addGeom(geom)
        node_path = NodePath(geom_node)
        node_path.setColor(*color)
        
        return node_path
        
    def create_3d_solar_panel(self, size, color):
        """Create a 3D solar panel with white border and grid lines"""
        try:
            # Create main black panel surface
            format = GeomVertexFormat.getV3()
            vdata = GeomVertexData('solar_panel', format, Geom.UHStatic)
            vdata.setNumRows(4)
            vertex = GeomVertexWriter(vdata, 'vertex')
            
            # Create a flat rectangular panel
            half_size = size / 2
            vertex.addData3f(-half_size, -half_size, 0)
            vertex.addData3f(half_size, -half_size, 0)
            vertex.addData3f(half_size, half_size, 0)
            vertex.addData3f(-half_size, half_size, 0)
            
            # Create the main panel geometry
            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)
            # Two triangles for the rectangle
            tris.addVertices(0, 1, 2)
            tris.addVertices(0, 2, 3)
            geom.addPrimitive(tris)
            
            # Create the main panel node
            panel_node = GeomNode('solar_panel')
            panel_node.addGeom(geom)
            
            # Create the complete solar panel with grid
            solar_panel = self.base.render.attachNewNode(panel_node)
            solar_panel.setColor(0.1, 0.1, 0.1, 1.0)  # Dark panel surface
            
            # Add white border outline with very thin lines
            border_lines = self.create_zoom_aware_line_segs("solar_border", 1.0, (1.0, 1.0, 1.0, 1.0))  # Much thinner lines
            
            # Draw border rectangle
            border_lines.moveTo(-half_size, -half_size, 0.01)
            border_lines.drawTo(half_size, -half_size, 0.01)
            border_lines.drawTo(half_size, half_size, 0.01)
            border_lines.drawTo(-half_size, half_size, 0.01)
            border_lines.drawTo(-half_size, -half_size, 0.01)
            
            # Add grid lines - vertical lines
            grid_lines = 6  # Number of grid divisions
            for i in range(1, grid_lines):
                x = -half_size + (i * size / grid_lines)
                border_lines.moveTo(x, -half_size, 0.01)
                border_lines.drawTo(x, half_size, 0.01)
            
            # Add grid lines - horizontal lines  
            for i in range(1, grid_lines):
                y = -half_size + (i * size / grid_lines)
                border_lines.moveTo(-half_size, y, 0.01)
                border_lines.drawTo(half_size, y, 0.01)
            
            # Attach border and grid to panel
            border_node = solar_panel.attachNewNode(border_lines.create())
            border_node.setTwoSided(True)
            
            # Make sure it renders properly
            solar_panel.setTwoSided(True)
            solar_panel.setTransparency(TransparencyAttrib.MAlpha)
            
            return solar_panel
            
        except Exception as e:
            print(f"Error creating 3D solar panel: {e}")
            return None
        
    def create_3d_hexagon(self, size, height, color):
        """Create a 3D hexagon prism for laser buildings"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('hexagon', format, Geom.UHStatic)
        vdata.setNumRows(12)  # 6 top + 6 bottom
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        # Hexagon vertices
        radius = size / 2
        
        # Top hexagon
        for i in range(6):
            angle = i * 2 * math.pi / 6
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertex.addData3f(x, y, height/2)
        
        # Bottom hexagon
        for i in range(6):
            angle = i * 2 * math.pi / 6
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertex.addData3f(x, y, -height/2)
        
        # Create triangles
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)
        
        # Top hexagon (fan triangulation)
        for i in range(4):
            tris.addVertices(0, i + 1, i + 2)
        
        # Bottom hexagon (fan triangulation)
        for i in range(4):
            tris.addVertices(6, 6 + i + 2, 6 + i + 1)
        
        # Side faces
        for i in range(6):
            next_i = (i + 1) % 6
            # Two triangles per side
            tris.addVertices(i, i + 6, next_i)
            tris.addVertices(next_i, i + 6, next_i + 6)
        
        tris.closePrimitive()
        geom.addPrimitive(tris)
        
        # Create node
        geom_node = GeomNode('hexagon')
        geom_node.addGeom(geom)
        node_path = NodePath(geom_node)
        node_path.setColor(*color)
        
        return node_path
        
    def create_3d_asteroid(self, pos_x, pos_y, radius):
        """Create a 3D polyhedral asteroid"""
        # Removed debug print to reduce spam
        
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('asteroid', format, Geom.UHStatic)
        
        # Create an irregular polyhedron (modified icosahedron)
        # Golden ratio for icosahedron
        phi = (1.0 + 5.0 ** 0.5) / 2.0
        scale = radius / 2
        
        # 12 vertices of icosahedron with some randomization
        import random
        # Use position-based seed for unique but consistent asteroids
        random.seed(int(pos_x * 1000 + pos_y * 1000) % 10000)
        
        vertices = []
        base_vertices = [
            (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
            (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
            (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)
        ]
        
        for v in base_vertices:
            # Add some randomness to make it look more asteroid-like
            x = v[0] + random.uniform(-0.3, 0.3)
            y = v[1] + random.uniform(-0.3, 0.3)
            z = v[2] + random.uniform(-0.3, 0.3)
            # Normalize and scale
            length = (x*x + y*y + z*z) ** 0.5
            vertices.append((x/length * scale, y/length * scale, z/length * scale))
        
        vdata.setNumRows(len(vertices))
        vertex = GeomVertexWriter(vdata, 'vertex')
        for v in vertices:
            vertex.addData3f(*v)
        
        # Create triangles (icosahedron faces)
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)
        
        # Icosahedron triangle indices
        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
        ]
        
        for face in faces:
            tris.addVertices(*face)
        
        tris.closePrimitive()
        geom.addPrimitive(tris)
        
        # Create node
        geom_node = GeomNode('asteroid')
        geom_node.addGeom(geom)
        node_path = NodePath(geom_node)
        node_path.setColor(0.6, 0.5, 0.3, 1.0) # Brighter brownish color for asteroid
        node_path.setPos(pos_x, pos_y, 5) # Position slightly above XY plane for better visibility
        
        # Make asteroids larger and more visible
        scale_factor = 1.5  # Make 50% larger
        node_path.setScale(scale_factor)
        
        # IMPORTANT: Attach to render tree so it's visible
        node_path.reparentTo(self.base.render)
        
        # Set asteroid to render in background behind everything else
        node_path.setBin("background", 0)  # Lowest priority in background
        node_path.setDepthOffset(1)  # Render further back
        
        # Removed debug print to reduce spam
        
        return node_path
        
    def generate_asteroid_fields(self, base_x, base_y, world_width, world_height):
        """Generate asteroid field clumps around the starting base"""
        asteroid_nodes = []
        
        # Define clump locations relative to base (3-5 clumps with 5-9 larger asteroids each)
        clump_configs = [
            {'offset': (-500, -400), 'count': 7, 'spread': 120},  # Southwest clump
            {'offset': (600, -300), 'count': 9, 'spread': 140},  # Southeast clump  
            {'offset': (-400, 500), 'count': 5, 'spread': 100},  # Northwest clump
            {'offset': (0, -700), 'count': 8, 'spread': 130},    # South clump
        ]
        
        import random
        
        for clump in clump_configs:
            clump_x = base_x + clump['offset'][0]
            clump_y = base_y + clump['offset'][1]
            
            # Skip if clump would be outside world bounds
            if (clump_x < 200 or clump_x > world_width - 200 or 
                clump_y < 200 or clump_y > world_height - 200):
                continue
                
            # Generate asteroids in this clump
            for i in range(clump['count']):
                # Random position within clump spread
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(20, clump['spread'])
                
                ast_x = clump_x + distance * math.cos(angle)
                ast_y = clump_y + distance * math.sin(angle)
                
                # Random asteroid size (much larger)
                size = random.uniform(60, 120)
                
                # Asteroid color variations (brown/gray)
                color_variation = random.uniform(0.7, 1.0)
                color = (
                    0.4 * color_variation,
                    0.3 * color_variation, 
                    0.2 * color_variation,
                    1.0
                )
                
                # Create asteroid
                asteroid = self.create_3d_asteroid(ast_x, ast_y, size)
                if asteroid:
                    asteroid.setPos(ast_x, ast_y, 0)
                    # Random rotation for variety, but keep it primarily in the H axis for top-down view
                    asteroid.setH(random.uniform(0, 360))
                    asteroid.setP(random.uniform(-10, 10))  # Reduced tilt for top-down view
                    asteroid.setR(random.uniform(-10, 10))  # Reduced roll for top-down view
                    asteroid.reparentTo(self.base.render)
                    asteroid_nodes.append(asteroid)
        
        print(f"✓ Generated {len(asteroid_nodes)} asteroids in {len(clump_configs)} clumps")
        return asteroid_nodes
        
    def generate_enhanced_asteroid_fields(self, base_x, base_y, world_width, world_height):
        """Generate enhanced asteroid field data for building system to create as asteroid buildings"""
        import random
        import math
        
        asteroid_data = []
        
        # Add 2-3 guaranteed medium asteroids close to base (reduced from 6)
        print("Generating close asteroids near starting base...")
        close_count = random.randint(2, 3)  # Reduced by factor of 2.5 (was 6)
        for i in range(close_count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(80, 200)  # Close range
            x = base_x + distance * math.cos(angle)
            y = base_y + distance * math.sin(angle)
            
            # Medium-sized asteroid for early game
            radius = random.uniform(25, 35)
            minerals = random.randint(3000, 5000)  # Medium value range
            
            asteroid_data.append({
                'x': x,
                'y': y,
                'radius': radius,
                'minerals': minerals,
                'health': minerals  # Use minerals as base health
            })
            print(f"  Close asteroid at ({x:.0f}, {y:.0f}) with {minerals} minerals")
        
        # Generate 9-15 distant clusters with 12-21 asteroids each (3x increase)
        num_clusters = random.randint(9, 15)
        print(f"Generating {num_clusters} distant asteroid clusters...")
        
        for cluster_idx in range(num_clusters):
            # Position clusters at distance 200-800 from base
            distance = random.uniform(200, 800)
            angle = random.uniform(0, 2 * math.pi)
            
            cluster_x = base_x + distance * math.cos(angle)
            cluster_y = base_y + distance * math.sin(angle)
            
            # Ensure clusters stay within world bounds
            cluster_x = max(200, min(world_width - 200, cluster_x))
            cluster_y = max(200, min(world_height - 200, cluster_y))
            
            # Generate 5-8 asteroids per cluster (reduced from 12-21 by factor of 2.5)
            cluster_size = random.randint(5, 8)
            cluster_data = self.generate_enhanced_asteroid_cluster_data(cluster_x, cluster_y, cluster_size)
            asteroid_data.extend(cluster_data)
            
            print(f"  Cluster {cluster_idx + 1}: {cluster_size} asteroids at ({cluster_x:.0f}, {cluster_y:.0f})")
        
        print(f"✓ Generated data for {len(asteroid_data)} asteroids total")
        return asteroid_data
        
    def generate_enhanced_asteroid_cluster_data(self, center_x, center_y, num_asteroids, cluster_radius=100):
        """Generate asteroid cluster data for building system to create as asteroid buildings"""
        import random
        import math
        
        cluster_data = []
        print(f"🔧 Creating cluster data at center ({center_x:.0f}, {center_y:.0f}) with {num_asteroids} asteroids")
        
        for i in range(num_asteroids):
            # Position asteroid within cluster radius
            distance = random.uniform(0, cluster_radius)
            angle = random.uniform(0, 2 * math.pi)
            
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            
            # Enhanced asteroid size and mineral value distribution
            size_roll = random.random()
            if size_roll < 0.5:  # 50% small asteroids
                radius = random.uniform(15, 25)
                minerals = random.randint(1700, 3000)  # Small: 1700-3000
            elif size_roll < 0.85:  # 35% medium asteroids  
                radius = random.uniform(25, 35)
                minerals = random.randint(3000, 5500)  # Medium: 3000-5500
            else:  # 15% large asteroids
                radius = random.uniform(35, 50)
                minerals = random.randint(5500, 8000)  # Large: 5500-8000
            
            cluster_data.append({
                'x': x,
                'y': y,
                'radius': radius,
                'minerals': minerals,
                'health': minerals  # Use minerals as base health
            })
            
        return cluster_data
    
    def create_enhanced_asteroid_cluster(self, center_x, center_y, num_asteroids, cluster_radius=100):
        """Create a cluster of asteroids with enhanced mineral values (1700-8000)"""
        import random
        import math
        
        cluster_asteroids = []
        print(f"🔧 Creating cluster at center ({center_x:.0f}, {center_y:.0f}) with {num_asteroids} asteroids")
        
        for i in range(num_asteroids):
            # Position asteroid within cluster radius
            distance = random.uniform(0, cluster_radius)
            angle = random.uniform(0, 2 * math.pi)
            
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            
            # Enhanced asteroid size and mineral value distribution
            size_roll = random.random()
            if size_roll < 0.5:  # 50% small asteroids
                radius = random.uniform(15, 25)
                minerals = random.randint(1700, 3000)  # Small: 1700-3000
            elif size_roll < 0.85:  # 35% medium asteroids  
                radius = random.uniform(25, 35)
                minerals = random.randint(3000, 5500)  # Medium: 3000-5500
            else:  # 15% large asteroids
                radius = random.uniform(35, 50)
                minerals = random.randint(5500, 8000)  # Large: 5500-8000
            
            # Create asteroid visual
            asteroid_node = self.create_3d_asteroid(x, y, radius)
            
            # Store mineral data on the asteroid node
            asteroid_node.setPythonTag("minerals", minerals)
            asteroid_node.setPythonTag("max_minerals", minerals)
            asteroid_node.setPythonTag("position", (x, y))
            asteroid_node.setPythonTag("radius", radius)
            
            cluster_asteroids.append(asteroid_node)
            
        return cluster_asteroids
        
    def create_building_placement_preview(self, building_type, x, y, radius, valid_placement=True):
        """Create a semi-transparent building preview during placement"""
        
        # Create the building visual
        building_preview = self.create_building_visual(building_type, x, y, radius)
        
        if building_preview:
            # Make it semi-transparent
            if valid_placement:
                building_preview.setColor(0.0, 1.0, 0.0, 0.5)  # Green if valid
            else:
                building_preview.setColor(1.0, 0.0, 0.0, 0.5)  # Red if invalid
                
            building_preview.setTransparency(True)
            
        # Create range indicator
        range_circle = self.create_range_indicator(radius * 2, (1.0, 1.0, 1.0, 0.3))
        if range_circle:
            range_circle.setPos(x, y, 0.1)  # Slightly above ground
            
        return building_preview, range_circle
        
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

    def create_circle_particle(self, name, radius):
        """Create a circular particle using CardMaker with a circular texture"""
        try:
            # Use CardMaker for reliable particle creation
            from panda3d.core import CardMaker, PNMImage, Texture
            card = CardMaker(name)
            card.setFrame(-radius, radius, -radius, radius)
            
            node_path = NodePath(card.generate())
            
            # Create a circular texture
            size = 32  # Texture size
            image = PNMImage(size, size, 4)  # RGBA
            center = size // 2
            
            # Draw a circle
            for y in range(size):
                for x in range(size):
                    dx = x - center
                    dy = y - center
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance <= center:
                        # Inside circle - white with alpha based on distance
                        alpha = 1.0 - (distance / center) * 0.5  # Soft edge
                        image.setXel(x, y, 1.0, 1.0, 1.0)
                        image.setAlpha(x, y, alpha)
                    else:
                        # Outside circle - transparent
                        image.setXel(x, y, 0.0, 0.0, 0.0)
                        image.setAlpha(x, y, 0.0)
            
            # Create texture from image
            texture = Texture()
            texture.load(image)
            node_path.setTexture(texture)
            
            # Make it visible and properly rendered
            node_path.setTwoSided(True)
            node_path.setBillboardPointEye()  # Always face camera
            node_path.setTransparency(TransparencyAttrib.MAlpha)
            
            return node_path
            
        except Exception as e:
            print(f"Error creating circle particle: {e}")
            # Fallback to basic card
            from panda3d.core import CardMaker
            card = CardMaker(name)
            card.setFrame(-radius, radius, -radius, radius)
            node_path = NodePath(card.generate())
            node_path.setTwoSided(True)
            node_path.setBillboardPointEye()
            node_path.setTransparency(TransparencyAttrib.MAlpha)
            return node_path

    def create_zoom_aware_line_segs(self, name="line", base_thickness=2.0, color=(1.0, 1.0, 1.0, 1.0)):
        """Create a LineSegs object with thickness that scales with camera zoom
        
        Args:
            name: Name for the LineSegs object
            base_thickness: Base thickness in pixels (will be multiplied by zoom)
            color: RGBA color tuple
            
        Returns:
            LineSegs object with zoom-scaled thickness
        """
        from panda3d.core import LineSegs
        
        # Get zoom factor for thickness scaling
        zoom_factor = 1.0
        if hasattr(self.base, 'game_engine') and hasattr(self.base.game_engine, 'camera'):
            zoom_factor = self.base.game_engine.camera.zoom
        
        # Create LineSegs with scaled thickness
        line_segs = LineSegs(name)
        line_segs.setThickness(base_thickness * zoom_factor)
        line_segs.setColor(*color)
        
        return line_segs

    def create_thin_rectangle_line(self, start_x, start_y, end_x, end_y, thickness=2.0, color=(1.0, 1.0, 1.0, 1.0), name="rect_line"):
        """Create a thin rectangle that acts as a zoom-aware line
        
        Args:
            start_x, start_y: Start coordinates
            end_x, end_y: End coordinates  
            thickness: Thickness in world units (will scale with zoom naturally)
            color: RGBA color tuple
            name: Name for the geometry
            
        Returns:
            NodePath containing the rectangle line
        """
        try:
            import math
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
            
            # Add vertices for rectangle corners
            vertex.addData3f(start_x + perp_x, start_y + perp_y, 0)  # Bottom-left
            vertex.addData3f(start_x - perp_x, start_y - perp_y, 0)  # Top-left
            vertex.addData3f(end_x - perp_x, end_y - perp_y, 0)     # Top-right
            vertex.addData3f(end_x + perp_x, end_y + perp_y, 0)     # Bottom-right
            
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
                from panda3d.core import TransparencyAttrib
                node_path.setTransparency(TransparencyAttrib.MAlpha)
            
            return node_path
            
        except Exception as e:
            print(f"Error creating rectangle line: {e}")
            return None

    def create_mining_laser_effect(self, start_x, start_y, end_x, end_y, asteroid_radius=25):
        """Create a mining laser with random target point within asteroid and render on top"""
        try:
            import random
            import math
            
            # Generate random point within 2/3 of asteroid radius for more concentrated impact
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, asteroid_radius * 0.67)  # 2/3 of radius instead of 80%
            
            target_x = end_x + distance * math.cos(angle)
            target_y = end_y + distance * math.sin(angle)
            
            # Create main laser beam using thin rectangle (auto zoom-aware)
            laser_path = self.create_thin_rectangle_line(
                start_x, start_y, target_x, target_y, 
                thickness=3.0, color=(0.3, 0.9, 0.3, 0.9), name="laser_main"
            )
            
            if not laser_path:
                return None
                
            laser_path.reparentTo(self.base.render)
            
            # Create outer glow layer
            outer_path = self.create_thin_rectangle_line(
                start_x, start_y, target_x, target_y,
                thickness=5.0, color=(0.1, 0.6, 0.1, 0.3), name="laser_glow"
            )
            if outer_path:
                outer_path.reparentTo(laser_path)
            
            # Create inner bright core
            inner_path = self.create_thin_rectangle_line(
                start_x, start_y, target_x, target_y,
                thickness=1.0, color=(0.6, 1.0, 0.6, 1.0), name="laser_core"
            )
            if inner_path:
                inner_path.reparentTo(laser_path)
            
            # Render on top of asteroids
            laser_path.setBin("fixed", 100)  # Higher than asteroids
            laser_path.setDepthTest(False)
            laser_path.setDepthWrite(False)
            
            # Set transparency
            laser_path.setTransparency(TransparencyAttrib.MAlpha)
            
            # Add dynamic lighting effect from the laser
            from panda3d.core import PointLight
            light = PointLight('laser_light')
            light.setColor(VBase4(0.3, 1.0, 0.3, 1)) # Bright green light
            light_np = laser_path.attachNewNode(light)
            # Position light at the target end of the laser relative to laser_path's origin
            light_np.setPos(target_x - start_x, target_y - start_y, 0) 
            self.base.render.setLight(light_np)
            
            # Store light in laser_path for easy access during fade
            laser_path.setPythonTag("light", light_np)
            
            # Start fade task
            self.base.taskMgr.add(self._animate_laser_fadeout, f"laser_fade_{id(laser_path)}",
                                extraArgs=[laser_path, light_np], appendTask=True)
            
            return laser_path
        except Exception as e:
            print(f"Error creating mining laser effect: {e}")
            return None
    
    def create_mining_dust_effect(self, x, y):
        """Create a realistic dust cloud particle effect at the asteroid location"""
        try:
            # Create dust particles using simple geometry
            dust_root = NodePath("dust_effect")
            dust_root.reparentTo(self.base.render)
            dust_root.setPos(x, y, 0)
            
            # Set dust particles to render on top of everything
            dust_root.setBin("fixed", 200)  # Highest priority in fixed bin
            dust_root.setDepthTest(False)   # Don't use depth testing
            dust_root.setDepthWrite(False)  # Don't write to depth buffer
            
            # Create multiple small dust particles with varied properties
            import random
            num_particles = random.randint(12, 20)  # Random number of particles
            
            for i in range(num_particles):
                # Create circular dust particle with random size
                particle_size = random.uniform(1.5, 4.0)
                dust_node = self.create_circle_particle(f"dust_{i}", particle_size)
                dust_node.reparentTo(dust_root)
                
                # Random position with clustered distribution (more realistic)
                cluster_radius = random.uniform(3, 8)
                angle = random.uniform(0, 6.28)  # 2*PI
                offset_x = cluster_radius * math.cos(angle) + random.uniform(-3, 3)
                offset_y = cluster_radius * math.sin(angle) + random.uniform(-3, 3)
                dust_node.setPos(offset_x, offset_y, random.uniform(0, 3))
                
                # Varied brown/tan dust colors with some randomness
                red = random.uniform(0.5, 0.7)
                green = random.uniform(0.3, 0.5)
                blue = random.uniform(0.1, 0.3)
                alpha = random.uniform(0.6, 0.9)
                dust_node.setColor(red, green, blue, alpha)
                dust_node.setTransparency(TransparencyAttrib.MAlpha)
                dust_node.setBillboardPointEye()
                
                # Random initial scale
                initial_scale = random.uniform(0.5, 1.2)
                dust_node.setScale(initial_scale)
                
                # Store velocity for individual particle movement
                dust_node.setPythonTag("velocity", (
                    random.uniform(-15, 15),  # x velocity
                    random.uniform(-15, 15),  # y velocity
                    random.uniform(0, 8)      # z velocity
                ))
                dust_node.setPythonTag("life", random.uniform(1.2, 2.0))  # Lifetime
                
            # Animate dust expansion and fade with individual particle movement
            self._animate_dust_effect(dust_root, 1.5)
            
            return dust_root
            
        except Exception as e:
            print(f"Error creating mining dust effect: {e}")
    
    def _animate_laser_fadeout(self, laser_path, light_np, task):
        """Animate laser beam fading out with both transparency and thickness reduction"""
        fade_duration = 1.5
        
        if task.time > fade_duration:
            # Clean up light before removing laser
            self.base.render.clearLight(light_np)
            light_np.removeNode()
            
            # Remove laser geometry
            laser_path.removeNode()
            return task.done
            
        # Calculate fade progress (0 to 1)
        progress = task.time / fade_duration
        
        # Fade alpha from 1.0 to 0.0 (simple fade out)
        alpha = 1.0 - progress
        
        # Apply alpha to main laser and children (glow, core)
        laser_path.setAlphaScale(alpha)
        
        # Fade light intensity
        light = light_np.node()
        original_color = (0.3, 1.0, 0.3, 1.0)
        faded_color = (
            original_color[0] * alpha,
            original_color[1] * alpha,
            original_color[2] * alpha,
            original_color[3]
        )
        light.setColor(VBase4(*faded_color))
        
        return task.cont
    
    def _animate_dust_effect(self, dust_root, duration):
        """Animate dust particles expanding and fading"""
        def dust_task(task):
            if task.time > duration:
                dust_root.removeNode()
                return task.done
                
            # Calculate expansion and fade
            progress = task.time / duration
            scale = 1.0 + progress * 2.0  # Expand to 3x size
            alpha = 1.0 - progress  # Fade out
            
            dust_root.setScale(scale)
            dust_root.setColorScale(1, 1, 1, alpha)
            
            return task.cont
            
        # Start dust animation task
        self.base.taskMgr.add(dust_task, f"dust_effect_{id(dust_root)}") 
    
    def create_conversion_effect(self, x, y):
        """Create a visual effect for energy-to-mineral conversion"""
        try:
            # Create sparkle effect using particles
            sparkle_root = NodePath("conversion_effect")
            sparkle_root.reparentTo(self.base.render)
            sparkle_root.setPos(x, y, 10)  # Above the building
            
            # Set sparkle particles to render on top of everything
            sparkle_root.setBin("fixed", 200)  # Highest priority in fixed bin
            sparkle_root.setDepthTest(False)   # Don't use depth testing
            sparkle_root.setDepthWrite(False)  # Don't write to depth buffer
            
            # Create multiple sparkle particles
            import random
            for i in range(12):
                # Create circular sparkle particle
                sparkle_node = self.create_circle_particle(f"sparkle_{i}", 1.0)
                sparkle_node.reparentTo(sparkle_root)
                
                # Random position around the building
                offset_x = random.uniform(-15, 15)
                offset_y = random.uniform(-15, 15)
                sparkle_node.setPos(offset_x, offset_y, random.uniform(-5, 5))
                
                # Orange/yellow conversion color
                sparkle_node.setColor(1.0, 0.8, 0.2, 1.0)
                sparkle_node.setTransparency(TransparencyAttrib.MAlpha)
                sparkle_node.setBillboardPointEye()
                
            # Animate sparkle effect
            self._animate_sparkle_effect(sparkle_root, 1.0)
            
            return sparkle_root
            
        except Exception as e:
            print(f"Error creating conversion effect: {e}")
            return None
    
    def create_building_placement_effect(self, x, y):
        """Create visual effect when a building is placed"""
        try:
            # Create placement burst effect
            burst_root = NodePath("placement_effect")
            burst_root.reparentTo(self.base.render)
            burst_root.setPos(x, y, 5)
            
            # Set placement particles to render on top of everything
            burst_root.setBin("fixed", 200)  # Highest priority in fixed bin
            burst_root.setDepthTest(False)   # Don't use depth testing
            burst_root.setDepthWrite(False)  # Don't write to depth buffer
            
            # Create scattered particles instead of perfect ring
            import random
            import math
            num_particles = random.randint(8, 15)  # Fewer particles
            
            for i in range(num_particles):
                # Random angle and distance for more natural spread (tighter)
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(4, 12)  # Much tighter radius
                
                # Create circular burst particle with smaller random size
                particle_size = random.uniform(0.2, 0.6)  # Even smaller particles
                burst_node = self.create_circle_particle(f"burst_{i}", particle_size)
                burst_node.reparentTo(burst_root)
                
                # Position with less randomness (tighter)
                pos_x = distance * math.cos(angle) + random.uniform(-1.5, 1.5)
                pos_y = distance * math.sin(angle) + random.uniform(-1.5, 1.5)
                pos_z = random.uniform(-0.5, 2)
                burst_node.setPos(pos_x, pos_y, pos_z)
                
                # Varied blue/white placement colors
                red = random.uniform(0.7, 1.0)
                green = random.uniform(0.8, 1.0)
                blue = 1.0
                alpha = random.uniform(0.8, 1.0)
                burst_node.setColor(red, green, blue, alpha)
                burst_node.setTransparency(TransparencyAttrib.MAlpha)
                burst_node.setBillboardPointEye()
                
                # Random initial scale (smaller)
                initial_scale = random.uniform(0.4, 0.8)
                burst_node.setScale(initial_scale)
                
                # Store velocity for outward movement
                vel_multiplier = random.uniform(0.6, 1.0)  # Slower spread
                burst_node.setPythonTag("velocity", (
                    math.cos(angle) * vel_multiplier * 10,
                    math.sin(angle) * vel_multiplier * 10,
                    random.uniform(-2, 8)
                ))
                
            # Animate burst effect
            self._animate_burst_effect(burst_root, 0.8)
            
            return burst_root
            
        except Exception as e:
            print(f"Error creating building placement effect: {e}")
            return None
    
    def _animate_sparkle_effect(self, sparkle_root, duration):
        """Animate sparkle particles rising and fading"""
        def sparkle_task(task):
            if task.time > duration:
                sparkle_root.removeNode()
                return task.done
                
            # Calculate rising motion and fade
            progress = task.time / duration
            rise = progress * 20  # Rise 20 units
            alpha = 1.0 - progress  # Fade out
            
            sparkle_root.setZ(10 + rise)
            sparkle_root.setColorScale(1, 1, 1, alpha)
            
            return task.cont
            
        # Start sparkle animation task
        self.base.taskMgr.add(sparkle_task, f"sparkle_effect_{id(sparkle_root)}")
    
    def _animate_burst_effect(self, burst_root, duration):
        """Animate burst particles expanding outward"""
        def burst_task(task):
            if task.time > duration:
                burst_root.removeNode()
                return task.done
                
            # Calculate expansion and fade
            progress = task.time / duration
            scale = 1.0 + progress * 3.0  # Expand to 4x size
            alpha = 1.0 - progress  # Fade out
            
            burst_root.setScale(scale)
            burst_root.setColorScale(1, 1, 1, alpha)
            
            return task.cont
            
        # Start burst animation task
        self.base.taskMgr.add(burst_task, f"burst_effect_{id(burst_root)}") 