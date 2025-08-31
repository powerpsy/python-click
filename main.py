import sys
import os
import pygame
from objects import create_object, get_object, get_all_objects

# Window
WIDTH, HEIGHT = 800, 600

# Layout: top 3/4 for scene
SCENE_RECT = pygame.Rect(0, 0, WIDTH, int(HEIGHT * 3 / 4))

# Bottom area
BOTTOM_RECT = pygame.Rect(0, SCENE_RECT.height, WIDTH, HEIGHT - SCENE_RECT.height)

# Action grid (3x3) bottom-left
ACTION_ROWS, ACTION_COLS = 3, 3
STATUS_HEIGHT = 28

# Reserve a status line between scene and the action/inventory area
STATUS_RECT = pygame.Rect(0, BOTTOM_RECT.top, WIDTH, STATUS_HEIGHT)

# Bottom interactive area sits below the status line
INTERACTIVE_BOTTOM = pygame.Rect(0, BOTTOM_RECT.top + STATUS_HEIGHT, WIDTH, BOTTOM_RECT.height - STATUS_HEIGHT)

# Action area (3x3) bottom-left - now takes 50% of width
ACTION_AREA = pygame.Rect(0, INTERACTIVE_BOTTOM.top, int(WIDTH * 0.5), INTERACTIVE_BOTTOM.height)

# Inventory right bottom (4x2) - now takes 50% of width
INV_COLS, INV_ROWS = 4, 2
INV_AREA = pygame.Rect(int(WIDTH * 0.5), INTERACTIVE_BOTTOM.top, int(WIDTH * 0.5), INTERACTIVE_BOTTOM.height)

ACTION_VERBS = [
    'Give', 'Open', 'Close',
    'Pick up', 'Look at', 'Talk to',
    'Use', 'Push', 'Pull'
]

def parse_script(path: str):
    """Parse a simple script.txt format into scenes with object-oriented objects.

    Returns dict scenes[id] = {title, desc, objects: {id: GameObject}, actions: {"obj.Action": result}}
    """
    scenes = {}
    if not os.path.exists(path):
        return scenes

    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f]

    cur = None
    parsing_objects = False
    parsing_properties = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('## '):
            sid = line[3:].strip()
            cur = {'title': '', 'desc': '', 'objects': {}, 'actions': {}}
            scenes[sid] = cur
            parsing_objects = False
            parsing_properties = False
            i += 1
            continue

        if not cur:
            i += 1
            continue

        if line.startswith('title:'):
            cur['title'] = line.split(':', 1)[1].strip()
        elif line.startswith('desc:'):
            cur['desc'] = line.split(':', 1)[1].strip()
        elif line.startswith('objects:'):
            parsing_objects = True
            parsing_properties = False
            i += 1
            continue
        elif line.startswith('object_properties:'):
            parsing_objects = False
            parsing_properties = True
            i += 1
            continue
        elif parsing_objects and '.' in line and ':' in line:
            # Parse object definition: x0001. door: Porte en bois
            num_part, rest = line.split('.', 1)
            obj_id = num_part.strip()
            obj_type, name = rest.split(':', 1)
            obj_type = obj_type.strip()
            name = name.strip()

            # Create the object with basic properties
            obj = create_object(obj_type, obj_id, name)
            cur['objects'][obj_id] = obj
        elif parsing_properties and line.startswith('  ') and not ':' in line:
            # Start of object properties block
            obj_id = line.strip()
            if obj_id in cur['objects']:
                obj = cur['objects'][obj_id]
                # Parse the following indented properties
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    prop_line = lines[i].strip()
                    if ':' in prop_line:
                        prop_name, prop_value = prop_line.split(':', 1)
                        prop_name = prop_name.strip()
                        prop_value = prop_value.strip()

                        if prop_name == 'type':
                            # Type already set during object creation
                            pass
                        elif prop_name == 'position':
                            # Parse position tuple
                            if prop_value.startswith('(') and prop_value.endswith(')'):
                                coords = prop_value[1:-1].split(',')
                                obj.position = (int(coords[0].strip()), int(coords[1].strip()))
                        elif prop_name == 'locked':
                            if hasattr(obj, 'locked'):
                                obj.locked = prop_value.lower() == 'true'
                        elif prop_name == 'key_required':
                            if hasattr(obj, 'key_required'):
                                obj.key_required = prop_value
                        elif prop_name == 'items_on_top':
                            if hasattr(obj, 'items_on_top'):
                                # Parse list of items
                                if prop_value.startswith('[') and prop_value.endswith(']'):
                                    items_str = prop_value[1:-1]
                                    if items_str:
                                        obj.items_on_top = [item.strip().strip("'\"") for item in items_str.split(',')]
                        elif prop_name == 'description':
                            obj.description = prop_value
                    i += 1
                continue
        elif '.' in line and ':' in line and not parsing_objects and not parsing_properties:
            # action line: object.Action [requires: id1,id2]: result
            left, right = line.split(':', 1)
            left = left.strip()
            right = right.strip()
            requires = []
            # detect [requires: ...]
            if '[' in left and ']' in left:
                lpart, meta = left.split('[', 1)
                left = lpart.strip()
                meta = meta.split(']', 1)[0]
                if 'requires' in meta:
                    _, vals = meta.split(':', 1)
                    requires = [v.strip() for v in vals.split(',') if v.strip()]

            cur['actions'][left] = {'text': right, 'requires': requires}

        i += 1

    return scenes


def draw_layout(surface, fonts, state):
    # Backgrounds
    surface.fill((30, 30, 30))
    pygame.draw.rect(surface, (50, 80, 120), SCENE_RECT)  # scene

    # Draw scene objects as simple sprites
    scene = state.get('current_scene_obj')
    if scene:
        # Define default positions for objects
        default_positions = {
            'x0001': (SCENE_RECT.centerx + 100, SCENE_RECT.centery - 50),  # door
            'x0002': (SCENE_RECT.centerx - 100, SCENE_RECT.centery),      # table
            'x0003': (SCENE_RECT.centerx - 50, SCENE_RECT.centery - 50),  # key
        }
        
        state['_scene_sprite_rects'] = {}
        for obj_id, obj in scene.get('objects', {}).items():
            if obj.visible:
                x, y = obj.position if obj.position else default_positions.get(obj_id, (SCENE_RECT.centerx, SCENE_RECT.centery))
                
                if obj_id == 'x0001':  # door
                    # Draw door as rectangle with knob
                    door_width, door_height = 60, 100
                    rect = pygame.Rect(x - door_width//2, y - door_height//2, door_width, door_height)
                    pygame.draw.rect(surface, (160, 82, 45), (x - door_width//2, y - door_height//2, door_width, door_height))
                    # Knob
                    pygame.draw.circle(surface, (255, 215, 0), (x + door_width//2 - 10, y), 5)
                    # Draw ID above only if option is enabled
                    if state.get('show_object_ids', True):
                        id_label = fonts['small'].render(obj_id, True, (255, 255, 255))
                        surface.blit(id_label, (x - id_label.get_width()//2, y - door_height//2 - 20))
                elif obj_id == 'x0002':  # table
                    # Draw table as brown rectangle with legs
                    table_width, table_height = 80, 40
                    rect = pygame.Rect(x - table_width//2, y - table_height//2, table_width, table_height + 20)  # include legs
                    pygame.draw.rect(surface, (139, 69, 19), (x - table_width//2, y - table_height//2, table_width, table_height))
                    # Legs
                    leg_height = 20
                    pygame.draw.rect(surface, (101, 67, 33), (x - table_width//2 + 5, y + table_height//2, 5, leg_height))
                    pygame.draw.rect(surface, (101, 67, 33), (x + table_width//2 - 10, y + table_height//2, 5, leg_height))
                    # Draw ID above only if option is enabled
                    if state.get('show_object_ids', True):
                        id_label = fonts['small'].render(obj_id, True, (255, 255, 255))
                        surface.blit(id_label, (x - id_label.get_width()//2, y - table_height//2 - 20))
                elif obj_id == 'x0003':  # key
                    # Draw key as simple shape
                    rect = pygame.Rect(x - 10, y - 5, 35, 10)
                    pygame.draw.rect(surface, (255, 215, 0), (x - 10, y - 5, 20, 10))  # key head
                    pygame.draw.rect(surface, (192, 192, 192), (x + 10, y - 2, 15, 4))  # key shaft
                    pygame.draw.rect(surface, (192, 192, 192), (x + 20, y - 5, 4, 10))  # key teeth
                    # Draw ID above only if option is enabled
                    if state.get('show_object_ids', True):
                        id_label = fonts['small'].render(obj_id, True, (255, 255, 255))
                        surface.blit(id_label, (x - id_label.get_width()//2, y - 15))
                state['_scene_sprite_rects'][obj_id] = rect

    # Bottom panels
    # status line
    pygame.draw.rect(surface, (20, 20, 20), STATUS_RECT)
    # interactive bottom panels background
    pygame.draw.rect(surface, (40, 40, 40), INTERACTIVE_BOTTOM)

    # Action grid with verb labels
    ax, ay, aw, ah = ACTION_AREA
    cell_w = aw // ACTION_COLS
    cell_h = ah // ACTION_ROWS
    for r in range(ACTION_ROWS):
        for c in range(ACTION_COLS):
            idx = r * ACTION_COLS + c
            rect = pygame.Rect(ax + c * cell_w, ay + r * cell_h, cell_w - 4, cell_h - 4)
            pygame.draw.rect(surface, (70, 70, 70), rect)
            verb = ACTION_VERBS[idx]
            # Use bold font if this action is hovered
            if state.get('hovered_action') == idx:
                label = fonts['small_bold'].render(verb, True, (255, 255, 255))
            else:
                label = fonts['small'].render(verb, True, (200, 200, 200))
            surface.blit(label, (rect.x + 8, rect.y + 8))
            # store last action rects for hit detection
            state.setdefault('_action_rects', {})[idx] = rect

    # Inventory grid
    ix, iy, iw, ih = INV_AREA
    inv_cell_w = iw // INV_COLS
    inv_cell_h = ih // INV_ROWS
    for r in range(INV_ROWS):
        for c in range(INV_COLS):
            rect = pygame.Rect(ix + c * inv_cell_w, iy + r * inv_cell_h, inv_cell_w - 6, inv_cell_h - 6)
            pygame.draw.rect(surface, (80, 60, 60), rect)
            idx = r * INV_COLS + c
            inv = state.get('inventory', [])
            if idx < len(inv):
                item = inv[idx]
                surface.blit(fonts['small'].render(item['name'], True, (240, 240, 200)), (rect.x + 6, rect.y + 6))
            state.setdefault('_inv_rects', {})[idx] = rect

    # Scene text and clickable object list (left column of scene)
    sx, sy = SCENE_RECT.x + 8, SCENE_RECT.y + 8
    if scene:
        surface.blit(fonts['large'].render(scene.get('title', ''), True, (240, 240, 240)), (sx, sy))
        surface.blit(fonts['small'].render(scene.get('desc', ''), True, (220, 220, 220)), (sx, sy + 36))

        # Show object IDs indicator in top-right corner (centered)
        if state.get('show_object_ids', True):
            indicator_text = "IDs: ON (F1 pour masquer)"
            indicator_color = (100, 255, 100)  # Green when ON
        else:
            indicator_text = "IDs: OFF (F1 pour afficher)"
            indicator_color = (255, 100, 100)  # Red when OFF
        
        indicator_label = fonts['small'].render(indicator_text, True, indicator_color)
        # Center the indicator in the top area
        indicator_x = WIDTH - indicator_label.get_width() - 10
        surface.blit(indicator_label, (indicator_x, 10))

        # status line text
        status = state.get('status', '')
        msg = state.get('message', '')
        
        # Show message if available, otherwise show status
        display_text = msg if msg else status
        if display_text:
            text_surface = fonts['small'].render(display_text, True, (200, 200, 200))
            # Center the text horizontally in the status bar
            text_x = STATUS_RECT.x + (STATUS_RECT.width - text_surface.get_width()) // 2
            text_y = STATUS_RECT.y + 6
            surface.blit(text_surface, (text_x, text_y))


def handle_mouse(pos, state):
    x, y = pos

    # check action cells first: clicking an action starts a pending action
    for idx, rect in state.get('_action_rects', {}).items():
        if rect.collidepoint(pos):
            verb = ACTION_VERBS[idx]
            state['pending_action'] = verb
            state['status'] = f"{verb} (choisissez une cible)"
            state['message'] = ''
            print('Pending action set to', verb)
            return

    # check scene sprite clicks
    for obj_id, rect in state.get('_scene_sprite_rects', {}).items():
        if rect.collidepoint(pos):
            scene = state.get('current_scene_obj')
            obj = scene['objects'][obj_id]
            
            # if we have a pending action, execute it on this object
            if state.get('pending_action'):
                verb = state.pop('pending_action')
                
                # Check if the object can perform this action
                if obj.can_interact(verb, state):
                    # Use the object's perform_action method
                    msg = obj.perform_action(verb, state)
                    
                    # Special handling for pick up
                    if verb == 'Pick up' and obj_id in scene.get('objects', {}):
                        objname = obj.name
                        state.setdefault('inventory', []).append({'id': obj_id, 'name': objname})
                        # Remove from scene
                        del scene['objects'][obj_id]
                        # Remove from sprite rects
                        if obj_id in state.get('_scene_sprite_rects', {}):
                            del state['_scene_sprite_rects'][obj_id]
                else:
                    # Provide specific error messages based on the action and object state
                    if verb == "Open" and hasattr(obj, 'state') and obj.state == "open":
                        msg = f"La {obj.name} est déjà ouverte."
                    elif verb == "Close" and hasattr(obj, 'state') and obj.state == "closed":
                        msg = f"La {obj.name} est déjà fermée."
                    elif verb == "Lock" and hasattr(obj, 'locked') and obj.locked:
                        msg = f"La {obj.name} est déjà verrouillée."
                    elif verb == "Unlock" and hasattr(obj, 'locked') and not obj.locked:
                        msg = f"La {obj.name} n'est pas verrouillée."
                    elif verb == "Pick up" and hasattr(obj, 'state') and obj.state != "on_ground":
                        msg = f"La {obj.name} n'est pas disponible à ramasser."
                    else:
                        msg = f"Vous ne pouvez pas {verb.lower()} {obj.name}."
                    
                state['message'] = msg
                state['status'] = ''
                print('Action', verb, 'on', obj_id, '->', msg)
                return

            # otherwise just select the object
            state['selected_object'] = obj_id
            state['message'] = f"Objet sélectionné: {obj.name}"
            print('Selected object', obj_id)
            return

    # check inventory clicks
    for idx, rect in state.get('_inv_rects', {}).items():
        if rect.collidepoint(pos):
            inv = state.get('inventory', [])
            if idx < len(inv):
                item = inv[idx]
                # if pending action, execute it on inventory item
                if state.get('pending_action'):
                    verb = state.pop('pending_action')
                    scene = state.get('current_scene')
                    # use id for key
                    key = f"{item['id']}.{verb}"
                    msg = "Rien ne se passe."
                    if scene and key in scene.get('actions', {}):
                        action = scene['actions'][key]
                        if isinstance(action, dict):
                            reqs = action.get('requires', [])
                            inv_ids = [it['id'] for it in state.get('inventory', [])]
                            missing = [r for r in reqs if r not in inv_ids]
                            if missing:
                                msg = f"Il vous manque: {', '.join(missing)}"
                            else:
                                msg = action.get('text', '')
                        else:
                            msg = action
                    state['message'] = msg
                    state['status'] = ''
                    print('Action', verb, 'on inventory', item['name'], '->', msg)
                    return

                # clicking inventory without pending action - just print for debug
                print('Clicked inventory item:', item['name'])
            return

    # click elsewhere
    if SCENE_RECT.collidepoint(pos):
        state['message'] = ''
        state['selected_object'] = None
        # clicking background without pending action clears status
        if not state.get('pending_action'):
            state['status'] = ''
        print('Clicked scene at', pos)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Point & Click Prototype')
    clock = pygame.time.Clock()

    fonts = {
        'small': pygame.font.SysFont('Arial', 16),
        'small_bold': pygame.font.SysFont('Arial', 16, bold=True),
        'large': pygame.font.SysFont('Arial', 24),
    }

    # load script
    scenes = parse_script(os.path.join(os.path.dirname(__file__), 'script.txt'))

    # initial state
    state = {
        'inventory': [],  # Start with empty inventory
        'last_click': None,
        'scenes': scenes,
        'current_scene': scenes.get('hall'),
        'current_scene_obj': scenes.get('hall'),
        'selected_object': None,
        'message': '',
        'show_object_ids': True,  # Option to show/hide object IDs on screen
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_mouse(event.pos, state)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    # Toggle object IDs display
                    state['show_object_ids'] = not state.get('show_object_ids', True)
                    state['message'] = f"Affichage des IDs: {'activé' if state['show_object_ids'] else 'désactivé'}"
                    print(f"Object IDs display: {'ON' if state['show_object_ids'] else 'OFF'}")
            elif event.type == pygame.MOUSEMOTION:
                # update hover status
                hovered = None
                hovered_action = None
                
                # Check if hovering over action buttons
                for idx, rect in state.get('_action_rects', {}).items():
                    if rect.collidepoint(event.pos):
                        hovered_action = idx
                        break
                
                # Check scene objects (sprites only)
                if not hovered_action:
                    for obj_id, rect in state.get('_scene_sprite_rects', {}).items():
                        if rect.collidepoint(event.pos):
                            scene = state.get('current_scene_obj')
                            obj = scene['objects'][obj_id]
                            hovered = obj.name
                            break
                
                # Check inventory
                if not hovered and not hovered_action:
                    for idx, rect in state.get('_inv_rects', {}).items():
                        if rect.collidepoint(event.pos):
                            inv = state.get('inventory', [])
                            if idx < len(inv):
                                hovered = inv[idx]['name']
                                break

                # Update state
                state['hovered_action'] = hovered_action

                if hovered:
                    # if there's a pending action, show verb + name
                    if state.get('pending_action'):
                        state['status'] = f"{state['pending_action']} → {hovered}"
                    else:
                        state['status'] = hovered
                else:
                    if state.get('pending_action'):
                        state['status'] = f"{state['pending_action']} (choisissez une cible)"
                    else:
                        state['status'] = ''

        draw_layout(screen, fonts, state)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
