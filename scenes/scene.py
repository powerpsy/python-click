"""
Scene Module
Gestion d'une scène du jeu avec ses entités
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
        self.background_color = (135, 206, 235)  # Sky blue

        # Créer les entités à partir des données de scène
        self.setup_entities()

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

                message = entity.on_click(action, context)
                
                # Désélectionner l'action après exécution
                if action and hasattr(self.game, 'interface') and self.game.interface:
                    self.game.interface.selected_action = None
                    context['selected_action'] = None
                
                if message:
                    # Ajouter une notification au-dessus de l'entité
                    self.game.notification_system.add_action_message(
                        message, (entity.bounding_box.centerx, entity.bounding_box.top)
                    )
                return True
        return False

    def handle_hover(self, pos):
        """Gérer le survol des entités dans la scène"""
        for entity in self.entities:
            if entity.visible and entity.bounding_box.collidepoint(pos):
                return entity.name
        return None
