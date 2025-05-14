import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_CONFIG = {
    "app": {
        "name": "AI Agent Studio",
        "version": "0.1.0",
        "debug": False,
        "save_dir": "saved_agents"
    },
    "providers": {
        "openai": {
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "default_model": "gpt-3.5-turbo"
        },
        "anthropic": {
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "default_model": "claude-3-opus-20240229"
        }
    }
}

# Global configuration object
config: Dict[str, Any] = DEFAULT_CONFIG.copy()

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from a JSON file"""
    global config
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                loaded_config = json.load(f)
                # Merge loaded config with default config
                _merge_configs(config, loaded_config)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
    
    return config

def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_configs(base[key], value)
        else:
            base[key] = value
    return base

def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get a configuration value by dot-separated path"""
    keys = key_path.split('.')
    current = config
    
    for key in keys:
        if key in current:
            current = current[key]
        else:
            return default
    
    return current

def set_config_value(key_path: str, value: Any) -> None:
    """Set a configuration value by dot-separated path"""
    keys = key_path.split('.')
    current = config
    
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
