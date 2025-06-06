"""
Clean MCP Server Orchestrator

This module replaces the monolithic aider_mcp.py file by importing
and registering all extracted tool functions in a clean, focused manner.
"""

from mcp.server.fastmcp import FastMCP
import os

# Import all extracted tool modules
from app.tools.planning_tools import planning, plan_from_scratch
from app.tools.ai_coding_tools import code_with_ai, code_with_multiple_ai
from app.tools.cost_management_tools import (
    get_cost_summary, 
    estimate_task_cost, 
    get_budget_status, 
    export_cost_report
)
from app.tools.health_monitoring_tools import get_system_health

# Import infrastructure components
from app.core.resilience import resilience_manager

# Create MCP server instance
mcp = FastMCP("Aider Coder")

# Register planning tools
@mcp.tool()
def planning(prompt: str) -> str:
    """
    Generate a project planning response with task breakdown and guidance.
    """
    from app.tools.planning_tools import planning as planning_func
    return planning_func(prompt)

@mcp.tool()
def plan_from_scratch(prompt: str) -> str:
    """
    Generate a comprehensive project planning response with preparation phase.
    """
    from app.tools.planning_tools import plan_from_scratch as plan_from_scratch_func
    return plan_from_scratch_func(prompt)

# Register AI coding tools
@mcp.tool()
def code_with_ai(
    prompt: str,
    working_dir: str,
    editable_files: list,
    readonly_files: list = None,
    model: str = None,
    target_elements: list = None,
) -> str:
    """
    Use Aider to perform AI coding tasks with strategic model selection.
    """
    from app.tools.ai_coding_tools import code_with_ai as code_with_ai_func
    return code_with_ai_func(
        prompt=prompt,
        working_dir=working_dir, 
        editable_files=editable_files,
        readonly_files=readonly_files,
        model=model,
        target_elements=target_elements
    )

@mcp.tool()
def code_with_multiple_ai(
    prompts: list,
    working_dir: str,
    editable_files_list: list,
    readonly_files_list: list = None,
    models: list = None,
    max_workers: int = None,
    parallel: bool = True,
    target_elements_list: list = None,
    conflict_handling: str = "auto",
) -> str:
    """
    Use Multiple Aider agents with strategic model selection.
    """
    from app.tools.ai_coding_tools import code_with_multiple_ai as code_with_multiple_ai_func
    return code_with_multiple_ai_func(
        prompts=prompts,
        working_dir=working_dir,
        editable_files_list=editable_files_list,
        readonly_files_list=readonly_files_list,
        models=models,
        max_workers=max_workers,
        parallel=parallel,
        target_elements_list=target_elements_list,
        conflict_handling=conflict_handling
    )

# Register cost management tools
@mcp.tool()
def get_cost_summary(days: int = 7) -> str:
    """
    Get cost summary and analytics for specified period.
    """
    from app.tools.cost_management_tools import get_cost_summary as get_cost_summary_func
    return get_cost_summary_func(days)

@mcp.tool()
def estimate_task_cost(
    prompt: str,
    file_paths: list = None,
    model: str = None
) -> str:
    """
    Estimate cost for a task before execution.
    """
    from app.tools.cost_management_tools import estimate_task_cost as estimate_task_cost_func
    return estimate_task_cost_func(prompt, file_paths, model)

@mcp.tool()
def get_budget_status() -> str:
    """
    Get current budget configuration and status.
    """
    from app.tools.cost_management_tools import get_budget_status as get_budget_status_func
    return get_budget_status_func()

@mcp.tool()
def export_cost_report(days: int = 30, format: str = "json") -> str:
    """
    Export detailed cost report for analysis.
    """
    from app.tools.cost_management_tools import export_cost_report as export_cost_report_func
    return export_cost_report_func(days, format)

# Register health monitoring tools
@mcp.tool()
def get_system_health() -> str:
    """
    Get a comprehensive health check of the AI coding system.
    """
    from app.tools.health_monitoring_tools import get_system_health as get_system_health_func
    return get_system_health_func()

# Initialize resilience manager
def initialize_server():
    """Initialize the MCP server with all necessary infrastructure."""
    # Resilience manager is automatically initialized as singleton
    print("🚀 MCP Server initialized with modular architecture")
    print("📋 Registered tools:")
    print("  - Planning: planning_tool, plan_from_scratch_tool")
    print("  - AI Coding: code_with_ai_tool, code_with_multiple_ai_tool") 
    print("  - Cost Management: get_cost_summary_tool, estimate_task_cost_tool, get_budget_status_tool, export_cost_report_tool")
    print("  - Health Monitoring: get_system_health_tool")
    print("✅ Server ready for operation")

# Main server runner
def run_server():
    """Run the MCP server."""
    initialize_server()
    mcp.run()

if __name__ == "__main__":
    run_server()
