"""
Main game interface
"""

import pygame
from typing import Dict, Any, Tuple, List


class GameInterface:
    """Main user interface controller"""

    def __init__(self):
        self.width = 800
        self.height = 600

        # UI Layout constants
        self.SCENE_RECT = pygame.Rect(0, 0, self.width, int(self.height * 3 / 4))
        self.BOTTOM_RECT = pygame.Rect(0, self.SCENE_RECT.height, self.width, self.height - self.SCENE_RECT.height)
        self.STATUS_HEIGHT = 28
        self.STATUS_RECT = pygame.Rect(0, self.BOTTOM_RECT.top, self.width, self.STATUS_HEIGHT)
        self.INTERACTIVE_BOTTOM = pygame.Rect(0, self.BOTTOM_RECT.top + self.STATUS_HEIGHT,
                                            self.width, self.BOTTOM_RECT.height - self.STATUS_HEIGHT)
        self.ACTION_AREA = pygame.Rect(0, self.INTERACTIVE_BOTTOM.top,
                                     int(self.width * 0.5), self.INTERACTIVE_BOTTOM.height)
        self.INV_AREA = pygame.Rect(int(self.width * 0.5), self.INTERACTIVE_BOTTOM.top,
                                   int(self.width * 0.5), self.INTERACTIVE_BOTTOM.height)

        # Action verbs (French)
        self.action_verbs = [
            'Donner', 'Ouvrir', 'Fermer',
            'Prendre', 'Regarder', 'Parler à',
            'Utiliser', 'Pousser', 'Tirer'
        ]

        # UI state
        self.show_inventory = False
        self.selected_action = None
        self.hovered_action = None

        # Fonts
        self.fonts = self._load_fonts()

    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Load UI fonts"""
        fonts = {}
        try:
            fonts['small'] = pygame.font.SysFont('Arial', 16)
            fonts['small_bold'] = pygame.font.SysFont('Arial', 16, bold=True)
            fonts['medium'] = pygame.font.SysFont('Arial', 20)
            fonts['large'] = pygame.font.SysFont('Arial', 24)
        except:
            pygame.font.init()
            fonts['small'] = pygame.font.Font(None, 16)
            fonts['medium'] = pygame.font.Font(None, 20)
            fonts['large'] = pygame.font.Font(None, 24)
        return fonts

    def update(self, context: Dict[str, Any]) -> None:
        """Update interface state"""
        # Update based on context
        pass

    def render(self, renderer, context: Dict[str, Any]) -> None:
        """Render the interface"""
        # Render status bar
        self._render_status_bar(renderer, context)

        # Render action bar
        self._render_action_bar(renderer, context)

        # Render inventory if visible
        if self.show_inventory:
            self._render_inventory(renderer, context)

        # Render temporary descriptions
        temp_descriptions = context.get('temp_descriptions', [])
        renderer.render_temp_descriptions(temp_descriptions)

    def _render_status_bar(self, renderer, context: Dict[str, Any]) -> None:
        """Render the status bar"""
        # Background
        renderer.fill_rect(self.STATUS_RECT, (20, 20, 20))

        # Status text
        status_text = context.get('status', '')
        if status_text:
            renderer.render_text(status_text, (10, self.STATUS_RECT.centery),
                               font_name='small', center=False)

        # Message text
        message = context.get('message', '')
        if message:
            renderer.render_text(message, (self.width - 10, self.STATUS_RECT.centery),
                               font_name='small', center=True)

    def _render_action_bar(self, renderer, context: Dict[str, Any]) -> None:
        """Render the action buttons"""
        # Background
        renderer.fill_rect(self.ACTION_AREA, (40, 40, 40))

        # Action buttons (3x3 grid)
        button_width = self.ACTION_AREA.width // 3
        button_height = self.ACTION_AREA.height // 3

        for i, action in enumerate(self.action_verbs):
            row = i // 3
            col = i % 3

            button_rect = pygame.Rect(
                self.ACTION_AREA.left + col * button_width,
                self.ACTION_AREA.top + row * button_height,
                button_width,
                button_height
            )

            # Button background
            color = (60, 60, 60)
            if self.hovered_action == action:
                color = (80, 80, 80)
            if self.selected_action == action:
                color = (100, 100, 100)

            renderer.fill_rect(button_rect, color)
            renderer.draw_rect(button_rect, (255, 255, 255), 1)

            # Button text
            text_color = (255, 255, 255)
            renderer.render_text(action, button_rect.center,
                               color=text_color, font_name='small', center=True)

    def _render_inventory(self, renderer, context: Dict[str, Any]) -> None:
        """Render the inventory panel"""
        # Background
        renderer.fill_rect(self.INV_AREA, (50, 50, 50))

        # Inventory title
        title_rect = pygame.Rect(self.INV_AREA.left, self.INV_AREA.top,
                               self.INV_AREA.width, 30)
        renderer.fill_rect(title_rect, (30, 30, 30))
        renderer.render_text("Inventaire", title_rect.center,
                           font_name='medium', center=True)

        # Inventory items
        inventory = context.get('inventory', [])
        item_height = 40
        for i, item in enumerate(inventory):
            item_rect = pygame.Rect(
                self.INV_AREA.left + 5,
                self.INV_AREA.top + 35 + i * item_height,
                self.INV_AREA.width - 10,
                item_height - 5
            )

            renderer.fill_rect(item_rect, (70, 70, 70))
            renderer.draw_rect(item_rect, (255, 255, 255), 1)

            renderer.render_text(item['name'], (item_rect.left + 10, item_rect.centery),
                               font_name='small', center=False)

    def handle_click(self, pos: Tuple[int, int], context: Dict[str, Any]) -> bool:
        """Handle mouse click on interface"""
        # Check action buttons
        if self._handle_action_click(pos, context):
            return True

        # Check inventory
        if self.show_inventory and self._handle_inventory_click(pos, context):
            return True

        return False

    def _handle_action_click(self, pos: Tuple[int, int], context: Dict[str, Any]) -> bool:
        """Handle click on action buttons"""
        button_width = self.ACTION_AREA.width // 3
        button_height = self.ACTION_AREA.height // 3

        for i, action in enumerate(self.action_verbs):
            row = i // 3
            col = i % 3

            button_rect = pygame.Rect(
                self.ACTION_AREA.left + col * button_width,
                self.ACTION_AREA.top + row * button_height,
                button_width,
                button_height
            )

            if button_rect.collidepoint(pos):
                self.selected_action = action
                context['selected_action'] = action
                context['message'] = ""
                return True

        return False

    def _handle_inventory_click(self, pos: Tuple[int, int], context: Dict[str, Any]) -> bool:
        """Handle click on inventory items"""
        inventory = context.get('inventory', [])
        item_height = 40

        for i, item in enumerate(inventory):
            item_rect = pygame.Rect(
                self.INV_AREA.left + 5,
                self.INV_AREA.top + 35 + i * item_height,
                self.INV_AREA.width - 10,
                item_height - 5
            )

            if item_rect.collidepoint(pos):
                # Handle inventory item click
                context['selected_item'] = item
                return True

        return False

    def toggle_inventory(self) -> None:
        """Toggle inventory visibility"""
        self.show_inventory = not self.show_inventory
