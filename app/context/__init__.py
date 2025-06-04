"""
Context-Aware File Pruning System

This module provides intelligent context extraction for AI coding tasks,
reducing token usage by 2-3x while maintaining code accuracy.
"""

from .context_manager import ContextManager, extract_context
from .language_parsers import PythonParser, TypeScriptParser, JavaScriptParser
from .relevance_scorer import RelevanceScorer
from .context_extractor import ContextExtractor
from .types import ContextBlock, ExtractionConfig

__all__ = [
    'ContextManager',
    'extract_context',
    'PythonParser',
    'TypeScriptParser', 
    'JavaScriptParser',
    'RelevanceScorer',
    'ContextExtractor',
    'ContextBlock',
    'ExtractionConfig'
]
