"""
Notification system for displaying temporary messages
"""

import pygame
from typing import List, Tuple, Dict, Any
import time


class Notification:
    """Represents a temporary notification message"""

    def __init__(self, text: str, position: Tuple[int, int], duration: float = 3.0,
                 color: Tuple[int, int, int] = (255, 255, 255)):
        self.text = text
        self.position = position
        self.duration = duration
        self.color = color
        self.start_time = time.time()
        self.alpha = 255

    def is_expired(self) -> bool:
        """Check if notification has expired"""
        return time.time() - self.start_time > self.duration

    def get_alpha(self) -> int:
        """Get current alpha value for fade effect"""
        elapsed = time.time() - self.start_time
        if elapsed > self.duration - 1.0:  # Start fading 1 second before expiry
            fade_progress = (elapsed - (self.duration - 1.0)) / 1.0
            self.alpha = int(255 * (1 - fade_progress))
        return max(0, self.alpha)

    def update_position(self, new_position: Tuple[int, int]) -> None:
        """Update notification position"""
        self.position = new_position


class NotificationSystem:
    """Manages temporary notifications and messages"""

    def __init__(self):
        self.notifications: List[Notification] = []
        self.font = None
        self._load_font()

    def _load_font(self) -> None:
        """Load notification font"""
        try:
            self.font = pygame.font.SysFont('Arial', 18, bold=True)
        except:
            pygame.font.init()
            self.font = pygame.font.Font(None, 18)

    def add_notification(self, text: str, position: Tuple[int, int],
                        duration: float = 3.0, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Add a new notification"""
        notification = Notification(text, position, duration, color)
        self.notifications.append(notification)

    def add_action_message(self, text: str, object_position: Tuple[int, int],
                          color: Tuple[int, int, int] = (255, 255, 0)) -> None:
        """Add an action message above an object"""
        # Position message above the object
        message_x = object_position[0]
        message_y = object_position[1] - 50  # 50 pixels above object

        self.add_notification(text, (message_x, message_y), duration=2.0, color=color)

    def add_status_message(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Add a status message (for compatibility)"""
        # Status messages are now handled by the interface
        pass

    def update(self, delta_time: float) -> None:
        """Update all notifications"""
        # Remove expired notifications
        self.notifications = [n for n in self.notifications if not n.is_expired()]

        # Update notification positions if needed
        # (Could be used for following moving objects)

    def render(self, renderer) -> None:
        """Render all active notifications"""
        for notification in self.notifications:
            alpha = notification.get_alpha()
            if alpha > 0:
                # Create semi-transparent surface for fade effect
                text_surface = self.font.render(notification.text, True, notification.color)
                text_surface.set_alpha(alpha)

                # Center the text
                text_rect = text_surface.get_rect(center=notification.position)

                # Render with background for better visibility
                bg_padding = 4
                bg_rect = pygame.Rect(
                    text_rect.left - bg_padding,
                    text_rect.top - bg_padding,
                    text_rect.width + bg_padding * 2,
                    text_rect.height + bg_padding * 2
                )

                # Semi-transparent background
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
                bg_surface.set_alpha(128)
                bg_surface.fill((0, 0, 0))

                renderer.surface.blit(bg_surface, bg_rect)
                renderer.surface.blit(text_surface, text_rect)

    def clear_all(self) -> None:
        """Clear all notifications"""
        self.notifications.clear()

    def get_active_count(self) -> int:
        """Get number of active notifications"""
        return len(self.notifications)
