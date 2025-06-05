"""
Smart Target Detection for Automatic Context Extraction

This module automatically detects function/class names from prompts
to enable automatic context extraction without manual intervention.
"""

import re
import os
from typing import List, Optional, Set
import logging

logger = logging.getLogger(__name__)

def extract_targets_from_prompt(prompt: str, file_content: str = None) -> List[str]:
    """
    Automatically extract function/class names from natural language prompts.
    
    This function looks for common patterns in prompts that indicate specific
    functions or classes the user wants to work with, enabling automatic
    context extraction for token savings.
    
    Args:
        prompt: The natural language prompt from the user
        file_content: Optional file content to verify targets exist
        
    Returns:
        List of detected function/class names that exist in the code
        
    Examples:
        "Fix the login_user function" -> ["login_user"]
        "Update UserManager class" -> ["UserManager"] 
        "Debug the authenticate method" -> ["authenticate"]
        "The calculate_sum function has a bug" -> ["calculate_sum"]
    """
    
    # Patterns for detecting function/class names in prompts
    patterns = [
        # Direct function references
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?(\w+)\s+function',
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?(\w+)\s+method',
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?(\w+)\s+class',
        
        # Function with issues
        r'(\w+)\s+function\s+(?:has\s+)?(?:a\s+)?(?:bug|issue|problem|error)',
        r'(\w+)\s+method\s+(?:has\s+)?(?:a\s+)?(?:bug|issue|problem|error)',
        r'(\w+)\s+class\s+(?:has\s+)?(?:a\s+)?(?:bug|issue|problem|error)',
        
        # Function not working
        r'(\w+)\s+function\s+(?:is\s+)?(?:not\s+)?(?:working|broken|failing)',
        r'(\w+)\s+method\s+(?:is\s+)?(?:not\s+)?(?:working|broken|failing)',
        
        # Bug in function
        r'bug\s+in\s+(?:the\s+)?(\w+)\s+function',
        r'bug\s+in\s+(?:the\s+)?(\w+)\s+method',
        r'bug\s+in\s+(?:the\s+)?(\w+)\s+class',
        
        # Error in function
        r'error\s+in\s+(?:the\s+)?(\w+)\s+function',
        r'error\s+in\s+(?:the\s+)?(\w+)\s+method',
        
        # Specific function actions
        r'add\s+(?:a\s+)?(\w+)\s+function',
        r'create\s+(?:a\s+)?(\w+)\s+function',
        r'write\s+(?:a\s+)?(\w+)\s+function',
        
        # Function needs improvement
        r'improve\s+(?:the\s+)?(\w+)\s+function',
        r'optimize\s+(?:the\s+)?(\w+)\s+function',
        
        # Error handling patterns
        r'add\s+error\s+handling\s+to\s+(?:the\s+)?(\w+)',
        r'add\s+(?:\w+\s+)?(?:to\s+)?(?:the\s+)?(\w+)\s+function',
        
        # Direct function mentions (more conservative)
        r'(?:^|\s)(\w+)\(\)',  # function() calls
        r'def\s+(\w+)',        # def function_name
        r'class\s+(\w+)',      # class ClassName
    ]
    
    detected_targets = set()
    
    # Extract targets using patterns
    for pattern in patterns:
        matches = re.findall(pattern, prompt, re.IGNORECASE)
        for match in matches:
            # Filter out common words that aren't likely function names
            if len(match) > 2 and not _is_common_word(match):
                detected_targets.add(match)
    
    # Convert to list
    candidate_targets = list(detected_targets)
    
    # If file content provided, verify targets actually exist in the code
    if file_content and candidate_targets:
        verified_targets = []
        for target in candidate_targets:
            if _target_exists_in_code(target, file_content):
                verified_targets.append(target)
        
        if verified_targets:
            logger.info(f"Auto-detected targets from prompt: {verified_targets}")
            return verified_targets
        else:
            logger.info(f"Detected targets {candidate_targets} but none found in code")
            return []
    
    if candidate_targets:
        logger.info(f"Auto-detected targets from prompt: {candidate_targets}")
    
    return candidate_targets

def _is_common_word(word: str) -> bool:
    """Filter out common English words that aren't likely function names."""
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'can', 'may', 'might', 'must', 'this', 'that', 'these', 'those',
        'fix', 'bug', 'error', 'issue', 'problem', 'update', 'change', 'add',
        'not', 'working', 'broken', 'failing', 'function', 'method', 'class'
    }
    return word.lower() in common_words

def _target_exists_in_code(target: str, file_content: str) -> bool:
    """Check if the target function/class actually exists in the code."""
    # Look for function or class definitions
    patterns = [
        f'def {target}\\(',
        f'class {target}\\b',
        f'def {target}\\s*\\(',
        f'class {target}\\s*[\\(:]'
    ]
    
    for pattern in patterns:
        if re.search(pattern, file_content, re.IGNORECASE):
            return True
    
    return False

def should_use_auto_detection() -> bool:
    """Check if automatic target detection is enabled."""
    return os.getenv("ENABLE_AUTO_TARGET_DETECTION", "false").lower() == "true"

def get_auto_detected_targets(prompt: str, file_paths: List[str] = None, working_dir: str = None) -> Optional[List[str]]:
    """
    Get automatically detected targets if auto-detection is enabled.
    
    Args:
        prompt: The user's prompt
        file_paths: Optional list of file paths to check targets against
        working_dir: Working directory for file paths
        
    Returns:
        List of detected targets if auto-detection enabled and targets found,
        None if auto-detection disabled or no targets detected
    """
    
    if not should_use_auto_detection():
        return None
    
    # First pass: detect from prompt only
    targets = extract_targets_from_prompt(prompt)
    
    if not targets:
        return None
    
    # Second pass: verify against file content if files provided
    if file_paths and working_dir:
        verified_targets = []
        
        for file_path in file_paths:
            full_path = os.path.join(working_dir, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Check which targets exist in this file
                    for target in targets:
                        if _target_exists_in_code(target, file_content):
                            if target not in verified_targets:
                                verified_targets.append(target)
                                
                except Exception as e:
                    logger.warning(f"Could not read file {full_path} for target verification: {e}")
                    continue
        
        if verified_targets:
            logger.info(f"Auto-detection found verified targets: {verified_targets}")
            return verified_targets
        else:
            logger.info(f"Auto-detection found targets {targets} but none verified in code files")
            return None
    
    # Return unverified targets if no files to check against
    logger.info(f"Auto-detection found targets: {targets} (unverified)")
    return targets
