"""
🧠 Central Model Registry for Aider-MCP
Provides a single source of truth for model mappings and configuration.
"""

import os
import json
import threading
from typing import Dict, List, Optional, Set
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from pathlib import Path
from app.core.config import Config # Added this import

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
        self._default_model = "gpt-4o" # Initialize with a sensible default
        self._override_model = None    # Initialize override model
        self._load_configuration()
        self._initialized = True
    
    def _get_config_paths(self) -> List[str]:
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
        
        if load_dotenv is not None:
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
        """Load all model mappings from Config class."""
        config = Config()
        assignments = config.models.assignments
        
        # Store default model first, as it's used for fallbacks
        self._default_model = getattr(assignments, "default", "gpt-4o")
        
        self._config_cache = {
            # Complexity-based models
            "hard": getattr(assignments, "complexity_hard", self._default_model),
            "complex": getattr(assignments, "complexity_complex", self._default_model),
            "medium": getattr(assignments, "complexity_medium", self._default_model),
            "easy": getattr(assignments, "complexity_easy", self._default_model),
            "simple": getattr(assignments, "complexity_simple", self._default_model),
            
            # Task-type based models
            "writing": getattr(assignments, "task_writing", self._default_model),
            "documentation": getattr(assignments, "task_docs", self._default_model),
            "testing": getattr(assignments, "task_testing", self._default_model),
            "refactor": getattr(assignments, "task_refactor", self._default_model),
            "optimization": getattr(assignments, "task_optimization", self._default_model), # Added missing task mapping
            "algorithm": getattr(assignments, "task_algorithm", self._default_model),     # Added missing task mapping
            
            # Technology-specific models (corrected names and added fallbacks)
            "react": getattr(assignments, "technology_react", self._default_model),
            "vue": getattr(assignments, "technology_vue", self._default_model),
            "python": getattr(assignments, "technology_python", self._default_model),
            "javascript": getattr(assignments, "technology_javascript", self._default_model),
            "typescript": getattr(assignments, "technology_typescript", self._default_model),
            "css": getattr(assignments, "technology_html_css", self._default_model), # Corrected to html_css
            "database": getattr(assignments, "technology_database", self._default_model),
            "api": getattr(assignments, "technology_api", self._default_model),
            "frontend": getattr(assignments, "technology_frontend", self._default_model),
            "backend": getattr(assignments, "technology_backend", self._default_model),
            
            # Performance-based models
            "fast": getattr(assignments, "performance_fast", self._default_model),
            "quick": getattr(assignments, "performance_quick", self._default_model),
            "debug": getattr(assignments, "performance_debug", self._default_model),
        }
        
        # Store override model if specified.
        # Removed non-existent 'default_override' attribute.
        # If there's another attribute for global override, it should be used here.
        # Otherwise, it remains None as initialized.
        self._override_model = None # Explicitly set to None as default_override is non-existent

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
