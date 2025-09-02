"""
Game Entities
Main game entities using the BaseEntity system
"""

from typing import Dict, Any, Optional, List
from entities.base_entity import BaseEntity
import pygame

# Import localization manager
try:
    from localization import LocalizationManager
except ImportError:
    # Fallback if localization is not available
    class LocalizationManager:
        def get_message(self, key):
            return key


class Door(BaseEntity):
    """Door entity for the game"""

    def __init__(self, entity_id: str, name: str, position: Optional[tuple] = None,
                 width: int = 64, height: int = 128, locked: bool = False,
                 key_required: Optional[str] = None, **kwargs):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height,
            **kwargs
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

        # Configure allowed actions for doors
        self.allowed_actions = {
            "open": self._action_ouvrir,
            "close": self._action_fermer,
            "look": self._action_regarder,
            "push": self._get_localized_message("door_resist_push"),
            "pull": self._get_localized_message("door_pull")
        }

        # Configure forbidden actions for doors
        self.forbidden_actions = {
            "talk": self._get_localized_message("cant_talk_door"),
            "eat": self._get_localized_message("cant_eat_door"),
            "Boire": "Ce n'est pas quelque chose que l'on peut boire.",
            "Embrasser": "Embrasser une porte ? Vraiment ?",
            "Sentir": "La porte sent le bois.",
            "Écouter": "Vous entendez peut-être du bruit de l'autre côté...",
            "Lécher": "Eurk ! Vous ne voulez vraiment pas faire ça.",
            "Casser": "Vous n'arrivez pas à casser cette porte solide."
        }

    def _get_localized_message(self, key: str) -> str:
        """Get localized message for the given key"""
        try:
            from localization import get_localization_manager
            loc = get_localization_manager()
            return loc.get_message(key)
        except:
            return key

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the door can perform the given action"""
        if not self.interactive:
            return False

        # Allow all actions to reach perform_action for proper handling
        return True

    def _action_ouvrir(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle opening the door"""
        if self.state == "open":
            self._show_message_above("La porte est déjà ouverte.", game_context)
            return None
            
        if self.locked:
            # Si la porte est verrouillée, impossible de l'ouvrir
            self._show_message_above("La porte est verrouillée. Il faut d'abord la déverrouiller.", game_context)
            return None
        
        # La porte n'est pas verrouillée, on peut l'ouvrir
        self.state = "open"
        self.properties['state'] = "open"
        self._show_message_above("La porte s'ouvre.", game_context)
        return None

    def _action_fermer(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle closing the door"""
        if self.state == "closed":
            self._show_message_above("La porte est déjà fermée.", game_context)
            return None
        self.state = "closed"
        self.properties['state'] = "closed"
        self._show_message_above("La porte se ferme.", game_context)
        return None

    def _action_regarder(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle examining the door"""
        description_text = ""
        if self.locked:
            description_text = "Une porte verrouillée."
        elif self.state == "open":
            description_text = "Une porte ouverte."
        else:
            description_text = "Une porte fermée."

        # Comportement différent selon si l'objet est dans l'inventaire ou dans la scène
        if hasattr(self, 'from_inventory') and self.from_inventory:
            # Objet dans l'inventaire : afficher la description au centre de l'écran
            if 'temp_descriptions' not in game_context:
                game_context['temp_descriptions'] = []
            
            game_context['temp_descriptions'].append({
                'text': description_text,
                'position': (400, 200),  # Position centrale
                'start_time': pygame.time.get_ticks(),
                'duration': 4000
            })
        else:
            # Objet dans la scène : afficher au-dessus de l'objet
            self._show_message_above(description_text, game_context)
        return None

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
                 width: int = 32, height: int = 32, description: str = "en laiton qui brille faiblement dans la lumière ambiante, avec des gravures complexes sur sa surface", **kwargs):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height,
            **kwargs  # Passer les propriétés supplémentaires comme visible
        )

        self.description = description
        self.state = "on_ground"
        self.properties.update({
            'state': self.state,
            'description': self.description
        })

        # Configure allowed actions for keys
        self.allowed_actions = {
            "take": self._action_prendre,
            "look": self._action_regarder,
            "use": "Vous essayez d'utiliser la clé, mais rien ne se passe."
        }

        # Configure forbidden actions for keys
        self.forbidden_actions = {
            "talk": "La clé reste silencieuse.",
            "eat": "Vous ne pouvez pas manger une clé !",
            "drink": "Ce n'est pas quelque chose que l'on peut boire.",
            "kiss": "Vous embrassez la clé. Ça ne change rien.",
            "smell": "La clé sent le métal.",
            "listen": "La clé ne fait aucun bruit.",
            "lick": "Le goût métallique n'est pas agréable.",
            "Casser": "La clé est trop solide pour être cassée.",
            "Ouvrir": "On ne peut pas ouvrir une clé.",
            "Fermer": "On ne peut pas fermer une clé.",
            "Pousser": "Pousser une clé ne sert à rien.",
            "Tirer": "Tirer une clé ne sert à rien."
        }

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the key can perform the given action"""
        if not self.interactive:
            return False

        # Allow all actions to reach perform_action for proper handling
        return True

    def _action_prendre(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle taking the key"""
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

    def _action_regarder(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle examining the key"""
        # Comportement différent selon si l'objet est dans l'inventaire ou dans la scène
        if hasattr(self, 'from_inventory') and self.from_inventory:
            # Objet dans l'inventaire : afficher la description au centre de l'écran
            description_text = f"Une {self.name} {self.description}."
            if 'temp_descriptions' not in game_context:
                game_context['temp_descriptions'] = []
            
            game_context['temp_descriptions'].append({
                'text': description_text,
                'position': (400, 200),  # Position centrale
                'start_time': pygame.time.get_ticks(),
                'duration': 4000
            })
        else:
            # Objet dans la scène : afficher au-dessus de l'objet
            description_text = f"Une {self.name} {self.description}."
            self._show_message_above(description_text, game_context)
        return None

    def use_with(self, other_entity, game_context: Dict[str, Any]) -> Optional[str]:
        """Use key with another entity"""
        # Import here to avoid circular import
        if hasattr(other_entity, '__class__') and other_entity.__class__.__name__ == 'Door':
            # Using key with door
            if other_entity.locked and other_entity.key_required == self.id:
                other_entity.locked = False
                other_entity.state = "closed"  # Déverrouillée mais fermée
                other_entity.properties['locked'] = False
                other_entity.properties['state'] = "closed"
                self._show_message_above("Vous déverrouillez la porte avec la clé. Elle est maintenant fermée mais déverrouillée.", game_context, 3000)
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
                 width: int = 96, height: int = 64, items_on_top: Optional[List[str]] = None,
                 items_underneath: Optional[List[str]] = None, **kwargs):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height,
            **kwargs  # Passer les propriétés supplémentaires comme has_been_moved
        )

        self.items_on_top = items_on_top or []
        self.items_underneath = items_underneath or []
        self.has_been_moved = kwargs.get('has_been_moved', False)  # Récupérer has_been_moved
        self.properties.update({
            'items_on_top': self.items_on_top,
            'items_underneath': self.items_underneath,
            'has_been_moved': self.has_been_moved
        })

        # Configure allowed actions for tables
        self.allowed_actions = {
            "look": self._action_regarder,
            "push": self._action_pousser,
            "pull": self._action_tirer
        }

        # Configure forbidden actions for tables
        self.forbidden_actions = {
            "talk": "La table ne vous répond pas.",
            "eat": "Vous ne pouvez pas manger une table !",
            "drink": "Ce n'est pas quelque chose que l'on peut boire.",
            "take": "La table est trop lourde pour être prise.",
            "kiss": "Vous embrassez la table. Bizarre...",
            "Sentir": "La table sent le bois vernis.",
            "Écouter": "La table est silencieuse.",
            "Lécher": "Le goût du vernis n'est pas terrible.",
            "Casser": "Vous n'arrivez pas à casser cette table solide.",
            "Ouvrir": "On ne peut pas ouvrir une table.",
            "Fermer": "On ne peut pas fermer une table.",
            "Utiliser": "Pour utiliser la table, posez quelque chose dessus."
        }

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the table can perform the given action"""
        if not self.interactive:
            return False

        # Allow all actions to reach perform_action for proper handling
        return True

    def _action_regarder(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle examining the table"""
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
            # Check if table has items underneath and hasn't been moved
            if self.items_underneath and not self.has_been_moved:
                description_text = "Une table bancale qui semble instable."
            else:
                description_text = "C'est une table."

        # Comportement différent selon si l'objet est dans l'inventaire ou dans la scène
        if hasattr(self, 'from_inventory') and self.from_inventory:
            # Objet dans l'inventaire : afficher la description au centre de l'écran
            if 'temp_descriptions' not in game_context:
                game_context['temp_descriptions'] = []
            
            game_context['temp_descriptions'].append({
                'text': description_text,
                'position': (400, 200),  # Position centrale
                'start_time': pygame.time.get_ticks(),
                'duration': 4000
            })
        else:
            # Objet dans la scène : afficher au-dessus de l'objet
            self._show_message_above(description_text, game_context)
        return None

    def _action_pousser(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle pushing the table"""
        return self._move_table(game_context, "Vous poussez la table.")

    def _action_tirer(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle pulling the table"""
        return self._move_table(game_context, "Vous tirez la table.")

    def _move_table(self, game_context: Dict[str, Any], action_message: str) -> Optional[str]:
        """Move the table and reveal hidden items"""
        if self.has_been_moved:
            self._show_message_above(f"{action_message} Elle ne bouge plus beaucoup.", game_context)
            return None

        if self.items_underneath:
            # Reveal hidden items
            objects = game_context.get('current_scene_obj', {}).get('objects', {})
            revealed_items = []
            
            for item_id in self.items_underneath:
                if item_id in objects:
                    objects[item_id].visible = True
                    revealed_items.append(objects[item_id].name)
            
            self.has_been_moved = True
            self.properties['has_been_moved'] = True
            
            if revealed_items:
                items_str = ", ".join(revealed_items)
                message = f"{action_message} En la déplaçant, vous découvrez {items_str} qui était caché dessous !"
                self._show_message_above(message, game_context, 4000)
            else:
                self._show_message_above(f"{action_message} Elle se déplace un peu.", game_context)
        else:
            self._show_message_above(f"{action_message} Elle ne bouge pas beaucoup.", game_context)
        
        return None

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


class Box(BaseEntity):
    """Box entity that can be opened/closed"""

    def __init__(self, entity_id: str, name: str, position: Optional[tuple] = None,
                 width: int = 48, height: int = 48, is_open: bool = False, 
                 contents: Optional[List[str]] = None):
        super().__init__(
            entity_id=entity_id,
            name=name,
            position=position,
            width=width,
            height=height
        )

        self.is_open = is_open
        self.contents = contents or []
        self.properties.update({
            'is_open': is_open,
            'contents': self.contents
        })

        # Configure allowed actions for boxes
        self.allowed_actions = {
            "open": self._action_ouvrir,
            "close": self._action_fermer,
            "look": self._action_regarder,
            "push": "La boîte glisse un peu.",
            "pull": "Vous tirez la boîte vers vous."
        }

        # Configure forbidden actions for boxes
        self.forbidden_actions = {
            "talk": "La boîte ne vous répond pas.",
            "Manger": "Vous ne pouvez pas manger une boîte !",
            "Boire": "Ce n'est pas quelque chose que l'on peut boire.",
            "Embrasser": "Vous embrassez la boîte. Étrange...",
            "Sentir": "La boîte sent le carton ou le bois.",
            "Écouter": "Vous entendez peut-être quelque chose bouger à l'intérieur...",
            "Lécher": "Vous ne voulez vraiment pas lécher ça.",
            "Casser": "Vous ne voulez pas casser la boîte et son contenu.",
            "Prendre": "La boîte est trop encombrante pour être prise.",
            "Utiliser": "Ouvrez la boîte pour voir ce qu'elle contient."
        }

    def can_interact(self, action: str, game_context: Dict[str, Any]) -> bool:
        """Check if the box can perform the given action"""
        if not self.interactive:
            return False
        return True

    def _action_ouvrir(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle opening the box"""
        if self.is_open:
            message = "La boîte est déjà ouverte."
        else:
            self.is_open = True
            self.properties['is_open'] = True
            if self.contents:
                contents_str = ", ".join(self.contents)
                message = f"Vous ouvrez la boîte. Elle contient : {contents_str}."
            else:
                message = "Vous ouvrez la boîte. Elle est vide."
        
        self._show_message_for_context(message, game_context)
        return None

    def _action_fermer(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle closing the box"""
        if not self.is_open:
            message = "La boîte est déjà fermée."
        else:
            self.is_open = False
            self.properties['is_open'] = False
            message = "Vous fermez la boîte."
        
        self._show_message_for_context(message, game_context)
        return None

    def _action_regarder(self, game_context: Dict[str, Any]) -> Optional[str]:
        """Handle examining the box"""
        if self.is_open:
            if self.contents:
                contents_str = ", ".join(self.contents)
                description_text = f"Une boîte ouverte contenant : {contents_str}."
            else:
                description_text = "Une boîte ouverte et vide."
        else:
            description_text = "Une boîte fermée."

        self._show_message_for_context(description_text, game_context)
        return None

    def _show_message_for_context(self, message: str, game_context: Dict[str, Any], duration: int = 3000):
        """Show message either above entity or in center based on context"""
        if hasattr(self, 'from_inventory') and self.from_inventory:
            # Objet dans l'inventaire : afficher au centre de l'écran
            if 'temp_descriptions' not in game_context:
                game_context['temp_descriptions'] = []
            
            game_context['temp_descriptions'].append({
                'text': message,
                'position': (400, 200),  # Position centrale
                'start_time': pygame.time.get_ticks(),
                'duration': duration
            })
        else:
            # Objet dans la scène : afficher au-dessus de l'objet
            self._show_message_above(message, game_context, duration)


# Factory function to create game entities
def create_entity(entity_type: str, entity_id: str, name: str, **kwargs) -> BaseEntity:
    """Factory function to create game entities"""
    if entity_type.lower() == "door":
        return Door(entity_id, name, **kwargs)
    elif entity_type.lower() == "key":
        return Key(entity_id, name, **kwargs)
    elif entity_type.lower() == "table":
        return Table(entity_id, name, **kwargs)
    elif entity_type.lower() == "box":
        return Box(entity_id, name, **kwargs)
    else:
        # Default to base entity
        return BaseEntity(entity_id, name, **kwargs)
