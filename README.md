# Point & Click Game - Système Orienté Objet

## Vue d'ensemble

Ce projet implémente un jeu point & click avec une architecture orientée objet pour la gestion des objets et de leurs états.

## Architecture

### Classes d'objets

Le système utilise une hiérarchie de classes pour différents types d'objets :

- `GameObject` : Classe de base pour tous les objets
- `Door` : Porte qui peut être ouverte, fermée, verrouillée
- `Key` : Clé qui peut être ramassée et utilisée
- `Table` : Table qui peut contenir des objets

### Identification des objets

Les objets utilisent des identifiants hexadécimaux :
- `x0001` : Porte
- `x0002` : Table
- `x0003` : Clé

### États des objets

Chaque objet peut avoir différents états :
- **Porte** : `closed`/`open`, `locked`/`unlocked`
- **Clé** : `on_ground`/`in_inventory`
- **Table** : `normal` (avec possibilité d'objets dessus)

## Format du script (script.txt)

```
## scene_name
title: Titre de la scène
desc: Description de la scène
objects:
  x0001. door: Porte en bois
  x0002. table: Table ancienne
  x0003. key: Petite clé en laiton

object_properties:
  x0001:
    type: door
    position: (500, 300)
    locked: true
    key_required: x0003
  x0002:
    type: table
    position: (300, 350)
    items_on_top: [x0003]
  x0003:
    type: key
    position: (300, 320)
    description: laiton
```

## États et conditions des objets

Le système gère automatiquement les états des objets et applique des conditions logiques :

### Porte (`Door`)
- **États** : `closed`/`open`, `locked`/`unlocked`
- **Conditions** :
  - Ne peut pas s'ouvrir si elle est déjà ouverte
  - Ne peut pas se fermer si elle est déjà fermée
  - Ne peut pas s'ouvrir si verrouillée (nécessite la clé appropriée)
  - Ne peut pas se verrouiller si elle est ouverte
  - Ne peut pas se déverrouiller si elle n'est pas verrouillée

### Clé (`Key`)
- **États** : `on_ground`/`in_inventory`
- **Conditions** :
  - Ne peut être ramassée que si elle est par terre
  - Change automatiquement d'état après ramassage

### Table (`Table`)
- **États** : `normal`
- **Conditions** :
  - Peut contenir des objets dessus (définis dans `items_on_top`)
  - Affiche la liste des objets lors de l'inspection

## Messages d'erreur contextuels

Le système fournit des messages spécifiques selon la condition qui empêche l'action :

- `"La porte est déjà ouverte."`
- `"La porte est déjà fermée."`
- `"Il vous faut la bonne clé pour ouvrir cette porte."`
- `"La clé n'est pas disponible à ramasser."`
- etc.

## Comment étendre

### Ajouter un nouveau type d'objet

1. Créer une nouvelle classe héritant de `GameObject`
2. Implémenter `can_interact()` et `perform_action()`
3. Ajouter la création dans `create_object()`

### Ajouter de nouvelles actions

1. Ajouter l'action à `ACTION_VERBS` dans `main.py`
2. Implémenter la logique dans les classes d'objets appropriées

## Contrôles

- **Clic gauche** : Interagir avec les objets ou sélectionner des actions
- **F1** : Afficher/masquer les IDs des objets à l'écran

### Indicateur d'état

En haut à droite de l'écran, un indicateur montre :
- **IDs: ON** (vert) : Les IDs des objets sont affichés
- **IDs: OFF** (rouge) : Les IDs des objets sont masqués

Appuyez sur **F1** pour basculer entre ces deux modes.
