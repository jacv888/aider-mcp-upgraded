#!/usr/bin/env python3
"""
Bootstrap Template Validator
Ensures templates contain real data, not placeholders
"""

import re
import sys

def validate_template(template_text: str) -> dict:
    """Validate that template contains real data, not placeholders"""
    
    issues = []
    warnings = []
    
    # Check for placeholder patterns
    placeholder_patterns = [
        r'\[X\]',  # [X] placeholders
        r'\[.*\]',  # Any bracket placeholders
        r'Unknown',  # Unknown values
        r'\$0\.00',  # Zero costs
        r'0 sessions',  # Zero sessions
        r'placeholder',  # Literal placeholder text
        r'PLACEHOLDER',  # Uppercase placeholder
        r'TBD',  # To be determined
        r'N/A'   # Not available
    ]
    
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, template_text, re.IGNORECASE)
        if matches:
            issues.append(f"Found placeholder pattern '{pattern}': {matches}")
    
    # Check for required real data sections
    required_data = [
        (r'📊 Backed up: (\d+) sessions', "session count"),
        (r'💰 Costs: \$(\d+\.\d+) today', "daily cost"),
        (r'🎯 Target elements identified: ([\d,]+)', "target elements"),
        (r'📂 Found: .*/([^/]+\.md)', "context file")
    ]
    
    for pattern, description in required_data:
        if not re.search(pattern, template_text):
            issues.append(f"Missing required {description} data")
    
    # Check for realistic values
    cost_matches = re.findall(r'\$(\d+\.\d+)', template_text)
    if cost_matches:
        costs = [float(cost) for cost in cost_matches]
        if all(cost == 0.0 for cost in costs):
            warnings.append("All costs are $0.00 - verify this is accurate")
    
    session_matches = re.findall(r'(\d+) sessions', template_text)
    if session_matches:
        sessions = [int(session) for session in session_matches]
        if all(session == 0 for session in sessions):
            warnings.append("All session counts are 0 - verify this is accurate")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "score": max(0, 100 - len(issues) * 20 - len(warnings) * 5)
    }

def main():
    """Validate a bootstrap template"""
    
    if len(sys.argv) != 2:
        print("Usage: python3 validate_template.py <template_file>")
        sys.exit(1)
    
    template_file = sys.argv[1]
    
    try:
        with open(template_file, 'r') as f:
            template_text = f.read()
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_file}")
        sys.exit(1)
    
    validation = validate_template(template_text)
    
    print("🔍 Bootstrap Template Validation Report")
    print("=" * 50)
    print(f"📊 Validation Score: {validation['score']}/100")
    
    if validation["is_valid"]:
        print("✅ Template is valid - contains real data")
    else:
        print("❌ Template validation failed")
        
    if validation["issues"]:
        print("\n🚨 Issues Found:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    if validation["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    
    if not validation["issues"] and not validation["warnings"]:
        print("🎉 Perfect template - no issues found!")
    
    sys.exit(0 if validation["is_valid"] else 1)

if __name__ == "__main__":
    main()
