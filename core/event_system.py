"""
Event system for handling user input and game events
"""

import pygame
from typing import Dict, Any, Callable, List


class EventSystem:
    """Manages event handling and dispatching"""

    def __init__(self):
        self.handlers: Dict[int, List[Callable]] = {}

    def add_handler(self, event_type: int, handler: Callable) -> None:
        """Add an event handler for a specific event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def remove_handler(self, event_type: int, handler: Callable) -> None:
        """Remove an event handler"""
        if event_type in self.handlers:
            if handler in self.handlers[event_type]:
                self.handlers[event_type].remove(handler)

    def handle_event(self, event: pygame.event.Event, context: Dict[str, Any]) -> None:
        """Handle a single event"""
        event_type = event.type

        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event, context)
                except Exception as e:
                    print(f"Error in event handler: {e}")

    def clear_handlers(self, event_type: int = None) -> None:
        """Clear all handlers or handlers for a specific event type"""
        if event_type is None:
            self.handlers.clear()
        elif event_type in self.handlers:
            self.handlers[event_type].clear()

    def get_handler_count(self, event_type: int) -> int:
        """Get the number of handlers for an event type"""
        return len(self.handlers.get(event_type, []))
