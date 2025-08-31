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
        """Render a single description with outlined text, wrapped to fit screen"""
        text = desc['text']
        position = desc['position']

        # Get font
        font = self.fonts.get('small', self.fonts['small'])
        
        # Define the graphics area boundaries (top 3/4 of screen)
        graphics_height = int(600 * 3 / 4)  # 450 pixels
        max_width = 400  # Half screen width for better readability
        margin = 10
        
        # Wrap text to fit within boundaries
        wrapped_lines = self._wrap_text(text, font, max_width)
        
        # Calculate total text height
        line_height = font.get_height() + 2  # Small spacing between lines
        total_height = len(wrapped_lines) * line_height
        
        # Find the widest line to determine block width
        max_line_width = max(font.size(line)[0] for line in wrapped_lines)
        
        # Calculate starting Y position (above the object, but stay in graphics area)
        start_y = position[1] - 60 - total_height
        if start_y < margin:  # Too high, move below object
            start_y = position[1] + 20
        if start_y + total_height > graphics_height - margin:  # Too low, clamp to graphics area
            start_y = graphics_height - total_height - margin
        
        # Calculate the center X position for the entire block (ideally centered on object)
        ideal_block_center_x = position[0]
        
        # Calculate the actual boundaries of the text block when centered
        block_left = ideal_block_center_x - max_line_width // 2
        block_right = ideal_block_center_x + max_line_width // 2
        
        # Adjust block position if it exceeds screen boundaries
        if block_left < margin:
            # Shift right to respect left margin
            block_center_x = margin + max_line_width // 2
        elif block_right > 800 - margin:
            # Shift left to respect right margin
            block_center_x = 800 - margin - max_line_width // 2
        else:
            # Use ideal position
            block_center_x = ideal_block_center_x
        
        # Render each line, centered within the adjusted block
        for i, line in enumerate(wrapped_lines):
            line_width = font.size(line)[0]
            # Center each line around the adjusted block center
            line_x = block_center_x - line_width // 2
            line_y = start_y + (i * line_height)
            self._render_outlined_text_no_clamp(line, (line_x, line_y), font, (255, 255, 255), (0, 0, 0))

    def _render_outlined_text_no_clamp(self, text: str, position: tuple, font: pygame.font.Font, 
                                      text_color: tuple, outline_color: tuple, outline_width: int = 2):
        """Render text with an outline effect without position clamping"""
        # Use position directly without clamping
        final_pos = position
        
        # Render outline by drawing text in multiple offset positions
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:  # Don't draw at center position yet
                    outline_surface = font.render(text, True, outline_color)
                    self.surface.blit(outline_surface, (final_pos[0] + dx, final_pos[1] + dy))
        
        # Render main text on top
        main_text_surface = font.render(text, True, text_color)
        self.surface.blit(main_text_surface, final_pos)

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list:
        """Wrap text to fit within specified width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed max width
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start a new one
                if current_line:  # Don't add empty lines
                    lines.append(' '.join(current_line))
                current_line = [word]
                
                # Check if single word is too long for one line
                if font.size(word)[0] > max_width:
                    # Split long word by characters
                    char_lines = self._split_long_word(word, font, max_width)
                    lines.extend(char_lines[:-1])  # Add all but last
                    current_line = [char_lines[-1]] if char_lines[-1] else []
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _split_long_word(self, word: str, font: pygame.font.Font, max_width: int) -> list:
        """Split a word that's too long to fit on one line"""
        lines = []
        current_chars = ""
        
        for char in word:
            test_chars = current_chars + char
            if font.size(test_chars)[0] <= max_width:
                current_chars = test_chars
            else:
                if current_chars:
                    lines.append(current_chars)
                current_chars = char
        
        if current_chars:
            lines.append(current_chars)
        
        return lines

    def _render_outlined_text(self, text: str, position: tuple, font: pygame.font.Font, 
                             text_color: tuple, outline_color: tuple, outline_width: int = 2, center: bool = False):
        """Render text with an outline effect"""
        # Create text surface for measuring
        text_surface = font.render(text, True, text_color)
        
        # Calculate final position if centering
        if center:
            final_pos = (position[0] - text_surface.get_width() // 2, position[1])
        else:
            final_pos = position
        
        # Clamp position to stay within screen bounds with 10px margins
        margin = 10
        final_pos = (
            max(margin, min(final_pos[0], 800 - text_surface.get_width() - margin)),
            max(margin, min(final_pos[1], 600 - text_surface.get_height() - margin))
        )
        
        # Render outline by drawing text in multiple offset positions
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:  # Don't draw at center position yet
                    outline_surface = font.render(text, True, outline_color)
                    self.surface.blit(outline_surface, (final_pos[0] + dx, final_pos[1] + dy))
        
        # Render main text on top
        main_text_surface = font.render(text, True, text_color)
        self.surface.blit(main_text_surface, final_pos)

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
