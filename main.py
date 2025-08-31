"""
Point & Click Game - Architecture Modulaire
Jeu d'aventure pointer-cliquer utilisant BaseEntity
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from typing import Dict, Any
from core import Game, SceneManager, EventSystem, Renderer
from scenes import Scene
from ui import GameInterface, NotificationSystem, Inventory
from utils.logger import get_logger


class PointClickGame(Game):

    def __init__(self, width: int = 800, height: int = 600, title: str = "Point & Click Game"):
        # Initialiser Pygame si pas déjà fait
        if not pygame.get_init():
            pygame.init()

        # Configuration de la fenêtre
        self.width = width
        self.height = height
        self.title = title

        # Créer la fenêtre
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # Systèmes de jeu
        self.renderer = Renderer(self.screen)
        self.event_system = EventSystem()
        self.scene_manager = SceneManager()
        self.interface = GameInterface()
        self.notification_system = NotificationSystem()

        # Systèmes optionnels
        self.script_engine = None
        self.inventory = Inventory()
        self.resources = None  # Pour extension future

        # État du jeu
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.show_debug_ids = False  # Affichage des codes d'objets (F1)

        # Contexte partagé
        self.context: Dict[str, Any] = {
            'game': self,
            'inventory': [],
            'current_scene': None,
            'temp_descriptions': [],
            'message': '',
            'selected_action': None,
            'show_debug_ids': False,
        }

        # Initialiser les systèmes
        self._initialize_systems()

    def _initialize_systems(self):
        """Initialiser tous les systèmes"""
        # Charger la scène par défaut
        self.load_scenes_from_script()

        # Configurer les gestionnaires d'événements
        self.event_system.add_handler(pygame.QUIT, self._handle_quit)
        self.event_system.add_handler(pygame.MOUSEBUTTONDOWN, self._handle_mouse_click)
        self.event_system.add_handler(pygame.MOUSEMOTION, self._handle_mouse_motion)
        self.event_system.add_handler(pygame.KEYDOWN, self._handle_key_press)

    def load_scenes_from_script(self):
        """Charger les scènes depuis script.txt"""
        script_path = os.path.join(os.path.dirname(__file__), 'script.txt')
        if not os.path.exists(script_path):
            # Créer une scène par défaut si script.txt n'existe pas
            self.create_default_scene()
            return

        try:
            # Parser le script (version simplifiée)
            scenes_data = self.parse_script_simple(script_path)

            for scene_id, scene_data in scenes_data.items():
                scene = Scene(self, scene_data)
                self.scene_manager.scenes[scene_id] = scene

            # Définir la scène actuelle
            if 'hall' in self.scene_manager.scenes:
                self.scene_manager.current_scene = self.scene_manager.scenes['hall']
                self.context['current_scene'] = self.scene_manager.current_scene

        except Exception as e:
            logger = get_logger()
            logger.error(f"Error loading script: {e}")
            self.create_default_scene()

    def parse_script_simple(self, script_path: str) -> Dict[str, Any]:
        """Parser simplifié du script.txt - version optimisée"""
        scenes = {}

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parser basique pour les scènes
            sections = content.split('## ')
            for section in sections[1:]:  # Skip first empty section
                lines = section.strip().split('\n')
                scene_id = lines[0].strip()

                scene_data = {
                    'id': scene_id,
                    'name': scene_id,
                    'entities': []
                }

                # Chercher les objets dans la section
                in_objects = False
                for line in lines[1:]:
                    line = line.strip()
                    if line == 'objects:':
                        in_objects = True
                    elif in_objects and '.' in line and ':' in line:
                        try:
                            obj_id, obj_info = line.split('.', 1)
                            obj_type, obj_name = obj_info.split(':', 1)
                            scene_data['entities'].append({
                                'id': obj_id.strip(),
                                'name': obj_name.strip(),
                                'type': obj_type.strip(),
                                'position': self.get_default_position(obj_id.strip()),
                                'properties': self.get_default_properties(obj_id.strip(), obj_type.strip())
                            })
                        except:
                            pass
                    elif line.startswith('object_properties:'):
                        break

                scenes[scene_id] = scene_data

        except Exception as e:
            logger = get_logger()
            logger.error(f"Error parsing script: {e}")

        return scenes

    def get_default_position(self, obj_id: str) -> tuple:
        """Positions par défaut pour les objets"""
        positions = {
            'x0001': (500, 300),  # Porte (selon script.txt)
            'x0002': (300, 350),  # Table (selon script.txt)  
            'x0003': (300, 320),  # Clé (selon script.txt)
        }
        return positions.get(obj_id, (400, 300))

    def get_default_properties(self, obj_id: str, obj_type: str) -> Dict[str, Any]:
        """Propriétés par défaut pour les objets selon le script.txt"""
        if obj_id == 'x0001' and obj_type == 'door':
            # Porte verrouillée nécessitant la clé x0003
            return {
                'width': 64,
                'height': 128,
                'locked': True,
                'key_required': 'x0003'
            }
        elif obj_id == 'x0002' and obj_type == 'table':
            # Table avec la clé dessus
            return {
                'width': 96,
                'height': 64,
                'items_on_top': ['x0003']
            }
        elif obj_id == 'x0003' and obj_type == 'key':
            # Clé
            return {
                'width': 32,
                'height': 32,
                'description': 'petite clé en laiton brillant'
            }
        else:
            return {}

    def create_default_scene(self):
        """Créer une scène par défaut si le script n'existe pas"""
        scene_data = {
            'id': 'hall',
            'name': 'Hall d\'entrée',
            'entities': [
                {
                    'id': 'door_001',
                    'name': 'Porte d\'entrée',
                    'type': 'door',
                    'position': (300, 200),
                    'properties': {
                        'width': 64,
                        'height': 128,
                        'locked': True,
                        'key_required': 'key_001'
                    }
                },
                {
                    'id': 'key_001',
                    'name': 'Clé en laiton',
                    'type': 'key',
                    'position': (500, 350),
                    'properties': {
                        'width': 32,
                        'height': 32
                    }
                },
                {
                    'id': 'table_001',
                    'name': 'Table d\'entrée',
                    'type': 'table',
                    'position': (150, 300),
                    'properties': {
                        'width': 96,
                        'height': 64,
                        'items_on_top': ['key_001']
                    }
                }
            ]
        }

        scene = Scene(self, scene_data)
        self.scene_manager.scenes['hall'] = scene
        self.scene_manager.current_scene = scene
        self.context['current_scene'] = scene

    def _handle_mouse_click(self, event, context):
        """Gérer les clics souris"""
        pos = event.pos

        # Vérifier si le clic est dans la scène
        scene_rect = pygame.Rect(0, 0, self.width, int(self.height * 3/4))
        if scene_rect.collidepoint(pos):
            # Gérer le clic dans la scène
            if self.scene_manager.current_scene:
                clicked_entity = self._get_clicked_entity(pos)
                
                if clicked_entity:
                    # Un objet a été cliqué
                    if self.interface.selected_action in self.interface.two_object_actions:
                        # Action à deux objets
                        if self.interface.first_object is None:
                            # Premier objet sélectionné
                            self.interface.first_object = clicked_entity
                            preposition = "à" if self.interface.selected_action == "Donner" else "avec"
                            self.context['status'] = f"{self.interface.selected_action} {clicked_entity.name} {preposition}"
                        else:
                            # Deuxième objet sélectionné - exécuter l'action
                            self._execute_two_object_action(
                                self.interface.selected_action,
                                self.interface.first_object,
                                clicked_entity
                            )
                            # Reset l'état
                            self.interface.selected_action = None
                            self.interface.first_object = None
                            self.context['selected_action'] = None
                            self.context['status'] = ""
                    else:
                        # Action normale à un objet
                        if not self.scene_manager.current_scene.handle_click(pos, self.interface.selected_action):
                            # Reset si l'action échoue
                            if self.interface.selected_action:
                                self.interface.selected_action = None
                                self.interface.first_object = None
                                self.context['selected_action'] = None
                else:
                    # Aucun objet cliqué - annuler les actions en cours
                    if self.interface.selected_action:
                        self.interface.selected_action = None
                        self.interface.first_object = None
                        self.context['selected_action'] = None
                        self.context['status'] = ""
        else:
            # Gérer les clics UI
            if self.interface:
                self.interface.handle_click(pos, self.context)

    def _get_clicked_entity(self, pos):
        """Trouve l'entité cliquée à la position donnée"""
        if self.scene_manager.current_scene:
            for entity in self.scene_manager.current_scene.entities:
                if entity.visible and entity.bounding_box.collidepoint(pos):
                    return entity
        return None

    def _execute_two_object_action(self, action, first_obj, second_obj):
        """Exécute une action à deux objets"""
        if action == "Utiliser":
            # Logique pour "Utiliser X avec Y"
            result = first_obj.use_with(second_obj, self.context)
            if result:
                self.context['status'] = result
        elif action == "Donner":
            # Logique pour "Donner X à Y" 
            result = first_obj.give_to(second_obj, self.context)
            if result:
                self.context['status'] = result

    def _handle_mouse_motion(self, event, context):
        """Gérer le mouvement de la souris"""
        pos = event.pos
        
        # Gérer le survol de l'interface (priorité aux boutons d'action)
        if self.interface:
            self.interface.handle_hover(pos)
            # Si une action est survolée, afficher son nom
            if self.interface.hovered_action:
                self.context['status'] = self.interface.hovered_action
                return
        
        # Vérifier si le survol est dans la scène pour les entités
        scene_rect = pygame.Rect(0, 0, self.width, int(self.height * 3/4))
        if scene_rect.collidepoint(pos):
            # Vérifier le survol des entités dans la scène
            if self.scene_manager.current_scene:
                entity_name = self.scene_manager.current_scene.handle_hover(pos)
                if entity_name:
                    # Gestion spéciale pour les actions à deux objets
                    if self.interface.selected_action in self.interface.two_object_actions:
                        if self.interface.first_object is None:
                            # Premier objet à sélectionner
                            self.context['status'] = f"{self.interface.selected_action} {entity_name}"
                        else:
                            # Deuxième objet (combinaison complète)
                            if self.interface.selected_action == "Donner":
                                self.context['status'] = f"{self.interface.selected_action} {self.interface.first_object.name} à {entity_name}"
                            else:  # Utiliser
                                self.context['status'] = f"{self.interface.selected_action} {self.interface.first_object.name} avec {entity_name}"
                    elif self.interface.selected_action:
                        # Action normale à un objet
                        self.context['status'] = f"{self.interface.selected_action} {entity_name}"
                    else:
                        self.context['status'] = entity_name
                else:
                    # Pas d'entité survolée, afficher l'état actuel
                    if self.interface.selected_action and self.interface.first_object:
                        if self.interface.selected_action == "Donner":
                            self.context['status'] = f"{self.interface.selected_action} {self.interface.first_object.name} à"
                        else:  # Utiliser
                            self.context['status'] = f"{self.interface.selected_action} {self.interface.first_object.name} avec"
                    elif self.interface.selected_action:
                        self.context['status'] = self.interface.selected_action
                    else:
                        self.context['status'] = ""
        else:
            # Hors de la scène, afficher l'état actuel
            if self.interface.selected_action and self.interface.first_object:
                if self.interface.selected_action == "Donner":
                    self.context['status'] = f"{self.interface.selected_action} {self.interface.first_object.name} à"
                else:  # Utiliser
                    self.context['status'] = f"{self.interface.selected_action} {self.interface.first_object.name} avec"
            elif self.interface.selected_action:
                self.context['status'] = self.interface.selected_action
            else:
                self.context['status'] = ""

    def _handle_key_press(self, event, context):
        """Gérer les appuis de touches"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_i:
            # Basculer l'inventaire
            if self.interface:
                self.interface.toggle_inventory()
        elif event.key == pygame.K_F1:
            # Basculer l'affichage des codes d'objets
            self.show_debug_ids = not self.show_debug_ids
            self.context['show_debug_ids'] = self.show_debug_ids

    def _handle_quit(self, event, context):
        """Gérer la fermeture"""
        self.running = False

    def update(self, delta_time: float):
        """Mettre à jour le jeu"""
        # Mettre à jour la scène
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.update(delta_time)

        # Mettre à jour l'interface
        if self.interface:
            self.interface.update(self.context)

        # Nettoyer les descriptions temporaires
        self._update_temp_descriptions()

    def _update_temp_descriptions(self):
        """Nettoyer les descriptions temporaires expirées"""
        current_time = pygame.time.get_ticks()
        temp_descriptions = self.context.get('temp_descriptions', [])

        # Garder seulement les descriptions actives
        active_descriptions = []
        for desc in temp_descriptions:
            if current_time - desc['start_time'] < desc['duration']:
                active_descriptions.append(desc)

        self.context['temp_descriptions'] = active_descriptions

    def render(self):
        """Rendre le jeu"""
        # Effacer l'écran
        self.renderer.clear()

        # Rendre la scène
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.render(self.renderer, self.context)

        # Rendre l'interface
        if self.interface:
            self.interface.render(self.renderer, self.context)

        # Rendre les notifications
        if self.notification_system:
            self.notification_system.render(self.renderer)

        # Mettre à jour l'affichage
        pygame.display.flip()

    def run(self):
        """Boucle principale du jeu"""
        self.running = True
        logger = get_logger()
        logger.info("Démarrage du jeu")

        try:
            while self.running:
                delta_time = self.clock.tick(self.fps) / 1000.0

                # Gérer les événements
                for event in pygame.event.get():
                    self.event_system.handle_event(event, self.context)

                # Mettre à jour et rendre
                self.update(delta_time)
                self.render()

        except KeyboardInterrupt:
            logger.info("Jeu interrompu par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur pendant l'exécution: {e}")
        finally:
            logger.info("Jeu terminé")
            pygame.quit()


def main():
    """Point d'entrée principal"""
    game = PointClickGame()
    game.run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
