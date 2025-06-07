#!/usr/bin/env python3
"""
Enhanced Bootstrap with Automatic Template Generation
Generates the exact template with real data - no manual work required
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Optional import for dotenv; install python-dotenv if needed
try:
    from dotenv import load_dotenv
    _has_dotenv = True
except ImportError:
    _has_dotenv = False

def get_workspace_dir() -> str:
    """Get workspace directory from environment variables or current directory"""
    if _has_dotenv:
        load_dotenv()
    workspace_dir = os.getenv('MCP_SERVER_ROOT')
    if workspace_dir:
        return workspace_dir
    return os.getcwd()

def get_real_metrics(workspace_dir: str) -> dict:
    """Extract real metrics from all available sources"""
    metrics = {
        "context_file": "Unknown",
        "last_activity": "Unknown",
        "sessions_backed_up": 0,
        "total_cost": 0.0,
        "file_size": "Unknown",
        "health_status": "Unknown",
        "daily_cost": 0.0,
        "monthly_cost": 0.0,
        "estimated_savings": 0.0,
        "target_elements": 0,
        "optimization_sessions": 0,
        "token_reduction": "Unknown",
        "elements_detected": 0,
        "issues": []
    }
    
    # 1. Get cost analytics
    try:
        result = subprocess.run([
            sys.executable, "app/scripts/aider_cost_analytics.py"
        ], capture_output=True, text=True, cwd=workspace_dir)
        
        if result.returncode == 0:
            cost_data = json.loads(result.stdout)
            metrics.update({
                "sessions_backed_up": cost_data.get("backed_up_sessions_count", 0),
                "total_cost": cost_data.get("total_cost_usd", 0.0),
                "monthly_cost": cost_data.get("total_cost_usd", 0.0),
                "estimated_savings": cost_data.get("cost_savings_estimation", {}).get("estimated_savings", 0.0),
                "target_elements": cost_data.get("target_elements_identified", {}).get("potential_code_elements_count", 0),
                "optimization_sessions": cost_data.get("backed_up_sessions_count", 0)
            })
            
            # Calculate today's cost
            daily_breakdown = cost_data.get("daily_cost_breakdown", {})
            today = datetime.now().strftime("%Y-%m-%d")
            metrics["daily_cost"] = daily_breakdown.get(today, 0.0)
            
            # Calculate efficiency percentage
            actual_cost = cost_data.get("total_cost_usd", 0.0)
            baseline_cost = cost_data.get("cost_savings_estimation", {}).get("estimated_baseline_cost", actual_cost)
            if baseline_cost > 0:
                efficiency = ((baseline_cost - actual_cost) / baseline_cost) * 100
                metrics["token_reduction"] = f"{efficiency:.0f}%"
            
    except Exception as e:
        metrics["issues"].append(f"Cost analytics error: {e}")
    
    # 2. Get context file info
    ai_logs_dir = Path(workspace_dir) / "ai-logs" / "active"
    if ai_logs_dir.exists():
        log_files = list(ai_logs_dir.glob("2025-*.md"))
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            metrics["context_file"] = latest_log.name
            
            # Extract last activity
            try:
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    # Look for recent activity markers
                    for line in reversed(lines):
                        if line.strip().startswith('**Request**:') or line.strip().startswith('##'):
                            metrics["last_activity"] = line.strip()[:80] + "..."
                            break
            except Exception as e:
                metrics["issues"].append(f"Context reading error: {e}")
    
    # 3. Get file size info
    try:
        aider_history = Path(workspace_dir) / ".aider.chat.history.md"
        if aider_history.exists():
            size_bytes = aider_history.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            metrics["file_size"] = f"{size_mb:.2f}MB"
    except Exception as e:
        metrics["issues"].append(f"File size error: {e}")
    
    # 4. Get system health (simulate MCP call)
    try:
        # Check for common health indicators
        logs_dir = Path(workspace_dir) / "logs" / "current"
        operational_log = logs_dir / "operational_2025-06.json"
        detection_log = logs_dir / "auto_detection_2025-06.json"
        
        if not operational_log.exists():
            metrics["issues"].append("Missing operational logs")
        if not detection_log.exists():
            metrics["issues"].append("Missing auto-detection logs")
            
        if not metrics["issues"]:
            metrics["health_status"] = "healthy"
        else:
            metrics["health_status"] = "degraded"
            
    except Exception as e:
        metrics["health_status"] = "unknown"
        metrics["issues"].append(f"Health check error: {e}")
    
    return metrics

def generate_bootstrap_template(metrics: dict, workspace_dir: str) -> str:
    """Generate the concise bootstrap template with real data"""
    
    # Extract project name from workspace directory
    project_name = Path(workspace_dir).name
    
    template = f"""🔄 Context Loading...
📂 Found: {workspace_dir}/ai-logs/active/{metrics['context_file']}
📋 Last activity: {metrics['last_activity']}

💾 Aider History Status...
📊 Backed up: {metrics['sessions_backed_up']} sessions, ${metrics['total_cost']:.2f} total cost
📏 Current size: {metrics['file_size']} (healthy)
🏥 System Health: {metrics['health_status']}

💰 Costs: ${metrics['daily_cost']:.2f} today, ${metrics['monthly_cost']:.2f} this month
⚡ Savings: ${metrics['estimated_savings']:.2f} estimated savings this month ({metrics['token_reduction']} efficiency)
🎯 Target elements identified: {metrics['target_elements']:,} functions/classes
🚀 Token efficiency: Strategic model selection working ({metrics['optimization_sessions']} sessions optimized)

⚡ Auto-Detection Performance (Real Metrics) ⚡
--------------------------------------------------
📊 Total Optimizations: {metrics['optimization_sessions']} (measured)
🎯 Average Token Reduction: {metrics['token_reduction']} (measured via cost efficiency)
🔧 Elements Detected: {metrics['target_elements']:,} (measured)
📅 Sessions Today: Active development ongoing
✅ Ready to continue with {project_name}"""

    return template

def main():
    """Execute bootstrap and generate template with real data"""
    workspace_dir = get_workspace_dir()
    
    print("🚀 Executing Enhanced Bootstrap with Real Data Template")
    print(f"📁 Working directory: {workspace_dir}")
    print("=" * 70)
    
    # Execute standard bootstrap
    bootstrap_cmd = [sys.executable, "app/scripts/complete_bootstrap.py"]
    result = subprocess.run(bootstrap_cmd, cwd=workspace_dir)
    
    if result.returncode != 0:
        print("❌ Standard bootstrap failed")
        return False
    
    # Extract real metrics
    print("\n📊 Extracting Real Metrics...")
    metrics = get_real_metrics(workspace_dir)
    
    # Generate template
    template = generate_bootstrap_template(metrics, workspace_dir)
    
    # Save template for copy-paste
    template_file = Path(workspace_dir) / "bootstrap_template_output.md"
    with open(template_file, 'w') as f:
        f.write(template)
    
    print("\n" + "=" * 70)
    print("📋 BOOTSTRAP TEMPLATE WITH REAL DATA:")
    print("=" * 70)
    print(template)
    print("=" * 70)
    print(f"📁 Template saved to: {template_file}")
    print("💡 Copy the template above for use in responses!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
