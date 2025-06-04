import logging
import json
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

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
        if os.getenv("LOG_JSON_PRETTY_PRINT", "false").lower() == "true":
            return json.dumps(log_entry, indent=2)
        else:
            return json.dumps(log_entry)

def get_logger(name, log_category="operational"):
    """
    Get a configured logger instance with configurable persistent storage and JSON support.
    
    Args:
        name: The name of the logger (typically __name__)
        log_category: Type of logger - "operational" or "debug"
        
    Returns:
        A configured logger instance with handlers based on .env configuration
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Load configuration from environment variables
    enable_file_storage = os.getenv("LOG_ENABLE_FILE_STORAGE", "true").lower() == "true"
    enable_json_file = os.getenv("LOG_ENABLE_JSON_FILE", "true").lower() == "true"
    log_directory = os.getenv("LOG_DIRECTORY", "logs")
    max_file_size_mb = int(os.getenv("LOG_MAX_FILE_SIZE_MB", "10"))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    enable_console = os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true"
    enable_structured = os.getenv("LOG_ENABLE_STRUCTURED_DATA", "true").lower() == "true"
    log_format_type = os.getenv("LOG_FORMAT", "standard")
    json_file_name = os.getenv("LOG_JSON_FILE_NAME", "operational.json")
    
    # Set log levels based on category
    if log_category == "operational":
        log_level = getattr(logging, os.getenv("LOG_LEVEL_OPERATIONAL", "INFO").upper())
    else:  # debug
        log_level = getattr(logging, os.getenv("LOG_LEVEL_DEBUG", "DEBUG").upper())
    
    logger.setLevel(log_level)
    
    # Configure standard log format
    if log_format_type == "json":
        log_format = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    elif log_format_type == "minimal":
        log_format = '%(levelname)s: %(message)s'
    else:  # standard
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    standard_formatter = logging.Formatter(log_format)
    json_formatter = JSONFormatter()
    
    # Console handler (if enabled)
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(standard_formatter)
        logger.addHandler(console_handler)
    
    # Create log directory if it doesn't exist
    if enable_file_storage or enable_json_file:
        log_path = Path(log_directory)
        log_path.mkdir(exist_ok=True)
    
    # Standard file handler (if enabled)
    if enable_file_storage:
        if log_category == "operational":
            log_file = log_path / "operational.log"
        elif log_category == "debug" and os.getenv("LOG_ENABLE_DEBUG_FILE", "false").lower() == "true":
            log_file = log_path / "debug.log"
        else:
            log_file = None
        
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size_mb * 1024 * 1024,
                backupCount=backup_count
            )
            file_handler.setFormatter(standard_formatter)
            logger.addHandler(file_handler)
    
    # JSON file handler (if enabled) - Phase 2A addition
    if enable_json_file and log_category == "operational":
        json_log_file = log_path / json_file_name
        json_handler = RotatingFileHandler(
            json_log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count
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
    enable_structured = os.getenv("LOG_ENABLE_STRUCTURED_DATA", "true").lower() == "true"
    
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
