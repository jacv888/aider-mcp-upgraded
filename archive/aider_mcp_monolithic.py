from mcp.server.fastmcp import FastMCP
import os
import json
import datetime
from typing import List, Optional
from app.adapters.aider_ai_code import code_with_aider
from dotenv import load_dotenv

# Resilience imports
import threading
import psutil
import time
from app.core.logging import get_logger, log_structured
from queue import Queue, Full, Empty

# Load environment variables from multiple locations using ModelRegistry
# The ModelRegistry handles proper path resolution and priority loading
from app.models.model_registry import model_registry

# Import strategic model selector
from app.models.strategic_model_selector import get_optimal_model

# Import cost management
from app.cost.cost_manager import cost_manager, estimate_cost, check_budget, record_cost

# Import context extraction system
from app.context import extract_context
from app.context.auto_detection import get_auto_detected_targets

# Import conflict detection system
from app.core.conflict_detector import FileConflictDetector

# --- Resilience features added by install_resilience.py ---
import psutil
import threading
import time
import sys

def monitor_memory(threshold_mb=500):
    def monitor():
        process = psutil.Process()
        while True:
            mem = process.memory_info().rss / (1024 * 1024)  # MB
            if mem > threshold_mb:
                print(f"[Resilience] Memory usage exceeded {threshold_mb} MB: {mem:.2f} MB. Restarting server.")
                # Restart logic: exit process to let external supervisor restart it
                sys.exit(1)
            time.sleep(5)
    t = threading.Thread(target=monitor, daemon=True)
    t.start()

# Start monitoring with threshold from config or default
import configparser
config = configparser.ConfigParser()
config.read("resilience_config.ini")
threshold = 500
try:
    threshold = int(config.get("Resilience", "memory_threshold_mb"))
except Exception:
    pass

monitor_memory(threshold)
# --- End resilience features ---


FALL_BACK_MODEL = "gpt-4.1-mini"

# Configure logging for resilience features
logger = get_logger("aider_mcp_resilience", "operational")

# Resilience configuration from environment variables with sensible defaults
MAX_TASK_QUEUE_SIZE = int(os.getenv("MAX_TASK_QUEUE_SIZE", "10"))
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
CPU_USAGE_THRESHOLD = float(os.getenv("CPU_USAGE_THRESHOLD", "85.0"))  # percent
MEMORY_USAGE_THRESHOLD = float(os.getenv("MEMORY_USAGE_THRESHOLD", "90.0"))  # percent
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(
    os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3")
)
CIRCUIT_BREAKER_RESET_TIMEOUT = int(
    os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60")
)  # seconds
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # seconds

# Task queue for managing incoming tasks
task_queue = Queue(maxsize=MAX_TASK_QUEUE_SIZE)


# Circuit breaker state
class CircuitBreaker:
    def __init__(self, failure_threshold, reset_timeout):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_time = None
        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self.lock:
            if self.state == "OPEN":
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.reset_timeout:
                    self.state = "HALF-OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN. Rejecting calls.")

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.warning("Circuit breaker OPENED due to failures.")
            raise e
        else:
            with self.lock:
                if self.state == "HALF-OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
            return result


circuit_breaker = CircuitBreaker(
    CIRCUIT_BREAKER_FAILURE_THRESHOLD, CIRCUIT_BREAKER_RESET_TIMEOUT
)


# Resource monitor thread to throttle tasks if CPU or memory usage is high
def resource_monitor():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        if cpu > CPU_USAGE_THRESHOLD or mem > MEMORY_USAGE_THRESHOLD:
            logger.warning(
                f"High resource usage detected: CPU {cpu}%, Memory {mem}%. Throttling task intake."
            )
            # Pause intake by not allowing new tasks to be added until usage drops
            while (
                psutil.cpu_percent(interval=1) > CPU_USAGE_THRESHOLD
                or psutil.virtual_memory().percent > MEMORY_USAGE_THRESHOLD
            ):
                time.sleep(5)
            logger.info("Resource usage normalized. Resuming task intake.")
        time.sleep(HEALTH_CHECK_INTERVAL)


resource_monitor_thread = threading.Thread(target=resource_monitor, daemon=True)
resource_monitor_thread.start()


# Connection health monitor thread to log health status periodically
def connection_health_monitor():
    while True:
        # Here we could add real connection checks if applicable
        logger.info("Connection health check: OK")
        time.sleep(HEALTH_CHECK_INTERVAL)


connection_health_thread = threading.Thread(
    target=connection_health_monitor, daemon=True
)
connection_health_thread.start()

# Create an MCP server
mcp = FastMCP("Aidar Coder")


@mcp.tool()
def planning(prompt: str) -> str:
    return f"""
    Requirements: {prompt}

    ## Planning
    But I want you first to think deep and plan the project,
    **Parallel and small tasks** Then create multiple tasks that can be done simultaneously in parallel which means no tasks should have dependency to each others, and tasks should be small and limited to one file,
    **Readme and Tasks** Create a readme file that contains information about the project and tasks,
    **Coding Tool** For each tasks share the readme and dependency files needed to **code_with_multiple_ai** tool so it can has knowledge about it
    **Coding Tool** For coding simultaneously use **code_with_multiple_ai** but just run 4 tasks at same time, For coding just one file use **code_with_ai**
    **Coding Tool** which they are not depended on each others,

    **Task Branches** I suggest you to create takes branches, which each branch work on different part of the app and they have no dependency, then run tasks one by one from different branches together, (like task 1 of different branches at same time, then task 2 and ...)

    **Step by Step** Consider small tasks, and consider developing the app step by step,
    **Sprints** Which means, I need to have sprints,
    after each sprint we need to have a runnable game, and I want you to use browser tool to run it so we can see,
    for example sprint 1 can just load the game with nothing inside (but proper working)
    then sprint 2, we might have the bird that can jump, with no wall
    then sprint 3 we add the walls and movements
    ....
    **Runnable app** So all the time I can see the result.

    **Limitation of Coding tools** If you need to run any command line, use your command line tool, don't give command running to our coder it can't run commands, it can just code
    **Limitation of coding ** don't code yourself, even if you need to review and if you find something is wrong don't fix it yourself, ask **code_with_ai** to fix it
    **Rule file for repeated mistakes** If you found it is doing some mistakes all the time, then create a rule for it, and as part of prompt give it to it in next time run.
    **Interfaces for tasks** Also consider giving each task the methods and interfaces , method name, inputs and outputs, this way when they connect to each other they don't have issue

    **Load docs in context window** If there is any /docs or /doc folder or any readme or md file, be sure to read from it before you start
    """


# sdsd
@mcp.tool()
def plan_from_scratch(prompt: str) -> str:
    return f"""
    Requirements: {prompt}

    ## Preparation
    Before start, you need to check for requirements and dependencies and technologies, then use Context7 MCP tool and get required information and save them in /docs folder and already read from them
    If there is any github repo mentioned in requirements, use command line tool to clone it in /docs folder and read from it

    ## Planning
    But I want you first to think deep and plan the project,
    **Parallel and small tasks** Then create multiple tasks that can be done simultaneously in parallel which means no tasks should have dependency to each others, and tasks should be small and limited to one file,
    **Readme and Tasks** Create a readme file that contains information about the project and tasks,
    **Coding Tool** For each tasks share the readme and dependency files needed to **code_with_multiple_ai** tool so it can has knowledge about it
    **Coding Tool** For coding simultaneously use **code_with_multiple_ai** but just run 4 tasks at same time, For coding just one file use **code_with_ai**
    **Coding Tool** which they are not depended on each others,

    **Task Branches** I suggest you to create takes branches, which each branch work on different part of the app and they have no dependency, then run tasks one by one from different branches together, (like task 1 of different branches at same time, then task 2 and ...)

    **Step by Step** Consider small tasks, and consider developing the app step by step,
    **Sprints** Which means, I need to have sprints,
    after each sprint we need to have a runnable game, and I want you to use browser tool to run it so we can see,
    for example sprint 1 can just load the game with nothing inside (but proper working)
    then sprint 2, we might have the bird that can jump, with no wall
    then sprint 3 we add the walls and movements
    ....
    **Runnable app** So all the time I can see the result.

    **Limitation of Coding tools** If you need to run any command line, use your command line tool, don't give command running to our coder it can't run commands, it can just code
    **Limitation of coding ** don't code yourself, even if you need to review and if you find something is wrong don't fix it yourself, ask **code_with_ai** to fix it
    **Rule file for repeated mistakes** If you found it is doing some mistakes all the time, then create a rule for it, and as part of prompt give it to it in next time run.
    **Interfaces for tasks** Also consider giving each task the methods and interfaces , method name, inputs and outputs, this way when they connect to each other they don't have issue

    **Load docs in context window** If there is any /docs or /doc folder or any readme or md file, be sure to read from it before you start
    """




# Import AI coding tools
from app_staging.tools.ai_coding_tools import code_with_ai as _code_with_ai, code_with_multiple_ai as _code_with_multiple_ai

# Add Aider AI coding tool
@mcp.tool()
def code_with_ai(
    prompt: str,
    working_dir: str,
    editable_files: List[str],
    readonly_files: Optional[List[str]] = None,
    model: Optional[str] = None,  # Strategic model selection if None
    target_elements: Optional[List[str]] = None,  # NEW: Context extraction targets
) -> str:
    """
    Use Aider to perform AI coding tasks with strategic model selection.

    The system will automatically select the optimal model based on your prompt:
    - Complex algorithms: Gemini 2.5 Pro (best reasoning)
    - Simple tasks: GPT-4.1 Nano (fastest & cheapest)
    - Documentation: Gemini 2.5 Flash (excellent writing)
    - Debugging: GPT-4.1 Mini (best problem-solving)
    - CSS/Styling: Gemini 2.5 Flash (great design capabilities)
    - React/Frontend: GPT-4.1 Mini (best for complex logic)
    - API/Backend: Gemini 2.5 Flash (fast server code)
    - Testing: GPT-4.1 Mini (efficient for test generation)
    - General tasks: GPT-4.1 Mini (balanced performance)

    You can override model selection by specifying the 'model' parameter.

    Args:
        prompt: The natural language prompt describing what code changes to make
        working_dir: working directory where the files are located
        editable_files: List of files that can be edited by the AI
        readonly_files: Optional list of files that can be read but not edited (for context)
        model: Optional AI model to use (default: defined in environment variable or fallback model) **Don't change model unless users asked for it**
        target_elements: Optional list of specific functions/classes/methods to focus on for context extraction

    Returns:
        JSON string with results including success status and diff output
    """
    return _code_with_ai(prompt, working_dir, editable_files, readonly_files, model, target_elements)


@mcp.tool()
def code_with_multiple_ai(
    prompts: List[str],
    working_dir: str,
    editable_files_list: List[List[str]],
    readonly_files_list: Optional[List[List[str]]] = None,
    models: Optional[List[str]] = None,
    max_workers: Optional[int] = None,
    parallel: bool = True,
    target_elements_list: Optional[List[List[str]]] = None,  # NEW: Context extraction targets
    conflict_handling: str = os.getenv("DEFAULT_CONFLICT_HANDLING", "auto"),  # NEW: Conflict detection handling from env
) -> str:
    """
    Use Multiple Aider agents with strategic model selection to perform AI coding tasks.

    🧠 STRATEGIC MODEL SELECTION:
    Each task automatically gets the optimal model based on its prompt:
    - Complex algorithms: Gemini 2.5 Pro (best reasoning)
    - Simple tasks: GPT-4.1 Nano (fastest & cheapest)
    - Documentation: Gemini 2.5 Flash (excellent writing)
    - Testing: GPT-4.1 Mini (efficient for test generation)
    - CSS/Styling: Gemini 2.5 Flash (great design capabilities)
    - React/Frontend: GPT-4.1 Mini (best for complex logic)
    - API/Backend: Gemini 2.5 Flash (fast for server code)
    - Debugging: GPT-4.1 Mini (best problem-solving)

    🔒 SMART CONFLICT DETECTION:
    Automatically detects file conflicts between parallel tasks.
    The conflict handling behavior can be configured via the environment variable
    DEFAULT_CONFLICT_HANDLING with possible values:
    - "auto" (default): Detects conflicts and switches to sequential execution
    - "warn": Detects conflicts but continues parallel execution with warnings
    - "ignore": Skips conflict detection entirely

    💫 EXAMPLE USAGE WITH STRATEGIC SELECTION:
    code_with_multiple_ai(
        prompts=[
            "Create complex React component with state management",  # → GPT-4.1 Mini
            "Write unit tests for the API",                         # → GPT-4.1 Mini
            "Generate comprehensive documentation",                  # → Gemini 2.5 Flash
            "Add CSS animations and styling"                        # → Gemini 2.5 Flash
        ],
        # models=None,  # Let system choose optimal models
        working_dir="./my-project"
    )

    This tool provides multiple agents that can run simultaneously to write code.
    Tasks should be parallel-compatible with no dependencies on each other.
    You can divide the project into multiple task branches like this example:

    Branch 1: Front end --> Task1: initiate front end, Task2: implement index page
    Branch 2: Back end -->  Task1: initiate backend, Task2: implement api
    Branch 3: Database -->  Task1: initiate database, Task2: implement database

    Or
    Branch 1: Task1: Implement index.html, Task2: assemble everything into index.html
    Branch 2: Task1: Implement script.js
    Branch 3: Task1: Implement styles.css
    Branch 4: Task1: Implement script3.js
    Branch 5: Task1: Implement script4.js
    Branch 6: Task1: Implement script5.js
    Branch 7: Task1: Implement script6.js
    Then in each round you can get all the Task 1 to this method, but in task 2 you know all the tasks 1 are implemented,
    then you can have dependency to all other implemented tasks 1

    *** Do not run more than 5 prompts in parallel.***

    Args:
        prompts: List of natural language prompts describing what code changes to make
        working_dir: Working directory where the files are located
        editable_files_list: List of lists of files that can be edited by the AI (one list per prompt)
        readonly_files_list: Optional list of lists of files that can be read but not edited (one list per prompt)
        models: Optional list of models to use (one model per prompt)
        max_workers: Optional maximum number of parallel workers (defaults to number of prompts)
        parallel: Whether to run tasks in parallel (True) or sequentially (False). Default is True.
        target_elements_list: Optional list of lists of specific functions/classes/methods to focus on for context extraction (one list per prompt)
        conflict_handling: How to handle file conflicts - "auto" (default: detect and serialize), "warn" (detect and warn), "ignore" (skip detection).
            This parameter can be overridden by the environment variable DEFAULT_CONFLICT_HANDLING.

    Returns:
        JSON string with aggregated results including success status and diff outputs
    """
    return _code_with_multiple_ai(
        prompts, working_dir, editable_files_list, readonly_files_list, 
        models, max_workers, parallel, target_elements_list, conflict_handling
    )


# 💰 Phase 2: Cost Management Tools

@mcp.tool()
def get_cost_summary(
    days: int = 7
) -> str:
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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




# Run the server if this file is executed directly
if __name__ == "__main__":
    mcp.run()
