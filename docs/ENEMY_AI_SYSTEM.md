# Enemy AI System

## 📋 Overview

The Enemy AI System manages 7 distinct enemy types with unique behaviors, weapons, and tactical roles. Enemies spawn in waves around the map perimeter and attack the player's base and infrastructure using various AI patterns and special abilities.

## 🤖 Core AI Framework

### AI State Machine
```python
class EnemyAI:
    def __init__(self):
        self.state = "seeking"
        self.target = None
        self.last_state_change = 0
        
    states = {
        "seeking": "Looking for nearest target",
        "moving": "Pathfinding toward target", 
        "orbiting": "Circling target at optimal range",
        "attacking": "Engaging target with weapons",
        "retreating": "Moving away from threats",
        "special": "Executing special abilities"
    }
```

### Target Selection Algorithm
```python
def find_nearest_target(enemy, buildings, base_pos, friendly_ships):
    # Priority order: Friendly ships > Buildings > Base
    all_targets = []
    
    # Add all potential targets with priorities
    for ship in friendly_ships:
        distance = calculate_distance(enemy, ship)
        all_targets.append((ship, distance, priority=3))
    
    for building in buildings:
        distance = calculate_distance(enemy, building)
        all_targets.append((building, distance, priority=2))
    
    # Base as fallback target
    base_distance = calculate_distance(enemy, base_pos)
    all_targets.append((base_pos, base_distance, priority=1))
    
    # Select closest target with highest priority
    return min(all_targets, key=lambda x: (x[2], x[1]))
```

### Movement Behavior
```python
def update_movement(enemy, target, delta_time):
    distance_to_target = calculate_distance(enemy, target)
    
    if distance_to_target > enemy.orbit_radius + 10:
        # Move directly toward target
        direction = normalize(target.position - enemy.position)
        enemy.position += direction * enemy.speed * delta_time
        enemy.is_orbiting = False
        
    else:
        # Enter orbital behavior
        if not enemy.is_orbiting:
            enemy.orbit_angle = calculate_angle_to_target(enemy, target)
            enemy.is_orbiting = True
        
        # Orbital movement
        enemy.orbit_angle += enemy.orbit_speed * delta_time
        offset = Vector2(
            enemy.orbit_radius * cos(enemy.orbit_angle),
            enemy.orbit_radius * sin(enemy.orbit_angle)
        )
        enemy.position = target.position + offset
```

## 👾 Enemy Types

### 1. Basic Fighter
```json
{
  "name": "Fighter",
  "health": "24 × wave_number",
  "speed": 0.5,
  "size": 15,
  "color": [200, 200, 200],
  "points": 1,
  "abilities": ["basic_laser", "orbit"]
}
```

**AI Behavior:**
- **Targeting**: Nearest building or base
- **Movement**: Direct approach then orbital pattern
- **Combat**: Basic laser every 60 frames (1 second)
- **Tactics**: Swarm behavior, strength in numbers

**Combat Stats:**
- **Weapon**: Basic laser beam
- **Damage**: Low, sustained
- **Range**: 120 pixels
- **Cooldown**: 60 frames

### 2. Kamikaze Ship
```json
{
  "name": "Kamikaze Ship", 
  "health": 30,
  "speed": 1.25,
  "size": 10,
  "color": [255, 50, 50],
  "points": 2,
  "abilities": ["suicide_attack"]
}
```

**AI Behavior:**
- **Targeting**: Prioritizes high-value buildings
- **Movement**: Direct high-speed approach, no orbiting
- **Combat**: Explosion on contact (20 pixel range)
- **Tactics**: Sacrifice for maximum damage

**Special Mechanics:**
- **Explosion Damage**: 50 points
- **Trigger Distance**: 20 pixels from target
- **Self-Destruction**: Dies after explosion
- **Area Effect**: Damages all buildings in blast radius

### 3. Large Ship
```json
{
  "name": "Large Ship",
  "health": 200,
  "speed": 0.25, 
  "size": 25,
  "color": [0, 100, 255],
  "points": 5,
  "abilities": ["building_laser"]
}
```

**AI Behavior:**
- **Targeting**: Prioritizes buildings over base
- **Movement**: Slow, methodical approach
- **Combat**: Powerful building-targeting laser
- **Tactics**: Tank role, absorbs damage while dealing heavy hits

**Combat Stats:**
- **Weapon**: Building laser cannon
- **Damage**: 7 per shot
- **Range**: 200 pixels
- **Cooldown**: 90 frames (1.5 seconds)
- **Special**: Can damage buildings from outside most turret ranges

### 4. Assault Ship
```json
{
  "name": "Assault Ship",
  "health": 120,
  "speed": 0.75,
  "size": 18, 
  "color": [150, 75, 0],
  "points": 3,
  "abilities": ["machine_gun"]
}
```

**AI Behavior:**
- **Targeting**: Aggressive building targeting
- **Movement**: Medium-speed direct approach
- **Combat**: Rapid-fire burst attacks
- **Tactics**: Sustained DPS through volume of fire

**Combat Stats:**
- **Weapon**: Machine gun bursts
- **Damage**: 4 per shot
- **Range**: 150 pixels
- **Burst Pattern**: 5 shots, then 120-frame pause
- **Shot Interval**: 30 frames between shots in burst

### 5. Stealth Ship
```json
{
  "name": "Stealth Ship",
  "health": 80,
  "speed": 1.0,
  "size": 12,
  "color": [100, 0, 150],
  "points": 4,
  "abilities": ["cloaking", "emp_burst"]
}
```

**AI Behavior:**
- **Targeting**: Multiple buildings simultaneously (EMP)
- **Movement**: Cloaked approach phases
- **Combat**: Area EMP attacks
- **Tactics**: Disruption and infrastructure damage

**Special Abilities:**
- **Cloaking**: 120 frames invisible, 180 frames visible cycle
- **EMP Weapon**: 100 pixel area effect
- **EMP Damage**: 12 damage to all buildings in range
- **EMP Cooldown**: 180 frames (3 seconds)

**Stealth Mechanics:**
```python
def update_stealth(stealth_ship, delta_time):
    stealth_ship.stealth_timer += delta_time
    
    if stealth_ship.is_cloaked:
        if stealth_ship.stealth_timer >= CLOAK_DURATION:
            stealth_ship.is_cloaked = False
            stealth_ship.stealth_timer = 0
    else:
        if stealth_ship.stealth_timer >= DECLOAK_DURATION:
            stealth_ship.is_cloaked = True
            stealth_ship.stealth_timer = 0
```

### 6. Heavy Cruiser
```json
{
  "name": "Heavy Cruiser",
  "health": 300,
  "speed": 0.4,
  "size": 30,
  "color": [80, 80, 120], 
  "points": 6,
  "abilities": ["plasma_cannon"]
}
```

**AI Behavior:**
- **Targeting**: High-value buildings and base
- **Movement**: Slow but inexorable advance
- **Combat**: Charging plasma cannon
- **Tactics**: Siege warfare, breakthrough unit

**Combat Stats:**
- **Weapon**: Charging plasma cannon
- **Damage**: 15 per shot (devastating)
- **Range**: 250 pixels
- **Charge Time**: 90 frames (1.5 seconds)
- **Total Cooldown**: 150 frames (2.5 seconds)

**Plasma Cannon Mechanics:**
```python
def update_plasma_cannon(cruiser, delta_time):
    if not cruiser.is_charging and target_in_range:
        cruiser.is_charging = True
        cruiser.charge_start_time = current_time
        
    elif cruiser.is_charging:
        charge_progress = (current_time - cruiser.charge_start_time) / CHARGE_TIME
        
        if charge_progress >= 1.0:
            fire_plasma_shot(cruiser, cruiser.target)
            cruiser.is_charging = False
            cruiser.last_shot_time = current_time
```

### 7. Mothership
```json
{
  "name": "Mothership",
  "health": "120 × wave_number (5× basic)",
  "speed": 0.6,
  "size": 25,
  "color": [120, 0, 120],
  "points": 10,
  "abilities": ["missile_launcher", "command"]
}
```

**AI Behavior:**
- **Targeting**: Strategic priority targeting
- **Movement**: Calculated positioning for maximum effect
- **Combat**: Long-range missile bombardment
- **Tactics**: Command unit, coordinates other enemies

**Combat Stats:**
- **Weapon**: Long-range missiles
- **Damage**: 15 per missile
- **Range**: 400 pixels (longest enemy range)
- **Cooldown**: 120 frames (2 seconds)
- **Special**: Can outrange most player defenses

**Spawn Mechanics:**
- **Availability**: Waves 3+ only
- **Spawn Chance**: 15% per enemy slot
- **Health Scaling**: 5× normal enemy health formula
- **Elite Status**: Treated as mini-boss

## 🎯 Advanced AI Behaviors

### Swarm Intelligence
```python
def update_swarm_behavior(enemies):
    for enemy in enemies:
        nearby_enemies = find_enemies_in_radius(enemy, 100)
        
        if len(nearby_enemies) >= 3:
            # Coordinate attack on same target
            shared_target = most_common_target(nearby_enemies)
            enemy.target = shared_target
            
            # Adjust positioning to avoid overlap
            enemy.orbit_radius += random.uniform(-10, 10)
```

### Formation Flying
```python
def update_formation(enemy_group, formation_type):
    if formation_type == "wedge":
        for i, enemy in enumerate(enemy_group):
            offset_angle = (i - len(enemy_group)/2) * 0.3
            enemy.formation_offset = Vector2(
                30 * cos(offset_angle),
                30 * sin(offset_angle)
            )
```

### Adaptive Targeting
```python
def calculate_target_priority(enemy, potential_targets):
    priorities = {}
    
    for target in potential_targets:
        priority = 0
        
        # Distance factor (closer = higher priority)
        distance = calculate_distance(enemy, target)
        priority += 1000 / max(distance, 1)
        
        # Health factor (weaker = higher priority)  
        if hasattr(target, 'health'):
            priority += (target.max_health - target.health) * 0.1
        
        # Building type priority
        if target.type == "solar":
            priority += 50  # Target power infrastructure
        elif target.type == "connector":
            priority += 75  # Critical network nodes
        elif target.type == "turret":
            priority += 25  # Defensive threats
        
        priorities[target] = priority
    
    return max(priorities.items(), key=lambda x: x[1])[0]
```

## ⚔️ Combat Mechanics

### Weapon Systems
```python
class EnemyWeapon:
    def __init__(self, weapon_type):
        self.type = weapon_type
        self.damage = WEAPON_STATS[weapon_type]['damage']
        self.range = WEAPON_STATS[weapon_type]['range']
        self.cooldown = WEAPON_STATS[weapon_type]['cooldown']
        self.last_fire_time = 0
        
    def can_fire(self, current_time):
        return current_time - self.last_fire_time >= self.cooldown
        
    def fire(self, shooter, target):
        if self.can_fire(current_time):
            create_projectile(shooter.position, target.position, self.damage)
            self.last_fire_time = current_time
            return True
        return False
```

### Damage Application
```python
def apply_damage(target, damage, damage_type="direct"):
    if damage_type == "direct":
        target.health -= damage
        
    elif damage_type == "area":
        # Find all targets in splash radius
        nearby_targets = find_targets_in_radius(target.position, splash_radius)
        for nearby in nearby_targets:
            distance_factor = 1.0 - (distance_to_target / splash_radius)
            actual_damage = damage * distance_factor
            nearby.health -= actual_damage
            
    elif damage_type == "continuous":
        # Damage over time (lasers)
        target.health -= damage * delta_time
        
    # Check for destruction
    if target.health <= 0:
        destroy_target(target)
```

### Collision Detection
```python
def check_enemy_collisions(enemies, buildings, friendly_ships):
    for enemy in enemies:
        # Check building collisions
        for building in buildings:
            if circle_collision(enemy, building):
                apply_contact_damage(building, ENEMY_CONTACT_DAMAGE)
                
        # Check friendly ship collisions  
        for ship in friendly_ships:
            if circle_collision(enemy, ship):
                apply_contact_damage(ship, ENEMY_CONTACT_DAMAGE)
                apply_contact_damage(enemy, SHIP_RAMMING_DAMAGE)
```

## 📊 AI Performance Metrics

### Behavior Effectiveness
- **Target Selection Accuracy**: Optimal target choice percentage
- **Movement Efficiency**: Path length vs. optimal path
- **Combat Effectiveness**: Damage dealt per unit time
- **Survival Rate**: Time alive vs. expected lifetime

### Difficulty Balancing
```python
def calculate_ai_difficulty(wave_number):
    base_difficulty = 1.0
    
    # Increase reaction speed
    reaction_multiplier = 1.0 + (wave_number * 0.05)
    
    # Improve target selection
    targeting_accuracy = min(1.0, 0.5 + (wave_number * 0.02))
    
    # Enhanced coordination
    coordination_factor = min(2.0, 1.0 + (wave_number * 0.03))
    
    return {
        'reaction_speed': reaction_multiplier,
        'targeting_accuracy': targeting_accuracy,
        'coordination': coordination_factor
    }
```

---

*The Enemy AI System creates varied and challenging opponents that force players to adapt their strategies, with each enemy type requiring different defensive approaches and countermeasures.* 