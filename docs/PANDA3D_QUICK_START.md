# Panda3D Migration - Quick Start Guide

## 🚀 Getting Started with Phase 1

This guide provides step-by-step instructions to begin the Panda3D migration. Follow this to implement Phase 1 of the [Migration Plan](./PANDA3D_MIGRATION_PLAN.md).

## 📋 Prerequisites

### Environment Setup
```bash
# Create virtual environment for Panda3D project
python -m venv panda3d_env
source panda3d_env/bin/activate  # On Windows: panda3d_env\Scripts\activate

# Install Panda3D and dependencies
pip install -r panda3d_requirements.txt
```

### Verify Installation
```bash
# Test Panda3D installation
python -c "from direct.showbase.ShowBase import ShowBase; print('Panda3D ready!')"
```

## 🏗️ Phase 1 Implementation

### Step 1: Create Project Structure
```bash
mkdir panda3d_spacegame
cd panda3d_spacegame

# Create directory structure
mkdir -p game/{core,systems,panda3d,entities}
mkdir -p assets/{models,textures,shaders,audio}
mkdir -p config
mkdir -p tests

# Copy existing configuration files
cp ../config/*.json config/
cp ../config/config_loader.py config/
```

### Step 2: Basic Panda3D Application
Create `main.py`:
```python
#!/usr/bin/env python3
"""
Panda3D Space Game Clone - Main Entry Point
Phase 1: Basic application setup with ShowBase
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_loader import GameConfig
from game.core.engine import Panda3DGameEngine

class SpaceGameApp(ShowBase):
    """Main Panda3D application class"""
    
    def __init__(self):
        # Initialize Panda3D ShowBase
        ShowBase.__init__(self)
        
        # Load configuration
        self.config = GameConfig("config/")
        
        # Set up window
        self.setup_window()
        
        # Initialize game engine
        self.game_engine = Panda3DGameEngine(self, self.config)
        
        # Start the game
        self.setup_tasks()
        
    def setup_window(self):
        """Configure the Panda3D window"""
        display_config = self.config.get_display_config()
        
        # Set window title
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Space Game Clone - Panda3D Edition")
        props.setSize(display_config["screen_width"], display_config["screen_height"])
        self.win.requestProperties(props)
        
        # Disable default mouse camera control
        self.disableMouse()
        
    def setup_tasks(self):
        """Set up main game loop tasks"""
        # Main game update task
        self.taskMgr.add(self.game_update_task, "game_update")
        
    def game_update_task(self, task):
        """Main game update loop"""
        dt = globalClock.getDt()
        
        # Update game engine
        if hasattr(self, 'game_engine'):
            self.game_engine.update(dt)
            
        return task.cont
        
    def cleanup(self):
        """Clean up resources on exit"""
        if hasattr(self, 'game_engine'):
            self.game_engine.cleanup()

def main():
    """Application entry point"""
    try:
        app = SpaceGameApp()
        app.run()
        return 0
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if 'app' in locals():
            app.cleanup()

if __name__ == "__main__":
    sys.exit(main())
```

### Step 3: Game Engine Adapter
Create `game/core/engine.py`:
```python
"""
Panda3D Game Engine - Adapter for existing game logic
Preserves all game mechanics while adapting to Panda3D
"""

from game.systems.power_network import PowerNetwork
from game.systems.building_system import BuildingSystem  
from game.systems.enemy_system import EnemySystem
from game.systems.wave_system import WaveSystem
from game.panda3d.camera_controller import Panda3DCamera
from game.panda3d.scene_manager import SceneManager
from game.panda3d.input_system import Panda3DInputSystem

class Panda3DGameEngine:
    """
    Main game engine that preserves existing game logic
    while adapting to Panda3D rendering pipeline
    """
    
    def __init__(self, base, config):
        self.base = base
        self.config = config
        
        # Game state
        self.state = "menu"  # menu, playing, paused, game_over
        self.game_time = 0.0
        
        # Initialize systems (preserve existing logic)
        self.init_core_systems()
        self.init_panda3d_systems()
        
    def init_core_systems(self):
        """Initialize core game systems (unchanged from original)"""
        # Preserve all existing game logic systems
        self.power_network = PowerNetwork()
        self.building_system = BuildingSystem(self.config)
        self.enemy_system = EnemySystem(self.config)
        self.wave_system = WaveSystem(self.config)
        
        # Connect systems (preserve existing connections)
        self.building_system.set_power_network(self.power_network)
        self.wave_system.set_enemy_system(self.enemy_system)
        
    def init_panda3d_systems(self):
        """Initialize Panda3D-specific systems (new)"""
        # Panda3D rendering and interaction systems
        self.scene_manager = SceneManager(self.base)
        self.camera = Panda3DCamera(self.base, self.config)
        self.input_system = Panda3DInputSystem(self.base, self)
        
    def update(self, dt):
        """Main update loop - preserves existing game logic"""
        self.game_time += dt
        
        if self.state == "playing":
            # Update core game systems (unchanged)
            self.power_network.update(dt)
            self.building_system.update(dt)
            self.enemy_system.update(dt)
            self.wave_system.update(dt)
            
            # Update Panda3D systems
            self.camera.update(dt)
            self.input_system.update(dt)
            
        elif self.state == "menu":
            # Handle menu state
            pass
            
    def start_game(self):
        """Start a new game"""
        self.state = "playing"
        
        # Initialize game state (preserve existing logic)
        self.building_system.reset()
        self.enemy_system.reset()
        self.wave_system.reset()
        self.power_network.reset()
        
        # Create starting base (from documentation)
        base_pos = (
            self.config.get_display_config()["world_width"] // 2,
            self.config.get_display_config()["world_height"] // 2
        )
        self.building_system.create_building("starting_base", *base_pos)
        
    def cleanup(self):
        """Clean up resources"""
        # Clean up game systems
        if hasattr(self, 'scene_manager'):
            self.scene_manager.cleanup()
```

### Step 4: Configuration Adapter
Create `game/core/config_adapter.py`:
```python
"""
Configuration adapter to ensure existing JSON configs work with Panda3D
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.config_loader import GameConfig as BaseGameConfig

class Panda3DGameConfig(BaseGameConfig):
    """Panda3D-specific configuration adapter"""
    
    def __init__(self, config_dir):
        super().__init__(config_dir)
        
    def get_panda3d_display_config(self):
        """Get Panda3D-specific display configuration"""
        base_config = self.get_display_config()
        
        return {
            **base_config,
            "panda3d_specific": {
                "camera_type": "orthographic",
                "near_plane": -1000,
                "far_plane": 1000,
                "camera_height": 100,
                "lighting": {
                    "ambient": [0.3, 0.3, 0.3, 1.0],
                    "directional": [0.7, 0.7, 0.7, 1.0],
                    "directional_direction": [-1, -1, -1]
                }
            }
        }
```

### Step 5: Basic Systems Stubs
Create stub files to get the application running:

`game/panda3d/camera_controller.py`:
```python
"""Panda3D Camera Controller - Phase 1 Basic Implementation"""

class Panda3DCamera:
    def __init__(self, base, config):
        self.base = base
        self.config = config
        self.setup_camera()
        
    def setup_camera(self):
        """Set up orthographic top-down camera"""
        # Position camera above the world
        self.base.camera.setPos(2400, 1350, 100)  # Center of world
        self.base.camera.lookAt(2400, 1350, 0)
        
    def update(self, dt):
        """Update camera (placeholder for Phase 2)"""
        pass
```

`game/panda3d/scene_manager.py`:
```python
"""Panda3D Scene Manager - Phase 1 Basic Implementation"""

from panda3d.core import AmbientLight, DirectionalLight

class SceneManager:
    def __init__(self, base):
        self.base = base
        self.setup_basic_lighting()
        
    def setup_basic_lighting(self):
        """Set up basic lighting for visibility"""
        # Ambient light
        ambient = AmbientLight('ambient')
        ambient.setColor((0.3, 0.3, 0.3, 1))
        ambient_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(ambient_np)
        
        # Directional light
        directional = DirectionalLight('directional')
        directional.setDirection((-1, -1, -1))
        directional.setColor((0.7, 0.7, 0.7, 1))
        directional_np = self.base.render.attachNewNode(directional)
        self.base.render.setLight(directional_np)
        
    def cleanup(self):
        """Clean up scene resources"""
        pass
```

`game/panda3d/input_system.py`:
```python
"""Panda3D Input System - Phase 1 Basic Implementation"""

from direct.showbase.DirectObject import DirectObject

class Panda3DInputSystem(DirectObject):
    def __init__(self, base, game_engine):
        DirectObject.__init__(self)
        self.base = base
        self.game_engine = game_engine
        self.setup_input()
        
    def setup_input(self):
        """Set up basic input handling"""
        # Basic key bindings for Phase 1
        self.accept('escape', self.quit_game)
        self.accept('space', self.start_game)
        
    def update(self, dt):
        """Update input system"""
        pass
        
    def quit_game(self):
        """Quit the application"""
        self.base.userExit()
        
    def start_game(self):
        """Start the game"""
        self.game_engine.start_game()
```

## ✅ Phase 1 Verification

### Test the Basic Setup
```bash
# Run the application
python main.py
```

**Expected Results:**
- [x] Panda3D window opens with correct title
- [x] No error messages in console
- [x] Configuration files load successfully
- [x] Basic lighting is visible
- [x] ESC key quits the application
- [x] SPACE key triggers game start (logged)

### Verification Checklist
- [ ] Panda3D environment working
- [ ] Configuration system preserved
- [ ] Basic application structure in place
- [ ] Window opens and displays properly
- [ ] Input handling responds
- [ ] No import errors or crashes

## 🔄 Next Steps

Once Phase 1 is working:

1. **Phase 2**: Implement camera controls and basic entity visualization
2. **Phase 3**: Integrate existing game logic systems
3. **Phase 4**: Add enhanced visuals and 3D models
4. **Phase 5**: Polish and optimization

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# If you get import errors, ensure the project structure is correct
# and that panda3d is properly installed
pip list | grep panda3d
```

**Window Not Opening:**
```bash
# Check if your system supports OpenGL
python -c "from panda3d.core import *; print('OpenGL support:', ConfigVariableBool('gl-debug').getValue())"
```

**Configuration Errors:**
- Ensure all JSON files are copied from the original project
- Verify paths in config_loader.py are correct

### Development Tips

1. **Keep Original Code**: Don't delete the original Pygame version until migration is complete
2. **Test Incrementally**: Verify each phase before moving to the next
3. **Preserve Logic**: Only change rendering, keep all game mechanics unchanged
4. **Use Git Branches**: Create separate branches for each migration phase

---

*This quick start gets you up and running with Phase 1 of the Panda3D migration. The goal is to establish the foundation while preserving all existing game logic and configuration.* 