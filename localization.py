"""
Gestionnaire de localisation pour le jeu Point & Click
Permet la traduction de tous les textes selon la langue choisie
"""

import json
import os
from typing import Dict, Any, Optional

# Variable globale pour le singleton
_localization_manager = None


class LocalizationManager:
    """Gestionnaire de localisation pour traduire les textes du jeu"""
    
    def __init__(self, default_language: str = 'fr'):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        
        # Charger les traductions disponibles
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Charger tous les fichiers de traduction disponibles"""
        if not os.path.exists(self.locales_dir):
            print(f"Warning: Locales directory not found: {self.locales_dir}")
            return
            
        for filename in os.listdir(self.locales_dir):
            if filename.endswith('.json'):
                language_code = filename[:-5]  # Remove .json extension
                filepath = os.path.join(self.locales_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.translations[language_code] = json.load(f)
                    # print(f"Loaded translations for language: {language_code}")  # Commenté pour éviter le spam
                except Exception as e:
                    print(f"Error loading translations for {language_code}: {e}")
    
    def set_language(self, language_code: str) -> bool:
        """Changer la langue courante"""
        if language_code in self.translations:
            self.current_language = language_code
            print(f"Language set to: {language_code}")
            return True
        else:
            print(f"Warning: Language {language_code} not available")
            return False
    
    def get_available_languages(self) -> list:
        """Retourner la liste des langues disponibles"""
        return list(self.translations.keys())
    
    def t(self, key: str, category: Optional[str] = None, **kwargs) -> str:
        """
        Traduire une clé donnée
        
        Args:
            key: La clé de traduction (ex: "door_locked")
            category: La catégorie optionnelle (ex: "actions", "objects")
            **kwargs: Variables à remplacer dans le texte
            
        Returns:
            Le texte traduit ou la clé si traduction non trouvée
        """
        # Essayer avec la langue courante
        text = self._get_translation(self.current_language, key, category)
        
        # Fallback vers la langue par défaut si pas trouvé
        if text is None and self.current_language != self.default_language:
            text = self._get_translation(self.default_language, key, category)
        
        # Fallback vers la clé si aucune traduction trouvée
        if text is None:
            print(f"Warning: Translation not found for key '{key}' in category '{category}'")
            return f"[{key}]"
        
        # Remplacer les variables si nécessaire
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Variable {e} not provided for translation '{key}'")
        
        return text
    
    def _get_translation(self, language: str, key: str, category: Optional[str] = None) -> Optional[str]:
        """Récupérer une traduction spécifique"""
        if language not in self.translations:
            return None
        
        translations = self.translations[language]
        
        if category:
            # Chercher dans une catégorie spécifique
            if category in translations and key in translations[category]:
                return translations[category][key]
        else:
            # Chercher dans toutes les catégories
            for cat_name, cat_data in translations.items():
                if isinstance(cat_data, dict) and key in cat_data:
                    return cat_data[key]
        
        return None
    
    def get_action_name(self, action_key: str) -> str:
        """Raccourci pour récupérer le nom d'une action"""
        return self.t(action_key, 'actions')
    
    def get_object_name(self, object_key: str) -> str:
        """Raccourci pour récupérer le nom d'un objet"""
        return self.t(object_key, 'objects')
    
    def get_description(self, desc_key: str, **kwargs) -> str:
        """Raccourci pour récupérer une description"""
        return self.t(desc_key, 'descriptions', **kwargs)
    
    def get_message(self, msg_key: str, **kwargs) -> str:
        """Raccourci pour récupérer un message"""
        return self.t(msg_key, 'messages', **kwargs)
    
    def get_ui_text(self, ui_key: str) -> str:
        """Raccourci pour récupérer un texte d'interface"""
        return self.t(ui_key, 'ui')


# Instance globale pour utilisation dans tout le jeu
_localization_manager = None

def get_localization_manager() -> LocalizationManager:
    """Récupérer l'instance globale du gestionnaire de localisation"""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager

def t(key: str, category: Optional[str] = None, **kwargs) -> str:
    """Fonction raccourcie pour la traduction"""
    return get_localization_manager().t(key, category, **kwargs)
