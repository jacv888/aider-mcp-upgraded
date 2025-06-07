#!/usr/bin/env python3
"""
Bootstrap Status Display
Shows visual bootstrap status in terminal prompt
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

def get_bootstrap_status_indicator() -> str:
    """Return a visual indicator for bootstrap status"""
    workspace_dir = os.getcwd()
    bootstrap_marker = Path(workspace_dir) / ".session_bootstrap_complete"
    
    if not bootstrap_marker.exists():
        return "🔴 NO-BOOTSTRAP"
    
    try:
        with open(bootstrap_marker, 'r') as f:
            data = json.load(f)
            
        last_bootstrap = datetime.fromisoformat(data['timestamp'])
        age = datetime.now() - last_bootstrap
        
        if age < timedelta(hours=1):
            return "🟢 FRESH-BOOTSTRAP"
        elif age < timedelta(hours=4):
            return "🟡 VALID-BOOTSTRAP"
        else:
            return "🟠 EXPIRED-BOOTSTRAP"
            
    except:
        return "🔴 INVALID-BOOTSTRAP"

def display_bootstrap_banner():
    """Display bootstrap status banner"""
    status = get_bootstrap_status_indicator()
    
    print("┌" + "─" * 50 + "┐")
    print(f"│  Bootstrap Status: {status:<25} │")
    print("└" + "─" * 50 + "┘")
    
    if "🔴" in status or "🟠" in status:
        print("⚠️  Bootstrap required before AI coding tasks!")
        print("🔧 Run: python3 app/scripts/complete_bootstrap.py")

if __name__ == "__main__":
    display_bootstrap_banner()
