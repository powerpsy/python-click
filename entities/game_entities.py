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

        if action == "Ouvrir":
            if self.state == "open":
                return False  # Already open
            if self.locked and game_context:
                # Check if player has the required key
                inventory_ids = [item.get('id') for item in game_context.get('inventory', [])]
                if self.key_required and self.key_required not in inventory_ids:
                    return False  # Missing key
            return not self.locked
        elif action == "Fermer":
            return self.state == "open"  # Can only close if open
        elif action in ["Regarder", "Pousser", "Tirer"]:
            return True

        return False

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
                 width: int = 32, height: int = 32):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height
        )

        self.state = "on_ground"
        self.properties.update({
            'state': self.state
        })

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the key can perform the given action"""
        if not self.interactive:
            return False

        if action == "Prendre":
            return self.state == "on_ground"  # Can only pick up if on ground
        elif action in ["Regarder", "Utiliser"]:
            return True

        return False

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

        return super().perform_action(action, game_context)

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

        if action in ["Regarder", "Pousser", "Tirer"]:
            return True

        return False

    def perform_action(self, action: str, game_context: Dict[str, Any]) -> Optional[str]:
        """Perform an action on the table"""
        if action == "Regarder":
            description_text = ""
            if self.items_on_top:
                # Try to get item names from the game context
                items_names = []
                objects = game_context.get('current_scene_obj', {}).get('objects', {})
                for item_id in self.items_on_top:
                    if item_id in objects:
                        items_names.append(objects[item_id].name)

                if items_names:
                    items_str = ", ".join(items_names)
                    description_text = f"Une {self.name} avec {items_str} dessus."
                else:
                    description_text = f"Une {self.name}."
            else:
                description_text = f"Une {self.name} vide."

            self._show_message_above(description_text, game_context)
            return None

        elif action == "Pousser":
            self._show_message_above("Vous poussez la table, mais elle ne bouge pas beaucoup.", game_context)
            return None

        elif action == "Tirer":
            self._show_message_above("Vous tirez la table, mais elle est trop lourde.", game_context)
            return None

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
