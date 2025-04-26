# MyMCP - Multiple Coding Prompts with Aider

MyMCP is a Python application that enables parallel execution of multiple AI coding tasks using the Aider tool. It provides a framework for running multiple coding prompts simultaneously, improving efficiency and reducing execution time.

## Features

- **Parallel Execution**: Run multiple AI coding tasks simultaneously for faster results
- **Sequential Execution**: Option to run tasks sequentially when needed
- **Detailed Reporting**: Get comprehensive reports on task execution, including success/failure status and implementation details
- **MCP Integration**: Built on the Model Context Protocol (MCP) for standardized AI model interactions
- **Performance Metrics**: Compare parallel vs. sequential execution times

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for tracking code changes)
- Aider CLI tool

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/myMcp.git
   cd myMcp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   Create a `.env` file in the project root with the following variables:
   ```
   AIDER_MODEL=your-preferred-model
   ```

## Usage

### Basic Usage

```python
from aider_mcp import code_with_multiple_ai

# Define your prompts and files
prompts = [
    "Create a simple hello world function in Python",
    "Create a simple calculator function that adds two numbers in Python"
]

editable_files_list = [
    ["hello.py"],
    ["calculator.py"]
]

readonly_files_list = [
    [],
    []
]

# Optional: specify models for each prompt
models = [
    "gpt-4.1-mini",
    "gpt-4.1-mini"
]

# Run the tasks in parallel
result = code_with_multiple_ai(
    prompts=prompts,
    working_dir=".",
    editable_files_list=editable_files_list,
    readonly_files_list=readonly_files_list,
    models=models,
    max_workers=2,  # Number of parallel workers
    parallel=True   # Set to False for sequential execution
)

# Parse and use the result
import json
parsed_result = json.loads(result)
print(parsed_result["summary"])
```

### Running Tests

The project includes tests to verify functionality and compare parallel vs. sequential execution:

```bash
python tests/test_multiple_ai.py
```

## Architecture

The project consists of several key components:

- **aider_mcp.py**: Main module providing the `code_with_multiple_ai` function
- **aider_ai_code.py**: Integration with the Aider tool for AI coding
- **aider_adapter.py**: Custom adapter for the Aider CLI tool
- **tests/**: Test files to verify functionality

## Response Format

The `code_with_multiple_ai` function returns a JSON string with the following structure:

```json
{
    "success": true,
    "results": [...],
    "success_statuses": [true, true, false, true],
    "status_messages": ["Successfully implemented...", ...],
    "summary": "Processed 4 prompts with 3 successes",
    "execution_time": 13.5,
    "execution_type": "parallel",
    "theoretical_sequential_time": 40.2,
    "modified_files": ["file1.py", "file2.py"],
    "speedup": 2.98
}
```

## Performance

Parallel execution typically provides a 2-3x speedup compared to sequential execution, depending on the number of tasks and available system resources.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Aider](https://aider.chat) - AI pair programming tool
- [MCP (Model Context Protocol)](https://modelcontextprotocol.ai) - Protocol for AI model interactions
