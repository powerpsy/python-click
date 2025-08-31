"""
Rendering system for the game
"""

import pygame
from typing import Dict, Any, Tuple, Optional
import os


class Renderer:
    """Handles all rendering operations"""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.width, self.height = surface.get_size()

        # Font cache
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._load_fonts()

        # Asset cache
        self.images: Dict[str, pygame.Surface] = {}
        self.asset_path = "resources/assets/"

    def _load_fonts(self) -> None:
        """Load default fonts"""
        try:
            self.fonts['small'] = pygame.font.SysFont('Arial', 16)
            self.fonts['small_bold'] = pygame.font.SysFont('Arial', 16, bold=True)
            self.fonts['medium'] = pygame.font.SysFont('Arial', 20)
            self.fonts['large'] = pygame.font.SysFont('Arial', 24)
        except:
            # Fallback if system fonts fail
            pygame.font.init()
            self.fonts['small'] = pygame.font.Font(None, 16)
            self.fonts['medium'] = pygame.font.Font(None, 20)
            self.fonts['large'] = pygame.font.Font(None, 24)

    def render_background(self, background_name: str) -> None:
        """Render background image"""
        if background_name in self.images:
            bg = self.images[background_name]
        else:
            bg = self._load_image(background_name)
            if bg:
                self.images[background_name] = bg

        if bg:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(bg, (self.width, self.height))
            self.surface.blit(scaled_bg, (0, 0))

    def render_text(self, text: str, position: Tuple[int, int],
                   color: Tuple[int, int, int] = (255, 255, 255),
                   font_name: str = 'small',
                   center: bool = False) -> None:
        """Render text at position"""
        font = self.fonts.get(font_name, self.fonts['small'])

        text_surface = font.render(text, True, color)
        if center:
            rect = text_surface.get_rect(center=position)
            self.surface.blit(text_surface, rect)
        else:
            self.surface.blit(text_surface, position)

    def render_temp_descriptions(self, descriptions: list) -> None:
        """Render temporary descriptions above objects"""
        current_time = pygame.time.get_ticks()

        for desc in descriptions:
            if current_time - desc['start_time'] < desc['duration']:
                self._render_description(desc)

    def _render_description(self, desc: Dict[str, Any]) -> None:
        """Render a single description with background"""
        text = desc['text']
        position = desc['position']

        # Create text surface
        font = self.fonts.get('small', self.fonts['small'])
        text_surface = font.render(text, True, (255, 255, 255))

        # Create background rectangle
        bg_rect = pygame.Rect(
            position[0] - text_surface.get_width() // 2 - 5,
            position[1] - 60,
            text_surface.get_width() + 10,
            text_surface.get_height() + 6
        )

        # Draw background and border
        pygame.draw.rect(self.surface, (0, 0, 0), bg_rect)  # Black background
        pygame.draw.rect(self.surface, (255, 255, 255), bg_rect, 1)  # White border

        # Draw text
        text_pos = (position[0] - text_surface.get_width() // 2, position[1] - 55)
        self.surface.blit(text_surface, text_pos)

    def _load_image(self, image_name: str) -> Optional[pygame.Surface]:
        """Load an image from assets"""
        image_path = os.path.join(self.asset_path, image_name)
        if os.path.exists(image_path):
            try:
                return pygame.image.load(image_path).convert_alpha()
            except pygame.error:
                print(f"Error loading image: {image_path}")
        return None

    def draw_rect(self, rect: pygame.Rect, color: Tuple[int, int, int],
                 width: int = 0) -> None:
        """Draw a rectangle"""
        pygame.draw.rect(self.surface, color, rect, width)

    def fill_rect(self, rect: pygame.Rect, color: Tuple[int, int, int]) -> None:
        """Fill a rectangle"""
        pygame.draw.rect(self.surface, color, rect)

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen"""
        self.surface.fill(color)
