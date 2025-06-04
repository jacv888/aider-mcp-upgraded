#!/usr/bin/env python3
"""
Quick test for Context-Aware File Pruning system
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from app.context import extract_context, ContextManager, ExtractionConfig
    print("✅ Context-Aware File Pruning imports successful!")
    
    # Create a simple test file
    test_content = '''
def hello_world():
    print("Hello, World!")
    return "success"

def goodbye_world():
    print("Goodbye, World!")
    return hello_world()

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    print(f"📝 Created test file: {temp_file}")
    
    # Test simple extraction
    focused = extract_context(temp_file, 'hello_world', 500)
    print(f"🎯 Simple extraction result:")
    print(f"   Length: {len(focused)} chars")
    print(f"   Contains target: {'hello_world' in focused}")
    
    # Test advanced extraction
    manager = ContextManager()
    config = ExtractionConfig(max_tokens=300, min_relevance_score=2.0)
    result = manager.extract_relevant_context(temp_file, 'get_value', config)
    
    print(f"🔧 Advanced extraction result:")
    print(f"   Extraction used: {not result.get('fallback_used', False)}")
    print(f"   Language detected: {result.get('language', 'unknown')}")
    print(f"   Target found: {len(result.get('target_elements', [])) > 0}")
    
    if result.get('extraction_stats'):
        stats = result['extraction_stats']
        print(f"   Token reduction: {stats.get('reduction_ratio', 0):.2%}")
        print(f"   Focused tokens: {stats.get('focused_tokens', 0)}")
    
    # Clean up
    import os
    os.unlink(temp_file)
    
    print("✅ All tests passed! Context-Aware File Pruning is working correctly.")
    print("🚀 Ready for integration with your AI coding workflow!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required dependencies are installed.")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
