# 🚀 Space Game Clone

A real-time strategy space defense game built with Python and Pygame. Defend your base by building energy infrastructure, mining operations, and powerful defense systems against waves of increasingly challenging enemy ships.

## 🎮 Game Overview

Space Game Clone is an engaging tower defense / RTS hybrid where you must:
- **Build and manage** a power grid to support your operations
- **Mine asteroids** for resources to expand your infrastructure 
- **Defend your base** against escalating enemy waves
- **Strategic planning** is key - balance economy, defense, and expansion

## ✨ Key Features

### 🏗️ **Building System**
- **Modular Construction**: Place buildings anywhere with intelligent connection system
- **Power Grid Management**: Buildings must be connected to power sources to function
- **Resource Economy**: Mine asteroids to gather minerals for construction
- **Strategic Placement**: Buildings have interference zones requiring tactical positioning

### ⚡ **Power Grid System**
- **Automatic Connections**: Buildings automatically connect to nearby structures
- **Power Sources**: Solar panels and batteries provide energy
- **Connection Limits**: Different building types have varying connection capacities
- **Visual Feedback**: Blue lines show active power connections

### 🛡️ **Defense Systems**
- **Multiple Weapon Types**: Turrets, lasers, and superlasers with different capabilities
- **Targeting AI**: Automatic enemy detection and engagement
- **Range Visualization**: See weapon ranges during building placement
- **Upgrade Paths**: More powerful weapons for late-game threats

### 👾 **Enemy Waves**
- **Progressive Difficulty**: Waves get larger and more complex over time
- **Diverse Enemy Types**: Fighters, assault ships, stealth units, heavy cruisers
- **Formation Flying**: Enemies spawn in tactical grid formations
- **Balanced Composition**: Mix of fast attackers and heavy hitters

### 🎯 **Advanced Features**
- **Minimap**: Real-time overview of battlefield in lower-left corner
- **Speed Control**: Adjust game speed (0.5x to 3x) for tactical planning
- **Enhanced Graphics**: Modern UI with glass panels and visual effects
- **Asteroid Variety**: Multiple asteroid types with different mineral yields

## 🎮 Controls

### **Core Controls**
| Key | Action |
|-----|--------|
| **Arrow Keys** | Move camera around the battlefield |
| **Mouse** | Select buildings, place structures |
| **Mouse Wheel** | Zoom in/out |

### **Building Hotkeys**
| Key | Building Type | Cost | Function |
|-----|---------------|------|----------|
| **C** | Connector | 30 | Power distribution hub (6 connections) |
| **S** | Solar Panel | 50 | Generates power during operation |
| **B** | Battery | 80 | Stores and provides power |
| **M** | Miner | 100 | Extracts minerals from nearby asteroids |
| **T** | Turret | 150 | Basic projectile defense |
| **L** | Laser | 200 | Advanced energy weapon |
| **R** | Repair Node | 120 | Repairs nearby damaged buildings |
| **V** | Converter | 200 | Advanced resource processing |
| **X** | Superlaser | 500 | Ultimate defense weapon |
| **H** | Hangar | 250 | Launches friendly attack ships |

### **Game Speed & Controls**
| Key | Function |
|-----|----------|
| **1** | 0.5x game speed (slow motion) |
| **2** | 1x game speed (normal) |
| **3** | 2x game speed (fast) |
| **4** | 3x game speed (very fast) |
| **Spacebar** | Pause/unpause game |
| **O** | Open/close game menu |
| **P** | Quit game |

## 🏗️ Building Types & Strategy

### **Power Infrastructure**
- **Solar Panels**: Primary power source, essential for all operations
- **Batteries**: Store power and provide backup during low generation
- **Connectors**: Hub nodes that distribute power efficiently (up to 6 connections)

### **Resource Gathering**
- **Miners**: Extract minerals from asteroids (1 connection, up to 5 targets)
- **Converters**: Process raw materials for advanced construction

### **Defense Network**
- **Turrets**: Cost-effective early game defense (1 connection)
- **Lasers**: High-damage energy weapons (1 connection) 
- **Superlasers**: Ultimate late-game defense (1 connection)

### **Support Systems**
- **Repair Nodes**: Maintain your infrastructure automatically
- **Hangars**: Deploy friendly fighter squadrons

## ⚔️ Enemy Types

| Enemy | Health | Speed | Special Ability | Points |
|-------|--------|-------|-----------------|--------|
| **Fighter** | Low | Medium | Basic attacks | 1 |
| **Kamikaze** | Very Low | Very High | Suicide attacks | 2 |
| **Assault Ship** | Medium | Medium | Machine gun bursts | 3 |
| **Stealth Ship** | Low | High | Cloaking, EMP burst | 4 |
| **Large Ship** | High | Low | Heavy missiles | 5 |
| **Heavy Cruiser** | Very High | Very Low | Plasma cannon | 6 |

## 🎯 Gameplay Tips

### **Early Game (Waves 1-5)**
1. **Build power first**: Place solar panels and connectors near your base
2. **Start mining**: Place miners near dense asteroid clusters
3. **Basic defense**: A few turrets can handle early waves
4. **Expand carefully**: Don't overextend your power grid

### **Mid Game (Waves 6-15)**
1. **Scale up mining**: More miners = more resources for defense
2. **Upgrade weapons**: Lasers become essential for stronger enemies
3. **Power management**: Batteries help during peak demand
4. **Strategic placement**: Use terrain and range optimization

### **Late Game (Waves 16+)**
1. **Superlasers**: Ultimate weapons for massive enemy formations
2. **Hangars**: Deploy fighter squadrons for additional firepower
3. **Redundancy**: Multiple power sources and repair capabilities
4. **Advanced tactics**: Speed control for micro-management

## 🎨 Visual Features

- **Modern UI**: Glass-panel interface with transparency effects
- **Enhanced Graphics**: Glowing weapons, particle effects, laser beams
- **Minimap**: Color-coded overview with buildings, enemies, asteroids
- **Visual Feedback**: Building ranges, connection lines, health bars
- **Smooth Animations**: Rotating buildings, moving enemies, weapon effects

## 🔧 Technical Features

- **Modular Architecture**: Clean system-based design for extensibility
- **Event-Driven**: Decoupled systems communicate through events
- **Scalable Performance**: Efficient rendering and collision detection
- **Save System**: Persistent game state and configuration
- **Cross-Platform**: Runs on Windows, macOS, and Linux

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- Pygame-CE library

### **Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd SpaceGame

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install pygame-ce

# Run the game
python3 main.py
```

## 🎮 Development

### **Project Structure**
```
SpaceGame/
├── main.py              # Game entry point
├── settings.py          # Game configuration
├── power.py            # Power grid system
├── enemies.py          # Enemy types and AI
├── buildings.py        # Building definitions
├── asteroids.py        # Asteroid generation
├── game/               # Modular game systems
│   ├── core/          # Engine and state management
│   └── systems/       # Game logic, rendering, input
└── assets/            # Images and resources
```

### **Adding New Features**
The modular architecture makes it easy to extend:
- **New building types**: Add to `buildings.py` and register in systems
- **Enemy varieties**: Extend the enemy classes in `enemies.py`
- **Visual effects**: Enhance the render system with new particle types
- **Game modes**: Implement new states in the state management system

## 🏆 Advanced Strategies

### **Power Grid Mastery**
- **Redundant Connections**: Multiple power paths prevent single-point failures
- **Efficient Layout**: Minimize connector usage while maximizing coverage
- **Strategic Positioning**: Place power infrastructure away from combat zones

### **Economic Optimization**
- **Asteroid Selection**: Prioritize high-yield asteroids for mining
- **Build Order**: Balance immediate defense needs with long-term economy
- **Resource Banking**: Maintain mineral reserves for emergency construction

### **Combat Tactics**
- **Layered Defense**: Multiple weapon types at different ranges
- **Focus Fire**: Concentrate defenses on main attack routes
- **Adaptive Building**: Counter specific enemy types with appropriate weapons

## 🎯 Victory Conditions

- **Survive** all enemy waves to achieve victory
- **Protect your base** - if it's destroyed, the game ends
- **Resource management** is key to building adequate defenses
- **Adapt your strategy** as enemy waves become more challenging

## 🔄 Recent Updates

- **Simplified Power Grid**: Automatic building connections with clear limits
- **Enhanced Enemy AI**: New ship types with unique abilities and formations
- **Visual Improvements**: Better graphics, minimap, and UI effects
- **Control Refinements**: Safer key mappings and speed control
- **Performance Optimization**: Smoother gameplay and better frame rates

## 🤝 Contributing

This project welcomes contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

---

**Defend your base, expand your empire, and survive the endless waves!** 🚀⚡🛡️ 