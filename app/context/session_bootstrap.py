import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.context.auto_detection_tracker import get_metrics_summary
from app.scripts.backup_aider_history import get_backup_metrics, AiderHistoryManager
from app.scripts.aider_cost_analytics import get_cost_metrics

def bootstrap_session():
    """
    Displays a comprehensive bootstrap template with auto-detection, backup, and cost analytics metrics.
    Includes automatic backup and rotation of Aider history.
    """
    print("\n🔄 Initializing session...")
    
    # Perform backup and rotation check
    try:
        manager = AiderHistoryManager()
        if manager.should_rotate():
            print("📚 Backing up and rotating Aider history...")
            manager.rotate_history(keep_recent_entries=50)
            print("✅ History rotated successfully")
        else:
            print("📋 Aider history size is healthy")
    except Exception as e:
        print(f"⚠️ History management issue: {e}")
    
    # Get metrics
    auto_metrics = get_metrics_summary()
    backup_metrics = get_backup_metrics()
    cost_metrics = get_cost_metrics()

    # Auto-detection metrics
    total_optimizations = auto_metrics.get("total_optimizations", 0)
    average_reduction_ratio = auto_metrics.get("average_reduction_ratio", 0.0)
    total_elements_found = auto_metrics.get("total_elements_found", 0)
    sessions_optimized_today = auto_metrics.get("sessions_optimized_today", 0)
    reduction_percentage = (1.0 - average_reduction_ratio) * 100 if average_reduction_ratio > 0 else 0

    # Backup metrics
    backed_up_sessions = backup_metrics.get("backed_up_sessions", 0)
    total_cost = backup_metrics.get("total_cost", 0.0)
    current_backup_size_mb = backup_metrics.get("current_backup_size_mb", 0.0)
    backup_health = backup_metrics.get("backup_health", "Unknown")
    recent_cost_today = cost_metrics.get("cost_today", 0.0)
    recent_cost_month = cost_metrics.get("cost_month", 0.0)
    total_savings = cost_metrics.get("total_savings", 0.0)

    print("\n" + "="*80)
    print("🚀 AI-Powered Code Optimization & Cost Management Dashboard 🚀")
    print("="*80)
    print("\n⚡ Auto-Detection Performance (Real Metrics) ⚡")
    print("-" * 60)
    print(f"📊 Total Optimizations:   {total_optimizations}")
    print(f"🎯 Average Token Reduction: {reduction_percentage:.1f}%")
    print(f"🔧 Elements Detected:     {total_elements_found}")
    print(f"📅 Sessions Today:        {sessions_optimized_today}")
    print("-" * 60)
    print("\n🗄️ Backup & History Status 🗄️")
    print("-" * 60)
    print(f"📝 Backed Up Sessions: {backed_up_sessions}")
    print(f"💰 Total Cost: ${total_cost:.2f}")
    print(f"📦 Current Backup Size: {current_backup_size_mb:.2f} MB")
    print(f"🔄 Backup Health: {backup_health}")
    print("-" * 60)
    print("\n💸 Recent Costs & Savings 💸")
    print("-" * 60)
    print(f"Cost Today: ${recent_cost_today:.2f}")
    print(f"Cost This Month: ${recent_cost_month:.2f}")
    print(f"Total Savings: ${total_savings:.2f}")
    print("-" * 60)
    print("\n🎯 Focus: Intelligent context extraction for precision coding")
    print("⚡ Value: Real-time optimization, cost awareness, and history management")
    print("\n" + "="*80)
    print("Ready for optimized AI coding with cost efficiency!")
    print("="*80 + "\n")

if __name__ == '__main__':
    # Example usage for testing the bootstrap display
    bootstrap_session()
