# Point & Click Game

Jeu d'aventure pointer-cliquer utilisant une architecture modulaire moderne avec BaseEntity.

## 🚀 Démarrage Rapide

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement du jeu
python main.py
```

## 📁 Architecture

```
python-click/
├── core/                    # Noyau du jeu
│   ├── game.py             # Classe principale Game
│   ├── scene_manager.py    # Gestionnaire de scènes
│   ├── event_system.py     # Système d'événements
│   └── renderer.py         # Système de rendu
├── scenes/                 # Gestion des scènes
│   ├── scene.py            # Classe Scene et logique de rendu
│   └── __init__.py
├── entities/               # Système d'entités
│   ├── base_entity.py      # Classe de base pour les entités
│   ├── game_entities.py    # Entités du jeu (Door, Key, Table)
│   └── __init__.py
├── ui/                     # Interface utilisateur
│   ├── interface.py        # Interface principale
│   ├── notifications.py    # Système de notifications
│   ├── inventory.py        # Gestion d'inventaire
│   └── __init__.py
├── utils/                  # Utilitaires
│   ├── config.py           # Configuration
│   ├── logger.py           # Logging
│   └── __init__.py
├── main.py                 # Point d'entrée principal
├── script.txt              # Script d'exemple (optionnel)
└── requirements.txt        # Dépendances Python
```

## ✨ Fonctionnalités

### 🎮 Gameplay
- **Entités Interactives** : Portes, clés, tables avec comportements spécifiques
- **Système d'Inventaire** : Ramassage et utilisation d'objets
- **Actions Contextuelles** : Regarder, Prendre, Utiliser, Ouvrir, etc.
- **Notifications** : Messages au-dessus des objets

### 🏗️ Architecture
- **Modulaire** : Séparation claire des responsabilités
- **Évolutive** : Facilement extensible avec de nouvelles entités
- **Événements** : Système de communication propre
- **Configuration** : Paramètres persistants
- **Logging** : Système de débogage intégré

## 🎯 Utilisation

### Contrôles
- **Clic gauche** : Interagir avec les objets
- **Actions** : Sélectionner une action puis cliquer sur un objet
- **I** : Basculer l'inventaire
- **Échap** : Quitter le jeu

### Ajouter de Nouvelles Entités

```python
from entities import BaseEntity

class NewEntity(BaseEntity):
    def __init__(self, entity_id, name, position, **properties):
        super().__init__(entity_id, name, position, **properties)

    def on_click(self, action, context):
        if action == "Regarder":
            return f"Vous regardez {self.name}"
        return super().on_click(action, context)
```

## 📋 Prérequis

- Python 3.8+
- Pygame 2.0+

## 🔧 Développement

Le projet utilise une architecture modulaire permettant une extension facile :

1. **Scenes** : Gestion des scènes dans `scenes/scene.py`
2. **Entités** : Héritent de `BaseEntity` dans `entities/base_entity.py`
3. **UI** : Composants dans le dossier `ui/`
4. **Core** : Logique de jeu dans `core/`
5. **Utils** : Outils et configuration dans `utils/`

## � Notes

- Le fichier `script.txt` est optionnel et sert d'exemple
- Le jeu crée automatiquement une scène par défaut s'il n'existe pas
- Architecture optimisée pour la maintenabilité et l'extensibilité
- Implémentation complète du moteur de script
- Système de sauvegarde/chargement

### 📋 Planifié

- Système de quêtes
- Dialogues avec les PNJ
- Éditeur de niveaux intégré
- Support pour multiples langues
- Système de sons et musique

## 🛠️ Utilisation

### Installation

```bash
pip install -r requirements.txt
```

### Lancement

Pour tester la nouvelle architecture modulaire :
```bash
python example_usage.py
```

Pour utiliser l'ancien système :
```bash
python main.py
```

## 📖 Documentation des Modules

### Core Module

#### Game
Classe principale qui coordonne tous les systèmes du jeu.

```python
from core import Game

game = Game(renderer, event_system, scene_manager, interface, notifications)
game.run()
```

#### SceneManager
Gère les différentes scènes/locations du jeu.

```python
from core import SceneManager

scene_manager = SceneManager()
scene_manager.set_scene(my_scene)
```

#### EventSystem
Système d'événements pour la communication entre composants.

```python
from core import EventSystem

event_system = EventSystem()
event_system.subscribe('entity_clicked', my_handler)
```

#### Renderer
Abstraction du système de rendu.

```python
from core import Renderer

renderer = Renderer(width, height, title)
renderer.clear()
renderer.present()
```

### Entities Module

#### BaseEntity
Classe de base pour tous les objets interactifs du jeu.

```python
from entities import BaseEntity

class MyEntity(BaseEntity):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.name = "My Object"

    def on_click(self, action=None):
        return f"You clicked on {self.name}"
```

### UI Module

#### GameInterface
Interface utilisateur principale avec barre d'actions et inventaire.

```python
from ui import GameInterface

interface = GameInterface()
interface.render(renderer, context)
```

#### NotificationSystem
Gère les messages temporaires au-dessus des objets.

```python
from ui.notifications import NotificationSystem

notifications = NotificationSystem()
notifications.add_action_message("Door opened!", (x, y))
```

#### Inventory
Système de gestion d'inventaire.

```python
from ui.inventory import Inventory, InventoryItem

inventory = Inventory()
key = InventoryItem("key", "Clé", "Une clé en métal")
inventory.add_item(key)
```

### Resources Module

#### ResourceManager
Gestion centralisée des ressources du jeu.

```python
from resources.manager import ResourceManager

resources = ResourceManager()
resources.load_image("door", "images/door.png")
image = resources.get_image("door")
```

### Utils Module

#### ConfigManager
Gestion de la configuration du jeu.

```python
from utils.config import ConfigManager

config = ConfigManager()
volume = config.get("audio.master_volume")
config.set("audio.master_volume", 0.8)
```

#### Logger
Système de logging pour le débogage.

```python
from utils.logger import get_logger

logger = get_logger()
logger.info("Game started")
logger.error("Something went wrong", exc_info=True)
```

## 🎮 Création d'une Nouvelle Scène

```python
from core import SceneManager
from entities import BaseEntity

class MyScene:
    def __init__(self, game):
        self.game = game
        self.entities = []
        self.setup_entities()

    def setup_entities(self):
        # Créer des entités pour la scène
        door = MyDoorEntity(100, 100)
        self.entities.append(door)

    def update(self, delta_time):
        for entity in self.entities:
            entity.update(delta_time)

    def render(self, renderer):
        # Rendu de la scène
        for entity in self.entities:
            entity.render(renderer)

    def handle_click(self, pos, action=None):
        for entity in self.entities:
            if entity.rect.collidepoint(pos):
                message = entity.on_click(action)
                if message:
                    self.game.notification_system.add_action_message(
                        message, (entity.rect.centerx, entity.rect.top)
                    )
                return True
        return False

# Utilisation
scene_manager = SceneManager()
my_scene = MyScene(game)
scene_manager.set_scene(my_scene)
```

## 🔧 Extension du Jeu

### Ajouter un Nouveau Type d'Entité

1. Créer une classe héritant de `BaseEntity`
2. Implémenter les méthodes `on_click`, `update`, `render`
3. Ajouter à une scène

### Ajouter une Nouvelle Action

1. Modifier `GameInterface.action_verbs`
2. Gérer la nouvelle action dans les entités
3. Mettre à jour l'interface utilisateur

### Ajouter un Nouveau Système

1. Créer un nouveau module dans le dossier approprié
2. L'intégrer dans la classe `Game`
3. Mettre à jour les dépendances

## 🆕 **Entités du Jeu (NOUVEAU)**

Les classes existantes (`Door`, `Key`, `Table`) utilisent la nouvelle architecture `BaseEntity`. Voici comment utiliser les entités du jeu :

### Classes Disponibles

#### `Door`
```python
from entities import Door

door = Door(
    entity_id="door_001",
    name="Porte en bois",
    position=(300, 200),
    locked=True,
    key_required="key_001"
)
```

#### `Key`
```python
from entities import Key

key = Key(
    entity_id="key_001",
    name="Clé en laiton",
    position=(500, 350)
)
```

#### `Table`
```python
from entities import Table

table = Table(
    entity_id="table_001",
    name="Table massive",
    position=(150, 300),
    items_on_top=["key_001"]
)
```

### Utilisation dans le Jeu

```python
# Créer des entités
door = Door("door_001", "Porte", position=(300, 200), locked=True)
key = Key("key_001", "Clé", position=(500, 350))
table = Table("table_001", "Table", position=(150, 300))

# Ajouter à une scène
scene.entities.extend([door, key, table])

# Gestion des interactions
def handle_click(pos, action):
    for entity in scene.entities:
        if entity.bounding_box.collidepoint(pos):
            context = {'inventory': player_inventory, 'current_scene_obj': scene}
            message = entity.on_click(action, context)
            if message:
                notification_system.add_action_message(message, entity.position)
            return True
    return False
```

### Différences avec l'Ancien Système

| Ancien (GameObject) | Nouveau (BaseEntity) |
|-------------------|-------------------|
| `obj.perform_action(action, game_state)` | `entity.on_click(action, context)` |
| `obj.position` | `entity.position` (tuple) |
| `obj.bounding_box` | `entity.bounding_box` (pygame.Rect) |
| Messages dans `game_state['message']` | Messages automatiques au-dessus des objets |
| `obj.visible` | `entity.visible` |
| `obj.interactive` | `entity.interactive` |

### Tester les Entités

```bash
python main.py
```

Cet exemple montre :
- ✅ Porte verrouillée nécessitant une clé
- ✅ Clé à ramasser et utiliser
- ✅ Table avec objets dessus
- ✅ Messages contextuels au-dessus des objets
- ✅ Intégration complète avec l'architecture modulaire

## 📝 Scripts

Le jeu utilise un système de scripts JSON pour définir le contenu. Exemple :

```json
{
  "scenes": [
    {
      "id": "room1",
      "name": "Salle principale",
      "entities": [
        {
          "type": "door",
          "x": 300,
          "y": 200,
          "properties": {
            "name": "Porte",
            "locked": false
          }
        }
      ]
    }
  ]
}
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 📞 Support

Pour des questions ou des problèmes, créez une issue sur GitHub.