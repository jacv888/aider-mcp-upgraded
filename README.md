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
   git clone https://github.com/eiliyaabedini/aider-mcp.git
   cd aider-mcp
   ```

# Installation Guide for MyMCP

This guide will help you set up MyMCP on your system.

## Prerequisites

- Python 3.8 or higher
- Git
- Aider CLI tool

## Step 1: Install Aider

Aider is a required dependency for MyMCP. You can install it using one of the following methods:

### Option 1: One-line installer (Mac & Linux)

```bash
curl -s https://aider.chat/install.sh | sh
```

Or with wget:

```bash
wget -qO- https://aider.chat/install.sh | sh
```

### Option 2: Using pip

```bash
python -m pip install aider-install
aider-install
```

## Step 2: Install AiderMCP Requirements

### Option 1: Using pip

```bash
pip install -e .
```

### Option 2: Manual installation

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

Create a `.env` file from `.env.sample` in the project root directory with the following content:

```
# Default model to use if not specified
AIDER_MODEL=gpt-4.1-mini

# Add any other environment variables needed
```

## Step 4: Verify Installation

Run the test suite to verify that everything is working correctly:

```bash
python tests/test_multiple_ai.py
```

You should see output showing both parallel and sequential execution of AI coding tasks.

## Step 5: Use AiderMCP in Claude Desktop

```
"AiderMCP": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/path/to/aider_mcp.py"
      ]
    }
```

## Usage

### Basic Usage

```
Just ask your MCP client (Claude Desktop) to use the code_with_ai or code_with_multiple_ai tool for coding.
and provide the full path where it should create the files.

Sample of Snake game to run at same time:
Use this directory as WorkDirectory: /Users/eiliya/ai/snake 
This is the prompt for making a Snake Battle Royale,
First create a Readme and Architect file as your plan for implementation and save it as md file then, 
I want you to think deep and design tasks properly, You will use **code_with_multiple_ai **MCP tool to implement the code, so You need to give the coder good context, our coder needs some knowledge as readonly_files, so provide the location of the Readme.md and Architect.md (That you will create and is a big picture of whole project)
Important, this tools let you code in parallel but you need to be careful that your tasks has no dependency, planing is imporant, create different task branches, that each branch can be run without dependency to other branches,
then run tasks of multiple branches at same time,
even if you can design the code the way that all the tasks are seperated and can be run in one attempt (no dependency to each other) then you can run them all in one attempt:
Example:

Branch 1: Front end --> Task1: initiate front end, Task2: implement index page
Branch 2: Back end -->  Task1: initiate backend, Task2: implement api
Branch 3: Database -->  Task1: initiate database, Task2: implement database

Then in each round you can get all the Task 1 to this method
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

Game prompt:
"Snake Battle Royale Language: HTML/CSS/JavaScript (vanilla, no frameworks) Libraries: None, pure JavaScript Style: Minimalist design with accent colors in teal and orange Rules: 1. All files should be in the folder snake_battle_royale 1. Keep the code clean and reusable, use functions and classes and split the code into multiple files to keep it organized Guidelines: 2. You can move the snake around the screen using the arrow keys 3. Eat food to grow the snake 4. Avoid hitting the edges of the screen, or the snakes own body, or the enemy snake, or you lose. The game is only over when the players snake is dead. 5. There are at least 3 powerups that change the game mechanics, including effects that show how the powerups work 6. A scoring system that rewards the player for eating food and hitting powerups 7. A simple AI opponent that competes with the player using pathfinding 8. A home screen where the player can hit enter to start the game 9. A game over screen that shows your score and allows you to go back to the home screen or restart the game 10. On the game screen, display a legend containing the powerups and their names, as well as the user and enemy snake's name and score 11. When the game starts, we should have a 3 second countdown where everything is frozen in place, then the game starts"
if **code_with_multiple_ai **tool failed stop the process, I need to check it

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

- [Aider](https://aider.chat) - AI pair programming tool
- [MCP (Model Context Protocol)](https://modelcontextprotocol.ai) - Protocol for AI model interactions
