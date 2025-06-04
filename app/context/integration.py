"""
Integration layer for Context-Aware File Pruning with Aider-MCP

This module integrates the context-aware pruning system with Desktop Commander
and Aider-MCP, providing smart context extraction for AI coding tasks.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .context_manager import ContextManager, ExtractionConfig, extract_context
from .types import ContextBlock


class ContextAwareFileManager:
    """
    Integrates Context-Aware Pruning with Desktop Commander operations
    
    Automatically extracts relevant context when reading files for AI tasks,
    reducing token usage while maintaining accuracy.
    """
    
    def __init__(self, default_max_tokens: int = 4000):
        self.context_manager = ContextManager()
        self.default_max_tokens = default_max_tokens
        self.logger = logging.getLogger(__name__)
        
        # Cache for parsed files to avoid re-parsing
        self._parse_cache = {}
    
    def read_with_context(
        self, 
        file_path: str, 
        target_element: Optional[str] = None,
        max_tokens: Optional[int] = None,
        context_config: Optional[ExtractionConfig] = None
    ) -> Dict[str, Any]:
        """
        Read file with intelligent context extraction
        
        Args:
            file_path: Path to source file
            target_element: Specific function/class to focus on
            max_tokens: Token budget for extraction
            context_config: Advanced configuration
            
        Returns:
            Dict with 'content', 'stats', 'metadata'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # If no target specified, return full file
        if not target_element:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'content': content,
                'stats': {'reduction_ratio': 1.0, 'token_savings': 0},
                'metadata': {'extraction_used': False, 'file_path': file_path}
            }
        
        # Use context extraction
        config = context_config or ExtractionConfig(
            max_tokens=max_tokens or self.default_max_tokens
        )
        
        result = self.context_manager.extract_relevant_context(
            file_path, target_element, config
        )
        
        return {
            'content': result['focused_context'],
            'stats': result['extraction_stats'],
            'metadata': {
                'extraction_used': True,
                'target_elements': result['target_elements'],
                'language': result['language'],
                'dependency_map': result['dependency_map'],
                'suggested_edits': result['suggested_edits'],
                'file_path': file_path
            }
        }
    
    def prepare_context_for_aider(
        self, 
        files_and_targets: List[Dict[str, str]], 
        max_total_tokens: int = 8000
    ) -> Dict[str, Any]:
        """
        Prepare context for multiple files for Aider tasks
        
        Args:
            files_and_targets: List of {'file_path': str, 'target': str}
            max_total_tokens: Total token budget across all files
            
        Returns:
            Combined context optimized for Aider
        """
        if not files_and_targets:
            return {'combined_context': '', 'stats': {}, 'file_summaries': []}
        
        # Distribute token budget across files
        tokens_per_file = max_total_tokens // len(files_and_targets)
        
        combined_context_parts = []
        file_summaries = []
        total_savings = 0
        total_original_tokens = 0
        
        for file_info in files_and_targets:
            file_path = file_info['file_path']
            target = file_info.get('target')
            
            # Extract context for this file
            context_result = self.read_with_context(
                file_path, target, tokens_per_file
            )
            
            # Add file section to combined context
            file_name = Path(file_path).name
            combined_context_parts.append(f"# === {file_name} ===")
            
            if context_result['metadata']['extraction_used']:
                targets = context_result['metadata']['target_elements']
                combined_context_parts.append(f"# Focused on: {', '.join(targets)}")
                combined_context_parts.append(f"# Token reduction: {context_result['stats']['reduction_ratio']:.2%}")
            
            combined_context_parts.append(context_result['content'])
            combined_context_parts.append("")  # Separator
            
            # Collect stats
            stats = context_result['stats']
            total_savings += stats.get('token_savings', 0)
            total_original_tokens += stats.get('original_tokens', 0)
            
            file_summaries.append({
                'file_path': file_path,
                'target': target,
                'extraction_used': context_result['metadata']['extraction_used'],
                'token_reduction': stats.get('reduction_ratio', 1.0),
                'focused_tokens': stats.get('focused_tokens', 0)
            })
        
        combined_context = '\n'.join(combined_context_parts)
        
        return {
            'combined_context': combined_context,
            'stats': {
                'total_files': len(files_and_targets),
                'total_token_savings': total_savings,
                'total_original_tokens': total_original_tokens,
                'combined_tokens': len(combined_context.split()),
                'overall_reduction': total_savings / total_original_tokens if total_original_tokens > 0 else 0
            },
            'file_summaries': file_summaries
        }

class SmartEditManager:
    """
    Intelligent edit operations using context awareness
    
    Automatically identifies the best edit locations and provides focused
    context for AI models to make accurate modifications.
    """
    
    def __init__(self, file_manager: ContextAwareFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(__name__)
    
    def prepare_for_edit(
        self, 
        file_path: str, 
        edit_description: str, 
        target_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare a file for editing with optimal context
        
        Args:
            file_path: File to be edited
            edit_description: Description of the change needed
            target_hint: Hint about target function/class (optional)
            
        Returns:
            Edit preparation with focused context and suggestions
        """
        
        # If no target hint, try to extract it from description
        if not target_hint:
            target_hint = self._extract_target_from_description(edit_description)
        
        # Get focused context
        context_result = self.file_manager.read_with_context(
            file_path, target_hint, max_tokens=3000
        )
        
        # Prepare edit guidance
        edit_guidance = self._generate_edit_guidance(
            context_result, edit_description, target_hint
        )
        
        return {
            'focused_context': context_result['content'],
            'edit_guidance': edit_guidance,
            'suggested_locations': context_result['metadata'].get('suggested_edits', []),
            'dependencies': context_result['metadata'].get('dependency_map', {}),
            'stats': context_result['stats']
        }
    
    def _extract_target_from_description(self, description: str) -> Optional[str]:
        """Extract likely target function/class from edit description"""
        import re
        
        # Look for function/class names in common patterns
        patterns = [
            r'modify\s+(\w+)',
            r'update\s+(\w+)',
            r'fix\s+(\w+)',
            r'change\s+(\w+)',
            r'in\s+(\w+)\s+function',
            r'(\w+)\s+method',
            r'function\s+(\w+)',
            r'class\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_edit_guidance(
        self, 
        context_result: Dict[str, Any], 
        edit_description: str,
        target_hint: Optional[str]
    ) -> Dict[str, str]:
        """Generate guidance for making the edit"""
        
        guidance = {
            'description': edit_description,
            'context_quality': 'good' if context_result['stats'].get('reduction_ratio', 1.0) < 0.8 else 'full_file',
            'recommendations': []
        }
        
        # Add recommendations based on context
        if context_result['metadata'].get('extraction_used'):
            targets = context_result['metadata']['target_elements']
            if targets:
                guidance['recommendations'].append(f"Focus on: {', '.join(targets)}")
        
        dependencies = context_result['metadata'].get('dependency_map', {})
        if dependencies:
            guidance['recommendations'].append(f"Consider dependencies: {dependencies}")
        
        return guidance


# Integration helper functions
def smart_read_file(file_path: str, target_element: str = None, max_tokens: int = 4000) -> str:
    """
    Smart file reading with automatic context extraction
    
    This is a drop-in replacement for regular file reading that automatically
    applies context-aware pruning when a target is specified.
    """
    manager = ContextAwareFileManager(default_max_tokens=max_tokens)
    result = manager.read_with_context(file_path, target_element, max_tokens)
    return result['content']


def prepare_multi_file_context(file_targets: List[tuple], max_tokens: int = 8000) -> str:
    """
    Prepare context from multiple files for AI tasks
    
    Args:
        file_targets: List of (file_path, target_element) tuples
        max_tokens: Total token budget
        
    Returns:
        Combined optimized context
    """
    manager = ContextAwareFileManager()
    
    files_and_targets = [
        {'file_path': file_path, 'target': target}
        for file_path, target in file_targets
    ]
    
    result = manager.prepare_context_for_aider(files_and_targets, max_tokens)
    return result['combined_context']
