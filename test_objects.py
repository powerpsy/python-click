#!/usr/bin/env python3
"""
Test script for the object-oriented game system with conditions.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from objects import create_object, get_object, Door, Key, Table

def test_conditions():
    print("=== Test des conditions sur les objets ===\n")

    # Créer des objets
    door = create_object('door', 'x0001', 'Porte en bois', locked=True, key_required='x0003')
    key = create_object('key', 'x0003', 'Petite clé en laiton', description='en laiton')
    table = create_object('table', 'x0002', 'Table ancienne')

    # État du jeu (inventaire vide au départ)
    game_state = {'inventory': []}

    print("Objets créés:")
    print(f"- {door}")
    print(f"- {key}")
    print(f"- {table}")
    print()

    # Test des conditions
    print("=== Test des conditions ===")

    # 1. Tester ouverture de porte verrouillée sans clé
    print("1. Tentative d'ouverture de porte verrouillée sans clé:")
    can_open = door.can_interact("Open", game_state)
    print(f"   Peut ouvrir: {can_open}")
    if not can_open:
        print(f"   Message: {door.perform_action('Open', game_state)}")
    print()

    # 2. Ramasser la clé
    print("2. Ramassage de la clé:")
    can_pickup = key.can_interact("Pick up", game_state)
    print(f"   Peut ramasser: {can_pickup}")
    if can_pickup:
        print(f"   Message: {key.perform_action('Pick up', game_state)}")
        # Ajouter la clé à l'inventaire
        game_state['inventory'].append({'id': 'x0003', 'name': 'Petite clé en laiton'})
    print()

    # 3. Tester ouverture de porte avec clé
    print("3. Tentative d'ouverture de porte avec clé dans l'inventaire:")
    can_open_with_key = door.can_interact("Open", game_state)
    print(f"   Peut ouvrir: {can_open_with_key}")
    if can_open_with_key:
        print(f"   Message: {door.perform_action('Open', game_state)}")
    print()

    # 4. Tester ouverture de porte déjà ouverte
    print("4. Tentative d'ouverture de porte déjà ouverte:")
    can_open_again = door.can_interact("Open", game_state)
    print(f"   Peut ouvrir: {can_open_again}")
    if not can_open_again:
        print(f"   Message: {door.perform_action('Open', game_state)}")
    print()

    # 5. Tester fermeture de porte ouverte
    print("5. Fermeture de porte ouverte:")
    can_close = door.can_interact("Close", game_state)
    print(f"   Peut fermer: {can_close}")
    if can_close:
        print(f"   Message: {door.perform_action('Close', game_state)}")
    print()

    # 6. Tester fermeture de porte déjà fermée
    print("6. Tentative de fermeture de porte déjà fermée:")
    can_close_again = door.can_interact("Close", game_state)
    print(f"   Peut fermer: {can_close_again}")
    if not can_close_again:
        print(f"   Message: {door.perform_action('Close', game_state)}")
    print()

    print("=== Test terminé ===")

if __name__ == '__main__':
    test_conditions()
