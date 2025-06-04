"""
Language-specific parsers for Context-Aware File Pruning

This module provides AST parsers for different programming languages
to extract code elements and their dependencies.
"""

import ast
import re
from abc import ABC, abstractmethod
from typing import List, Set, Optional, Dict, Any
from dataclasses import dataclass

from .types import ContextBlock


class LanguageParser(ABC):
    """Abstract base class for language-specific parsers"""
    
    @abstractmethod
    def parse(self, source_code: str) -> Any:
        """Parse source code into AST"""
        pass
    
    @abstractmethod
    def extract_elements(self, ast_tree: Any, source_code: str) -> List[ContextBlock]:
        """Extract code elements from AST"""
        pass


class PythonParser(LanguageParser):
    """Parser for Python source code using AST module"""
    
    def parse(self, source_code: str) -> ast.AST:
        """Parse Python source code into AST"""
        return ast.parse(source_code)
    
    def extract_elements(self, ast_tree: ast.AST, source_code: str) -> List[ContextBlock]:
        """Extract Python code elements from AST"""
        elements = []
        source_lines = source_code.split('\n')
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                elements.append(self._extract_function(node, source_lines, source_code))
            elif isinstance(node, ast.ClassDef):
                elements.append(self._extract_class(node, source_lines, source_code))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                elements.append(self._extract_import(node, source_lines))
            elif isinstance(node, ast.Assign):
                if self._is_module_level_assignment(node, ast_tree):
                    elements.append(self._extract_variable(node, source_lines))
        
        return [e for e in elements if e is not None]
    
    def _extract_function(self, node: ast.FunctionDef, source_lines: List[str], source_code: str) -> ContextBlock:
        """Extract function definition"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        # Get function content
        content_lines = source_lines[start_line-1:end_line]
        content = '\n'.join(content_lines)
        
        # Extract dependencies (function calls)
        dependencies = self._extract_function_dependencies(node)
        
        return ContextBlock(
            content=content,
            start_line=start_line,
            end_line=end_line,
            element_type='function',
            element_name=node.name,
            relevance_score=0.0,  # Will be scored later
            dependencies=dependencies,
            token_count=len(content.split())
        )
    
    def _extract_class(self, node: ast.ClassDef, source_lines: List[str], source_code: str) -> ContextBlock:
        """Extract class definition"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        content_lines = source_lines[start_line-1:end_line]
        content = '\n'.join(content_lines)
        
        # Extract class dependencies (inheritance, method calls)
        dependencies = set()
        for base in node.bases:
            if isinstance(base, ast.Name):
                dependencies.add(base.id)
        
        return ContextBlock(
            content=content,
            start_line=start_line,
            end_line=end_line,
            element_type='class',
            element_name=node.name,
            relevance_score=0.0,
            dependencies=dependencies,
            token_count=len(content.split())
        )
    
    def _extract_import(self, node, source_lines: List[str]) -> ContextBlock:
        """Extract import statements"""
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line) or start_line
        
        content_lines = source_lines[start_line-1:end_line]
        content = '\n'.join(content_lines)
        
        # Extract imported names
        dependencies = set()
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                dependencies.add(node.module)
            for alias in node.names:
                dependencies.add(alias.name)
        
        return ContextBlock(
            content=content,
            start_line=start_line,
            end_line=end_line,
            element_type='import',
            element_name=f"import_{start_line}",
            relevance_score=0.0,
            dependencies=dependencies,
            token_count=len(content.split())
        )
    
    def _extract_variable(self, node: ast.Assign, source_lines: List[str]) -> Optional[ContextBlock]:
        """Extract module-level variable assignments"""
        if not node.targets:
            return None
            
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line) or start_line
        
        content_lines = source_lines[start_line-1:end_line]
        content = '\n'.join(content_lines)
        
        # Get variable name
        target = node.targets[0]
        if isinstance(target, ast.Name):
            var_name = target.id
        else:
            var_name = f"variable_{start_line}"
        
        return ContextBlock(
            content=content,
            start_line=start_line,
            end_line=end_line,
            element_type='variable',
            element_name=var_name,
            relevance_score=0.0,
            dependencies=set(),
            token_count=len(content.split())
        )
    
    def _extract_function_dependencies(self, node: ast.FunctionDef) -> Set[str]:
        """Extract dependencies (function calls) from a function"""
        dependencies = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # For method calls like obj.method()
                    if isinstance(child.func.value, ast.Name):
                        dependencies.add(child.func.value.id)
        
        return dependencies
    
    def _is_module_level_assignment(self, node: ast.Assign, ast_tree: ast.AST) -> bool:
        """Check if assignment is at module level"""
        # Simple heuristic: check if the assignment is a direct child of Module
        for child in ast.iter_child_nodes(ast_tree):
            if child == node:
                return True
        return False


class TypeScriptParser(LanguageParser):
    """Parser for TypeScript/JavaScript using regex patterns"""
    
    def parse(self, source_code: str) -> Dict[str, Any]:
        """Parse TypeScript source (using regex since no AST available)"""
        return {'source_code': source_code}
    
    def extract_elements(self, ast_tree: Dict[str, Any], source_code: str) -> List[ContextBlock]:
        """Extract TypeScript elements using regex patterns"""
        elements = []
        source_lines = source_code.split('\n')
        
        # Extract functions
        elements.extend(self._extract_ts_functions(source_lines))
        
        # Extract classes
        elements.extend(self._extract_ts_classes(source_lines))
        
        # Extract imports
        elements.extend(self._extract_ts_imports(source_lines))
        
        # Extract interfaces/types
        elements.extend(self._extract_ts_interfaces(source_lines))
        
        return elements
    
    def _extract_ts_functions(self, source_lines: List[str]) -> List[ContextBlock]:
        """Extract TypeScript functions using regex"""
        elements = []
        
        # Pattern for function declarations
        func_pattern = re.compile(r'^\s*(export\s+)?(async\s+)?function\s+(\w+)', re.MULTILINE)
        arrow_pattern = re.compile(r'^\s*(export\s+)?const\s+(\w+)\s*=\s*.*=>', re.MULTILINE)
        
        source_code = '\n'.join(source_lines)
        
        # Regular function declarations
        for match in func_pattern.finditer(source_code):
            func_name = match.group(3)
            start_line = source_code[:match.start()].count('\n') + 1
            
            # Find function end (simplified - look for closing brace)
            end_line = self._find_function_end(source_lines, start_line)
            
            content = '\n'.join(source_lines[start_line-1:end_line])
            
            elements.append(ContextBlock(
                content=content,
                start_line=start_line,
                end_line=end_line,
                element_type='function',
                element_name=func_name,
                relevance_score=0.0,
                dependencies=self._extract_ts_dependencies(content),
                token_count=len(content.split())
            ))
        
        return elements
    
    def _extract_ts_classes(self, source_lines: List[str]) -> List[ContextBlock]:
        """Extract TypeScript classes"""
        elements = []
        source_code = '\n'.join(source_lines)
        
        class_pattern = re.compile(r'^\s*(export\s+)?class\s+(\w+)', re.MULTILINE)
        
        for match in class_pattern.finditer(source_code):
            class_name = match.group(2)
            start_line = source_code[:match.start()].count('\n') + 1
            end_line = self._find_class_end(source_lines, start_line)
            
            content = '\n'.join(source_lines[start_line-1:end_line])
            
            elements.append(ContextBlock(
                content=content,
                start_line=start_line,
                end_line=end_line,
                element_type='class',
                element_name=class_name,
                relevance_score=0.0,
                dependencies=set(),
                token_count=len(content.split())
            ))
        
        return elements
    
    def _extract_ts_imports(self, source_lines: List[str]) -> List[ContextBlock]:
        """Extract TypeScript imports"""
        elements = []
        
        for i, line in enumerate(source_lines):
            if line.strip().startswith('import '):
                elements.append(ContextBlock(
                    content=line,
                    start_line=i + 1,
                    end_line=i + 1,
                    element_type='import',
                    element_name=f"import_{i+1}",
                    relevance_score=0.0,
                    dependencies=self._extract_import_names(line),
                    token_count=len(line.split())
                ))
        
        return elements
    
    def _extract_ts_interfaces(self, source_lines: List[str]) -> List[ContextBlock]:
        """Extract TypeScript interfaces and types"""
        elements = []
        source_code = '\n'.join(source_lines)
        
        interface_pattern = re.compile(r'^\s*(export\s+)?interface\s+(\w+)', re.MULTILINE)
        type_pattern = re.compile(r'^\s*(export\s+)?type\s+(\w+)', re.MULTILINE)
        
        for pattern, element_type in [(interface_pattern, 'interface'), (type_pattern, 'type')]:
            for match in pattern.finditer(source_code):
                name = match.group(2)
                start_line = source_code[:match.start()].count('\n') + 1
                end_line = self._find_interface_end(source_lines, start_line)
                
                content = '\n'.join(source_lines[start_line-1:end_line])
                
                elements.append(ContextBlock(
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                    element_type=element_type,
                    element_name=name,
                    relevance_score=0.0,
                    dependencies=set(),
                    token_count=len(content.split())
                ))
        
        return elements
    
    def _find_function_end(self, source_lines: List[str], start_line: int) -> int:
        """Find the end of a function (simplified brace matching)"""
        brace_count = 0
        found_opening = False
        
        for i in range(start_line - 1, len(source_lines)):
            line = source_lines[i]
            
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening = True
                elif char == '}':
                    brace_count -= 1
                    
                    if found_opening and brace_count == 0:
                        return i + 1
        
        return min(start_line + 10, len(source_lines))  # Fallback
    
    def _find_class_end(self, source_lines: List[str], start_line: int) -> int:
        """Find the end of a class"""
        return self._find_function_end(source_lines, start_line)
    
    def _find_interface_end(self, source_lines: List[str], start_line: int) -> int:
        """Find the end of an interface"""
        return self._find_function_end(source_lines, start_line)
    
    def _extract_import_names(self, import_line: str) -> Set[str]:
        """Extract imported names from import statement"""
        names = set()
        
        # Simple regex patterns for different import styles
        patterns = [
            r'import\s+(\w+)',  # import foo
            r'import\s+\{([^}]+)\}',  # import { foo, bar }
            r'from\s+[\'"]([^\'"]+)[\'"]',  # from "module"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, import_line)
            for match in matches:
                if ',' in match:
                    names.update(name.strip() for name in match.split(','))
                else:
                    names.add(match.strip())
        
        return names
    
    def _extract_ts_dependencies(self, content: str) -> Set[str]:
        """Extract function/variable dependencies from TypeScript content"""
        dependencies = set()
        
        # Function calls
        call_pattern = re.compile(r'(\w+)\s*\(')
        for match in call_pattern.finditer(content):
            dependencies.add(match.group(1))
        
        # Variable references (simplified)
        var_pattern = re.compile(r'\b([a-zA-Z_]\w*)\b')
        for match in var_pattern.finditer(content):
            name = match.group(1)
            # Filter out keywords
            if name not in ['const', 'let', 'var', 'function', 'if', 'else', 'for', 'while', 'return']:
                dependencies.add(name)
        
        return dependencies


class JavaScriptParser(TypeScriptParser):
    """Parser for JavaScript (inherits from TypeScript parser)"""
    pass


# Parser factory function
def get_parser_for_language(language: str) -> Optional[LanguageParser]:
    """Get appropriate parser for the given language"""
    parsers = {
        'python': PythonParser,
        'typescript': TypeScriptParser,
        'javascript': JavaScriptParser,
    }
    
    parser_class = parsers.get(language.lower())
    return parser_class() if parser_class else None
