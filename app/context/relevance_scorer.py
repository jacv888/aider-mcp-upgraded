"""
Relevance Scorer for Context-Aware File Pruning

This module implements the scoring algorithm that determines which code blocks
are most relevant for a given modification target.
"""

from typing import List, Set, Dict
from .types import ContextBlock, ExtractionConfig


class RelevanceScorer:
    """
    Scores code blocks by relevance to target modifications
    
    Uses a sophisticated scoring system that considers:
    - Direct targets (highest score)
    - Function call relationships 
    - Shared state/variables
    - Type definitions
    - Import dependencies
    """
    
    # Relevance scoring weights
    RELEVANCE_SCORES = {
        'target_element': 10,      # Function being modified
        'direct_calls': 8,         # Functions this calls
        'reverse_calls': 7,        # Functions that call this
        'shared_state': 6,         # Shared variables/properties
        'type_definitions': 5,     # Related types/interfaces
        'imports': 4,              # Required imports
        'class_context': 3,        # Containing class structure
        'unrelated': 0             # Everything else (excluded)
    }
    
    def score_blocks(
        self, 
        elements: List[ContextBlock], 
        target_blocks: List[ContextBlock],
        dependency_graph: Dict[str, Set[str]],
        config: ExtractionConfig
    ) -> List[ContextBlock]:
        """Score all blocks by relevance to targets"""
        
        # Get target names for quick lookup
        target_names = {block.element_name for block in target_blocks}
        
        # Score each element
        scored_elements = []
        for element in elements:
            score = self._calculate_relevance_score(
                element, target_names, dependency_graph, elements
            )
            
            if score >= config.min_relevance_score:
                element.relevance_score = score
                scored_elements.append(element)
        
        return scored_elements
    
    def _calculate_relevance_score(
        self, 
        element: ContextBlock, 
        target_names: Set[str],
        dependency_graph: Dict[str, Set[str]],
        all_elements: List[ContextBlock]
    ) -> float:
        """Calculate relevance score for a single element"""
        
        # Direct target gets highest score
        if element.element_name in target_names:
            return self.RELEVANCE_SCORES['target_element']
        
        # Check if element calls any targets (direct calls)
        element_deps = dependency_graph.get(element.element_name, set())
        if element_deps.intersection(target_names):
            return self.RELEVANCE_SCORES['direct_calls']
        
        # Check if any targets call this element (reverse calls)
        for target_name in target_names:
            target_deps = dependency_graph.get(target_name, set())
            if element.element_name in target_deps:
                return self.RELEVANCE_SCORES['reverse_calls']
        
        # Check for shared state/variables
        if self._has_shared_state(element, target_names, all_elements):
            return self.RELEVANCE_SCORES['shared_state']
        
        # Type definitions and interfaces
        if element.element_type in ['interface', 'type', 'class'] and self._is_type_used(element, target_names, all_elements):
            return self.RELEVANCE_SCORES['type_definitions']
        
        # Essential imports
        if element.element_type == 'import' and self._is_essential_import(element, target_names, dependency_graph):
            return self.RELEVANCE_SCORES['imports']
        
        # Class context (if target is a method of this class)
        if element.element_type == 'class' and self._contains_target_methods(element, target_names, all_elements):
            return self.RELEVANCE_SCORES['class_context']
        
        return self.RELEVANCE_SCORES['unrelated']
    
    def _has_shared_state(self, element: ContextBlock, target_names: Set[str], all_elements: List[ContextBlock]) -> bool:
        """Check if element shares state/variables with targets"""
        # Simple heuristic: look for shared variable names in content
        element_vars = self._extract_variable_names(element.content)
        
        for target_name in target_names:
            # Find target elements
            target_elements = [e for e in all_elements if e.element_name == target_name]
            for target_element in target_elements:
                target_vars = self._extract_variable_names(target_element.content)
                if element_vars.intersection(target_vars):
                    return True
        
        return False
    
    def _extract_variable_names(self, content: str) -> Set[str]:
        """Extract variable names from code content (simplified)"""
        import re
        # Simple regex to find variable assignments
        var_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=')
        matches = var_pattern.findall(content)
        return set(matches)
    
    def _is_type_used(self, type_element: ContextBlock, target_names: Set[str], all_elements: List[ContextBlock]) -> bool:
        """Check if a type/interface is used by target functions"""
        type_name = type_element.element_name
        
        for target_name in target_names:
            target_elements = [e for e in all_elements if e.element_name == target_name]
            for target_element in target_elements:
                if type_name in target_element.content:
                    return True
        
        return False
    
    def _is_essential_import(self, import_element: ContextBlock, target_names: Set[str], dependency_graph: Dict[str, Set[str]]) -> bool:
        """Check if import is essential for target functions"""
        imported_names = import_element.dependencies
        
        # Check if any imported names are used by targets
        for target_name in target_names:
            target_deps = dependency_graph.get(target_name, set())
            if imported_names.intersection(target_deps):
                return True
        
        return False
    
    def _contains_target_methods(self, class_element: ContextBlock, target_names: Set[str], all_elements: List[ContextBlock]) -> bool:
        """Check if class contains any target methods"""
        class_start = class_element.start_line
        class_end = class_element.end_line
        
        for target_name in target_names:
            target_elements = [e for e in all_elements if e.element_name == target_name]
            for target_element in target_elements:
                if (target_element.element_type in ['method', 'function'] and
                    class_start <= target_element.start_line <= class_end):
                    return True
        
        return False
