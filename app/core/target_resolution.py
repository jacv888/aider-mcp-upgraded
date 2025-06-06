import os
import re
import logging
from typing import List, Optional

logger = logging.getLogger("target_resolution")

# Regex patterns for detecting decorators and function/class definitions
DECORATOR_PATTERN = re.compile(r"^\s*@(\w+)(?:\((.*?)\))?\s*$", re.MULTILINE)
FUNCTION_PATTERN = re.compile(r"^\s*def\s+(\w+)\s*\(", re.MULTILINE)
CLASS_PATTERN = re.compile(r"^\s*class\s+(\w+)\s*[\(:]", re.MULTILINE)

def resolve_target_elements(
    target_elements: List[str],
    file_paths: List[str],
    working_dir: Optional[str] = None,
) -> List[str]:
    """
    Expands decorator targets to actual function or class names by scanning files.

    Args:
        target_elements: List of target elements, possibly including decorators.
        file_paths: List of file paths to search for targets.
        working_dir: Optional base directory for file paths.

    Returns:
        List of resolved target element names.
    """
    resolved_targets = set()
    decorator_targets = set()
    normal_targets = set()

    # Separate decorator targets (starting with '@') and normal targets
    for target in target_elements:
        if target.startswith("@"):
            decorator_targets.add(target[1:])
        else:
            normal_targets.add(target)

    # Add normal targets directly
    resolved_targets.update(normal_targets)

    # If no decorator targets, return early
    if not decorator_targets:
        return list(resolved_targets)

    # Scan files to find functions/classes with matching decorators
    for file_path in file_paths:
        full_path = os.path.join(working_dir, file_path) if working_dir else file_path
        if not os.path.isfile(full_path):
            logger.warning(f"File not found during target resolution: {full_path}")
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {full_path} during target resolution: {e}")
            continue

        # Find all decorators with their line numbers
        decorator_matches = [(m.start(), m.group(1)) for m in DECORATOR_PATTERN.finditer(content)]

        # Find all function and class definitions with their line numbers and names
        func_matches = [(m.start(), m.group(1)) for m in FUNCTION_PATTERN.finditer(content)]
        class_matches = [(m.start(), m.group(1)) for m in CLASS_PATTERN.finditer(content)]

        # Combine function and class matches sorted by position
        def_class_matches = sorted(func_matches + class_matches, key=lambda x: x[0])

        # Map decorator positions to the next function/class definition
        for dec_pos, dec_name in decorator_matches:
            if dec_name not in decorator_targets:
                continue

            # Find the next function/class after decorator
            target_name = None
            for def_pos, def_name in def_class_matches:
                if def_pos > dec_pos:
                    target_name = def_name
                    break

            if target_name:
                resolved_targets.add(target_name)
                logger.info(f"Resolved decorator @{dec_name} to target '{target_name}' in {file_path}")

    return list(resolved_targets)


def find_targets_in_file(file_path: str, target_elements: List[str]) -> List[str]:
    """
    Finds which target elements exist in a specific file.

    Args:
        file_path: Path to the file to search.
        target_elements: List of target element names to find.

    Returns:
        List of target elements found in the file.
    """
    found_targets = set()

    if not os.path.isfile(file_path):
        logger.warning(f"File not found during target search: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path} during target search: {e}")
        return []

    # Search for function and class definitions
    func_names = set(m.group(1) for m in FUNCTION_PATTERN.finditer(content))
    class_names = set(m.group(1) for m in CLASS_PATTERN.finditer(content))

    # Check for presence of target elements in functions or classes
    for target in target_elements:
        if target in func_names or target in class_names:
            found_targets.add(target)

    return list(found_targets)
