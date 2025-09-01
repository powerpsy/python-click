#!/usr/bin/env python3
"""
Script de test pour vérifier les flèches d'inventaire
"""

import pygame
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import Game

def test_inventory_arrows():
    """Tester les flèches d'inventaire avec plusieurs objets"""
    
    # Créer le jeu
    game = Game()
    
    # Ajouter plusieurs objets fictifs à l'inventaire pour tester les flèches
    test_items = [
        {'id': 'key', 'name': 'clé'},
        {'id': 'item1', 'name': 'objet 1'},
        {'id': 'item2', 'name': 'objet 2'},
        {'id': 'item3', 'name': 'objet 3'},
        {'id': 'item4', 'name': 'objet 4'},
        {'id': 'item5', 'name': 'objet 5'},
        {'id': 'item6', 'name': 'objet 6'},
        {'id': 'item7', 'name': 'objet 7'},
        {'id': 'item8', 'name': 'objet 8'},
        {'id': 'item9', 'name': 'objet 9'},  # Plus de 8 objets pour voir les flèches
        {'id': 'item10', 'name': 'objet 10'},
    ]
    
    game.context['inventory'] = test_items
    print(f"Inventaire de test avec {len(test_items)} objets")
    print("Les flèches devraient être visibles à gauche de l'inventaire")
    
    # Lancer le jeu
    game.run()

if __name__ == "__main__":
    test_inventory_arrows()
