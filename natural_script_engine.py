"""
Natural Script Engine
Moteur pour interpréter les scripts naturels de jeu d'aventure
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from entities import Door, Key, Table, BaseEntity


@dataclass
class GameAction:
    """Représente une action possible dans le jeu"""
    verb: str
    target: str
    target2: Optional[str] = None  # Pour les actions à deux objets
    message: str = ""
    requires: List[str] = None  # Conditions pour que l'action soit possible
    effects: List[str] = None   # Effets de l'action
    
    def __post_init__(self):
        if self.requires is None:
            self.requires = []
        if self.effects is None:
            self.effects = []


@dataclass
class GameObject:
    """Représente un objet du jeu défini dans le script"""
    id: str
    name: str
    position: Tuple[int, int]
    properties: Dict[str, Any]
    entity_type: str = "generic"


class NaturalScriptEngine:
    """Moteur pour interpréter les scripts naturels"""
    
    def __init__(self, game_context):
        self.game_context = game_context
        self.objects: Dict[str, GameObject] = {}
        self.actions: List[GameAction] = []
        self.forbidden_actions: Dict[str, str] = {}
        self.game_state: Dict[str, Any] = {}
        self.scene_name = ""
        
    def parse_script(self, script_path: str):
        """Parse le script naturel"""
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # NE PAS strip() les lignes pour préserver l'indentation
        lines = [line.rstrip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()  # Strip seulement pour le test
            
            if line.startswith('SCENE'):
                i = self._parse_scene(lines, i)
            elif line.startswith('ACTION'):
                i = self._parse_action(lines, i)
            elif line.startswith('FORBIDDEN'):
                i = self._parse_forbidden(lines, i)
            else:
                i += 1
        
        return self._create_entities()
    
    def _parse_scene(self, lines: List[str], start_idx: int) -> int:
        """Parse la définition de scène"""
        line = lines[start_idx].strip()  # Strip pour le matching
        match = re.match(r'SCENE (\w+) "([^"]+)"', line)
        if match:
            scene_id, scene_name = match.groups()
            self.scene_name = scene_name
        
        i = start_idx + 1
        while i < len(lines) and lines[i].strip().startswith('OBJECT'):  # Vérifier que la ligne strippée commence par OBJECT
            i = self._parse_object(lines, i)
        
        return i
    
    def _parse_object(self, lines: List[str], start_idx: int) -> int:
        """Parse la définition d'un objet"""
        line = lines[start_idx]
        # OBJECT key "Petite clé en laiton" at (300, 370) [hidden]
        match = re.match(r'OBJECT (\w+) "([^"]+)" at \((\d+), (\d+)\)(?:\s*\[([^\]]+)\])?', line.strip())
        
        if match:
            obj_id, name, x, y, props_str = match.groups()
            position = (int(x), int(y))
            
            # Parse les propriétés
            properties = {}
            entity_type = "generic"
            
            if props_str:
                props = [p.strip() for p in props_str.split(',')]
                for prop in props:
                    if '=' in prop:
                        key, value = prop.split('=', 1)
                        properties[key.strip()] = value.strip()
                    else:
                        properties[prop] = True
            
            # Déterminer le type d'entité
            if 'door' in obj_id.lower() or 'porte' in name.lower():
                entity_type = "door"
            elif 'key' in obj_id.lower() or 'clé' in name.lower():
                entity_type = "key"
            elif 'table' in obj_id.lower():
                entity_type = "table"
            self.objects[obj_id] = GameObject(obj_id, name, position, properties, entity_type)
        
        return start_idx + 1
    
    def _parse_action(self, lines: List[str], start_idx: int) -> int:
        """Parse une action"""
        line = lines[start_idx].strip()  # Strip pour le matching
        # ACTION regarder table -> "Une table bancale qui semble instable."
        match = re.match(r'ACTION (\w+) (\w+)(?:\s+(\w+))?\s*->\s*"([^"]+)"', line)
        
        if match:
            verb, target1, target2, message = match.groups()
            action = GameAction(verb, target1, target2, message)
            
            # Parse les prérequis et effets
            i = start_idx + 1
            while i < len(lines) and lines[i].startswith('  '):  # Maintenant les lignes gardent l'indentation
                subline = lines[i].strip()
                if subline.startswith('REQUIRES:'):
                    req = subline[9:].strip()
                    action.requires.append(req)
                elif subline.startswith('EFFECTS:'):
                    pass  # Ignorer la ligne d'en-tête
                elif subline.startswith('- '):
                    effect = subline[2:].strip()
                    action.effects.append(effect)
                i += 1
            
            self.actions.append(action)
            return i
        
        return start_idx + 1
    
    def _parse_forbidden(self, lines: List[str], start_idx: int) -> int:
        """Parse une action interdite"""
        line = lines[start_idx]
        # FORBIDDEN parler door -> "Vous ne pouvez pas parler à une porte."
        match = re.match(r'FORBIDDEN (\w+) (\w+)\s*->\s*"([^"]+)"', line)
        
        if match:
            verb, target, message = match.groups()
            key = f"{verb}_{target}"
            self.forbidden_actions[key] = message
        
        return start_idx + 1
    
    def _create_entities(self) -> Dict[str, Any]:
        """Crée les entités à partir des objets parsés"""
        scene_data = {
            'id': 'hall',
            'name': self.scene_name,
            'entities': []
        }
        
        for obj_id, obj in self.objects.items():
            entity_data = {
                'id': obj_id,
                'name': obj.name,
                'type': obj.entity_type,
                'position': obj.position,
                'properties': self._convert_properties(obj.properties)
            }
            scene_data['entities'].append(entity_data)
        
        return {'hall': scene_data}
    
    def _convert_properties(self, props: Dict[str, Any]) -> Dict[str, Any]:
        """Convertit les propriétés du script en propriétés d'entité"""
        converted = {'visible': True}  # Par défaut, les objets sont visibles
        
        for key, value in props.items():
            if key == 'locked':
                converted['locked'] = True
            elif key == 'hidden':
                converted['visible'] = False  # Explicitement caché
            elif key == 'hiding':
                converted['items_underneath'] = [value]
            elif key == 'key_required':
                converted['key_required'] = value
            else:
                converted[key] = value
        
        return converted
    
    def check_action_requirements(self, action: GameAction) -> bool:
        """Vérifie si les prérequis d'une action sont remplis"""
        for req in action.requires:
            if not self._evaluate_condition(req):
                return False
        return True
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Évalue une condition (ex: "table.moved = true", "key IN inventory")"""
        condition = condition.strip()
        
        if ' IN inventory' in condition:
            obj_id = condition.replace(' IN inventory', '')
            inventory = self.game_context.get('inventory', [])
            return any(item.get('id') == obj_id for item in inventory)
        
        if '=' in condition:
            left, right = condition.split('=', 1)
            obj_prop, prop_name = left.strip().split('.')
            expected_value = right.strip()
            
            # Convertir la valeur attendue
            if expected_value.lower() == 'true':
                expected_value = True
            elif expected_value.lower() == 'false':
                expected_value = False
            
            # Vérifier la propriété de l'objet
            current_scene = self.game_context.get('current_scene')
            if current_scene:
                for entity in current_scene.entities:
                    if entity.id == obj_prop:
                        actual_value = getattr(entity, prop_name, None)
                        return actual_value == expected_value
        
        return False
    
    def execute_action_effects(self, action: GameAction):
        """Exécute les effets d'une action"""
        for effect in action.effects:
            self._execute_effect(effect)
    
    def _execute_effect(self, effect: str):
        """Exécute un effet spécifique"""
        effect = effect.strip()
        
        if effect.startswith('SHOW '):
            obj_id = effect[5:].strip()
            self._set_object_visible(obj_id, True)
        elif effect.startswith('HIDE '):
            obj_id = effect[5:].strip()
            self._set_object_visible(obj_id, False)
        elif effect.startswith('ADD_TO_INVENTORY '):
            obj_id = effect[17:].strip()
            self._add_to_inventory(obj_id)
        elif effect.startswith('SET '):
            # SET door.locked false OU SET table.description "Une table"
            effect_content = effect[4:].strip()  # Enlever "SET "
            
            # Trouver la première espace pour séparer la propriété de la valeur
            first_space = effect_content.find(' ')
            if first_space > 0:
                obj_prop = effect_content[:first_space]
                value = effect_content[first_space+1:].strip()
                obj_id, prop_name = obj_prop.split('.')
                self._set_object_property(obj_id, prop_name, value)
        elif effect == 'WIN_GAME':
            print("🎉 Félicitations ! Vous avez terminé le jeu !")
    
    def _set_object_visible(self, obj_id: str, visible: bool):
        """Change la visibilité d'un objet"""
        current_scene = self.game_context.get('current_scene')
        if current_scene:
            for entity in current_scene.entities:
                if entity.id == obj_id:
                    entity.visible = visible
                    break
    
    def _add_to_inventory(self, obj_id: str):
        """Ajoute un objet à l'inventaire"""
        current_scene = self.game_context.get('current_scene')
        if current_scene:
            for entity in current_scene.entities:
                if entity.id == obj_id:
                    if 'inventory' not in self.game_context:
                        self.game_context['inventory'] = []
                    self.game_context['inventory'].append({
                        'id': entity.id,
                        'name': entity.name
                    })
                    entity.visible = False
                    break
    
    def _set_object_property(self, obj_id: str, prop_name: str, value: str):
        """Modifie une propriété d'un objet"""
        # Convertir la valeur
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]  # Enlever les guillemets
        
        current_scene = self.game_context.get('current_scene')
        if current_scene:
            for entity in current_scene.entities:
                if entity.id == obj_id:
                    setattr(entity, prop_name, value)
                    if hasattr(entity, 'properties'):
                        entity.properties[prop_name] = value
                    break
    
    def find_action(self, verb: str, target1: str, target2: Optional[str] = None) -> Optional[GameAction]:
        """Trouve une action correspondante"""
        for action in self.actions:
            if (action.verb == verb and action.target == target1 and 
                action.target2 == target2):
                return action
        return None
    
    def get_forbidden_message(self, verb: str, target: str) -> Optional[str]:
        """Récupère le message d'une action interdite"""
        key = f"{verb}_{target}"
        return self.forbidden_actions.get(key)
    
    def get_forbidden_message_for_failed_requirements(self, verb: str, target: str) -> Optional[str]:
        """Récupère un message spécifique pour une action avec prérequis non remplis"""
        # Pour ouvrir la porte, si elle est verrouillée, donner un message spécifique
        if verb == "ouvrir" and target == "door":
            current_scene = self.game_context.get('current_scene')
            if current_scene:
                for entity in current_scene.entities:
                    if entity.id == target and hasattr(entity, 'locked') and entity.locked:
                        return "La porte est verrouillée. Il faut d'abord la déverrouiller."
        return None
