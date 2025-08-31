"""
Game Entities
Main game entities using the BaseEntity system
"""

from typing import Dict, Any, Optional, List
from entities.base_entity import BaseEntity
import pygame


class Door(BaseEntity):
    """Door entity for the game"""

    def __init__(self, entity_id: str, name: str, position: Optional[tuple] = None,
                 width: int = 64, height: int = 128, locked: bool = False,
                 key_required: Optional[str] = None):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height
        )

        # Door-specific properties
        self.locked = locked
        self.key_required = key_required
        self.state = "closed" if locked else "open"

        # Update properties dict
        self.properties.update({
            'locked': locked,
            'key_required': key_required,
            'state': self.state
        })

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the door can perform the given action"""
        if not self.interactive:
            return False

        # Allow all actions to reach perform_action for proper handling
        return True

    def perform_action(self, action: str, game_context: Dict[str, Any]) -> Optional[str]:
        """Perform an action on the door"""
        if action == "Ouvrir":
            if self.state == "open":
                self._show_message_above("La porte est déjà ouverte.", game_context)
                return None
            if self.locked:
                # Check if player has the required key
                inventory_ids = [item.get('id') for item in game_context.get('inventory', [])]
                if self.key_required and self.key_required not in inventory_ids:
                    self._show_message_above("Il vous faut la bonne clé pour ouvrir cette porte.", game_context)
                    return None
                else:
                    self.locked = False
                    self.state = "open"
                    self.properties['locked'] = False
                    self.properties['state'] = "open"
                    self._show_message_above("Vous utilisez la clé pour ouvrir la porte.", game_context)
                    return None
            self.state = "open"
            self.properties['state'] = "open"
            self._show_message_above("La porte s'ouvre.", game_context)
            return None

        elif action == "Fermer":
            if self.state == "closed":
                self._show_message_above("La porte est déjà fermée.", game_context)
                return None
            self.state = "closed"
            self.properties['state'] = "closed"
            self._show_message_above("La porte se ferme.", game_context)
            return None

        elif action == "Regarder":
            description_text = ""
            if self.locked:
                description_text = "Une porte verrouillée."
            elif self.state == "open":
                description_text = "Une porte ouverte."
            else:
                description_text = "Une porte fermée."

            self._show_message_above(description_text, game_context)
            return None

        elif action == "Pousser":
            self._show_message_above("La porte résiste à votre poussée.", game_context)
            return None

        elif action == "Tirer":
            self._show_message_above("Vous tirez la porte.", game_context)
            return None

        # For all other actions, use random message from parent class
        return super().perform_action(action, game_context)

    def _show_message_above(self, message: str, game_context: Dict[str, Any], duration: int = 2000) -> None:
        """Helper method to show a message above the door"""
        if 'temp_descriptions' not in game_context:
            game_context['temp_descriptions'] = []

        game_context['temp_descriptions'].append({
            'text': message,
            'position': self.position,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        })


class Key(BaseEntity):
    """Key entity for the game"""

    def __init__(self, entity_id: str, name: str, position: Optional[tuple] = None,
                 width: int = 32, height: int = 32, description: str = "en laiton qui brille faiblement dans la lumière ambiante, avec des gravures complexes sur sa surface"):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height
        )

        self.description = description
        self.state = "on_ground"
        self.properties.update({
            'state': self.state,
            'description': self.description
        })

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the key can perform the given action"""
        if not self.interactive:
            return False

        # Allow all actions to reach perform_action for proper handling
        return True

    def perform_action(self, action: str, game_context: Dict[str, Any]) -> Optional[str]:
        """Perform an action on the key"""
        if action == "Prendre":
            if self.state != "on_ground":
                self._show_message_above("La clé n'est pas disponible à ramasser.", game_context)
                return None

            self.state = "in_inventory"
            self.properties['state'] = "in_inventory"
            self.visible = False

            # Add the key to the player's inventory
            if 'inventory' not in game_context:
                game_context['inventory'] = []
            game_context['inventory'].append({
                'id': self.id,
                'name': self.name
            })

            self._show_message_above("J'ai la clé en laiton, à voir quelle porte elle peut ouvrir...", game_context, 3000)
            return None

        elif action == "Regarder":
            description_text = f"Une {self.name} {self.description}."
            self._show_message_above(description_text, game_context)
            return None

        elif action == "Utiliser":
            self._show_message_above("Vous essayez d'utiliser la clé, mais rien ne se passe.", game_context)
            return None

        # For all other actions, use random message from parent class
        return super().perform_action(action, game_context)

    def use_with(self, other_entity, game_context: Dict[str, Any]) -> Optional[str]:
        """Use key with another entity"""
        # Import here to avoid circular import
        if hasattr(other_entity, '__class__') and other_entity.__class__.__name__ == 'Door':
            # Using key with door
            if other_entity.locked and other_entity.key_required == self.id:
                other_entity.locked = False
                other_entity.state = "open"
                other_entity.properties['locked'] = False
                other_entity.properties['state'] = "open"
                self._show_message_above("Vous utilisez la clé pour ouvrir la porte.", game_context)
                return None
            elif not other_entity.locked:
                self._show_message_above("La porte n'est pas verrouillée.", game_context)
                return None
            else:
                self._show_message_above("Cette clé ne va pas avec cette porte.", game_context)
                return None
        
        # Default behavior for other combinations
        return super().use_with(other_entity, game_context)

    def _show_message_above(self, message: str, game_context: Dict[str, Any], duration: int = 2000) -> None:
        """Helper method to show a message above the key"""
        if 'temp_descriptions' not in game_context:
            game_context['temp_descriptions'] = []

        game_context['temp_descriptions'].append({
            'text': message,
            'position': self.position,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        })


class Table(BaseEntity):
    """Table entity for the game"""

    def __init__(self, entity_id: str, name: str, position: Optional[tuple] = None,
                 width: int = 96, height: int = 64, items_on_top: Optional[List[str]] = None):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height
        )

        self.items_on_top = items_on_top or []
        self.properties.update({
            'items_on_top': self.items_on_top
        })

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the table can perform the given action"""
        if not self.interactive:
            return False

        # Allow all actions to reach perform_action for proper handling
        return True

    def perform_action(self, action: str, game_context: Dict[str, Any]) -> Optional[str]:
        """Perform an action on the table"""
        if action == "Regarder":
            description_text = ""
            visible_items = []
            
            if self.items_on_top:
                # Check which items are still visible on the scene
                objects = game_context.get('current_scene_obj', {}).get('objects', {})
                for item_id in self.items_on_top:
                    if item_id in objects and objects[item_id].visible:
                        visible_items.append(objects[item_id].name)

            if visible_items:
                items_str = ", ".join(visible_items)
                description_text = f"Une {self.name} avec {items_str} dessus."
            else:
                description_text = f"C'est une table."

            self._show_message_above(description_text, game_context)
            return None

        elif action == "Pousser":
            self._show_message_above("Vous poussez la table, mais elle ne bouge pas beaucoup.", game_context)
            return None

        elif action == "Tirer":
            self._show_message_above("Vous tirez la table, mais elle est trop lourde.", game_context)
            return None

        # For all other actions, use random message from parent class
        return super().perform_action(action, game_context)

    def _show_message_above(self, message: str, game_context: Dict[str, Any], duration: int = 2000) -> None:
        """Helper method to show a message above the table"""
        if 'temp_descriptions' not in game_context:
            game_context['temp_descriptions'] = []

        game_context['temp_descriptions'].append({
            'text': message,
            'position': self.position,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        })


# Factory function to create game entities
def create_entity(entity_type: str, entity_id: str, name: str, **kwargs) -> BaseEntity:
    """Factory function to create game entities"""
    if entity_type.lower() == "door":
        return Door(entity_id, name, **kwargs)
    elif entity_type.lower() == "key":
        return Key(entity_id, name, **kwargs)
    elif entity_type.lower() == "table":
        return Table(entity_id, name, **kwargs)
    else:
        # Default to base entity
        return BaseEntity(entity_id, name, **kwargs)
