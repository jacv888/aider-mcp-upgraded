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

## Step 2: Install MyMCP

### Option 1: Using pip

```bash
pip install -e .
```

### Option 2: Manual installation

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

Create a `.env` file in the project root directory with the following content:

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

## Troubleshooting

### Common Issues

1. **Aider not found**: Make sure Aider is properly installed and available in your PATH.
   
2. **Model not available**: If you get errors about models not being available, check your API keys and model access.

3. **Permission issues**: Make sure you have write permissions to the directories where you're trying to create files.

### Getting Help

If you encounter any issues, please open an issue on the GitHub repository with details about your problem and the steps you've taken to resolve it.
