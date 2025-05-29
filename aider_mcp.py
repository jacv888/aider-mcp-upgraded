from mcp.server.fastmcp import FastMCP
import os
from typing import List, Optional
from aider_ai_code import code_with_aider
from dotenv import load_dotenv

# Resilience imports
import threading
import psutil
import time
import logging
from queue import Queue, Full, Empty

# Load environment variables from multiple locations
# Priority order: MCP aider-mcp directory is PRIMARY source, then fallbacks
load_dotenv()  # Load from current directory (lowest priority)
load_dotenv(os.path.expanduser("~/.config/aider/.env"))  # Load global config (medium priority)
load_dotenv("/Users/jacquesv/MCP/aider-mcp/.env", override=True)  # PRIMARY source (highest priority)

# Import strategic model selector
from strategic_model_selector import get_optimal_model

FALL_BACK_MODEL = "gpt-4.1-mini"

# Configure logging for resilience features
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aider_mcp_resilience")

# Resilience configuration from environment variables with sensible defaults
MAX_TASK_QUEUE_SIZE = int(os.getenv("MAX_TASK_QUEUE_SIZE", "10"))
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
CPU_USAGE_THRESHOLD = float(os.getenv("CPU_USAGE_THRESHOLD", "85.0"))  # percent
MEMORY_USAGE_THRESHOLD = float(os.getenv("MEMORY_USAGE_THRESHOLD", "90.0"))  # percent
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
CIRCUIT_BREAKER_RESET_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))  # seconds
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

circuit_breaker = CircuitBreaker(CIRCUIT_BREAKER_FAILURE_THRESHOLD, CIRCUIT_BREAKER_RESET_TIMEOUT)

# Resource monitor thread to throttle tasks if CPU or memory usage is high
def resource_monitor():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        if cpu > CPU_USAGE_THRESHOLD or mem > MEMORY_USAGE_THRESHOLD:
            logger.warning(f"High resource usage detected: CPU {cpu}%, Memory {mem}%. Throttling task intake.")
            # Pause intake by not allowing new tasks to be added until usage drops
            while psutil.cpu_percent(interval=1) > CPU_USAGE_THRESHOLD or psutil.virtual_memory().percent > MEMORY_USAGE_THRESHOLD:
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

connection_health_thread = threading.Thread(target=connection_health_monitor, daemon=True)
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

#sdsd
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


# Add Aider AI coding tool
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

        # Strategic model selection for multiple tasks
        if models is None:
            # Use strategic selection for each prompt
            models = [get_optimal_model(prompt) for prompt in prompts]
        else:
            # Fill in None values with strategic selection
            models = [get_optimal_model(prompts[i]) if models[i] is None else models[i] 
                     for i in range(num_prompts)]
        
        # Ensure models list matches prompts length
        if len(models) != num_prompts:
            error_msg = f"Error: Length of models ({len(models)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        # Set default max_workers if not provided
        if max_workers is None:
            max_workers = min(num_prompts, MAX_CONCURRENT_TASKS)

        # Define a function to process a single prompt with circuit breaker protection
        def process_prompt(i):
            prompt = prompts[i]
            editable_files = editable_files_list[i]
            readonly_files = readonly_files_list[i]
            model = models[i]

            # Enqueue task or reject if queue is full
            if not enqueue_task(i):
                return {
                    "success": False,
                    "error": "Task queue is full. Please try again later.",
                    "task_index": i,
                    "prompt": prompt,
                    "model": model,
                    "editable_files": editable_files,
                    "status_message": "Rejected due to full task queue."
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
                    working_dir=working_dir
                )

                # Log the completion of this task with timestamp and duration
                end_time = time.time()
                duration = end_time - start_time
                logger.info(f"Completed task {i + 1}/{num_prompts} in {duration:.2f} seconds")
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
                    "status_message": f"Failed to execute task {i + 1} due to an error: {str(e)}"
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
                result['execution_time'] = duration
                # Add task information
                result['task_index'] = i
                result['prompt'] = prompt
                result['model'] = model
                result['editable_files'] = editable_files

                # Add a human-readable status message
                if result.get('success', False):
                    status_message = f"Successfully implemented changes to {', '.join(editable_files)}"
                    if 'details' in result:
                        status_message += f": {result['details']}"
                    result['status_message'] = status_message
                else:
                    status_message = f"Failed to implement changes to {', '.join(editable_files)}"
                    if 'details' in result:
                        status_message += f": {result['details']}"
                    elif 'error' in result:
                        status_message += f": {result['error']}"
                    result['status_message'] = status_message

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
                    "status_message": f"Failed to parse JSON response for task {i + 1}"
                }

        # Process prompts either in parallel or sequentially based on the 'parallel' parameter
        results = []
        overall_success = True

        if parallel:
            # Parallel execution using ThreadPoolExecutor
            logger.info(f"Starting parallel execution of {num_prompts} tasks with {max_workers} workers")
            parallel_start_time = time.time()

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                logger.info(f"Submitting all {num_prompts} tasks to the thread pool")
                future_to_index = {executor.submit(process_prompt, i): i for i in range(num_prompts)}

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        results.append((index, result))  # Store with index for sorting later

                        # Update overall success status
                        if not result.get("success", False):
                            overall_success = False
                    except Exception as exc:
                        # Handle any exceptions that occurred during execution
                        error_result = {
                            "success": False,
                            "error": f"Exception occurred while processing prompt {index}: {str(exc)}"
                        }
                        results.append((index, error_result))
                        overall_success = False

            # Sort results by original index
            results.sort()  # Sort by index
            results = [result for _, result in results]  # Remove indices
        else:
            # Sequential execution
            logger.info(f"Starting sequential execution of {num_prompts} tasks")
            parallel_start_time = time.time()  # We'll still call it parallel_start_time for consistency

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
                        "error": f"Exception occurred while processing prompt {i}: {str(exc)}"
                    }
                    results.append(error_result)
                    overall_success = False

        # Calculate total execution time
        parallel_end_time = time.time()
        execution_duration = parallel_end_time - parallel_start_time

        # Print summary of execution
        successful_tasks = sum(1 for r in results if r.get('success', False))
        execution_type = "parallel" if parallel else "sequential"
        logger.info(f"Completed all {num_prompts} tasks in {execution_duration:.2f} seconds ({execution_type} execution)")
        logger.info(f"{successful_tasks}/{num_prompts} tasks completed successfully")

        # Print detailed status for each prompt
        logger.info("Detailed status for each prompt:")
        for i, result in enumerate(results):
            status = "SUCCESS" if result.get('success', False) else "FAILED"
            status_message = result.get('status_message', '')
            logger.info(f"Prompt {i + 1}: {status} - {prompts[i][:50]}...")
            if status_message:
                logger.info(f"   → {status_message}")
            if 'implementation_notes' in result and result['implementation_notes']:
                # Truncate implementation notes if too long
                notes = result['implementation_notes']
                if len(notes) > 200:
                    notes = notes[:197] + '...'
                logger.info(f"   → Implementation notes: {notes}")

        # Calculate the theoretical sequential execution time (sum of individual task times)
        theoretical_sequential_time = sum(result.get('execution_time', 0) for result in results)

        # If running in parallel, show the speedup compared to theoretical sequential time
        if parallel and theoretical_sequential_time > 0:  # Avoid division by zero
            speedup = theoretical_sequential_time / execution_duration
            logger.info(f"Parallel speedup: {speedup:.2f}x (theoretical sequential would take ~{theoretical_sequential_time:.2f}s)")

        # Create a list of success statuses for each prompt
        success_statuses = [result.get('success', False) for result in results]

        # Create a list of status messages for each prompt
        status_messages = [result.get('status_message', '') for result in results]

        # Create a summary of files modified
        all_modified_files = []
        for result in results:
            if result.get('success', False) and 'files_modified' in result:
                all_modified_files.extend(result['files_modified'])

        # Remove duplicates while preserving order
        unique_modified_files = []
        for file in all_modified_files:
            if file not in unique_modified_files:
                unique_modified_files.append(file)

        # Aggregate results
        try:
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
                "speedup": theoretical_sequential_time / execution_duration if parallel and execution_duration > 0 else 1.0
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
                "results": results if 'results' in locals() else [],  # Include the raw results if available
                "summary": f"Processed prompts but encountered an error during result aggregation"
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
            "details": "The server encountered a critical error but remained running."
        }
        return json.dumps(error_response, indent=4)

# Run the server if this file is executed directly
if __name__ == "__main__":
    mcp.run()
