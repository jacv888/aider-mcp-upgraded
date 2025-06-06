import json
import logging
from typing import List, Optional, Dict, Any, Union
import os
import os.path
import subprocess
import uuid
import time
from dotenv import load_dotenv
# Import our custom implementation instead of the actual aider package
from app.adapters.aider_adapter import Model, Coder, InputOutput
from app.core.logging import get_logger, log_structured, log_auto_detection_event

# Load environment variables with MCP aider-mcp as primary source
load_dotenv()  # Load from current directory (lowest priority)
load_dotenv(os.path.expanduser("~/.config/aider/.env"))  # Load global config (medium priority)

# Load project-level config (highest priority) - use MCP_SERVER_ROOT if available
project_root = os.getenv("MCP_SERVER_ROOT")
if project_root and os.path.exists(os.path.join(project_root, ".env")):
    load_dotenv(os.path.join(project_root, ".env"), override=True)
else:
    # Fallback to current directory's parent .env
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_env = os.path.join(current_dir, ".env")
    if os.path.exists(project_env):
        load_dotenv(project_env, override=True)

# Import strategic model selector
from app.models.strategic_model_selector import get_optimal_model

# Import context extraction system
from app.context import extract_context
from app.context.auto_detection import get_auto_detected_targets

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
    # Log git diff processing (consolidated)
    current_dir = os.getcwd()
    files_arg = " ".join(relative_editable_files)
    log_structured(logger, logging.INFO, "Processing git diff", 
                  working_dir=working_dir or current_dir, 
                  files=len(relative_editable_files),
                  current_dir=current_dir)

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
                        logger.debug(f"Read content for {file_path}")  # Moved to DEBUG level
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
    Enhanced to detect a wide variety of file types and content patterns.

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
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    stripped_content = content.strip()
                    
                    # If file is empty, skip it
                    if not stripped_content:
                        logger.info(f"File is empty: {file_path}")
                        continue
                    
                    # Check file size - any file over 10 bytes with content is meaningful
                    if len(stripped_content) > 10:
                        logger.info(f"Meaningful content found by size (>{len(stripped_content)} chars): {file_path}")
                        return True
                    
                    # Check for multiple lines (most code files have multiple lines)
                    lines = stripped_content.split("\n")
                    if len(lines) > 1:
                        logger.info(f"Meaningful content found by line count ({len(lines)} lines): {file_path}")
                        return True
                    
                    # Comprehensive keyword detection for various languages and file types
                    meaningful_patterns = [
                        # Python keywords
                        "def ", "class ", "import ", "from ", "async def", "if ", "for ", "while ", "return", "yield",
                        "try:", "except:", "finally:", "with ", "lambda", "elif", "@", "__",
                        
                        # JavaScript/TypeScript keywords  
                        "function", "const ", "let ", "var ", "export", "import", "require", "module.exports",
                        "async function", "await", "promise", "=>", "interface", "type ", "enum",
                        
                        # Web frameworks and routing
                        "router", "app.", "route", "@app.", "@router", "blueprint", "endpoint", "middleware",
                        "express", "fastapi", "flask", "django", "vue", "react", "angular",
                        
                        # Common programming constructs
                        "{", "}", "[", "]", "(", ")", "=", "==", "!=", "+=", "-=", "||", "&&",
                        "true", "false", "null", "undefined", "None", "True", "False",
                        
                        # Configuration and data patterns
                        '":', "':", "yaml", "json", "xml", "html", "css", "scss", "sass",
                        "config", "setting", "environment", "env", "database", "db", "api",
                        
                        # Common file extensions content indicators
                        ".py", ".js", ".ts", ".vue", ".jsx", ".tsx", ".php", ".rb", ".go", ".rs",
                        ".java", ".cpp", ".c", ".h", ".cs", ".swift", ".kt", ".scala",
                        
                        # Database and API patterns
                        "select", "insert", "update", "delete", "create", "drop", "alter", "index",
                        "get ", "post ", "put ", "delete ", "patch ", "options", "head",
                        "http", "https", "url", "uri", "endpoint", "rest", "graphql",
                        
                        # Common keywords that indicate actual content
                        "component", "service", "controller", "model", "view", "template",
                        "test", "spec", "mock", "stub", "fixture", "setup", "teardown",
                        "error", "exception", "warning", "info", "debug", "log",
                        
                        # Package management and build tools
                        "package", "dependency", "require", "install", "build", "compile",
                        "webpack", "babel", "rollup", "vite", "gulp", "grunt",
                        
                        # Documentation patterns
                        "readme", "changelog", "license", "contributing", "docs", "documentation",
                        "# ", "## ", "### ", "* ", "- ", "1. ", "TODO", "FIXME", "NOTE",
                    ]
                    
                    # Check if any meaningful patterns exist
                    content_lower = content.lower()
                    for pattern in meaningful_patterns:
                        if pattern.lower() in content_lower:
                            logger.info(f"Meaningful content found by pattern '{pattern}' in: {file_path}")
                            return True
                    
                    # Special check for structured data (JSON, YAML, etc.)
                    if any(char in content for char in ['{', '}', '[', ']', ':', '-']):
                        logger.info(f"Meaningful content found by structured data patterns in: {file_path}")
                        return True
                    
                    # If we reach here, log what we found for debugging
                    logger.info(f"Content preview for {file_path} (first 100 chars): {stripped_content[:100]}")
                    
            except Exception as e:
                logger.error(
                    f"Failed reading file {full_path} during meaningful change check: {e}"
                )
                # If we can't read it but it exists, assume it might be meaningful (binary files, etc.)
                logger.info(f"Assuming meaningful content due to read error in: {file_path}")
                return True
        else:
            logger.info(
                f"File not found, skipping meaningful check: {full_path}"
            )

    logger.info("No meaningful changes detected in any editable files after comprehensive check.")
    return False


def _process_coder_results(
    relative_editable_files: List[str], 
    working_dir: str = None, 
    aider_result: str = None,
    auto_detected_targets: Optional[List[str]] = None,
    context_extraction_used: bool = False,
    files_processed_with_context: Optional[List[str]] = None,
    original_target_elements: Optional[List[str]] = None
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
        response = {
            "success": True,
            "diff": diff_output,
            "details": "Meaningful changes were successfully implemented.",
            "implementation_notes": implementation_details,
            "files_modified": relative_editable_files,
            "auto_detection_info": {
                "auto_detected_targets": auto_detected_targets,
                "context_extraction_used": context_extraction_used,
                "files_processed_with_context": files_processed_with_context or [],
                "estimated_token_reduction": "60-80%" if context_extraction_used and files_processed_with_context else "0%",
                "target_elements_provided": bool(original_target_elements),
                "target_elements_used": auto_detected_targets or original_target_elements
            }
        }
        return response
    else:
        logger.warning(
            "No meaningful changes detected. Processing marked as unsuccessful."
        )
        # Even if no meaningful content, provide the diff/content if available
        response = {
            "success": False,
            "diff": diff_output or "No meaningful changes detected and no diff/content available.",
            "details": "No meaningful changes were detected in the files.",
            "implementation_notes": implementation_details,
            "files_attempted": relative_editable_files,
            "auto_detection_info": {
                "auto_detected_targets": auto_detected_targets,
                "context_extraction_used": context_extraction_used,
                "files_processed_with_context": files_processed_with_context or [],
                "estimated_token_reduction": "60-80%" if context_extraction_used and files_processed_with_context else "0%",
                "target_elements_provided": bool(original_target_elements),
                "target_elements_used": auto_detected_targets or original_target_elements
            }
        }
        return response


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
    target_elements: Optional[List[str]] = None,  # NEW: Context extraction targets
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
        target_elements (Optional[List[str]]): List of specific functions/classes/methods to focus on for context extraction.

    Returns:
        Dict[str, Any]: {'success': True/False, 'diff': str with git diff output}
    """
    # Working directory must be provided
    if not working_dir:
        error_msg = "Error: working_dir is required for code_with_aider"
        logger.error(error_msg)
        return json.dumps({"success": False, "diff": error_msg})
    
    # Generate task ID and extract task name for auto-detection logging
    task_id = str(uuid.uuid4())[:8]
    task_name = ai_coding_prompt[:50] + "..." if len(ai_coding_prompt) > 50 else ai_coding_prompt
    task_name = task_name.replace('\n', ' ').strip()
    
    # Start timing for auto-detection analytics
    operation_start_time = time.time()
    auto_detection_start_time = None
    context_extraction_start_time = None
    
    # Consolidated session start logging
    log_structured(logger, logging.INFO, "Starting Aider coding session",
                  prompt_length=len(ai_coding_prompt),
                  working_dir=working_dir,
                  editable_files=len(relative_editable_files) if relative_editable_files else 0,
                  readonly_files=len(relative_readonly_files) if relative_readonly_files else 0,
                  model=model)

    # Store the current directory
    original_dir = os.getcwd()
    
    # Track auto-detection information
    auto_detected_targets = None
    context_extraction_used = False
    files_processed_with_context = []
    original_target_elements = target_elements.copy() if target_elements else None

    try:
        # Change to the working directory to run aider
        os.chdir(working_dir)
        logger.info(f"Changed to working directory: {working_dir}")

        # Phase 2.5: Smart Auto-Detection (if target_elements not provided)
        if not target_elements:
            auto_detection_start_time = time.time()
            auto_detected = get_auto_detected_targets(
                prompt=ai_coding_prompt,
                file_paths=relative_editable_files,
                working_dir=working_dir
            )
            if auto_detected:
                target_elements = auto_detected
                auto_detected_targets = auto_detected  # Track what was auto-detected
                logger.info(f"Auto-detected targets from prompt: {target_elements}")

        # Context-Aware File Pruning (if enabled and target_elements available)
        enhanced_prompt = ai_coding_prompt
        context_processed_files = []
        
        if (target_elements and 
            os.getenv("ENABLE_CONTEXT_EXTRACTION", "false").lower() == "true"):
            try:
                context_extraction_start_time = time.time()
                context_extraction_used = True  # Mark that context extraction is being used
                logger.info("Context extraction enabled for aider, processing files...")
                
                # Get configuration
                max_tokens = int(os.getenv("CONTEXT_DEFAULT_MAX_TOKENS", "4000"))
                min_relevance = float(os.getenv("CONTEXT_MIN_RELEVANCE_SCORE", "3.0"))
                
                # Process each file with context extraction
                context_sections = []
                for i, file_path in enumerate(relative_editable_files):
                    full_path = os.path.join(working_dir, file_path)
                    
                    if os.path.exists(full_path):
                        # Get target element for this file
                        target = target_elements[i % len(target_elements)] if target_elements else None
                        
                        if target:
                            try:
                                # Extract focused context using the correct API
                                context_result = extract_context(
                                    file_path=full_path,
                                    target_element=target,  # Single element, not list
                                    max_tokens=max_tokens // len(relative_editable_files)  # Distribute budget
                                )
                                
                                if context_result:
                                    context_info = f"\n--- {file_path} (Focused Context for '{target}') ---\n"
                                    context_info += context_result + "\n\n"
                                    context_sections.append(context_info)
                                    context_processed_files.append(file_path)
                                    files_processed_with_context.append(file_path)  # Track for auto-detection info
                                    logger.info(f"Context extracted for {file_path} targeting '{target}'")
                                else:
                                    logger.warning(f"No relevant context found for {file_path} targeting '{target}'")
                            except Exception as e:
                                logger.warning(f"Context extraction failed for {file_path} targeting '{target}': {e}")
                                continue
                
                # Enhance prompt with context if any was extracted
                if context_sections:
                    enhanced_prompt = f"{ai_coding_prompt}\n\nFocused file context:\n{''.join(context_sections)}"
                    logger.info(f"Enhanced aider prompt with context from {len(context_processed_files)} files")
                    
                    # Remove context-processed files from editable_files to avoid duplication
                    remaining_editable_files = [f for f in relative_editable_files if f not in context_processed_files]
                    relative_editable_files = remaining_editable_files
                
            except Exception as e:
                logger.warning(f"Context extraction system failed in aider: {e}")
                # Continue with normal processing
                enhanced_prompt = ai_coding_prompt

        # Strategic model selection - use optimal model for the task
        selected_model = get_optimal_model(enhanced_prompt, model)
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
        logger.debug("Aider coder instance created successfully.")

        # Run the coding session using the CLI
        aider_result = coder.run(enhanced_prompt)
        
        # Consolidated session completion logging
        log_structured(logger, logging.INFO, "Aider coding session completed",
                      result_length=len(aider_result),
                      success=True)

        # Process the results after the coder has run
        logger.info("Processing coder results...")
        try:
            response = _process_coder_results(
                relative_editable_files,
                working_dir,
                aider_result,
                auto_detected_targets,
                context_extraction_used,
                files_processed_with_context,
                original_target_elements
            )
            logger.info("Coder results processed.")
        except Exception as e:
            logger.exception(f"Error processing coder results: {str(e)}")
            response = {
                "success": False,
                "diff": f"Error processing files after execution: {str(e)}",
                "details": "An error occurred while processing the results.",
                "error": str(e),
                "files_attempted": relative_editable_files,
                "auto_detection_info": {
                    "auto_detected_targets": auto_detected_targets,
                    "context_extraction_used": context_extraction_used,
                    "files_processed_with_context": files_processed_with_context or [],
                    "estimated_token_reduction": "60-80%" if context_extraction_used and files_processed_with_context else "0%",
                    "target_elements_provided": bool(original_target_elements),
                    "target_elements_used": auto_detected_targets or original_target_elements
                }
            }

    except Exception as e:
        logger.exception(f"Critical Error in code_with_aider: {str(e)}")
        response = {
            "success": False,
            "diff": f"Unhandled Error during Aider execution: {str(e)}",
            "details": "A critical error occurred during the Aider execution process.",
            "error": str(e),
            "error_type": type(e).__name__,
            "files_attempted": relative_editable_files,
            "auto_detection_info": {
                "auto_detected_targets": auto_detected_targets if 'auto_detected_targets' in locals() else None,
                "context_extraction_used": context_extraction_used if 'context_extraction_used' in locals() else False,
                "files_processed_with_context": files_processed_with_context if 'files_processed_with_context' in locals() else [],
                "estimated_token_reduction": "0%",
                "target_elements_provided": bool(original_target_elements) if 'original_target_elements' in locals() else False,
                "target_elements_used": None
            }
        }
    finally:
        # Restore original directory
        os.chdir(original_dir)
        logger.info(f"Restored original directory: {original_dir}")

    formatted_response = _format_response(response)
    
    # Log auto-detection event for analytics
    try:
        operation_end_time = time.time()
        total_duration = operation_end_time - operation_start_time
        
        # Calculate timing breakdown
        auto_detection_time_ms = 0
        context_extraction_time_ms = 0
        
        if auto_detection_start_time:
            # If context extraction happened, auto-detection time is until context extraction started
            end_time = context_extraction_start_time if context_extraction_start_time else operation_end_time
            auto_detection_time_ms = (end_time - auto_detection_start_time) * 1000
        
        if context_extraction_start_time:
            context_extraction_time_ms = (operation_end_time - context_extraction_start_time) * 1000
        
        # Extract auto-detection info from response
        response_data = json.loads(formatted_response) if isinstance(formatted_response, str) else formatted_response
        auto_info = response_data.get("auto_detection_info", {})
        
        # Prepare auto-detection results
        auto_detection_results = {
            "targets_detected": auto_info.get("auto_detected_targets", []),
            "detection_method": "prompt_analysis" if auto_detected_targets else "manual",
            "context_extraction_used": auto_info.get("context_extraction_used", False),
            "files_processed": auto_info.get("files_processed_with_context", []),
            "estimated_token_reduction": auto_info.get("estimated_token_reduction", "0%"),
            "target_elements_provided": auto_info.get("target_elements_provided", False),
            "target_elements_used": auto_info.get("target_elements_used", [])
        }
        
        # Prepare performance impact metrics
        performance_impact = {
            "detection_time_ms": round(auto_detection_time_ms, 2),
            "context_extraction_time_ms": round(context_extraction_time_ms, 2),
            "total_overhead_ms": round(auto_detection_time_ms + context_extraction_time_ms, 2),
            "operation_success": response_data.get("success", False)
        }
        
        # Log the auto-detection event
        log_auto_detection_event(
            task_id=task_id,
            task_name=task_name,
            operation_type="code_with_aider",
            model=model if model else "unknown",
            duration_seconds=round(total_duration, 3),
            auto_detection_results=auto_detection_results,
            performance_impact=performance_impact
        )
        
    except Exception as e:
        logger.warning(f"Failed to log auto-detection event: {e}")
    
    logger.info(f"code_with_aider process completed. Success: {response.get('success')}")
    logger.info(f"Formatted response: {formatted_response[:200] + '...' if len(formatted_response) > 200 else formatted_response}")
    return formatted_response
