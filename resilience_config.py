import os
import json
import logging
from typing import Dict, Any, Optional, Union

# Configure a logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("AIDER_MCP_RESILIENCE_LOG_LEVEL", "INFO").upper())
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class ResilienceConfig:
    """
    Manages configuration settings for aider-mcp resilience features.

    This class provides:
    - Default configuration values for various resilience features.
    - Loading of settings from environment variables with fallbacks to defaults.
    - Configuration validation to ensure settings are within acceptable ranges/types.
    - Runtime updates for dynamic configuration changes.
    - Export and import functionality for saving/loading configurations.
    - Detailed comments explaining each setting.
    - Predefined configuration profiles (development, production, high-load).
    """

    # 1. Default configuration values for all resilience features
    # These are the base settings if no environment variables or profiles are specified.
    DEFAULT_CONFIG: Dict[str, Any] = {
        "connection_health": {
            # Interval in seconds for checking the health of external connections/services.
            "HEALTH_CHECK_INTERVAL_SECONDS": 30,
            # Timeout in seconds for a single health check attempt.
            "HEALTH_CHECK_TIMEOUT_SECONDS": 5,
            # Number of consecutive health check failures before a connection is considered unhealthy.
            "MAX_CONSECUTIVE_FAILURES": 3,
        },
        "resource_usage": {
            # CPU usage threshold (percentage) above which a warning might be triggered or
            # certain operations might be throttled.
            "CPU_THRESHOLD_PERCENT": 80.0,
            # Memory usage threshold (percentage) above which a warning might be triggered or
            # certain operations might be throttled.
            "MEMORY_THRESHOLD_PERCENT": 85.0,
            # Disk usage threshold (percentage) above which a warning might be triggered.
            "DISK_THRESHOLD_PERCENT": 90.0,
        },
        "task_queue": {
            # Maximum number of tasks allowed in the pending queue.
            # Prevents overwhelming the system with too many concurrent requests.
            "MAX_PENDING_TASKS": 100,
            # Maximum time in seconds a task is allowed to run before being considered timed out.
            "TASK_TIMEOUT_SECONDS": 300,  # 5 minutes
        },
        "circuit_breaker": {
            # Number of failures within a rolling window that will trip the circuit breaker.
            "FAILURE_THRESHOLD": 5,
            # Time in seconds the circuit breaker stays open before attempting to half-open.
            "RECOVERY_TIMEOUT_SECONDS": 60,
            # Number of successful requests allowed in the half-open state to close the circuit.
            "HALF_OPEN_TEST_COUNT": 2,
            # The duration in seconds for the rolling window used to count failures.
            "ROLLING_WINDOW_SECONDS": 30,
        },
        "connection_pool": {
            # Maximum number of connections in the pool.
            "MAX_SIZE": 10,
            # Maximum time in seconds a connection can remain idle in the pool before being closed.
            "MAX_IDLE_SECONDS": 300,  # 5 minutes
        },
        "logging": {
            # The minimum logging level to output messages (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
            "LOG_LEVEL": "INFO",
        },
        "recovery_timeouts": {
            # Maximum number of retry attempts for failed operations.
            "RETRY_ATTEMPTS": 3,
            # Factor by which the delay between retries increases (e.g., 2 means 1s, 2s, 4s).
            "RETRY_BACKOFF_FACTOR": 2.0,
            # Maximum delay in seconds between retry attempts.
            "RETRY_MAX_DELAY_SECONDS": 60,
        },
    }

    # 7. Configuration profiles (development, production, high-load)
    # These profiles override specific default settings for different environments.
    PROFILES: Dict[str, Dict[str, Any]] = {
        "development": {
            "connection_health": {
                "HEALTH_CHECK_INTERVAL_SECONDS": 10,
                "MAX_CONSECUTIVE_FAILURES": 1,
            },
            "task_queue": {
                "MAX_PENDING_TASKS": 10,
                "TASK_TIMEOUT_SECONDS": 60,
            },
            "circuit_breaker": {
                "FAILURE_THRESHOLD": 2,
                "RECOVERY_TIMEOUT_SECONDS": 10,
            },
            "logging": {
                "LOG_LEVEL": "DEBUG",
            },
            "recovery_timeouts": {
                "RETRY_ATTEMPTS": 1,
                "RETRY_MAX_DELAY_SECONDS": 10,
            }
        },
        "production": {
            # Production settings are generally more conservative and robust.
            # Many defaults are suitable, but some might be tightened.
            "connection_health": {
                "HEALTH_CHECK_INTERVAL_SECONDS": 60,
                "MAX_CONSECUTIVE_FAILURES": 5,
            },
            "resource_usage": {
                "CPU_THRESHOLD_PERCENT": 90.0,
                "MEMORY_THRESHOLD_PERCENT": 95.0,
            },
            "task_queue": {
                "MAX_PENDING_TASKS": 200,
                "TASK_TIMEOUT_SECONDS": 600, # 10 minutes
            },
            "circuit_breaker": {
                "FAILURE_THRESHOLD": 10,
                "RECOVERY_TIMEOUT_SECONDS": 120,
            },
            "logging": {
                "LOG_LEVEL": "INFO",
            },
        },
        "high-load": {
            # Settings optimized for high throughput and resilience under heavy load.
            "connection_health": {
                "HEALTH_CHECK_INTERVAL_SECONDS": 15,
                "MAX_CONSECUTIVE_FAILURES": 2,
            },
            "resource_usage": {
                "CPU_THRESHOLD_PERCENT": 95.0,
                "MEMORY_THRESHOLD_PERCENT": 98.0,
            },
            "task_queue": {
                "MAX_PENDING_TASKS": 500,
                "TASK_TIMEOUT_SECONDS": 180, # 3 minutes
            },
            "circuit_breaker": {
                "FAILURE_THRESHOLD": 3,
                "RECOVERY_TIMEOUT_SECONDS": 30,
                "HALF_OPEN_TEST_COUNT": 1,
            },
            "connection_pool": {
                "MAX_SIZE": 20,
                "MAX_IDLE_SECONDS": 120,
            },
            "logging": {
                "LOG_LEVEL": "WARNING", # Reduce verbosity under high load
            },
            "recovery_timeouts": {
                "RETRY_ATTEMPTS": 5,
                "RETRY_BACKOFF_FACTOR": 1.5,
                "RETRY_MAX_DELAY_SECONDS": 90,
            }
        },
    }

    def __init__(self, profile: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initializes the ResilienceConfig.

        The configuration is loaded in the following order of precedence (lowest to highest):
        1. Default values
        2. Environment variables
        3. Specified profile settings
        4. Settings loaded from a configuration file

        Args:
            profile (str, optional): The name of a predefined configuration profile to load.
                                     E.g., "development", "production", "high-load".
            config_file (str, optional): Path to a JSON file containing configuration overrides.
        """
        self._config = self._load_defaults()
        self._load_env_vars()

        if profile:
            self.load_profile(profile)

        if config_file:
            self.import_config(config_file)

        # Final validation after all loading
        self._validate_config(self._config)
        logger.info("Resilience configuration initialized.")
        logger.debug(f"Current configuration: {self._config}")

    def _load_defaults(self) -> Dict[str, Any]:
        """
        Loads the base default configuration.
        Creates a deep copy to ensure modifications don't affect the original DEFAULT_CONFIG.
        """
        return json.loads(json.dumps(self.DEFAULT_CONFIG)) # Simple deep copy for dicts/lists

    def _load_env_vars(self):
        """
        2. Environment variable loading with fallbacks
        Loads configuration settings from environment variables, overriding defaults.
        Environment variables should be prefixed with 'AIDER_MCP_RESILIENCE_'.
        Example: AIDER_MCP_RESILIENCE_CONNECTION_HEALTH_HEALTH_CHECK_INTERVAL_SECONDS=10
        """
        logger.debug("Loading configuration from environment variables...")
        for category, settings in self._config.items():
            for key, default_value in settings.items():
                env_var_name = f"AIDER_MCP_RESILIENCE_{category.upper()}_{key.upper()}"
                env_value = os.getenv(env_var_name)

                if env_value is not None:
                    try:
                        # Attempt to convert environment variable string to the correct type
                        if isinstance(default_value, int):
                            settings[key] = int(env_value)
                        elif isinstance(default_value, float):
                            settings[key] = float(env_value)
                        elif isinstance(default_value, bool):
                            settings[key] = env_value.lower() in ('true', '1', 't', 'y', 'yes')
                        else: # Assume string for other types, or direct assignment
                            settings[key] = env_value
                        logger.debug(f"Loaded {key} from env var {env_var_name}: {settings[key]}")
                    except ValueError:
                        logger.warning(
                            f"Environment variable '{env_var_name}' has an invalid value '{env_value}'. "
                            f"Expected type: {type(default_value).__name__}. Using default: {default_value}"
                        )
                else:
                    logger.debug(f"Environment variable {env_var_name} not set. Using default for {key}.")

    def _validate_config(self, config: Dict[str, Any]):
        """
        3. Configuration validation
        Validates the entire configuration dictionary against expected types and ranges.
        Raises ValueError if any setting is invalid.
        """
        logger.debug("Validating configuration...")
        errors = []

        # Helper for type and range validation
        def validate_setting(category_name, setting_name, value, expected_type, min_val=None, max_val=None):
            if not isinstance(value, expected_type):
                errors.append(
                    f"Invalid type for {category_name}.{setting_name}: "
                    f"Expected {expected_type.__name__}, got {type(value).__name__} ({value})"
                )
            if expected_type in (int, float):
                if min_val is not None and value < min_val:
                    errors.append(
                        f"Value for {category_name}.{setting_name} ({value}) is below minimum allowed ({min_val})."
                    )
                if max_val is not None and value > max_val:
                    errors.append(
                        f"Value for {category_name}.{setting_name} ({value}) is above maximum allowed ({max_val})."
                    )

        # Connection Health
        conn_health = config.get("connection_health", {})
        validate_setting("connection_health", "HEALTH_CHECK_INTERVAL_SECONDS", conn_health.get("HEALTH_CHECK_INTERVAL_SECONDS"), int, 1, 3600)
        validate_setting("connection_health", "HEALTH_CHECK_TIMEOUT_SECONDS", conn_health.get("HEALTH_CHECK_TIMEOUT_SECONDS"), int, 1, 60)
        validate_setting("connection_health", "MAX_CONSECUTIVE_FAILURES", conn_health.get("MAX_CONSECUTIVE_FAILURES"), int, 1, 100)

        # Resource Usage
        resource_usage = config.get("resource_usage", {})
        validate_setting("resource_usage", "CPU_THRESHOLD_PERCENT", resource_usage.get("CPU_THRESHOLD_PERCENT"), float, 0.0, 100.0)
        validate_setting("resource_usage", "MEMORY_THRESHOLD_PERCENT", resource_usage.get("MEMORY_THRESHOLD_PERCENT"), float, 0.0, 100.0)
        validate_setting("resource_usage", "DISK_THRESHOLD_PERCENT", resource_usage.get("DISK_THRESHOLD_PERCENT"), float, 0.0, 100.0)

        # Task Queue
        task_queue = config.get("task_queue", {})
        validate_setting("task_queue", "MAX_PENDING_TASKS", task_queue.get("MAX_PENDING_TASKS"), int, 1, 10000)
        validate_setting("task_queue", "TASK_TIMEOUT_SECONDS", task_queue.get("TASK_TIMEOUT_SECONDS"), int, 10, 3600)

        # Circuit Breaker
        circuit_breaker = config.get("circuit_breaker", {})
        validate_setting("circuit_breaker", "FAILURE_THRESHOLD", circuit_breaker.get("FAILURE_THRESHOLD"), int, 1, 100)
        validate_setting("circuit_breaker", "RECOVERY_TIMEOUT_SECONDS", circuit_breaker.get("RECOVERY_TIMEOUT_SECONDS"), int, 1, 3600)
        validate_setting("circuit_breaker", "HALF_OPEN_TEST_COUNT", circuit_breaker.get("HALF_OPEN_TEST_COUNT"), int, 1, 10)
        validate_setting("circuit_breaker", "ROLLING_WINDOW_SECONDS", circuit_breaker.get("ROLLING_WINDOW_SECONDS"), int, 1, 3600)

        # Connection Pool
        conn_pool = config.get("connection_pool", {})
        validate_setting("connection_pool", "MAX_SIZE", conn_pool.get("MAX_SIZE"), int, 1, 100)
        validate_setting("connection_pool", "MAX_IDLE_SECONDS", conn_pool.get("MAX_IDLE_SECONDS"), int, 1, 3600)

        # Logging
        logging_settings = config.get("logging", {})
        log_level = logging_settings.get("LOG_LEVEL")
        if not isinstance(log_level, str) or log_level.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append(f"Invalid value for logging.LOG_LEVEL: {log_level}. Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")

        # Recovery Timeouts
        recovery_timeouts = config.get("recovery_timeouts", {})
        validate_setting("recovery_timeouts", "RETRY_ATTEMPTS", recovery_timeouts.get("RETRY_ATTEMPTS"), int, 0, 10)
        validate_setting("recovery_timeouts", "RETRY_BACKOFF_FACTOR", recovery_timeouts.get("RETRY_BACKOFF_FACTOR"), float, 1.0, 5.0)
        validate_setting("recovery_timeouts", "RETRY_MAX_DELAY_SECONDS", recovery_timeouts.get("RETRY_MAX_DELAY_SECONDS"), int, 1, 300)

        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(errors)
            logger.error(error_message)
            raise ValueError(error_message)
        logger.debug("Configuration validated successfully.")

    def update_config(self, new_settings: Dict[str, Any]):
        """
        4. Runtime configuration updates
        Updates the current configuration with new settings provided.
        Only specified settings are updated; others remain unchanged.
        The updated configuration is validated before being applied.

        Args:
            new_settings (dict): A dictionary of new settings to apply.
                                 Structure should mirror the config (e.g., {"category": {"setting": value}}).
        Raises:
            ValueError: If the new settings lead to an invalid configuration.
        """
        logger.info("Attempting to update configuration...")
        temp_config = json.loads(json.dumps(self._config)) # Deep copy current config

        for category, settings in new_settings.items():
            if category in temp_config:
                for key, value in settings.items():
                    if key in temp_config[category]:
                        temp_config[category][key] = value
                    else:
                        logger.warning(f"Attempted to update unknown setting: {category}.{key}. Skipping.")
            else:
                logger.warning(f"Attempted to update unknown configuration category: {category}. Skipping.")

        self._validate_config(temp_config) # Validate the proposed new config
        self._config = temp_config # Apply changes if validation passes
        logger.info("Configuration updated successfully.")
        logger.debug(f"New configuration: {self._config}")

        # Update module-level logger if LOG_LEVEL changed
        if "logging" in new_settings and "LOG_LEVEL" in new_settings["logging"]:
            new_log_level = new_settings["logging"]["LOG_LEVEL"].upper()
            logger.setLevel(new_log_level)
            logger.info(f"Module logger level updated to {new_log_level}")


    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value using a dot-separated key path.

        Args:
            key_path (str): The dot-separated path to the configuration setting
                            (e.g., "connection_health.HEALTH_CHECK_INTERVAL_SECONDS").
            default (Any, optional): The default value to return if the key path is not found.

        Returns:
            Any: The configuration value, or the default if not found.
        """
        parts = key_path.split('.')
        current_value = self._config
        for part in parts:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            else:
                logger.warning(f"Configuration key '{key_path}' not found. Returning default value.")
                return default
        return current_value

    def export_config(self, file_path: str):
        """
        5. Configuration export/import
        Exports the current configuration to a JSON file.

        Args:
            file_path (str): The path to the file where the configuration will be saved.
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self._config, f, indent=4)
            logger.info(f"Configuration exported to {file_path}")
        except IOError as e:
            logger.error(f"Failed to export configuration to {file_path}: {e}")
            raise

    def import_config(self, file_path: str):
        """
        5. Configuration export/import
        Imports configuration settings from a JSON file, overriding current settings.
        The imported configuration is validated before being applied.

        Args:
            file_path (str): The path to the JSON file to import.
        Raises:
            ValueError: If the imported configuration is invalid.
            IOError: If the file cannot be read.
        """
        logger.info(f"Attempting to import configuration from {file_path}...")
        try:
            with open(file_path, 'r') as f:
                imported_config = json.load(f)
            self._validate_config(imported_config) # Validate imported config
            self._config = imported_config # Apply if valid
            logger.info(f"Configuration imported successfully from {file_path}.")
            logger.debug(f"New configuration after import: {self._config}")

            # Update module-level logger if LOG_LEVEL changed
            if "logging" in imported_config and "LOG_LEVEL" in imported_config["logging"]:
                new_log_level = imported_config["logging"]["LOG_LEVEL"].upper()
                logger.setLevel(new_log_level)
                logger.info(f"Module logger level updated to {new_log_level}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {file_path}: {e}")
            raise ValueError(f"Invalid JSON format in {file_path}: {e}")
        except IOError as e:
            logger.error(f"Failed to import configuration from {file_path}: {e}")
            raise
        except ValueError as e:
            logger.error(f"Imported configuration from {file_path} failed validation: {e}")
            raise

    def load_profile(self, profile_name: str):
        """
        7. Configuration profiles
        Loads a predefined configuration profile, overriding current settings.
        The profile settings are validated before being applied.

        Args:
            profile_name (str): The name of the profile to load (e.g., "production").
        Raises:
            ValueError: If the profile name is invalid or the profile settings are invalid.
        """
        logger.info(f"Attempting to load profile: {profile_name}...")
        if profile_name not in self.PROFILES:
            raise ValueError(f"Unknown configuration profile: {profile_name}. "
                             f"Available profiles: {list(self.PROFILES.keys())}")

        profile_settings = self.PROFILES[profile_name]
        temp_config = json.loads(json.dumps(self._config)) # Deep copy current config

        # Apply profile settings, merging them into the current config
        for category, settings in profile_settings.items():
            if category in temp_config:
                temp_config[category].update(settings)
            else:
                # This case should ideally not happen if profiles only override existing categories
                temp_config[category] = settings

        self._validate_config(temp_config) # Validate the proposed profile config
        self._config = temp_config # Apply changes if validation passes
        logger.info(f"Profile '{profile_name}' loaded successfully.")
        logger.debug(f"Configuration after profile load: {self._config}")

        # Update module-level logger if LOG_LEVEL changed
        if "logging" in profile_settings and "LOG_LEVEL" in profile_settings["logging"]:
            new_log_level = profile_settings["logging"]["LOG_LEVEL"].upper()
            logger.setLevel(new_log_level)
            logger.info(f"Module logger level updated to {new_log_level}")


    def get_all_settings(self) -> Dict[str, Any]:
        """
        Returns a deep copy of the entire current configuration.
        """
        return json.loads(json.dumps(self._config))

# Example Usage (for demonstration purposes, typically not run directly in a module)
if __name__ == "__main__":
    print("--- Initializing ResilienceConfig with defaults ---")
    config = ResilienceConfig()
    print(f"Health Check Interval: {config.get('connection_health.HEALTH_CHECK_INTERVAL_SECONDS')}s")
    print(f"Max Pending Tasks: {config.get('task_queue.MAX_PENDING_TASKS')}")
    print(f"Current Log Level: {config.get('logging.LOG_LEVEL')}")

    print("\n--- Loading 'development' profile ---")
    try:
        config.load_profile("development")
        print(f"Health Check Interval (dev): {config.get('connection_health.HEALTH_CHECK_INTERVAL_SECONDS')}s")
        print(f"Max Pending Tasks (dev): {config.get('task_queue.MAX_PENDING_TASKS')}")
        print(f"Current Log Level (dev): {config.get('logging.LOG_LEVEL')}")
    except ValueError as e:
        print(f"Error loading profile: {e}")

    print("\n--- Overriding with Environment Variables (set before running) ---")
    # To test this, run:
    # AIDER_MCP_RESILIENCE_TASK_QUEUE_MAX_PENDING_TASKS=50 \
    # AIDER_MCP_RESILIENCE_LOGGING_LOG_LEVEL=DEBUG \
    # python resilience_config.py
    os.environ["AIDER_MCP_RESILIENCE_TASK_QUEUE_MAX_PENDING_TASKS"] = "50"
    os.environ["AIDER_MCP_RESILIENCE_LOGGING_LOG_LEVEL"] = "DEBUG"
    config_env = ResilienceConfig() # Re-initialize to pick up env vars
    print(f"Max Pending Tasks (from env): {config_env.get('task_queue.MAX_PENDING_TASKS')}")
    print(f"Current Log Level (from env): {config_env.get('logging.LOG_LEVEL')}")
    del os.environ["AIDER_MCP_RESILIENCE_TASK_QUEUE_MAX_PENDING_TASKS"]
    del os.environ["AIDER_MCP_RESILIENCE_LOGGING_LOG_LEVEL"]


    print("\n--- Updating configuration at runtime ---")
    try:
        config.update_config({
            "task_queue": {
                "MAX_PENDING_TASKS": 75,
                "TASK_TIMEOUT_SECONDS": 120
            },
            "logging": {
                "LOG_LEVEL": "WARNING"
            }
        })
        print(f"Updated Max Pending Tasks: {config.get('task_queue.MAX_PENDING_TASKS')}")
        print(f"Updated Task Timeout: {config.get('task_queue.TASK_TIMEOUT_SECONDS')}s")
        print(f"Updated Log Level: {config.get('logging.LOG_LEVEL')}")
    except ValueError as e:
        print(f"Error updating config: {e}")

    print("\n--- Attempting invalid update ---")
    try:
        config.update_config({
            "task_queue": {
                "MAX_PENDING_TASKS": -5 # Invalid value
            }
        })
    except ValueError as e:
        print(f"Caught expected error for invalid update: {e}")
    print(f"Max Pending Tasks (after failed update, should be unchanged): {config.get('task_queue.MAX_PENDING_TASKS')}")


    print("\n--- Exporting and Importing configuration ---")
    test_file = "resilience_config_test.json"
    try:
        config.export_config(test_file)
        print(f"Configuration exported to {test_file}")

        # Create a new config instance to import into
        imported_config = ResilienceConfig()
        imported_config.import_config(test_file)
        print(f"Imported Max Pending Tasks: {imported_config.get('task_queue.MAX_PENDING_TASKS')}")
        print(f"Imported Log Level: {imported_config.get('logging.LOG_LEVEL')}")

    except (IOError, ValueError) as e:
        print(f"Error during export/import: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Cleaned up {test_file}")

    print("\n--- Loading 'production' profile ---")
    try:
        config.load_profile("production")
        print(f"Health Check Interval (prod): {config.get('connection_health.HEALTH_CHECK_INTERVAL_SECONDS')}s")
        print(f"Max Pending Tasks (prod): {config.get('task_queue.MAX_PENDING_TASKS')}")
        print(f"Current Log Level (prod): {config.get('logging.LOG_LEVEL')}")
    except ValueError as e:
        print(f"Error loading profile: {e}")
