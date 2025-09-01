"""
Main game interface
"""

import pygame
from typing import Dict, Any, Tuple, List


class GameInterface:
    """Main user interface controller"""

    def __init__(self):
        self.width = 800
        self.height = 600

        # UI Layout constants
        self.SCENE_RECT = pygame.Rect(0, 0, self.width, int(self.height * 3 / 4))
        self.BOTTOM_RECT = pygame.Rect(0, self.SCENE_RECT.height, self.width, self.height - self.SCENE_RECT.height)
        self.STATUS_HEIGHT = 28
        self.STATUS_RECT = pygame.Rect(0, self.BOTTOM_RECT.top, self.width, self.STATUS_HEIGHT)
        self.INTERACTIVE_BOTTOM = pygame.Rect(0, self.BOTTOM_RECT.top + self.STATUS_HEIGHT,
                                            self.width, self.BOTTOM_RECT.height - self.STATUS_HEIGHT)
        self.ACTION_AREA = pygame.Rect(0, self.INTERACTIVE_BOTTOM.top,
                                     int(self.width * 0.5), self.INTERACTIVE_BOTTOM.height)
        self.INV_AREA = pygame.Rect(int(self.width * 0.5), self.INTERACTIVE_BOTTOM.top,
                                   int(self.width * 0.5), self.INTERACTIVE_BOTTOM.height)

        # Action verbs (French)
        self.action_verbs = [
            'Donner', 'Ouvrir', 'Fermer',
            'Prendre', 'Regarder', 'Parler à',
            'Utiliser', 'Pousser', 'Tirer'
        ]

        # UI state
        self.show_inventory = True  # Inventaire toujours visible par défaut
        self.selected_action = None
        self.hovered_action = None
        self.hovered_inventory_item = None  # Objet survolé dans l'inventaire
        self.selected_inventory_item = None  # Objet sélectionné dans l'inventaire
        
        # Inventory scrolling state
        self.inventory_scroll_offset = 0  # Index du premier objet affiché
        self.max_visible_items = 8  # 8 cases visibles à la fois
        
        # Two-object action state
        self.first_object = None  # For actions like "Utiliser clé avec..."
        self.two_object_actions = ['Donner', 'Utiliser']  # Actions that require two objects

        # Fonts
        self.fonts = self._load_fonts()
        
        # Sprites cache pour les objets (pour les futurs PNG)
        self.item_sprites = self._load_item_sprites()

    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Load UI fonts"""
        fonts = {}
        try:
            fonts['small'] = pygame.font.SysFont('Arial', 16)
            fonts['small_bold'] = pygame.font.SysFont('Arial', 16, bold=True)
            fonts['medium'] = pygame.font.SysFont('Arial', 20)
            fonts['large'] = pygame.font.SysFont('Arial', 24)
        except:
            pygame.font.init()
            fonts['small'] = pygame.font.Font(None, 16)
            fonts['medium'] = pygame.font.Font(None, 20)
            fonts['large'] = pygame.font.Font(None, 24)
        return fonts

    def _load_item_sprites(self) -> Dict[str, Any]:
        """Charger les sprites des objets (PNG)"""
        import os
        sprites = {}
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        
        # Liste des sprites à charger
        sprite_files = {
            'cle': 'cle.png',
            'porte': 'porte.png', 
            'table': 'table.png'
        }
        
        for sprite_key, filename in sprite_files.items():
            sprite_path = os.path.join(assets_dir, filename)
            if os.path.exists(sprite_path):
                try:
                    sprites[sprite_key] = pygame.image.load(sprite_path)
                    print(f"Sprite chargé: {filename}")
                except:
                    print(f"Erreur lors du chargement de {filename}")
            else:
                print(f"Sprite non trouvé: {filename} (utilisation de l'icône par défaut)")
        
        return sprites

    def update(self, context: Dict[str, Any]) -> None:
        """Update interface state"""
        # Update based on context
        pass

    def render(self, renderer, context: Dict[str, Any]) -> None:
        """Render the interface"""
        # Render status bar
        self._render_status_bar(renderer, context)

        # Render action bar
        self._render_action_bar(renderer, context)

        # Render inventory (toujours visible)
        self._render_inventory(renderer, context)

        # Render temporary descriptions
        temp_descriptions = context.get('temp_descriptions', [])
        renderer.render_temp_descriptions(temp_descriptions)

    def _render_status_bar(self, renderer, context: Dict[str, Any]) -> None:
        """Render the status bar"""
        # Background
        renderer.fill_rect(self.STATUS_RECT, (20, 20, 20))

        # Status text - centered horizontally and vertically
        status_text = context.get('status', '')
        if status_text:
            renderer.render_text(status_text, self.STATUS_RECT.center,
                               font_name='small', center=True)

    def _render_action_bar(self, renderer, context: Dict[str, Any]) -> None:
        """Render the action buttons"""
        # Background
        renderer.fill_rect(self.ACTION_AREA, (40, 40, 40))

        # Action buttons (3x3 grid)
        button_width = self.ACTION_AREA.width // 3
        button_height = self.ACTION_AREA.height // 3

        for i, action in enumerate(self.action_verbs):
            row = i // 3
            col = i % 3

            button_rect = pygame.Rect(
                self.ACTION_AREA.left + col * button_width,
                self.ACTION_AREA.top + row * button_height,
                button_width,
                button_height
            )

            # Button background
            color = (60, 60, 60)
            if self.hovered_action == action:
                color = (80, 80, 80)
            if self.selected_action == action:
                color = (100, 100, 100)

            renderer.fill_rect(button_rect, color)
            renderer.draw_rect(button_rect, (255, 255, 255), 1)

            # Button text
            text_color = (255, 255, 255)
            font_name = 'small_bold' if self.hovered_action == action else 'small'
            renderer.render_text(action, button_rect.center,
                               color=text_color, font_name=font_name, center=True)

    def _render_inventory(self, renderer, context: Dict[str, Any]) -> None:
        """Render the inventory panel"""
        # Background
        renderer.fill_rect(self.INV_AREA, (50, 50, 50))
        renderer.draw_rect(self.INV_AREA, (255, 255, 255), 1)

        # Get inventory items
        inventory = context.get('inventory', [])
        total_items = len(inventory)
        
        # Zone de flèches à gauche de l'inventaire (30px comme spécifié)
        scroll_area = pygame.Rect(
            self.INV_AREA.left,
            self.INV_AREA.top + 1,  # 1px de marge en haut
            30,
            self.INV_AREA.height - 2  # 1px de marge en haut et en bas
        )
        
        # Zone d'inventaire ajustée (sans les 30px des flèches + marges haut/bas)
        inv_content_area = pygame.Rect(
            self.INV_AREA.left + 30,
            self.INV_AREA.top + 1,  # 1px de marge en haut
            self.INV_AREA.width - 30,
            self.INV_AREA.height - 2  # 1px de marge en haut et en bas
        )

        # Dessiner les flèches de défilement si nécessaire
        if total_items > self.max_visible_items:
            self._render_scroll_arrows(renderer, scroll_area, total_items)

        # Afficher les 8 cases d'inventaire utilisant tout l'espace disponible
        slots_per_row = 4  # 4 cases par rangée
        rows = 2  # 2 rangées
        
        # Diviser l'espace en 8 parties égales
        slot_width = inv_content_area.width // slots_per_row
        slot_height = inv_content_area.height // rows
        
        # Afficher les 8 cases visibles avec défilement
        for i in range(self.max_visible_items):
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_rect = pygame.Rect(
                inv_content_area.left + col * slot_width,
                inv_content_area.top + row * slot_height,
                slot_width,
                slot_height
            )
            
            # Rectangle pour l'objet avec 1px de marge
            item_rect = pygame.Rect(
                slot_rect.left + 1,
                slot_rect.top + 1,
                slot_rect.width - 2,
                slot_rect.height - 2
            )

            # Index de l'objet réel avec le défilement
            item_index = self.inventory_scroll_offset + i
            
            if item_index < total_items:
                # Case avec un objet
                item = inventory[item_index]
                item_name = item.get('name', '')
                
                # Vérifier si l'objet est survolé ou sélectionné
                is_hovered = (self.hovered_inventory_item == item_name)
                is_selected = (self.selected_inventory_item == item_name)
                
                # Couleur de fond selon l'état
                if is_selected:
                    bg_color = (100, 100, 100)  # Plus clair si sélectionné
                    border_color = (255, 255, 255)  # Bordure blanche
                elif is_hovered:
                    bg_color = (85, 85, 85)  # Légèrement plus clair si survolé
                    border_color = (255, 255, 255)  # Bordure blanche
                else:
                    bg_color = (70, 70, 70)  # Couleur normale
                    border_color = None  # Pas de bordure
                
                # Dessiner le fond
                renderer.fill_rect(item_rect, bg_color)
                
                # Dessiner la bordure si nécessaire
                if border_color:
                    renderer.draw_rect(item_rect, border_color, 1)
                
                # Afficher l'icône/image de l'objet
                self._render_item_icon(renderer, item, item_rect)
            else:
                # Case vide
                renderer.fill_rect(item_rect, (30, 30, 30))
                renderer.draw_rect(item_rect, (100, 100, 100), 1)

    def _render_scroll_arrows(self, renderer, scroll_area: pygame.Rect, total_items: int) -> None:
        """Dessiner les flèches de défilement à gauche de l'inventaire"""
        # Background pour la zone de défilement
        renderer.fill_rect(scroll_area, (40, 40, 40))
        renderer.draw_rect(scroll_area, (255, 255, 255), 1)
        
        # Dimensions des flèches (verticalement empilées)
        arrow_size = 20
        spacing = 10
        
        # Position verticale centrée
        center_y = scroll_area.centery
        
        # Flèche vers le haut (scroll vers les objets précédents)
        up_arrow_rect = pygame.Rect(
            scroll_area.centerx - arrow_size // 2, 
            center_y - arrow_size - spacing // 2,
            arrow_size, arrow_size
        )
        
        # Flèche vers le bas (scroll vers les objets suivants)
        down_arrow_rect = pygame.Rect(
            scroll_area.centerx - arrow_size // 2, 
            center_y + spacing // 2,
            arrow_size, arrow_size
        )
        
        # Couleurs des flèches selon la possibilité de scroll
        can_scroll_up = self.inventory_scroll_offset > 0
        can_scroll_down = self.inventory_scroll_offset + self.max_visible_items < total_items
        
        # Dessiner flèche vers le haut
        up_color = (255, 255, 255) if can_scroll_up else (100, 100, 100)
        renderer.fill_rect(up_arrow_rect, (60, 60, 60))
        renderer.draw_rect(up_arrow_rect, up_color, 2)
        
        # Dessiner triangle pointant vers le haut
        triangle_points = [
            (up_arrow_rect.centerx, up_arrow_rect.top + 4),  # Sommet
            (up_arrow_rect.left + 4, up_arrow_rect.bottom - 4),  # Base gauche
            (up_arrow_rect.right - 4, up_arrow_rect.bottom - 4)  # Base droite
        ]
        pygame.draw.polygon(renderer.surface, up_color, triangle_points)
        
        # Dessiner flèche vers le bas
        down_color = (255, 255, 255) if can_scroll_down else (100, 100, 100)
        renderer.fill_rect(down_arrow_rect, (60, 60, 60))
        renderer.draw_rect(down_arrow_rect, down_color, 2)
        
        # Dessiner triangle pointant vers le bas
        triangle_points = [
            (down_arrow_rect.centerx, down_arrow_rect.bottom - 4),  # Sommet
            (down_arrow_rect.left + 4, down_arrow_rect.top + 4),  # Base gauche
            (down_arrow_rect.right - 4, down_arrow_rect.top + 4)  # Base droite
        ]
        pygame.draw.polygon(renderer.surface, down_color, triangle_points)

    def _render_item_icon(self, renderer, item: Dict[str, Any], slot_rect: pygame.Rect) -> None:
        """Rendre l'icône d'un objet dans l'inventaire"""
        item_id = item.get('id', '')
        item_name = item.get('name', '')
        
        # Essayer d'abord de charger un sprite PNG si disponible
        sprite_key = self._get_sprite_key(item_id, item_name)
        if sprite_key in self.item_sprites:
            # Afficher le sprite PNG
            sprite = self.item_sprites[sprite_key]
            # Redimensionner et centrer le sprite dans la case
            sprite_rect = sprite.get_rect(center=slot_rect.center)
            renderer.screen.blit(sprite, sprite_rect)
            return
        
        # Sinon, utiliser les icônes par défaut
        if 'clé' in item_name.lower() or 'key' in item_id.lower():
            # Icône de clé - dessiner une clé
            self._draw_key_icon(renderer, slot_rect)
        elif 'porte' in item_name.lower() or 'door' in item_id.lower():
            # Icône de porte
            renderer.render_text("🚪", slot_rect.center, font_name='medium', center=True, color=(255, 255, 255))
        elif 'table' in item_name.lower():
            # Icône de table  
            renderer.render_text("🪑", slot_rect.center, font_name='medium', center=True, color=(255, 255, 255))
        else:
            # Objet générique - afficher la première lettre du nom
            first_letter = item_name[0].upper() if item_name else "?"
            renderer.render_text(first_letter, slot_rect.center, font_name='large', center=True, color=(255, 255, 255))

    def _get_sprite_key(self, item_id: str, item_name: str) -> str:
        """Obtenir la clé du sprite selon l'objet"""
        if 'clé' in item_name.lower() or 'key' in item_id.lower():
            return 'cle'
        elif 'porte' in item_name.lower() or 'door' in item_id.lower():
            return 'porte'
        elif 'table' in item_name.lower():
            return 'table'
        else:
            return 'default'
    
    def _draw_key_icon(self, renderer, slot_rect: pygame.Rect) -> None:
        """Dessiner une icône de clé simple"""
        # TODO: Plus tard, charger cle.png depuis les assets
        # Pour l'instant, dessiner une clé simple avec des rectangles
        
        center_x = slot_rect.centerx
        center_y = slot_rect.centery
        
        # Corps de la clé (tige)
        key_body = pygame.Rect(center_x - 15, center_y - 2, 20, 4)
        renderer.fill_rect(key_body, (255, 215, 0))  # Couleur dorée
        
        # Tête de la clé (cercle/carré)
        key_head = pygame.Rect(center_x - 18, center_y - 6, 8, 12)
        renderer.fill_rect(key_head, (255, 215, 0))
        renderer.draw_rect(key_head, (200, 180, 0), 1)
        
        # Dents de la clé
        tooth1 = pygame.Rect(center_x + 2, center_y, 3, 4)
        tooth2 = pygame.Rect(center_x + 8, center_y, 2, 3)
        renderer.fill_rect(tooth1, (255, 215, 0))
        renderer.fill_rect(tooth2, (255, 215, 0))

    def handle_click(self, pos: Tuple[int, int], context: Dict[str, Any]) -> bool:
        """Handle mouse click on interface"""
        # Check action buttons
        if self._handle_action_click(pos, context):
            return True

        # Check inventory (toujours interactif)
        if self._handle_inventory_click(pos, context):
            return True

        return False

    def handle_hover(self, pos: Tuple[int, int], context: Dict[str, Any] = None) -> None:
        """Handle mouse hover on interface elements"""
        # Reset hover state
        self.hovered_action = None
        self.hovered_inventory_item = None
        
        # Check action buttons
        button_width = self.ACTION_AREA.width // 3
        button_height = self.ACTION_AREA.height // 3

        for i, action in enumerate(self.action_verbs):
            row = i // 3
            col = i % 3

            button_rect = pygame.Rect(
                self.ACTION_AREA.left + col * button_width,
                self.ACTION_AREA.top + row * button_height,
                button_width,
                button_height
            )

            if button_rect.collidepoint(pos):
                self.hovered_action = action
                break
        
        # Check inventory hover if context is provided
        if context is not None:
            self.hovered_inventory_item = self.get_hovered_inventory_item(pos, context)

    def get_hovered_inventory_item(self, pos: Tuple[int, int], context: Dict[str, Any]) -> str:
        """Retourner le nom de l'objet survolé dans l'inventaire"""
        inventory = context.get('inventory', [])
        
        # Zone d'inventaire ajustée (sans les 30px des flèches + marges haut/bas)
        inv_content_area = pygame.Rect(
            self.INV_AREA.left + 30,
            self.INV_AREA.top + 1,  # 1px de marge en haut
            self.INV_AREA.width - 30,
            self.INV_AREA.height - 2  # 1px de marge en haut et en bas
        )
        
        # Utiliser les mêmes dimensions que le rendu
        slots_per_row = 4
        rows = 2
        slot_width = inv_content_area.width // slots_per_row
        slot_height = inv_content_area.height // rows
        
        # Calculer les objets visibles avec le décalage de scroll
        start_index = self.inventory_scroll_offset
        visible_inventory = inventory[start_index:start_index + self.max_visible_items]

        for i, item in enumerate(visible_inventory):
            row = i // slots_per_row
            col = i % slots_per_row
            
            # Rectangle de la case complète
            slot_rect = pygame.Rect(
                inv_content_area.left + col * slot_width,
                inv_content_area.top + row * slot_height,
                slot_width,
                slot_height
            )
            
            # Rectangle pour l'objet avec 1px de marge
            item_rect = pygame.Rect(
                slot_rect.left + 1,
                slot_rect.top + 1,
                slot_rect.width - 2,
                slot_rect.height - 2
            )

            if item_rect.collidepoint(pos):
                return item['name']

        return ""

    def _handle_action_click(self, pos: Tuple[int, int], context: Dict[str, Any]) -> bool:
        """Handle click on action buttons"""
        button_width = self.ACTION_AREA.width // 3
        button_height = self.ACTION_AREA.height // 3

        for i, action in enumerate(self.action_verbs):
            row = i // 3
            col = i % 3

            button_rect = pygame.Rect(
                self.ACTION_AREA.left + col * button_width,
                self.ACTION_AREA.top + row * button_height,
                button_width,
                button_height
            )

            if button_rect.collidepoint(pos):
                self.selected_action = action
                context['selected_action'] = action
                context['status'] = action
                return True

        return False

    def _handle_inventory_click(self, pos: Tuple[int, int], context: Dict[str, Any]) -> bool:
        """Handle click on inventory items and scroll arrows"""
        inventory = context.get('inventory', [])
        total_items = len(inventory)
        
        # Zone de flèches à gauche (30px + marges haut/bas)
        scroll_area = pygame.Rect(
            self.INV_AREA.left,
            self.INV_AREA.top + 1,  # 1px de marge en haut
            30,
            self.INV_AREA.height - 2  # 1px de marge en haut et en bas
        )
        
        # Zone d'inventaire ajustée (sans les 30px des flèches + marges haut/bas)
        inv_content_area = pygame.Rect(
            self.INV_AREA.left + 30,
            self.INV_AREA.top + 1,  # 1px de marge en haut
            self.INV_AREA.width - 30,
            self.INV_AREA.height - 2  # 1px de marge en haut et en bas
        )

        # Vérifier les clics sur les flèches de défilement
        if total_items > self.max_visible_items and scroll_area.collidepoint(pos):
            # Dimensions des flèches (verticalement empilées)
            arrow_size = 20
            spacing = 10
            center_y = scroll_area.centery
            
            # Zone de la flèche vers le haut
            up_arrow_rect = pygame.Rect(
                scroll_area.centerx - arrow_size // 2, 
                center_y - arrow_size - spacing // 2,
                arrow_size, arrow_size
            )
            
            # Zone de la flèche vers le bas
            down_arrow_rect = pygame.Rect(
                scroll_area.centerx - arrow_size // 2, 
                center_y + spacing // 2,
                arrow_size, arrow_size
            )
            
            if up_arrow_rect.collidepoint(pos) and self.inventory_scroll_offset > 0:
                # Défiler vers le haut
                self.inventory_scroll_offset = max(0, self.inventory_scroll_offset - self.max_visible_items)
                return True
                
            elif down_arrow_rect.collidepoint(pos) and self.inventory_scroll_offset + self.max_visible_items < total_items:
                # Défiler vers le bas
                self.inventory_scroll_offset = min(total_items - self.max_visible_items, 
                                                 self.inventory_scroll_offset + self.max_visible_items)
                return True

        # Vérifier les clics sur les cases d'inventaire
        slots_per_row = 4
        rows = 2
        
        # Diviser l'espace en 8 parties égales
        slot_width = inv_content_area.width // slots_per_row
        slot_height = inv_content_area.height // rows

        for i in range(self.max_visible_items):
            row = i // slots_per_row
            col = i % slots_per_row
            
            # Rectangle de la case complète
            slot_rect = pygame.Rect(
                inv_content_area.left + col * slot_width,
                inv_content_area.top + row * slot_height,
                slot_width,
                slot_height
            )
            
            # Rectangle pour l'objet avec 1px de marge
            item_rect = pygame.Rect(
                slot_rect.left + 1,
                slot_rect.top + 1,
                slot_rect.width - 2,
                slot_rect.height - 2
            )

            if item_rect.collidepoint(pos):
                # Index de l'objet réel avec le défilement
                item_index = self.inventory_scroll_offset + i
                
                if item_index < total_items:
                    # Objet cliqué
                    clicked_item = inventory[item_index]
                    item_name = clicked_item.get('name', '')
                    
                    # Gérer la sélection - toggle si on clique sur le même objet
                    if self.selected_inventory_item == item_name:
                        self.selected_inventory_item = None
                    else:
                        self.selected_inventory_item = item_name
                    
                    # Stocker l'objet cliqué pour usage externe
                    context['selected_inventory_item'] = clicked_item
                    return clicked_item

        return None

    def get_clicked_inventory_item(self, pos: Tuple[int, int], context: Dict[str, Any]):
        """Retourner l'objet de l'inventaire cliqué (pour les actions à deux objets)"""
        return self._handle_inventory_click(pos, context)

    def clear_selections(self) -> None:
        """Nettoyer tous les états de sélection après l'exécution d'une action"""
        self.selected_inventory_item = None
        self.selected_action = None
        self.first_object = None

    def toggle_inventory(self) -> None:
        """Toggle inventory visibility"""
        self.show_inventory = not self.show_inventory
