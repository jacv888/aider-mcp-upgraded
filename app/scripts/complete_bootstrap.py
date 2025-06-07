#!/usr/bin/env python3
"""
Complete Bootstrap Script
Automatically executes the full Session Bootstrap Template
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd: list, description: str) -> tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True, result.stdout
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False, "Command timed out"
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False, str(e)

def complete_bootstrap(workspace_dir: str = None):
    """Execute complete bootstrap sequence"""
    workspace_dir = workspace_dir or os.getcwd()
    print("🚀 Executing Complete Session Bootstrap Template")
    print("=" * 60)
    
    # Step 1: Backup Aider History
    backup_cmd = [sys.executable, "app/scripts/backup_aider_history.py"]
    backup_success, backup_output = run_command(backup_cmd, "Aider History Backup")
    
    # Step 2: Load project context
    ai_logs_dir = Path(workspace_dir) / "ai-logs" / "active"
    context_loaded = False
    latest_context = "No active session logs found"
    
    if ai_logs_dir.exists():
        log_files = list(ai_logs_dir.glob("2025-*.md"))
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            print(f"📂 Loading context from: {latest_log.name}")
            try:
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    # Extract last few entries for summary
                    context_lines = [line for line in lines[-50:] if line.strip().startswith('##')]
                    latest_context = context_lines[-1].strip() if context_lines else "Context file exists but no recent entries"
                    context_loaded = True
                    print(f"📋 Latest activity: {latest_context}")
            except Exception as e:
                latest_context = f"Error reading context: {e}"
    
    # Step 3: System Health Check (simulate since we can't import MCP tools here)
    print("🏥 System Health Check...")
    health_status = "unknown"
    
    # Check for common issues
    issues = []
    
    # Check logs directory structure
    logs_dir = Path(workspace_dir) / "logs" / "current"
    if not logs_dir.exists():
        issues.append("Missing logs/current directory")
        
    operational_log = logs_dir / "operational_2025-06.json"
    detection_log = logs_dir / "auto_detection_2025-06.json"
    
    if not operational_log.exists():
        issues.append("Missing operational logs")
    if not detection_log.exists():
        issues.append("Missing auto-detection logs")
        
    # Check key directories
    required_dirs = ["app/core", "app/tools", "app/scripts"]
    for dir_path in required_dirs:
        if not Path(workspace_dir, dir_path).exists():
            issues.append(f"Missing {dir_path} directory")
    
    if not issues:
        health_status = "healthy"
        print("✅ System health: Healthy")
    else:
        health_status = "degraded"
        print("⚠️  System health: Degraded")
        for issue in issues:
            print(f"   - {issue}")
    
    # Step 4: Display metrics summary
    print("\n📊 Session Bootstrap Summary:")
    print("─" * 40)
    
    if backup_success:
        # Extract metrics from backup output
        lines = backup_output.split('\n')
        for line in lines:
            if 'Sessions in current file:' in line or 'Current file size:' in line:
                print(f"💾 {line.strip()}")
    
    print(f"🏥 Health Status: {health_status}")
    print(f"📋 Context Status: {'✅ Loaded' if context_loaded else '❌ Missing'}")
    print(f"📁 Workspace: {workspace_dir}")
    print(f"⏰ Bootstrap Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 5: Mark bootstrap complete
    validator_cmd = [sys.executable, "app/scripts/validate_bootstrap.py", "--complete", "--health", health_status]
    validator_success, _ = run_command(validator_cmd, "Bootstrap Validation Marker")
    
    print("\n🎯 Bootstrap Template Complete!")
    print("=" * 60)
    
    if backup_success and context_loaded and validator_success:
        print("✅ All bootstrap steps completed successfully")
        print("🚀 Ready for AI coding tasks with full context")
        return True
    else:
        print("⚠️  Bootstrap completed with some issues")
        print("💡 Review output above for any problems")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete Bootstrap Execution")
    parser.add_argument("--workspace", help="Workspace directory")
    parser.add_argument("--force", action="store_true", help="Force bootstrap even if recently completed")
    
    args = parser.parse_args()
    
    # Check if bootstrap was already completed recently
    if not args.force:
        validator_cmd = [sys.executable, "app/scripts/validate_bootstrap.py", "--check"]
        try:
            result = subprocess.run(validator_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                status = json.loads(result.stdout)
                if status.get("bootstrap_completed") and status.get("session_valid"):
                    print("✅ Bootstrap already completed for this session")
                    print("💡 Use --force to re-run bootstrap")
                    return
        except:
            pass  # Continue with bootstrap if check fails
    
    success = complete_bootstrap(args.workspace)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
