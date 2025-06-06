"""
js_framework_detection.py

Modular JavaScript/TypeScript framework and pattern detection for auto-context extraction.

This module extends the auto-detection system to support:
    1. React components (function/const/class)
    2. Next.js API routes and page functions
    3. Zod schema definitions
    4. TypeScript interfaces and types
    5. Astro components
    6. SolidJS components
    7. General JS/TS function patterns

Usage Example:
    detector = JSFrameworkDetector(config=JSFrameworkDetectionConfig())
    matches = detector.detect_targets(file_content)
    for match in matches:
        print(match['type'], match['name'], match['span'])

Configuration:
    - Enable/disable specific patterns via JSFrameworkDetectionConfig.
    - Add new patterns by extending the PATTERNS list.

Author: [Your Name]
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Pattern

@dataclass
class JSFrameworkDetectionConfig:
    """
    Configuration for JS/TS framework detection.
    Set any field to False to disable that pattern.
    """
    react_function_components: bool = True
    react_class_components: bool = True
    nextjs_api_routes: bool = True
    nextjs_page_functions: bool = True
    zod_schemas: bool = True
    ts_interfaces: bool = True
    ts_types: bool = True
    astro_components: bool = True
    solidjs_components: bool = True
    general_functions: bool = True

@dataclass
class PatternSpec:
    name: str
    regex: str
    type: str
    example: str
    enabled_field: Optional[str] = None

class JSFrameworkDetector:
    """
    Detects JS/TS framework constructs and patterns in source code.

    Returns a list of dicts:
        {
            "type": <pattern type>,
            "name": <detected name>,
            "span": (start, end),
            "match": <re.Match object>
        }
    """

    PATTERNS: List[PatternSpec] = [
        # React function component (named export or default)
        PatternSpec(
            name="React Function Component",
            regex=r"(?:export\s+)?function\s+([A-Z][A-Za-z0-9_]*)\s*\(",
            type="react_function_component",
            example="export function MyComponent(props) { ... }",
            enabled_field="react_function_components"
        ),
        # React function component (const arrow)
        PatternSpec(
            name="React Const Arrow Component",
            regex=r"(?:export\s+)?const\s+([A-Z][A-Za-z0-9_]*)\s*=\s*\([^\)]*\)\s*=>",
            type="react_function_component",
            example="export const MyComponent = (props) => { ... }",
            enabled_field="react_function_components"
        ),
        # React class component
        PatternSpec(
            name="React Class Component",
            regex=r"(?:export\s+)?class\s+([A-Z][A-Za-z0-9_]*)\s+extends\s+React\.Component",
            type="react_class_component",
            example="class MyComponent extends React.Component { ... }",
            enabled_field="react_class_components"
        ),
        # Next.js API route (handler)
        PatternSpec(
            name="Next.js API Route Handler",
            regex=r"export\s+(?:default\s+)?async\s+function\s+([a-zA-Z0-9_]+)\s*\(",
            type="nextjs_api_route",
            example="export default async function handler(req, res) { ... }",
            enabled_field="nextjs_api_routes"
        ),
        # Next.js page function (getServerSideProps, getStaticProps, etc)
        PatternSpec(
            name="Next.js Page Function",
            regex=r"export\s+async\s+function\s+(getServerSideProps|getStaticProps|getStaticPaths)\s*\(",
            type="nextjs_page_function",
            example="export async function getServerSideProps(context) { ... }",
            enabled_field="nextjs_page_functions"
        ),
        # Zod schema definition
        PatternSpec(
            name="Zod Schema",
            regex=r"(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*z\.object\s*\(",
            type="zod_schema",
            example="const userSchema = z.object({ ... })",
            enabled_field="zod_schemas"
        ),
        # TypeScript interface
        PatternSpec(
            name="TypeScript Interface",
            regex=r"interface\s+([A-Za-z0-9_]+)\s*{",
            type="ts_interface",
            example="interface User { ... }",
            enabled_field="ts_interfaces"
        ),
        # TypeScript type alias
        PatternSpec(
            name="TypeScript Type Alias",
            regex=r"type\s+([A-Za-z0-9_]+)\s*=\s*",
            type="ts_type",
            example="type User = { ... }",
            enabled_field="ts_types"
        ),
        # Astro component (exported function or const, .astro file)
        PatternSpec(
            name="Astro Component",
            regex=r"---\s*[\s\S]*?(?:export\s+default\s+function\s+([A-Z][A-Za-z0-9_]*)|export\s+const\s+([A-Z][A-Za-z0-9_]*)\s*=)",
            type="astro_component",
            example="---\nexport default function MyAstroComponent() { ... }\n---",
            enabled_field="astro_components"
        ),
        # SolidJS component (function or const, JSX return)
        PatternSpec(
            name="SolidJS Component",
            regex=r"(?:export\s+)?function\s+([A-Z][A-Za-z0-9_]*)\s*\([^\)]*\)\s*{[^}]*return\s*<",
            type="solidjs_component",
            example="function MySolidComponent(props) { return <div /> }",
            enabled_field="solidjs_components"
        ),
        # General JS/TS function (named)
        PatternSpec(
            name="General Function",
            regex=r"(?:export\s+)?function\s+([a-zA-Z0-9_]+)\s*\(",
            type="function",
            example="function doSomething() { ... }",
            enabled_field="general_functions"
        ),
        # General JS/TS const arrow function
        PatternSpec(
            name="General Const Arrow Function",
            regex=r"(?:export\s+)?const\s+([a-zA-Z0-9_]+)\s*=\s*\([^\)]*\)\s*=>",
            type="function",
            example="const doSomething = () => { ... }",
            enabled_field="general_functions"
        ),
    ]

    def __init__(self, config: Optional[JSFrameworkDetectionConfig] = None):
        """
        Initialize the detector with a configuration.
        """
        self.config = config or JSFrameworkDetectionConfig()
        self.compiled_patterns: List[Dict[str, Any]] = []
        self._compile_patterns()

    def _compile_patterns(self):
        """
        Compile regex patterns based on config.
        """
        self.compiled_patterns.clear()
        for spec in self.PATTERNS:
            enabled = True
            if spec.enabled_field:
                enabled = getattr(self.config, spec.enabled_field, True)
            if enabled:
                self.compiled_patterns.append({
                    "spec": spec,
                    "regex": re.compile(spec.regex, re.MULTILINE | re.DOTALL)
                })

    def detect_targets(self, file_content: str) -> List[Dict[str, Any]]:
        """
        Detect all matching patterns in the given file content.

        Returns:
            List of dicts with keys: type, name, span, match, pattern_name
        """
        results = []
        for pat in self.compiled_patterns:
            for match in pat["regex"].finditer(file_content):
                # Some patterns have multiple capture groups, pick the first non-None
                name = None
                if match.lastindex:
                    for i in range(1, match.lastindex + 1):
                        name = match.group(i)
                        if name:
                            break
                else:
                    name = match.group(1) if match.groups() else None
                results.append({
                    "type": pat["spec"].type,
                    "name": name,
                    "span": match.span(),
                    "match": match,
                    "pattern_name": pat["spec"].name
                })
        return results

    def set_config(self, **kwargs):
        """
        Update config and recompile patterns.
        Example: detector.set_config(react_function_components=False)
        """
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
        self._compile_patterns()

# Example usage (for documentation/testing)
if __name__ == "__main__":
    example_code = '''
    // React function component
    export function MyComponent(props) { return <div /> }
    // React class component
    class MyClassComponent extends React.Component { render() { return <div /> } }
    // Next.js API route
    export default async function handler(req, res) { res.status(200).json({}) }
    // Zod schema
    const userSchema = z.object({ name: z.string() })
    // TypeScript interface
    interface User { id: number }
    // TypeScript type
    type User = { id: number }
    // Astro component
    --- 
    export default function MyAstroComponent() { return <div /> }
    ---
    // SolidJS component
    function MySolidComponent(props) { return <div /> }
    // General function
    function doSomething() { return 42 }
    // General arrow function
    const doSomethingElse = () => { return 43 }
    '''
    detector = JSFrameworkDetector()
    matches = detector.detect_targets(example_code)
    for m in matches:
        print(f"{m['pattern_name']}: {m['name']} at {m['span']}")
