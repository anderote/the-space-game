"""
Research System - Manages technology research and global bonuses
"""

import json
import time
from enum import Enum
from typing import Dict, List, Optional, Set


class ResearchState(Enum):
    """Research technology states"""
    AVAILABLE = "available"
    RESEARCHING = "researching" 
    COMPLETED = "completed"
    LOCKED = "locked"


class ResearchTechnology:
    """Represents a single research technology"""
    
    def __init__(self, tech_id: str, config: dict):
        self.tech_id = tech_id
        self.name = config.get("name", tech_id)
        self.description = config.get("description", "")
        self.cost = config.get("cost", 100)
        self.energy_cost = config.get("energy_cost", 50)
        self.research_time = config.get("research_time", 30)  # seconds
        self.prerequisites = config.get("prerequisites", [])
        self.effects = config.get("effects", {})
        self.category = config.get("category", "general")
        
        # Research state
        self.state = ResearchState.LOCKED
        self.research_start_time = 0
        self.research_progress = 0.0  # 0.0 to 1.0


class ResearchSystem:
    """Manages technology research and global bonuses"""
    
    def __init__(self, config_loader):
        self.config = config_loader
        self.technologies: Dict[str, ResearchTechnology] = {}
        self.completed_research: Set[str] = set()
        self.current_research: Optional[str] = None
        
        # Global research bonuses - these affect all relevant buildings/systems
        self.bonuses = {
            "mining_rate_multiplier": 1.0,
            "solar_power_multiplier": 1.0,
            "nuclear_power_multiplier": 1.0,
            "turret_damage_multiplier": 1.0,
            "turret_range_multiplier": 1.0,
            "turret_cooldown_multiplier": 1.0,
            "building_health_multiplier": 1.0,
            "connection_range_multiplier": 1.0,
            "construction_speed_multiplier": 1.0,
            "energy_cost_multiplier": 1.0,
            "repair_rate_multiplier": 1.0,
            "repair_cost_multiplier": 1.0,
            "mining_energy_multiplier": 1.0,
            "miner_max_connections_bonus": 0,
            "max_connections_bonus": 0
        }
        
        self._load_research_config()
        self._update_research_availability()
    
    def _load_research_config(self):
        """Load research technologies from config"""
        try:
            research_config = self.config.research
            tech_configs = research_config.get("research_technologies", {})
            
            for tech_id, tech_config in tech_configs.items():
                self.technologies[tech_id] = ResearchTechnology(tech_id, tech_config)
                
            print(f"✓ Loaded {len(self.technologies)} research technologies")
            
        except Exception as e:
            print(f"Error loading research config: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_research_availability(self):
        """Update which technologies are available for research"""
        for tech in self.technologies.values():
            if tech.tech_id in self.completed_research:
                tech.state = ResearchState.COMPLETED
            elif tech.tech_id == self.current_research:
                tech.state = ResearchState.RESEARCHING
            elif self._are_prerequisites_met(tech.prerequisites):
                tech.state = ResearchState.AVAILABLE
            else:
                tech.state = ResearchState.LOCKED
    
    def _are_prerequisites_met(self, prerequisites: List[str]) -> bool:
        """Check if all prerequisites for a technology are met"""
        return all(prereq in self.completed_research for prereq in prerequisites)
    
    def can_afford_research(self, tech_id: str, minerals: float, energy: float) -> bool:
        """Check if player can afford to start this research"""
        if tech_id not in self.technologies:
            return False
            
        tech = self.technologies[tech_id]
        return (tech.state == ResearchState.AVAILABLE and 
                minerals >= tech.cost and 
                energy >= tech.energy_cost)
    
    def start_research(self, tech_id: str, minerals: float, energy: float) -> bool:
        """Start researching a technology"""
        if not self.can_afford_research(tech_id, minerals, energy):
            tech = self.technologies[tech_id]
            print(f"Cannot afford research: {tech_id}")
            print(f"  Required: {tech.cost} minerals, {tech.energy_cost} energy")
            print(f"  Available: {minerals} minerals, {energy} energy")
            return False
            
        if self.current_research is not None:
            print(f"Already researching: {self.current_research}")
            return False
            
        tech = self.technologies[tech_id]
        tech.state = ResearchState.RESEARCHING
        tech.research_start_time = time.time()
        tech.research_progress = 0.0
        self.current_research = tech_id
        
        print(f"🔬 Started researching: {tech.name}")
        return True
    
    def cancel_research(self) -> Optional[str]:
        """Cancel current research and return the tech ID"""
        if self.current_research is None:
            return None
            
        canceled_tech = self.current_research
        tech = self.technologies[self.current_research]
        tech.state = ResearchState.AVAILABLE
        tech.research_progress = 0.0
        tech.research_start_time = 0
        self.current_research = None
        
        self._update_research_availability()
        print(f"🚫 Canceled research: {tech.name}")
        return canceled_tech
    
    def update(self, dt: float):
        """Update research progress"""
        if self.current_research is None:
            return
            
        tech = self.technologies[self.current_research]
        elapsed_time = time.time() - tech.research_start_time
        tech.research_progress = min(1.0, elapsed_time / tech.research_time)
        
        # Check if research is complete
        if tech.research_progress >= 1.0:
            self._complete_research(tech.tech_id)
    
    def _complete_research(self, tech_id: str):
        """Complete a research technology and apply its effects"""
        tech = self.technologies[tech_id]
        tech.state = ResearchState.COMPLETED
        self.completed_research.add(tech_id)
        self.current_research = None
        
        # Apply research effects to global bonuses
        for effect_name, effect_value in tech.effects.items():
            if effect_name in self.bonuses:
                # For multipliers, we multiply the current bonus
                if "multiplier" in effect_name:
                    self.bonuses[effect_name] *= effect_value
                # For bonus values (like connection bonuses), we add them
                elif "bonus" in effect_name:
                    self.bonuses[effect_name] += effect_value
                else:
                    self.bonuses[effect_name] += effect_value
                    
        self._update_research_availability()
        print(f"🎉 Research completed: {tech.name}")
        print(f"✓ Applied effects: {tech.effects}")
    
    def get_available_research(self) -> List[ResearchTechnology]:
        """Get list of technologies available for research"""
        return [tech for tech in self.technologies.values() 
                if tech.state == ResearchState.AVAILABLE]
    
    def get_researching_technology(self) -> Optional[ResearchTechnology]:
        """Get currently researching technology"""
        if self.current_research:
            return self.technologies[self.current_research]
        return None
    
    def get_completed_research(self) -> List[ResearchTechnology]:
        """Get list of completed research technologies"""
        return [tech for tech in self.technologies.values() 
                if tech.state == ResearchState.COMPLETED]
    
    def get_research_by_category(self, category: str) -> List[ResearchTechnology]:
        """Get research technologies by category"""
        return [tech for tech in self.technologies.values() 
                if tech.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all research categories"""
        try:
            research_config = self.config.get_research_config()
            return list(research_config.get("research_categories", {}).keys())
        except:
            return []
    
    def get_category_info(self, category: str) -> dict:
        """Get category information (name, color, etc.)"""
        try:
            research_config = self.config.get_research_config()
            categories = research_config.get("research_categories", {})
            return categories.get(category, {"name": category, "color": [1, 1, 1, 1]})
        except:
            return {"name": category, "color": [1, 1, 1, 1]}
    
    def get_bonus(self, bonus_name: str) -> float:
        """Get current value of a research bonus"""
        return self.bonuses.get(bonus_name, 1.0)
    
    def get_research_progress_text(self) -> str:
        """Get text description of current research progress"""
        if self.current_research is None:
            return "No active research"
            
        tech = self.technologies[self.current_research]
        elapsed = time.time() - tech.research_start_time
        remaining = max(0, tech.research_time - elapsed)
        
        if remaining > 0:
            return f"Researching {tech.name} - {remaining:.1f}s remaining"
        else:
            return f"Completing {tech.name}..."
