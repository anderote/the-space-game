"""
Space Game Clone - Refactored Architecture
A modular real-time strategy defense game.
"""

__version__ = "2.0.0"
__author__ = "Space Game Team"

from .core.engine import GameEngine
from .core.state_manager import StateManager
from .systems.render_system import RenderSystem
from .systems.ui_system import UISystem

__all__ = [
    'GameEngine',
    'StateManager', 
    'RenderSystem',
    'UISystem'
] 