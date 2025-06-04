"""
Data structures for Context-Aware File Pruning

This module defines the core data structures used throughout the context system.
"""

from dataclasses import dataclass
from typing import Set, Optional


@dataclass
class ContextBlock:
    """Represents a block of code with relevance scoring"""
    content: str
    start_line: int
    end_line: int
    element_type: str  # 'function', 'class', 'import', etc.
    element_name: str
    relevance_score: float
    dependencies: Set[str]
    token_count: int


@dataclass
class ExtractionConfig:
    """Configuration for context extraction"""
    max_tokens: int = 4000
    min_relevance_score: float = 3.0
    include_imports: bool = True
    include_type_hints: bool = True
    preserve_syntax: bool = True
    language: Optional[str] = None
