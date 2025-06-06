import json
import os
import datetime
from typing import List
from app.cost.cost_manager import cost_manager, estimate_cost, check_budget
from app.models.strategic_model_selector import get_optimal_model
from app.core.logging import get_logger

logger = get_logger("cost_management_tools", "operational")


def get_cost_summary(days: int = 7) -> str:
    """
    Get cost summary and analytics for specified period.
    
    Args:
        days: Number of days to include in summary (default: 7)
        
    Returns:
        JSON string with cost summary including total cost, task count, 
        average cost per task, and breakdown by model
    """
    try:
        summary = cost_manager.get_cost_summary(days)
        
        # Add human-readable summary
        summary["human_summary"] = {
            "period": f"Last {days} days",
            "total_spent": f"${summary['total_cost']:.4f}",
            "average_per_task": f"${summary['average_cost']:.4f}" if summary['task_count'] > 0 else "$0.00",
            "total_tokens": f"{summary['total_tokens']:,}",
            "tasks_completed": summary['task_count']
        }
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        error_response = {
            "success": False,
            "error": f"Failed to get cost summary: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response, indent=2)


def estimate_task_cost(
    prompt: str,
    file_paths: List[str] = None,
    model: str = None
) -> str:
    """
    Estimate cost for a task before execution.
    
    Args:
        prompt: The task prompt to estimate cost for
        file_paths: Optional list of file paths to include in cost calculation
        model: Optional specific model to use (defaults to strategic selection)
        
    Returns:
        JSON string with cost estimate including token counts and pricing breakdown
    """
    try:
        if file_paths is None:
            file_paths = []
            
        if model is None:
            model = get_optimal_model(prompt)
        
        # Read file contents if paths provided
        files_content = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files_content.append(f.read())
                except Exception:
                    logger.warning(f"Could not read file: {file_path}")
        
        # Get cost estimate
        estimate = estimate_cost(prompt, files_content, model, "code_generation")
        
        # Check budget
        budget_ok, budget_message = check_budget(estimate.total_cost)
        
        result = {
            "success": True,
            "cost_estimate": {
                "total_cost": estimate.total_cost,
                "input_cost": estimate.input_cost,
                "estimated_output_cost": estimate.estimated_output_cost,
                "input_tokens": estimate.input_tokens,
                "estimated_output_tokens": estimate.estimated_output_tokens,
                "total_tokens": estimate.total_tokens,
                "model": estimate.model
            },
            "budget_check": {
                "within_budget": budget_ok,
                "message": budget_message if budget_message else "Cost is within budget limits"
            },
            "human_readable": {
                "estimated_cost": f"${estimate.total_cost:.4f}",
                "model_used": model,
                "token_breakdown": f"{estimate.input_tokens:,} input + ~{estimate.estimated_output_tokens:,} output = {estimate.total_tokens:,} total tokens"
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error estimating task cost: {e}")
        error_response = {
            "success": False,
            "error": f"Failed to estimate cost: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response, indent=2)


def get_budget_status() -> str:
    """
    Get current budget configuration and status.
    
    Returns:
        JSON string with budget limits, current usage, and remaining budget
    """
    try:
        # Get current budget limits
        budget_limits = cost_manager.budget_limits
        
        # Get usage for different periods
        daily_summary = cost_manager.get_cost_summary(1)
        monthly_summary = cost_manager.get_cost_summary(30)
        
        result = {
            "success": True,
            "budget_limits": {
                "max_cost_per_task": f"${budget_limits['max_cost_per_task']:.2f}",
                "max_daily_cost": f"${budget_limits['max_daily_cost']:.2f}",
                "max_monthly_cost": f"${budget_limits['max_monthly_cost']:.2f}",
                "warning_threshold": f"${budget_limits['warning_threshold']:.2f}"
            },
            "current_usage": {
                "today": f"${daily_summary['total_cost']:.4f}",
                "this_month": f"${monthly_summary['total_cost']:.4f}",
                "tasks_today": daily_summary['task_count'],
                "tasks_this_month": monthly_summary['task_count']
            },
            "remaining_budget": {
                "daily": f"${max(0, budget_limits['max_daily_cost'] - daily_summary['total_cost']):.2f}",
                "monthly": f"${max(0, budget_limits['max_monthly_cost'] - monthly_summary['total_cost']):.2f}"
            },
            "status": {
                "daily_usage_percent": (daily_summary['total_cost'] / budget_limits['max_daily_cost'] * 100) if budget_limits['max_daily_cost'] > 0 else 0,
                "monthly_usage_percent": (monthly_summary['total_cost'] / budget_limits['max_monthly_cost'] * 100) if budget_limits['max_monthly_cost'] > 0 else 0
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting budget status: {e}")
        error_response = {
            "success": False,
            "error": f"Failed to get budget status: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response, indent=2)


def export_cost_report(
    days: int = 30,
    format: str = "json"
) -> str:
    """
    Export detailed cost report for analysis.
    
    Args:
        days: Number of days to include in report (default: 30)
        format: Export format - "json", "summary", or "csv" (default: json)
        
    Returns:
        Detailed cost report. CSV format creates file in /costs directory.
    """
    try:
        if format == "summary":
            # Human-readable summary format
            summary = cost_manager.get_cost_summary(days)
            
            report_lines = [
                f"📊 Cost Report - Last {days} Days",
                "=" * 40,
                f"Total Spent: ${summary['total_cost']:.4f}",
                f"Tasks Completed: {summary['task_count']}",
                f"Average per Task: ${summary['average_cost']:.4f}" if summary['task_count'] > 0 else "Average per Task: $0.00",
                f"Total Tokens: {summary['total_tokens']:,}",
                "",
                "📈 Cost by Model:",
            ]
            
            for model, stats in summary.get('cost_by_model', {}).items():
                report_lines.append(f"  {model}: ${stats['total_cost']:.4f} ({stats['task_count']} tasks)")
            
            return "\n".join(report_lines)
        elif format == "csv":
            # Export to CSV file - ONLY created on request
            try:
                from app.cost.cost_storage import cost_storage
                
                # Filter costs by days
                from datetime import timedelta
                cutoff_date = datetime.datetime.now() - timedelta(days=days)
                filtered_costs = [c for c in cost_manager.cost_history if c.timestamp >= cutoff_date]
                
                output_file = cost_storage.export_to_csv(filtered_costs)
                
                return json.dumps({
                    "success": True,
                    "message": f"Cost data exported to CSV",
                    "file": str(output_file),
                    "records": len(filtered_costs),
                    "period_days": days,
                    "note": "CSV files are saved in /costs directory"
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": f"CSV export failed: {str(e)}"
                }, indent=2)
        else:
            # Full JSON export
            return cost_manager.export_cost_report(days)
            
    except Exception as e:
        logger.error(f"Error exporting cost report: {e}")
        error_response = {
            "success": False,
            "error": f"Failed to export cost report: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response, indent=2)
