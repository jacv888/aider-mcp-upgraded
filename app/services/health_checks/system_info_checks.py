import platform
import psutil
import os
from typing import Dict, Any

class SystemInfoService:
    """
    Service class for gathering system and environment information.
    """

    def get_system_info(self) -> Dict[str, Any]:
        """
        Retrieves basic operating system and Python version information.
        """
        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
        }

    def get_memory_and_performance(self) -> Dict[str, Any]:
        """
        Retrieves current CPU and memory usage.
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Non-blocking call
        memory_info = psutil.virtual_memory()
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_total_gb": round(memory_info.total / (1024**3), 2),
            "memory_used_gb": round(memory_info.used / (1024**3), 2),
            "memory_percent": memory_info.percent,
        }

    def get_env_status(self) -> Dict[str, Any]:
        """
        Checks the status of essential environment variables.
        (Placeholder for actual implementation - customize with your critical env vars)
        """
        required_env_vars = ["APP_ENV", "DATABASE_URL"] # Example critical environment variables
        missing_vars = [var for var in required_env_vars if var not in os.environ]

        if missing_vars:
            return {"status": "degraded", "message": f"Missing essential environment variables: {', '.join(missing_vars)}"}
        else:
            return {"status": "ok", "message": "All essential environment variables are set"}

