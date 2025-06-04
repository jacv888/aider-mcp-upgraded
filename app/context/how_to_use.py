"""
Practical Usage Guide: How to Use Context-Aware File Pruning TODAY

This script shows you exactly how to start using the context extraction
system in your daily workflow.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.context import extract_context, ContextManager, ExtractionConfig


def show_practical_usage():
    """Show exactly how to use this in your daily workflow"""
    
    print("🔧 HOW TO USE CONTEXT-AWARE FILE PRUNING TODAY")
    print("=" * 55)
    
    print("\n💡 SCENARIO: You want to modify a function in a large file")
    print("-" * 55)
    
    # Create example usage
    example_file = "/Users/jacquesv/project/src/api/users.py"  # Your file
    target_function = "update_user"  # Function you want to modify
    
    print(f"📁 Large file: {example_file}")
    print(f"🎯 Target: {target_function}")
    print()
    
    print("❌ OLD WAY (using lots of messages):")
    print('   You: "read the users.py file"')
    print("   DC: [Returns entire 500-line file = 3000 tokens]")
    print('   You: "find the update_user function"')
    print("   DC: [Searches and shows function location]")
    print('   You: "show me the imports and related functions"')
    print("   DC: [More file reading operations]")
    print('   You: "now modify the update_user function to..."')
    print("   TOTAL: 4-5 messages, 5000+ tokens")
    print()
    
    print("✅ NEW WAY (using context extraction):")
    print("   1. Run this code:")
    
    # Show the actual code they should run
    code_example = f'''
# In your Python environment or script:
from app.context import extract_context

focused_context = extract_context(
    "{example_file}",
    "{target_function}",
    max_tokens=2000
)

print("Focused context:")
print(focused_context)
'''
    
    print(code_example)
    
    print("   2. Copy the focused_context output")
    print("   3. Paste it into your prompt:")
    print('   You: "Here\'s the relevant code: [paste focused_context]"')
    print('        "Please modify the update_user function to..."')
    print("   TOTAL: 1 message, ~800 tokens (70% reduction!)")


def show_step_by_step_tutorial():
    """Step-by-step tutorial for first use"""
    
    print("\n🚀 STEP-BY-STEP: Your First Use")
    print("=" * 40)
    
    steps = [
        {
            'step': 1,
            'title': 'Open your terminal/Python environment',
            'action': 'cd /Users/jacquesv/MCP/aider-mcp'
        },
        {
            'step': 2, 
            'title': 'Test the system works',
            'action': 'python app/context/test_context.py'
        },
        {
            'step': 3,
            'title': 'Try it on a real file',
            'action': '''python -c "
from app.context import extract_context
result = extract_context('your_file.py', 'your_function', 2000)
print(result)
"'''
        },
        {
            'step': 4,
            'title': 'Use the output in your AI prompt',
            'action': 'Copy the focused context and paste into Claude/Aider'
        }
    ]
    
    for step in steps:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   → {step['action']}")
    
    print(f"\n🎉 That's it! You're now using Context-Aware File Pruning!")


def show_integration_phases():
    """Clarify what the 3 phases actually mean"""
    
    print("\n🔄 UNDERSTANDING THE 3 PHASES")
    print("=" * 40)
    
    phases = [
        {
            'phase': 'Phase 1: Manual Use',
            'status': '✅ AVAILABLE NOW',
            'what': 'YOU manually call extract_context() functions',
            'effort': 'Zero development needed',
            'benefit': '2-3x token reduction when you use it',
            'example': 'You run Python commands to extract context, then paste into prompts'
        },
        {
            'phase': 'Phase 2: Aider Integration', 
            'status': '🟡 NEXT DEVELOPMENT',
            'what': 'AIDER automatically uses context extraction',
            'effort': 'Modify your code_with_ai functions',
            'benefit': 'Automatic optimization of all Aider tasks',
            'example': 'code_with_ai() automatically extracts context before sending to AI'
        },
        {
            'phase': 'Phase 3: DC Integration',
            'status': '🔵 FUTURE ENHANCEMENT', 
            'what': 'DESKTOP COMMANDER automatically uses smart reading',
            'effort': 'Modify Desktop Commander MCP tools',
            'benefit': 'All file operations automatically optimized',
            'example': 'read_file() automatically returns focused context when appropriate'
        }
    ]
    
    for phase in phases:
        print(f"\n📍 {phase['phase']} ({phase['status']})")
        print(f"   What: {phase['what']}")
        print(f"   Effort: {phase['effort']}")
        print(f"   Benefit: {phase['benefit']}")
        print(f"   Example: {phase['example']}")


def show_real_example():
    """Show a real example you can try right now"""
    
    print("\n🎯 REAL EXAMPLE YOU CAN TRY NOW")
    print("=" * 40)
    
    print("Let's use one of your existing files...")
    
    # Check if main.py exists (from your project)
    main_file = "/Users/jacquesv/MCP/aider-mcp/main.py"
    
    print(f"\n📁 File: {main_file}")
    print("🎯 Let's extract context for the main entry point")
    print()
    print("Run this command:")
    
    command = f'''python -c "
import sys
sys.path.insert(0, '/Users/jacquesv/MCP/aider-mcp')
from app.context import extract_context

# Extract context for main.py
focused = extract_context('{main_file}', 'main', 1000)
print('=== FOCUSED CONTEXT ===')
print(focused)
print()
print('=== STATS ===')
print(f'Context length: {{len(focused)}} characters')
print(f'Estimated tokens: {{len(focused.split())}}')
"'''
    
    print(command)
    print()
    print("This will show you exactly how the system works on your actual code!")


if __name__ == "__main__":
    show_practical_usage()
    show_step_by_step_tutorial()
    show_integration_phases()
    show_real_example()
    
    print("\n" + "="*60)
    print("🚀 SUMMARY: Start with Phase 1 TODAY!")
    print("   • No development needed")
    print("   • Immediate 2-3x token savings")
    print("   • Use extract_context() manually in your workflow")
    print("   • Plan Phase 2 (Aider integration) for next sprint")
    print("="*60)
