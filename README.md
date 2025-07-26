# Space Game Clone - Panda3D Edition

## 🎮 About

This is a real-time strategy tower defense game built with **Panda3D**, featuring a unique power network system where buildings must be connected to power sources to operate. Players defend their base against increasingly difficult waves of enemies by strategically placing buildings and managing resources.

## 🌟 Key Features

### 🔌 **Unique Power Network System**
- Buildings require power connections to operate
- Strategic network topology affects vulnerability
- Hub vs. ring vs. grid building patterns create emergent gameplay

### 🏗️ **12 Building Types**
- **Power Infrastructure**: Solar panels, connectors, batteries
- **Resource Extraction**: Miners, converters  
- **Defense Systems**: Turrets, lasers, super lasers, missile launchers
- **Support Systems**: Repair nodes, hangars, force fields

### 👾 **7 Enemy Types** 
- From basic fighters to massive motherships
- Each with unique AI behaviors and special abilities
- Adaptive targeting and swarm intelligence

### 🌊 **5 Wave Types**
- Normal, Formation, Elite, Swarm, and Boss waves
- Exponential difficulty scaling (1.6x growth factor)
- Dynamic enemy composition based on game phase

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment support

### Installation & Setup
```bash
# Clone and enter the repository
git clone <repository-url>
cd SpaceGame

# Create and activate virtual environment  
python3 -m venv panda3d_env
source panda3d_env/bin/activate  # On Windows: panda3d_env\Scripts\activate

# Install dependencies
pip install -r panda3d_requirements.txt

# Verify installation
python test_phase1.py

# Run the game
python main.py
```

## 🎮 Controls

- **ESC** - Quit game
- **SPACE** - Start/toggle game state
- **P** - Pause/resume game
- **WASD** - Camera movement (Phase 2+)
- **Mouse** - Building placement (Phase 2+)

## 📊 Game Mechanics

### Resources
- **Minerals** (600 starting): Construction currency
- **Energy** (50 starting): Operational currency for building actions  
- **Power**: Real-time generation/consumption for building operation

### Victory Condition
- **Survival Challenge**: Survive as many waves as possible
- **Infinite Scaling**: No traditional victory, difficulty scales infinitely

### Strategic Depth
- **Multi-Resource Economy**: Minerals, energy, and power create meaningful trade-offs
- **Infrastructure Vulnerability**: Network attacks can disable large areas
- **Emergent Tactics**: Simple rules create complex decision spaces

## 🏗️ Architecture

```
Project Structure:
├── main.py                    # Panda3D application entry point
├── config/                    # JSON configuration files (all game balance)
├── docs/                      # Complete technical documentation  
├── game/
│   ├── core/                 # Game engine and state management
│   ├── panda3d/             # Panda3D-specific rendering systems
│   ├── systems/             # Game logic systems (ready for Phase 3)
│   └── entities/            # Game objects (ready for Phase 3)
├── assets/                   # 3D models, textures, shaders (Phase 4)
└── tests/                    # Test utilities
```

## 📈 Development Status

### ✅ **Phase 1 Complete: Foundation**
- ✅ Panda3D application with 3D scene
- ✅ Configuration system with all game balance preserved
- ✅ Basic input handling and window management
- ✅ Orthographic top-down camera system

### 🔄 **Upcoming Phases**
- **Phase 2**: Camera controls and basic entity rendering
- **Phase 3**: Complete game logic integration  
- **Phase 4**: Enhanced 3D visuals and models
- **Phase 5**: Polish and optimization

## 📚 Documentation

Comprehensive technical documentation available in [`docs/`](docs/):

- **[Game Specification](docs/GAME_SPECIFICATION.md)** - High-level overview and core concepts
- **[Power Network System](docs/POWER_NETWORK_SYSTEM.md)** - The game's unique core mechanic
- **[Building System](docs/BUILDING_SYSTEM.md)** - Complete building mechanics and types
- **[Enemy AI System](docs/ENEMY_AI_SYSTEM.md)** - Enemy types, behaviors, and combat
- **[Wave System](docs/WAVE_SYSTEM.md)** - Wave generation and difficulty progression
- **[Migration Plan](docs/PANDA3D_MIGRATION_PLAN.md)** - Complete 5-phase migration strategy

## ⚙️ Configuration

All game balance and mechanics are externalized in JSON files in [`config/`](config/):

- `game_config.json` - Core settings, display, resources
- `buildings.json` - All building types and stats  
- `enemies.json` - Enemy types and AI behaviors
- `waves.json` - Wave generation and difficulty
- `research.json` - Technology tree and upgrades
- `controls.json` - Input mapping and UI settings

## 🎯 Design Philosophy

### **Emergent Complexity**
Simple rules create complex strategic situations through the interaction of:
- Power network dependencies
- Resource management trade-offs  
- Exponential difficulty scaling
- Multiple valid strategies

### **Strategic Depth**  
- **Network Topology Strategy**: Hub vs. ring vs. grid patterns
- **Infrastructure Risk**: Network attacks create cascade failures
- **Resource Tension**: Meaningful trade-offs between spending options
- **Escalating Challenge**: Difficulty grows faster than player power

## 🧪 Testing

Run the verification suite:
```bash
python test_phase1.py
```

Expected result: All tests pass with green checkmarks ✅

## 🤝 Contributing

This project preserves a carefully balanced game design through:
- **Configuration-driven balance**: Easy tweaks through JSON files
- **Complete documentation**: Technical specs enable faithful reimplementation  
- **Modular architecture**: Clean separation of systems
- **Comprehensive testing**: Verification of all mechanics

## 📝 License

[Add your license information here]

---

**Built with Panda3D for enhanced 3D graphics while preserving the strategic depth and unique gameplay mechanics that make this tower defense game engaging and challenging.** 