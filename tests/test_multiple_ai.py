#!/usr/bin/env python3
import json
import time
import sys
import os

# TEST_MODEL = "gpt-4.1-mini"
TEST_MODEL = "anthropic/claude-3-5-haiku-20241022"

# Add the parent directory to the path so we can import aider_mcp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aider_mcp import code_with_multiple_ai

# Define common test parameters
TEST_PROMPTS = [
    "Create a simple hello world function in Python",
    "Create a simple goodbye world function in Python",
    "Create a simple calculator function that adds two numbers in Python",
    "Create a simple function that returns the current date and time in Python"
]

TEST_WORKING_DIR = "."

TEST_EDITABLE_FILES_LIST = [
    ["hello.py"],
    ["goodbye.py"],
    ["calculator.py"],
    ["datetime_util.py"]
]

TEST_READONLY_FILES_LIST = [
    [],
    [],
    [],
    []
]

# Always use gpt-4.1-mini model as requested
TEST_MODELS = [
    TEST_MODEL,
    TEST_MODEL,
    TEST_MODEL,
    TEST_MODEL
]

def run_test(parallel=True):
    """Run the test with either parallel or sequential execution"""
    # Start timing
    start_time = time.time()

    # Determine execution mode for display
    mode = "parallel" if parallel else "sequential"
    print(f"\n{'='*50}")
    print(f"Running test in {mode.upper()} mode")
    print(f"{'='*50}")

    # Call the function with specified execution mode
    result = code_with_multiple_ai(
        prompts=TEST_PROMPTS,
        working_dir=TEST_WORKING_DIR,
        editable_files_list=TEST_EDITABLE_FILES_LIST,
        readonly_files_list=TEST_READONLY_FILES_LIST,
        models=TEST_MODELS,
        max_workers=len(TEST_PROMPTS),  # Use max workers for parallel mode
        parallel=parallel  # Set parallel mode based on parameter
    )

    # End timing
    end_time = time.time()
    total_execution_time = end_time - start_time

    # Parse the result
    parsed_result = json.loads(result)

    # Print summary
    print(f"\n{'-'*50}")
    print(f"SUMMARY ({mode.upper()} mode):")
    print(f"{'-'*50}")
    print(f"Total execution time: {total_execution_time:.2f} seconds")
    print(f"Actual {mode} execution time: {parsed_result.get('execution_time', 0):.2f} seconds")
    print(f"Theoretical sequential time: {parsed_result.get('theoretical_sequential_time', 0):.2f} seconds")

    if parallel:
        speedup = parsed_result.get('theoretical_sequential_time', 0) / parsed_result.get('execution_time', 1)
        print(f"Speedup from parallelization: {speedup:.2f}x")

    # Print success statuses
    print(f"\nSuccess statuses for each prompt:")
    print(parsed_result["success_statuses"])

    return parsed_result["success"], total_execution_time, parsed_result.get('execution_time', 0)

def test_multiple_ai():
    """Test both parallel and sequential execution and compare results"""
    # Run in parallel mode
    parallel_success, parallel_total_time, parallel_execution_time = run_test(parallel=True)

    # Clean up any files created by the first test
    for file in ["hello.py", "goodbye.py", "calculator.py", "datetime_util.py"]:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed {file} before sequential test")
            except Exception as e:
                print(f"Warning: Could not remove {file}: {e}")

    # Run in sequential mode
    sequential_success, sequential_total_time, sequential_execution_time = run_test(parallel=False)

    # Compare and print results
    print(f"\n{'='*50}")
    print("COMPARISON BETWEEN PARALLEL AND SEQUENTIAL EXECUTION")
    print(f"{'='*50}")
    print(f"Parallel total time: {parallel_total_time:.2f} seconds")
    print(f"Sequential total time: {sequential_total_time:.2f} seconds")
    print(f"Difference: {sequential_total_time - parallel_total_time:.2f} seconds")

    if parallel_execution_time > 0 and sequential_execution_time > 0:
        actual_speedup = sequential_execution_time / parallel_execution_time
        print(f"Actual speedup: {actual_speedup:.2f}x")

    # Return overall success (both tests must succeed)
    return parallel_success and sequential_success

if __name__ == "__main__":
    success = test_multiple_ai()
    print(f"\nOverall test {'succeeded' if success else 'failed'}")
