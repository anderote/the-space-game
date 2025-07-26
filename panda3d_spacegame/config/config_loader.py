"""
Configuration loader for Space Game Clone.
Loads and manages all JSON configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class GameConfig:
    """Main configuration manager for the game."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files from the config directory."""
        config_files = {
            'game': 'game_config.json',
            'buildings': 'buildings.json',
            'enemies': 'enemies.json',
            'waves': 'waves.json',
            'research': 'research.json',
            'controls': 'controls.json'
        }
        
        for config_name, filename in config_files.items():
            filepath = self.config_dir / filename
            try:
                with open(filepath, 'r') as f:
                    self._configs[config_name] = json.load(f)
                print(f"✓ Loaded {config_name} configuration from {filename}")
            except FileNotFoundError:
                print(f"⚠ Warning: {filename} not found, using defaults")
                self._configs[config_name] = {}
            except json.JSONDecodeError as e:
                print(f"✗ Error loading {filename}: {e}")
                self._configs[config_name] = {}
    
    def get(self, config_name: str, key_path: str = None, default: Any = None) -> Any:
        """Get configuration value by path.
        
        Args:
            config_name: Name of the configuration (game, buildings, etc.)
            key_path: Dot-separated path to the value (e.g., 'display.screen_width')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if config_name not in self._configs:
            return default
        
        config = self._configs[config_name]
        
        if key_path is None:
            return config
        
        # Navigate through the key path
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, config_name: str, key_path: str, value: Any):
        """Set configuration value by path.
        
        Args:
            config_name: Name of the configuration
            key_path: Dot-separated path to the value
            value: Value to set
        """
        if config_name not in self._configs:
            self._configs[config_name] = {}
        
        config = self._configs[config_name]
        keys = key_path.split('.')
        
        # Navigate to the parent of the target key
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
    
    def save_config(self, config_name: str):
        """Save a specific configuration back to file.
        
        Args:
            config_name: Name of the configuration to save
        """
        if config_name not in self._configs:
            return
        
        filename = f"{config_name}.json"
        filepath = self.config_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self._configs[config_name], f, indent=2)
            print(f"✓ Saved {config_name} configuration to {filename}")
        except Exception as e:
            print(f"✗ Error saving {filename}: {e}")
    
    def reload_config(self, config_name: str):
        """Reload a specific configuration from file.
        
        Args:
            config_name: Name of the configuration to reload
        """
        config_files = {
            'game': 'game_config.json',
            'buildings': 'buildings.json',
            'enemies': 'enemies.json',
            'waves': 'waves.json',
            'research': 'research.json',
            'controls': 'controls.json'
        }
        
        if config_name not in config_files:
            print(f"✗ Unknown configuration: {config_name}")
            return
        
        filename = config_files[config_name]
        filepath = self.config_dir / filename
        
        try:
            with open(filepath, 'r') as f:
                self._configs[config_name] = json.load(f)
            print(f"✓ Reloaded {config_name} configuration from {filename}")
        except Exception as e:
            print(f"✗ Error reloading {filename}: {e}")
    
    # Convenience properties for easy access
    @property
    def game(self) -> Dict[str, Any]:
        """Get game configuration."""
        return self._configs.get('game', {})
    
    @property
    def buildings(self) -> Dict[str, Any]:
        """Get buildings configuration."""
        return self._configs.get('buildings', {})
    
    @property
    def enemies(self) -> Dict[str, Any]:
        """Get enemies configuration."""
        return self._configs.get('enemies', {})
    
    @property
    def waves(self) -> Dict[str, Any]:
        """Get waves configuration."""
        return self._configs.get('waves', {})
    
    @property
    def research(self) -> Dict[str, Any]:
        """Get research configuration."""
        return self._configs.get('research', {})
    
    @property
    def controls(self) -> Dict[str, Any]:
        """Get controls configuration."""
        return self._configs.get('controls', {})
    
    def get_building_config(self, building_type: str) -> Dict[str, Any]:
        """Get configuration for a specific building type.
        
        Args:
            building_type: Type of building (solar, turret, etc.)
            
        Returns:
            Building configuration dict
        """
        return self.get('buildings', f'building_types.{building_type}', {})
    
    def get_enemy_config(self, enemy_type: str) -> Dict[str, Any]:
        """Get configuration for a specific enemy type.
        
        Args:
            enemy_type: Type of enemy (basic, kamikaze, etc.)
            
        Returns:
            Enemy configuration dict
        """
        return self.get('enemies', f'enemy_types.{enemy_type}', {})
    
    def get_research_config(self, research_id: str) -> Dict[str, Any]:
        """Get configuration for a specific research.
        
        Args:
            research_id: ID of the research
            
        Returns:
            Research configuration dict
        """
        return self.get('research', f'research_tree.{research_id}', {})
    
    def validate_config(self) -> bool:
        """Validate all loaded configurations.
        
        Returns:
            True if all configurations are valid
        """
        valid = True
        
        # Validate required game settings
        required_game_keys = [
            'display.screen_width',
            'display.screen_height',
            'base.health',
            'resources.starting_minerals'
        ]
        
        for key in required_game_keys:
            if self.get('game', key) is None:
                print(f"✗ Missing required game config: {key}")
                valid = False
        
        # Validate building types have required fields
        building_types = self.get('buildings', 'building_types', {})
        required_building_fields = ['name', 'cost', 'base_health']
        
        for building_id, building_config in building_types.items():
            for field in required_building_fields:
                if field not in building_config:
                    print(f"✗ Building {building_id} missing required field: {field}")
                    valid = False
        
        # Validate enemy types have required fields
        enemy_types = self.get('enemies', 'enemy_types', {})
        required_enemy_fields = ['name', 'speed', 'points']
        
        for enemy_id, enemy_config in enemy_types.items():
            for field in required_enemy_fields:
                if field not in enemy_config:
                    print(f"✗ Enemy {enemy_id} missing required field: {field}")
                    valid = False
        
        if valid:
            print("✓ All configurations validated successfully")
        
        return valid


# Global configuration instance
config: Optional[GameConfig] = None


def initialize_config(config_dir: str = "config") -> GameConfig:
    """Initialize the global configuration.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        GameConfig instance
    """
    global config
    config = GameConfig(config_dir)
    return config


def get_config() -> GameConfig:
    """Get the global configuration instance.
    
    Returns:
        GameConfig instance
        
    Raises:
        RuntimeError: If configuration not initialized
    """
    if config is None:
        raise RuntimeError("Configuration not initialized. Call initialize_config() first.")
    return config


# Example usage functions
def load_settings_from_config():
    """Example function showing how to load settings from config files."""
    cfg = get_config()
    
    # Get display settings
    SCREEN_WIDTH = cfg.get('game', 'display.screen_width', 1600)
    SCREEN_HEIGHT = cfg.get('game', 'display.screen_height', 900)
    FPS = cfg.get('game', 'display.fps', 60)
    
    # Get building costs
    BUILD_COSTS = cfg.get('buildings', 'building_costs', {})
    
    # Get enemy base stats
    ENEMY_HEALTH_BASE = cfg.get('enemies', 'enemy_base_stats.health_base', 24)
    
    # Get wave settings
    WAVE_WAIT_TIME = cfg.get('waves', 'wave_timing.wait_time', 120)
    
    return {
        'SCREEN_WIDTH': SCREEN_WIDTH,
        'SCREEN_HEIGHT': SCREEN_HEIGHT,
        'FPS': FPS,
        'BUILD_COSTS': BUILD_COSTS,
        'ENEMY_HEALTH_BASE': ENEMY_HEALTH_BASE,
        'WAVE_WAIT_TIME': WAVE_WAIT_TIME
    }


if __name__ == "__main__":
    # Test the configuration system
    print("Testing configuration system...")
    
    # Initialize config
    cfg = initialize_config()
    
    # Validate configurations
    cfg.validate_config()
    
    # Test accessing values
    print(f"Screen width: {cfg.get('game', 'display.screen_width')}")
    print(f"Turret config: {cfg.get_building_config('turret')}")
    print(f"Basic enemy config: {cfg.get_enemy_config('basic')}")
    
    # Test loading settings
    settings = load_settings_from_config()
    print(f"Loaded settings: {settings}") 