# Wave System

## 📋 Overview

The Wave System is responsible for generating challenging and varied enemy encounters that scale in difficulty over time. It manages enemy composition, spawn patterns, timing, and special wave events to create engaging gameplay progression.

## 🌊 Core Wave Mechanics

### Wave Timing
```python
class WaveTimer:
    def __init__(self):
        self.initial_wait = 9600        # 160 seconds at 60fps (2.67 minutes)
        self.wave_interval = 120        # 2 seconds between waves
        self.spawn_interval = 30        # 0.5 seconds between spawns
        self.current_timer = 0
        self.wave_active = False
```

### Wave Progression Formula
```python
def calculate_wave_difficulty(wave_number):
    base_points = 10
    growth_factor = 1.6
    
    # Exponential difficulty scaling
    total_points = base_points * (growth_factor ** wave_number)
    
    # Cap extremely high values for performance
    return min(total_points, 10000)
```

### Enemy Health Scaling
```python
def calculate_enemy_health(wave_number, enemy_type):
    base_health = ENEMY_BASE_HEALTH[enemy_type]
    
    if enemy_type == "basic":
        # Linear scaling for basic enemies
        return 24 * wave_number
    elif enemy_type == "mothership":
        # Enhanced scaling for elite units
        return (24 * wave_number) * 5
    else:
        # Fixed health for special enemies
        return base_health
```

## 🎯 Wave Types

### 1. Normal Waves
```python
def generate_normal_wave(wave_number):
    total_points = calculate_wave_difficulty(wave_number)
    composition = determine_enemy_composition(wave_number)
    enemies = allocate_points_to_enemies(total_points, composition)
    return create_wave(enemies, spawn_pattern="single_point")
```

**Characteristics:**
- **Frequency**: Default wave type (70% of waves)
- **Composition**: Mixed enemy types based on game phase
- **Spawn Pattern**: Single spawn point around map perimeter
- **Scaling**: Follows standard difficulty progression

### 2. Formation Waves
```python
def generate_formation_wave(wave_number):
    # Every 6th wave is a formation wave
    if wave_number % 6 == 0:
        enemy_count = int(30 * (1 + 0.8 * wave_number))
        spawn_points = min(16, max(8, enemy_count // 6))
        
        return create_wave(
            enemies=generate_formation_enemies(enemy_count),
            spawn_pattern="multi_directional",
            spawn_points=spawn_points,
            coordination=True
        )
```

**Characteristics:**
- **Trigger**: Every 6th wave (waves 6, 12, 18, etc.)
- **Scale**: 30 × (1 + 0.8 × wave) enemies
- **Spawn Pattern**: 8-16 spawn points around entire perimeter
- **Coordination**: Enemies attack from all directions simultaneously
- **Purpose**: Major escalation events requiring prepared defenses

### 3. Elite Waves
```python
def generate_elite_wave(wave_number):
    if random.random() < 0.15:  # 15% chance
        enemy_count = max(8, int(10 + wave_number * 2))
        elite_types = ["large", "cruiser", "mothership"]
        
        return create_wave(
            enemies=generate_elite_composition(enemy_count, elite_types),
            spawn_pattern="calculated",
            enhanced_ai=True
        )
```

**Characteristics:**
- **Trigger**: 15% random chance per wave
- **Composition**: Heavy emphasis on Large Ships, Cruisers, Motherships
- **Count**: 8-20+ elite enemies depending on wave number
- **AI Enhancement**: Improved targeting and coordination
- **Purpose**: Quality over quantity challenge

### 4. Swarm Waves
```python
def generate_swarm_wave(wave_number):
    if random.random() < 0.12:  # 12% chance
        enemy_count = int(40 + wave_number * 6)
        swarm_types = ["basic", "kamikaze"]
        
        return create_wave(
            enemies=generate_swarm_composition(enemy_count, swarm_types),
            spawn_pattern="rapid_spawn",
            spawn_interval=15  # Faster spawning
        )
```

**Characteristics:**
- **Trigger**: 12% random chance per wave
- **Composition**: Overwhelming numbers of basic enemies and kamikazes
- **Count**: 40+ enemies, scaling rapidly
- **Spawn Rate**: Double speed (15 frames between spawns)
- **Purpose**: Resource depletion and overwhelming firepower

### 5. Boss Waves
```python
def generate_boss_wave(wave_number):
    if random.random() < 0.08:  # 8% chance
        escort_count = max(5, int(8 + wave_number))
        
        return create_wave(
            boss="mothership",
            escorts=generate_boss_escorts(escort_count),
            spawn_pattern="boss_entrance",
            boss_abilities=True
        )
```

**Characteristics:**
- **Trigger**: 8% random chance per wave
- **Composition**: Single mothership with escort fleet
- **Escort Types**: Assault Ships and Stealth Ships
- **Special Abilities**: Enhanced mothership capabilities
- **Purpose**: Single powerful threat requiring focused defense

## 📊 Enemy Composition System

### Game Phase Distribution
```python
def get_enemy_distribution(wave_number):
    if wave_number <= 5:  # Early Game
        return {
            "basic": 0.6,
            "kamikaze": 0.3,
            "assault": 0.1
        }
    elif wave_number <= 15:  # Mid Game
        return {
            "basic": 0.4,
            "kamikaze": 0.2,
            "assault": 0.2,
            "large": 0.15,
            "stealth": 0.05
        }
    elif wave_number <= 30:  # Late Game
        return {
            "basic": 0.25,
            "kamikaze": 0.15,
            "assault": 0.2,
            "large": 0.2,
            "stealth": 0.1,
            "cruiser": 0.1
        }
    else:  # End Game
        return {
            "basic": 0.2,
            "kamikaze": 0.1,
            "assault": 0.2,
            "large": 0.2,
            "stealth": 0.15,
            "cruiser": 0.15
        }
```

### Point Allocation Algorithm
```python
def allocate_points_to_enemies(total_points, distribution):
    enemies = []
    remaining_points = total_points
    
    # Sort enemy types by point value (highest first)
    sorted_types = sorted(ENEMY_POINT_VALUES.items(), 
                         key=lambda x: x[1], reverse=True)
    
    for enemy_type, point_value in sorted_types:
        target_ratio = distribution.get(enemy_type, 0)
        target_points = total_points * target_ratio
        enemy_count = int(target_points / point_value)
        
        # Add enemies and deduct points
        for _ in range(enemy_count):
            if remaining_points >= point_value:
                enemies.append(enemy_type)
                remaining_points -= point_value
    
    # Fill remaining points with basic enemies
    while remaining_points >= ENEMY_POINT_VALUES["basic"]:
        enemies.append("basic")
        remaining_points -= ENEMY_POINT_VALUES["basic"]
    
    return enemies
```

## 🗺️ Spawn Patterns

### Single Point Spawning
```python
def generate_single_spawn():
    # Choose random edge of the map
    edge = random.choice(["top", "right", "bottom", "left"])
    
    if edge == "top":
        x = random.randint(0, WORLD_WIDTH)
        y = random.randint(-50, 0)
    elif edge == "right":
        x = random.randint(WORLD_WIDTH, WORLD_WIDTH + 50)
        y = random.randint(0, WORLD_HEIGHT)
    # ... similar for other edges
    
    return (x, y)
```

### Multi-Directional Formation
```python
def generate_formation_spawns(num_formations):
    spawn_points = []
    
    for i in range(num_formations):
        # Distribute around perimeter
        side = i % 4
        
        if side == 0:  # Top edge
            x = random.randint(WORLD_WIDTH // 8, 7 * WORLD_WIDTH // 8)
            y = random.randint(-50, 50)
        elif side == 1:  # Right edge
            x = random.randint(WORLD_WIDTH - 50, WORLD_WIDTH + 50)
            y = random.randint(WORLD_HEIGHT // 8, 7 * WORLD_HEIGHT // 8)
        # ... similar for other sides
        
        spawn_points.append((x, y))
    
    # Randomize order for unpredictable attacks
    random.shuffle(spawn_points)
    return spawn_points
```

### Coordinated Assault
```python
def execute_coordinated_spawn(spawn_points, enemies):
    # Divide enemies among spawn points
    enemies_per_point = len(enemies) // len(spawn_points)
    spawn_groups = []
    
    for i, spawn_point in enumerate(spawn_points):
        start_idx = i * enemies_per_point
        end_idx = start_idx + enemies_per_point
        group_enemies = enemies[start_idx:end_idx]
        
        spawn_groups.append({
            'position': spawn_point,
            'enemies': group_enemies,
            'spawn_delay': i * 30  # Stagger spawning
        })
    
    return spawn_groups
```

## ⏱️ Wave Management

### Wave State Machine
```python
class WaveManager:
    def __init__(self):
        self.state = "waiting"
        self.current_wave = 1
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.wave_complete = False
        
    def update(self, delta_time):
        if self.state == "waiting":
            self.update_wait_timer(delta_time)
        elif self.state == "spawning":
            self.update_spawning(delta_time)
        elif self.state == "active":
            self.check_wave_completion()
        elif self.state == "complete":
            self.prepare_next_wave()
```

### Wave Completion Detection
```python
def check_wave_completion(self):
    # Wave complete when no enemies remain and no more to spawn
    if len(self.enemies) == 0 and len(self.enemies_to_spawn) == 0:
        self.wave_complete = True
        self.state = "complete"
        
        # Award completion bonuses
        award_wave_completion_bonus(self.current_wave)
        
        # Prepare next wave
        self.current_wave += 1
        self.wave_timer = WAVE_WAIT_TIME
        self.state = "waiting"
```

### Difficulty Adaptation
```python
def adapt_difficulty(player_performance):
    base_multiplier = 1.0
    
    # Analyze player performance metrics
    survival_time = get_player_survival_time()
    buildings_remaining = count_player_buildings()
    resources_remaining = get_player_resources()
    
    # Scale difficulty based on player success
    if survival_time > expected_survival_time:
        difficulty_multiplier = 1.1  # Increase difficulty
    elif buildings_remaining < expected_buildings:
        difficulty_multiplier = 0.9  # Decrease difficulty
    
    return base_multiplier * difficulty_multiplier
```

## 🎮 Strategic Implications

### Player Preparation Windows
- **Initial Grace Period**: 160 seconds for base setup
- **Inter-Wave Breaks**: 2 seconds for quick repairs/building
- **Formation Warning**: Visual/audio cues for major waves
- **Resource Management**: Balance spending vs. saving for upgrades

### Defensive Strategies by Wave Type
- **Normal Waves**: Standard defensive lines
- **Formation Waves**: 360-degree defense coverage
- **Elite Waves**: Concentrated firepower and energy reserves
- **Swarm Waves**: Area damage and rapid-fire weapons
- **Boss Waves**: Focus fire and priority targeting

### Economic Pressure
```python
def calculate_resource_pressure(wave_number):
    # Increased costs over time
    building_cost_multiplier = 1.0 + (wave_number * 0.02)
    energy_consumption_rate = 1.0 + (wave_number * 0.01)
    
    # Decreased income efficiency
    mining_efficiency = max(0.5, 1.0 - (wave_number * 0.005))
    
    return {
        'cost_multiplier': building_cost_multiplier,
        'energy_rate': energy_consumption_rate,
        'mining_efficiency': mining_efficiency
    }
```

## 📈 Performance Balancing

### Wave Difficulty Metrics
- **Clear Rate**: Percentage of players surviving each wave
- **Average Survival Time**: How long players last
- **Resource Depletion**: Rate of mineral/energy consumption
- **Building Loss Rate**: Infrastructure damage per wave

### Dynamic Adjustments
```python
def balance_wave_difficulty(wave_data, player_statistics):
    target_clear_rate = 0.7  # 70% of players should survive normal waves
    actual_clear_rate = calculate_clear_rate(wave_data)
    
    if actual_clear_rate < target_clear_rate - 0.1:
        # Wave too difficult, reduce enemy points
        return apply_difficulty_reduction(0.9)
    elif actual_clear_rate > target_clear_rate + 0.1:
        # Wave too easy, increase enemy points
        return apply_difficulty_increase(1.1)
    else:
        # Difficulty balanced
        return 1.0
```

---

*The Wave System creates escalating challenge through varied enemy compositions, spawn patterns, and special events, requiring players to continuously adapt their strategies and expand their defensive capabilities.* 