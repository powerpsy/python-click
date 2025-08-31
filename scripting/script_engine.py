"""
Script execution engine
"""

from typing import Dict, Any, Optional, List
import json
import os


class ScriptEngine:
    """Executes game scripts and handles scripted events"""

    def __init__(self):
        self.scripts: Dict[str, Dict[str, Any]] = {}
        self.script_path = "resources/scripts/"

    def load_script(self, script_name: str) -> bool:
        """Load a script file"""
        script_file = os.path.join(self.script_path, f"{script_name}.json")
        if os.path.exists(script_file):
            with open(script_file, 'r', encoding='utf-8') as f:
                self.scripts[script_name] = json.load(f)
            return True
        return False

    def execute_action(self, action_key: str, context: Dict[str, Any]) -> Optional[str]:
        """Execute a scripted action"""
        # Parse action key (format: "scene.entity.action" or "entity.action")
        parts = action_key.split('.')

        if len(parts) == 3:
            scene_id, entity_id, action = parts
        elif len(parts) == 2:
            entity_id, action = parts
            scene_id = context.get('current_scene', {}).get('id', 'default')
        else:
            return None

        # Find the script
        script = self._find_script_for_action(scene_id, entity_id, action)
        if not script:
            return None

        # Execute the action
        return self._execute_script_action(script, context)

    def _find_script_for_action(self, scene_id: str, entity_id: str, action: str) -> Optional[Dict[str, Any]]:
        """Find the script that contains the specified action"""
        for script_name, script_data in self.scripts.items():
            scenes = script_data.get('scenes', {})
            if scene_id in scenes:
                scene = scenes[scene_id]
                actions = scene.get('actions', {})
                action_key = f"{entity_id}.{action}"
                if action_key in actions:
                    return actions[action_key]
        return None

    def _execute_script_action(self, action_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """Execute a script action"""
        text_result = action_data.get('text', '')

        # Execute effects
        effects = action_data.get('effects', [])
        for effect in effects:
            self._execute_effect(effect, context)

        return text_result

    def _execute_effect(self, effect: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute a single effect"""
        effect_type = effect.get('type', '')
        params = effect.get('params', {})

        if effect_type == 'show_message':
            message = params.get('message', '')
            context['status'] = message

        elif effect_type == 'show_above_object':
            # This will be handled by the current object
            pass

        elif effect_type == 'add_to_inventory':
            item_id = params.get('object_id')
            item_name = params.get('name', item_id)
            if 'inventory' not in context:
                context['inventory'] = []
            context['inventory'].append({'id': item_id, 'name': item_name})

        elif effect_type == 'remove_from_inventory':
            item_id = params.get('object_id')
            if 'inventory' in context:
                context['inventory'] = [item for item in context['inventory'] if item['id'] != item_id]

        elif effect_type == 'change_scene':
            scene_id = params.get('scene_id')
            # This would trigger a scene change in the game

        elif effect_type == 'hide_object':
            obj_id = params.get('object_id')
            # This would hide an object in the current scene

        # Add more effect types as needed

    def evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition"""
        condition_type = condition.get('type', '')
        params = condition.get('params', {})

        if condition_type == 'has_item':
            item_id = params.get('item_id')
            inventory = context.get('inventory', [])
            return any(item['id'] == item_id for item in inventory)

        elif condition_type == 'scene_visited':
            scene_id = params.get('scene_id')
            visited_scenes = context.get('visited_scenes', [])
            return scene_id in visited_scenes

        # Add more condition types as needed

        return True  # Default to true if condition type not recognized
