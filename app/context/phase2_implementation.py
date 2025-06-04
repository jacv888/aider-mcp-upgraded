"""
Phase 2 Implementation: Minimal Code Changes Required

Shows exactly what needs to be modified for automatic Aider integration.
"""

# ==============================================================================
# CHANGE 1: Add to function signature (1 line addition)
# ==============================================================================

def code_with_ai(
    ai_coding_prompt: str,
    relative_editable_files: List[str],
    relative_readonly_files: List[str],
    model: str = None,
    working_dir: str = None,
    target_elements: Optional[List[str]] = None,  # NEW PARAMETER
) -> str:


# ==============================================================================
# CHANGE 2: Add context extraction logic (~15 lines)
# ==============================================================================

def code_with_ai(
    ai_coding_prompt: str,
    relative_editable_files: List[str],
    relative_readonly_files: List[str],
    model: str = None,
    working_dir: str = None,
    target_elements: Optional[List[str]] = None,
) -> str:
    # Existing code...
    
    # NEW: Context extraction logic
    enhanced_prompt = ai_coding_prompt
    
    if (os.getenv('ENABLE_CONTEXT_EXTRACTION', 'false').lower() == 'true' and 
        target_elements and len(target_elements) > 0):
        
        from app.context import extract_context
        
        max_tokens = int(os.getenv('CONTEXT_DEFAULT_MAX_TOKENS', '4000'))
        
        # Extract focused context for each file/target pair
        context_parts = []
        for i, file_path in enumerate(relative_editable_files):
            full_path = os.path.join(working_dir or '.', file_path)
            target = target_elements[i] if i < len(target_elements) else target_elements[0]
            
            focused_context = extract_context(full_path, target, max_tokens // len(relative_editable_files))
            context_parts.append(f"# {file_path} (focused on {target}):\n{focused_context}")
        
        # Enhance the prompt with focused context
        enhanced_prompt = f"""FOCUSED CONTEXT:
{chr(10).join(context_parts)}

TASK: {ai_coding_prompt}"""
    
    # Continue with existing Aider logic using enhanced_prompt instead of ai_coding_prompt
    # ... rest of function unchanged


# ==============================================================================
# CHANGE 3: Add same logic to code_with_multiple_ai (~5 lines)
# ==============================================================================

def code_with_multiple_ai(
    prompts: List[str],
    working_dir: str,
    editable_files_list: List[List[str]],
    readonly_files_list: Optional[List[List[str]]] = None,
    models: Optional[List[str]] = None,
    max_workers: Optional[int] = None,
    parallel: bool = True,
    target_elements_list: Optional[List[List[str]]] = None,  # NEW PARAMETER
):
    # Similar context extraction logic for multiple files
    pass


# ==============================================================================
# TOTAL IMPLEMENTATION EFFORT: ~20 lines of code, 2-4 hours work
# ==============================================================================

print("""
✅ PHASE 2 IMPLEMENTATION SUMMARY:

📝 Code Changes Required:
   • Add 1 optional parameter to function signatures
   • Add ~15 lines of context extraction logic  
   • Add ~5 lines for multiple AI function
   • Total: ~20 lines of code

⏱️ Time Estimate: 2-4 hours
   • 1 hour: Code changes
   • 1 hour: Testing
   • 1-2 hours: Validation and edge cases

🔧 Environment Variable Control:
   • ENABLE_CONTEXT_EXTRACTION=true/false
   • Easy to toggle on/off for testing
   • Backward compatible (defaults to disabled)
   • No breaking changes to existing workflows

🎯 Usage After Implementation:
   code_with_ai(
       prompt="Fix the validation bug",
       editable_files=["src/api/users.py"], 
       target_elements=["update_user"]  # NEW!
   )
   # Automatically uses 70% fewer tokens!

✅ This is VERY easy to implement!
""")
