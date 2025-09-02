"""
Scene Module
Gestion d'une scène du jeu avec ses entités (une scene est une image 800x450)
"""

import pygame
from typing import Dict, Any, Optional
from entities import Door, Key, Table, BaseEntity
from utils.logger import get_logger


class Scene:
    """Scene utilisant les entités du jeu"""

    def __init__(self, game, scene_data: Dict[str, Any]):
        self.game = game
        self.scene_data = scene_data
        self.entities = []
        self.background_color = (75, 126, 165)  # Sky blue
        self.background_image = None  # Image de fond
        
        # Charger l'image de fond si spécifiée
        if 'background' in scene_data:
            self.load_background(scene_data['background'])

        # Créer les entités à partir des données de scène
        self.setup_entities()

    def load_background(self, background_path: str):
        """Charger une image de fond"""
        import pygame
        try:
            self.background_image = pygame.image.load(background_path)
            # Redimensionner l'image pour qu'elle fasse 800x450 (taille de la scène)
            self.background_image = pygame.transform.scale(self.background_image, (800, 450))
            print(f"Image de fond chargée: {background_path}")
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image de fond {background_path}: {e}")
            self.background_image = None

    def setup_entities(self):
        """Créer les entités à partir des données de scène"""
        entities_data = self.scene_data.get('entities', [])

        for entity_data in entities_data:
            entity = self.create_entity_from_data(entity_data)
            if entity:
                self.entities.append(entity)

    def create_entity_from_data(self, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Créer une entité à partir des données"""
        entity_type = entity_data.get('type', 'unknown')
        entity_id = entity_data.get('id', 'unknown')
        name = entity_data.get('name', entity_id)
        position = entity_data.get('position')
        properties = entity_data.get('properties', {})

        try:
            if entity_type.lower() == 'door':
                return Door(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'key':
                return Key(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'table':
                return Table(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'crystal':
                from entities.game_entities import Crystal
                return Crystal(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'ancient_book':
                from entities.game_entities import AncientBook
                return AncientBook(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'pedestal':
                from entities.game_entities import Pedestal
                return Pedestal(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'portal':
                from entities.game_entities import ExitPortal
                return ExitPortal(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            elif entity_type.lower() == 'mysterious_key':
                from entities.game_entities import MysteriousKey
                return MysteriousKey(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
            else:
                # Entité générique
                return BaseEntity(
                    entity_id=entity_id,
                    name=name,
                    position=position,
                    **properties
                )
        except Exception as e:
            logger = get_logger()
            logger.error(f"Error creating entity {entity_id}: {e}")
            return None

    def update(self, delta_time: float):
        """Mettre à jour la scène"""
        for entity in self.entities:
            entity.update(self.game.context)

    def render(self, renderer, context=None):
        """Rendre la scène"""
        # Fond
        if self.background_image:
            # Afficher l'image de fond
            renderer.surface.blit(self.background_image, (0, 0))
        else:
            # Afficher la couleur de fond par défaut
            renderer.fill_rect(pygame.Rect(0, 0, 800, 600), self.background_color)

        # Rendre les entités
        for entity in self.entities:
            if entity.visible:
                # Couleurs selon le type d'entité
                if isinstance(entity, Door):
                    # Rendu spécial pour les portes selon leur état
                    self._render_door(renderer, entity)
                elif isinstance(entity, Key):
                    color = (255, 215, 0)  # Or pour les clés
                    renderer.fill_rect(entity.bounding_box, color)
                    renderer.draw_rect(entity.bounding_box, (0, 0, 0), 2)
                elif isinstance(entity, Table):
                    color = (160, 82, 45)  # Marron clair pour les tables
                    renderer.fill_rect(entity.bounding_box, color)
                    renderer.draw_rect(entity.bounding_box, (0, 0, 0), 2)
                else:
                    color = (128, 128, 128)  # Gris par défaut
                    renderer.fill_rect(entity.bounding_box, color)
                    renderer.draw_rect(entity.bounding_box, (0, 0, 0), 2)

                # Afficher l'ID pour le débogage (conditionnel avec F1)
                if context and context.get('show_debug_ids', False) and hasattr(renderer, 'render_text'):
                    renderer.render_text(
                        entity.id,
                        (entity.bounding_box.centerx, entity.bounding_box.top - 15),
                        font_name='small',
                        center=True
                    )

    def _render_door(self, renderer, door):
        """Rendre une porte selon son état"""
        door_rect = door.bounding_box
        
        if door.state == "open":
            # Porte ouverte : afficher une porte entrouverte (décalée)
            # Porte principale plus fine (ouverte vers la droite)
            open_width = door_rect.width // 3
            open_rect = pygame.Rect(
                door_rect.right - open_width,
                door_rect.y,
                open_width,
                door_rect.height
            )
            
            # Couleur plus claire pour une porte ouverte
            door_color = (160, 100, 50)  # Marron clair
            renderer.fill_rect(open_rect, door_color)
            renderer.draw_rect(open_rect, (0, 0, 0), 2)
            
            # Afficher l'espace ouvert (plus sombre)
            space_rect = pygame.Rect(
                door_rect.x,
                door_rect.y,
                door_rect.width - open_width,
                door_rect.height
            )
            renderer.fill_rect(space_rect, (50, 30, 20))  # Très sombre pour l'ouverture
            
        elif door.locked:
            # Porte verrouillée : couleur plus sombre avec un verrou
            door_color = (80, 40, 20)  # Marron très sombre
            renderer.fill_rect(door_rect, door_color)
            renderer.draw_rect(door_rect, (0, 0, 0), 3)  # Bordure plus épaisse
            
            # Dessiner un verrou (petit rectangle doré au centre)
            lock_size = 8
            lock_x = door_rect.centerx - lock_size // 2
            lock_y = door_rect.centery - lock_size // 2
            lock_rect = pygame.Rect(lock_x, lock_y, lock_size, lock_size)
            renderer.fill_rect(lock_rect, (255, 215, 0))  # Or
            renderer.draw_rect(lock_rect, (0, 0, 0), 1)
            
        else:
            # Porte fermée : couleur normale
            door_color = (139, 69, 19)  # Marron normal
            renderer.fill_rect(door_rect, door_color)
            renderer.draw_rect(door_rect, (0, 0, 0), 2)

    def handle_click(self, pos, action=None):
        """Gérer les clics dans la scène"""
        for entity in self.entities:
            if entity.visible and entity.bounding_box.collidepoint(pos):
                # Utiliser le contexte principal du jeu
                context = self.game.context
                
                # Mettre à jour quelques informations spécifiques à cette interaction
                context['current_scene_obj'] = {'objects': {e.id: e for e in self.entities}}

                # Vérifier d'abord si le moteur de script naturel peut gérer cette action
                if hasattr(self.game, 'script_engine') and self.game.script_engine and action:
                    script_action = self.game.script_engine.find_action(action.lower(), entity.id)
                    if script_action:
                        # Afficher le message de l'action
                        self._show_message_above(script_action.message, entity, context)
                        # Exécuter les effets
                        self.game.script_engine.execute_action_effects(script_action)
                        # Nettoyer les sélections d'interface après l'exécution réussie
                        if hasattr(self.game, 'interface') and self.game.interface:
                            self.game.interface.clear_selections()
                        return  # Ne pas passer au système classique
                    else:
                        # Vérifier si c'est une action interdite
                        if action:
                            forbidden_msg = self.game.script_engine.get_forbidden_message(action.lower(), entity.id)
                            if forbidden_msg:
                                self._show_message_above(forbidden_msg, entity, context)
                                return  # Ne pas passer au système classique
                        # Fallback vers le système d'entités classique
                            message = entity.on_click(action, context)
                            # Nettoyer les sélections après l'action classique
                            if hasattr(self.game, 'interface') and self.game.interface:
                                self.game.interface.clear_selections()
                else:
                    # Système classique si pas de moteur de script
                    message = entity.on_click(action, context)
                    # Nettoyer les sélections après l'action classique
                    if hasattr(self.game, 'interface') and self.game.interface:
                        self.game.interface.clear_selections()

    def _show_message_above(self, message: str, entity, context: Dict[str, Any], duration: int = 3000):
        """Affiche un message au-dessus d'une entité"""
        if 'temp_descriptions' not in context:
            context['temp_descriptions'] = []

        context['temp_descriptions'].append({
            'text': message,
            'position': entity.position,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        })
        return False

    def handle_hover(self, pos):
        """Gérer le survol des entités dans la scène"""
        for entity in self.entities:
            if entity.visible and entity.bounding_box.collidepoint(pos):
                # Vérifier si c'est une porte ouverte (pour changer le curseur)
                if (entity.id == "door" and hasattr(entity, 'state') and 
                    entity.state == "open"):
                    # Retourner un tuple spécial pour indiquer la porte ouverte
                    return ("door_open", "Aller vers le jardin secret")
                elif entity.id == "return_door":
                    # Porte de retour toujours accessible
                    return ("door_open", "Retourner au hall")
                return entity.name
        return None
