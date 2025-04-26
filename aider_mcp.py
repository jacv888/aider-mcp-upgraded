from mcp.server.fastmcp import FastMCP
import os
from typing import List, Optional
from aider_ai_code import code_with_aider

FALL_BACK_MODEL = "gpt-4.1-mini"

# Create an MCP server
mcp = FastMCP("Aidar Coder")

# Create an MCP server
mcp = FastMCP("Aidar Coder")


# Add Aider AI coding tool
@mcp.tool()
def code_with_ai(
        prompt: str,
        working_dir: str,
        editable_files: List[str],
        readonly_files: Optional[List[str]] = None,
        model: Optional[str] = None,
) -> str:
    """
    Use Aider to perform AI coding tasks based on the provided prompt and files.

    Args:
        prompt: The natural language prompt describing what code changes to make
        working_dir: working directory where the files are located
        editable_files: List of files that can be edited by the AI
        readonly_files: Optional list of files that can be read but not edited (for context)
        model: Optional AI model to use (default: defined in environment variable or fallback model)

    Returns:
        JSON string with results including success status and diff output
    """
    import json

    try:
        # Set default empty list for readonly files if not provided
        if readonly_files is None:
            readonly_files = []

        # Set default model if not provided
        if model is None:
            model = os.environ.get("AIDER_MODEL", FALL_BACK_MODEL)

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
        print(f"Error in code_with_ai: {str(e)}")

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
    Use Multiple Aider agents to perform AI coding tasks based on the provided prompts and files.
    This tool will provide you multiple agents that can run simultaneously to write the code.
    It's important to provide it tasks that can run in parallel and have no dependencies on each other.
    Think deep and plan the tasks and just run the tasks that can run in parallel.
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

        # Set default models if not provided
        if models is None:
            default_model = os.environ.get("AIDER_MODEL", FALL_BACK_MODEL)
            models = [default_model for _ in range(num_prompts)]
        elif len(models) != num_prompts:
            error_msg = f"Error: Length of models ({len(models)}) must match length of prompts ({num_prompts})"
            return json.dumps({"success": False, "error": error_msg})

        # Set default max_workers if not provided
        if max_workers is None:
            max_workers = num_prompts

        # Define a function to process a single prompt
        def process_prompt(i):
            prompt = prompts[i]
            editable_files = editable_files_list[i]
            readonly_files = readonly_files_list[i]
            model = models[i]

            try:
                # Log the start of this task with timestamp
                start_time = time.time()
                print(f"[{time.strftime('%H:%M:%S')}] Starting task {i + 1}/{num_prompts}: {prompt[:50]}...")

                # Call the Aider integration function
                result_json = code_with_aider(
                    ai_coding_prompt=prompt,
                    relative_editable_files=editable_files,
                    relative_readonly_files=readonly_files,
                    model=model,
                    working_dir=working_dir
                )

                # Log the completion of this task with timestamp and duration
                end_time = time.time()
                duration = end_time - start_time
                print(f"[{time.strftime('%H:%M:%S')}] Completed task {i + 1}/{num_prompts} in {duration:.2f} seconds")
            except Exception as e:
                # Log the error but continue processing
                print(f"[{time.strftime('%H:%M:%S')}] Error in task {i + 1}/{num_prompts}: {str(e)}")
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
            print(
                f"\n[{time.strftime('%H:%M:%S')}] Starting parallel execution of {num_prompts} tasks with {max_workers} workers")
            parallel_start_time = time.time()

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                print(f"[{time.strftime('%H:%M:%S')}] Submitting all {num_prompts} tasks to the thread pool")
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
            print(f"\n[{time.strftime('%H:%M:%S')}] Starting sequential execution of {num_prompts} tasks")
            parallel_start_time = time.time()  # We'll still call it parallel_start_time for consistency

            for i in range(num_prompts):
                try:
                    print(f"[{time.strftime('%H:%M:%S')}] Processing task {i + 1}/{num_prompts} sequentially")
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
        print(
            f"\n[{time.strftime('%H:%M:%S')}] Completed all {num_prompts} tasks in {execution_duration:.2f} seconds ({execution_type} execution)")
        print(f"[{time.strftime('%H:%M:%S')}] {successful_tasks}/{num_prompts} tasks completed successfully")

        # Print detailed status for each prompt
        print(f"\n[{time.strftime('%H:%M:%S')}] Detailed status for each prompt:")
        for i, result in enumerate(results):
            status = "SUCCESS" if result.get('success', False) else "FAILED"
            status_message = result.get('status_message', '')
            print(f"[{time.strftime('%H:%M:%S')}] Prompt {i + 1}: {status} - {prompts[i][:50]}...")
            if status_message:
                print(f"   → {status_message}")
            if 'implementation_notes' in result and result['implementation_notes']:
                # Truncate implementation notes if too long
                notes = result['implementation_notes']
                if len(notes) > 200:
                    notes = notes[:197] + '...'
                print(f"   → Implementation notes: {notes}")

        # Calculate the theoretical sequential execution time (sum of individual task times)
        theoretical_sequential_time = sum(result.get('execution_time', 0) for result in results)

        # If running in parallel, show the speedup compared to theoretical sequential time
        if parallel and theoretical_sequential_time > 0:  # Avoid division by zero
            speedup = theoretical_sequential_time / execution_duration
            print(
                f"[{time.strftime('%H:%M:%S')}] Parallel speedup: {speedup:.2f}x (theoretical sequential would take ~{theoretical_sequential_time:.2f}s)")

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
            print(f"Critical error in code_with_multiple_ai: {str(e)}")
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
        print(f"Critical error in code_with_multiple_ai: {str(e)}")
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
