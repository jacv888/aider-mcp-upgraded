import os
import sys

def setup_directories():
    """
    Ensures all necessary directory structures are created for the aider-mcp system.
    """
    # Define the base directory for logs and AI-related data
    # Assuming this script is run from the project root or a level below it.
    # If run from 'app/scripts', then '..' would be the project root.
    # For simplicity, let's assume it's run from the project root.
    
    # Directories explicitly requested by the user
    directories_to_create = [
        "logs/current",
        "logs/archive",
        "ai-logs/active",
        "ai-logs/archive",
    ]

    # Add any other directories that might be needed based on common patterns
    # For example, a directory for temporary files or configuration files if they are not in the root
    # Based on the provided summaries, these are the most evident ones.
    # If configuration files were to be stored in a specific directory, e.g., 'config/', it would be added here.
    # For now, sticking to the log/AI-log structure.

    print("Setting up necessary directories...")

    for path in directories_to_create:
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Ensured directory exists: {path}")
        except OSError as e:
            print(f"Error creating directory {path}: {e}", file=sys.stderr)

    print("Directory setup complete.")

if __name__ == "__main__":
    setup_directories()
