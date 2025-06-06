"""
Smart Target Detection for Automatic Context Extraction

This module automatically detects function/class names from prompts
to enable automatic context extraction without manual intervention.
"""

import re
import os
from typing import List, Optional, Set
import logging

# --- JS/TS Framework Detector Import ---
try:
    from app.context.js_framework_detection import JSFrameworkDetector
    JS_FRAMEWORK_SUPPORT = True
except ImportError:
    JSFrameworkDetector = None  # fallback if not available
    JS_FRAMEWORK_SUPPORT = False

logger = logging.getLogger(__name__)

def extract_targets_from_prompt(prompt: str, file_content: str = None, file_path: str = None) -> List[str]:
    """
    Automatically extract function/class/component names from natural language prompts.
    Supports Python and (optionally) JavaScript/TypeScript frameworks.

    Args:
        prompt: The natural language prompt from the user
        file_content: Optional file content to verify targets exist
        file_path: Optional file path for extension-based framework detection

    Returns:
        List of detected function/class/component names that exist in the code

    Examples:
        "Fix the login_user function" -> ["login_user"]
        "Update UserManager class" -> ["UserManager"]
        "Debug the authenticate method" -> ["authenticate"]
        "The calculate_sum function has a bug" -> ["calculate_sum"]
        "Refactor the Zod schema UserSchema" -> ["UserSchema"]
        "Update the Next.js getServerSideProps" -> ["getServerSideProps"]
    """

    # --- Python patterns (existing) ---
    patterns = [
        # --- New universal quoted creation patterns ---
        r'(?:create|add|build|make)\s+(?:a\s+new\s+)?(?:[\w\s]+)?called\s+[\'"`]([\w_]+)[\'"`]',
        r'(?:create|add|build|make)\s+(?:a\s+new\s+)?(?:[\w\s]+)?named\s+[\'"`]([\w_]+)[\'"`]',
        r'(?:create|add|build|make)\s+(?:a\s+new\s+)?(?:[\w\s]+)?named\s+(\w+)',
        r'(?:create|add|build|make)\s+(?:a\s+new\s+)?(?:[\w\s]+)?called\s+(\w+)',

        # --- New quoted function references ---
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+[\'"`]([\w_]+)[\'"`]',
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?[\'"`]([\w_]+)[\'"`](?:\s+function|\s+method|\s+class)?',

        # --- Existing patterns ---
        r'add\s+(?:a\s+new\s+)?mcp\s+tool\s+called\s+[\'"`]?(\w+)[\'"`]?',
        r'create\s+(?:a\s+new\s+)?mcp\s+tool\s+called\s+[\'"`]?(\w+)[\'"`]?',
        r'write\s+(?:a\s+new\s+)?mcp\s+tool\s+called\s+[\'"`]?(\w+)[\'"`]?',
        r'add\s+(?:a\s+new\s+)?mcp\s+tool\s+[\'"`]?(\w+)[\'"`]?',
        r'create\s+(?:a\s+new\s+)?mcp\s+tool\s+[\'"`]?(\w+)[\'"`]?',
        r'write\s+(?:a\s+new\s+)?mcp\s+tool\s+[\'"`]?(\w+)[\'"`]?',

        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?(\w+)\s+function',
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?(\w+)\s+method',
        r'(?:fix|update|debug|modify|change|improve|refactor|implement)\s+(?:the\s+)?(\w+)\s+class',

        r'(\w+)\s+function\s+(?:has\s+)?(?:a\s+)?(?:bug|issue|problem|error)',
        r'(\w+)\s+method\s+(?:has\s+)?(?:a\s+)?(?:bug|issue|problem|error)',
        r'(\w+)\s+class\s+(?:has\s+)?(?:a\s+)?(?:bug|issue|problem|error)',

        r'(\w+)\s+function\s+(?:is\s+)?(?:not\s+)?(?:working|broken|failing)',
        r'(\w+)\s+method\s+(?:is\s+)?(?:not\s+)?(?:working|broken|failing)',

        r'bug\s+in\s+(?:the\s+)?(\w+)\s+function',
        r'bug\s+in\s+(?:the\s+)?(\w+)\s+method',
        r'bug\s+in\s+(?:the\s+)?(\w+)\s+class',

        r'error\s+in\s+(?:the\s+)?(\w+)\s+function',
        r'error\s+in\s+(?:the\s+)?(\w+)\s+method',

        r'add\s+(?:a\s+)?(\w+)\s+function',
        r'create\s+(?:a\s+)?(\w+)\s+function',
        r'write\s+(?:a\s+)?(\w+)\s+function',

        r'improve\s+(?:the\s+)?(\w+)\s+function',
        r'optimize\s+(?:the\s+)?(\w+)\s+function',

        r'add\s+error\s+handling\s+to\s+(?:the\s+)?(\w+)',
        r'add\s+(?:\w+\s+)?(?:to\s+)?(?:the\s+)?(\w+)\s+function',

        r'(?:^|\s)(\w+)\(\)',  # function() calls
        r'def\s+(\w+)',        # def function_name
        r'class\s+(\w+)',      # class ClassName
    ]

    # --- JS/TS patterns (React, Next.js, Zod, etc.) ---
    js_ts_patterns = [
        # React/Component patterns
        r'(?:fix|update|refactor|create|add|remove|rename)\s+(?:the\s+)?([A-Z][A-Za-z0-9_]*)\s+(?:component|hook|context|provider|container|page|layout|store|slice|schema|middleware|api|endpoint)',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+(?:the\s+)?([A-Z][A-Za-z0-9_]*)',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+[\'"`]([A-Z][A-Za-z0-9_]*)[\'"`]',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+(?:the\s+)?([a-zA-Z0-9_]+)\s+(?:Zod\s+schema|schema|type|interface|enum|validator)',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+[\'"`]([a-zA-Z0-9_]+)[\'"`]\s+(?:Zod\s+schema|schema|type|interface|enum|validator)',
        # Next.js/Remix/SSR patterns
        r'(?:fix|update|refactor|create|add|remove|rename)\s+(getServerSideProps|getStaticProps|getInitialProps|getServerSession|getLoaderData|getActionData)',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+[\'"`](getServerSideProps|getStaticProps|getInitialProps|getServerSession|getLoaderData|getActionData)[\'"`]',
        # General function/variable patterns
        r'(?:fix|update|refactor|create|add|remove|rename)\s+(?:the\s+)?([a-zA-Z0-9_]+)\s+(?:function|variable|const|let|export|import|middleware|api|endpoint)',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+[\'"`]([a-zA-Z0-9_]+)[\'"`]\s+(?:function|variable|const|let|export|import|middleware|api|endpoint)',
        # Zod/validation
        r'(?:fix|update|refactor|create|add|remove|rename)\s+(?:the\s+)?([A-Za-z0-9_]+)\s+zod\s+schema',
        r'(?:fix|update|refactor|create|add|remove|rename)\s+[\'"`]([A-Za-z0-9_]+)[\'"`]\s+zod\s+schema',
    ]

    detected_targets = set()

    # --- Python patterns extraction ---
    for pattern in patterns:
        matches = re.findall(pattern, prompt, re.IGNORECASE)
        for match in matches:
            if len(match) > 2 and not _is_common_word(match):
                detected_targets.add(match)

    # --- JS/TS framework support (if enabled) ---
    js_ts_enabled = os.getenv("ENABLE_JS_TS_AUTO_DETECTION", "false").lower() == "true"
    js_ts_file = False
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in {".js", ".jsx", ".ts", ".tsx", ".astro"}:
            js_ts_file = True

    if js_ts_enabled and (js_ts_file or not file_path):
        # JS/TS prompt pattern extraction
        for pattern in js_ts_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if len(match) > 2 and not _is_common_word(match):
                    detected_targets.add(match)

        # Framework-specific detection using JSFrameworkDetector
        if JSFrameworkDetector and file_content:
            try:
                framework_targets = JSFrameworkDetector.detect_targets(prompt, file_content)
                for t in framework_targets:
                    if len(t) > 2 and not _is_common_word(t):
                        detected_targets.add(t)
            except Exception as e:
                logger.warning(f"JSFrameworkDetector failed: {e}")

    candidate_targets = list(detected_targets)

    # If file content provided, verify targets actually exist in the code
    if file_content and candidate_targets:
        verified_targets = []
        for target in candidate_targets:
            if js_ts_enabled and js_ts_file and JSFrameworkDetector:
                # Use JSFrameworkDetector for verification if available
                try:
                    if JSFrameworkDetector.target_exists_in_code(target, file_content):
                        verified_targets.append(target)
                        continue
                except Exception as e:
                    logger.warning(f"JSFrameworkDetector target_exists_in_code failed: {e}")
            # Fallback to Python-style verification
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
    Supports both Python and (optionally) JS/TS frameworks.

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

    # First pass: detect from prompt only (per file if JS/TS enabled)
    js_ts_enabled = os.getenv("ENABLE_JS_TS_AUTO_DETECTION", "false").lower() == "true"
    if file_paths and working_dir:
        all_verified_targets = set()
        for file_path in file_paths:
            full_path = os.path.join(working_dir, file_path)
            ext = os.path.splitext(file_path)[1].lower()
            js_ts_file = ext in {".js", ".jsx", ".ts", ".tsx", ".astro"}
            try:
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    # Use file_path for extension detection
                    targets = extract_targets_from_prompt(prompt, file_content, file_path=file_path)
                    for t in targets:
                        all_verified_targets.add(t)
            except Exception as e:
                logger.warning(f"Could not read file {full_path} for target verification: {e}")
                continue
        if all_verified_targets:
            logger.info(f"Auto-detection found verified targets: {list(all_verified_targets)}")
            return list(all_verified_targets)
        else:
            logger.info("Auto-detection found no verified targets in code files")
            return None

    # If no files, just use prompt (Python and optionally JS/TS patterns)
    targets = extract_targets_from_prompt(prompt)
    if targets:
        logger.info(f"Auto-detection found targets: {targets} (unverified)")
        return targets
    return None
