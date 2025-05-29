#!/usr/bin/env python3
"""
GitHub Repository Verification Script
Verifies that all repository setup is correct before publication.
"""

import os
import sys
import re
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_github_links(file_path):
    """Check if GitHub links point to jacv888 repository."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for old repository links
        old_links = re.findall(r'github\.com/eiliyaabedini', content)
        if old_links:
            print(f"❌ {file_path}: Still contains old repository links")
            return False
        
        # Check for new repository links
        new_links = re.findall(r'github\.com/jacv888', content)
        if new_links:
            print(f"✅ {file_path}: Contains {len(new_links)} correct jacv888 links")
            return True
        
        print(f"⚠️  {file_path}: No GitHub links found")
        return True
        
    except Exception as e:
        print(f"❌ Error checking {file_path}: {e}")
        return False

def check_api_key_security():
    """Check if API keys are properly secured."""
    env_file = '.env'
    if not Path(env_file).exists():
        print("⚠️  .env file not found - this is OK if using .env.example")
        return True
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check for exposed API keys (more precise patterns)
        exposed_patterns = [
            (r'sk-[a-zA-Z0-9]{40,}', 'OpenAI API key'),  # Real OpenAI keys are longer
            (r'AIza[a-zA-Z0-9_-]{35}', 'Google API key'),
            (r'sk-ant-api03-[a-zA-Z0-9_-]{40,}', 'Anthropic API key'),  # Real Anthropic pattern
        ]
        
        has_real_keys = False
        for pattern, key_type in exposed_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"❌ .env file contains real {key_type}: {len(matches)} found")
                has_real_keys = True
        
        if has_real_keys:
            return False
        
        # Check for placeholder values
        if 'your_' in content and '_key_here' in content:
            print("✅ .env file contains secure placeholders")
            return True
        
        print("⚠️  .env file doesn't contain expected placeholders")
        return True
        
    except Exception as e:
        print(f"❌ Error checking .env: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 GitHub Repository Verification")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check essential repository files
    print("\n📁 Repository Files:")
    essential_files = [
        ("README.md", "Main documentation"),
        ("LICENSE", "License file"),
        ("CONTRIBUTING.md", "Contribution guidelines"),
        ("CHANGELOG.md", "Version history"),
        (".env.example", "Secure configuration template"),
        (".gitignore", "Git ignore rules"),
    ]
    
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check GitHub integration files
    print("\n🤖 GitHub Integration:")
    github_files = [
        (".github/workflows/test.yml", "CI/CD pipeline"),
        (".github/ISSUE_TEMPLATE/bug_report.md", "Bug report template"),
        (".github/ISSUE_TEMPLATE/feature_request.md", "Feature request template"),
        (".github/pull_request_template.md", "Pull request template"),
    ]
    
    for file_path, description in github_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check core application files
    print("\n🚀 Application Files:")
    app_files = [
        ("aider_mcp.py", "Enhanced MCP server"),
        ("strategic_model_selector.py", "Strategic model selection"),
        ("aider_mcp_resilience.py", "Resilience components"),
        ("resilience_config.py", "Configuration management"),
        ("install_resilience.py", "Installation script"),
        ("requirements.txt", "Python dependencies"),
    ]
    
    for file_path, description in app_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check GitHub links
    print("\n🔗 GitHub Links:")
    files_to_check = ["README.md", "CONTRIBUTING.md"]
    for file_path in files_to_check:
        if Path(file_path).exists():
            if not check_github_links(file_path):
                all_checks_passed = False
    
    # Check API key security
    print("\n🔐 Security:")
    if not check_api_key_security():
        all_checks_passed = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Repository is ready for GitHub publication")
        print("\n🚀 Next steps:")
        print("1. Create repository at https://github.com/jacv888/aider-mcp")
        print("2. git remote add origin https://github.com/jacv888/aider-mcp.git")
        print("3. git add . && git commit -m 'Initial release'")
        print("4. git push -u origin main")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("Please fix the issues above before publishing to GitHub")
        sys.exit(1)

if __name__ == "__main__":
    main()
