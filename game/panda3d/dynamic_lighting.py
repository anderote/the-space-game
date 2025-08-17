"""
Dynamic Lighting System for Space Game
Handles multiple types of dynamic lights that respond to game events
"""

from panda3d.core import (
    PointLight, AmbientLight, DirectionalLight,
    Vec3, Vec4, LVector3, LColor,
    PandaNode, NodePath
)
import math
import random


class DynamicLightingManager:
    """Manages dynamic lighting effects for the space game"""
    
    def __init__(self, base, render_node):
        self.base = base
        self.render = render_node
        
        # Light storage
        self.dynamic_lights = {}
        self.light_effects = {}
        self.next_light_id = 0
        
        # Enhanced material properties
        self.setup_enhanced_materials()
        
        # Animation timers
        self.time = 0.0
        
    def setup_enhanced_materials(self):
        """Set up enhanced material properties for better lighting"""
        # Enable automatic normal generation for better lighting
        from panda3d.core import RenderState, ShadeModelAttrib
        
        # Set up render states for better lighting
        self.render.setShaderAuto()  # Enable automatic shader generation
        
        # Enable two-sided lighting for thin geometry
        from panda3d.core import CullFaceAttrib
        self.render.setTwoSided(True)
        
        print("✓ Enhanced materials and lighting setup complete")
    
    def update(self, dt):
        """Update dynamic lighting effects"""
        self.time += dt
        
        # Update animated lights
        for light_id, effect_data in list(self.light_effects.items()):
            if not self._update_light_effect(light_id, effect_data, dt):
                # Effect finished, clean up
                self.remove_light(light_id)
    
    def _update_light_effect(self, light_id, effect_data, dt):
        """Update a specific light effect"""
        effect_type = effect_data['type']
        
        if light_id not in self.dynamic_lights:
            return False
            
        light_np = self.dynamic_lights[light_id]['node']
        light = self.dynamic_lights[light_id]['light']
        
        try:
            if effect_type == 'pulse':
                return self._update_pulse_effect(light, effect_data, dt)
            elif effect_type == 'flicker':
                return self._update_flicker_effect(light, effect_data, dt)
            elif effect_type == 'explosion':
                return self._update_explosion_effect(light, light_np, effect_data, dt)
            elif effect_type == 'weapon_flash':
                return self._update_weapon_flash_effect(light, effect_data, dt)
            elif effect_type == 'engine_glow':
                return self._update_engine_glow_effect(light, effect_data, dt)
            elif effect_type == 'building_glow':
                return self._update_building_glow_effect(light, effect_data, dt)
                
        except Exception as e:
            print(f"Error updating light effect {light_id}: {e}")
            return False
            
        return True
    
    def _update_pulse_effect(self, light, effect_data, dt):
        """Update pulsing light effect"""
        effect_data['phase'] = effect_data.get('phase', 0) + dt * effect_data.get('speed', 2.0)
        effect_data['lifetime'] -= dt
        
        if effect_data['lifetime'] <= 0:
            return False
            
        # Calculate pulse intensity
        pulse = (math.sin(effect_data['phase']) + 1) * 0.5
        base_intensity = effect_data.get('base_intensity', 1.0)
        pulse_intensity = effect_data.get('pulse_intensity', 0.5)
        
        intensity = base_intensity + pulse * pulse_intensity
        
        # Apply to light
        base_color = effect_data.get('base_color', (1, 1, 1, 1))
        light.setColor(LColor(base_color[0] * intensity, base_color[1] * intensity, 
                             base_color[2] * intensity, base_color[3]))
        
        return True
    
    def _update_flicker_effect(self, light, effect_data, dt):
        """Update flickering light effect"""
        effect_data['lifetime'] -= dt
        effect_data['flicker_timer'] = effect_data.get('flicker_timer', 0) - dt
        
        if effect_data['lifetime'] <= 0:
            return False
            
        # Random flicker
        if effect_data['flicker_timer'] <= 0:
            effect_data['flicker_timer'] = random.uniform(0.05, 0.3)
            effect_data['current_intensity'] = random.uniform(0.3, 1.0)
            
        base_color = effect_data.get('base_color', (1, 1, 1, 1))
        intensity = effect_data.get('current_intensity', 1.0)
        
        light.setColor(LColor(base_color[0] * intensity, base_color[1] * intensity,
                             base_color[2] * intensity, base_color[3]))
        
        return True
    
    def _update_explosion_effect(self, light, light_np, effect_data, dt):
        """Update explosion light effect"""
        effect_data['lifetime'] -= dt
        
        if effect_data['lifetime'] <= 0:
            return False
            
        # Explosion expands and fades
        progress = 1.0 - (effect_data['lifetime'] / effect_data.get('max_lifetime', 1.0))
        
        # Intensity starts high and fades
        intensity = max(0, 1.0 - progress * 2)
        
        # Range expands
        max_range = effect_data.get('max_range', 100)
        current_range = progress * max_range
        
        # Apply effects
        base_color = effect_data.get('base_color', (1, 0.5, 0, 1))  # Orange explosion
        light.setColor(LColor(base_color[0] * intensity, base_color[1] * intensity,
                             base_color[2] * intensity, base_color[3]))
        
        # Update attenuation for expanding effect
        light.setAttenuation(1.0, 0.01, 0.001)
        
        return True
    
    def _update_weapon_flash_effect(self, light, effect_data, dt):
        """Update weapon flash effect"""
        effect_data['lifetime'] -= dt
        
        if effect_data['lifetime'] <= 0:
            return False
            
        # Sharp flash that fades quickly
        progress = 1.0 - (effect_data['lifetime'] / effect_data.get('max_lifetime', 0.2))
        intensity = max(0, 1.0 - progress * 4)  # Fast fade
        
        base_color = effect_data.get('base_color', (1, 1, 1, 1))
        light.setColor(LColor(base_color[0] * intensity, base_color[1] * intensity,
                             base_color[2] * intensity, base_color[3]))
        
        return True
    
    def _update_engine_glow_effect(self, light, effect_data, dt):
        """Update engine glow effect"""
        # Infinite duration engine glow with subtle variations
        effect_data['phase'] = effect_data.get('phase', 0) + dt * 3.0
        
        # Subtle intensity variation
        variation = math.sin(effect_data['phase']) * 0.1
        base_intensity = effect_data.get('base_intensity', 0.8)
        intensity = base_intensity + variation
        
        base_color = effect_data.get('base_color', (0, 0.5, 1, 1))  # Blue engine glow
        light.setColor(LColor(base_color[0] * intensity, base_color[1] * intensity,
                             base_color[2] * intensity, base_color[3]))
        
        return True  # Never expires
    
    def _update_building_glow_effect(self, light, effect_data, dt):
        """Update building operational glow"""
        # Gentle breathing effect for operational buildings
        effect_data['phase'] = effect_data.get('phase', 0) + dt * 1.0
        
        # Very subtle intensity variation
        variation = math.sin(effect_data['phase']) * 0.05
        base_intensity = effect_data.get('base_intensity', 0.6)
        intensity = base_intensity + variation
        
        base_color = effect_data.get('base_color', (0.2, 0.8, 0.2, 1))  # Green operational glow
        light.setColor(LColor(base_color[0] * intensity, base_color[1] * intensity,
                             base_color[2] * intensity, base_color[3]))
        
        return True  # Never expires
    
    def create_building_light(self, x, y, z, building_type, building_state):
        """Create dynamic lighting for a building"""
        light_id = self._get_next_light_id()
        
        # Different lighting based on building type and state
        if building_type in ['solar', 'nuclear']:
            return self._create_power_building_light(light_id, x, y, z, building_type, building_state)
        elif building_type in ['turret', 'laser', 'superlaser', 'missile_launcher']:
            return self._create_weapon_building_light(light_id, x, y, z, building_type, building_state)
        elif building_type == 'miner':
            return self._create_miner_light(light_id, x, y, z, building_state)
        elif building_type == 'repair':
            return self._create_repair_light(light_id, x, y, z, building_state)
        else:
            return self._create_generic_building_light(light_id, x, y, z, building_state)
    
    def _create_power_building_light(self, light_id, x, y, z, building_type, building_state):
        """Create lighting for power generation buildings"""
        if building_state != 'OPERATIONAL':
            return None
            
        # Create point light
        light = PointLight(f'power_light_{light_id}')
        
        if building_type == 'nuclear':
            # Nuclear - bright blue-white glow
            color = (0.8, 0.9, 1.0, 1.0)
            intensity = 1.2
            range_val = 80
        else:  # solar
            # Solar - warm yellow glow
            color = (1.0, 0.9, 0.6, 1.0)
            intensity = 0.8
            range_val = 60
            
        light.setColor(LColor(color[0] * intensity, color[1] * intensity, 
                             color[2] * intensity, color[3]))
        # Set basic attenuation values directly
        light.setAttenuation(1.0, 0.02, 0.001)
        
        # Create node and position
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 10)
        
        # Enable lighting on render tree
        self.render.setLight(light_np)
        
        # Store light
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'building',
            'building_type': building_type
        }
        
        # Add breathing glow effect
        self.light_effects[light_id] = {
            'type': 'building_glow',
            'base_color': color,
            'base_intensity': intensity,
            'phase': random.uniform(0, math.pi * 2)
        }
        
        return light_id
    
    def _create_weapon_building_light(self, light_id, x, y, z, building_type, building_state):
        """Create lighting for weapon buildings"""
        if building_state != 'OPERATIONAL':
            return None
            
        light = PointLight(f'weapon_light_{light_id}')
        
        if building_type == 'laser' or building_type == 'superlaser':
            # Laser - bright red glow
            color = (1.0, 0.2, 0.2, 1.0)
            intensity = 0.9
        elif building_type == 'missile_launcher':
            # Missile launcher - orange glow
            color = (1.0, 0.6, 0.2, 1.0)
            intensity = 0.7
        else:  # turret
            # Turret - white with blue tint
            color = (0.9, 0.9, 1.0, 1.0)
            intensity = 0.6
            
        light.setColor(LColor(color[0] * intensity, color[1] * intensity,
                             color[2] * intensity, color[3]))
        light.setAttenuation(1.0, 0.03, 0.002)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 8)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'building',
            'building_type': building_type
        }
        
        # Add subtle pulse effect
        self.light_effects[light_id] = {
            'type': 'pulse',
            'base_color': color,
            'base_intensity': intensity * 0.7,
            'pulse_intensity': intensity * 0.3,
            'speed': 1.5,
            'lifetime': float('inf'),
            'phase': random.uniform(0, math.pi * 2)
        }
        
        return light_id
    
    def _create_miner_light(self, light_id, x, y, z, building_state):
        """Create lighting for miner buildings"""
        if building_state != 'OPERATIONAL':
            return None
            
        light = PointLight(f'miner_light_{light_id}')
        color = (0.2, 1.0, 0.8, 1.0)  # Cyan mining laser color
        intensity = 0.8
        
        light.setColor(LColor(color[0] * intensity, color[1] * intensity,
                             color[2] * intensity, color[3]))
        light.setAttenuation(1.0, 0.025, 0.002)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 6)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'building',
            'building_type': 'miner'
        }
        
        # Flickering effect for mining activity
        self.light_effects[light_id] = {
            'type': 'flicker',
            'base_color': color,
            'lifetime': float('inf'),
            'current_intensity': intensity
        }
        
        return light_id
    
    def _create_repair_light(self, light_id, x, y, z, building_state):
        """Create lighting for repair buildings"""
        if building_state != 'OPERATIONAL':
            return None
            
        light = PointLight(f'repair_light_{light_id}')
        color = (0.2, 1.0, 0.2, 1.0)  # Green healing color
        intensity = 0.7
        
        light.setColor(LColor(color[0] * intensity, color[1] * intensity,
                             color[2] * intensity, color[3]))
        # Set basic attenuation values directly
        light.setAttenuation(1.0, 0.02, 0.001)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 8)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'building',
            'building_type': 'repair'
        }
        
        # Gentle pulse for healing
        self.light_effects[light_id] = {
            'type': 'pulse',
            'base_color': color,
            'base_intensity': intensity * 0.6,
            'pulse_intensity': intensity * 0.4,
            'speed': 2.0,
            'lifetime': float('inf'),
            'phase': random.uniform(0, math.pi * 2)
        }
        
        return light_id
    
    def _create_generic_building_light(self, light_id, x, y, z, building_state):
        """Create generic building lighting"""
        if building_state not in ['OPERATIONAL', 'UNDER_CONSTRUCTION']:
            return None
            
        light = PointLight(f'building_light_{light_id}')
        
        if building_state == 'UNDER_CONSTRUCTION':
            color = (1.0, 0.8, 0.4, 1.0)  # Warm construction glow
            intensity = 0.5
        else:
            color = (0.6, 0.8, 1.0, 1.0)  # Cool operational glow
            intensity = 0.4
            
        light.setColor(LColor(color[0] * intensity, color[1] * intensity,
                             color[2] * intensity, color[3]))
        light.setAttenuation(1.0, 0.04, 0.003)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 5)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'building',
            'building_type': 'generic'
        }
        
        return light_id
    
    def create_enemy_light(self, x, y, z, enemy_type):
        """Create dynamic lighting for enemies"""
        light_id = self._get_next_light_id()
        
        light = PointLight(f'enemy_light_{light_id}')
        
        # Different colors based on enemy type
        if enemy_type in ['laser_mothership', 'dreadnought']:
            color = (1.0, 0.3, 0.3, 1.0)  # Red menacing glow
            intensity = 1.5
            range_val = 100
        elif enemy_type in ['carrier', 'missile_cruiser']:
            color = (1.0, 0.6, 0.2, 1.0)  # Orange threat glow
            intensity = 1.2
            range_val = 80
        elif enemy_type == 'support_ship':
            color = (0.2, 1.0, 0.2, 1.0)  # Green support glow
            intensity = 0.8
            range_val = 60
        elif enemy_type == 'interceptor':
            color = (1.0, 1.0, 0.3, 1.0)  # Yellow speed glow
            intensity = 0.9
            range_val = 40
        else:
            color = (1.0, 0.5, 0.5, 1.0)  # Default red
            intensity = 0.7
            range_val = 50
            
        light.setColor(LColor(color[0] * intensity, color[1] * intensity,
                             color[2] * intensity, color[3]))
        light.setAttenuation(1.0, 0.03, 0.002)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 5)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'enemy',
            'enemy_type': enemy_type
        }
        
        # Add engine glow effect for enemies
        self.light_effects[light_id] = {
            'type': 'engine_glow',
            'base_color': color,
            'base_intensity': intensity,
            'phase': random.uniform(0, math.pi * 2)
        }
        
        return light_id
    
    def create_weapon_flash(self, x, y, z, weapon_type):
        """Create a brief flash when weapons fire"""
        light_id = self._get_next_light_id()
        
        light = PointLight(f'flash_light_{light_id}')
        
        if weapon_type == 'laser':
            color = (1.0, 0.2, 0.2, 1.0)  # Bright red
            duration = 0.15
        elif weapon_type == 'missile':
            color = (1.0, 0.6, 0.2, 1.0)  # Orange
            duration = 0.3
        else:  # bullet
            color = (1.0, 1.0, 0.8, 1.0)  # White-yellow
            duration = 0.1
            
        light.setColor(LColor(color[0], color[1], color[2], color[3]))
        light.setAttenuation(1.0, 0.05, 0.01)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 3)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'effect'
        }
        
        self.light_effects[light_id] = {
            'type': 'weapon_flash',
            'base_color': color,
            'lifetime': duration,
            'max_lifetime': duration
        }
        
        return light_id
    
    def create_explosion_light(self, x, y, z, explosion_type='normal'):
        """Create an explosion light effect"""
        light_id = self._get_next_light_id()
        
        light = PointLight(f'explosion_light_{light_id}')
        
        if explosion_type == 'missile':
            color = (1.0, 0.7, 0.3, 1.0)  # Orange-yellow
            duration = 1.5
            max_range = 120
        elif explosion_type == 'enemy_death':
            color = (1.0, 0.4, 0.1, 1.0)  # Bright orange
            duration = 1.0
            max_range = 80
        else:  # normal
            color = (1.0, 0.6, 0.2, 1.0)  # Orange
            duration = 0.8
            max_range = 60
            
        light.setColor(LColor(color[0], color[1], color[2], color[3]))
        light.setAttenuation(1.0, 0.01, 0.001)
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(x, y, z + 5)
        self.render.setLight(light_np)
        
        self.dynamic_lights[light_id] = {
            'light': light,
            'node': light_np,
            'type': 'effect'
        }
        
        self.light_effects[light_id] = {
            'type': 'explosion',
            'base_color': color,
            'lifetime': duration,
            'max_lifetime': duration,
            'max_range': max_range
        }
        
        return light_id
    
    def update_light_position(self, light_id, x, y, z):
        """Update the position of a dynamic light (for moving enemies)"""
        if light_id in self.dynamic_lights:
            self.dynamic_lights[light_id]['node'].setPos(x, y, z + 5)
    
    def remove_light(self, light_id):
        """Remove a dynamic light"""
        if light_id in self.dynamic_lights:
            light_data = self.dynamic_lights[light_id]
            self.render.clearLight(light_data['node'])
            light_data['node'].removeNode()
            del self.dynamic_lights[light_id]
            
        if light_id in self.light_effects:
            del self.light_effects[light_id]
    
    def _get_next_light_id(self):
        """Get the next available light ID"""
        light_id = self.next_light_id
        self.next_light_id += 1
        return light_id
    
    def cleanup(self):
        """Clean up all dynamic lights"""
        for light_id in list(self.dynamic_lights.keys()):
            self.remove_light(light_id)
        
        print("✓ Dynamic lighting cleanup complete")
