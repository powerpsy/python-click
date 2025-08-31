"""
Main Game class - Central game controller
"""

import pygame
import sys
from typing import Dict, Any, Optional
from .scene_manager import SceneManager
from .event_system import EventSystem
from .renderer import Renderer

# Import other modules using absolute imports to avoid relative import issues
try:
    from scripting.script_engine import ScriptEngine
except ImportError:
    ScriptEngine = None

try:
    from ui.interface import GameInterface
except ImportError:
    GameInterface = None


class Game:
    """
    Main game controller class
    Manages the game loop, scenes, events, and rendering
    """

    def __init__(self, renderer=None, event_system=None, scene_manager=None, interface=None, notification_system=None, width: int = 800, height: int = 600, title: str = "Python Click Adventure"):
        # Initialize Pygame if not already done
        if not pygame.get_init():
            pygame.init()

        # Game window
        self.width = width
        self.height = height
        self.title = title

        # Create window if renderer not provided
        if renderer is None:
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(title)
            self.renderer = Renderer(self.screen)
        else:
            self.screen = renderer.surface if hasattr(renderer, 'surface') else None
            self.renderer = renderer

        # Use provided systems or create new ones
        self.scene_manager = scene_manager or SceneManager()
        self.event_system = event_system or EventSystem()
        self.interface = interface
        self.notification_system = notification_system
        self.script_engine = ScriptEngine() if ScriptEngine else None

        # Game state
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Game context (shared state)
        self.context: Dict[str, Any] = {
            'game': self,
            'inventory': [],
            'current_scene': None,
            'temp_descriptions': [],
            'message': '',
            'selected_action': None,
        }

        # Initialize systems
        self._initialize_systems()

    def _initialize_systems(self) -> None:
        """Initialize all game systems"""
        # Load initial scene
        self.scene_manager.load_scene('hall', self.context)

        # Set up event handlers
        self.event_system.add_handler(pygame.QUIT, self._handle_quit)
        self.event_system.add_handler(pygame.MOUSEBUTTONDOWN, self._handle_mouse_click)
        self.event_system.add_handler(pygame.KEYDOWN, self._handle_key_press)

    def run(self) -> None:
        """Main game loop"""
        self.running = True

        while self.running:
            # Handle events
            self._handle_events()

            # Update game state
            self._update()

            # Render everything
            self._render()

            # Control frame rate
            self.clock.tick(self.fps)

        # Clean up
        self._cleanup()

    def _handle_events(self) -> None:
        """Process all pending events"""
        for event in pygame.event.get():
            self.event_system.handle_event(event, self.context)

    def _update(self) -> None:
        """Update game state"""
        # Update current scene
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.update(self.context)

        # Update interface
        if self.interface:
            self.interface.update(self.context)

        # Update temporary descriptions (auto-cleanup)
        self._update_temp_descriptions()

    def _render(self) -> None:
        """Render the game"""
        # Clear screen
        self.screen.fill((0, 0, 0))

        # Render current scene
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.render(self.renderer, self.context)

        # Render interface
        if self.interface:
            self.interface.render(self.renderer, self.context)

        # Update display
        pygame.display.flip()

    def _update_temp_descriptions(self) -> None:
        """Update and clean up temporary descriptions"""
        current_time = pygame.time.get_ticks()
        temp_descriptions = self.context.get('temp_descriptions', [])

        # Filter out expired descriptions
        active_descriptions = []
        for desc in temp_descriptions:
            if current_time - desc['start_time'] < desc['duration']:
                active_descriptions.append(desc)

        self.context['temp_descriptions'] = active_descriptions

    def _handle_quit(self, event: pygame.event.Event, context: Dict[str, Any]) -> None:
        """Handle quit event"""
        self.running = False

    def _handle_mouse_click(self, event: pygame.event.Event, context: Dict[str, Any]) -> None:
        """Handle mouse click events"""
        pos = event.pos

        # Check if click is on interface
        if self.interface and self.interface.handle_click(pos, context):
            return

        # Check if click is on scene objects
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.handle_click(pos, context)

    def _handle_key_press(self, event: pygame.event.Event, context: Dict[str, Any]) -> None:
        """Handle key press events"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_i:
            # Toggle inventory
            if self.interface:
                self.interface.toggle_inventory()

    def change_scene(self, scene_id: str) -> None:
        """Change to a different scene"""
        self.scene_manager.load_scene(scene_id, self.context)

    def show_message(self, message: str, duration: int = 2000) -> None:
        """Show a message to the player"""
        self.context['message'] = message
        # Auto-clear after duration
        pygame.time.set_timer(pygame.USEREVENT + 1, duration)

    def _cleanup(self) -> None:
        """Clean up resources"""
        pygame.quit()
        sys.exit()

    def get_context(self) -> Dict[str, Any]:
        """Get the current game context"""
        return self.context

    def set_context_value(self, key: str, value: Any) -> None:
        """Set a value in the game context"""
        self.context[key] = value

    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the game context"""
        return self.context.get(key, default)
