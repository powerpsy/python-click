"""
Core module - Main game engine components
"""

from .game import Game
from .scene_manager import SceneManager
from .event_system import EventSystem
from .renderer import Renderer

__all__ = ['Game', 'SceneManager', 'EventSystem', 'Renderer']
