import re
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from aider_mcp_server.atoms.logging import get_logger

# Load environment variables with MCP aider-mcp as primary source
load_dotenv()  # Load from current directory (lowest priority)
load_dotenv(os.path.expanduser("~/.config/aider/.env"))  # Load global config (medium priority)
load_dotenv("/Users/jacquesv/MCP/aider-mcp/.env", override=True)  # PRIMARY source (highest priority)

logger = get_logger(__name__)

class StrategicModelSelector:
    """
    Intelligent model selection based on task type, complexity, and requirements.
    """
    
    def __init__(self):
        self.task_models = self._load_task_models()
        self.default_model = os.getenv("AIDER_MODEL", "gpt-4o-mini")
        
    def _load_task_models(self) -> Dict[str, str]:
        """Load model mappings from environment variables."""
        return {            # Complexity-based models
            "hard": os.getenv("AIDER_MODEL_HARD", "anthropic/claude-3-5-sonnet-20241022"),
            "complex": os.getenv("AIDER_MODEL_COMPLEX", "anthropic/claude-3-5-sonnet-20241022"),
            "medium": os.getenv("AIDER_MODEL_MEDIUM", "gpt-4o"),
            "easy": os.getenv("AIDER_MODEL_EASY", "gpt-4o-mini"),
            "simple": os.getenv("AIDER_MODEL_SIMPLE", "gpt-4o-mini"),
            
            # Task-type based models
            "writing": os.getenv("AIDER_MODEL_WRITING", "gemini/gemini-2.5-pro-exp-03-25"),
            "documentation": os.getenv("AIDER_MODEL_DOCS", "gemini/gemini-2.5-pro-exp-03-25"),
            "testing": os.getenv("AIDER_MODEL_TESTING", "gpt-4o-mini"),
            "refactor": os.getenv("AIDER_MODEL_REFACTOR", "anthropic/claude-3-5-haiku-20241022"),
            "optimization": os.getenv("AIDER_MODEL_OPTIMIZATION", "anthropic/claude-3-5-haiku-20241022"),
            "algorithm": os.getenv("AIDER_MODEL_ALGORITHM", "anthropic/claude-3-5-sonnet-20241022"),
            "database": os.getenv("AIDER_MODEL_DATABASE", "gpt-4o"),
            "api": os.getenv("AIDER_MODEL_API", "anthropic/claude-3-5-haiku-20241022"),
            "frontend": os.getenv("AIDER_MODEL_FRONTEND", "gpt-4o"),
            "backend": os.getenv("AIDER_MODEL_BACKEND", "anthropic/claude-3-5-sonnet-20241022"),
            "css": os.getenv("AIDER_MODEL_CSS", "gpt-4o"),
            "react": os.getenv("AIDER_MODEL_REACT", "anthropic/claude-3-5-sonnet-20241022"),
            "python": os.getenv("AIDER_MODEL_PYTHON", "anthropic/claude-3-5-sonnet-20241022"),
            "javascript": os.getenv("AIDER_MODEL_JAVASCRIPT", "gpt-4o"),
            "fast": os.getenv("AIDER_MODEL_FAST", "anthropic/claude-3-5-haiku-20241022"),
            "debug": os.getenv("AIDER_MODEL_DEBUG", "anthropic/claude-3-5-sonnet-20241022"),
        }
    
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
        
        # Select model based on highest scoring category
        if scores:
            best_category = max(scores.keys(), key=lambda k: scores[k])
            selected_model = self.task_models.get(best_category, self.default_model)
            logger.info(f"Selected model '{selected_model}' for category '{best_category}'")
            return selected_model
        
        return self.default_model

# Global instance
model_selector = StrategicModelSelector()

def get_optimal_model(prompt: str, explicit_model: Optional[str] = None) -> str:
    return model_selector.select_model(prompt, explicit_model)
