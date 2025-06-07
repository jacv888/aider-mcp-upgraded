# 🚨 Bootstrap & Context Management Module

*Load this once at session start, then focus on core coding workflow*
{MCP_SERVER_ROOT}=/Users/user/mcps/aider-mcp-upgraded/

## 🔄 PRIORITY: Session Initialization

**FIRST ACTION**: Activate Desktop Context Management Protocol (see attached document)
- **README.md**: Ingest→Build→Prepare (understand project context)
- **Load project context** from: `{MCP_SERVER_ROOT}/ai-logs/active`
- **Display real metrics** via bootstrap template
- **Report** current project status and measured optimization performance
- **Ready** system for auto-detection optimization (70% token savings confirmed)
- **Pre-Task Health Check**:
 ```bash
 # Backup Aider history and extract cost analytics
 python3 scripts/backup_aider_history.py && echo "History backed up - Ready for AI coding!"
 ```

---

## **FIRST ACTION**: Session Bootstrap

**User Command: "BOOTSTRAP SESSION"**

### **Mandatory Initialization Sequence:**
1. **Environment Setup**: Load `MCP_SERVER_ROOT` from `.env`
2. **Context Loading**: Check `${MCP_SERVER_ROOT}/ai-logs/active` for project logs
3. **Health Check**: Validate system status and cost tracking
4. **Template Generation**: Extract real metrics (no placeholders allowed)
5. **Ready State**: Report current project and optimization status

### **Bootstrap Commands:**
```bash
# Generate real data template (mandatory)
python3 app/scripts/bootstrap_with_template.py

# Backup and cost analytics
python3 scripts/backup_aider_history.py && echo "Ready for AI coding!"

# Validate template (no placeholders)
python3 app/scripts/validate_template.py bootstrap_template_output.md
```

### **Expected Bootstrap Output Format:**
```
🔄 Context Loading...
📂 Found: {WORKSPACE_DIR}/ai-logs/active/[latest].md
📋 Last activity: [Previous session summary]

💾 Aider History Status...
📊 Backed up: [X] sessions, $[X] total cost
📏 Current size: [X]MB (healthy)
🏥 System Health: [healthy/degraded/unhealthy]

💰 Costs: $[X] today, $[X] this month
⚡ Savings: $[X] estimated savings this month ([X]% efficiency)
🎯 Target elements identified: [X] functions/classes
🚀 Token efficiency: Strategic model selection working ([X] sessions optimized)

⚡ Auto-Detection Performance (Real Metrics) ⚡
--------------------------------------------------
📊 Total Optimizations: [X] (measured)
🎯 Average Token Reduction: [X]% (measured)
🔧 Elements Detected: [X] (measured)
📅 Sessions Today: Active development ongoing
✅ Ready to continue with [project-name]
```

---

## 🔄 Context Management

### **Environment Configuration**
```bash
# From your .env file:
MCP_SERVER_ROOT=/Users/yourname/your-project-path

# Directory structure:
${MCP_SERVER_ROOT}/
├── ai-logs/
│   ├── active/           # Current project logs
│   ├── archive/          # Completed projects
│   └── .context         # Project metadata
└── .env                  # Configuration
```

### **Session Context Loading**
1. Load workspace from `MCP_SERVER_ROOT` environment variable
2. Check for active logs: `list_directory(${MCP_SERVER_ROOT}/ai-logs/active)`
3. Find project context matching current directory
4. Load latest log and extract current focus
5. Report what was loaded and project status

### **Log File Management**
- **File naming**: `YYYY-MM-DD_HH-MM_{PROJECT_NAME}.md`
- **Auto-rotation**: When log exceeds 50KB or user says "NEW PROJECT"
- **Context preservation**: Keep last 2-3 result entries when rotating

---

## 🛡️ Validation & Error Handling

### **Zero Tolerance for Placeholders**
❌ **Never use**: `[X]`, `[latest]`, `$0.43 today`, `143 sessions`
✅ **Always use**: Real data from analytics scripts and system checks

### **Template Validation Pipeline**
```bash
# Must pass 100/100 validation score
python3 app/scripts/validate_template.py [template_file]

# Auto-blocks any placeholder data
# Generates audit trail for accountability
```

### **Error Recovery**
- **Missing files**: Auto-create directory structure
- **Corrupted logs**: Create backup, start fresh with note
- **Environment issues**: Fallback to current directory with warning
- **Permission problems**: Report error, suggest manual creation

---

## 📋 User Commands

| Command | Action |
|---------|--------|
| `BOOTSTRAP SESSION` | Complete initialization with protocol enforcement |
| `NEW PROJECT: {name}` | Start fresh log for new project |
| `ARCHIVE LOG` | Move current to archive, start new |
| `LOAD PROJECT: {name}` | Switch to different project context |
| `STATUS` | Show current log file and project state |

---

## 📊 Cost & Performance Monitoring

### **Real Data Analytics**
```bash
# Extract actual spending from your usage
python3 app/scripts/aider_cost_analytics.py

# System health with real metrics
get_system_health()

# Backup session history
python3 app/scripts/backup_aider_history.py
```

### **Success Metrics Tracking**
- Token optimization rates (target: 70% reduction)
- Element specificity in prompts (target: >90%)
- Session cost trends and budget adherence
- Auto-detection trigger rates

---

**This module loads once per session. After bootstrap, focus shifts to core coding workflow with DC + Aider optimization.**