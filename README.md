# Point & Click Game - liste des bugs à corriger

⚠️ **ATTENTION AI/COPILOT : NE JAMAIS MODIFIER CE FICHIER README.md !** 
Seul l'utilisateur humain peut juger si un point est résolu et modifier ce fichier.
L'AI ne doit en aucun cas marquer des points comme résolus ou modifier le contenu.

x. Amélioration à mettre dans le script du jeu: la clé se situe maintenant sous un pied de la table. On décrit la table comme bancale (tant que la clé est dessous). Si le joueur pousse ou tire la table alors elle se déplace et affiche la clé sur l'interface de jeu. La table a alors une description simple ("c'est une table"). On peut ramasser la clé pour ensuite déverrouiller la porte en l'utilisant.

x. Bug: Le jeu se lance mais la scene ne contient aucun objet !

x. Amélioration: l'inventaire prend tout l'espace disponible réservé. pas la peinde de tracer des boites avec des marges, il suffit de séparer l'espace en 8 cases. entre les actions et l'inventaire, tu vas prendre un peu d'espace (~30px pour afficher deux flèches haut et bas qui permettront de dérouler les objets de l'inventaire s'il y en a plus de 8)

x. bug: quand le jeu s'affiche, si on ouvre la porte, le message "la porte s'ouvre" est affiché (ne devrait pas), mais la porte reste verrouillée (ok). la table est bancale, mais quand on la pousse ou on la tire, la clé n'apparait pas donc on ne peut pas la prendre.

x. quand on ouvre la porte, l'image de la porte ouverte ne s'affiche pas. quand on pousse la table on voit la clé mais on ne peut pas la prendre. par contre on peut utliser clé sur porte, c'est fonctionnel.

x. amélioration: tous les mots des actions, tous les mots des objets, toutes les phrases de description dans le jeu, bref tout ce qui est affiché devrait être dans des fichiers spécifiques à la langue de l'utilisateur, cela permettra la traduction facilement. du coup, chaque mot ou phrase doit avoir une référence. je propose d'avoir un fichier avec les mots des actions dans <core>, un fichier avec les noms des objets dans <entities>, un fichier avec les descriptions dans <scenes> ou <entities>, à voir ce qui est le plus logique. je suis ouvert à de meilleures propositions si tu en as.

x. bug: les flèches haut et bas de l'inventaire ne sont pas affichées. il y a une place existante à gauche de l'inventaire mais elles n'existent pas.

5. quand on passe au dessus des actions sans cliquer cela indique dans la barre de status l'action mais en anglais


