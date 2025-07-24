"""
Research and upgrade system for Space Game Clone.
Provides technology trees for improving building performance, defenses, and capabilities.
"""

import pygame
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ResearchNode:
    """Represents a single research upgrade."""
    id: str
    name: str
    description: str
    cost: int  # Minerals required
    prerequisites: List[str]  # Required research IDs
    completed: bool = False
    category: str = "general"  # Category for organization
    
    # Upgrade effects (building type -> attribute -> multiplier/bonus)
    building_effects: Dict[str, Dict[str, float]] = None
    global_effects: Dict[str, float] = None
    
    def __post_init__(self):
        if self.building_effects is None:
            self.building_effects = {}
        if self.global_effects is None:
            self.global_effects = {}


class ResearchSystem:
    """Manages the research tree and upgrade system."""
    
    def __init__(self):
        self.research_nodes: Dict[str, ResearchNode] = {}
        self.completed_research: set = set()
        self.selected_node: Optional[str] = None
        self.scroll_offset = 0
        self.max_scroll = 0
        
        self._initialize_research_tree()
    
    def _initialize_research_tree(self):
        """Initialize all research nodes and their relationships."""
        
        # Combat Upgrades
        self.research_nodes["armor_plating"] = ResearchNode(
            id="armor_plating",
            name="Armor Plating",
            description="Buildings take 25% less damage",
            cost=150,
            prerequisites=[],
            category="defense",
            global_effects={"building_armor": 0.75}  # 25% damage reduction
        )
        
        self.research_nodes["reinforced_structures"] = ResearchNode(
            id="reinforced_structures",
            name="Reinforced Structures",
            description="All buildings +50% health",
            cost=200,
            prerequisites=["armor_plating"],
            category="defense",
            global_effects={"building_health": 1.5}
        )
        
        self.research_nodes["advanced_armor"] = ResearchNode(
            id="advanced_armor",
            name="Advanced Armor",
            description="Buildings take 50% less damage",
            cost=400,
            prerequisites=["reinforced_structures"],
            category="defense",
            global_effects={"building_armor": 0.5}  # Replaces armor_plating
        )
        
        # Turret Upgrades
        self.research_nodes["targeting_systems"] = ResearchNode(
            id="targeting_systems",
            name="Targeting Systems",
            description="Turrets +25% range",
            cost=100,
            prerequisites=[],
            category="combat",
            building_effects={"turret": {"range": 1.25}}
        )
        
        self.research_nodes["rapid_fire"] = ResearchNode(
            id="rapid_fire",
            name="Rapid Fire",
            description="Turrets fire 50% faster",
            cost=180,
            prerequisites=["targeting_systems"],
            category="combat",
            building_effects={"turret": {"fire_rate": 1.5}}
        )
        
        self.research_nodes["explosive_rounds"] = ResearchNode(
            id="explosive_rounds",
            name="Explosive Rounds",
            description="Turrets +100% damage",
            cost=300,
            prerequisites=["rapid_fire"],
            category="combat",
            building_effects={"turret": {"damage": 2.0}}
        )
        
        # Laser Upgrades
        self.research_nodes["laser_focusing"] = ResearchNode(
            id="laser_focusing",
            name="Laser Focusing",
            description="Lasers +30% range, +25% damage",
            cost=120,
            prerequisites=[],
            category="combat",
            building_effects={"laser": {"range": 1.3, "damage": 1.25}, 
                            "superlaser": {"range": 1.3, "damage": 1.25}}
        )
        
        self.research_nodes["beam_intensity"] = ResearchNode(
            id="beam_intensity",
            name="Beam Intensity",
            description="Lasers +75% damage",
            cost=250,
            prerequisites=["laser_focusing"],
            category="combat",
            building_effects={"laser": {"damage": 1.75}, 
                            "superlaser": {"damage": 1.75}}
        )
        
        self.research_nodes["continuous_beam"] = ResearchNode(
            id="continuous_beam",
            name="Continuous Beam",
            description="Lasers fire continuously",
            cost=400,
            prerequisites=["beam_intensity"],
            category="combat",
            building_effects={"laser": {"fire_rate": 3.0}, 
                            "superlaser": {"fire_rate": 3.0}}
        )
        
        # Hangar Upgrades
        self.research_nodes["fighter_design"] = ResearchNode(
            id="fighter_design",
            name="Fighter Design",
            description="Hangars +1 ship capacity",
            cost=200,
            prerequisites=[],
            category="support",
            building_effects={"hangar": {"capacity": 1}}  # Additive bonus
        )
        
        self.research_nodes["advanced_engines"] = ResearchNode(
            id="advanced_engines",
            name="Advanced Engines",
            description="Fighter ships +50% speed",
            cost=180,
            prerequisites=["fighter_design"],
            category="support",
            global_effects={"fighter_speed": 1.5}
        )
        
        self.research_nodes["ship_armor"] = ResearchNode(
            id="ship_armor",
            name="Ship Armor",
            description="Fighter ships +100% health",
            cost=220,
            prerequisites=["fighter_design"],
            category="support",
            global_effects={"fighter_health": 2.0}
        )
        
        self.research_nodes["squadron_tactics"] = ResearchNode(
            id="squadron_tactics",
            name="Squadron Tactics",
            description="Hangars +2 ship capacity, ships +25% damage",
            cost=350,
            prerequisites=["advanced_engines", "ship_armor"],
            category="support",
            building_effects={"hangar": {"capacity": 2}},
            global_effects={"fighter_damage": 1.25}
        )
        
        # Mining Upgrades
        self.research_nodes["efficient_extraction"] = ResearchNode(
            id="efficient_extraction",
            name="Efficient Extraction",
            description="Miners +50% mining rate",
            cost=100,
            prerequisites=[],
            category="economy",
            building_effects={"miner": {"mining_rate": 1.5}}
        )
        
        self.research_nodes["deep_drilling"] = ResearchNode(
            id="deep_drilling",
            name="Deep Drilling",
            description="Miners +25% range, +25% rate",
            cost=180,
            prerequisites=["efficient_extraction"],
            category="economy",
            building_effects={"miner": {"range": 1.25, "mining_rate": 1.25}}
        )
        
        self.research_nodes["automated_mining"] = ResearchNode(
            id="automated_mining",
            name="Automated Mining",
            description="Miners can mine 2 more asteroids",
            cost=300,
            prerequisites=["deep_drilling"],
            category="economy",
            building_effects={"miner": {"max_asteroids": 2}}  # Additive
        )
        
        # Energy Upgrades
        self.research_nodes["solar_efficiency"] = ResearchNode(
            id="solar_efficiency",
            name="Solar Efficiency",
            description="Solar panels +50% energy production",
            cost=120,
            prerequisites=[],
            category="energy",
            building_effects={"solar": {"production": 1.5}}
        )
        
        self.research_nodes["energy_storage"] = ResearchNode(
            id="energy_storage",
            name="Energy Storage",
            description="Batteries +100% capacity",
            cost=150,
            prerequisites=[],
            category="energy",
            building_effects={"battery": {"capacity": 2.0}}
        )
        
        self.research_nodes["power_grid"] = ResearchNode(
            id="power_grid",
            name="Power Grid",
            description="Connectors +2 connection limit",
            cost=200,
            prerequisites=["energy_storage"],
            category="energy",
            building_effects={"connector": {"connections": 2}}  # Additive
        )
        
        self.research_nodes["fusion_power"] = ResearchNode(
            id="fusion_power",
            name="Fusion Power",
            description="Solar panels +100% production, batteries +50% capacity",
            cost=400,
            prerequisites=["solar_efficiency", "power_grid"],
            category="energy",
            building_effects={"solar": {"production": 2.0}, "battery": {"capacity": 1.5}}
        )
        
        # Special Upgrades
        self.research_nodes["repair_protocols"] = ResearchNode(
            id="repair_protocols",
            name="Repair Protocols",
            description="Repair stations +100% healing rate",
            cost=160,
            prerequisites=[],
            category="support",
            building_effects={"repair": {"healing_rate": 2.0}}
        )
        
        self.research_nodes["missile_guidance"] = ResearchNode(
            id="missile_guidance",
            name="Missile Guidance",
            description="Missile launchers +50% range, +25% damage",
            cost=220,
            prerequisites=[],
            category="combat",
            building_effects={"missile_launcher": {"range": 1.5, "damage": 1.25}}
        )
        
        self.research_nodes["warhead_upgrade"] = ResearchNode(
            id="warhead_upgrade",
            name="Warhead Upgrade",
            description="Missiles +100% splash damage and radius",
            cost=350,
            prerequisites=["missile_guidance"],
            category="combat",
            building_effects={"missile_launcher": {"splash_damage": 2.0, "splash_radius": 2.0}}
        )
        
        # Advanced Combat Research
        self.research_nodes["plasma_weapons"] = ResearchNode(
            id="plasma_weapons",
            name="Plasma Weapons",
            description="All weapons +25% damage, ignore 50% armor",
            cost=500,
            prerequisites=["explosive_rounds", "continuous_beam"],
            category="combat",
            global_effects={"weapon_damage": 1.25, "armor_penetration": 0.5}
        )
        
        self.research_nodes["shield_generators"] = ResearchNode(
            id="shield_generators",
            name="Shield Generators",
            description="Buildings absorb first 50 damage per wave",
            cost=450,
            prerequisites=["advanced_armor"],
            category="defense",
            global_effects={"building_shields": 50}
        )
        
        self.research_nodes["point_defense"] = ResearchNode(
            id="point_defense",
            name="Point Defense",
            description="Buildings have 25% chance to intercept projectiles",
            cost=350,
            prerequisites=["targeting_systems"],
            category="defense",
            global_effects={"projectile_intercept": 0.25}
        )
        
        # Economic Expansion
        self.research_nodes["mineral_processing"] = ResearchNode(
            id="mineral_processing",
            name="Mineral Processing",
            description="All mineral income +50%",
            cost=250,
            prerequisites=["automated_mining"],
            category="economy",
            global_effects={"mineral_income": 1.5}
        )
        
        self.research_nodes["trade_networks"] = ResearchNode(
            id="trade_networks",
            name="Trade Networks",
            description="Passive mineral income +2/sec, building costs -25%",
            cost=400,
            prerequisites=["mineral_processing"],
            category="economy",
            global_effects={"passive_income": 2.0, "building_cost": 0.75}
        )
        
        # Advanced Energy Research
        self.research_nodes["quantum_generators"] = ResearchNode(
            id="quantum_generators",
            name="Quantum Generators",
            description="All energy buildings +50% efficiency, -25% power consumption",
            cost=600,
            prerequisites=["fusion_power"],
            category="energy",
            building_effects={"solar": {"production": 1.5}},
            global_effects={"power_consumption": 0.75}
        )
        
        self.research_nodes["auto_repair"] = ResearchNode(
            id="auto_repair",
            name="Auto-Repair Systems",
            description="All buildings slowly regenerate health",
            cost=400,
            prerequisites=["repair_protocols"],
            category="support",
            global_effects={"building_regen": 0.5}  # HP per second
        )
        
        # Advanced Tactics
        self.research_nodes["orbital_bombardment"] = ResearchNode(
            id="orbital_bombardment",
            name="Orbital Bombardment",
            description="Unlocks orbital strike ability (hotkey: O)",
            cost=800,
            prerequisites=["plasma_weapons", "quantum_generators"],
            category="special",
            global_effects={"orbital_strike": 1}
        )
        
        self.research_nodes["temporal_shields"] = ResearchNode(
            id="temporal_shields",
            name="Temporal Shields",
            description="Buildings can phase out for 3 seconds (hotkey: T)",
            cost=700,
            prerequisites=["shield_generators", "quantum_generators"],
            category="special",
            global_effects={"temporal_phase": 1}
        )
        
        # New Building Unlock
        self.research_nodes["force_field_tech"] = ResearchNode(
            id="force_field_tech",
            name="Force Field Technology",
            description="Unlocks Force Field Generator building",
            cost=600,
            prerequisites=["shield_generators", "point_defense"],
            category="special",
            global_effects={"force_field_unlocked": 1}
        )
        
        # Ultimate Research
        self.research_nodes["singularity_core"] = ResearchNode(
            id="singularity_core",
            name="Singularity Core",
            description="Unlocks ultimate defensive structure",
            cost=1200,
            prerequisites=["orbital_bombardment", "temporal_shields", "trade_networks"],
            category="ultimate",
            global_effects={"singularity_unlocked": 1}
        )
        
        # Wave Difficulty Modifiers
        self.research_nodes["early_warning"] = ResearchNode(
            id="early_warning",
            name="Early Warning System",
            description="See next wave composition, +15 seconds prep time",
            cost=300,
            prerequisites=["targeting_systems"],
            category="tactical",
            global_effects={"wave_preview": 1, "wave_delay": 15}
        )
        
        self.research_nodes["reinforcements"] = ResearchNode(
            id="reinforcements",
            name="Emergency Reinforcements",
            description="Spawn 3 allied fighters when base takes damage",
            cost=500,
            prerequisites=["squadron_tactics"],
            category="tactical",
            global_effects={"emergency_fighters": 3}
        )
    
    def can_research(self, node_id: str, minerals: int) -> bool:
        """Check if a research node can be researched."""
        if node_id not in self.research_nodes:
            return False
        
        node = self.research_nodes[node_id]
        
        # Already completed
        if node.completed:
            return False
        
        # Not enough minerals
        if minerals < node.cost:
            return False
        
        # Check prerequisites
        for prereq in node.prerequisites:
            if prereq not in self.completed_research:
                return False
        
        return True
    
    def research(self, node_id: str, minerals: int) -> Tuple[bool, int]:
        """Attempt to research a node. Returns (success, cost)."""
        if not self.can_research(node_id, minerals):
            return False, 0
        
        node = self.research_nodes[node_id]
        node.completed = True
        self.completed_research.add(node_id)
        
        return True, node.cost
    
    def get_building_multiplier(self, building_type: str, attribute: str) -> float:
        """Get the total multiplier for a building attribute from all completed research."""
        multiplier = 1.0
        additive_bonus = 0
        
        for node_id in self.completed_research:
            node = self.research_nodes[node_id]
            
            # Check building-specific effects
            if building_type in node.building_effects:
                if attribute in node.building_effects[building_type]:
                    effect = node.building_effects[building_type][attribute]
                    if attribute in ["capacity", "max_asteroids", "connections"]:
                        additive_bonus += effect  # Additive for capacity-type attributes
                    else:
                        multiplier *= effect  # Multiplicative for most attributes
        
        return multiplier + additive_bonus
    
    def get_global_multiplier(self, attribute: str) -> float:
        """Get the global multiplier for an attribute from all completed research."""
        multiplier = 1.0
        
        for node_id in self.completed_research:
            node = self.research_nodes[node_id]
            
            if attribute in node.global_effects:
                effect = node.global_effects[attribute]
                if attribute == "building_armor":
                    # For armor, we want the latest (strongest) research to override
                    multiplier = effect
                else:
                    multiplier *= effect
        
        return multiplier
    
    def get_available_research(self) -> List[ResearchNode]:
        """Get all research nodes that can currently be researched."""
        available = []
        for node in self.research_nodes.values():
            if not node.completed:
                # Check if prerequisites are met
                prereqs_met = all(prereq in self.completed_research for prereq in node.prerequisites)
                if prereqs_met:
                    available.append(node)
        return available
    
    def get_research_by_category(self) -> Dict[str, List[ResearchNode]]:
        """Get all research nodes organized by category."""
        categories = {}
        for node in self.research_nodes.values():
            if node.category not in categories:
                categories[node.category] = []
            categories[node.category].append(node)
        
        # Sort each category by cost
        for category in categories:
            categories[category].sort(key=lambda n: n.cost)
        
        return categories 