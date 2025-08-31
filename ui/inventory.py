"""
Inventory management system
"""

from typing import List, Dict, Any, Optional
import pygame


class InventoryItem:
    """Represents an item in the inventory"""

    def __init__(self, item_id: str, name: str, description: str,
                 icon_path: Optional[str] = None, quantity: int = 1):
        self.id = item_id
        self.name = name
        self.description = description
        self.icon_path = icon_path
        self.quantity = quantity
        self.icon = None

        # Load icon if provided
        if self.icon_path:
            self._load_icon()

    def _load_icon(self) -> None:
        """Load item icon"""
        try:
            self.icon = pygame.image.load(self.icon_path)
        except:
            self.icon = None

    def use(self) -> bool:
        """Use the item (returns True if item was consumed)"""
        if self.quantity > 0:
            self.quantity -= 1
            return self.quantity == 0
        return False

    def add_quantity(self, amount: int = 1) -> None:
        """Add quantity to the item"""
        self.quantity += amount

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_path': self.icon_path,
            'quantity': self.quantity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """Create item from dictionary"""
        return cls(
            item_id=data['id'],
            name=data['name'],
            description=data['description'],
            icon_path=data.get('icon_path'),
            quantity=data.get('quantity', 1)
        )


class Inventory:
    """Player inventory management"""

    def __init__(self, max_slots: int = 20):
        self.max_slots = max_slots
        self.items: List[InventoryItem] = []
        self.selected_item: Optional[InventoryItem] = None

    def add_item(self, item: InventoryItem) -> bool:
        """Add an item to inventory. Returns True if successful."""
        # Check if item already exists
        for existing_item in self.items:
            if existing_item.id == item.id:
                existing_item.add_quantity(item.quantity)
                return True

        # Check if inventory is full
        if len(self.items) >= self.max_slots:
            return False

        # Add new item
        self.items.append(item)
        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory. Returns True if successful."""
        for item in self.items:
            if item.id == item_id:
                if item.quantity >= quantity:
                    item.quantity -= quantity
                    if item.quantity == 0:
                        self.items.remove(item)
                    return True
                break
        return False

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains the specified item and quantity"""
        for item in self.items:
            if item.id == item_id and item.quantity >= quantity:
                return True
        return False

    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def select_item(self, item_id: str) -> bool:
        """Select an item for use. Returns True if successful."""
        item = self.get_item(item_id)
        if item:
            self.selected_item = item
            return True
        return False

    def deselect_item(self) -> None:
        """Deselect current item"""
        self.selected_item = None

    def use_selected_item(self) -> bool:
        """Use the currently selected item. Returns True if item was consumed."""
        if self.selected_item:
            consumed = self.selected_item.use()
            if consumed:
                self.items.remove(self.selected_item)
                self.selected_item = None
            return True
        return False

    def get_items_list(self) -> List[Dict[str, Any]]:
        """Get list of items for UI display"""
        return [item.to_dict() for item in self.items]

    def get_total_items(self) -> int:
        """Get total number of items in inventory"""
        return len(self.items)

    def is_full(self) -> bool:
        """Check if inventory is full"""
        return len(self.items) >= self.max_slots

    def clear(self) -> None:
        """Clear all items from inventory"""
        self.items.clear()
        self.selected_item = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for serialization"""
        return {
            'max_slots': self.max_slots,
            'items': [item.to_dict() for item in self.items],
            'selected_item_id': self.selected_item.id if self.selected_item else None
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load inventory from dictionary"""
        self.max_slots = data.get('max_slots', 20)
        self.items = [InventoryItem.from_dict(item_data) for item_data in data.get('items', [])]

        # Restore selected item
        selected_id = data.get('selected_item_id')
        if selected_id:
            self.select_item(selected_id)
