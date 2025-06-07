import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger("health_monitoring", "operational")


def get_system_health() -> str:
    """
    Get a comprehensive health check of the AI coding system by analyzing recent logs.
    
    Returns:
        A JSON string containing the overall health status (healthy/degraded/unhealthy)
        and a summary of any issues found in recent operations.
    """
    try:
        # Helper function to get log file path
        def get_log_file_path(base_name: str) -> str:
            current_month = datetime.utcnow().strftime("%Y-%m")
            return f"logs/current/{base_name}_{current_month}.json"
        
        # Helper function to load and analyze logs
        def analyze_recent_logs(log_file: str, hours: int = 24) -> dict:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                recent_entries = []
                error_count = 0
                warning_count = 0
                
                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        timestamp_str = entry.get("timestamp", "").replace('Z', '+00:00')
                        log_timestamp = datetime.fromisoformat(timestamp_str)
                        
                        if log_timestamp >= time_threshold:
                            recent_entries.append(entry)
                            level = entry.get("level", "").lower()
                            if level == "error":
                                error_count += 1
                            elif level == "warning":
                                warning_count += 1
                    except (json.JSONDecodeError, ValueError):
                        continue
                
                return {
                    "recent_entries": len(recent_entries),
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "latest_errors": [e.get("message", "") for e in recent_entries if e.get("level", "").lower() == "error"][:3]
                }
            except FileNotFoundError:
                return {"error": f"Log file not found: {log_file}"}
            except Exception as e:
                return {"error": f"Failed to analyze {log_file}: {str(e)}"}
        
        # Analyze operational logs
        operational_log = get_log_file_path("operational")
        operational_stats = analyze_recent_logs(operational_log)
        
        # Analyze auto-detection logs  
        auto_detection_log = get_log_file_path("auto_detection")
        auto_detection_stats = analyze_recent_logs(auto_detection_log)
        
        # Determine overall health status
        overall_status = "healthy"
        issues = []
        
        # Check operational health
        if "error" in operational_stats:
            issues.append(f"Operational logs: {operational_stats['error']}")
            overall_status = "degraded"
        elif operational_stats.get("error_count", 0) > 0:
            issues.append(f"Found {operational_stats['error_count']} errors in operational logs")
            overall_status = "unhealthy"
        elif operational_stats.get("warning_count", 0) > 5:
            issues.append(f"High warning count: {operational_stats['warning_count']} warnings")
            overall_status = "degraded" if overall_status == "healthy" else overall_status
        
        # Check auto-detection health
        if "error" in auto_detection_stats:
            issues.append(f"Auto-detection logs: {auto_detection_stats['error']}")
            overall_status = "degraded" if overall_status == "healthy" else overall_status
        elif auto_detection_stats.get("error_count", 0) > 0:
            issues.append(f"Found {auto_detection_stats['error_count']} auto-detection errors")
            overall_status = "unhealthy"
        
        # Get latest error details if unhealthy
        error_details = []
        if overall_status == "unhealthy":
            error_details = operational_stats.get("latest_errors", [])
        
        health_report = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "operational_entries_24h": operational_stats.get("recent_entries", 0),
                "operational_errors": operational_stats.get("error_count", 0),
                "operational_warnings": operational_stats.get("warning_count", 0),
                "auto_detection_entries_24h": auto_detection_stats.get("recent_entries", 0),
                "auto_detection_errors": auto_detection_stats.get("error_count", 0)
            },
            "issues": issues,
            "recent_errors": error_details[:3] if error_details else []
        }
        
        if overall_status == "healthy":
            health_report["message"] = "✅ AI coding system is operating normally"
        elif overall_status == "degraded":
            health_report["message"] = "⚠️ AI coding system has minor issues but is functional"
        else:
            health_report["message"] = "❌ AI coding system has critical issues requiring attention"
        
        return json.dumps(health_report, indent=2)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_report = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": f"❌ Health check system failure: {str(e)}",
            "error": str(e)
        }
        return json.dumps(error_report, indent=2)
