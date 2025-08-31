"""
Resource management system
"""

import pygame
import os
from typing import Dict, Any, Optional, Union
import json


class ResourceManager:
    """Manages game resources (images, sounds, fonts, etc.)"""

    def __init__(self, base_path: str = "resources"):
        self.base_path = base_path
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.data: Dict[str, Any] = {}

        # Create resource directories if they don't exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure resource directories exist"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, "images"),
            os.path.join(self.base_path, "sounds"),
            os.path.join(self.base_path, "fonts"),
            os.path.join(self.base_path, "data")
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def load_image(self, name: str, path: str) -> Optional[pygame.Surface]:
        """Load an image resource"""
        try:
            full_path = os.path.join(self.base_path, path)
            image = pygame.image.load(full_path).convert_alpha()
            self.images[name] = image
            return image
        except pygame.error as e:
            print(f"Error loading image {name}: {e}")
            return None

    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get a loaded image"""
        return self.images.get(name)

    def load_sound(self, name: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound resource"""
        try:
            full_path = os.path.join(self.base_path, path)
            sound = pygame.mixer.Sound(full_path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"Error loading sound {name}: {e}")
            return None

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a loaded sound"""
        return self.sounds.get(name)

    def play_sound(self, name: str) -> bool:
        """Play a sound effect"""
        sound = self.get_sound(name)
        if sound:
            sound.play()
            return True
        return False

    def load_font(self, name: str, path: str, size: int) -> Optional[pygame.font.Font]:
        """Load a font resource"""
        try:
            full_path = os.path.join(self.base_path, path)
            font = pygame.font.Font(full_path, size)
            self.fonts[name] = font
            return font
        except Exception as e:
            print(f"Error loading font {name}: {e}")
            return None

    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Get a loaded font"""
        return self.fonts.get(name)

    def load_data(self, name: str, path: str) -> Optional[Any]:
        """Load JSON data"""
        try:
            full_path = os.path.join(self.base_path, path)
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.data[name] = data
            return data
        except Exception as e:
            print(f"Error loading data {name}: {e}")
            return None

    def get_data(self, name: str) -> Optional[Any]:
        """Get loaded data"""
        return self.data.get(name)

    def save_data(self, name: str, path: str, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            full_path = os.path.join(self.base_path, path)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving data {name}: {e}")
            return False

    def create_default_resources(self) -> None:
        """Create default placeholder resources"""
        # Create placeholder images
        self._create_placeholder_image("door", (64, 128), (139, 69, 19))
        self._create_placeholder_image("key", (32, 32), (255, 215, 0))
        self._create_placeholder_image("table", (96, 64), (160, 82, 45))

        # Create default sounds (placeholder)
        # Note: Actual sound files would need to be provided

        # Create default fonts
        self._create_default_fonts()

    def _create_placeholder_image(self, name: str, size: tuple, color: tuple) -> None:
        """Create a placeholder image"""
        surface = pygame.Surface(size)
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        self.images[name] = surface

        # Save to file
        path = os.path.join(self.base_path, "images", f"{name}.png")
        try:
            pygame.image.save(surface, path)
        except:
            pass  # Ignore save errors for placeholders

    def _create_default_fonts(self) -> None:
        """Create default system fonts"""
        try:
            self.fonts['small'] = pygame.font.SysFont('Arial', 16)
            self.fonts['medium'] = pygame.font.SysFont('Arial', 20)
            self.fonts['large'] = pygame.font.SysFont('Arial', 24)
            self.fonts['bold'] = pygame.font.SysFont('Arial', 18, bold=True)
        except:
            pygame.font.init()
            self.fonts['small'] = pygame.font.Font(None, 16)
            self.fonts['medium'] = pygame.font.Font(None, 20)
            self.fonts['large'] = pygame.font.Font(None, 24)
            self.fonts['bold'] = pygame.font.Font(None, 18)

    def unload_all(self) -> None:
        """Unload all resources"""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.data.clear()

    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics"""
        return {
            'images': len(self.images),
            'sounds': len(self.sounds),
            'fonts': len(self.fonts),
            'data_files': len(self.data)
        }
