import os
import json
import time
import uuid
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from queue import Queue, Full, Empty
import traceback
import re

# Import strategic model selector
from app.models.strategic_model_selector import get_optimal_model

# Import cost management
from app.cost.cost_manager import cost_manager, estimate_cost, check_budget, record_cost, generate_task_name

# Import context extraction system
from app.context import extract_context
from app.context.auto_detection import get_auto_detected_targets

# Import conflict detection system
from app.core.conflict_detector import FileConflictDetector

# Import aider adapter
from app.adapters.aider_ai_code import code_with_aider

# Import logging
from app.core.logging import get_logger, log_structured

# Import Config class
from app.core.config import get_config

# Configure logging
logger = get_logger("ai_coding_tools", "operational")

# Helper to load and cache configuration
_cached_config = None
def _get_cached_config():
    global _cached_config
    if _cached_config is None:
        try:
            _cached_config = get_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}. Using default values.")
            # Create a dummy config object with defaults if loading fails
            class DummyConfig:
                class System:
                    task_queue_max_size = 10
                    default_conflict_handling = "auto"
                class Features:
                    max_parallel_workers = 5
                    enable_cost_tracking = True
                    enable_cost_logging = False
                    enable_target_resolution = True
                    enable_context_extraction = False
                    enable_conflict_detection = True
                class Resilience:
                    circuit_breaker_max_failures = 3
                    circuit_breaker_reset_time_sec = 60
                class Context:
                    default_max_tokens = 4000
                system = System()
                features = Features()
                resilience = Resilience()
                context = Context()
            _cached_config = DummyConfig()
    return _cached_config

# Load configuration
config = _get_cached_config()

# Resilience configuration from Config with sensible defaults
MAX_TASK_QUEUE_SIZE = getattr(config.system, 'task_queue_max_size', 10)
MAX_CONCURRENT_TASKS = getattr(config.features, 'max_parallel_workers', 5)
CIRCUIT_BREAKER_FAILURE_THRESHOLD = getattr(config.resilience, 'circuit_breaker_max_failures', 3)
CIRCUIT_BREAKER_RESET_TIMEOUT = getattr(config.resilience, 'circuit_breaker_reset_time_sec', 60)  # seconds

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


def resolve_target_elements(
    target_elements: Optional[List[str]], 
    file_paths: List[str], 
    working_dir: str
) -> List[str]:
    """
    Enhanced target resolution system that expands decorator targets to actual function names.
    
    For decorator targets (like "mcp.tool", "app.route", etc.), finds all functions with those decorators.
    Keeps regular function/class targets unchanged. Framework-agnostic.
    
    Args:
        target_elements: List of target elements (functions, classes, or decorators)
        file_paths: List of file paths to search in
        working_dir: Working directory for resolving relative paths
        
    Returns:
        Expanded list of actual function/class names found
    """
    import re
    
    if not target_elements:
        return []
    
    resolved_targets = []
    decorator_expansions = {}
    
    for target in target_elements:
        is_decorator_target = False
        expanded_functions = []
        
        # Check if this looks like a decorator target (contains dots or common decorator patterns)
        if ('.' in target or 
            target.lower() in ['tool', 'route', 'fixture', 'test', 'property', 'staticmethod', 'classmethod']):
            
            # Try to find functions decorated with this target across all files
            for file_path in file_paths:
                full_path = os.path.join(working_dir, file_path)
                if not os.path.exists(full_path):
                    continue
                    
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Framework-agnostic decorator patterns
                    decorator_patterns = [
                        # Basic patterns: @decorator, @decorator(), @decorator(args)
                        rf'@{re.escape(target)}\s*(?:\([^)]*\))?\s*\n\s*def\s+(\w+)\s*\(',
                        # Module patterns: @module.decorator, @module.decorator(), @module.decorator(args)
                        rf'@{re.escape(target)}\s*(?:\([^)]*\))?\s*\n\s*def\s+(\w+)\s*\(',
                        # Method chaining: @decorator.method, @decorator.method()
                        rf'@{re.escape(target)}\.\w+\s*(?:\([^)]*\))?\s*\n\s*def\s+(\w+)\s*\(',
                    ]
                    
                    for pattern in decorator_patterns:
                        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                        if matches:
                            expanded_functions.extend(matches)
                            is_decorator_target = True
                            
                except Exception as e:
                    logger.warning(f"Could not read file {full_path} for target resolution: {e}")
                    continue
        
        if is_decorator_target and expanded_functions:
            # Remove duplicates while preserving order
            unique_functions = []
            for func in expanded_functions:
                if func not in unique_functions:
                    unique_functions.append(func)
            
            resolved_targets.extend(unique_functions)
            decorator_expansions[target] = unique_functions
            logger.info(f"🎯 TARGET RESOLUTION: Expanded '{target}' to functions: {unique_functions}")
        else:
            # Keep regular function/class targets unchanged
            resolved_targets.append(target)
    
    # Log summary if any expansions occurred
    if decorator_expansions:
        total_expanded = sum(len(funcs) for funcs in decorator_expansions.values())
        logger.info(f"🔍 TARGET RESOLUTION SUMMARY: Expanded {len(decorator_expansions)} decorator targets to {total_expanded} function targets")
        for decorator, functions in decorator_expansions.items():
            logger.info(f"   {decorator} → {', '.join(functions)}")
    
    return resolved_targets


def find_targets_in_file(file_path: str, target_elements: List[str]) -> List[str]:
    """
    Find which target elements actually exist in a specific file.

    Args:
        file_path: Full path to the file to search
        target_elements: List of function/class/decorator names to find

    Returns:
        List of target elements that exist in the file
    """
    import re
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        found_targets = []
        for target in target_elements:
            # Special handling for "mcp.tool" target: find all MCP tool functions decorated with @mcp.tool
            if target == "mcp.tool":
                # Find all function names decorated with @mcp.tool
                tool_pattern = r'@mcp\.tool\(\)\s*\ndef\s+(\w+)\s*\('
                matches = re.findall(tool_pattern, content, re.MULTILINE)
                found_targets.extend(matches)
                continue

            # Build decorator-aware patterns
            # Support: @decorator, @decorator(), @decorator.method, @module.decorator, @module.decorator(), etc.
            # Accept compound names (e.g., "pytest.fixture", "app.route", "mcp.tool")
            decorator_patterns = [
                rf'@{re.escape(target)}\s*\n',                # @decorator or @module.decorator
                rf'@{re.escape(target)}\s*\(',                # @decorator( or @module.decorator(
                rf'@{re.escape(target)}\s*\)\s*\n',           # @decorator() or @module.decorator()
                rf'@{re.escape(target)}\s*\.\w+\s*\n',        # @decorator.method or @module.decorator.method
                rf'@{re.escape(target)}\s*\.\w+\s*\(',        # @decorator.method( or @module.decorator.method(
                rf'@{re.escape(target)}\s*\.\w+\s*\)\s*\n',   # @decorator.method() or @module.decorator.method()
            ]

            # Existing function/class/JS patterns (unchanged)
            patterns = [
                f'def {target}\\(',
                f'class {target}\\b',
                f'def {target}\\s*\\(',
                f'class {target}\\s*[\\(:]',
                f'function {target}\\(',  # JavaScript
                f'const {target}\\s*=',   # JavaScript const functions
                f'let {target}\\s*=',     # JavaScript let functions
                f'var {target}\\s*=',     # JavaScript var functions
                f'@{target}\\b',          # Decorator pattern (legacy, keep for compatibility)
            ] + decorator_patterns

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_targets.append(target)
                    break

        return found_targets

    except Exception as e:
        logger.warning(f"Could not search for targets in {file_path}: {e}")
        return []


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
    try:
        # Load config inside the function to ensure it's always fresh if needed,
        # though _get_cached_config handles caching.
        current_config = _get_cached_config()

        # Set default empty list for readonly files if not provided
        if readonly_files is None:
            readonly_files = []

        # Strategic model selection - get optimal model for the task
        if model is None:
            model = get_optimal_model(prompt)

        # Phase 2: Cost Pre-flight Check
        if getattr(current_config.features, 'enable_cost_tracking', True):
            try:
                # Read file contents for cost estimation
                files_content = []
                for file_path in editable_files + (readonly_files or []):
                    full_path = os.path.join(working_dir, file_path)
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                files_content.append(f.read())
                        except Exception:
                            # Skip files that can't be read
                            pass
                
                # Estimate cost before execution
                cost_estimate = estimate_cost(prompt, files_content, model, "code_generation")
                
                # Check budget limits
                budget_ok, budget_message = check_budget(cost_estimate.total_cost)
                
                if not budget_ok:
                    # Budget exceeded - return error
                    error_response = {
                        "success": False,
                        "error": f"Task aborted: {budget_message}",
                        "cost_estimate": {
                            "total_cost": cost_estimate.total_cost,
                            "input_tokens": cost_estimate.input_tokens,
                            "estimated_output_tokens": cost_estimate.estimated_output_tokens,
                            "model": model
                        },
                        "details": "Task was aborted to prevent budget overrun."
                    }
                    return json.dumps(error_response)
                
                # Log cost estimate only if logging enabled
                if getattr(current_config.features, 'enable_cost_logging', False):
                    if budget_message:  # Warning message
                        logger.warning(f"Cost warning: {budget_message}")
                    
                    logger.info(f"Task cost estimate: ${cost_estimate.total_cost:.4f} "
                               f"({cost_estimate.input_tokens}+{cost_estimate.estimated_output_tokens} tokens, {model})")
                
            except Exception as e:
                if getattr(current_config.features, 'enable_cost_logging', False):
                    logger.warning(f"Cost estimation failed: {e}")
                # Continue without cost tracking if estimation fails

        # Execute the task
        start_time = time.time()
        
        # Phase 2.5: Smart Auto-Detection (if target_elements not provided)
        auto_detected = False
        if not target_elements:
            auto_detected_targets = get_auto_detected_targets(
                prompt=prompt,
                file_paths=editable_files,
                working_dir=working_dir
            )
            if auto_detected_targets:
                target_elements = auto_detected_targets
                auto_detected = True
                logger.info(f"🎯 AUTO-DETECTION SUCCESS: Found targets {target_elements} from prompt")
            else:
                logger.info("🔍 AUTO-DETECTION: No targets detected, using full file processing")
        
        # Phase 2.6: Target Resolution (expand decorator targets to actual function names)
        original_targets = target_elements.copy() if target_elements else None
        if target_elements and getattr(current_config.features, 'enable_target_resolution', True):
            try:
                resolved_targets = resolve_target_elements(
                    target_elements=target_elements,
                    file_paths=editable_files,
                    working_dir=working_dir
                )
                if resolved_targets != target_elements:
                    target_elements = resolved_targets
                    logger.info(f"🎯 TARGET RESOLUTION: Expanded from {len(original_targets)} to {len(target_elements)} targets")
                else:
                    logger.info("🔍 TARGET RESOLUTION: No expansion needed, targets unchanged")
            except Exception as e:
                logger.warning(f"⚠️ TARGET RESOLUTION failed: {e}, using original targets")
        
        # Phase 2: Context-Aware File Pruning (if enabled and target_elements available)
        enhanced_prompt = prompt
        context_processed_files = []
        context_extraction_used = False
        
        if (target_elements and 
            getattr(current_config.features, 'enable_context_extraction', False)):
            try:
                context_extraction_used = True
                logger.info("Context extraction enabled, processing files...")
                
                # Get configuration
                max_tokens = getattr(current_config.context, 'default_max_tokens', 4000)
                
                # NEW: Smart target-to-file mapping instead of round-robin
                context_sections = []
                files_with_targets = []
                
                for file_path in editable_files:
                    full_path = os.path.join(working_dir, file_path)
                    
                    if os.path.exists(full_path):
                        # Find which target elements exist in this file
                        targets_for_file = find_targets_in_file(full_path, target_elements)
                        
                        if targets_for_file:
                            try:
                                # Extract context for the first matching target
                                primary_target = targets_for_file[0]
                                context_result = extract_context(
                                    file_path=full_path,
                                    target_element=primary_target,
                                    max_tokens=max_tokens // len(editable_files) if len(editable_files) > 0 else max_tokens
                                )
                                
                                if context_result:
                                    context_info = f"\n--- {file_path} (Focused Context for '{primary_target}') ---\n"
                                    context_info += context_result + "\n\n"
                                    context_sections.append(context_info)
                                    context_processed_files.append(file_path)
                                    files_with_targets.append(file_path)
                                    logger.info(f"✅ Context extracted for {file_path} targeting '{primary_target}'")
                                else:
                                    logger.warning(f"⚠️ No relevant context found for {file_path} targeting '{primary_target}'")
                            except Exception as e:
                                logger.error(f"❌ Context extraction failed for {file_path} targeting '{primary_target}': {e}")
                                continue
                        else:
                            logger.info(f"ℹ️ No target elements found in {file_path}, skipping context extraction")
                
                # Enhance prompt with context if any was extracted
                if context_sections:
                    enhanced_prompt = f"{prompt}\n\nFocused file context:\n{''.join(context_sections)}"
                    logger.info(f"💰 CONTEXT EXTRACTION SUCCESS: Enhanced prompt with context from {len(context_processed_files)} files")
                    
                    # FIXED: Don't remove files, let adapter handle full files alongside context
                    # This allows for proper diff tracking
                else:
                    logger.warning("⚠️ Context extraction enabled but no context was successfully extracted")
                    context_extraction_used = False
                
            except Exception as e:
                logger.error(f"❌ Context extraction system failed: {e}")
                context_extraction_used = False
                enhanced_prompt = prompt

        # Track auto-detection metadata for logging
        auto_detection_metadata = {
            "auto_detected_targets": target_elements if auto_detected else None,
            "detection_method": "prompt_analysis" if auto_detected else ("manual" if target_elements else "none"),
            "context_extraction_used": context_extraction_used,
            "files_processed_with_context": context_processed_files,
            "target_elements_provided": bool(target_elements),
            "original_auto_detected": bool(auto_detected)
        }
        
        # Call the Aider integration function
        result = code_with_aider(
            ai_coding_prompt=enhanced_prompt,
            relative_editable_files=editable_files,
            relative_readonly_files=readonly_files,
            model=model,
            working_dir=working_dir,
            target_elements=target_elements,
            auto_detection_metadata=auto_detection_metadata  # NEW: Pass metadata
        )
        
        # Phase 2: Record actual cost (if cost tracking enabled)
        if getattr(current_config.features, 'enable_cost_tracking', True):
            try:
                duration = time.time() - start_time
                
                # Parse result to extract token usage (if available)
                # Note: This is a simplified version - actual token counting would need
                # integration with the AI provider's response
                task_id = str(uuid.uuid4())[:8]
                
                # Estimate actual tokens used (this could be improved with real API response data)
                estimated_input = cost_estimate.input_tokens if 'cost_estimate' in locals() else 1000
                estimated_output = max(500, len(str(result)) // 4)  # Rough estimate from result length
                
                # Generate descriptive task name from prompt
                task_name = generate_task_name(prompt)
                
                # Record the cost
                cost_result = record_cost(task_id, estimated_input, estimated_output, model, duration, task_name)
                
                # Add cost info to result if it's JSON
                try:
                    result_data = json.loads(result) if isinstance(result, str) else result
                    if isinstance(result_data, dict):
                        result_data["cost_info"] = {
                            "total_cost": cost_result.total_cost,
                            "input_tokens": cost_result.input_tokens,
                            "output_tokens": cost_result.output_tokens,
                            "model": model,
                            "duration_seconds": duration
                        }
                        result = json.dumps(result_data)
                except Exception:
                    # If result parsing fails, just continue with original result
                    pass
                    
            except Exception as e:
                if getattr(current_config.features, 'enable_cost_logging', False):
                    logger.warning(f"Cost recording failed: {e}")
        
        # Add auto-detection metadata to result
        try:
            result_data = json.loads(result) if isinstance(result, str) else result
            if isinstance(result_data, dict):
                # Auto-detection info is now provided by code_with_aider, no need to reconstruct it
                # If somehow it's missing, add a basic version
                if "auto_detection_info" not in result_data:
                    result_data["auto_detection_info"] = {
                        "auto_detected_targets": None,
                        "context_extraction_used": False,
                        "files_processed_with_context": [],
                        "estimated_token_reduction": "0%",
                        "target_elements_provided": bool(target_elements),
                        "target_elements_used": target_elements
                    }
                result = json.dumps(result_data)
        except Exception:
            # If result parsing fails, just continue with original result
            pass
        
        return result
    except Exception as e:
        # Log the error
        logger.error(f"Error in code_with_ai: {str(e)}")

        # Return a JSON error response instead of crashing
        error_response = {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}",
            "error_type": type(e).__name__,
            "details": "The server encountered an error but remained running.",
        }
        return json.dumps(error_response)


def code_with_multiple_ai(
    prompts: List[str],
    working_dir: str,
    editable_files_list: List[List[str]],
    readonly_files_list: Optional[List[List[str]]] = None,
    models: Optional[List[str]] = None,
    max_workers: Optional[int] = None,
    parallel: bool = True,
    target_elements_list: Optional[List[List[str]]] = None,  # NEW: Context extraction targets
    conflict_handling: str = None, # Default to None, will be set by config
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

    # Load config inside the function to ensure it's always fresh if needed,
    # though _get_cached_config handles caching.
    current_config = _get_cached_config()

    # Resolve conflict_handling from config if not explicitly provided
    if conflict_handling is None:
        conflict_handling = getattr(current_config.system, 'default_conflict_handling', "auto")

    def enqueue_task(task):
        try:
            task_queue.put(task, block=False)
            logger.info(f"Task enqueued. Queue size: {task_queue.qsize()}")
            return True
        except Full:
            logger.warning("Task queue is full. Rejecting new task.")
            return False

    def dequeue_task():
        try:
            return task_queue.get(block=True, timeout=5)
        except Empty:
            return None

    # Validate and normalize conflict_handling
    valid_conflict_values = {"auto", "warn", "ignore"}
    if conflict_handling not in valid_conflict_values:
        logger.warning(f"Invalid conflict_handling value '{conflict_handling}' detected. Falling back to 'auto'.")
        conflict_handling = "auto"
    else:
        logger.info(f"Using conflict_handling mode: '{conflict_handling}' from config or parameter.")

    # Respect ENABLE_CONFLICT_DETECTION config value
    enable_conflict_detection = getattr(current_config.features, 'enable_conflict_detection', True)
    if not enable_conflict_detection:
        logger.info("Conflict detection disabled by configuration. Forcing conflict_handling to 'ignore'.")
        conflict_handling = "ignore"

    try:
        # Validate inputs
        num_prompts = len(prompts)
        if len(editable_files_list) != num_prompts:
            error_msg = f"Error: Length of editable_files_list ({len(editable_files_list)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        # Set default empty lists for readonly_files_list if not provided
        if readonly_files_list is None:
            readonly_files_list = [[] for _ in range(num_prompts)]
        elif len(readonly_files_list) != num_prompts:
            error_msg = f"Error: Length of readonly_files_list ({len(readonly_files_list)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        # Set default empty lists for target_elements_list if not provided
        if target_elements_list is None:
            target_elements_list = [None for _ in range(num_prompts)]
        elif len(target_elements_list) != num_prompts:
            error_msg = f"Error: Length of target_elements_list ({len(target_elements_list)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        # Strategic model selection for multiple tasks
        if models is None:
            # Use strategic selection for each prompt
            models = [get_optimal_model(prompt) for prompt in prompts]
        else:
            # Fill in None values with strategic selection
            models = [
                get_optimal_model(prompts[i]) if models[i] is None else models[i]
                for i in range(num_prompts)
            ]

        # Ensure models list matches prompts length
        if len(models) != num_prompts:
            error_msg = f"Error: Length of models ({len(models)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        # Set default max_workers if not provided
        if max_workers is None:
            max_workers = min(num_prompts, MAX_CONCURRENT_TASKS)

        # Conflict Detection and Handling
        conflict_info = {"has_conflicts": False, "report": "", "auto_serialized": False}
        
        if conflict_handling != "ignore":
            try:
                logger.info("Running file conflict detection...")
                detector = FileConflictDetector(working_dir=working_dir)
                
                # Prepare tasks data for conflict detection
                tasks_data = []
                for i in range(num_prompts):
                    tasks_data.append({
                        "task_id": f"Task-{i+1}",
                        "editable_files": editable_files_list[i]
                    })
                
                # Detect conflicts
                conflicts = detector.detect_conflicts(tasks_data)
                conflict_info["has_conflicts"] = conflicts["has_conflicts"]
                
                if conflicts["has_conflicts"]:
                    # Generate human-readable report
                    conflict_report = detector.generate_conflict_report(conflicts)
                    conflict_info["report"] = conflict_report
                    
                    logger.warning("File conflicts detected between tasks!")
                    logger.warning(conflict_report)
                    
                    if conflict_handling == "auto":
                        # Automatically switch to sequential execution
                        logger.info("Automatically switching to sequential execution due to conflicts.")
                        parallel = False
                        conflict_info["auto_serialized"] = True
                    elif conflict_handling == "warn":
                        # Just warn but continue with parallel execution
                        logger.warning("Continuing with parallel execution despite conflicts. Monitor for merge issues.")
                else:
                    logger.info("No file conflicts detected. Parallel execution is safe.")
                    
            except Exception as e:
                logger.error(f"Error during conflict detection: {str(e)}. Continuing with original execution plan.")
                conflict_info["report"] = f"Conflict detection failed: {str(e)}"

        # Define a function to process a single prompt with circuit breaker protection
        def process_prompt(i):
            prompt = prompts[i]
            editable_files = editable_files_list[i]
            readonly_files = readonly_files_list[i]
            model = models[i]
            target_elements = target_elements_list[i]

            # Enqueue task or reject if queue is full
            if not enqueue_task(i):
                return {
                    "success": False,
                    "error": "Task queue is full. Please try again later.",
                    "task_index": i,
                    "prompt": prompt,
                    "model": model,
                    "editable_files": editable_files,
                    "status_message": "Rejected due to full task queue.",
                }

            try:
                # Log the start of this task with timestamp
                start_time = time.time()
                logger.info(f"Starting task {i + 1}/{num_prompts}: {prompt[:50]}...")

                # Use circuit breaker to call the AI coding function
                result_json = circuit_breaker.call(
                    code_with_aider,
                    ai_coding_prompt=prompt,
                    relative_editable_files=editable_files,
                    relative_readonly_files=readonly_files,
                    model=model,
                    working_dir=working_dir,
                    target_elements=target_elements,
                )

                # Log the completion of this task with timestamp and duration
                end_time = time.time()
                duration = end_time - start_time
                logger.info(
                    f"Completed task {i + 1}/{num_prompts} in {duration:.2f} seconds"
                )
            except Exception as e:
                logger.error(f"Error in task {i + 1}/{num_prompts}: {str(e)}")
                # Create an error JSON response
                end_time = time.time()
                duration = end_time - start_time
                return {
                    "success": False,
                    "error": f"Error executing task: {str(e)}",
                    "error_type": type(e).__name__,
                    "execution_time": duration,
                    "task_index": i,
                    "prompt": prompt,
                    "model": model,
                    "editable_files": editable_files,
                    "status_message": f"Failed to execute task {i + 1} due to an error: {str(e)}",
                }
            finally:
                # Remove task from queue after processing
                try:
                    task_queue.get_nowait()
                    task_queue.task_done()
                    logger.info(f"Task dequeued. Queue size: {task_queue.qsize()}")
                except Empty:
                    logger.warning("Task queue was empty when trying to dequeue.")

            # Parse the result
            try:
                result = json.loads(result_json)
                # Add execution time to the result
                result["execution_time"] = duration
                # Add task information
                result["task_index"] = i
                result["prompt"] = prompt
                result["model"] = model
                result["editable_files"] = editable_files

                # Add a human-readable status message
                if result.get("success", False):
                    status_message = f"Successfully implemented changes to {', '.join(editable_files)}"
                    if "details" in result:
                        status_message += f": {result['details']}"
                    result["status_message"] = status_message
                else:
                    status_message = (
                        f"Failed to implement changes to {', '.join(editable_files)}"
                    )
                    if "details" in result:
                        status_message += f": {result['details']}"
                    elif "error" in result:
                        status_message += f": {result['error']}"
                    result["status_message"] = status_message

                return result
            except json.JSONDecodeError:
                # Handle case where result is not valid JSON
                return {
                    "success": False,
                    "error": "Failed to parse result as JSON",
                    "raw": result_json,
                    "execution_time": duration,
                    "task_index": i,
                    "prompt": prompt,
                    "model": model,
                    "editable_files": editable_files,
                    "status_message": f"Failed to parse JSON response for task {i + 1}",
                }

        # Process prompts either in parallel or sequentially based on the 'parallel' parameter
        results = []
        overall_success = True

        if parallel:
            # Parallel execution using ThreadPoolExecutor
            logger.info(
                f"Starting parallel execution of {num_prompts} tasks with {max_workers} workers"
            )
            parallel_start_time = time.time()

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                logger.info(f"Submitting all {num_prompts} tasks to the thread pool")
                future_to_index = {
                    executor.submit(process_prompt, i): i for i in range(num_prompts)
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        results.append(
                            (index, result)
                        )  # Store with index for sorting later

                        # Update overall success status
                        if not result.get("success", False):
                            overall_success = False
                    except Exception as exc:
                        # Handle any exceptions that occurred during execution
                        error_result = {
                            "success": False,
                            "error": f"Exception occurred while processing prompt {index}: {str(exc)}",
                        }
                        results.append((index, error_result))
                        overall_success = False

            # Sort results by original index
            results.sort()  # Sort by index
            results = [result for _, result in results]  # Remove indices
        else:
            # Sequential execution
            logger.info(f"Starting sequential execution of {num_prompts} tasks")
            parallel_start_time = (
                time.time()
            )  # We'll still call it parallel_start_time for consistency

            for i in range(num_prompts):
                try:
                    logger.info(f"Processing task {i + 1}/{num_prompts} sequentially")
                    result = process_prompt(i)
                    results.append(result)

                    # Update overall success status
                    if not result.get("success", False):
                        overall_success = False
                except Exception as exc:
                    # Handle any exceptions that occurred during execution
                    error_result = {
                        "success": False,
                        "error": f"Exception occurred while processing prompt {i}: {str(exc)}",
                    }
                    results.append(error_result)
                    overall_success = False

        # Calculate total execution time
        parallel_end_time = time.time()
        execution_duration = parallel_end_time - parallel_start_time

        # Print summary of execution
        successful_tasks = sum(1 for r in results if r.get("success", False))
        execution_type = "parallel" if parallel else "sequential"
        logger.info(
            f"Completed all {num_prompts} tasks in {execution_duration:.2f} seconds ({execution_type} execution)"
        )
        logger.info(f"{successful_tasks}/{num_prompts} tasks completed successfully")

        # Print detailed status for each prompt
        logger.info("Detailed status for each prompt:")
        for i, result in enumerate(results):
            status = "SUCCESS" if result.get("success", False) else "FAILED"
            status_message = result.get("status_message", "")
            logger.info(f"Prompt {i + 1}: {status} - {prompts[i][:50]}...")
            if status_message:
                logger.info(f"   → {status_message}")
            if "implementation_notes" in result and result["implementation_notes"]:
                # Truncate implementation notes if too long
                notes = result["implementation_notes"]
                if len(notes) > 200:
                    notes = notes[:197] + "..."
                logger.info(f"   → Implementation notes: {notes}")

        # Calculate the theoretical sequential execution time (sum of individual task times)
        theoretical_sequential_time = sum(
            result.get("execution_time", 0) for result in results
        )

        # If running in parallel, show the speedup compared to theoretical sequential time
        if parallel and theoretical_sequential_time > 0:  # Avoid division by zero
            speedup = theoretical_sequential_time / execution_duration
            logger.info(
                f"Parallel speedup: {speedup:.2f}x (theoretical sequential would take ~{theoretical_sequential_time:.2f}s)"
            )

        # Create a list of success statuses for each prompt
        success_statuses = [result.get("success", False) for result in results]

        # Create a list of status messages for each prompt
        status_messages = [result.get("status_message", "") for result in results]

        # Create a summary of files modified
        all_modified_files = []
        for result in results:
            if result.get("success", False) and "files_modified" in result:
                all_modified_files.extend(result["files_modified"])

        # Remove duplicates while preserving order
        unique_modified_files = []
        for file in all_modified_files:
            if file not in unique_modified_files:
                unique_modified_files.append(file)

        # Aggregate results
        try:
            # Collect auto-detection information from all results
            auto_detection_summary = {
                "total_tasks": num_prompts,
                "tasks_with_auto_detection": 0,
                "tasks_with_context_extraction": 0,
                "total_files_processed_with_context": 0,
                "auto_detected_targets_by_task": [],
                "context_extraction_used_by_task": [],
                "estimated_token_reductions": []
            }
            
            for result in results:
                auto_info = result.get("auto_detection_info", {})
                if auto_info.get("auto_detected_targets"):
                    auto_detection_summary["tasks_with_auto_detection"] += 1
                if auto_info.get("context_extraction_used"):
                    auto_detection_summary["tasks_with_context_extraction"] += 1
                
                auto_detection_summary["auto_detected_targets_by_task"].append(auto_info.get("auto_detected_targets"))
                auto_detection_summary["context_extraction_used_by_task"].append(auto_info.get("context_extraction_used", False))
                auto_detection_summary["estimated_token_reductions"].append(auto_info.get("estimated_token_reduction", "0%"))
                
                files_with_context = auto_info.get("files_processed_with_context", [])
                auto_detection_summary["total_files_processed_with_context"] += len(files_with_context)
            
            aggregated_result = {
                "success": overall_success,  # True only if all prompts succeeded
                "results": results,
                "success_statuses": success_statuses,  # List of success/failure for each prompt
                "status_messages": status_messages,  # List of status messages for each prompt
                "summary": f"Processed {num_prompts} prompts with {successful_tasks} successes",
                "execution_time": execution_duration,
                "execution_type": "parallel" if parallel else "sequential",
                "theoretical_sequential_time": theoretical_sequential_time,
                "modified_files": unique_modified_files,
                "speedup": (
                    theoretical_sequential_time / execution_duration
                    if parallel and execution_duration > 0
                    else 1.0
                ),
                "auto_detection_summary": auto_detection_summary,
                "conflict_info": conflict_info  # NEW: Include conflict detection results
            }

            return json.dumps(aggregated_result, indent=4)
        except Exception as e:
            # Final catch-all for any unexpected errors in the entire function
            logger.error(f"Critical error in code_with_multiple_ai: {str(e)}")
            traceback.print_exc()
            error_response = {
                "success": False,
                "error": f"Error aggregating results: {str(e)}",
                "error_type": type(e).__name__,
                "results": (
                    results if "results" in locals() else []
                ),  # Include the raw results if available
                "summary": f"Processed prompts but encountered an error during result aggregation",
            }
            return json.dumps(error_response, indent=4)
    except Exception as e:
        # Final catch-all for any unexpected errors in the entire function
        logger.error(f"Critical error in code_with_multiple_ai: {str(e)}")
        traceback.print_exc()
        error_response = {
            "success": False,
            "error": f"Critical error in code_with_multiple_ai: {str(e)}",
            "error_type": type(e).__name__,
            "details": "The server encountered a critical error but remained running.",
        }
        return json.dumps(error_response, indent=4)

