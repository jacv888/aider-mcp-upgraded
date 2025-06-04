"""
💰 Cost Manager for Aider-MCP
Provides token counting, cost estimation, and budget management.
"""

import os
import re
import json
import logging
import tiktoken
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from app.core.logging import get_logger, log_structured

# Get logger
logger = get_logger(__name__, "operational")

@dataclass
class CostEstimate:
    """Cost estimation result."""
    input_tokens: int
    estimated_output_tokens: int
    total_tokens: int
    input_cost: float
    estimated_output_cost: float
    total_cost: float
    model: str
    currency: str = "USD"

@dataclass
class TaskCostResult:
    """Actual cost result after task execution."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    model: str
    duration_seconds: float
    timestamp: datetime
    task_id: str
    task_name: str = "Unnamed Task"
    currency: str = "USD"

class CostManager:
    """
    Centralized cost management for AI model usage.
    
    Features:
    - Token counting for different models
    - Pre-flight cost estimation
    - Real-time usage tracking
    - Budget enforcement
    - Cost analytics and reporting
    """
    
    def __init__(self):
        self.pricing_db = self._load_pricing_database()
        self.token_encoders = {}
        self.budget_limits = self._load_budget_configuration()
        
        # Load persistent cost history
        try:
            from app.cost.cost_storage import cost_storage
            self.cost_history = cost_storage.load_cost_history()
            self.cost_storage = cost_storage
        except ImportError:
            # Fallback to memory-only storage
            self.cost_history = []
            self.cost_storage = None
        
    def _load_pricing_database(self) -> Dict[str, Dict[str, float]]:
        """Load model pricing information from environment variables."""
        return {
            # OpenAI GPT-4.1 models
            "gpt-4.1-2025-04-14": {
                "input": float(os.getenv("GPT_4_1_INPUT_PRICE", "30.00")),
                "output": float(os.getenv("GPT_4_1_OUTPUT_PRICE", "60.00"))
            },
            "gpt-4.1-mini-2025-04-14": {
                "input": float(os.getenv("GPT_4_1_MINI_INPUT_PRICE", "0.15")),
                "output": float(os.getenv("GPT_4_1_MINI_OUTPUT_PRICE", "0.60"))
            },
            "gpt-4.1-nano-2025-04-14": {
                "input": float(os.getenv("GPT_4_1_NANO_INPUT_PRICE", "0.05")),
                "output": float(os.getenv("GPT_4_1_NANO_OUTPUT_PRICE", "0.20"))
            },
            
            # Gemini models
            "gemini/gemini-2.5-pro-preview-05-06": {
                "input": float(os.getenv("GEMINI_PRO_INPUT_PRICE", "2.50")),
                "output": float(os.getenv("GEMINI_PRO_OUTPUT_PRICE", "10.00"))
            },
            "gemini/gemini-2.5-flash-preview-05-20": {
                "input": float(os.getenv("GEMINI_FLASH_INPUT_PRICE", "0.20")),
                "output": float(os.getenv("GEMINI_FLASH_OUTPUT_PRICE", "0.40"))
            },
            
            # Anthropic Claude models
            "anthropic/claude-sonnet-4-20250514": {
                "input": float(os.getenv("CLAUDE_SONNET_4_INPUT_PRICE", "15.00")),
                "output": float(os.getenv("CLAUDE_SONNET_4_OUTPUT_PRICE", "75.00"))
            },
            "claude-sonnet-4-20250514": {
                "input": float(os.getenv("CLAUDE_SONNET_4_INPUT_PRICE", "15.00")),
                "output": float(os.getenv("CLAUDE_SONNET_4_OUTPUT_PRICE", "75.00"))
            }
        }    
    def _load_budget_configuration(self) -> Dict[str, float]:
        """Load budget limits from environment variables."""
        return {
            "max_cost_per_task": float(os.getenv("MAX_COST_PER_TASK", "5.00")),
            "max_daily_cost": float(os.getenv("MAX_DAILY_COST", "50.00")),
            "max_monthly_cost": float(os.getenv("MAX_MONTHLY_COST", "500.00")),
            "warning_threshold": float(os.getenv("COST_WARNING_THRESHOLD", "1.00"))
        }
    
    def get_token_encoder(self, model: str):
        """Get or create token encoder for model."""
        if model not in self.token_encoders:
            try:
                # Try to get model-specific encoder
                if "gpt" in model.lower():
                    self.token_encoders[model] = tiktoken.encoding_for_model("gpt-4")
                else:
                    # Fallback to general encoder
                    self.token_encoders[model] = tiktoken.get_encoding("cl100k_base")
            except Exception:
                # Ultimate fallback
                self.token_encoders[model] = tiktoken.get_encoding("cl100k_base")
        
        return self.token_encoders[model]
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for specific model."""
        try:
            encoder = self.get_token_encoder(model)
            return len(encoder.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed for model {model}: {e}")
            # Rough estimate: ~4 characters per token
            return len(text) // 4
    
    def estimate_output_tokens(self, input_tokens: int, task_type: str = "general") -> int:
        """Estimate output tokens based on input and task type."""
        # Base ratios for different task types
        output_ratios = {
            "code_generation": 2.0,    # Code tasks often generate more output
            "documentation": 1.5,      # Documentation is moderately verbose
            "testing": 1.2,           # Tests are usually concise
            "refactor": 0.8,          # Refactoring often reduces code
            "debug": 0.5,             # Debug fixes are usually small
            "simple": 0.3,            # Simple tasks have minimal output
            "general": 1.0            # Default ratio
        }
        
        ratio = output_ratios.get(task_type, 1.0)
        estimated = int(input_tokens * ratio)
        
        # Apply reasonable bounds
        min_tokens = max(100, input_tokens // 10)  # At least 100 tokens or 10% of input
        max_tokens = min(4000, input_tokens * 3)   # At most 4000 tokens or 3x input
        
        return max(min_tokens, min(estimated, max_tokens))
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> Tuple[float, float, float]:
        """Calculate cost for token usage."""
        # Get pricing for model (fallback to expensive model if unknown)
        pricing = self.pricing_db.get(model, {"input": 30.0, "output": 60.0})
        
        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return input_cost, output_cost, total_cost
    
    def estimate_task_cost(self, prompt: str, files_content: List[str], 
                          model: str, task_type: str = "general") -> CostEstimate:
        """Estimate cost for a task before execution."""
        # Count input tokens
        full_input = prompt + "\n" + "\n".join(files_content)
        input_tokens = self.count_tokens(full_input, model)
        
        # Estimate output tokens
        estimated_output = self.estimate_output_tokens(input_tokens, task_type)
        total_tokens = input_tokens + estimated_output
        
        # Calculate costs
        input_cost, estimated_output_cost, total_cost = self.calculate_cost(
            input_tokens, estimated_output, model
        )
        
        return CostEstimate(
            input_tokens=input_tokens,
            estimated_output_tokens=estimated_output,
            total_tokens=total_tokens,
            input_cost=input_cost,
            estimated_output_cost=estimated_output_cost,
            total_cost=total_cost,
            model=model
        )
    
    def check_budget_limits(self, estimated_cost: float) -> Tuple[bool, str]:
        """Check if estimated cost exceeds budget limits."""
        max_task_cost = self.budget_limits["max_cost_per_task"]
        warning_threshold = self.budget_limits["warning_threshold"]
        
        if estimated_cost > max_task_cost:
            return False, f"Task cost ${estimated_cost:.4f} exceeds limit ${max_task_cost:.2f}"
        
        if estimated_cost > warning_threshold:
            return True, f"High cost warning: ${estimated_cost:.4f} (threshold: ${warning_threshold:.2f})"
        
        return True, ""
    
    def record_task_cost(self, task_id: str, input_tokens: int, output_tokens: int,
                        model: str, duration_seconds: float, task_name: str = "Unnamed Task") -> TaskCostResult:
        """Record actual cost after task execution."""
        input_cost, output_cost, total_cost = self.calculate_cost(
            input_tokens, output_tokens, model
        )
        
        result = TaskCostResult(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            model=model,
            duration_seconds=duration_seconds,
            timestamp=datetime.now(),
            task_id=task_id,
            task_name=task_name
        )
        
        # Store in history
        self.cost_history.append(result)
        
        # Save to persistent storage
        if self.cost_storage:
            try:
                self.cost_storage.save_cost_history(self.cost_history)
            except Exception as e:
                if os.getenv("ENABLE_COST_LOGGING", "false").lower() == "true":
                    logger.warning(f"Failed to save cost data: {e}")
        
        # Log the cost only if logging is enabled
        if os.getenv("ENABLE_COST_LOGGING", "false").lower() == "true":
            log_structured(logger, logging.INFO, "Task cost calculated",
                          task_id=task_id,
                          total_cost=f"${total_cost:.4f}",
                          input_tokens=input_tokens,
                          output_tokens=output_tokens,
                          model=model)
        
        return result
    
    def get_cost_summary(self, days: int = 7) -> Dict:
        """Get cost summary for specified period."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_costs = [c for c in self.cost_history if c.timestamp >= cutoff_date]
        
        if not recent_costs:
            return {"total_cost": 0, "task_count": 0, "average_cost": 0}
        
        total_cost = sum(c.total_cost for c in recent_costs)
        total_tokens = sum(c.total_tokens for c in recent_costs)
        
        return {
            "total_cost": total_cost,
            "task_count": len(recent_costs),
            "average_cost": total_cost / len(recent_costs),
            "total_tokens": total_tokens,
            "period_days": days,
            "cost_by_model": self._group_costs_by_model(recent_costs)
        }
    
    def _group_costs_by_model(self, cost_results: List[TaskCostResult]) -> Dict[str, Dict]:
        """Group cost results by model."""
        model_costs = {}
        for result in cost_results:
            if result.model not in model_costs:
                model_costs[result.model] = {
                    "total_cost": 0,
                    "task_count": 0,
                    "total_tokens": 0
                }
            
            model_costs[result.model]["total_cost"] += result.total_cost
            model_costs[result.model]["task_count"] += 1
            model_costs[result.model]["total_tokens"] += result.total_tokens
        
        return model_costs
    
    def export_cost_report(self, days: int = 30) -> str:
        """Export detailed cost report as JSON."""
        summary = self.get_cost_summary(days)
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period_days": days,
            "summary": summary,
            "budget_limits": self.budget_limits,
            "pricing_database": self.pricing_db
        }
        
        return json.dumps(report, indent=2, default=str)


# Global cost manager instance
cost_manager = CostManager()


# Convenience functions
def estimate_cost(prompt: str, files_content: List[str], model: str, 
                 task_type: str = "general") -> CostEstimate:
    """Estimate cost for a task."""
    return cost_manager.estimate_task_cost(prompt, files_content, model, task_type)


def check_budget(estimated_cost: float) -> Tuple[bool, str]:
    """Check if cost is within budget."""
    return cost_manager.check_budget_limits(estimated_cost)


def generate_task_name(prompt: str) -> str:
    """Generate a descriptive task name from the prompt."""
    import re
    
    # Clean and truncate the prompt
    clean_prompt = re.sub(r'[^\w\s]', '', prompt.lower())
    words = clean_prompt.split()
    
    # Extract key words (skip common words)
    skip_words = {'create', 'make', 'build', 'write', 'generate', 'add', 'implement', 'a', 'an', 'the', 'for', 'with', 'that', 'simple', 'basic'}
    key_words = [word for word in words[:10] if word not in skip_words and len(word) > 2]
    
    # Generate name
    if key_words:
        task_name = ' '.join(key_words[:4])  # Take first 4 meaningful words
        # Capitalize first letter of each word
        task_name = ' '.join(word.capitalize() for word in task_name.split())
        return task_name[:50]  # Limit to 50 characters
    else:
        return "Coding Task"


def record_cost(task_id: str, input_tokens: int, output_tokens: int,
               model: str, duration_seconds: float, task_name: str = "Unnamed Task") -> TaskCostResult:
    """Record actual task cost."""
    return cost_manager.record_task_cost(task_id, input_tokens, output_tokens, 
                                        model, duration_seconds, task_name)


def get_cost_summary(days: int = 7) -> Dict:
    """Get cost summary for period."""
    return cost_manager.get_cost_summary(days)
