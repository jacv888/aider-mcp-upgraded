import os
import json
import time
import threading
import queue
import logging
import psutil
from functools import wraps
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from aider_ai_code import code_with_aider
from dotenv import load_dotenv

# Load environment variables from multiple locations
load_dotenv()  # Load from current directory (lowest priority)
load_dotenv(os.path.expanduser("~/.config/aider/.env"))  # Load global config (medium priority)
load_dotenv("/Users/jacquesv/MCP/aider-mcp/.env", override=True)  # PRIMARY source (highest priority)

# Import strategic model selector
from strategic_model_selector import get_optimal_model

# Configure logging
LOG_LEVEL = os.getenv("AIDER_MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(asctime)s] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("aider_mcp_enhanced")

# Resilience configuration from environment variables
CONNECTION_HEALTH_CHECK_INTERVAL = float(os.getenv("CONNECTION_HEALTH_CHECK_INTERVAL", "10.0"))
TASK_QUEUE_MAX_SIZE = int(os.getenv("TASK_QUEUE_MAX_SIZE", "50"))
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
CIRCUIT_BREAKER_RESET_TIMEOUT = float(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60.0"))
RESOURCE_MONITOR_INTERVAL = float(os.getenv("RESOURCE_MONITOR_INTERVAL", "5.0"))
CPU_USAGE_THRESHOLD = float(os.getenv("CPU_USAGE_THRESHOLD", "85.0"))
MEMORY_USAGE_THRESHOLD = float(os.getenv("MEMORY_USAGE_THRESHOLD", "85.0"))
THROTTLE_DELAY_SECONDS = float(os.getenv("THROTTLE_DELAY_SECONDS", "2.0"))
MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "4"))
GRACEFUL_DEGRADATION_ENABLED = os.getenv("GRACEFUL_DEGRADATION_ENABLED", "true").lower() == "true"

FALL_BACK_MODEL = "gpt-4.1-mini"

# Circuit breaker states
class CircuitBreakerState:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int, reset_timeout: float):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
        self.lock = threading.Lock()

    def call(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                if self.state == CircuitBreakerState.OPEN:
                    elapsed = time.time() - (self.last_failure_time or 0)
                    if elapsed >= self.reset_timeout:
                        logger.info("Circuit breaker transitioning to HALF_OPEN state")
                        self.state = CircuitBreakerState.HALF_OPEN
                    else:
                        logger.warning("Circuit breaker OPEN - rejecting call")
                        raise RuntimeError("Circuit breaker is OPEN, rejecting call")

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                with self.lock:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        self.state = CircuitBreakerState.OPEN
                        logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
                raise
            else:
                with self.lock:
                    if self.state == CircuitBreakerState.HALF_OPEN:
                        logger.info("Circuit breaker CLOSED after successful call in HALF_OPEN state")
                        self.state = CircuitBreakerState.CLOSED
                        self.failure_count = 0
                return result
        return wrapper

# Initialize circuit breaker for aider calls
aider_circuit_breaker = CircuitBreaker(CIRCUIT_BREAKER_FAILURE_THRESHOLD, CIRCUIT_BREAKER_RESET_TIMEOUT)

# Task queue for code_with_multiple_ai
task_queue = queue.Queue(maxsize=TASK_QUEUE_MAX_SIZE)

# Connection health state
connection_healthy = True
connection_health_lock = threading.Lock()

def monitor_connection_health():
    global connection_healthy
    while True:
        try:
            # Here we could implement real health checks, e.g. pinging external services
            # For now, we just set healthy to True to simulate
            with connection_health_lock:
                connection_healthy = True
            logger.debug("Connection health check passed")
        except Exception as e:
            with connection_health_lock:
                connection_healthy = False
            logger.error(f"Connection health check failed: {e}")
        time.sleep(CONNECTION_HEALTH_CHECK_INTERVAL)

def monitor_resources():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        logger.debug(f"Resource monitor: CPU {cpu}%, Memory {mem}%")
        if cpu > CPU_USAGE_THRESHOLD or mem > MEMORY_USAGE_THRESHOLD:
            logger.warning(f"High resource usage detected: CPU {cpu}%, Memory {mem}% - throttling tasks")
            time.sleep(THROTTLE_DELAY_SECONDS)
        else:
            time.sleep(RESOURCE_MONITOR_INTERVAL)

# Start background monitoring threads
threading.Thread(target=monitor_connection_health, daemon=True).start()
threading.Thread(target=monitor_resources, daemon=True).start()

# Create an MCP server
mcp = FastMCP("Aidar Coder")

def check_connection_health():
    with connection_health_lock:
        return connection_healthy

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

@mcp.tool()
def code_with_ai(
        prompt: str,
        working_dir: str,
        editable_files: List[str],
        readonly_files: Optional[List[str]] = None,
        model: Optional[str] = None,  # Strategic model selection if None
) -> str:
    """
    Use Aider to perform AI coding tasks with strategic model selection.
    
    The system will automatically select the optimal model based on your prompt:
    - Complex algorithms: Claude 3.5 Sonnet
    - Simple tasks: GPT-4o Mini  
    - Documentation: Gemini 2.5 Pro
    - Testing: GPT-4o Mini
    - CSS/Styling: GPT-4o
    - React/Frontend: Claude 3.5 Sonnet
    - API/Backend: Claude 3.5 Haiku
    
    You can override model selection by specifying the 'model' parameter.

    Args:
        prompt: The natural language prompt describing what code changes to make
        working_dir: working directory where the files are located
        editable_files: List of files that can be edited by the AI
        readonly_files: Optional list of files that can be read but not edited (for context)
        model: Optional AI model to use (default: defined in environment variable or fallback model) **Don't change model unless users asked for it**

    Returns:
        JSON string with results including success status and diff output
    """
    import json

    try:
        # Set default empty list for readonly files if not provided
        if readonly_files is None:
            readonly_files = []

        # Strategic model selection - get optimal model for the task
        if model is None:
            model = get_optimal_model(prompt)
        
        # Call the Aider integration function
        return code_with_aider(
            ai_coding_prompt=prompt,
            relative_editable_files=editable_files,
            relative_readonly_files=readonly_files,
            model=model,
            working_dir=working_dir
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error in code_with_ai: {str(e)}")

        # Return a JSON error response instead of crashing
        error_response = {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}",
            "error_type": type(e).__name__,
            "details": "The server encountered an error but remained running."
        }
        return json.dumps(error_response)

@mcp.tool()
def code_with_multiple_ai(
        prompts: List[str],
        working_dir: str,
        editable_files_list: List[List[str]],
        readonly_files_list: Optional[List[List[str]]] = None,
        models: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
        parallel: bool = True,
) -> str:
    """
    Use Multiple Aider agents with strategic model selection to perform AI coding tasks.
    
    🧠 STRATEGIC MODEL SELECTION:
    Each task automatically gets the optimal model based on its prompt:
    - Complex algorithms: Claude 3.5 Sonnet (best reasoning)
    - Simple tasks: GPT-4o Mini (fast & cheap)  
    - Documentation: Gemini 2.5 Pro (excellent writing)
    - Testing: GPT-4o Mini (efficient for test generation)
    - CSS/Styling: GPT-4o (great design capabilities)
    - React/Frontend: Claude 3.5 Sonnet (best for complex logic)
    - API/Backend: Claude 3.5 Haiku (fast for server code)
    - Debugging: Claude 3.5 Sonnet (best problem-solving)
    
    💫 EXAMPLE USAGE WITH STRATEGIC SELECTION:
    code_with_multiple_ai(
        prompts=[
            "Create complex React component with state management",  # → Claude 3.5 Sonnet
            "Write unit tests for the API",                         # → GPT-4o Mini  
            "Generate comprehensive documentation",                  # → Gemini 2.5 Pro
            "Add CSS animations and styling"                        # → GPT-4o
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

    Returns:
        JSON string with aggregated results including success status and diff outputs
    """
    import json
    import time
    import concurrent.futures
    import traceback
    from concurrent.futures import ThreadPoolExecutor

    # Internal function to execute a single task with circuit breaker protection
    @aider_circuit_breaker.call
    def execute_task(i):
        prompt = prompts[i]
        editable_files = editable_files_list[i]
        readonly_files = readonly_files_list[i]
        model = models[i]

        try:
            start_time = time.time()
            logger.info(f"Starting task {i + 1}/{len(prompts)}: {prompt[:50]}...")
            result_json = code_with_aider(
                ai_coding_prompt=prompt,
                relative_editable_files=editable_files,
                relative_readonly_files=readonly_files,
                model=model,
                working_dir=working_dir
            )
            duration = time.time() - start_time
            logger.info(f"Completed task {i + 1}/{len(prompts)} in {duration:.2f} seconds")
            return result_json, duration
        except Exception as e:
            logger.error(f"Error in task {i + 1}: {e}")
            raise

    try:
        # Validate inputs
        num_prompts = len(prompts)
        if len(editable_files_list) != num_prompts:
            error_msg = f"Error: Length of editable_files_list ({len(editable_files_list)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        if readonly_files_list is None:
            readonly_files_list = [[] for _ in range(num_prompts)]
        elif len(readonly_files_list) != num_prompts:
            error_msg = f"Error: Length of readonly_files_list ({len(readonly_files_list)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        if models is None:
            models = [get_optimal_model(prompt) for prompt in prompts]
        else:
            models = [get_optimal_model(prompts[i]) if models[i] is None else models[i] for i in range(num_prompts)]

        if len(models) != num_prompts:
            error_msg = f"Error: Length of models ({len(models)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        if max_workers is None:
            max_workers = min(num_prompts, MAX_PARALLEL_WORKERS)

        # Check connection health before starting
        if not check_connection_health():
            msg = "Connection unhealthy, rejecting new tasks"
            logger.warning(msg)
            return json.dumps({"success": False, "error": msg})

        # Enqueue tasks and manage queue size for resilience
        if task_queue.qsize() + num_prompts > TASK_QUEUE_MAX_SIZE:
            msg = "Task queue full, rejecting new tasks to prevent overload"
            logger.warning(msg)
            return json.dumps({"success": False, "error": msg})

        for i in range(num_prompts):
            task_queue.put(i)

        results = []
        overall_success = True

        def worker():
            while not task_queue.empty():
                try:
                    idx = task_queue.get_nowait()
                except queue.Empty:
                    break
                try:
                    result_json, duration = execute_task(idx)
                    result = json.loads(result_json)
                    result['execution_time'] = duration
                    result['task_index'] = idx
                    result['prompt'] = prompts[idx]
                    result['model'] = models[idx]
                    result['editable_files'] = editable_files_list[idx]

                    if result.get('success', False):
                        status_message = f"Successfully implemented changes to {', '.join(editable_files_list[idx])}"
                        if 'details' in result:
                            status_message += f": {result['details']}"
                        result['status_message'] = status_message
                    else:
                        status_message = f"Failed to implement changes to {', '.join(editable_files_list[idx])}"
                        if 'details' in result:
                            status_message += f": {result['details']}"
                        elif 'error' in result:
                            status_message += f": {result['error']}"
                        result['status_message'] = status_message

                    results.append((idx, result))
                    if not result.get("success", False):
                        nonlocal overall_success
                        overall_success = False
                except Exception as e:
                    logger.error(f"Exception in worker for task {idx}: {e}")
                    error_result = {
                        "success": False,
                        "error": f"Exception occurred while processing prompt {idx}: {str(e)}"
                    }
                    results.append((idx, error_result))
                    overall_success = False
                finally:
                    task_queue.task_done()

        # Run workers in parallel or sequentially
        if parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(worker) for _ in range(max_workers)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Worker thread raised exception: {e}")
        else:
            worker()

        # Sort results by original index
        results.sort()
        results = [result for _, result in results]

        # Aggregate results
        successful_tasks = sum(1 for r in results if r.get('success', False))
        theoretical_sequential_time = sum(r.get('execution_time', 0) for r in results)
        execution_duration = theoretical_sequential_time  # Approximate since tasks run in parallel

        aggregated_result = {
            "success": overall_success,
            "results": results,
            "summary": f"Processed {num_prompts} prompts with {successful_tasks} successes",
            "execution_time": execution_duration,
            "execution_type": "parallel" if parallel else "sequential",
            "theoretical_sequential_time": theoretical_sequential_time,
            "modified_files": list({file for r in results if r.get('success', False) for file in r.get('files_modified', [])}),
            "speedup": 1.0  # Could be improved with real timing
        }

        return json.dumps(aggregated_result, indent=4)

    except Exception as e:
        logger.error(f"Critical error in code_with_multiple_ai: {str(e)}", exc_info=True)
        error_response = {
            "success": False,
            "error": f"Critical error in code_with_multiple_ai: {str(e)}",
            "error_type": type(e).__name__,
            "details": "The server encountered a critical error but remained running."
        }
        return json.dumps(error_response, indent=4)

# Run the server if this file is executed directly
if __name__ == "__main__":
    logger.info("Starting MCP server with enhanced resilience features")
    mcp.run()
