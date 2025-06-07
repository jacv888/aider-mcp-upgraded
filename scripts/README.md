# Aider Chat History Management

This directory contains tools for managing and archiving your `.aider.chat.history.md` file with cost analytics extraction.

## Scripts

### `backup_aider_history.py`
Intelligent backup, rotation, and cost analytics tool for Aider chat history.

**Features:**
- 📊 **Cost Analytics Extraction** - Extracts session costs, model usage, and daily breakdowns
- 🔄 **Smart Rotation** - Automatically rotates large files (>5MB) or old files (>30 days)
- 💾 **Timestamped Backups** - Creates organized backups with full history preservation
- 🗑️ **Cleanup Management** - Maintains 10 most recent backups automatically
- 📈 **Cost Reporting** - Generates cost summaries from historical data

**Usage:**
```bash
# Basic usage (uses default workspace)
python3 scripts/backup_aider_history.py

# Custom workspace
python3 scripts/backup_aider_history.py /path/to/your/workspace

# Make executable and run directly
chmod +x scripts/backup_aider_history.py
./scripts/backup_aider_history.py
```

**Output Structure:**
```
ai-logs/
├── aider-history-archive/     # Archived history files
│   ├── aider_history_2025-06-07_15-30-45.md
│   └── aider_history_2025-06-06_12-20-30.md
└── aider-analytics/           # Extracted cost analytics
    ├── aider_analytics_2025-06-07_15-30-45.json
    └── aider_analytics_2025-06-06_12-20-30.json
```

**Integration with Existing Project:**
- Integrates with existing `ai-logs/` directory structure
- Compatible with operational and auto-detection logs
- Uses same backup patterns as project Context Management Protocol

## Automation Recommendations

### Weekly Backup (Cron)
```bash
# Add to crontab (run every Sunday at 2 AM)
0 2 * * 0 cd /Users/jacquesv/MCP/aider-mcp && python3 scripts/backup_aider_history.py
```

### Monthly Rotation
```bash
# Force rotation monthly (first day of month at 1 AM)
0 1 1 * * cd /Users/jacquesv/MCP/aider-mcp && python3 scripts/backup_aider_history.py
```

### Pre-Task Health Check
```bash
# Check before starting major AI coding tasks
python3 scripts/backup_aider_history.py && echo "Ready for AI coding!"
```

## Cost Analytics Features

The extracted analytics include:
- **Total sessions and costs** per backup period
- **Model usage breakdown** (which models used how often)
- **Daily cost patterns** for budget tracking
- **Date ranges** for historical analysis
- **Session summaries** for audit purposes

This data can be used for:
- Budget planning and cost forecasting
- Model performance analysis
- Historical usage patterns
- Compliance and audit requirements

## Integration with Health Monitoring

The backup script complements the existing health monitoring system:
- Uses same directory structure (`ai-logs/`)
- Provides historical cost data for trend analysis
- Maintains audit trail for system changes
- Enables long-term operational insights
