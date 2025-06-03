"""
🧠 Central Model Registry for Aider-MCP
Provides a single source of truth for model mappings and configuration.
"""

import os
import json
import threading
from typing import Dict, Optional, Set
from dotenv import load_dotenv
from pathlib import Path


class ModelRegistry:
    """
    Centralized model registry with dynamic configuration loading.
    
    This singleton class manages all model mappings and provides a consistent
    interface for model resolution throughout the application.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelRegistry, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._config_cache = {}
        self._last_reload_time = 0
        self._config_file_paths = []
        self._load_configuration()
        self._initialized = True
    
    def _get_config_paths(self) -> list[str]:
        """Get configuration file paths in priority order (highest to lowest)."""
        project_root = Path(__file__).parent
        return [
            str(project_root / ".env"),  # Project-level (highest priority)
            os.path.expanduser("~/.config/aider/.env"),  # Global config
            ".env"  # Current directory fallback (lowest priority)
        ]
    def _load_configuration(self):
        """Load model configuration from environment files in priority order."""
        self._config_file_paths = self._get_config_paths()
        
        # Load in reverse priority order (lowest to highest)
        for config_path in reversed(self._config_file_paths):
            if os.path.exists(config_path):
                load_dotenv(config_path, override=False)
        
        # Final load with override to ensure highest priority takes precedence
        primary_config = self._config_file_paths[0]
        if os.path.exists(primary_config):
            load_dotenv(primary_config, override=True)
        
        self._load_model_mappings()
    
    def _load_model_mappings(self):
        """Load all model mappings from environment variables."""
        self._config_cache = {
            # Complexity-based models
            "hard": os.getenv("AIDER_MODEL_HARD", "gpt-4.1-2025-04-14"),
            "complex": os.getenv("AIDER_MODEL_COMPLEX", "gemini/gemini-2.5-pro-preview-05-06"),
            "medium": os.getenv("AIDER_MODEL_MEDIUM", "gemini/gemini-2.5-flash-preview-05-20"),
            "easy": os.getenv("AIDER_MODEL_EASY", "gpt-4.1-mini-2025-04-14"),
            "simple": os.getenv("AIDER_MODEL_SIMPLE", "gpt-4.1-nano-2025-04-14"),
            
            # Task-type based models
            "writing": os.getenv("AIDER_MODEL_WRITING", "anthropic/claude-sonnet-4-20250514"),
            "documentation": os.getenv("AIDER_MODEL_DOCS", "gemini/gemini-2.5-flash-preview-05-20"),
            "testing": os.getenv("AIDER_MODEL_TESTING", "gpt-4.1-mini-2025-04-14"),
            "refactor": os.getenv("AIDER_MODEL_REFACTOR", "anthropic/claude-sonnet-4-20250514"),
            "optimization": os.getenv("AIDER_MODEL_OPTIMIZATION", "gpt-4.1-2025-04-14"),
            "algorithm": os.getenv("AIDER_MODEL_ALGORITHM", "gemini/gemini-2.5-pro-preview-05-06"),
            
            # Technology-specific models
            "react": os.getenv("AIDER_MODEL_REACT", "gpt-4.1-mini-2025-04-14"),
            "vue": os.getenv("AIDER_MODEL_VUE", "gpt-4.1-mini-2025-04-14"),
            "python": os.getenv("AIDER_MODEL_PYTHON", "gpt-4.1-mini-2025-04-14"),
            "javascript": os.getenv("AIDER_MODEL_JAVASCRIPT", "gemini/gemini-2.5-flash-preview-05-20"),
            "typescript": os.getenv("AIDER_MODEL_TYPESCRIPT", "gpt-4.1-mini-2025-04-14"),
            "css": os.getenv("AIDER_MODEL_CSS", "gemini/gemini-2.5-flash-preview-05-20"),
            "database": os.getenv("AIDER_MODEL_DATABASE", "gpt-4.1-mini-2025-04-14"),
            "api": os.getenv("AIDER_MODEL_API", "gemini/gemini-2.5-flash-preview-05-20"),
            "frontend": os.getenv("AIDER_MODEL_FRONTEND", "gemini/gemini-2.5-flash-preview-05-20"),
            "backend": os.getenv("AIDER_MODEL_BACKEND", "gpt-4.1-mini-2025-04-14"),
            
            # Performance-based models
            "fast": os.getenv("AIDER_MODEL_FAST", "gemini/gemini-2.5-flash-preview-05-20"),
            "quick": os.getenv("AIDER_MODEL_QUICK", "gpt-4.1-nano-2025-04-14"),
            "debug": os.getenv("AIDER_MODEL_DEBUG", "gpt-4.1-mini-2025-04-14"),
        }
        
        # Store default model
        self._default_model = os.getenv("AIDER_MODEL", "gpt-4.1-mini-2025-04-14")
        
        # Store override model if specified
        self._override_model = os.getenv("AIDER_MODEL") if os.getenv("AIDER_MODEL") else None

    def resolve_model(self, task_type: str, explicit_model: Optional[str] = None) -> str:
        """
        Resolve the optimal model for a given task type.
        
        Args:
            task_type: The type of task (e.g., 'complex', 'testing', 'react')
            explicit_model: Optional explicit model override
            
        Returns:
            Model identifier string
        """
        # Explicit model takes highest precedence
        if explicit_model:
            return explicit_model
        
        # Global override takes second precedence
        if self._override_model:
            return self._override_model
        
        # Task-specific model
        model = self._config_cache.get(task_type.lower())
        if model:
            return model
        
        # Fallback to default
        return self._default_model
    
    def get_all_models(self) -> Dict[str, str]:
        """Get all available model mappings."""
        return self._config_cache.copy()
    
    def get_model_categories(self) -> Set[str]:
        """Get all available model categories."""
        return set(self._config_cache.keys())
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self._default_model
    
    def reload_configuration(self) -> bool:
        """
        Reload configuration from files.
        
        Returns:
            True if configuration was reloaded, False if no changes detected
        """
        try:
            # Check if any config files have been modified
            current_time = max(
                os.path.getmtime(path) for path in self._config_file_paths 
                if os.path.exists(path)
            ) if any(os.path.exists(path) for path in self._config_file_paths) else 0
            
            if current_time > self._last_reload_time:
                self._load_configuration()
                self._last_reload_time = current_time
                return True
            
            return False
        except Exception:
            return False

    def get_configuration_info(self) -> Dict:
        """Get information about current configuration."""
        return {
            "config_files": [
                {"path": path, "exists": os.path.exists(path)} 
                for path in self._config_file_paths
            ],
            "default_model": self._default_model,
            "override_model": self._override_model,
            "total_mappings": len(self._config_cache),
            "last_reload": self._last_reload_time
        }
    
    def export_configuration(self) -> str:
        """Export current configuration as JSON."""
        config_data = {
            "default_model": self._default_model,
            "override_model": self._override_model,
            "model_mappings": self._config_cache,
            "configuration_info": self.get_configuration_info()
        }
        return json.dumps(config_data, indent=2)


# Global registry instance
model_registry = ModelRegistry()


def get_model_for_task(task_type: str, explicit_model: Optional[str] = None) -> str:
    """
    Convenience function to get model for a task type.
    
    Args:
        task_type: The type of task
        explicit_model: Optional explicit model override
        
    Returns:
        Model identifier string
    """
    return model_registry.resolve_model(task_type, explicit_model)


def reload_model_configuration() -> bool:
    """
    Reload model configuration from files.
    
    Returns:
        True if configuration was reloaded
    """
    return model_registry.reload_configuration()


def get_available_models() -> Dict[str, str]:
    """Get all available model mappings."""
    return model_registry.get_all_models()


def get_model_info() -> Dict:
    """Get information about current model configuration."""
    return model_registry.get_configuration_info()
