import re
import os
from typing import Dict, List, Optional
from app.models.model_registry import model_registry, get_model_for_task
from app.core.logging import get_logger

logger = get_logger(__name__)

class StrategicModelSelector:
    """
    Intelligent model selection based on task type, complexity, and requirements.
    Now uses centralized ModelRegistry for consistency.
    """
    
    def __init__(self):
        # Use the centralized model registry
        self.model_registry = model_registry
        
    def select_model(self, prompt: str, explicit_model: Optional[str] = None) -> str:
        """Select the optimal model based on prompt analysis."""
        if explicit_model:
            return explicit_model
            
        prompt_lower = prompt.lower()
        
        # Define keyword patterns for different task types
        patterns = {
            "hard": ["complex", "advanced", "sophisticated", "intricate", "challenging"],
            "easy": ["simple", "basic", "quick", "easy", "straightforward", "minimal"],
            "algorithm": ["algorithm", "data structure", "sorting", "searching"],
            "testing": ["test", "unittest", "pytest", "spec", "assertion", "mock"],
            "documentation": ["documentation", "readme", "docs", "comment", "explain"],
            "writing": ["write", "content", "article", "blog", "copy", "text"],
            "database": ["database", "sql", "query", "orm", "migration", "schema"],
            "api": ["api", "endpoint", "rest", "graphql", "request", "response"],
            "frontend": ["frontend", "ui", "interface", "component", "view"],
            "backend": ["backend", "server", "service", "logic", "business"],
            "css": ["css", "style", "styling", "animation", "layout", "design"],
            "react": ["react", "jsx", "component", "hook", "state"],
            "python": ["python", "py", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "npm"],
            "refactor": ["refactor", "cleanup", "reorganize", "restructure"],
            "optimization": ["optimize", "performance", "speed", "efficient"],
            "debug": ["debug", "fix", "error", "bug", "issue", "problem"],
        }        
        # Score each category
        scores = {}
        for category, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                scores[category] = score
        
        # Select model based on highest scoring category using ModelRegistry
        if scores:
            best_category = max(scores.keys(), key=lambda k: scores[k])
            selected_model = self.model_registry.resolve_model(best_category)
            logger.info(f"Selected model '{selected_model}' for category '{best_category}'")
            return selected_model
        
        return self.model_registry.get_default_model()

# Global instance
model_selector = StrategicModelSelector()

def get_optimal_model(prompt: str, explicit_model: Optional[str] = None) -> str:
    """
    Get optimal model for a given prompt.
    Now uses centralized ModelRegistry for consistency.
    """
    return model_selector.select_model(prompt, explicit_model)
