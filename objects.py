"""
Game Objects Module
Contains object definitions and state management for the point-and-click game.
"""

class GameObject:
    """Base class for all game objects."""

    def __init__(self, obj_id, name, description="", position=None, state="default"):
        self.id = obj_id  # Hexadecimal ID like x0001
        self.name = name
        self.description = description
        self.position = position  # (x, y) coordinates in scene
        self.state = state  # Current state of the object
        self.visible = True
        self.interactive = True

    def __str__(self):
        return f"{self.id}: {self.name} ({self.state})"

    def can_interact(self, action, game_state=None):
        """Check if a specific action can be performed on this object."""
        return self.interactive

    def perform_action(self, action, game_state):
        """Perform an action on this object. Returns a message."""
        return f"Rien ne se passe avec {self.name}."


class Door(GameObject):
    """Door object that can be opened, closed, locked, etc."""

    def __init__(self, obj_id, name, description="", position=None, locked=False):
        super().__init__(obj_id, name, description, position, "closed")
        self.locked = locked
        self.key_required = None  # ID of key required to unlock

    def can_interact(self, action, game_state=None):
        if not self.interactive:
            return False

        if action == "Open":
            if self.state == "open":
                return False  # Already open
            if self.locked and game_state:
                # Check if player has the required key
                inventory_ids = [item['id'] for item in game_state.get('inventory', [])]
                if self.key_required and self.key_required not in inventory_ids:
                    return False  # Missing key
            return not self.locked
        elif action == "Close":
            return self.state == "open"  # Can only close if open
        elif action == "Lock":
            return self.state == "closed" and not self.locked  # Can only lock if closed and unlocked
        elif action == "Unlock":
            if not self.locked:
                return False  # Already unlocked
            if game_state:
                # Check if player has the required key
                inventory_ids = [item['id'] for item in game_state.get('inventory', [])]
                if self.key_required and self.key_required not in inventory_ids:
                    return False  # Missing key
            return True
        elif action in ["Look at", "Push", "Pull"]:
            return True

        return False

    def perform_action(self, action, game_state):
        if action == "Open":
            if self.state == "open":
                return f"La {self.name} est déjà ouverte."
            if self.locked:
                # Check if player has the required key
                inventory_ids = [item['id'] for item in game_state.get('inventory', [])]
                if self.key_required and self.key_required not in inventory_ids:
                    return f"Il vous faut la bonne clé pour ouvrir cette {self.name}."
                else:
                    self.locked = False
                    self.state = "open"
                    return f"Vous utilisez la clé pour ouvrir la {self.name}."
            self.state = "open"
            return f"La {self.name} s'ouvre."
        elif action == "Close":
            if self.state == "closed":
                return f"La {self.name} est déjà fermée."
            self.state = "closed"
            return f"La {self.name} se ferme."
        elif action == "Lock":
            if self.state == "open":
                return f"Vous ne pouvez pas verrouiller une {self.name} ouverte."
            if self.locked:
                return f"La {self.name} est déjà verrouillée."
            self.locked = True
            return f"La {self.name} est verrouillée."
        elif action == "Unlock":
            if not self.locked:
                return f"La {self.name} n'est pas verrouillée."
            # Check if player has the required key
            inventory_ids = [item['id'] for item in game_state.get('inventory', [])]
            if self.key_required and self.key_required not in inventory_ids:
                return f"Il vous faut la bonne clé pour déverrouiller cette {self.name}."
            self.locked = False
            return f"La {self.name} est déverrouillée."
        elif action == "Look at":
            if self.locked:
                return f"Une {self.name} verrouillée."
            elif self.state == "open":
                return f"Une {self.name} ouverte."
            else:
                return f"Une {self.name} fermée."

        return super().perform_action(action, game_state)


class Key(GameObject):
    """Key object that can be picked up and used."""

    def __init__(self, obj_id, name, description="", position=None):
        super().__init__(obj_id, name, description, position, "on_ground")

    def can_interact(self, action, game_state=None):
        if not self.interactive:
            return False

        if action == "Pick up":
            return self.state == "on_ground"  # Can only pick up if on ground
        elif action == "Look at":
            return True
        elif action == "Use":
            return True  # Can always try to use, even if it doesn't work

        return False

    def perform_action(self, action, game_state):
        if action == "Pick up":
            if self.state != "on_ground":
                return f"La {self.name} n'est pas disponible à ramasser."
            self.state = "in_inventory"
            self.visible = False
            # Add the object to the player's inventory
            if 'inventory' not in game_state:
                game_state['inventory'] = []
            game_state['inventory'].append({'id': self.id, 'name': self.name})
            return f"Vous ramassez la {self.name}."
        elif action == "Look at":
            if self.state == "on_ground":
                return f"Une {self.name} {self.description} posée par terre."
            elif self.state == "in_inventory":
                return f"Une {self.name} {self.description} dans votre inventaire."
            else:
                return f"Une {self.name} {self.description}."
        elif action == "Use":
            return f"Vous essayez d'utiliser la {self.name}, mais rien ne se passe."

        return super().perform_action(action, game_state)


class Table(GameObject):
    """Table object that can hold other objects."""

    def __init__(self, obj_id, name, description="", position=None):
        super().__init__(obj_id, name, description, position, "normal")
        self.items_on_top = []  # List of object IDs on the table

    def can_interact(self, action, game_state=None):
        if not self.interactive:
            return False

        if action in ["Look at", "Push", "Pull"]:
            return True

        return False

    def perform_action(self, action, game_state):
        if action == "Look at":
            if self.items_on_top:
                items_names = []
                for item_id in self.items_on_top:
                    if item_id in game_state.get('objects', {}):
                        items_names.append(game_state['objects'][item_id].name)
                if items_names:
                    items_str = ", ".join(items_names)
                    return f"Une {self.name} avec {items_str} dessus."
            return f"Une {self.name} vide."
        elif action == "Push":
            return f"Vous poussez la {self.name}, mais elle ne bouge pas beaucoup."
        elif action == "Pull":
            return f"Vous tirez la {self.name}, mais elle est trop lourde."

        return super().perform_action(action, game_state)


# Object registry - maps object IDs to their instances
OBJECT_REGISTRY = {}

def create_object(obj_type, obj_id, name, **kwargs):
    """Factory function to create objects of different types."""
    if obj_type == "door":
        obj = Door(obj_id, name, **kwargs)
    elif obj_type == "key":
        obj = Key(obj_id, name, **kwargs)
    elif obj_type == "table":
        obj = Table(obj_id, name, **kwargs)
    else:
        obj = GameObject(obj_id, name, **kwargs)

    OBJECT_REGISTRY[obj_id] = obj
    return obj

def get_object(obj_id):
    """Get an object by its ID."""
    return OBJECT_REGISTRY.get(obj_id)

def get_all_objects():
    """Get all registered objects."""
    return OBJECT_REGISTRY

def reset_objects():
    """Reset all objects to their initial state."""
    for obj in OBJECT_REGISTRY.values():
        # Reset basic properties - more complex reset logic can be added per object type
        obj.visible = True
        obj.interactive = True
        if hasattr(obj, 'state'):
            obj.state = getattr(obj, 'initial_state', 'default')
