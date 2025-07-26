# Space Game Configuration System

This directory contains JSON configuration files that define all the game mechanics, balance, and settings for the Space Game Clone. The configuration system allows for easy modification of game parameters without changing code.

## 📁 Configuration Files

### `game_config.json`
**Core game settings and global parameters**
- Display settings (screen size, FPS)
- Camera controls (zoom, speed)
- Color palette
- Base and resource configuration
- Combat and mining mechanics
- Asteroid generation settings

### `buildings.json`
**Complete building definitions and stats**
- Building costs and construction requirements
- Health, damage, and energy consumption
- Special abilities and connection limits
- Visual properties (colors, sizes)
- Hotkey mappings

### `enemies.json`
**Enemy types and AI behavior**
- Health, speed, and damage values
- Special abilities (cloaking, EMP, plasma cannons)
- AI behavior patterns
- Wave point values and spawn weights
- Friendly ship configurations

### `waves.json`
**Wave generation and difficulty scaling**
- Wave timing and spawn intervals
- Special wave types (formation, elite, swarm, boss)
- Enemy composition by game phase
- Difficulty scaling formulas
- Spawn pattern configurations

### `research.json`
**Technology tree and upgrades**
- Research categories and descriptions
- Technology prerequisites and costs
- Upgrade effects and modifiers
- Research mechanics and progression

### `controls.json`
**Input mapping and UI settings**
- Keyboard and mouse controls
- Building hotkeys
- UI layout and positioning
- Accessibility options
- Game speed controls

## 🛠️ Using the Configuration System

### Basic Usage

```python
from config.config_loader import initialize_config, get_config

# Initialize the configuration system
config = initialize_config()

# Access specific values
screen_width = config.get('game', 'display.screen_width', 1600)
turret_damage = config.get('buildings', 'building_types.turret.damage', 15)

# Get entire building configuration
turret_config = config.get_building_config('turret')
enemy_config = config.get_enemy_config('kamikaze')
```

### Advanced Usage

```python
# Modify values at runtime
config.set('game', 'display.fps', 120)

# Save changes back to file
config.save_config('game')

# Reload configuration from file
config.reload_config('buildings')

# Validate all configurations
is_valid = config.validate_config()
```

### Replacing hardcoded values

**Before (settings.py):**
```python
TURRET_DAMAGE = 15
TURRET_RANGE = 350
BUILD_COSTS = {'turret': 150}
```

**After (using config):**
```python
cfg = get_config()
TURRET_DAMAGE = cfg.get('buildings', 'building_types.turret.damage')
TURRET_RANGE = cfg.get('buildings', 'building_types.turret.range')
BUILD_COSTS = cfg.get('buildings', 'building_costs')
```

## 🎯 Configuration Categories

### 🎮 Game Balance
- **Building Stats**: Health, damage, costs, energy consumption
- **Enemy Stats**: Health scaling, damage values, speed multipliers
- **Wave Difficulty**: Spawn rates, enemy composition, special wave frequency
- **Resource Economy**: Starting resources, mining rates, upgrade costs

### ⚡ Performance Settings
- **Display**: Screen resolution, FPS limits, visual effects
- **Camera**: Movement speed, zoom limits, smoothing
- **Particle Effects**: Enable/disable, intensity settings

### 🎨 Visual Customization
- **Colors**: Building colors, UI themes, enemy colors
- **UI Layout**: Panel positions, minimap settings, HUD elements
- **Effects**: Damage numbers, health bars, laser effects

### 🕹️ Input Controls
- **Hotkeys**: Building placement, camera controls, game speed
- **Mouse**: Click behaviors, scroll actions, context menus
- **Accessibility**: Key repeat rates, visual assistance

## 📝 Modifying Configurations

### 1. Direct JSON Editing
Edit the JSON files directly for permanent changes:

```json
{
  "building_types": {
    "turret": {
      "damage": 20,
      "range": 400,
      "cost": 150
    }
  }
}
```

### 2. Runtime Modifications
Change values during gameplay for testing:

```python
# Increase turret damage for testing
config.set('buildings', 'building_types.turret.damage', 25)

# Spawn faster waves
config.set('waves', 'wave_timing.wait_time', 60)
```

### 3. Save Changes
Persist runtime changes back to files:

```python
config.save_config('buildings')
config.save_config('waves')
```

## 🧪 Testing and Validation

### Configuration Validation
The system includes built-in validation:

```python
# Check if all required fields are present
if config.validate_config():
    print("All configurations are valid!")
else:
    print("Configuration errors found!")
```

### Test Configuration Loading
```bash
cd config/
python config_loader.py
```

## 📊 Examples

### Creating a New Building Type

```json
{
  "building_types": {
    "shield_generator": {
      "name": "Shield Generator",
      "description": "Provides energy shields to nearby buildings",
      "cost": 300,
      "base_health": 150,
      "radius": 25,
      "color": [0, 200, 255],
      "energy_cost": 2.0,
      "shield_range": 150,
      "shield_strength": 100,
      "max_connections": 1,
      "hotkey": "G"
    }
  }
}
```

### Adding a New Enemy Type

```json
{
  "enemy_types": {
    "bomber": {
      "name": "Bomber Ship",
      "description": "Heavy bomber with area damage",
      "base_health": 250,
      "speed": 0.3,
      "radius": 20,
      "size": 35,
      "color": [200, 100, 0],
      "points": 8,
      "abilities": ["area_bomb"],
      "bomb_damage": 50,
      "bomb_radius": 80,
      "spawn_weight": 3
    }
  }
}
```

### Customizing Wave Progression

```json
{
  "wave_composition": {
    "nightmare_mode": {
      "wave_range": [20, 999],
      "enemy_distribution": {
        "cruiser": 0.4,
        "stealth": 0.3,
        "assault": 0.2,
        "bomber": 0.1
      },
      "max_enemy_types": 4,
      "mothership_chance": 0.3
    }
  }
}
```

## 🔧 Integration Guide

### Step 1: Replace Constants
Replace hardcoded values in existing files:

```python
# In buildings.py
from config.config_loader import get_config
cfg = get_config()

class Turret(Building):
    def __init__(self, x, y):
        config = cfg.get_building_config('turret')
        super().__init__(
            x, y, 
            color=config.get('color', [255, 0, 0]),
            radius=config.get('radius', 28)
        )
        self.damage = config.get('damage', 15)
        self.range = config.get('range', 350)
```

### Step 2: Initialize on Startup
```python
# In main.py
from config.config_loader import initialize_config

def main():
    # Initialize configuration system
    config = initialize_config()
    
    # Validate configurations
    if not config.validate_config():
        print("Configuration validation failed!")
        return
    
    # Start game...
```

### Step 3: Use Throughout Game
```python
# Access config anywhere in the game
from config.config_loader import get_config

cfg = get_config()
enemy_health = cfg.get('enemies', 'enemy_base_stats.health_base') * wave_number
```

## 🚀 Benefits

### 🎯 **Easy Balance Tweaking**
- Modify damage, health, costs without code changes
- Test different balance scenarios quickly
- Save different configurations for different difficulty modes

### 🔧 **Modding Support** 
- Players can create custom configurations
- Easy to share balance modifications
- Support for total conversion mods

### 🧪 **Rapid Iteration**
- Change values and reload instantly
- A/B testing different configurations
- Quick prototyping of new features

### 📈 **Maintainability**
- Centralized configuration management
- Version control for balance changes
- Clear separation of data and logic

---

*This configuration system preserves all the carefully balanced game mechanics while making them easily modifiable and maintainable.* 