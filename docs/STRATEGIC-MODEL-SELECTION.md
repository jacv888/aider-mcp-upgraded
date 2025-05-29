# Strategic Model Selection Examples and Documentation

## 🧠 Enhanced Aider Integration with Strategic Model Selection

Your aider integration now includes intelligent model selection that automatically chooses the optimal AI model based on the task type and complexity.

## 🎯 Model Selection Strategy

### **Complexity-Based Selection:**
- **Hard/Complex tasks** → `anthropic/claude-3-5-sonnet-20241022` (Best reasoning)
- **Medium tasks** → `gpt-4o` (Balanced performance)  
- **Easy/Simple tasks** → `gpt-4o-mini` (Fast & cost-effective)

### **Task-Type Based Selection:**
- **Algorithm/Data Structure** → `claude-3-5-sonnet` (Best logical reasoning)
- **Documentation/Writing** → `gemini-2.5-pro` (Excellent at explanations)
- **Testing** → `gpt-4o-mini` (Efficient for test generation)
- **CSS/Styling** → `gpt-4o` (Great design capabilities)
- **React/Frontend** → `claude-3-5-sonnet` (Complex state management)
- **API/Backend** → `claude-3-5-haiku` (Fast server-side code)
- **Database** → `gpt-4o` (Good with SQL and queries)
- **Debugging** → `claude-3-5-sonnet` (Best problem-solving)

## 💡 Usage Examples

### **Single Task with Auto-Selection:**
```python
code_with_ai(
    prompt="Create a complex React component with advanced state management",
    # Automatically selects: claude-3-5-sonnet (detected: complex + react)
    working_dir="./my-app",
    editable_files=["src/components/AdvancedComponent.tsx"]
)
```

### **Multiple Tasks with Strategic Selection:**
```python
code_with_multiple_ai(
    prompts=[
        "Create complex algorithm for pathfinding",        # → claude-3-5-sonnet
        "Write simple unit tests",                         # → gpt-4o-mini
        "Generate comprehensive documentation",            # → gemini-2.5-pro  
        "Add CSS animations and hover effects",           # → gpt-4o
        "Optimize database queries for performance",      # → claude-3-5-haiku
        "Debug the authentication system"                 # → claude-3-5-sonnet
    ],
    working_dir="./my-project",
    # models=None,  # Let system choose optimal models automatically
    parallel=True
)
```

### **Mixed Auto/Manual Selection:**
```python
code_with_multiple_ai(
    prompts=[
        "Create React dashboard with charts",
        "Write API documentation", 
        "Generate test cases"
    ],
    models=[
        None,                                    # Auto-select → claude-3-5-sonnet
        "gemini/gemini-2.5-pro-exp-03-25",     # Force specific model
        None                                     # Auto-select → gpt-4o-mini
    ],
    working_dir="./dashboard-app"
)
```

## ⚙️ Configuration

All model mappings are defined in your primary config file:
`/Users/jacquesv/MCP/aider-mcp/.env`

You can customize the strategic selection by updating these environment variables:

```bash
# Complexity-based models
AIDER_MODEL_HARD=anthropic/claude-3-5-sonnet-20241022
AIDER_MODEL_EASY=gpt-4o-mini

# Task-type models  
AIDER_MODEL_REACT=anthropic/claude-3-5-sonnet-20241022
AIDER_MODEL_CSS=gpt-4o
AIDER_MODEL_TESTING=gpt-4o-mini
AIDER_MODEL_WRITING=gemini/gemini-2.5-pro-exp-03-25

# And many more...
```

## 🎯 Benefits

✅ **Cost Optimization**: Uses cheaper models for simple tasks
✅ **Performance**: Uses fastest models for quick iterations  
✅ **Quality**: Uses best models for complex reasoning tasks
✅ **Automatic**: No need to manually choose models
✅ **Flexible**: Can override selection when needed
✅ **Configurable**: Customize mappings via .env file

## 🔄 How It Works

1. **Prompt Analysis**: System analyzes your prompt for keywords and patterns
2. **Category Scoring**: Assigns scores to different task categories
3. **Model Selection**: Chooses optimal model based on highest-scoring category
4. **Fallback**: Uses default model if no specific patterns match
5. **Override**: Explicit model parameter always takes precedence

Your aider integration is now significantly more intelligent and cost-effective! 🚀
