"""
Entities module - Game object definitions and management
"""

from .base_entity import BaseEntity
from .game_entities import Door, Key, Table, Box, create_entity

__all__ = [
    'BaseEntity',
    'Door',
    'Key',
    'Table',
    'Box',
    'create_entity'
]
