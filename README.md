# 🚀 Aider-MCP: Advanced AI Coding Server with Resilience & Strategic Model Selection

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Resilience](https://img.shields.io/badge/resilience-enhanced-blue)]()
[![Models](https://img.shields.io/badge/models-strategic%20selection-purple)]()

**Aider-MCP** is a production-grade MCP server that enables intelligent, parallel AI coding tasks with comprehensive resilience features and strategic model selection. Built for reliability, performance, and optimal model utilization.

## ✨ Key Features

### 🧠 **Strategic Model Selection**
- **Automatic model optimization** based on task type and complexity
- **Context-aware selection**: Complex algorithms → Claude 3.5 Sonnet, Simple tasks → GPT-4o Mini
- **Custom model override** capability when needed
- **Cost optimization** through intelligent model matching

### 🛡️ **Resilience & Stability**
- **Connection health monitoring** with automatic recovery
- **Resource management** with CPU/Memory thresholds
- **Circuit breaker protection** against cascade failures
- **Task queue management** preventing system overload
- **Zero disconnection** architecture for stable operations

### ⚡ **High-Performance Parallel Processing**
- **Multi-agent execution** with configurable concurrency limits
- **2.6x performance boost** through intelligent parallelization
- **Task branching** for independent development streams
- **Real-time progress monitoring** and detailed reporting

### ⚙️ **Advanced Configuration System**
- **Priority-based configuration** loading (project → global → defaults)
- **Environment variable support** with hot-reloading
- **Profile-based settings** (development, production, high-load)
- **Runtime configuration updates** without server restart

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│   Aider-MCP      │◄──►│   AI Models     │
│   (Claude)      │    │   Server         │    │   (Strategic)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
            ┌───────▼───┐ ┌────▼────┐ ┌───▼────────┐
            │ Task Queue│ │Resource │ │ Circuit    │
            │ Manager   │ │Monitor  │ │ Breaker    │
            └───────────┘ └─────────┘ └────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/eiliyaabedini/aider-mcp.git
cd aider-mcp

# Install dependencies
pip install -r requirements.txt

# Install resilience features
python3 install_resilience.py --install

# Configure environment
cp .env.sample .env
# Edit .env with your API keys
```

### Basic Usage

#### Single AI Task
```python
code_with_ai(
    prompt="Create a React login component with validation",
    working_dir="./my-project",
    editable_files=["src/LoginForm.jsx"]
)
```

#### Multiple AI Tasks (Parallel)
```python
code_with_multiple_ai(
    prompts=[
        "Create React component with hooks",      # → Claude 3.5 Sonnet
        "Write unit tests for the API",          # → GPT-4o Mini  
        "Generate comprehensive docs",           # → Gemini 2.5 Pro
        "Add responsive CSS styling"             # → GPT-4o
    ],
    working_dir="./my-project",
    editable_files_list=[
        ["src/Component.jsx"],
        ["tests/api.test.js"], 
        ["docs/README.md"],
        ["src/styles.css"]
    ]
)
```

## 📋 Configuration Guide

### Priority System
Configuration is loaded in priority order:
1. **Project-level**: `/path/to/project/.env` (highest priority)
2. **Global**: `~/.config/aider/.env` (medium priority)  
3. **System**: Current directory `.env` (lowest priority)

### Resilience Settings
```bash
# Task Management
MAX_CONCURRENT_TASKS=3           # Prevent overload
MAX_TASK_QUEUE_SIZE=10          # Queue capacity

# Resource Monitoring  
CPU_USAGE_THRESHOLD=75.0        # CPU limit (%)
MEMORY_USAGE_THRESHOLD=80.0     # Memory limit (%)

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=3   # Failure limit
CIRCUIT_BREAKER_RESET_TIMEOUT=60      # Reset time (seconds)

# Health Monitoring
HEALTH_CHECK_INTERVAL=30        # Check frequency (seconds)
```

### Strategic Model Configuration
```bash
# Automatic model selection (recommended)
AIDER_MODEL=                    # Empty = strategic selection

# Or specify default model
AIDER_MODEL=gpt-4.1-mini       # Override strategic selection

# API Keys
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key
```

## 🎯 Strategic Model Selection

The system automatically selects optimal models based on task analysis:

| Task Type | Optimal Model | Reason |
|-----------|---------------|---------|
| **Complex Algorithms** | Claude 3.5 Sonnet | Superior reasoning |
| **Simple Tasks** | GPT-4o Mini | Fast & cost-effective |
| **Documentation** | Gemini 2.5 Pro | Excellent writing |
| **Testing** | GPT-4o Mini | Efficient generation |
| **CSS/Styling** | GPT-4o | Great design capabilities |
| **React/Frontend** | Claude 3.5 Sonnet | Complex logic handling |
| **API/Backend** | Claude 3.5 Haiku | Fast server code |
| **Debugging** | Claude 3.5 Sonnet | Best problem-solving |

## 🛡️ Resilience Features

### Connection Health Monitor
- **Heartbeat system** detects connection issues
- **Automatic reconnection** without manual intervention
- **Health status logging** for monitoring

### Resource Management
- **CPU/Memory monitoring** with configurable thresholds
- **Automatic throttling** under high load
- **Graceful degradation** instead of crashes

### Circuit Breaker Protection
- **Failure threshold detection** (default: 3 failures)
- **Automatic recovery** after timeout (default: 60s)
- **Cascade failure prevention**

### Task Queue Management
- **Concurrency limits** prevent system overload
- **Queue size management** with overflow protection
- **Task prioritization** and fair scheduling

## 📊 Performance Benchmarks

Based on real testing with tech startup landing page generation:

| Metric | Before Resilience | After Resilience |
|--------|------------------|------------------|
| **Connection Stability** | ❌ Disconnected | ✅ **100% Stable** |
| **Task Success Rate** | ❌ Failed | ✅ **100% (3/3)** |
| **Parallel Speedup** | ❌ N/A | ✅ **2.64x** |
| **Resource Usage** | ❌ Uncontrolled | ✅ **Monitored** |
| **Recovery Time** | ❌ Manual restart | ✅ **Automatic** |

### Test Results
- **Tasks**: 3 parallel (HTML, JS, CSS generation)
- **Execution Time**: 25.02 seconds (parallel) vs 65.96 seconds (sequential)
- **Files Generated**: 451 lines of production-ready code
- **Connection**: Zero disconnections throughout intensive processing

## 🔧 Advanced Usage

### Task Branching Strategy
```python
# Branch 1: Frontend Development
frontend_tasks = [
    "Create React components",
    "Add responsive styling", 
    "Implement user interactions"
]

# Branch 2: Backend Development  
backend_tasks = [
    "Design API endpoints",
    "Add database models",
    "Implement authentication"
]

# Branch 3: Testing & Documentation
testing_tasks = [
    "Write unit tests",
    "Add integration tests",
    "Generate API documentation"
]

# Execute branches in parallel
code_with_multiple_ai(
    prompts=frontend_tasks + backend_tasks + testing_tasks,
    working_dir="./project",
    # ... configuration
)
```

### Custom Model Selection
```python
# Override strategic selection
code_with_multiple_ai(
    prompts=["Complex algorithm task"],
    models=["claude-3-5-sonnet-20241022"],  # Force specific model
    # ... other parameters
)

# Mixed approach
code_with_multiple_ai(
    prompts=["Task 1", "Task 2", "Task 3"],
    models=[None, "gpt-4o-mini", None],  # Strategic, Custom, Strategic
    # ... other parameters
)
```

## 🐛 Troubleshooting

### Common Issues

#### Connection Disconnections
```bash
# Check resilience status
python tests/multi-ai-2/resilience-test.py

# Verify configuration
cat .env | grep -E "(THRESHOLD|CONCURRENT|QUEUE)"

# Monitor server logs
tail -f aider_mcp.log
```

#### High Resource Usage
```bash
# Check current usage
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

# Adjust thresholds in .env
CPU_USAGE_THRESHOLD=60.0
MEMORY_USAGE_THRESHOLD=70.0
```

#### Model Selection Issues
```bash
# Test strategic selection
python -c "from strategic_model_selector import get_optimal_model; print(get_optimal_model('create React component'))"

# Check API keys
python -c "import os; print('OPENAI_KEY:', bool(os.getenv('OPENAI_API_KEY'))); print('ANTHROPIC_KEY:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

## 📁 Project Structure

```
aider-mcp/
├── 📄 aider_mcp.py                 # Main MCP server with resilience
├── 🧠 strategic_model_selector.py  # Intelligent model selection
├── 🛡️ aider_mcp_resilience.py     # Resilience components
├── ⚙️ resilience_config.py         # Configuration management
├── 📊 install_resilience.py        # Installation script
├── 📚 docs/
│   ├── CONFIG-PRIORITY.md          # Configuration system guide
│   ├── STRATEGIC-MODEL-SELECTION.md # Model selection guide
│   └── RESILIENCE_GUIDE.md         # Resilience features guide
├── 🧪 tests/
│   ├── multi-ai/                   # Original test results
│   └── multi-ai-2/                 # Resilience test results
└── 📝 README.md                    # This file
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone https://github.com/eiliyaabedini/aider-mcp.git
cd aider-mcp

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python tests/test_multiple_ai.py
```

### Adding New Features
1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Implement** changes with tests
4. **Test** resilience: `python tests/multi-ai-2/resilience-test.py`
5. **Submit** pull request

### Testing Guidelines
- Test both single and multiple AI operations
- Verify resilience features remain active
- Check strategic model selection accuracy
- Validate configuration priority system

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Aider** - The amazing AI coding assistant that powers this server
- **Model Context Protocol** - For standardizing AI model interactions
- **Contributors** - Everyone who helped improve stability and performance

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/eiliyaabedini/aider-mcp/issues)
- **Documentation**: See `docs/` directory for detailed guides
- **Community**: Join discussions in GitHub Discussions

---

**Built with ❤️ for developers who need reliable, intelligent AI coding assistance**
