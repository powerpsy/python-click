import sys
import os
import pygame

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
    """Parse a simple script.txt format into scenes.

    Returns dict scenes[id] = {title, desc, objects: {id:name}, actions: {"obj.Action": result}}
    """
    scenes = {}
    if not os.path.exists(path):
        return scenes

    with open(path, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f]

    cur = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('## '):
            sid = line[3:].strip()
            cur = {'title': '', 'desc': '', 'objects': {}, 'actions': {}}
            scenes[sid] = cur
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
            # read following indented object lines
            i += 1
            while i < len(lines) and lines[i].startswith('  '):
                ol = lines[i].strip()
                if ':' in ol:
                    oid, name = ol.split(':', 1)
                    cur['objects'][oid.strip()] = name.strip()
                i += 1
            continue
        elif '.' in line and ':' in line:
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
    scene = state.get('current_scene_obj')
    if scene:
        surface.blit(fonts['large'].render(scene.get('title', ''), True, (240, 240, 240)), (sx, sy))
        surface.blit(fonts['small'].render(scene.get('desc', ''), True, (220, 220, 220)), (sx, sy + 36))

        # list objects
        obj_y = sy + 64
        state['_scene_object_rects'] = {}
        for oid, name in scene.get('objects', {}).items():
            orect = pygame.Rect(sx, obj_y, 220, 22)
            color = (120, 120, 90) if state.get('selected_object') == oid else (90, 90, 90)
            pygame.draw.rect(surface, color, orect)
            surface.blit(fonts['small'].render(name, True, (255, 255, 220)), (orect.x + 4, orect.y + 3))
            state['_scene_object_rects'][oid] = orect
            obj_y += 28

        # status line text
        status = state.get('status', '')
        msg = state.get('message', '')
        
        # Show message if available, otherwise show status
        display_text = msg if msg else status
        if display_text:
            surface.blit(fonts['small'].render(display_text, True, (200, 200, 200)), (STATUS_RECT.x + 8, STATUS_RECT.y + 6))


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

    # check scene object clicks
    for oid, rect in state.get('_scene_object_rects', {}).items():
        if rect.collidepoint(pos):
            # if we have a pending action, execute it on this object
            if state.get('pending_action'):
                verb = state.pop('pending_action')
                scene = state.get('current_scene')
                key = f"{oid}.{verb}"
                msg = "Rien ne se passe."
                if scene and key in scene.get('actions', {}):
                    action = scene['actions'][key]
                    # action may be dict with text/requires
                    if isinstance(action, dict):
                        reqs = action.get('requires', [])
                        inv_ids = [it['id'] for it in state.get('inventory', [])]
                        missing = [r for r in reqs if r not in inv_ids]
                        if missing:
                            msg = f"Il vous manque: {', '.join(missing)}"
                        else:
                            msg = action.get('text', '')
                            if verb == 'Pick up' and oid in scene.get('objects', {}):
                                objname = scene['objects'].pop(oid)
                                state.setdefault('inventory', []).append({'id': oid, 'name': objname})
                    else:
                        msg = action
                state['message'] = msg
                state['status'] = ''
                print('Action', verb, 'on', oid, '->', msg)
                return

            # otherwise just select the object
            state['selected_object'] = oid
            state['message'] = f"Objet sélectionné: {state['current_scene_obj']['objects'][oid]}"
            print('Selected object', oid)
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
        'inventory': [{'id': 'key', 'name': 'Key'}, {'id': 'note', 'name': 'Note'}, {'id': 'coin', 'name': 'Coin'}],
        'last_click': None,
        'scenes': scenes,
        'current_scene': scenes.get('hall'),
        'current_scene_obj': scenes.get('hall'),
        'selected_object': None,
        'message': '',
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_mouse(event.pos, state)
            elif event.type == pygame.MOUSEMOTION:
                # update hover status
                hovered = None
                hovered_action = None
                
                # Check if hovering over action buttons
                for idx, rect in state.get('_action_rects', {}).items():
                    if rect.collidepoint(event.pos):
                        hovered_action = idx
                        break
                
                # Check scene objects
                if not hovered_action:
                    for oid, rect in state.get('_scene_object_rects', {}).items():
                        if rect.collidepoint(event.pos):
                            hovered = state['current_scene_obj']['objects'][oid]
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
