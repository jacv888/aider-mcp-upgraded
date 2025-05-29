---
name: 🐛 Bug Report
about: Create a report to help us improve Aider-MCP
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ['jacv888']

---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Run command '....'
3. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## ❌ Actual Behavior
A clear and concise description of what actually happened.

## 📊 Environment
- **OS**: [e.g. macOS 13.0, Ubuntu 20.04, Windows 11]
- **Python Version**: [e.g. 3.9.7]
- **Aider-MCP Version**: [e.g. 2.0.0]
- **AI Models Used**: [e.g. GPT-4, Claude 3.5 Sonnet]

## 🛡️ Resilience Status
- [ ] Resilience features installed (`python3 install_resilience.py --install`)
- [ ] Resource monitoring active
- [ ] Connection health monitoring enabled
- **Max Concurrent Tasks**: [e.g. 3]
- **CPU Threshold**: [e.g. 75%]
- **Memory Threshold**: [e.g. 80%]

## 📋 Configuration
```bash
# Paste relevant parts of your .env configuration (WITHOUT API keys)
MAX_CONCURRENT_TASKS=3
CPU_USAGE_THRESHOLD=75.0
# etc...
```

## 📝 Logs
```
Paste relevant error messages or logs here
```

## 🎯 Additional Context
Add any other context about the problem here.

## 🧪 Have you tried?
- [ ] Restarting the MCP server
- [ ] Running resilience test (`python tests/multi-ai-2/resilience-test.py`)
- [ ] Checking resource usage
- [ ] Updating to latest version
