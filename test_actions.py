#!/usr/bin/env python3
"""
Test script to demonstrate the new action system
"""

from entities.game_entities import Key, Door, Table, Box

def test_action_system():
    """Test the new allowed/forbidden action system"""
    
    print("=== TEST DU SYSTÈME D'ACTIONS ===\n")
    
    # Créer des entités de test
    key = Key("test_key", "clé de test")
    door = Door("test_door", "porte de test", locked=True, key_required="test_key")
    table = Table("test_table", "table de test")
    box = Box("test_box", "boîte de test", contents=["objet mystérieux"])
    
    entities = [
        ("Clé", key),
        ("Porte", door), 
        ("Table", table),
        ("Boîte", box)
    ]
    
    # Test context minimal
    game_context = {
        'temp_descriptions': [],
        'inventory': []
    }
    
    for entity_name, entity in entities:
        print(f"=== {entity_name.upper()} ===")
        
        print("Actions autorisées:")
        for action in entity.allowed_actions:
            print(f"  ✓ {action}")
        
        print("Actions interdites:")
        for action, message in entity.forbidden_actions.items():
            print(f"  ✗ {action}: \"{message}\"")
        
        print()

if __name__ == "__main__":
    test_action_system()
