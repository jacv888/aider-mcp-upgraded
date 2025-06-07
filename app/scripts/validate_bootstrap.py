#!/usr/bin/env python3
"""
Bootstrap Validation Tool
Ensures Session Bootstrap Template is executed before AI coding tasks
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

class BootstrapValidator:
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.getcwd()
        self.bootstrap_marker = Path(self.workspace_dir) / ".session_bootstrap_complete"
        self.ai_logs_dir = Path(self.workspace_dir) / "ai-logs" / "active"
        
    def check_bootstrap_status(self) -> dict:
        """Check if bootstrap was completed for current session"""
        result = {
            "bootstrap_completed": False,
            "session_valid": False,
            "missing_steps": [],
            "last_bootstrap": None,
            "issues": []
        }
        
        # Check if marker file exists and is recent (within last 4 hours)
        if self.bootstrap_marker.exists():
            try:
                with open(self.bootstrap_marker, 'r') as f:
                    data = json.load(f)
                    
                last_bootstrap = datetime.fromisoformat(data['timestamp'])
                result["last_bootstrap"] = last_bootstrap.isoformat()
                
                # Check if bootstrap is recent (4 hour session window)
                if datetime.now() - last_bootstrap < timedelta(hours=4):
                    result["session_valid"] = True
                    result["bootstrap_completed"] = data.get('completed', False)
                else:
                    result["issues"].append("Bootstrap session expired (>4 hours old)")
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                result["issues"].append(f"Invalid bootstrap marker: {e}")
        else:
            result["issues"].append("No bootstrap marker found")
            
        # Validate bootstrap steps were completed
        result["missing_steps"] = self._check_bootstrap_steps(result)
        
        return result
        
    def _check_bootstrap_steps(self, result: dict) -> list:
        """Check which bootstrap steps are missing"""
        missing = []
        
        # Check aider history backup
        backup_dir = Path(self.workspace_dir) / "ai-logs" / "aider-history-archive"
        if not backup_dir.exists() or not list(backup_dir.glob("aider_history_*.md")):
            missing.append("aider_history_backup")
            
        # Check session log exists
        if not self.ai_logs_dir.exists():
            missing.append("session_context")
        else:
            recent_logs = list(self.ai_logs_dir.glob("2025-*.md"))
            if not recent_logs:
                missing.append("session_context")
                
        # Check health monitoring (marker should contain health status)
        if result.get("bootstrap_completed"):
            try:
                with open(self.bootstrap_marker, 'r') as f:
                    data = json.load(f)
                    if 'health_status' not in data:
                        missing.append("health_check")
            except:
                missing.append("health_check")
                
        return missing
        
    def enforce_bootstrap(self, force: bool = False) -> bool:
        """Enforce bootstrap completion before proceeding"""
        status = self.check_bootstrap_status()
        
        if force:
            print("⚠️  BOOTSTRAP ENFORCEMENT OVERRIDDEN!")
            self._log_violation("Force override used")
            return True
            
        if status["bootstrap_completed"] and status["session_valid"]:
            print("✅ Bootstrap validation passed")
            return True
            
        # Bootstrap not completed - block execution
        print("🚨 BOOTSTRAP PROTOCOL VIOLATION DETECTED!")
        print("=" * 50)
        
        if not status["session_valid"]:
            print("❌ Session bootstrap required")
            print(f"   Last bootstrap: {status.get('last_bootstrap', 'Never')}")
            
        if status["missing_steps"]:
            print("❌ Missing bootstrap steps:")
            for step in status["missing_steps"]:
                print(f"   - {step}")
                
        print("\n🔧 REQUIRED ACTIONS:")
        print("1. Execute: python3 app/scripts/backup_aider_history.py")
        print("2. Execute: get_system_health()")
        print("3. Load project context from ai-logs/active/")
        print("4. Run: python3 app/scripts/validate_bootstrap.py --complete")
        print("\n💡 Or use: python3 app/scripts/complete_bootstrap.py")
        print("\n⚠️  Force override: --force (not recommended)")
        
        return False
        
    def mark_bootstrap_complete(self, health_status: str = "unknown"):
        """Mark bootstrap as completed"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "completed": True,
            "health_status": health_status,
            "workspace": self.workspace_dir,
            "validator_version": "1.0"
        }
        
        with open(self.bootstrap_marker, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"✅ Bootstrap marked complete at {data['timestamp']}")
        
    def _log_violation(self, reason: str):
        """Log bootstrap protocol violations"""
        log_dir = Path(self.workspace_dir) / "ai-logs" / "violations"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        violation = {
            "timestamp": datetime.now().isoformat(),
            "type": "bootstrap_protocol_violation",
            "reason": reason,
            "workspace": self.workspace_dir
        }
        
        log_file = log_dir / f"violation_{datetime.now().strftime('%Y%m%d')}.json"
        violations = []
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                violations = json.load(f)
                
        violations.append(violation)
        
        with open(log_file, 'w') as f:
            json.dump(violations, f, indent=2)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Bootstrap Validation Tool")
    parser.add_argument("--check", action="store_true", help="Check bootstrap status")
    parser.add_argument("--enforce", action="store_true", help="Enforce bootstrap (blocks if not complete)")
    parser.add_argument("--complete", action="store_true", help="Mark bootstrap as complete")
    parser.add_argument("--health", default="unknown", help="Health status to record")
    parser.add_argument("--force", action="store_true", help="Force override (emergency use)")
    parser.add_argument("--workspace", help="Workspace directory")
    
    args = parser.parse_args()
    
    validator = BootstrapValidator(args.workspace)
    
    if args.check:
        status = validator.check_bootstrap_status()
        print(json.dumps(status, indent=2))
        
    elif args.enforce:
        if not validator.enforce_bootstrap(args.force):
            sys.exit(1)
            
    elif args.complete:
        validator.mark_bootstrap_complete(args.health)
        
    else:
        # Default: check and enforce
        if not validator.enforce_bootstrap(args.force):
            sys.exit(1)

if __name__ == "__main__":
    main()
