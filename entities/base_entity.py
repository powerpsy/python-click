"""
Base entity class for all game objects (entity size 90x58px)
"""

import pygame
import time
import random
from typing import Dict, Any, List, Optional, Tuple


class Component:
    """Base class for entity components"""

    def __init__(self, **properties):
        self.properties = properties

    def update(self, entity, game_context):
        """Update component logic"""
        pass

    def render(self, entity, surface, game_context):
        """Render component"""
        pass


class BaseEntity:
    """
    Base class for all game entities (objects, NPCs, etc.)
    Uses component-based architecture for flexibility
    """

    def __init__(self, entity_id: str, name: str, position: Optional[Tuple[int, int]] = None, **properties):
        self.id = entity_id
        self.name = name
        self.position = position or (0, 0)
        self.properties = properties

        # Component system
        self.components: Dict[str, Component] = {}

        # Entity state
        self.visible = properties.get('visible', True)
        self.interactive = properties.get('interactive', True)
        self.state = properties.get('state', 'default')

        # Action system - to be overridden in subclasses
        self.allowed_actions = {}  # Dict[str, callable] - action_name: method or message
        self.forbidden_actions = {}  # Dict[str, str] - action_name: denial_message

        # Visual properties
        width = properties.get('width', 50)
        height = properties.get('height', 50)
        self.sprite = None
        self.bounding_box = pygame.Rect(0, 0, width, height)  # Use provided size

        # Update bounding box if position is set
        if self.position:
            self.bounding_box.center = self.position

    def add_component(self, component: Component) -> None:
        """Add a component to this entity"""
        self.components[component.__class__.__name__] = component

    def get_component(self, component_type: type) -> Optional[Component]:
        """Get a component by type"""
        return self.components.get(component_type.__name__)

    def remove_component(self, component_type: type) -> None:
        """Remove a component by type"""
        if component_type.__name__ in self.components:
            del self.components[component_type.__name__]

    def has_component(self, component_type: type) -> bool:
        """Check if entity has a specific component"""
        return component_type.__name__ in self.components

    def update(self, game_context: Dict[str, Any]) -> None:
        """Update all components"""
        for component in self.components.values():
            component.update(self, game_context)

    def render(self, surface: pygame.Surface, game_context: Dict[str, Any]) -> None:
        """Render entity and all its components"""
        if not self.visible:
            return

        # Render sprite if available
        if self.sprite:
            surface.blit(self.sprite, self.position)

        # Render all components
        for component in self.components.values():
            component.render(self, surface, game_context)

    def on_click(self, action: Optional[str] = None, game_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Handle click interaction on this entity
        Returns a message string to display, or None
        """
        if game_context is None:
            game_context = {}

        # Check if entity can interact
        if not self.can_interact(action or 'click', game_context):
            return None

        # Perform the action
        return self.perform_action(action or 'click', game_context)

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if this entity can perform the given action"""
        # Default implementation - override in subclasses
        return self.interactive

    def perform_action(self, action: str, game_context: Dict[str, Any]) -> Optional[str]:
        """
        Perform an action on this entity
        Returns a message to display, or None to show message above entity
        """
        # Check if action is explicitly forbidden
        if action in self.forbidden_actions:
            self._show_message_above(self.forbidden_actions[action], game_context)
            return None
        
        # Check if action is explicitly allowed
        if action in self.allowed_actions:
            action_handler = self.allowed_actions[action]
            if callable(action_handler):
                # Call the method
                return action_handler(game_context)
            else:
                # Show the message
                self._show_message_above(str(action_handler), game_context)
                return None
        
        # Default implementation - show random message for unsupported actions
        random_messages = [
            "Cela n'a pas d'effet.",
            "Je ne vois pas ce que cela est censé faire.",
            "Je ne crois pas, non.",
            "Ça ne semble pas être une bonne idée.",
            "Je n'arrive pas à faire ça.",
            "Ce n'est pas possible.",
            "Rien ne se passe.",
            "Je ne pense pas que ce soit utile.",
            "Cela ne mène à rien.",
            "Je ne vois pas l'intérêt.",
            "Ça ne fonctionne pas comme ça.",
            "Je préfère ne pas essayer."
        ]
        
        message = random.choice(random_messages)
        self._show_message_above(message, game_context)
        return None

    def use_with(self, other_entity, game_context: Dict[str, Any]) -> Optional[str]:
        """
        Use this entity with another entity (for two-object actions)
        Returns a message to display, or None to show message above entity
        """
        # Default implementation for unsupported combinations
        random_messages = [
            f"Je ne vois pas comment utiliser {self.name} avec {other_entity.name}.",
            f"Ça ne fonctionne pas ensemble.",
            f"Ce n'est pas compatible.",
            f"Je ne pense pas que ce soit une bonne combinaison."
        ]
        
        message = random.choice(random_messages)
        self._show_message_above(message, game_context)
        return None

    def give_to(self, other_entity, game_context: Dict[str, Any]) -> Optional[str]:
        """
        Give this entity to another entity (for two-object actions)
        Returns a message to display, or None to show message above entity
        """
        # Default implementation for unsupported combinations
        random_messages = [
            f"Je ne peux pas donner {self.name} à {other_entity.name}.",
            f"{other_entity.name} ne semble pas intéressé.",
            f"Ce n'est pas nécessaire.",
            f"Ça ne sert à rien."
        ]
        
        message = random.choice(random_messages)
        self._show_message_above(message, game_context)
        return None

    def get_bounding_box(self) -> pygame.Rect:
        """Get the entity's bounding box for collision detection"""
        return self.bounding_box

    def collides_with_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point collides with this entity"""
        return self.bounding_box.collidepoint(point)

    def _show_message_above(self, message: str, game_context: Dict[str, Any], duration: int = 2000) -> None:
        """Helper method to show a message above the entity"""
        if 'temp_descriptions' not in game_context:
            game_context['temp_descriptions'] = []

        game_context['temp_descriptions'].append({
            'text': message,
            'position': self.position,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        })

    def __str__(self) -> str:
        return f"{self.id}: {self.name} at {self.position}"

    def __repr__(self) -> str:
        return f"BaseEntity(id='{self.id}', name='{self.name}', position={self.position})"
