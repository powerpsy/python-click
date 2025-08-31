"""
Configuration management
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages game configuration settings"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.defaults = {
            'window': {
                'width': 800,
                'height': 600,
                'fullscreen': False,
                'vsync': True
            },
            'audio': {
                'master_volume': 1.0,
                'music_volume': 0.7,
                'sfx_volume': 0.8,
                'mute': False
            },
            'gameplay': {
                'language': 'fr',
                'difficulty': 'normal',
                'auto_save': True,
                'save_interval': 300  # seconds
            },
            'controls': {
                'mouse_sensitivity': 1.0,
                'invert_mouse': False
            },
            'debug': {
                'show_fps': False,
                'show_hitboxes': False,
                'log_level': 'INFO'
            }
        }

        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                self._merge_config(self.defaults, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self.defaults.copy()
        else:
            self.config = self.defaults.copy()
            self.save_config()

    def _merge_config(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> None:
        """Merge loaded config with defaults"""
        self.config = defaults.copy()
        self._deep_merge(self.config, loaded)

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge two dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path"""
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})

    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """Set entire configuration section"""
        self.config[section] = values

    def to_dict(self) -> Dict[str, Any]:
        """Get copy of entire configuration"""
        return self.config.copy()
