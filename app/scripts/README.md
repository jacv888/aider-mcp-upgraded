# Aider MCP Scripts

This directory contains utility scripts for the Aider-MCP system.

## Scripts

### `backup_aider_history.py`
Pure backup and rotation functionality for Aider chat history.

**Features:**
- 🔄 **Smart Rotation** - Automatically rotates large files (>5MB) or old files (>30 days)
- 💾 **Timestamped Backups** - Creates organized backups with full history preservation
- 🗑️ **Cleanup Management** - Maintains organized backup archives
- 📊 **Backup Metrics** - Provides backup status for session bootstrap

**Usage:**
```python
from app.scripts.backup_aider_history import get_backup_metrics
metrics = get_backup_metrics()
```

### `aider_cost_analytics.py`
Cost analytics and metrics extraction from Aider history.

**Features:**
- 📊 **Cost Analytics Extraction** - Extracts session costs, model usage, and daily breakdowns
- 💰 **Savings Calculations** - Tracks optimization savings and token efficiency
- 📈 **Cost Reporting** - Generates cost summaries from historical data
- 🎯 **Target Element Tracking** - Monitors auto-detection optimization events

**Usage:**
```python
from app.scripts.aider_cost_analytics import get_cost_metrics
metrics = get_cost_metrics()
```

### `generate_claude_config.py`
Generates Claude Desktop configuration files.

### `setup.sh`
One-command setup script for the entire Aider-MCP system.

### `update_claude_config.py`
Updates existing Claude Desktop configuration.

### `verify_github_setup.py`
Verifies GitHub integration setup.

## Integration

These scripts are integrated into the session bootstrap system:

```python
from app.context.session_bootstrap import bootstrap_session
bootstrap_session()
```

This provides comprehensive metrics including backup status, cost analytics, and auto-detection performance for the AI coding session initialization.
