import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler

from app.core.config import get_config


class MonthlyRotatingFileHandler(logging.FileHandler):
    """
    A custom file handler that automatically rotates log files monthly.
    Creates files like: base_name_2025-06.json, base_name_2025-07.json, etc.
    """

    def __init__(self, base_path, base_name, mode='a', encoding=None, delay=False):
        """
        Initialize the monthly rotating file handler.

        Args:
            base_path: Directory where log files will be stored
            base_name: Base name for log files (e.g., 'operational', 'auto_detection')
            mode: File mode (default 'a' for append)
            encoding: File encoding
            delay: Whether to delay file opening
        """
        self.base_path = Path(base_path)
        self.base_name = base_name
        self.current_month = None

        # Ensure directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize with current month file
        current_file = self._get_current_file_path()
        super().__init__(current_file, mode, encoding, delay)

    def _get_current_file_path(self):
        """Get the file path for the current month."""
        current_month = datetime.now().strftime("%Y-%m")
        return self.base_path / f"{self.base_name}_{current_month}.json"

    def emit(self, record):
        """Emit a log record, rotating to new file if month changed."""
        current_month = datetime.now().strftime("%Y-%m")

        # Check if we need to rotate to a new month
        if self.current_month != current_month:
            self.current_month = current_month

            # Close current file
            if self.stream:
                self.stream.close()
                self.stream = None

            # Update to new file path
            new_file_path = self._get_current_file_path()
            self.baseFilename = str(new_file_path)

        # Call parent emit method
        super().emit(record)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add structured data if present
        if hasattr(record, 'structured_data'):
            log_entry["data"] = record.structured_data

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Pretty print if enabled
        try:
            config = get_config()
            pretty_print = getattr(config.logging, "json_pretty_print", False)
        except Exception:
            pretty_print = False

        if pretty_print:
            return json.dumps(log_entry, indent=2)
        else:
            return json.dumps(log_entry)


def _load_logging_config():
    """
    Helper to load and cache logging config from app.core.config.get_config.
    Returns a dict with all needed logging config values with sensible defaults.
    """
    try:
        config = get_config()
        logging_cfg = getattr(config, "logging", None)
    except Exception:
        logging_cfg = None

    def get_attr(obj, attr, default):
        try:
            return getattr(obj, attr)
        except Exception:
            return default

    enable_file_logging = get_attr(logging_cfg, "enable_file_logging", True)
    enable_json_logging = get_attr(logging_cfg, "enable_json_logging", None)
    if enable_json_logging is None:
        enable_json_logging = enable_file_logging
    log_file_path = get_attr(logging_cfg, "log_file_path", "logs")
    # Extract directory part if path includes filename
    log_directory = Path(log_file_path).parent if Path(log_file_path).suffix else Path(log_file_path)
    max_file_size_mb = get_attr(logging_cfg, "log_rotation_max_size_mb", 10)
    backup_count = get_attr(logging_cfg, "log_rotation_backup_count", 5)
    enable_console_logging = get_attr(logging_cfg, "enable_console_logging", True)
    log_format = get_attr(logging_cfg, "log_format", "standard")
    log_level_operational = get_attr(logging_cfg, "log_level", "INFO")
    log_level_debug = log_level_operational  # fallback to operational level

    # Some config keys may not exist, so provide defaults for structured and pretty print
    enable_structured_data = True
    json_pretty_print = False

    return {
        "enable_file_logging": enable_file_logging,
        "enable_json_logging": enable_json_logging,
        "log_directory": log_directory,
        "max_file_size_mb": max_file_size_mb,
        "backup_count": backup_count,
        "enable_console_logging": enable_console_logging,
        "log_format": log_format,
        "log_level_operational": log_level_operational,
        "log_level_debug": log_level_debug,
        "enable_structured_data": enable_structured_data,
        "json_pretty_print": json_pretty_print,
    }


def get_logger(name, log_category="operational"):
    """
    Get a configured logger instance with configurable persistent storage and JSON support.

    Args:
        name: The name of the logger (typically __name__)
        log_category: Type of logger - "operational" or "debug"

    Returns:
        A configured logger instance with handlers based on config
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    cfg = _load_logging_config()

    # Set log levels based on category
    if log_category == "operational":
        log_level_name = cfg.get("log_level_operational", "INFO")
    else:  # debug
        log_level_name = cfg.get("log_level_debug", "DEBUG")

    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Configure standard log format
    log_format_type = cfg.get("log_format", "standard")
    if log_format_type == "json":
        log_format = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    elif log_format_type == "minimal":
        log_format = '%(levelname)s: %(message)s'
    else:  # standard
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    standard_formatter = logging.Formatter(log_format)
    json_formatter = JSONFormatter()

    # Console handler (if enabled)
    if cfg.get("enable_console_logging", True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(standard_formatter)
        logger.addHandler(console_handler)

    # Create log directory if it doesn't exist
    if cfg.get("enable_file_logging", True) or cfg.get("enable_json_logging", True):
        log_path = Path(cfg.get("log_directory", "logs"))
        log_path.mkdir(exist_ok=True)

    # Standard file handler (if enabled)
    if cfg.get("enable_file_logging", True):
        if log_category == "operational":
            log_file = log_path / "operational.log"
        elif log_category == "debug" and False:  # No config for debug file enable, keep disabled
            log_file = log_path / "debug.log"
        else:
            log_file = None

        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=cfg.get("max_file_size_mb", 10) * 1024 * 1024,
                backupCount=cfg.get("backup_count", 5)
            )
            file_handler.setFormatter(standard_formatter)
            logger.addHandler(file_handler)

    # JSON file handler (if enabled) - Phase 2A addition with monthly rotation
    if cfg.get("enable_json_logging", True) and log_category == "operational":
        # Use monthly rotating handler for operational logs
        json_handler = MonthlyRotatingFileHandler(
            base_path=log_path,
            base_name="operational"
        )
        json_handler.setFormatter(json_formatter)
        logger.addHandler(json_handler)

    return logger

def log_structured(logger, level, message, **structured_data):
    """
    Log a message with structured data in both standard and JSON formats.

    Args:
        logger: Logger instance
        level: Log level (e.g., logging.INFO)
        message: Base log message
        **structured_data: Key-value pairs to include as structured data
    """
    try:
        config = get_config()
        enable_structured = getattr(config.logging, "enable_structured_data", True)
    except Exception:
        enable_structured = True

    # Create a custom log record with structured data
    record = logger.makeRecord(
        logger.name, level, "(unknown file)", 0, message, (), None
    )

    # Add structured data to the record for JSON formatter
    if structured_data:
        record.structured_data = structured_data

    # Format message for standard formatters
    if enable_structured and structured_data:
        # Format structured data as [key=value, key=value] for standard logs
        structured_parts = [f"{k}={v}" for k, v in structured_data.items()]
        structured_str = "[" + ", ".join(structured_parts) + "]"
        full_message = f"{message} {structured_str}"
    else:
        full_message = message

    # Update the record message for standard formatters
    record.msg = full_message
    record.args = ()

    # Log the record (will be formatted differently by each handler)
    logger.handle(record)


class AutoDetectionJSONFormatter(logging.Formatter):
    """Custom JSON formatter specifically for auto-detection logs"""
    
    def format(self, record):
        # Use the auto-detection data if available, otherwise create basic structure
        if hasattr(record, 'auto_detection_data'):
            log_entry = record.auto_detection_data
        else:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "task_id": getattr(record, 'task_id', 'unknown'),
                "task_name": getattr(record, 'task_name', 'unknown'),
                "operation_type": getattr(record, 'operation_type', 'unknown'),
                "message": record.getMessage()
            }
        
        # Check if pretty formatting is enabled
        try:
            config = get_config()
            pretty_format = getattr(config.logging, "auto_detection_log_pretty", False)
        except Exception:
            pretty_format = False
        
        if pretty_format:
            return json.dumps(log_entry, indent=2)
        else:
            return json.dumps(log_entry)


def get_auto_detection_logger() -> logging.Logger:
    """
    Get or create the auto-detection logger for tracking auto-detection events and analytics.

    Returns:
        Logger instance configured for auto-detection logging
    """
    logger_name = "auto_detection"
    logger = logging.getLogger(logger_name)

    # Return existing logger if already configured
    if logger.handlers:
        return logger

    try:
        config = get_config()
        enable_auto_detection_logging = getattr(config, "enable_auto_detection_logging", True)
        log_directory = getattr(config.logging, "log_file_path", "logs")
    except Exception:
        enable_auto_detection_logging = True
        log_directory = "logs"

    if not enable_auto_detection_logging:
        # Return a no-op logger if auto-detection logging is disabled
        logger.addHandler(logging.NullHandler())
        return logger

    logger.setLevel(logging.INFO)

    # Create log directory if it doesn't exist
    Path(log_directory).mkdir(parents=True, exist_ok=True)

    # JSON file handler for auto-detection events with monthly rotation
    json_handler = MonthlyRotatingFileHandler(
        base_path=log_directory,
        base_name="auto_detection"
    )
    json_handler.setFormatter(AutoDetectionJSONFormatter())
    logger.addHandler(json_handler)

    return logger


def log_auto_detection_event(
    task_id: str,
    task_name: str,
    operation_type: str,
    model: str,
    duration_seconds: float,
    auto_detection_results: Dict[str, Any],
    performance_impact: Optional[Dict[str, Any]] = None
):
    """
    Log an auto-detection event with comprehensive analytics data.
    
    Args:
        task_id: Unique task identifier for correlation with cost logs
        task_name: Human-readable task description
        operation_type: Type of operation (code_with_ai, code_with_multiple_ai)
        model: AI model used for the operation
        duration_seconds: Total operation duration
        auto_detection_results: Results of auto-detection analysis
        performance_impact: Optional performance metrics
    """
    logger = get_auto_detection_logger()
    
    # Construct the complete auto-detection log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "task_id": task_id,
        "task_name": task_name,
        "operation_type": operation_type,
        "model": model,
        "duration_seconds": duration_seconds,
        "auto_detection_results": auto_detection_results,
        "performance_impact": performance_impact or {}
    }
    
    # Create a custom log record with the auto-detection data
    record = logger.makeRecord(
        logger.name, logging.INFO, "(auto_detection)", 0, 
        f"Auto-detection event: {task_name}", (), None
    )
    record.auto_detection_data = log_entry
    
    # Log the record
    logger.handle(record)
