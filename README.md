# 🚀 Aider-MCP: Advanced AI Coding Server with Resilience & Strategic Model Selection

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Resilience](https://img.shields.io/badge/resilience-enhanced-blue)]()
[![Models](https://img.shields.io/badge/models-strategic%20selection-purple)]()

**Aider-MCP** is a production-grade MCP server that enables intelligent, parallel AI coding tasks with comprehensive resilience features and strategic model selection. Built for reliability, performance, and optimal model utilization.

## ✨ Key Features

### 🧠 **Strategic Model Selection**
- **Automatic model optimization** based on task type and complexity
- **Context-aware selection**: Complex algorithms → Gemini 2.5 Pro, Simple tasks → GPT-4.1 Nano
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

### 💰 **Cost Management & Budget Controls** ✨ **NEW**
- **Pre-flight cost estimation** with accurate token counting using tiktoken
- **Budget limits** prevent expensive operations ($5/task, $50/day, $500/month by default)
- **Real-time cost tracking** included in all task responses
- **Model-specific pricing** loaded from environment variables for easy updates
- **Organized data storage** in monthly JSON files (`/costs` directory)
- **On-demand CSV exports** for accounting and analysis
- **Privacy protection** with git-excluded cost data
- **4 MCP cost tools** for analytics, reporting, and budget monitoring

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
            │ Task Queue│ │Resource │ │ Cost       │
            │ Manager   │ │Monitor  │ │ Manager    │
            └───────────┘ └─────────┘ └────────────┘
```

## 📁 Project Structure ✨ **NEW**

The project follows a clean, professional app structure for better organization and maintainability:

```
aider-mcp-upgraded/
├── 📁 app/                      # Main application code
│   ├── 🔧 core/                # Core server functionality
│   │   └── aider_mcp.py        # Main MCP server entry point
│   ├── 🧠 models/              # AI model management
│   │   ├── model_registry.py   # Central model registry
│   │   └── strategic_model_selector.py # Intelligent model selection
│   ├── 💰 cost/                # Cost tracking & budget management
│   │   ├── cost_manager.py     # Cost tracking and budget management
│   │   └── cost_storage.py     # Cost data persistence
│   ├── 🔌 adapters/            # External integrations
│   │   ├── aider_adapter.py    # Aider integration adapter
│   │   └── aider_ai_code.py    # AI coding implementation
│   ├── 🛡️ resilience/          # Stability features
│   │   ├── aider_mcp_resilience.py # Resilience features
│   │   └── resilience_config.py    # Configuration management
│   └── 📜 scripts/             # Automation & setup scripts
│       ├── setup.sh            # One-command setup
│       ├── update_claude_config.py # Auto-update Claude config
│       └── generate_claude_config.py # Generate config manually
├── 🚀 main.py                  # Entry point (runs app.core.aider_mcp)
├── 📋 requirements.txt         # Python dependencies
├── ⚙️ .env.example             # Configuration template
└── 📖 README.md               # This file
```

### 🏆 **Benefits of This Structure**

- ✅ **Professional Organization** - Follows Python best practices
- ✅ **Clear Separation** - Related modules grouped by functionality
- ✅ **Easy Navigation** - Logical directory structure
- ✅ **Scalable** - Simple to add new features in appropriate directories
- ✅ **Maintainable** - Clean imports and dependencies

### 🔧 **How to Run**

```bash
# Primary method (recommended)
python main.py

# Alternative method
python -m app.core.aider_mcp
```

## 🚀 Quick Start

### One-Command Setup ✨ **NEW**

```bash
# Clone and setup everything automatically
git clone https://github.com/jacv888/aider-mcp-upgraded.git
cd aider-mcp-upgraded
./app/scripts/setup.sh
# 🎉 That's it! Restart Claude Desktop and you're ready to go!
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/jacv888/aider-mcp-upgraded.git
cd aider-mcp-upgraded

# Install dependencies (includes tiktoken for cost management)
pip install -r requirements.txt

# Install resilience features
python3 install_resilience.py --install

# Configure environment
cp .env.example .env
# Edit .env with your API keys and budget settings
```

### Basic Usage

#### Single AI Task
```python
code_with_ai(
    prompt="Create a React login component with validation",
    working_dir="./my-project",
    editable_files=["src/LoginForm.jsx"]
)
# Returns: {"success": true, "cost_info": {"total_cost": 0.001234, "model": "gpt-4.1-mini"}}
```

#### Multiple AI Tasks (Parallel)
```python
code_with_multiple_ai(
    prompts=[
        "Create React component with hooks",      # → GPT-4.1 Mini
        "Write unit tests for the API",          # → GPT-4.1 Mini
        "Generate comprehensive docs",           # → Gemini 2.5 Flash
        "Add responsive CSS styling"             # → Gemini 2.5 Flash
    ],
    working_dir="./my-project",
    editable_files_list=[
        ["src/Component.jsx"],
        ["tests/api.test.js"],
        ["docs/README.md"],
        ["src/styles.css"]
    ]
)
# Each task includes cost_info in response
```

#### Cost Management Tools ✨ **NEW**
```python
# Get cost summary (loads from monthly JSON files)
get_cost_summary(days=7)
# Returns: {"total_cost": 0.045, "task_count": 12, "average_cost": 0.004}

# Estimate cost before running (no storage required)
estimate_task_cost(
    prompt="Create React component",
    file_paths=["src/App.js"]
)
# Returns: {"cost_estimate": {"total_cost": 0.001234, "within_budget": true}}

# Check budget status
get_budget_status()
# Returns: {"remaining_budget": {"daily": "$49.95", "monthly": "$495.50"}}

# Export cost data (creates CSV in /costs directory)
export_cost_report(format="csv", days=30)
# Creates: costs/cost_export_20250603_181341.csv
# Returns: {"success": true, "file": "...", "records": 15}
```

## 💾 Cost Data Organization ✨ **NEW**

### Automatic Data Storage
Cost data is automatically organized in monthly files for optimal performance and management:

```
costs/
├── costs_2025-06.json         # Current month (auto-created)
├── costs_2025-05.json         # Previous months (auto-loaded for analytics)
└── cost_export_*.csv           # On-demand exports only
```

### Key Features
- **📊 Monthly JSON files** prevent massive single files
- **📋 CSV exports on request** via `export_cost_report(format="csv")`
- **🔒 Git protection** - `costs/` directory excluded from version control
- **📈 Auto-analytics** - loads 2-3 recent months for comprehensive summaries
- **💾 Automatic backups** - `.json.bak` files created on save
- **⚡ Fast loading** - only recent data loaded for better performance

### Usage Examples
```python
# Automatic: All tasks save to current month JSON
code_with_ai(prompt="...", editable_files=["..."])
# → Saves to costs/costs_2025-06.json

# Manual: Export specific period to CSV
export_cost_report(format="csv", days=30)
# → Creates costs/cost_export_20250603_181341.csv

# Analytics: Get summary from monthly files
get_cost_summary(days=90)
# → Loads costs_2025-06.json + costs_2025-05.json + costs_2025-04.json
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

### Cost Management & Budget Controls ✨ **NEW**
```bash
# Budget Protection
MAX_COST_PER_TASK=5.00          # Maximum cost per task (USD)
MAX_DAILY_COST=50.00            # Daily spending limit (USD)
MAX_MONTHLY_COST=500.00         # Monthly spending limit (USD)
COST_WARNING_THRESHOLD=1.00     # Warning threshold (USD)

# Cost Tracking & Data Storage
ENABLE_COST_TRACKING=true       # Enable cost management features
ENABLE_COST_LOGGING=false       # Console logging (off by default)

# Data Storage (automatic - no configuration needed)
# JSON: Saved to /costs/costs_YYYY-MM.json (monthly files)
# CSV: On-demand export to /costs/cost_export_TIMESTAMP.csv

# Model Pricing (per 1M tokens) - Easy to update when prices change
GPT_4_1_MINI_INPUT_PRICE=0.15   # GPT-4.1 Mini input price
GPT_4_1_MINI_OUTPUT_PRICE=0.60  # GPT-4.1 Mini output price
# ... (see .env.example for all model pricing)
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

## 🔧 Automated Configuration Setup ✨ **NEW**

We've made the setup process much more robust and maintainable! The server paths and configuration are now managed through `.env` variables instead of hardcoded paths.

### Quick Setup (Recommended)

```bash
# 1. Configure your paths in .env
cd aider-mcp-upgraded
cp .env.example .env
# Edit .env and set:
# MCP_SERVER_ROOT=/your/path/to/aider-mcp
# UV_PATH=/your/path/to/uv

# 2. Auto-update Claude Desktop config
python app/scripts/update_claude_config.py
# ✅ Automatically updates your Claude config with correct paths

# 3. Restart Claude Desktop
# The aider-mcp server will connect automatically!
```

### Manual Setup

```bash
# Generate configuration block for manual setup
python app/scripts/generate_claude_config.py
# Copy the output to your Claude Desktop config file
```

### Configuration Variables in .env

```bash
# 🛠️ MCP SERVER CONFIGURATION
MCP_SERVER_ROOT=/Users/jacquesv/mcp/aider-mcp    # Project root path
MCP_SERVER_ENTRY_POINT=app/core/aider_mcp.py    # Server entry point
UV_PATH=/Users/jacquesv/.local/bin/uv           # UV binary path
```

### Benefits of New Configuration System

- ✅ **No hardcoded paths** - Everything configurable via `.env`
- ✅ **Automatic setup** - Scripts handle Claude config updates
- ✅ **Cross-platform support** - Works on macOS, Windows, and Linux
- ✅ **Portable** - Easy to move between machines
- ✅ **Maintainable** - One place to update paths
- ✅ **Error-resistant** - Proper PYTHONPATH handling

### Cross-Platform Claude Desktop Config Paths

The scripts automatically detect the correct Claude Desktop config location:

| Platform | Default Config Path |
|----------|-------------------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%/Claude/claude_desktop_config.json` |
| **Linux** | `~/.config/claude/claude_desktop_config.json` |

**Custom Path Override:**
```bash
# Set custom Claude config location in .env
CLAUDE_CONFIG_PATH=/custom/path/to/claude_desktop_config.json
```

## 🎯 Strategic Model Selection

The system automatically selects optimal models based on task analysis:

| Task Type | Optimal Model | Reason |
|-----------|---------------|---------|
| **Complex Algorithms** | Gemini 2.5 Pro | Superior reasoning |
| **Simple Tasks** | GPT-4.1 Nano | Fast & cost-effective |
| **Documentation** | Gemini 2.5 Flash | Excellent writing |
| **Testing** | GPT-4.1 Mini | Efficient generation |
| **CSS/Styling** | Gemini 2.5 Flash | Great design capabilities |
| **React/Frontend** | GPT-4.1 Mini | Complex logic handling |
| **API/Backend** | Gemini 2.5 Flash | Fast server code |
| **Debugging** | GPT-4.1 Mini | Best problem-solving |

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

| Metric | Before Resilience | After Resilience + Cost Management |
|--------|------------------|------------------|
| **Connection Stability** | ❌ Disconnected | ✅ **100% Stable** |
| **Task Success Rate** | ❌ Failed | ✅ **100% (3/3)** |
| **Parallel Speedup** | ❌ N/A | ✅ **2.64x** |
| **Resource Usage** | ❌ Uncontrolled | ✅ **Monitored** |
| **Recovery Time** | ❌ Manual restart | ✅ **Automatic** |
| **Cost Transparency** | ❌ Unknown | ✅ **Real-time tracking** |
| **Budget Protection** | ❌ No limits | ✅ **Automatic blocking** |

### Cost Management Results ✨ **NEW**
- **Simple tasks**: ~$0.0008 (500 tokens, GPT-4.1 Mini)
- **Medium tasks**: ~$0.003 (2,000 tokens)
- **Budget protection**: Prevents tasks >$5.00 automatically
- **Overhead**: <2ms per task, zero token usage for cost calculations
- **Cost tracking**: Included in every response JSON

### Test Results
- **Tasks**: 3 parallel (HTML, JS, CSS generation)
- **Execution Time**: 25.02 seconds (parallel) vs 65.96 seconds (sequential)
- **Files Generated**: 451 lines of production-ready code
- **Connection**: Zero disconnections throughout intensive processing
- **Total Cost**: $0.024 for complete landing page generation
- **Data Storage**: Organized in monthly JSON files with on-demand CSV export

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

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone https://github.com/jacv888/aider-mcp-upgraded.git
cd aider-mcp-upgraded

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

- **Issues**: [GitHub Issues](https://github.com/jacv888/aider-mcp-upgraded/issues)
- **Community**: Join discussions in GitHub Discussions

---

**Built with ❤️ for developers who need reliable, intelligent AI coding assistance**
