"""
Main game window for Arcade implementation with shader support.
"""

import arcade
import arcade.gl as gl
from typing import Optional
from .engine import ArcadeGameEngine


class SpaceGameWindow(arcade.Window):
    """Main game window with shader support and modern graphics."""
    
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title, resizable=True)
        
        # Game engine
        self.game_engine: Optional[ArcadeGameEngine] = None
        
        # Shader programs
        self.particle_shader: Optional[gl.Program] = None
        self.post_process_shader: Optional[gl.Program] = None
        self.lighting_shader: Optional[gl.Program] = None
        
        # Framebuffers for post-processing
        self.main_framebuffer: Optional[gl.Framebuffer] = None
        self.bloom_framebuffer: Optional[gl.Framebuffer] = None
        
        # Performance tracking
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = 0
        
        # Set background color
        arcade.set_background_color(arcade.color.BLACK)
        
    def setup(self):
        """Initialize the game window and all systems."""
        print("Setting up Space Game - Arcade Edition...")
        
        # Initialize shaders
        self._setup_shaders()
        
        # Initialize framebuffers
        self._setup_framebuffers()
        
        # Create game engine
        self.game_engine = ArcadeGameEngine(self)
        
        # Setup game engine
        self.game_engine.setup()
        
        print("Space Game setup complete!")
        
    def _setup_shaders(self):
        """Initialize shader programs."""
        try:
            # Load shader programs
            self.particle_shader = self._load_particle_shader()
            self.post_process_shader = self._load_post_process_shader()
            self.lighting_shader = self._load_lighting_shader()
            
            print("Shaders loaded successfully")
            
        except Exception as e:
            print(f"Warning: Could not load shaders: {e}")
            print("Falling back to basic rendering")
            
    def _load_particle_shader(self) -> gl.Program:
        """Load particle system shader."""
        vertex_shader = """
        #version 330 core
        
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec3 color;
        layout (location = 2) in float size;
        layout (location = 3) in float life;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform float time;
        
        out vec3 fragColor;
        out float fragLife;
        
        void main() {
            gl_Position = projection * view * vec4(position, 0.0, 1.0);
            gl_PointSize = size * (1.0 - life);
            fragColor = color;
            fragLife = life;
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 fragColor;
        in float fragLife;
        
        out vec4 FragColor;
        
        void main() {
            vec2 coord = gl_PointCoord - vec2(0.5);
            float distance = length(coord);
            
            if (distance > 0.5) discard;
            
            float alpha = (1.0 - distance * 2.0) * fragLife;
            FragColor = vec4(fragColor, alpha);
        }
        """
        
        return self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
    def _load_post_process_shader(self) -> gl.Program:
        """Load post-processing shader for bloom effect."""
        vertex_shader = """
        #version 330 core
        
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec2 tex_coords;
        
        out vec2 TexCoords;
        
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
            TexCoords = tex_coords;
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec2 TexCoords;
        out vec4 FragColor;
        
        uniform sampler2D screenTexture;
        uniform float bloom_threshold;
        uniform float bloom_intensity;
        
        void main() {
            vec3 color = texture(screenTexture, TexCoords).rgb;
            float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));
            
            if (brightness > bloom_threshold) {
                FragColor = vec4(color * bloom_intensity, 1.0);
            } else {
                FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            }
        }
        """
        
        return self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
    def _load_lighting_shader(self) -> gl.Program:
        """Load lighting shader for dynamic lighting effects."""
        vertex_shader = """
        #version 330 core
        
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec2 tex_coords;
        
        out vec2 TexCoords;
        
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
            TexCoords = tex_coords;
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec2 TexCoords;
        out vec4 FragColor;
        
        uniform sampler2D screenTexture;
        uniform vec2 light_positions[10];
        uniform vec3 light_colors[10];
        uniform int light_count;
        uniform vec2 screen_size;
        
        void main() {
            vec3 color = texture(screenTexture, TexCoords).rgb;
            vec3 lighting = vec3(0.1); // ambient lighting
            
            vec2 pixel_pos = TexCoords * screen_size;
            
            for (int i = 0; i < light_count; i++) {
                float distance = length(light_positions[i] - pixel_pos);
                float attenuation = 1.0 / (1.0 + distance * distance * 0.0001);
                lighting += light_colors[i] * attenuation;
            }
            
            FragColor = vec4(color * lighting, 1.0);
        }
        """
        
        return self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
    def _setup_framebuffers(self):
        """Setup framebuffers for post-processing effects."""
        # Main framebuffer for rendering
        self.main_framebuffer = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.width, self.height), 4)]
        )
        
        # Bloom framebuffer for glow effects
        self.bloom_framebuffer = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.width, self.height), 4)]
        )
        
    def on_draw(self):
        """Main rendering loop with post-processing."""
        # Clear the screen
        self.clear()
        
        # Render to main framebuffer
        with self.main_framebuffer.bind():
            self.clear()
            self._render_game()
            
        # Apply post-processing effects
        self._apply_post_processing()
        
        # Update performance counters
        self._update_performance_counters()
        
    def _render_game(self):
        """Render the main game content."""
        if self.game_engine:
            self.game_engine.render()
            
    def _apply_post_processing(self):
        """Apply post-processing effects like bloom."""
        if not self.post_process_shader:
            # Fallback: just draw the main framebuffer
            self.ctx.screen.use()
            self.main_framebuffer.color_attachments[0].use(0)
            return
            
        # Apply bloom effect
        with self.bloom_framebuffer.bind():
            self.clear()
            self.post_process_shader.use()
            self.post_process_shader["screenTexture"] = 0
            self.post_process_shader["bloom_threshold"] = 0.8
            self.post_process_shader["bloom_intensity"] = 1.5
            
            self.main_framebuffer.color_attachments[0].use(0)
            self._draw_fullscreen_quad()
            
        # Combine main and bloom
        self.ctx.screen.use()
        self.main_framebuffer.color_attachments[0].use(0)
        self.bloom_framebuffer.color_attachments[0].use(1)
        
        # Simple additive blending for bloom
        self.ctx.blend_func = self.ctx.ONE, self.ctx.ONE
        self._draw_fullscreen_quad()
        self.ctx.blend_func = self.ctx.SRC_ALPHA, self.ctx.ONE_MINUS_SRC_ALPHA
        
    def _draw_fullscreen_quad(self):
        """Draw a fullscreen quad for post-processing."""
        # Create fullscreen quad geometry
        vertices = self.ctx.buffer(data=arcade.gl.geometry.quad_2d_fs())
        geometry = self.ctx.geometry([arcade.gl.BufferDescription(
            vertices, "2f", ["position", "tex_coords"]
        )])
        geometry.render(self.post_process_shader)
        
    def on_update(self, delta_time: float):
        """Update game logic."""
        if self.game_engine:
            self.game_engine.update(delta_time)
            
        self.frame_count += 1
        
    def on_key_press(self, key: int, modifiers: int):
        """Handle key press events."""
        if self.game_engine:
            self.game_engine.on_key_press(key, modifiers)
            
    def on_key_release(self, key: int, modifiers: int):
        """Handle key release events."""
        if self.game_engine:
            self.game_engine.on_key_release(key, modifiers)
            
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse press events."""
        if self.game_engine:
            self.game_engine.on_mouse_press(x, y, button, modifiers)
            
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse release events."""
        if self.game_engine:
            self.game_engine.on_mouse_release(x, y, button, modifiers)
            
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Handle mouse motion events."""
        if self.game_engine:
            self.game_engine.on_mouse_motion(x, y, dx, dy)
            
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """Handle mouse scroll events."""
        if self.game_engine:
            self.game_engine.on_mouse_scroll(x, y, scroll_x, scroll_y)
            
    def on_resize(self, width: int, height: int):
        """Handle window resize events."""
        super().on_resize(width, height)
        
        # Recreate framebuffers with new size
        if self.main_framebuffer:
            self.main_framebuffer = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((width, height), 4)]
            )
        if self.bloom_framebuffer:
            self.bloom_framebuffer = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((width, height), 4)]
            )
            
        if self.game_engine:
            self.game_engine.on_resize(width, height)
            
    def _update_performance_counters(self):
        """Update FPS and performance counters."""
        import time
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            fps = self.fps_counter / (current_time - self.last_fps_time)
            self.set_caption(f"Space Game - Arcade Edition | FPS: {fps:.1f}")
            self.fps_counter = 0
            self.last_fps_time = current_time
            
        self.fps_counter += 1 