import threading
import queue
import time
import os
import logging
import psutil
from collections import deque
from typing import Callable, Any, Optional, Dict, Set

# Assume get_logger is available or define a simple one for standalone
try:
    from app.core.logging import get_logger
except ImportError:
    # Fallback for standalone testing or if logging module is not yet integrated
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    def get_logger(name, log_category="operational"):
        return logging.getLogger(name)

logger = get_logger("resilience_manager", "operational")

# Default configuration for resilience features
DEFAULT_RESILIENCE_CONFIG = {
    "heartbeat": {
        "enabled": True,
        "interval_seconds": 60,
        "timeout_seconds": 180,
    },
    "resource_monitoring": {
        "enabled": True,
        "interval_seconds": 30,
        "max_memory_percent": 80,
        "max_cpu_percent": 90,
        "degraded_mode_threshold": 70, # % of max_memory/cpu before degraded mode is triggered
    },
    "task_queue": {
        "enabled": True,
        "max_concurrent_tasks": 5,
        "queue_timeout_seconds": 10, # Timeout for workers trying to get tasks from queue
    },
    "circuit_breaker": {
        "enabled": True,
        "failure_threshold": 3,
        "reset_time_seconds": 300,
    },
    "auto_recovery": {
        "enabled": True,
        "reconnect_interval_seconds": 60,
    },
    "performance_metrics": {
        "enabled": True,
        "window_size": 100, # Number of recent task durations to keep
    }
}

# Helper to get config values, respecting environment variables
def _get_config_value(key_path: str, default_value: Any) -> Any:
    """
    Retrieves a configuration value, prioritizing environment variables.
    Environment variable names are constructed as RESILIENCE_<CATEGORY>_<KEY>.
    """
    env_var_name = f"RESILIENCE_{key_path.replace('.', '_').upper()}"
    env_val = os.getenv(env_var_name)

    if env_val is not None:
        # Attempt to convert to appropriate type based on default_value's type
        if isinstance(default_value, bool):
            return env_val.lower() == "true"
        elif isinstance(default_value, int):
            try:
                return int(env_val)
            except ValueError:
                logger.warning(f"Invalid integer value for {env_var_name}: '{env_val}'. Using default: {default_value}")
                return default_value
        elif isinstance(default_value, float):
            try:
                return float(env_val)
            except ValueError:
                logger.warning(f"Invalid float value for {env_var_name}: '{env_val}'. Using default: {default_value}")
                return default_value
        return env_val # Return as string if type conversion fails or not applicable
    return default_value

class ConnectionHealthMonitor(threading.Thread):
    """
    Monitors the health of external connections by periodically sending heartbeats.
    """
    def __init__(self, send_heartbeat: Callable[[], bool], interval: int, timeout: int, logger: logging.Logger):
        super().__init__(daemon=True)
        self.send_heartbeat = send_heartbeat
        self.interval = interval
        self.timeout = timeout
        self.logger = logger
        self.last_heartbeat = time.time()
        self.running = True
        self.healthy = True # Initial state is healthy

    def run(self):
        self.logger.info("ConnectionHealthMonitor started.")
        while self.running:
            time.sleep(self.interval)
            try:
                # Attempt to send a heartbeat
                if not self.send_heartbeat():
                    self.logger.warning("Heartbeat failed. Connection might be unhealthy.")
                    if self.healthy: # Log state change only
                        self.healthy = False
                else:
                    self.last_heartbeat = time.time()
                    if not self.healthy: # Log state change only
                        self.logger.info("Heartbeat successful. Connection restored.")
                        self.healthy = True

                # Check for timeout
                if time.time() - self.last_heartbeat > self.timeout:
                    if self.healthy: # Log state change only
                        self.logger.error(f"No successful heartbeat for {self.timeout} seconds. Connection considered unhealthy.")
                        self.healthy = False
            except Exception as e:
                self.logger.error(f"Error in ConnectionHealthMonitor: {e}")
                if self.healthy: # Log state change only
                    self.healthy = False

    def stop(self):
        self.running = False
        self.logger.info("ConnectionHealthMonitor stopped.")

    def is_healthy(self) -> bool:
        """Returns True if the connection is currently considered healthy."""
        return self.healthy

class ResourceManager(threading.Thread):
    """
    Monitors system CPU and memory usage and reports degraded or critical states.
    """
    def __init__(self, config: dict, logger: logging.Logger):
        super().__init__(daemon=True)
        self.config = config
        self.max_memory_percent = config["max_memory_percent"]
        self.max_cpu_percent = config["max_cpu_percent"]
        self.degraded_mode_threshold = config["degraded_mode_threshold"]
        self.logger = logger
        self.running = True
        self._current_memory_percent = 0.0
        self._current_cpu_percent = 0.0
        self._is_degraded = False

    def run(self):
        self.logger.info("ResourceManager started.")
        while self.running:
            try:
                self._current_memory_percent = psutil.virtual_memory().percent
                # psutil.cpu_percent blocks for 'interval' seconds to get a meaningful average
                self._current_cpu_percent = psutil.cpu_percent(interval=1)
                
                mem_degraded = self._current_memory_percent >= self.degraded_mode_threshold
                cpu_degraded = self._current_cpu_percent >= self.degraded_mode_threshold

                new_degraded_status = mem_degraded or cpu_degraded

                if new_degraded_status and not self._is_degraded:
                    self.logger.warning(f"System entering degraded mode: Memory {self._current_memory_percent:.1f}% (>{self.degraded_mode_threshold}%), CPU {self._current_cpu_percent:.1f}% (>{self.degraded_mode_threshold}%)")
                elif not new_degraded_status and self._is_degraded:
                    self.logger.info("System exiting degraded mode.")
                
                self._is_degraded = new_degraded_status

                if self._current_memory_percent >= self.max_memory_percent:
                    self.logger.critical(f"Memory usage critical: {self._current_memory_percent:.1f}% (>{self.max_memory_percent}%). Consider restarting.")
                if self._current_cpu_percent >= self.max_cpu_percent:
                    self.logger.critical(f"CPU usage critical: {self._current_cpu_percent:.1f}% (>{self.max_cpu_percent}%).")

            except Exception as e:
                self.logger.error(f"Error in ResourceManager: {e}")
            time.sleep(self.config["interval_seconds"])

    def stop(self):
        self.running = False
        self.logger.info("ResourceManager stopped.")

    def is_degraded(self) -> bool:
        """Returns True if system resources are currently in a degraded state."""
        return self._is_degraded

    def get_metrics(self) -> Dict[str, float]:
        """Returns current memory and CPU usage percentages."""
        return {
            "memory_percent": self._current_memory_percent,
            "cpu_percent": self._current_cpu_percent,
            "is_degraded": self._is_degraded
        }

class TaskQueueManager:
    """
    Manages a task queue and tracks active tasks to enforce concurrency limits.
    """
    def __init__(self, max_concurrent_tasks: int, logger: logging.Logger, queue_timeout: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logger
        self.task_queue = queue.Queue() # This queue is for internal worker management if needed
        self.active_tasks = 0
        self.queue_timeout = queue_timeout
        self._active_tasks_lock = threading.Lock()

    def submit(self, func: Callable, *args, **kwargs):
        """Submits a task to the internal queue (if workers are managed by this class)."""
        self.task_queue.put((func, args, kwargs))
        self.logger.debug(f"Task submitted to internal queue. Queue size: {self.task_queue.qsize()}")

    def enqueue_task(self, task_id: Any) -> bool:
        """
        Attempts to 'enqueue' a task by incrementing the active task count.
        Returns True if successful, False if max_concurrent_tasks is reached.
        """
        with self._active_tasks_lock:
            if self.active_tasks >= self.max_concurrent_tasks:
                self.logger.warning(f"Task queue full. Max concurrent tasks ({self.max_concurrent_tasks}) reached. Task {task_id} rejected.")
                return False
            self.active_tasks += 1
            self.logger.debug(f"Task {task_id} enqueued. Active tasks: {self.active_tasks}")
            return True

    def dequeue_task(self) -> None:
        """Decrements the active task count."""
        with self._active_tasks_lock:
            if self.active_tasks > 0:
                self.active_tasks -= 1
                self.logger.debug(f"Task dequeued. Active tasks: {self.active_tasks}")

    def get_active_tasks_count(self) -> int:
        """Returns the current number of active tasks."""
        with self._active_tasks_lock:
            return self.active_tasks

    def start_workers(self, num_workers: int):
        """Starts worker threads to process tasks from the internal queue."""
        self.logger.info(f"Starting {num_workers} task queue workers.")
        for _ in range(num_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()

    def _worker_loop(self):
        """Worker loop to fetch and execute tasks from the queue."""
        while True:
            try:
                func, args, kwargs = self.task_queue.get(timeout=self.queue_timeout)
                self.logger.debug(f"Worker processing task: {func.__name__}")
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error processing task in worker: {e}")
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                self.logger.debug("Task queue empty, worker waiting...")
                time.sleep(1) # Wait a bit before checking again
            except Exception as e:
                self.logger.critical(f"Critical error in task queue worker: {e}")

class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent repeated failures against a service.
    States: CLOSED, OPEN, HALF-OPEN.
    """
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF-OPEN"

    def __init__(self, threshold: int, reset_time: int, logger: logging.Logger):
        self.threshold = threshold # Number of failures before opening
        self.reset_time = reset_time # Time in seconds to wait before attempting to close
        self.logger = logger
        self.failures = 0
        self.last_failure_time = None
        self.state = self.CLOSED
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs):
        """
        Attempts to call the given function, applying circuit breaker logic.
        Raises CircuitBreakerOpenException if the circuit is open.
        Raises CircuitBreakerTrippedException if the call fails and trips the circuit.
        """
        with self._lock:
            if self.state == self.OPEN:
                if time.time() - self.last_failure_time > self.reset_time:
                    self.state = self.HALF_OPEN
                    self.logger.info("Circuit Breaker: State changed to HALF-OPEN (reset time elapsed).")
                else:
                    self.logger.warning("Circuit Breaker: OPEN. Call rejected.")
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN. Calls are being rejected.")
            elif self.state == self.HALF_OPEN:
                self.logger.info("Circuit Breaker: HALF-OPEN. Allowing one test call.")

        try:
            result = func(*args, **kwargs)
            with self._lock:
                if self.state == self.HALF_OPEN:
                    self.state = self.CLOSED
                    self.failures = 0
                    self.logger.info("Circuit Breaker: State changed to CLOSED (successful call in HALF-OPEN).")
                elif self.state == self.CLOSED:
                    self.failures = 0 # Reset failures on success in CLOSED state
            return result
        except Exception as e:
            with self._lock:
                self.failures += 1
                self.last_failure_time = time.time()
                self.logger.error(f"Circuit Breaker: Call failed. Failures: {self.failures}/{self.threshold}. Error: {e}")
                if self.failures >= self.threshold and self.state == self.CLOSED:
                    self.state = self.OPEN
                    self.logger.error("Circuit Breaker: State changed to OPEN (too many failures).")
                elif self.state == self.HALF_OPEN:
                    self.state = self.OPEN
                    self.logger.error("Circuit Breaker: State changed back to OPEN (failure in HALF-OPEN).")
            raise CircuitBreakerTrippedException(f"Circuit breaker tripped due to failure: {e}") from e

    def reset(self):
        """Manually resets the circuit breaker to the CLOSED state."""
        with self._lock:
            self.failures = 0
            self.state = self.CLOSED
            self.last_failure_time = None
            self.logger.info("Circuit Breaker: Manually reset to CLOSED state.")

class CircuitBreakerOpenException(Exception):
    """Exception raised when the circuit breaker is open and rejects a call."""
    pass

class CircuitBreakerTrippedException(Exception):
    """Exception raised when a call fails and causes the circuit breaker to trip."""
    pass

class AutoRecoverySystem:
    """
    Attempts to automatically recover from connection or service failures by
    periodically calling a reconnect function.
    """
    def __init__(self, reconnect_func: Callable[[], bool], interval: int, logger: logging.Logger):
        self.reconnect_func = reconnect_func
        self.interval = interval
        self.logger = logger
        self.running = True
        self._recovery_thread = None

    def start(self):
        """Starts the auto-recovery thread."""
        if self._recovery_thread is None or not self._recovery_thread.is_alive():
            self.running = True
            self._recovery_thread = threading.Thread(target=self._recovery_loop, daemon=True)
            self._recovery_thread.start()
            self.logger.info("AutoRecoverySystem started.")

    def _recovery_loop(self):
        """The main loop for the auto-recovery thread."""
        while self.running:
            time.sleep(self.interval)
            try:
                self.logger.info("AutoRecovery: Attempting to reconnect...")
                if not self.reconnect_func():
                    self.logger.warning("AutoRecovery: Reconnect attempt failed. Retrying later.")
                else:
                    self.logger.info("AutoRecovery: Reconnect successful.")
            except Exception as e:
                self.logger.error(f"Error during auto-recovery attempt: {e}")

    def stop(self):
        """Stops the auto-recovery thread."""
        self.running = False
        if self._recovery_thread and self._recovery_thread.is_alive():
            self._recovery_thread.join(timeout=self.interval + 1) # Give it a moment to finish
        self.logger.info("AutoRecoverySystem stopped.")

class PerformanceMetrics(threading.Thread):
    """
    Collects and provides summary statistics for task durations over a sliding window.
    """
    def __init__(self, window: int, logger: logging.Logger):
        super().__init__(daemon=True)
        self.window = window # Max number of metrics to store
        self.logger = logger
        self.metrics = deque(maxlen=window) # Stores (timestamp, duration)
        self.running = True
        self._metrics_lock = threading.Lock()

    def run(self):
        self.logger.info("PerformanceMetrics monitor started.")
        while self.running:
            time.sleep(30) # Periodically log summary
            self.get_latest() # Triggers logging of current stats
        self.logger.info("PerformanceMetrics monitor stopped.")

    def record_metric(self, duration: float):
        """Records a single task duration metric."""
        with self._metrics_lock:
            self.metrics.append((time.time(), duration))
            self.logger.debug(f"Recorded performance metric: {duration:.2f}s. Total metrics: {len(self.metrics)}")

    def get_latest(self) -> Dict[str, Any]:
        """Returns a summary of performance metrics (count, average, min, max duration)."""
        with self._metrics_lock:
            if not self.metrics:
                return {"count": 0, "avg_duration_seconds": 0, "min_duration_seconds": 0, "max_duration_seconds": 0, "window_size": self.window}

            durations = [m[1] for m in self.metrics]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)

            metrics_summary = {
                "count": len(durations),
                "avg_duration_seconds": avg_duration,
                "min_duration_seconds": min_duration,
                "max_duration_seconds": max_duration,
                "window_size": self.window
            }
            self.logger.debug(f"Current performance metrics: {metrics_summary}")
            return metrics_summary

    def stop(self):
        """Stops the performance metrics monitoring thread."""
        self.running = False
        self.logger.info("PerformanceMetrics monitor stopped.")


class ResilienceManager:
    """
    Orchestrates various resilience features for the AI coding system.
    This is implemented as a singleton class to ensure a single point of control.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ResilienceManager, cls).__new__(cls)
                    cls._instance._initialized = False # Flag to ensure __init__ runs only once
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.config = self._load_config()
        self.logger = get_logger("ResilienceManager", "operational")

        self.heartbeat_monitor: Optional[ConnectionHealthMonitor] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.task_queue_manager: Optional[TaskQueueManager] = None
        self.circuit_breaker: Optional[CircuitBreaker] = None
        self.auto_recovery: Optional[AutoRecoverySystem] = None
        self.performance_metrics: Optional[PerformanceMetrics] = None

        self._initialized = True
        self.start_monitors()

    def _load_config(self) -> Dict[str, Any]:
        """Loads configuration from defaults and overrides with environment variables."""
        config = {}
        for category, defaults in DEFAULT_RESILIENCE_CONFIG.items():
            config[category] = {}
            for key, default_val in defaults.items():
                full_key_path = f"{category}.{key}"
                config[category][key] = _get_config_value(full_key_path, default_val)
        return config

    def start_monitors(self):
        """Initializes and starts all enabled resilience monitors."""
        self.logger.info("Starting resilience monitors...")

        if self.config["heartbeat"]["enabled"]:
            # Placeholder for actual heartbeat function, needs to be passed from outside
            # For now, a dummy function. In a real system, this would check external service health.
            def dummy_heartbeat():
                self.logger.debug("Dummy heartbeat check.")
                return True
            self.heartbeat_monitor = ConnectionHealthMonitor(
                send_heartbeat=dummy_heartbeat,
                interval=self.config["heartbeat"]["interval_seconds"],
                timeout=self.config["heartbeat"]["timeout_seconds"],
                logger=self.logger
            )
            self.heartbeat_monitor.start()

        if self.config["resource_monitoring"]["enabled"]:
            self.resource_manager = ResourceManager(
                config=self.config["resource_monitoring"],
                logger=self.logger
            )
            self.resource_manager.start()

        if self.config["task_queue"]["enabled"]:
            self.task_queue_manager = TaskQueueManager(
                max_concurrent_tasks=self.config["task_queue"]["max_concurrent_tasks"],
                logger=self.logger,
                queue_timeout=self.config["task_queue"]["queue_timeout_seconds"]
            )
            # Note: We don't start internal workers here as `code_with_multiple_ai` uses ThreadPoolExecutor
            # and directly interacts with enqueue_task/dequeue_task for concurrency control.

        if self.config["circuit_breaker"]["enabled"]:
            self.circuit_breaker = CircuitBreaker(
                threshold=self.config["circuit_breaker"]["failure_threshold"],
                reset_time=self.config["circuit_breaker"]["reset_time_seconds"],
                logger=self.logger
            )

        if self.config["auto_recovery"]["enabled"]:
            # Placeholder for actual reconnect function, needs to be passed from outside
            # For now, a dummy function. In a real system, this would attempt to re-establish a broken connection.
            def dummy_reconnect():
                self.logger.debug("Dummy auto-recovery reconnect attempt.")
                return True
            self.auto_recovery = AutoRecoverySystem(
                reconnect_func=dummy_reconnect,
                interval=self.config["auto_recovery"]["reconnect_interval_seconds"],
                logger=self.logger
            )
            self.auto_recovery.start()

        if self.config["performance_metrics"]["enabled"]:
            self.performance_metrics = PerformanceMetrics(
                window=self.config["performance_metrics"]["window_size"],
                logger=self.logger
            )
            self.performance_metrics.start()

        self.logger.info("Resilience monitors started.")

    def stop_monitors(self):
        """Stops all running resilience monitors."""
        self.logger.info("Stopping resilience monitors...")
        if self.heartbeat_monitor:
            self.heartbeat_monitor.stop()
            self.heartbeat_monitor.join(timeout=1)
        if self.resource_manager:
            self.resource_manager.stop()
            self.resource_manager.join(timeout=1)
        if self.auto_recovery:
            self.auto_recovery.stop()
            self.auto_recovery.join(timeout=1)
        if self.performance_metrics:
            self.performance_metrics.stop()
            self.performance_metrics.join(timeout=1)
        self.logger.info("Resilience monitors stopped.")

    def is_degraded(self) -> bool:
        """
        Checks if the system is in a degraded state based on various factors.
        """
        if self.resource_manager and self.resource_manager.is_degraded():
            return True
        if self.heartbeat_monitor and not self.heartbeat_monitor.is_healthy():
            return True
        # Add other degradation checks here if needed
        return False

    def get_health_status(self) -> Dict[str, Any]:
        """
        Returns a comprehensive dictionary of the current health status of all
        resilience components.
        """
        status = {
            "overall_degraded": self.is_degraded(),
            "heartbeat_healthy": self.heartbeat_monitor.is_healthy() if self.heartbeat_monitor else "N/A (disabled)",
            "resource_metrics": self.resource_manager.get_metrics() if self.resource_manager else "N/A (disabled)",
            "task_queue_active_tasks": self.task_queue_manager.get_active_tasks_count() if self.task_queue_manager else "N/A (disabled)",
            "circuit_breaker_state": self.circuit_breaker.state if self.circuit_breaker else "N/A (disabled)",
            "performance_summary": self.performance_metrics.get_latest() if self.performance_metrics else "N/A (disabled)"
        }
        return status

# Global instance of ResilienceManager
resilience_manager = ResilienceManager()

# Register atexit to ensure monitors are stopped gracefully on program exit
import atexit
atexit.register(resilience_manager.stop_monitors)
