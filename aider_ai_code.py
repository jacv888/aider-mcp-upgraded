import json
from typing import List, Optional, Dict, Any, Union
import os
import os.path
import subprocess
from dotenv import load_dotenv
# Import our custom implementation instead of the actual aider package
from aider_adapter import Model, Coder, InputOutput
from aider_mcp_server.atoms.logging import get_logger

# Load environment variables with MCP aider-mcp as primary source
load_dotenv()  # Load from current directory (lowest priority)
load_dotenv(os.path.expanduser("~/.config/aider/.env"))  # Load global config (medium priority)
load_dotenv("/Users/jacquesv/MCP/aider-mcp/.env", override=True)  # PRIMARY source (highest priority)

# Import strategic model selector
from strategic_model_selector import get_optimal_model

# Configure logging for this module
logger = get_logger(__name__)

# Type alias for response dictionary
ResponseDict = Dict[str, Union[bool, str]]


def _get_changes_diff_or_content(
    relative_editable_files: List[str], working_dir: str = None
) -> str:
    """
    Get the git diff for the specified files, or their content if git fails.

    Args:
        relative_editable_files: List of files to check for changes
        working_dir: The working directory where the git repo is located
    """
    diff = ""
    # Log current directory for debugging
    current_dir = os.getcwd()
    logger.info(f"Current directory during diff: {current_dir}")
    if working_dir:
        logger.info(f"Using working directory: {working_dir}")

    # Always attempt to use git
    files_arg = " ".join(relative_editable_files)
    logger.info(f"Attempting to get git diff for: {' '.join(relative_editable_files)}")

    try:
        # Use git -C to specify the repository directory
        if working_dir:
            diff_cmd = f"git -C {working_dir} diff -- {files_arg}"
        else:
            diff_cmd = f"git diff -- {files_arg}"

        logger.info(f"Running git command: {diff_cmd}")
        diff = subprocess.check_output(
            diff_cmd, shell=True, text=True, stderr=subprocess.PIPE
        )
        logger.info("Successfully obtained git diff.")
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"Git diff command failed with exit code {e.returncode}. Error: {e.stderr.strip()}"
        )
        logger.warning("Falling back to reading file contents.")
        diff = "Git diff failed. Current file contents:\n\n"
        for file_path in relative_editable_files:
            full_path = (
                os.path.join(working_dir, file_path) if working_dir else file_path
            )
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r") as f:
                        content = f.read()
                        diff += f"--- {file_path} ---\n{content}\n\n"
                        logger.info(f"Read content for {file_path}")
                except Exception as read_e:
                    logger.error(
                        f"Failed reading file {full_path} for content fallback: {read_e}"
                    )
                    diff += f"--- {file_path} --- (Error reading file)\n\n"
            else:
                logger.warning(f"File {full_path} not found during content fallback.")
                diff += f"--- {file_path} --- (File not found)\n\n"
    except Exception as e:
        logger.error(f"Unexpected error getting git diff: {str(e)}")
        diff = f"Error getting git diff: {str(e)}\n\n"  # Provide error in diff string as fallback
    return diff


def _check_for_meaningful_changes(
    relative_editable_files: List[str], working_dir: str = None
) -> bool:
    """
    Check if the edited files contain meaningful content.

    Args:
        relative_editable_files: List of files to check
        working_dir: The working directory where files are located
    """
    for file_path in relative_editable_files:
        # Use the working directory if provided
        full_path = os.path.join(working_dir, file_path) if working_dir else file_path
        logger.info(f"Checking for meaningful content in: {full_path}")

        if os.path.exists(full_path):
            try:
                with open(full_path, "r") as f:
                    content = f.read()
                    # Check if the file has more than just whitespace or a single comment line,
                    # or contains common code keywords. This is a heuristic.
                    stripped_content = content.strip()
                    if stripped_content and (
                        len(stripped_content.split("\n")) > 1
                        or any(
                            kw in content
                            for kw in [
                                "def ",
                                "class ",
                                "import ",
                                "from ",
                                "async def",
                            ]
                        )
                    ):
                        logger.info(f"Meaningful content found in: {file_path}")
                        return True
            except Exception as e:
                logger.error(
                    f"Failed reading file {full_path} during meaningful change check: {e}"
                )
                # If we can't read it, we can't confirm meaningful change from this file
                continue
        else:
            logger.info(
                f"File not found or empty, skipping meaningful check: {full_path}"
            )

    logger.info("No meaningful changes detected in any editable files.")
    return False


def _process_coder_results(
    relative_editable_files: List[str], working_dir: str = None, aider_result: str = None
) -> ResponseDict:
    """
    Process the results after Aider has run, checking for meaningful changes
    and retrieving the diff or content.

    Args:
        relative_editable_files: List of files that were edited
        working_dir: The working directory where the git repo is located
        aider_result: The raw output from Aider's execution

    Returns:
        Dictionary with success status, diff output, and additional details
    """
    diff_output = _get_changes_diff_or_content(relative_editable_files, working_dir)
    logger.info("Checking for meaningful changes in edited files...")
    has_meaningful_content = _check_for_meaningful_changes(
        relative_editable_files, working_dir
    )

    # Extract implementation details from Aider's output
    implementation_details = ""
    if aider_result:
        # Check if it's a success message
        if aider_result.startswith("Success:"):
            # Extract the actual content after "Success:"
            implementation_details = aider_result[9:].strip()
        # Check if it's an error message
        elif aider_result.startswith("Failed:"):
            implementation_details = aider_result[8:].strip()
        else:
            # Just use the raw output
            implementation_details = aider_result.strip()

    # Create a more detailed response
    if has_meaningful_content:
        logger.info("Meaningful changes found. Processing successful.")
        return {
            "success": True,
            "diff": diff_output,
            "details": "Meaningful changes were successfully implemented.",
            "implementation_notes": implementation_details,
            "files_modified": relative_editable_files
        }
    else:
        logger.warning(
            "No meaningful changes detected. Processing marked as unsuccessful."
        )
        # Even if no meaningful content, provide the diff/content if available
        return {
            "success": False,
            "diff": diff_output or "No meaningful changes detected and no diff/content available.",
            "details": "No meaningful changes were detected in the files.",
            "implementation_notes": implementation_details,
            "files_attempted": relative_editable_files
        }


def _format_response(response: ResponseDict) -> str:
    """
    Format the response dictionary as a JSON string.

    Args:
        response: Dictionary containing success status and diff output

    Returns:
        JSON string representation of the response
    """
    return json.dumps(response, indent=4)


def code_with_aider(
    ai_coding_prompt: str,
    relative_editable_files: List[str],
    relative_readonly_files: List[str],
    model: str = None,  # Made optional for strategic selection
    working_dir: str = None,
) -> str:
    """
    Run Aider to perform AI coding tasks based on the provided prompt and files.
    This implementation uses a custom wrapper around the aider CLI tool.

    Args:
        ai_coding_prompt (str): The prompt for the AI to execute.
        relative_editable_files (List[str]): List of files that can be edited.
        relative_readonly_files (List[str], optional): List of files that can be read but not edited. Defaults to [].
        model (str): The model to use.
        working_dir (str, required): The working directory where git repository is located and files are stored.

    Returns:
        Dict[str, Any]: {'success': True/False, 'diff': str with git diff output}
    """
    logger.info("Starting code_with_aider process.")
    logger.info(f"Prompt: '{ai_coding_prompt}'")

    # Working directory must be provided
    if not working_dir:
        error_msg = "Error: working_dir is required for code_with_aider"
        logger.error(error_msg)
        return json.dumps({"success": False, "diff": error_msg})

    logger.info(f"Working directory: {working_dir}")
    logger.info(f"Editable files: {relative_editable_files}")
    logger.info(f"Readonly files: {relative_readonly_files}")
    logger.info(f"Model: {model}")

    # Store the current directory
    original_dir = os.getcwd()

    try:
        # Change to the working directory to run aider
        os.chdir(working_dir)
        logger.info(f"Changed to working directory: {working_dir}")

        # Strategic model selection - use optimal model for the task
        selected_model = get_optimal_model(ai_coding_prompt, model)
        logger.info(f"Strategic model selection: '{selected_model}' for prompt: {ai_coding_prompt[:50]}...")

        # Configure the model
        logger.info("Configuring AI model...")
        ai_model = Model(selected_model)
        logger.info("AI model configured.")

        # Create the coder instance
        logger.info("Creating Aider coder instance...")
        # Use working directory for chat history file
        chat_history_file = os.path.join(working_dir, ".aider.chat.history.md")
        logger.info(f"Using chat history file: {chat_history_file}")

        # Convert relative paths to absolute paths
        abs_editable_files = [
            os.path.join(working_dir, file) for file in relative_editable_files
        ]
        abs_readonly_files = [
            os.path.join(working_dir, file) for file in relative_readonly_files
        ]

        coder = Coder.create(
            main_model=ai_model,
            io=InputOutput(
                yes=True,
                chat_history_file=chat_history_file,
            ),
            fnames=abs_editable_files,
            read_only_fnames=abs_readonly_files,
            auto_commits=False,  # We'll handle commits separately
            suggest_shell_commands=False,
            detect_urls=False,
            use_git=True,  # Always use git
        )
        logger.info("Aider coder instance created successfully.")

        # Run the coding session using the CLI
        logger.info("Starting Aider coding session...")
        aider_result = coder.run(ai_coding_prompt)
        logger.info(f"Aider coding session result: {aider_result if len(aider_result) < 100 else aider_result[:100] + '...'}")
        logger.info("Aider coding session finished.")

        # Process the results after the coder has run
        logger.info("Processing coder results...")
        try:
            response = _process_coder_results(
                relative_editable_files,
                working_dir,
                aider_result
            )
            logger.info("Coder results processed.")
        except Exception as e:
            logger.exception(f"Error processing coder results: {str(e)}")
            response = {
                "success": False,
                "diff": f"Error processing files after execution: {str(e)}",
                "details": "An error occurred while processing the results.",
                "error": str(e),
                "files_attempted": relative_editable_files
            }

    except Exception as e:
        logger.exception(f"Critical Error in code_with_aider: {str(e)}")
        response = {
            "success": False,
            "diff": f"Unhandled Error during Aider execution: {str(e)}",
            "details": "A critical error occurred during the Aider execution process.",
            "error": str(e),
            "error_type": type(e).__name__,
            "files_attempted": relative_editable_files
        }
    finally:
        # Restore original directory
        os.chdir(original_dir)
        logger.info(f"Restored original directory: {original_dir}")

    formatted_response = _format_response(response)
    logger.info(f"code_with_aider process completed. Success: {response.get('success')}")
    logger.info(f"Formatted response: {formatted_response[:200] + '...' if len(formatted_response) > 200 else formatted_response}")
    return formatted_response
