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

    def render(self, renderer):
        """Rendre la scène"""
        # Fond
        renderer.fill_rect(pygame.Rect(0, 0, 800, 600), self.background_color)

        # Rendre les entités
        for entity in self.entities:
            if entity.visible:
                # Couleurs selon le type d'entité
                if isinstance(entity, Door):
                    color = (139, 69, 19)  # Marron pour les portes
                elif isinstance(entity, Key):
                    color = (255, 215, 0)  # Or pour les clés
                elif isinstance(entity, Table):
                    color = (160, 82, 45)  # Marron clair pour les tables
                else:
                    color = (128, 128, 128)  # Gris par défaut

                renderer.fill_rect(entity.bounding_box, color)
                renderer.draw_rect(entity.bounding_box, (0, 0, 0), 2)

                # Afficher l'ID pour le débogage
                if hasattr(renderer, 'render_text'):
                    renderer.render_text(
                        entity.id,
                        (entity.bounding_box.centerx, entity.bounding_box.top - 15),
                        font_name='small',
                        center=True
                    )

    def handle_click(self, pos, action=None):
        """Gérer les clics dans la scène"""
        for entity in self.entities:
            if entity.visible and entity.bounding_box.collidepoint(pos):
                # Créer le contexte pour l'interaction
                context = {
                    'game': self.game,
                    'inventory': self.game.inventory.get_items_list() if hasattr(self.game, 'inventory') else [],
                    'current_scene_obj': {'objects': {e.id: e for e in self.entities}}
                }

                message = entity.on_click(action, context)
                if message:
                    # Ajouter une notification au-dessus de l'entité
                    self.game.notification_system.add_action_message(
                        message, (entity.bounding_box.centerx, entity.bounding_box.top)
                    )
                return True
        return False
