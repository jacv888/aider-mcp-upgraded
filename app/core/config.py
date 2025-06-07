import os
import sys
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Union
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load .env file if present
load_dotenv(find_dotenv(raise_error_if_not_found=False))

def _env_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def _env_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default

def _env_float(key: str, default: float) -> float:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default

def _env_str(key: str, default: str) -> str:
    return os.getenv(key, default)

def _env_list_str(key: str, default: Optional[List[str]] = None) -> List[str]:
    if default is None:
        default = []
    val = os.getenv(key)
    if val is None:
        return default
    return [item.strip() for item in val.split(',') if item.strip()]

@dataclass
class ModelPricingEntry:
    input: float
    output: float

@dataclass
class ModelAssignments:
    default: str = field(default_factory=lambda: _env_str("AIDER_MODEL_DEFAULT", "gpt-4.1-nano"))
    # Complexity based
    complexity_hard: str = field(default_factory=lambda: _env_str("AIDER_MODEL_HARD", "claude-3-opus"))
    complexity_complex: str = field(default_factory=lambda: _env_str("AIDER_MODEL_COMPLEX", "gemini-2.5-pro"))
    complexity_medium: str = field(default_factory=lambda: _env_str("AIDER_MODEL_MEDIUM", "gemini-2.5-flash"))
    complexity_easy: str = field(default_factory=lambda: _env_str("AIDER_MODEL_EASY", "gpt-4.1-mini"))
    complexity_simple: str = field(default_factory=lambda: _env_str("AIDER_MODEL_SIMPLE", "gpt-4.1-nano"))
    # Task type based
    task_writing: str = field(default_factory=lambda: _env_str("AIDER_MODEL_WRITING", "gpt-4.1-nano"))
    task_docs: str = field(default_factory=lambda: _env_str("AIDER_MODEL_DOCS", "gemini-2.5-flash"))
    task_testing: str = field(default_factory=lambda: _env_str("AIDER_MODEL_TESTING", "gpt-4.1-mini"))
    task_refactor: str = field(default_factory=lambda: _env_str("AIDER_MODEL_REFACTOR", "gemini-2.5-pro"))
    task_translation: str = field(default_factory=lambda: _env_str("AIDER_MODEL_TRANSLATION", "gemini-2.5-flash"))
    task_analysis: str = field(default_factory=lambda: _env_str("AIDER_MODEL_ANALYSIS", "gemini-2.5-pro"))
    # Technology based
    technology_react: str = field(default_factory=lambda: _env_str("AIDER_MODEL_REACT", "gemini-2.5-pro"))
    technology_vue: str = field(default_factory=lambda: _env_str("AIDER_MODEL_VUE", "gemini-2.5-pro"))
    technology_python: str = field(default_factory=lambda: _env_str("AIDER_MODEL_PYTHON", "gemini-2.5-pro"))
    technology_javascript: str = field(default_factory=lambda: _env_str("AIDER_MODEL_JAVASCRIPT", "gemini-2.5-pro"))
    technology_java: str = field(default_factory=lambda: _env_str("AIDER_MODEL_JAVA", "gemini-2.5-pro"))
    technology_csharp: str = field(default_factory=lambda: _env_str("AIDER_MODEL_CSHARP", "gemini-2.5-pro"))
    technology_html_css: str = field(default_factory=lambda: _env_str("AIDER_MODEL_HTML_CSS", "gemini-2.5-flash"))
    # Performance based
    performance_fast: str = field(default_factory=lambda: _env_str("AIDER_MODEL_FAST", "gemini-2.5-flash"))
    performance_quick: str = field(default_factory=lambda: _env_str("AIDER_MODEL_QUICK", "gpt-4.1-mini"))
    performance_debug: str = field(default_factory=lambda: _env_str("AIDER_MODEL_DEBUG", "claude-3-opus"))

@dataclass
class ModelsConfig:
    assignments: ModelAssignments = field(default_factory=ModelAssignments)
    pricing: Dict[str, ModelPricingEntry] = field(default_factory=lambda: {
        "gpt-4.1-nano": ModelPricingEntry(input=float(os.getenv("GPT_4_1_INPUT_PRICE", 0.0005)), output=float(os.getenv("GPT_4_1_OUTPUT_PRICE", 0.0015))),
        "gpt-4.1-mini": ModelPricingEntry(input=0.001, output=0.003),
        "gemini-2.5-pro": ModelPricingEntry(input=float(os.getenv("GEMINI_PRO_INPUT_PRICE", 0.01)), output=float(os.getenv("GEMINI_PRO_OUTPUT_PRICE", 0.02))),
        "gemini-2.5-flash": ModelPricingEntry(input=0.0005, output=0.001),
        "claude-3-opus": ModelPricingEntry(input=0.015, output=0.075),
        "claude-3-sonnet": ModelPricingEntry(input=float(os.getenv("CLAUDE_SONNET_4_INPUT_PRICE", 0.003)), output=float(os.getenv("CLAUDE_SONNET_4_OUTPUT_PRICE", 0.015))),
        "claude-3-haiku": ModelPricingEntry(input=0.00025, output=0.00125),
        # Add other models and their pricing here
    })

@dataclass
class CostConfig:
    budget_limit_usd: float = field(default_factory=lambda: _env_float("BUDGET_LIMIT_USD", 100.0)) # Overall budget
    warn_threshold_usd: float = field(default_factory=lambda: _env_float("COST_WARNING_THRESHOLD", 80.0)) # Warning for overall budget
    max_cost_per_task_usd: float = field(default_factory=lambda: _env_float("MAX_COST_PER_TASK", 5.0))
    max_daily_cost_usd: float = field(default_factory=lambda: _env_float("MAX_DAILY_COST", 20.0))
    max_monthly_cost_usd: float = field(default_factory=lambda: _env_float("MAX_MONTHLY_COST", 300.0))
    enable_cost_tracking: bool = field(default_factory=lambda: _env_bool("ENABLE_COST_TRACKING", True))
    # Fallback token costs if model not in detailed pricing (per token, not per 1k tokens)
    fallback_cost_per_token_input: float = field(default_factory=lambda: _env_float("FALLBACK_COST_PER_TOKEN_INPUT", 0.000002)) # Example: $0.002/1k tokens
    fallback_cost_per_token_output: float = field(default_factory=lambda: _env_float("FALLBACK_COST_PER_TOKEN_OUTPUT", 0.000005)) # Example: $0.005/1k tokens

@dataclass
class ResilienceConfig:
    # Heartbeat
    heartbeat_enabled: bool = field(default_factory=lambda: _env_bool("RESILIENCE_HEARTBEAT_ENABLED", True))
    heartbeat_interval_seconds: int = field(default_factory=lambda: _env_int("RESILIENCE_HEARTBEAT_INTERVAL_SECONDS", 60))
    heartbeat_timeout_seconds: int = field(default_factory=lambda: _env_int("RESILIENCE_HEARTBEAT_TIMEOUT_SECONDS", 180))

    # Resource Monitoring
    resource_monitoring_enabled: bool = field(default_factory=lambda: _env_bool("RESILIENCE_RESOURCE_MONITORING_ENABLED", True))
    resource_monitoring_interval_seconds: int = field(default_factory=lambda: _env_int("RESILIENCE_RESOURCE_MONITORING_INTERVAL_SECONDS", 30))
    max_memory_percent: float = field(default_factory=lambda: _env_float("RESILIENCE_RESOURCE_MONITORING_MAX_MEMORY_PERCENT", 80.0))
    max_cpu_percent: float = field(default_factory=lambda: _env_float("RESILIENCE_RESOURCE_MONITORING_MAX_CPU_PERCENT", 90.0))
    degraded_mode_threshold: float = field(default_factory=lambda: _env_float("RESILIENCE_RESOURCE_MONITORING_DEGRADED_MODE_THRESHOLD", 70.0))

    # Task Queue
    task_queue_enabled: bool = field(default_factory=lambda: _env_bool("RESILIENCE_TASK_QUEUE_ENABLED", True))
    max_concurrent_tasks: int = field(default_factory=lambda: _env_int("RESILIENCE_TASK_QUEUE_MAX_CONCURRENT_TASKS", 5))
    queue_timeout_seconds: int = field(default_factory=lambda: _env_int("RESILIENCE_TASK_QUEUE_QUEUE_TIMEOUT_SECONDS", 10))

    # Circuit Breaker (existing)
    enable_circuit_breaker: bool = field(default_factory=lambda: _env_bool("ENABLE_CIRCUIT_BREAKER", True))
    circuit_breaker_max_failures: int = field(default_factory=lambda: _env_int("CIRCUIT_BREAKER_FAILURE_THRESHOLD", 5)) # Renamed from circuit_breaker_threshold for clarity
    circuit_breaker_reset_time_sec: int = field(default_factory=lambda: _env_int("CIRCUIT_BREAKER_RESET_TIMEOUT", 60))
    circuit_breaker_failure_rate_threshold_percent: float = field(default_factory=lambda: _env_float("CIRCUIT_BREAKER_FAILURE_RATE_THRESHOLD_PERCENT", 50.0))
    circuit_breaker_min_requests: int = field(default_factory=lambda: _env_int("CIRCUIT_BREAKER_MIN_REQUESTS", 10))

    # Auto Recovery (existing)
    enable_auto_recovery: bool = field(default_factory=lambda: _env_bool("ENABLE_AUTO_RECOVERY", True))
    auto_recovery_initial_delay_sec: int = field(default_factory=lambda: _env_int("AUTO_RECOVERY_INITIAL_DELAY_SEC", 5))
    auto_recovery_max_delay_sec: int = field(default_factory=lambda: _env_int("AUTO_RECOVERY_MAX_DELAY_SEC", 300))
    auto_recovery_backoff_multiplier: float = field(default_factory=lambda: _env_float("AUTO_RECOVERY_BACKOFF_MULTIPLIER", 2.0))

    # Request Retries (existing)
    enable_request_retries: bool = field(default_factory=lambda: _env_bool("ENABLE_REQUEST_RETRIES", True))
    max_retries: int = field(default_factory=lambda: _env_int("MAX_RETRIES", 3))
    retry_initial_delay_sec: int = field(default_factory=lambda: _env_int("RETRY_INITIAL_DELAY_SEC", 1))
    retry_max_delay_sec: int = field(default_factory=lambda: _env_int("RETRY_MAX_DELAY_SEC", 60))
    retry_backoff_factor: float = field(default_factory=lambda: _env_float("RETRY_BACKOFF_FACTOR", 2.0))

    # Performance Monitoring (existing)
    enable_performance_monitoring: bool = field(default_factory=lambda: _env_bool("ENABLE_PERFORMANCE_MONITORING", True))
    performance_monitor_window_sec: int = field(default_factory=lambda: _env_int("PERFORMANCE_MONITOR_WINDOW_SEC", 300))

    # Performance Metrics (new, from resilience.py)
    performance_metrics_enabled: bool = field(default_factory=lambda: _env_bool("RESILIENCE_PERFORMANCE_METRICS_ENABLED", True))
    performance_window_size: int = field(default_factory=lambda: _env_int("RESILIENCE_PERFORMANCE_METRICS_WINDOW_SIZE", 100))


@dataclass
class LoggingConfig:
    log_level: str = field(default_factory=lambda: _env_str("LOG_LEVEL", "INFO").upper())
    log_file_path: str = field(default_factory=lambda: _env_str("LOG_FILE_PATH", "logs/current/app_log.json"))
    log_format: str = field(default_factory=lambda: _env_str("LOG_FORMAT", "json")) # "json" or "text"
    log_rotation_policy: str = field(default_factory=lambda: _env_str("LOG_ROTATION_POLICY", "monthly")) # "daily", "weekly", "monthly", "size"
    log_rotation_max_size_mb: int = field(default_factory=lambda: _env_int("LOG_ROTATION_MAX_SIZE_MB", 100))
    log_rotation_backup_count: int = field(default_factory=lambda: _env_int("LOG_ROTATION_BACKUP_COUNT", 5))
    enable_console_logging: bool = field(default_factory=lambda: _env_bool("ENABLE_CONSOLE_LOGGING", True))
    enable_file_logging: bool = field(default_factory=lambda: _env_bool("ENABLE_FILE_LOGGING", False)) # To explicitly enable/disable file logging
    enable_auto_detection_logging: bool = field(default_factory=lambda: _env_bool("ENABLE_AUTO_DETECTION_LOGGING", True))
    auto_detection_log_file_path: str = field(default_factory=lambda: _env_str("AUTO_DETECTION_LOG_FILE_PATH", "logs/current/auto_detection_2025-06.json"))
    log_categories: List[str] = field(default_factory=lambda: _env_list_str("LOG_CATEGORIES", ["operational", "security", "cost", "debug"]))

@dataclass
class FeaturesConfig:
    enable_auto_detection: bool = field(default_factory=lambda: _env_bool("ENABLE_AUTO_DETECTION", True))
    enable_conflict_detection: bool = field(default_factory=lambda: _env_bool("ENABLE_CONFLICT_DETECTION", True))
    enable_parallel_tasks: bool = field(default_factory=lambda: _env_bool("ENABLE_PARALLEL_TASKS", True))
    default_conflict_handling: str = field(default_factory=lambda: _env_str("DEFAULT_CONFLICT_HANDLING", "auto")) # "auto", "manual", "overwrite"
    max_parallel_workers: int = field(default_factory=lambda: _env_int("MAX_CONCURRENT_TASKS", 4))
    enable_context_extraction: bool = field(default_factory=lambda: _env_bool("ENABLE_CONTEXT_EXTRACTION", True))
    enable_smart_edit: bool = field(default_factory=lambda: _env_bool("ENABLE_SMART_EDIT", True))
    enable_auto_apply_edits: bool = field(default_factory=lambda: _env_bool("ENABLE_AUTO_APPLY_EDITS", False))
    enable_usage_telemetry: bool = field(default_factory=lambda: _env_bool("ENABLE_USAGE_TELEMETRY", True)) # For product improvement analytics
    enable_debug_mode: bool = field(default_factory=lambda: _env_bool("ENABLE_DEBUG_MODE", False)) # Enables verbose logging and other debug features

@dataclass
class SystemSettingsConfig:
    cpu_threshold_percent_degraded: float = field(default_factory=lambda: _env_float("CPU_USAGE_THRESHOLD", 75.0))
    cpu_threshold_percent_critical: float = field(default_factory=lambda: _env_float("CPU_USAGE_THRESHOLD", 90.0))
    memory_threshold_percent_degraded: float = field(default_factory=lambda: _env_float("MEMORY_USAGE_THRESHOLD", 75.0))
    memory_threshold_percent_critical: float = field(default_factory=lambda: _env_float("MEMORY_USAGE_THRESHOLD", 90.0))
    task_queue_max_size: int = field(default_factory=lambda: _env_int("TASK_QUEUE_MAX_SIZE", 100))
    default_request_timeout_sec: int = field(default_factory=lambda: _env_int("DEFAULT_REQUEST_TIMEOUT_SEC", 120))
    max_context_tokens: int = field(default_factory=lambda: _env_int("MAX_CONTEXT_TOKENS", 8000))
    max_output_tokens: int = field(default_factory=lambda: _env_int("MAX_OUTPUT_TOKENS", 2000))
    max_file_size_mb_for_context: int = field(default_factory=lambda: _env_int("MAX_FILE_SIZE_MB_FOR_CONTEXT", 2))
    max_total_context_files: int = field(default_factory=lambda: _env_int("MAX_TOTAL_CONTEXT_FILES", 10))
    # API keys - it's better to load these directly where needed, but can be centralized if preferred
    # openai_api_key: Optional[str] = field(default_factory=lambda: _env_str("OPENAI_API_KEY", None)) 
    # gemini_api_key: Optional[str] = field(default_factory=lambda: _env_str("GEMINI_API_KEY", None))

@dataclass
class Config:
    models: ModelsConfig = field(default_factory=ModelsConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    resilience: ResilienceConfig = field(default_factory=ResilienceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    system: SystemSettingsConfig = field(default_factory=SystemSettingsConfig)

    # Backward compatibility methods & new helpers
    def get_model_for_task(self, task_type: str, technology: Optional[str] = None, complexity: Optional[str] = None) -> str:
        """
        Selects a model based on task type, technology, or complexity.
        Task type can be a direct key from ModelAssignments (e.g., "task_code_generation")
        or a legacy key (e.g., "complex_algorithm").
        """
        assignments = self.models.assignments
        
        # Direct match for new assignment keys
        if hasattr(assignments, task_type):
            return getattr(assignments, task_type)

        # Legacy key mapping
        legacy_map = {
            "default": assignments.default,
            "complex_algorithm": assignments.complexity_hard,
            "documentation": assignments.task_docs,
            "testing": assignments.task_testing,
            "css_styling": getattr(assignments, 'technology_html_css', assignments.default), # Or a more specific task model if defined
        }
        if task_type in legacy_map:
            return legacy_map[task_type]

        # Technology-based selection
        if technology:
            tech_key = f"technology_{technology.lower()}"
            if hasattr(assignments, tech_key):
                return getattr(assignments, tech_key)

        # Complexity-based selection
        if complexity:
            complexity_key = f"complexity_{complexity.lower()}"
            if hasattr(assignments, complexity_key):
                return getattr(assignments, complexity_key)
        
        return assignments.default


    def get_model_pricing_details(self, model_name: str) -> Optional[ModelPricingEntry]:
        return self.models.pricing.get(model_name)

    def get_model_price(self, model_name: str) -> float:
        """
        Returns a representative price for the model (e.g., output token price).
        For detailed input/output prices, use get_model_pricing_details.
        Prices are per token.
        """
        pricing_entry = self.get_model_pricing_details(model_name)
        if pricing_entry:
            return pricing_entry.output  # Default to output price
        # Fallback to generic costs if model not in detailed pricing
        # These are per token.
        return self.cost.fallback_cost_per_token_output # Or an average

    def is_feature_enabled(self, feature_name: str) -> bool:
        # Ensure feature_name matches attribute names in FeaturesConfig (e.g., "enable_auto_detection")
        if hasattr(self.features, feature_name):
            return getattr(self.features, feature_name)
        # For convenience, allow "auto_detection" to map to "enable_auto_detection"
        enable_feature_name = f"enable_{feature_name}"
        if hasattr(self.features, enable_feature_name):
            return getattr(self.features, enable_feature_name)
        return False

    def reload_env(self):
        # Reload environment variables from .env file and os.environ
        load_dotenv(find_dotenv(raise_error_if_not_found=False), override=True)
        # Re-initialize all configs to pick up new env vars
        self.models = ModelsConfig()
        self.cost = CostConfig()
        self.resilience = ResilienceConfig()
        self.logging = LoggingConfig()
        self.features = FeaturesConfig()
        self.system = SystemSettingsConfig()

    # Convenience method for testing/mocking
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        # Create Config from nested dict, allowing partial overrides
        def merge_dataclass(dc_class, data_dict_for_dc):
            # For nested dataclasses like ModelAssignments within ModelsConfig
            if hasattr(dc_class, '__dataclass_fields__'):
                field_types = {f.name: f.type for f in dc_class.__dataclass_fields__.values()}
                processed_args = {}
                for field_name, field_type in field_types.items():
                    if field_name in data_dict_for_dc:
                        field_value = data_dict_for_dc[field_name]
                        # If the field itself is a dataclass and we have a dict for it
                        if hasattr(field_type, '__dataclass_fields__') and isinstance(field_value, dict):
                            processed_args[field_name] = merge_dataclass(field_type, field_value)
                        # If field is ModelPricingEntry and value is dict
                        elif field_type == ModelPricingEntry and isinstance(field_value, dict):
                             processed_args[field_name] = ModelPricingEntry(**field_value)
                        # If field is Dict[str, ModelPricingEntry]
                        elif (hasattr(field_type, '__origin__') and field_type.__origin__ == dict and
                              hasattr(field_type, '__args__') and len(field_type.__args__) == 2 and
                              field_type.__args__[1] == ModelPricingEntry and isinstance(field_value, dict)):
                            processed_args[field_name] = {k: ModelPricingEntry(**v) if isinstance(v, dict) else v for k,v in field_value.items()}
                        else:
                            processed_args[field_name] = field_value
                return dc_class(**processed_args)
            return dc_class(**data_dict_for_dc)


        models_data = config_dict.get("models", {})
        assignments_data = models_data.get("assignments", {})
        pricing_data = models_data.get("pricing", {})
        
        # Manually construct ModelPricingEntry if pricing data is dict of dicts
        parsed_pricing = {
            name: ModelPricingEntry(**price_details) if isinstance(price_details, dict) else price_details
            for name, price_details in pricing_data.items()
        }

        models = ModelsConfig(
            assignments=merge_dataclass(ModelAssignments, assignments_data),
            pricing=parsed_pricing
        )
        
        cost = merge_dataclass(CostConfig, config_dict.get("cost", {}))
        resilience = merge_dataclass(ResilienceConfig, config_dict.get("resilience", {}))
        logging_cfg = merge_dataclass(LoggingConfig, config_dict.get("logging", {}))
        features = merge_dataclass(FeaturesConfig, config_dict.get("features", {}))
        system = merge_dataclass(SystemSettingsConfig, config_dict.get("system", {}))
        
        return cls(models=models, cost=cost, resilience=resilience, logging=logging_cfg, features=features, system=system)

# Singleton instance for global use
_global_config: Optional[Config] = None

def get_config() -> Config:
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config

def set_config(config: Config) -> None:
    global _global_config
    _global_config = config

# For backward compatibility, expose some top-level helpers
def get_model_for_task(task_type: str) -> str:
    return get_config().get_model_for_task(task_type)

def get_model_price(model_name: str) -> float:
    return get_config().get_model_price(model_name)

def is_feature_enabled(feature_name: str) -> bool:
    return get_config().is_feature_enabled(feature_name)
