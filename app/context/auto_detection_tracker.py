import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

_TRACKER_FILE = os.path.expanduser("~/.auto_detection_metrics.json")

def track_auto_detection(original_prompt_length: int, target_elements_found: int, optimized_prompt_length: int, session_context: str):
    if target_elements_found == 0:
        return
    reduction_ratio = optimized_prompt_length / original_prompt_length if original_prompt_length else 1.0
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "original_prompt_length": original_prompt_length,
        "target_elements_found": target_elements_found,
        "optimized_prompt_length": optimized_prompt_length,
        "reduction_ratio": reduction_ratio,
        "session_context": session_context,
    }
    data = []
    if os.path.exists(_TRACKER_FILE):
        try:
            with open(_TRACKER_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception):
            # Handle corrupted or unreadable file by starting fresh
            data = []
    data.append(entry)
    with open(_TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_metrics_summary() -> Dict[str, Any]:
    """
    Reads the auto-detection metrics file and returns a summary.

    Returns:
        Dict[str, Any]: A dictionary containing summary metrics:
            - total_optimizations (int): Total number of auto-detection optimizations recorded.
            - average_reduction_ratio (float): Average prompt length reduction ratio.
            - total_elements_found (int): Total target elements found across all optimizations.
            - sessions_optimized_today (int): Number of sessions optimized today (UTC).
    """
    data = []
    if os.path.exists(_TRACKER_FILE):
        try:
            with open(_TRACKER_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception):
            # Handle corrupted or unreadable file gracefully
            data = []

    total_optimizations = len(data)
    total_reduction_ratio = 0.0
    total_elements_found = 0
    sessions_optimized_today = 0
    
    today_utc = datetime.utcnow().date()

    for entry in data:
        total_reduction_ratio += entry.get("reduction_ratio", 0.0)
        total_elements_found += entry.get("target_elements_found", 0)
        
        try:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date == today_utc:
                sessions_optimized_today += 1
        except (ValueError, KeyError):
            # Skip entries with malformed timestamps
            pass

    average_reduction_ratio = total_reduction_ratio / total_optimizations if total_optimizations > 0 else 0.0

    return {
        "total_optimizations": total_optimizations,
        "average_reduction_ratio": round(average_reduction_ratio, 4),
        "total_elements_found": total_elements_found,
        "sessions_optimized_today": sessions_optimized_today,
    }
