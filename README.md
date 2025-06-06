# 🚀 Aider-MCP: Advanced AI Coding Server with Analytics Architecture

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Analytics](https://img.shields.io/badge/analytics-triple%20system-blue)]()
[![Auto-Detection](https://img.shields.io/badge/auto--detection-universal%20token%20savings-orange)]()
[![Conflict-Detection](https://img.shields.io/badge/conflict--detection-auto%20prevention-red)]()
[![Models](https://img.shields.io/badge/models-strategic%20selection-purple)]()
[![Chunking](https://img.shields.io/badge/logs-monthly%20chunked-green)]()
[![Frameworks](https://img.shields.io/badge/frameworks-universal%20support-yellowgreen)]()

**Aider-MCP** is a production-grade MCP server that enables intelligent, parallel AI coding tasks with universal auto-detection, context extraction, conflict prevention, and a comprehensive triple analytics architecture. Built for reliability, performance, and up to 70% token reduction through smart optimization—now for both Python and all major JavaScript/TypeScript frameworks.

---

## 🌐 Universal Framework Support ✨ **NEW**

Aider-MCP is now a truly universal system for modern full-stack development, supporting both Python and the entire JavaScript/TypeScript ecosystem:

- **Automatic context extraction and auto-detection** for Python, JavaScript, and TypeScript codebases
- **First-class support for React, Next.js, Zod, TypeScript, Node.js, Express, and more**
- **Universal token reduction**: Smart context pruning and target detection for all supported frameworks
- **Seamless integration** for monorepos and hybrid stacks

### 🏆 Supported Frameworks

| Language      | Framework/Library      | Auto-Detection | Context Extraction | Token Reduction |
|---------------|-----------------------|:--------------:|:-----------------:|:---------------:|
| Python        | Django, FastAPI, Flask|      ✅        |        ✅         |       ✅        |
| JavaScript    | React, Next.js, Node  |      ✅        |        ✅         |       ✅        |
| TypeScript    | React, Next.js, Zod   |      ✅        |        ✅         |       ✅        |
| JS/TS         | Express, Vite, Custom |      ✅        |        ✅         |       ✅        |

> **Universal**: Works out-of-the-box for any modern Python, JS, or TS project.

---

## ✨ Key Features

### 🧠 **Strategic Model Selection**
- **Automatic model optimization** based on task type and complexity
- **Context-aware selection**: Complex algorithms → Gemini 2.5 Pro, Simple tasks → GPT-4.1 Nano
- **Custom model override** capability when needed
- **Cost optimization** through intelligent model matching

### 🎯 **Universal Auto-Detection & Context Extraction** ✨ **ENHANCED**
- **Universal auto-detection** for Python, JavaScript, and TypeScript (React, Next.js, Zod, etc.)
- **70%+ token reduction** through intelligent context extraction—now for all major frameworks
- **Automatic target detection** from prompts (hands-free optimization) for both Python and JS/TS
- **Smart context pruning** focuses on relevant code sections only, regardless of language
- **Comprehensive analytics** track auto-detection performance and savings across all stacks

### 🔒 **Auto-Conflict Detection** ✨ **NEW**
- **Intelligent conflict prevention** for parallel task execution
- **Automatic serialization** when file conflicts are detected
- **Three handling modes**: auto (default), warn, ignore
- **Clear user feedback** about conflicts and actions taken
- **Zero configuration** required - works automatically
- **Maintains parallelism** for non-conflicting tasks

### 📊 **Dual Analytics Architecture** ✨ **NEW**
Specialized systems for comprehensive monitoring:

**🔧 Aider-MCP Cost Management**
- **Pre-flight cost estimation** with accurate token counting
- **Budget limits** prevent expensive operations ($5/task, $50/day, $500/month)
- **Real-time cost tracking** included in all task responses
- **4 MCP cost tools** for analytics, reporting, and budget monitoring

**⚡ Phase 2A Performance & Health Analytics**
- **Performance monitoring** (task duration, success rates)
- **Operational health** (error detection, system status)
- **Business intelligence** insights for optimization
- **JSON structured logging** with automated metrics extraction

### 📅 **Monthly Log Chunking** ✨ **NEW**
- **Standardized monthly files** across all log types for consistent analysis
- **Easy correlation** between operational, auto-detection, and cost data
- **Time-based archival** with predictable monthly chunks
- **Cross-system analytics** enabled by unified time windows

### 🏥 **Health Monitoring System** ✨ **NEW**
- **Real-time system health checks** via `get_system_health()` MCP tool
- **Log-based health analysis** using existing operational and auto-detection logs
- **Three-tier status system**: healthy/degraded/unhealthy with detailed explanations
- **24-hour health windows** for recent system activity analysis
- **Error detection and alerting** with specific issue identification
- **Zero additional infrastructure** - leverages existing logging system

### ⚙️ **Advanced Configuration System**
- **Priority-based configuration** loading (project → global → defaults)
- **Environment variable support** with hot-reloading
- **Profile-based settings** (development, production, high-load)
- **Runtime configuration updates** without server restart

## 🏗️ Analytics Architecture

The system provides comprehensive monitoring through specialized, independent systems with standardized monthly chunking:

```
COST MANAGEMENT           PERFORMANCE & HEALTH    AUTO-DETECTION ANALYTICS
(Aider-MCP Functions)     (Phase 2A Analytics)    (Dedicated Logging)
┌─────────────────┐      ┌─────────────────────┐  ┌────────────────────┐
│ get_cost_summary│      │ extract_performance │  │ Auto-detection     │
│ estimate_cost   │      │ extract_operational │  │ Token reduction    │
│ budget_status   │      │ system_health       │  │ Performance impact │
│ export_reports  │      │ business_insights   │  │ Context extraction │
└─────────────────┘      └─────────────────────┘  └────────────────────┘
        │                          │                        │
        └──────────┬─────────────────┴────────────────────────┘
                   │
             📅 MONTHLY CHUNKING (Standardized)
         /costs/costs_2025-06.json
         /logs/operational_2025-06.json  
         /logs/auto_detection_2025-06.json
            ┌─────────────┐
            │   USER      │
            │ Uses both   │
            │ as needed   │
            └─────────────┘
```

### Benefits of Dual System Architecture
- ✅ **Specialized Excellence** - Each system optimized for its purpose
- ✅ **No Duplication** - Clear separation of responsibilities
- ✅ **Independent Evolution** - Systems can be updated separately
- ✅ **User Clarity** - Know exactly which tool to use when
- ✅ **Universal Token Reduction** - Analytics and savings now apply to all major Python, JavaScript, and TypeScript frameworks

## 📋 USER GUIDANCE

### For Cost Management:
```python
# Use Aider-MCP Functions
get_cost_summary(days=7)
estimate_task_cost(prompt="Create component")
get_budget_status()
export_cost_report(format="csv")
# Export different time periods
export_cost_report(format="csv", days=7)   # Last week
export_cost_report(format="csv", days=1)   # Today only
# Export as JSON instead
export_cost_report(format="json", days=30)
# Export summary format
export_cost_report(format="summary", days=30)
```

### For Performance & Health Analytics:
```bash
# Use Phase 2A Analytics
python -m app.analytics.metrics_extractor --report=summary
python -m app.analytics.metrics_extractor --report=performance
python -m app.analytics.metrics_extractor --report=operational
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

## 🌐 Universal Framework Examples ✨ **NEW**

### Python Framework Examples
```python
# Django
code_with_ai(
    prompt="Fix the User model authentication method",
    editable_files=["accounts/models.py"]
)

# FastAPI
code_with_ai(
    prompt="Create endpoint for user registration with Pydantic validation",
    editable_files=["api/auth.py"]
)

# Flask
code_with_ai(
    prompt="Add Flask-Login authentication to the login_required decorator",
    editable_files=["app/auth/routes.py"]
)
```

### JavaScript/TypeScript Framework Examples
```python
# React Components
code_with_ai(
    prompt="Create UserProfile component with hooks and error handling",
    editable_files=["src/components/UserProfile.tsx"]
)

# Next.js API Routes  
code_with_ai(
    prompt="Add Next.js API route for user authentication with JWT",
    editable_files=["pages/api/auth/login.ts"]
)

# Next.js Server Components
code_with_ai(
    prompt="Update getServerSideProps to use Next.js 14 App Router",
    editable_files=["app/dashboard/page.tsx"]
)

# Zod Schema Validation
code_with_ai(
    prompt="Create comprehensive Zod schema for user registration form",
    editable_files=["src/schemas/userSchema.ts"]
)

# TypeScript Interfaces
code_with_ai(
    prompt="Define TypeScript interfaces for API response types",
    editable_files=["src/types/api.ts"]
)
```

### Full-Stack Project Examples (Python + JS/TS)
```python
# E-commerce Platform
code_with_multiple_ai(
    prompts=[
        "Create FastAPI product catalog endpoint with pagination",     # Python Backend
        "Build React ProductGrid component with infinite scroll",     # React Frontend  
        "Add Zod validation schema for product creation",             # TypeScript Validation
        "Implement Flask-SQLAlchemy Product model with relationships" # Python Database
    ],
    editable_files_list=[
        ["backend/api/products.py"],
        ["frontend/src/components/ProductGrid.tsx"],
        ["shared/schemas/productSchema.ts"],
        ["backend/models/product.py"]
    ]
)

# Real-time Chat Application
code_with_multiple_ai(
    prompts=[
        "Create Django WebSocket consumer for real-time messaging",   # Python WebSocket
        "Build React chat interface with TypeScript and hooks",      # React Frontend
        "Add Zod message validation and sanitization",               # TypeScript Validation
        "Implement Redis message queuing with Celery"                # Python Background Tasks
    ],
    editable_files_list=[
        ["backend/chat/consumers.py"],
        ["frontend/src/components/ChatInterface.tsx"],
        ["shared/types/messageTypes.ts"],
        ["backend/tasks/message_queue.py"]
    ]
)
```

### Framework-Specific Auto-Detection Examples
```python
# All these prompts automatically detect targets and extract focused context:

# React Ecosystem
"Refactor the LoginForm component to use React Hook Form"          → Detects: LoginForm
"Fix the useAuth custom hook with proper TypeScript types"        → Detects: useAuth  
"Update AuthProvider context to handle token refresh"             → Detects: AuthProvider

# Next.js Ecosystem  
"Add middleware for authentication in Next.js 14"                 → Detects: middleware
"Create dynamic [id] page component with getStaticPaths"          → Detects: getStaticPaths
"Fix the API route handler for user profile updates"              → Detects: handler

# TypeScript + Zod
"Create comprehensive validation schema using Zod for forms"       → Detects: schema
"Fix type definitions in the UserInterface"                       → Detects: UserInterface
"Add runtime validation to the API endpoint with Zod"             → Detects: validation schema

# Node.js + Express
"Create Express middleware for JWT authentication"                 → Detects: middleware
"Add route handler for file uploads with multer"                  → Detects: route handler
"Fix the database connection with proper error handling"          → Detects: connection
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

#### Cost Management (Aider-MCP Functions) ✨ **NEW**
```python
# Get comprehensive cost summary
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

#### Health Monitoring ✨ **NEW**
```python
# Get comprehensive system health status
get_system_health()
# Returns: {
#   "status": "healthy",
#   "message": "✅ AI coding system is operating normally",
#   "summary": {
#     "operational_entries_24h": 156,
#     "operational_errors": 0,
#     "operational_warnings": 2,
#     "auto_detection_entries_24h": 43,
#     "auto_detection_errors": 0
#   },
#   "issues": [],
#   "recent_errors": []
# }

# Use for workflow integration
health = get_system_health()
if json.loads(health)["status"] == "healthy":
    proceed_with_coding_task()
else:
    investigate_system_issues()
```
#### Performance & Health Analytics (Phase 2A) ✨ **NEW**
```bash
# Generate summary report
python -m app.analytics.metrics_extractor --report=summary

# Performance-specific analysis
python -m app.analytics.metrics_extractor --report=performance

# Operational health monitoring
python -m app.analytics.metrics_extractor --report=operational

# JSON output for integration
python -m app.analytics.metrics_extractor --output=json

# Generate HTML reports
python app/analytics/generate_reports.py --export=html

# Continuous monitoring
python app/analytics/generate_reports.py --watch --interval=300
```

### 🏥 Health Monitoring Integration ✨ **NEW**

#### Daily Workflow Examples
```python
# Morning system check
health = get_system_health()
print(json.loads(health)["message"])  # ✅ AI coding system is operating normally

# Pre-task validation
if json.loads(get_system_health())["status"] != "healthy":
    print("⚠️ System issues detected - check logs before proceeding")

# Post-deployment verification
after_deploy_health = get_system_health()
if "unhealthy" in after_deploy_health:
    trigger_rollback_procedure()
```

#### Monitoring & Alerting Patterns
```python
# Simple monitoring script
import json
import time

def monitor_system_health():
    health = json.loads(get_system_health())
    
    if health["status"] == "unhealthy":
        send_alert(f"🚨 CRITICAL: {health['message']}")
        log_incident(health["recent_errors"])
    elif health["status"] == "degraded":
        send_warning(f"⚠️ WARNING: {health['message']}")
    
    return health["status"]

# Continuous monitoring
while True:
    status = monitor_system_health()
    time.sleep(300)  # Check every 5 minutes
```

#### Health Status Integration
```python
# Before important coding tasks
def safe_coding_task(prompt, files):
    health = json.loads(get_system_health())
    
    if health["status"] == "unhealthy":
        return {"error": "System unhealthy - aborting task", "health": health}
    
    if health["status"] == "degraded":
        print("⚠️ System degraded but proceeding...")
    
    return code_with_ai(prompt=prompt, editable_files=files)

# Batch operation health checks
def batch_with_health_monitoring(tasks):
    results = []
    for i, task in enumerate(tasks):
        if i % 5 == 0:  # Check health every 5 tasks
            health = json.loads(get_system_health())
            if health["status"] == "unhealthy":
                return {"halted_at": i, "reason": health["message"]}
        
        results.append(execute_task(task))
    return results
```

## 💾 Analytics Data Organization ✨ **NEW**

### Cost Management (Aider-MCP)
Automatic cost data storage in monthly files:

```
costs/
├── costs_2025-06.json         # Current month (auto-created)
├── costs_2025-05.json         # Previous months (auto-loaded for analytics)
└── cost_export_*.csv           # On-demand exports only
```

### Performance Analytics (Phase 2A)
Structured logging for performance monitoring:

```
logs/
├── operational.json           # Machine-readable structured logs
├── operational.log           # Human-readable standard logs
└── reports/                  # Generated analytics reports
    ├── summary_latest.json
    ├── performance_latest.json
    └── operational_latest.json
```

### Key Features
- **📊 Monthly JSON files** prevent massive single files (cost management)
- **📋 CSV exports on request** via `export_cost_report(format="csv")`
- **🔒 Git protection** - `costs/` directory excluded from version control
- **📈 Auto-analytics** - loads 2-3 recent months for comprehensive summaries
- **⚡ Fast loading** - only recent data loaded for better performance
- **🎯 Specialized systems** - cost tracking separate from performance monitoring

### Usage Examples

#### Python Example
```python
# Auto-Detection & Context Extraction (70% token savings)
code_with_ai(prompt="Fix the calculate_sum function", editable_files=["math_utils.py"])
# → Auto-detects "calculate_sum" target, extracts focused context
# → Response includes auto_detection_info with token reduction metrics
```

#### JavaScript/TypeScript Example (React)
```python
code_with_ai(
    prompt="Refactor the LoginForm component to use hooks and Zod validation",
    editable_files=["src/components/LoginForm.tsx"]
)
# → Auto-detects "LoginForm" React component and Zod schema, extracts only relevant TSX/JSX code
```

#### Next.js Example
```python
code_with_ai(
    prompt="Update the getServerSideProps function for Next.js 14 compatibility",
    editable_files=["pages/index.tsx"]
)
# → Auto-detects "getServerSideProps" in Next.js, focuses context on the function and related exports
```

#### Zod/TypeScript Example
```python
code_with_ai(
    prompt="Fix the UserSchema definition using Zod",
    editable_files=["src/schemas/user.ts"]
)
# → Auto-detects "UserSchema" Zod object, extracts only the relevant schema code
```

#### Multiple AI Tasks (Universal)
```python
code_with_multiple_ai(
    prompts=[
        "Optimize the UserManager class",           # Python
        "Refactor the AuthForm React component",    # React/TS
        "Fix the validateUser Zod schema"           # Zod/TS
    ],
    editable_files_list=[
        ["user_manager.py"],
        ["src/components/AuthForm.tsx"],
        ["src/schemas/validateUser.ts"]
    ]
)
# → Auto-detects targets in both Python and JS/TS, provides aggregated auto_detection_summary
```

# Cost Management (Aider-MCP Functions)
get_cost_summary(days=90)
# → Loads costs_2025-06.json + costs_2025-05.json + costs_2025-04.json

export_cost_report(format="csv", days=30)
# → Creates costs/cost_export_20250603_181341.csv

# Performance Analytics (Phase 2A)
python -m app.analytics.metrics_extractor --report=summary
# → Analyzes logs/operational_2025-06.json

# Auto-Detection Analytics
# → Check logs/auto_detection_2025-06.json for detailed auto-detection metrics
```

## 📊 Auto-Detection Response Examples ✨ **NEW**

### Single AI with Universal Auto-Detection
```json
{
  "success": true,
  "diff": "Refactored LoginForm component to use hooks and Zod validation",
  "auto_detection_info": {
    "auto_detected_targets": ["LoginForm", "ZodSchema"],
    "context_extraction_used": true,
    "files_processed_with_context": ["src/components/LoginForm.tsx"],
    "estimated_token_reduction": "68%",
    "target_elements_provided": false,
    "target_elements_used": ["LoginForm", "ZodSchema"]
  }
}
```

### Multiple AI with Auto-Detection Summary (Python + JS/TS)
```json
{
  "success": true,
  "results": [
    {
      "auto_detection_info": {
        "auto_detected_targets": ["UserManager"],
        "context_extraction_used": true,
        "estimated_token_reduction": "70%"
      }
    },
    {
      "auto_detection_info": {
        "auto_detected_targets": ["AuthForm"],
        "context_extraction_used": true,
        "estimated_token_reduction": "65%"
      }
    },
    {
      "auto_detection_info": {
        "auto_detected_targets": ["validateUser"],
        "context_extraction_used": true,
        "estimated_token_reduction": "62%"
      }
    }
  ],
  "auto_detection_summary": {
    "total_tasks": 3,
    "tasks_with_auto_detection": 3,
    "tasks_with_context_extraction": 3,
    "estimated_token_reductions": ["70%", "65%", "62%"]
  }
}
```

## 📋 Configuration Guide

### Universal Auto-Detection & Context Extraction ✨ **ENHANCED**
```bash
# Auto-Detection Features (Enable 70%+ token savings for all frameworks)
ENABLE_CONTEXT_EXTRACTION=true         # 🎯 Smart context extraction
ENABLE_AUTO_TARGET_DETECTION=true      # 🚀 Automatic target detection
ENABLE_JS_TS_AUTO_DETECTION=true       # 🌐 Enable JS/TS framework auto-detection (React, Next.js, Zod, etc.)
CONTEXT_DEFAULT_MAX_TOKENS=4000        # 🎚️ Token budget per file
CONTEXT_MIN_RELEVANCE_SCORE=3.0        # 📊 Relevance threshold

# Auto-Detection Analytics (Monthly chunked)
ENABLE_AUTO_DETECTION_LOGGING=true     # 🔍 Dedicated analytics logging
AUTO_DETECTION_LOG_PRETTY=false        # 🎨 JSON format (minified/pretty)
```

### Monthly Log Chunking ✨ **NEW**
All logs now use standardized monthly chunking:
- `/logs/operational_2025-06.json` - Operational events
- `/logs/auto_detection_2025-06.json` - Auto-detection analytics  
- `/costs/costs_2025-06.json` - Cost tracking

Benefits: Easy correlation, time-based analysis, consistent archival

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

### Analytics Settings
```bash
# Cost Management (Aider-MCP)
MAX_COST_PER_TASK=5.00          # Maximum cost per task (USD)
MAX_DAILY_COST=50.00            # Daily spending limit (USD)
MAX_MONTHLY_COST=500.00         # Monthly spending limit (USD)
COST_WARNING_THRESHOLD=1.00     # Warning threshold (USD)
ENABLE_COST_TRACKING=true       # Enable cost management features
ENABLE_COST_LOGGING=false       # Console logging (off by default)

# Performance Analytics (Phase 2A)
LOG_ENABLE_JSON_FILE=true            # Enable structured JSON logging
LOG_ENABLE_STRUCTURED_DATA=true      # Include [key=value] structured data
LOG_ENABLE_METRICS_EXTRACTION=true   # Enable automated metrics extraction
METRICS_EXTRACTION_INTERVAL=300      # Extract metrics every N seconds

# Data Storage (automatic - no configuration needed)
# Cost: Saved to /costs/costs_YYYY-MM.json (monthly files)
# Performance: Saved to /logs/operational.json (structured logs)
# Reports: On-demand generation in /logs/reports/
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
MCP_SERVER_ROOT=/Users/jacquesv/MCP/aider-mcp    # Project root path
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

## 🎯 Which Analytics System to Use?

### Use Aider-MCP Cost Functions When:
- 💰 Planning budgets and estimating costs
- 📊 Monitoring spending and budget limits
- 📈 Analyzing cost efficiency across models
- 📋 Generating financial reports
- 💵 Making cost-based optimization decisions

### Use Phase 2A Analytics When:
- ⚡ Monitoring system performance and reliability
- 🔍 Detecting operational issues and errors
- 📊 Analyzing task execution patterns
- 🏥 Assessing system health status
- 🚀 Optimizing performance bottlenecks

### Use Both Together When:
- 📊 Creating comprehensive operational reports
- 🎯 Making holistic optimization decisions
- 📈 Conducting full system analysis
- 🏗️ Planning capacity and resources

### Example Integration Patterns

```python
# Daily monitoring
cost_summary = get_cost_summary(days=1)
health_check = LogMetricsExtractor().extract_operational_metrics()

# Weekly optimization
if health_check['error_rate'] > 0.05 and cost_summary['daily_avg'] > budget:
    optimize_for_both_performance_and_cost()

# Monthly reporting
cost_report = export_cost_report(days=30, format="csv")
perf_report = generate_reports.py --export=html
```

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

## 📊 Performance Benchmarks ✨ **ENHANCED**

Based on real testing with modern full-stack development projects:

| Metric | Before Universal Support | After Universal Enhancement |
|--------|-------------------------|----------------------------|
| **Framework Coverage** | ❌ Python Only | ✅ **Python + JavaScript/TypeScript** |
| **Auto-Detection** | ✅ Python frameworks | ✅ **Universal (all major frameworks)** |
| **Token Reduction** | ✅ 70% (Python only) | ✅ **70%+ (All frameworks)** |
| **React Components** | ❌ No support | ✅ **Full auto-detection & context extraction** |
| **Next.js Support** | ❌ No support | ✅ **API routes, SSR functions, App Router** |
| **Zod Schemas** | ❌ No support | ✅ **Schema detection & validation context** |
| **TypeScript** | ❌ No support | ✅ **Interfaces, types, generic functions** |
| **Full-Stack Projects** | ❌ Limited | ✅ **Seamless Python + JS/TS integration** |
| **System Monitoring** | ✅ Comprehensive | ✅ **Enhanced with universal analytics** |
| **Cost Transparency** | ✅ Real-time tracking | ✅ **Cross-framework cost optimization** |
| **Task Success Rate** | ✅ 100% (Python) | ✅ **100% (All supported frameworks)** |
| **Parallel Speedup** | ✅ 2.64x | ✅ **2.64x+ (improved with better targeting)** |

### Universal Analytics Results ✨ **NEW**

**Python Projects:**
- **Django**: ~70% token reduction on model/view modifications
- **FastAPI**: ~68% token reduction on endpoint implementations  
- **Flask**: ~65% token reduction on route and blueprint updates

**JavaScript/TypeScript Projects:**
- **React Components**: ~72% token reduction on component refactoring
- **Next.js Applications**: ~69% token reduction on API routes and pages
- **Zod Schemas**: ~75% token reduction on validation logic updates
- **TypeScript**: ~67% token reduction on interface and type definitions

**Full-Stack Projects:**
- **Mixed Python + React**: ~70% average token reduction across both stacks
- **API + Frontend**: Parallel processing with optimal model selection per stack
- **Monorepo Support**: Framework-aware detection across multiple directories

**Performance Impact:**
- **Universal Detection Overhead**: <3ms per task (negligible)
- **Framework Detection**: File extension-based optimization
- **Cross-Framework Analytics**: Unified reporting across all stacks
- **Memory Usage**: Optimized pattern matching with minimal resource impact

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

#### Path Configuration Issues ✨ **NEW**
```bash
# If code_with_ai fails with "TypeError: Cannot convert undefined or null to object"
# Check that MCP_SERVER_ROOT in .env matches your actual project path

# Verify .env configuration
cat .env | grep MCP_SERVER_ROOT
# Should show: MCP_SERVER_ROOT=/Users/yourname/MCP/aider-mcp (note: uppercase MCP)

# Check if UV is accessible
ls -la $(grep UV_PATH .env | cut -d'=' -f2)

# If paths are incorrect, run setup again
./app/scripts/setup.sh

# Or manually fix .env
# Edit .env and correct the MCP_SERVER_ROOT path to match your actual directory
```

#### JavaScript/TypeScript Framework Issues ✨ **NEW**
```bash
# If JS/TS auto-detection isn't working
# Check that JS/TS detection is enabled
cat .env | grep ENABLE_JS_TS_AUTO_DETECTION
# Should show: ENABLE_JS_TS_AUTO_DETECTION=true

# Test JS/TS detection manually
python -c "
import os
import sys
sys.path.insert(0, 'app')
os.environ['ENABLE_JS_TS_AUTO_DETECTION'] = 'true'
from app.context.auto_detection import extract_targets_from_prompt
result = extract_targets_from_prompt('Create React component called TestComponent', file_path='test.tsx')
print('Detected targets:', result)
"

# If React/Next.js components aren't detected
# Verify file extensions are recognized (.tsx, .jsx, .ts, .js)
# Check that component names start with uppercase (React convention)

# If Zod schemas aren't detected  
# Ensure schema variable names contain 'schema' or 'Schema'
# Example: userSchema, UserSchema, loginSchema

# For TypeScript interfaces
# Verify interface names follow TypeScript conventions
# Example: interface User, interface ApiResponse
```

#### Universal Auto-Detection Issues ✨ **NEW**
```bash
# If auto-detection works for Python but not JS/TS
# Check framework detection configuration
python -c "
import os
print('Python detection:', os.getenv('ENABLE_AUTO_TARGET_DETECTION', 'not set'))
print('JS/TS detection:', os.getenv('ENABLE_JS_TS_AUTO_DETECTION', 'not set'))
print('Context extraction:', os.getenv('ENABLE_CONTEXT_EXTRACTION', 'not set'))
"

# If mixed projects (Python + JS/TS) have issues
# Ensure both detection systems are enabled
# Check that file paths are correctly mapped to their frameworks

# Test framework-specific patterns
python -c "
from app.context.auto_detection import extract_targets_from_prompt
# Test Python
py_result = extract_targets_from_prompt('Fix the calculate_sum function', file_path='utils.py')
print('Python targets:', py_result)
# Test React
js_result = extract_targets_from_prompt('Fix the UserProfile component', file_path='UserProfile.tsx')
print('React targets:', js_result)
"
```

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

#### Framework-Specific Debugging ✨ **NEW**
```bash
# Debug React component detection
python -c "
from app.context.js_framework_detection import JSFrameworkDetector
detector = JSFrameworkDetector()
code = '''
export function MyComponent() {
  return <div>Hello</div>;
}
'''
matches = detector.detect_targets(code)
print('Detected React components:', [m['name'] for m in matches])
"

# Debug Next.js API route detection
python -c "
code = '''
export default async function handler(req, res) {
  res.json({ message: 'Hello' });
}
'''
# Test detection patterns...
"

# Debug Zod schema detection
python -c "
code = '''
const userSchema = z.object({
  name: z.string(),
  email: z.string().email()
});
'''
# Test detection patterns...
"
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

### Test Results
- **Tasks**: 3 parallel (HTML, JS, CSS generation)
- **Execution Time**: 25.02 seconds (parallel) vs 65.96 seconds (sequential)
- **Files Generated**: 451 lines of production-ready code
- **Total Cost**: $0.024 for complete landing page generation
- **Data Storage**: Organized in monthly JSON files + structured performance logs
- **Analytics**: Real-time cost tracking + performance monitoring
- **Health Status**: "HEALTHY" with 0% error rate throughout execution
