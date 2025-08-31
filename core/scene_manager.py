"""
Scene management system
"""

from typing import Dict, Any, Optional
import os
import json


class Scene:
    """Represents a game scene/location"""

    def __init__(self, scene_id: str, data: Dict[str, Any]):
        self.id = scene_id
        self.name = data.get('name', scene_id)
        self.description = data.get('description', '')
        self.background = data.get('background', None)
        self.entities = data.get('entities', [])
        self.actions = data.get('actions', {})
        self.exits = data.get('exits', {})

    def update(self, context: Dict[str, Any]) -> None:
        """Update scene logic"""
        for entity in self.entities:
            entity.update(context)

    def render(self, renderer, context: Dict[str, Any]) -> None:
        """Render the scene"""
        # Render background
        if self.background:
            renderer.render_background(self.background)

        # Render entities
        for entity in self.entities:
            entity.render(renderer.surface, context)

    def handle_click(self, pos, context: Dict[str, Any]) -> bool:
        """Handle mouse click in scene"""
        for entity in self.entities:
            if entity.collides_with_point(pos) and entity.can_interact('click', context):
                # Handle entity interaction
                return True
        return False

    def get_entity(self, entity_id: str):
        """Get an entity by ID"""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None


class SceneManager:
    """Manages loading and switching between scenes"""

    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_data_path = "resources/scripts/scenes/"

    def load_scene(self, scene_id: str, context: Dict[str, Any]) -> bool:
        """Load a scene by ID"""
        if scene_id in self.scenes:
            self.current_scene = self.scenes[scene_id]
            context['current_scene'] = self.current_scene
            return True

        # Try to load from file
        scene_file = os.path.join(self.scene_data_path, f"{scene_id}.json")
        if os.path.exists(scene_file):
            with open(scene_file, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
                scene = Scene(scene_id, scene_data)
                self.scenes[scene_id] = scene
                self.current_scene = scene
                context['current_scene'] = self.current_scene
                return True

        print(f"Warning: Scene '{scene_id}' not found")
        return False

    def create_scene(self, scene_id: str, scene_data: Dict[str, Any]) -> Scene:
        """Create a new scene from data"""
        scene = Scene(scene_id, scene_data)
        self.scenes[scene_id] = scene
        return scene

    def get_current_scene(self) -> Optional[Scene]:
        """Get the currently active scene"""
        return self.current_scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Get a scene by ID"""
        return self.scenes.get(scene_id)

    def set_scene(self, scene: Scene, context: Optional[Dict[str, Any]] = None) -> None:
        """Set the current scene directly"""
        self.current_scene = scene
        if context is not None:
            context['current_scene'] = self.current_scene
