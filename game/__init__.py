"""
Space Game - Arcade Implementation
A modern space defense game using Arcade with OpenGL shaders.
"""

__version__ = "3.0.0"
__author__ = "Space Game Team"

from .core.window import SpaceGameWindow
from .core.engine import ArcadeGameEngine

__all__ = [
    'SpaceGameWindow',
    'ArcadeGameEngine'
] 