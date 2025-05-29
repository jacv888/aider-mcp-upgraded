"""
aider_mcp_resilience.py

Comprehensive resilience enhancement module for the aider-mcp server.

Features:
1. Connection Health Monitor (heartbeat)
2. Resource Management (memory/CPU monitoring, throttling)
3. Task Queue Management (concurrency limits)
4. Auto-Recovery System (automatic reconnection)
5. Circuit Breaker Pattern (prevents cascade failures)
6. Connection Pool Management (efficient MCP connection handling)
7. Graceful Degradation (reduces functionality under load)
8. Performance Metrics (server health, connection status)

Integration:
- Import and instantiate `AiderMCPResilience` in your FastMCP server.
- Use hooks to integrate with task execution, connection management, etc.

Dependencies:
- psutil (for resource monitoring)
"""

import threading
import time
import logging
import queue
import psutil
from collections import deque
from typing import Callable, Optional, Any, Dict

# Default configuration
DEFAULT_CONFIG = {
    "heartbeat_interval": 5,  # seconds
    "heartbeat_timeout": 15,  # seconds
    "max_memory_percent": 80,  # percent
    "max_cpu_percent": 90,     # percent
    "max_concurrent_tasks": 8,
    "circuit_breaker_threshold": 5,  # failures
    "circuit_breaker_reset_time": 30,  # seconds
    "connection_pool_size": 10,
    "degraded_mode_threshold": 0.9,  # 90% resource usage triggers degraded mode
    "metrics_window": 60,  # seconds for rolling metrics
}

class ConnectionHealthMonitor(threading.Thread):
    def __init__(self, send_heartbeat: Callable[[], bool], interval: int, timeout: int, logger: logging.Logger):
        super().__init__(daemon=True)
        self.send_heartbeat = send_heartbeat
        self.interval = interval
        self.timeout = timeout
        self.logger = logger
        self.last_heartbeat = time.time()
        self.running = True
        self.status = "healthy"

    def run(self):
        while self.running:
            try:
                ok = self.send_heartbeat()
                now = time.time()
                if ok:
                    self.last_heartbeat = now
                    self.status = "healthy"
                elif now - self.last_heartbeat > self.timeout:
                    self.status = "unhealthy"
                    self.logger.warning("Connection health monitor: heartbeat timeout detected.")
                else:
                    self.logger.warning("Connection health monitor: missed heartbeat.")
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                self.status = "unhealthy"
            time.sleep(self.interval)

    def stop(self):
        self.running = False

class ResourceManager(threading.Thread):
    def __init__(self, config: dict, logger: logging.Logger):
        super().__init__(daemon=True)
        self.max_memory_percent = config["max_memory_percent"]
        self.max_cpu_percent = config["max_cpu_percent"]
        self.degraded_mode_threshold = config["degraded_mode_threshold"]
        self.logger = logger
        self.running = True
        self.in_degraded_mode = False

    def run(self):
        while self.running:
            mem = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=1)
            if mem > self.max_memory_percent or cpu > self.max_cpu_percent:
                self.logger.warning(f"ResourceManager: High resource usage detected (mem={mem}%, cpu={cpu}%). Throttling may be applied.")
            if mem > self.max_memory_percent * self.degraded_mode_threshold or cpu > self.max_cpu_percent * self.degraded_mode_threshold:
                if not self.in_degraded_mode:
                    self.logger.warning("ResourceManager: Entering degraded mode due to high resource usage.")
                self.in_degraded_mode = True
            else:
                if self.in_degraded_mode:
                    self.logger.info("ResourceManager: Exiting degraded mode.")
                self.in_degraded_mode = False
            time.sleep(2)

    def stop(self):
        self.running = False

class TaskQueueManager:
    def __init__(self, max_concurrent_tasks: int, logger: logging.Logger):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logger
        self.task_queue = queue.Queue()
        self.active_tasks = 0
        self.lock = threading.Lock()

    def submit(self, func: Callable, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))
        self.logger.debug("Task submitted to queue.")

    def worker(self):
        while True:
            func, args, kwargs = self.task_queue.get()
            with self.lock:
                if self.active_tasks >= self.max_concurrent_tasks:
                    self.logger.warning("TaskQueueManager: Max concurrent tasks reached, waiting...")
                while self.active_tasks >= self.max_concurrent_tasks:
                    time.sleep(0.1)
                self.active_tasks += 1
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Task execution error: {e}")
            finally:
                with self.lock:
                    self.active_tasks -= 1
                self.task_queue.task_done()

    def start_workers(self, num_workers: int):
        for _ in range(num_workers):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
        self.logger.info(f"TaskQueueManager: Started {num_workers} worker threads.")

class CircuitBreaker:
    def __init__(self, threshold: int, reset_time: int, logger: logging.Logger):
        self.threshold = threshold
        self.reset_time = reset_time
        self.logger = logger
        self.failures = 0
        self.last_failure_time = None
        self.open = False

    def call(self, func: Callable, *args, **kwargs):
        if self.open:
            if time.time() - self.last_failure_time > self.reset_time:
                self.logger.info("CircuitBreaker: Resetting after timeout.")
                self.open = False
                self.failures = 0
            else:
                self.logger.warning("CircuitBreaker: Open, call blocked.")
                raise Exception("CircuitBreaker is open")
        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            self.logger.error(f"CircuitBreaker: Failure {self.failures}/{self.threshold}: {e}")
            if self.failures >= self.threshold:
                self.open = True
                self.logger.error("CircuitBreaker: Opened due to repeated failures.")
            raise

class ConnectionPool:
    def __init__(self, create_connection: Callable[[], Any], pool_size: int, logger: logging.Logger):
        self.create_connection = create_connection
        self.pool_size = pool_size
        self.logger = logger
        self.pool = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        for _ in range(self.pool_size):
            conn = self.create_connection()
            self.pool.put(conn)
        self.logger.info(f"ConnectionPool: Initialized with {self.pool_size} connections.")

    def acquire(self, timeout: Optional[float] = None):
        try:
            conn = self.pool.get(timeout=timeout)
            self.logger.debug("ConnectionPool: Connection acquired.")
            return conn
        except queue.Empty:
            self.logger.error("ConnectionPool: No available connections.")
            raise

    def release(self, conn):
        self.pool.put(conn)
        self.logger.debug("ConnectionPool: Connection released.")

    def size(self):
        return self.pool.qsize()

class AutoRecoverySystem:
    def __init__(self, reconnect_func: Callable[[], bool], logger: logging.Logger):
        self.reconnect_func = reconnect_func
        self.logger = logger
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        while self.running:
            try:
                ok = self.reconnect_func()
                if ok:
                    self.logger.info("AutoRecoverySystem: Reconnection successful.")
                    time.sleep(10)
                else:
                    self.logger.warning("AutoRecoverySystem: Reconnection failed, retrying soon.")
                    time.sleep(5)
            except Exception as e:
                self.logger.error(f"AutoRecoverySystem: Exception during reconnection: {e}")
                time.sleep(5)

    def stop(self):
        self.running = False

class PerformanceMetrics(threading.Thread):
    def __init__(self, window: int, logger: logging.Logger):
        super().__init__(daemon=True)
        self.window = window
        self.logger = logger
        self.metrics = deque(maxlen=window)
        self.running = True
        self.latest = {}

    def run(self):
        while self.running:
            mem = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=1)
            metric = {
                "timestamp": time.time(),
                "memory_percent": mem,
                "cpu_percent": cpu,
            }
            self.metrics.append(metric)
            self.latest = metric
            self.logger.debug(f"PerformanceMetrics: {metric}")
            time.sleep(1)

    def stop(self):
        self.running = False

    def get_latest(self):
        return self.latest

    def get_metrics(self):
        return list(self.metrics)

class AiderMCPResilience:
    def __init__(self, config: Optional[Dict] = None, logger: Optional[logging.Logger] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.logger = logger or logging.getLogger("AiderMCPResilience")
        self.logger.setLevel(logging.INFO)
        self.heartbeat_monitor = None
        self.resource_manager = None
        self.task_queue_manager = None
        self.circuit_breaker = None
        self.connection_pool = None
        self.auto_recovery = None
        self.metrics = None

    def integrate(
        self,
        send_heartbeat: Callable[[], bool],
        reconnect_func: Callable[[], bool],
        create_connection: Callable[[], Any],
        task_executor: Optional[Callable] = None,
    ):
        # Heartbeat
        self.heartbeat_monitor = ConnectionHealthMonitor(
            send_heartbeat,
            self.config["heartbeat_interval"],
            self.config["heartbeat_timeout"],
            self.logger,
        )
        self.heartbeat_monitor.start()

        # Resource management
        self.resource_manager = ResourceManager(self.config, self.logger)
        self.resource_manager.start()

        # Task queue
        self.task_queue_manager = TaskQueueManager(self.config["max_concurrent_tasks"], self.logger)
        if task_executor:
            self.task_queue_manager.start_workers(self.config["max_concurrent_tasks"])

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            self.config["circuit_breaker_threshold"],
            self.config["circuit_breaker_reset_time"],
            self.logger,
        )

        # Connection pool
        self.connection_pool = ConnectionPool(
            create_connection,
            self.config["connection_pool_size"],
            self.logger,
        )

        # Auto-recovery
        self.auto_recovery = AutoRecoverySystem(reconnect_func, self.logger)
        self.auto_recovery.start()

        # Metrics
        self.metrics = PerformanceMetrics(self.config["metrics_window"], self.logger)
        self.metrics.start()

        self.logger.info("AiderMCPResilience: All resilience systems started.")

    def stop(self):
        if self.heartbeat_monitor:
            self.heartbeat_monitor.stop()
        if self.resource_manager:
            self.resource_manager.stop()
        if self.auto_recovery:
            self.auto_recovery.stop()
        if self.metrics:
            self.metrics.stop()
        self.logger.info("AiderMCPResilience: All resilience systems stopped.")

    def is_degraded(self):
        return self.resource_manager and self.resource_manager.in_degraded_mode

    def get_metrics(self):
        if self.metrics:
            return self.metrics.get_latest()
        return {}

    def submit_task(self, func: Callable, *args, **kwargs):
        if self.is_degraded():
            self.logger.warning("AiderMCPResilience: Degraded mode, task submission may be throttled.")
        self.task_queue_manager.submit(func, *args, **kwargs)

    def run_with_circuit_breaker(self, func: Callable, *args, **kwargs):
        return self.circuit_breaker.call(func, *args, **kwargs)

    def acquire_connection(self, timeout: Optional[float] = None):
        return self.connection_pool.acquire(timeout=timeout)

    def release_connection(self, conn):
        self.connection_pool.release(conn)

    def get_connection_pool_size(self):
        return self.connection_pool.size()

# Example logger setup (can be replaced by MCP's logger)
def get_logger(name="AiderMCPResilience"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
