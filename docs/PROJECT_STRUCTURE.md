# 📁 Aider-MCP Project Structure

## 🎯 Main Project Files
```
aider-mcp/
├── 📄 README.md                    # Main documentation
├── ⚙️ aider_mcp.py                # Enhanced MCP server with resilience
├── 🧠 strategic_model_selector.py # Intelligent model selection
├── 🛡️ aider_mcp_resilience.py    # Resilience components
├── 🔧 resilience_config.py        # Configuration management
├── 🔌 aider_adapter.py            # Aider integration layer
├── 🎯 aider_ai_code.py           # Core AI coding functions
├── 🚀 install_resilience.py       # Installation script
├── 📋 requirements.txt            # Python dependencies
├── 🔐 .env.example               # Environment template
└── 🗂️ aider-mcp.code-workspace  # VS Code workspace
```

## 📚 Documentation (`/docs/`)
```
docs/
├── ⚙️ CONFIG-PRIORITY.md          # Configuration system guide
├── 🛡️ RESILIENCE_GUIDE.md        # Stability features guide  
├── 🧠 STRATEGIC-MODEL-SELECTION.md # Model selection guide
├── 📋 ENHANCEMENT_SUMMARY.md      # All improvements summary
├── ✅ INSTALLATION_COMPLETE.md    # Installation verification
└── 📖 README.md                   # Documentation index
```

## 🗃️ Reference Files (`/reference/`)
```
reference/
├── 🔧 aider_mcp_enhanced.py      # Alternative implementation
├── ⚙️ .env.resilience            # Resilience config example
└── 📋 resilience_config.ini      # Legacy config format
```

## 💾 Backup Files (`/backup/`)
```
backup/
└── 📄 aider_mcp.py.bak           # Original server backup
```

## 📊 Logs (`/logs/`)
```
logs/
└── 📋 aider_mcp.log              # Server operation logs
```

## 🧪 Tests (`/tests/`)
```
tests/
├── 📁 multi-ai/                  # Original test results
├── 📁 multi-ai-2/                # Resilience test results
│   ├── 🎯 RESILIENCE_TEST_REPORT.md
│   ├── 🛡️ resilience-test.py
│   └── 📄 Generated test files...
└── 🧪 test_multiple_ai.py        # Test suite
```

## 🔐 Security & Configuration
- ✅ **API keys secured** - Removed from .env, added to .env.example
- ✅ **Sensitive files ignored** - Updated .gitignore
- ✅ **Environment template** - .env.example for users
- ✅ **Backup files organized** - Moved to /backup/
- ✅ **Logs centralized** - Moved to /logs/

## 🎯 Visible Main Files Only
The project root now contains only the essential files users need:
- Core server files
- Configuration templates  
- Documentation entry point
- Installation script

All backup, reference, and test files are properly organized in subdirectories.
