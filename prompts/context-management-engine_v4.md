# Claude Desktop Context Management Protocol v4

## Core Principle
Maintain project context across Claude conversations using simple, reliable file operations that work with Desktop Commander capabilities.

## 1. Directory Structure
```
{LOG_DIR}/
├── active/           # Current project logs
├── archive/          # Completed/old logs
└── .context         # Simple project metadata
```
**Default {LOG_DIR}**: /Users/name/mcp/aider-mcp/ai-logs

## 2. File Naming Convention
```
YYYY-MM-DD_HH-MM_{PROJECT_NAME}.md
```
**Examples:**
- `2025-06-06_09-15_meeting_analytics.md`
- `2025-06-06_14-30_user_auth_system.md`

## 3. Session Bootstrap

### Auto-Initialization Steps:
1. **Check for active logs**: `list_directory({LOG_DIR}/active)`
2. **Find project context**: Look for logs matching current working directory name or ask user
3. **Load latest log**: Read most recent file for the project
4. **Report status**: Always state what was loaded and why

### Bootstrap Template:
```
🔄 Context Loading...
📂 Found: {LOG_DIR}/active/2025-06-06_09-15_meeting_analytics.md
📋 Last activity: User requested API endpoint debugging
✅ Ready to continue with meeting-analytics project
```

## 4. Log File Structure (Optimized for Claude)

### File Header:
```markdown
# Project: {PROJECT_NAME}
**Started**: {TIMESTAMP}
**Last Updated**: {TIMESTAMP}
**Status**: Active | Archived | Paused

## Quick Context
{2-3 sentence project summary}

## Current Focus
{What we're working on right now}

---
```

### Entry Format:
```markdown
## {TIME} - {BRIEF_TOPIC}
**Request**: {One sentence user goal}
**Action**: {What Claude did}
**Result**: {Key outcome/files changed}
**Next**: {Logical next step if any}

{Optional details if important for future context}

---
```

## 5. Smart Rotation (User-Controlled)

### Manual Triggers:
- User says "NEW PROJECT: {name}" or "START FRESH"
- Current log exceeds 50KB
- User explicitly requests: "Archive this and start new log"

### Rotation Process:
1. **Move current log**: `{LOG_DIR}/active/{file}` → `{LOG_DIR}/archive/{file}`
2. **Create new log**: With proper header and brief context from previous
3. **Preserve key context**: Copy last 2-3 **Result** entries as "Previous Context"

### Auto-Rotation Hints:
Claude suggests rotation when:
- Log file becomes very long (>200 entries)
- Topic shifts significantly from original project
- User starts working on unrelated features

## 6. Context Compaction (Claude-Driven)

### When Reading Large Logs:
1. **Scan full file** but **summarize old sections** in memory
2. **Preserve last 20 entries** in full detail
3. **Extract key decisions/outcomes** from older entries
4. **Create working summary** for current session

### Compaction Template:
```markdown
## Archived Summary (Auto-generated {DATE})
**Project Phase**: {Description}
**Key Decisions**:
- {Decision 1 with brief context}
- {Decision 2 with brief context}
**Important Files**: {List of main files worked on}
**Last Known State**: {Where things were left}

---
{Continue with recent detailed entries...}
```

## 7. User Commands (Simple Overrides)

| Command | Action |
|---------|--------|
| `NEW PROJECT: {name}` | Start fresh log for new project |
| `ARCHIVE LOG` | Move current to archive, start new |
| `LOAD PROJECT: {name}` | Switch to different project context |
| `SUMMARIZE LOG` | Get condensed view of current log |
| `STATUS` | Show current log file and project state |

## 8. Error Handling (Realistic)

### Common Issues:
- **Directory not found**: Create directory /ai-logs, /ai-logs/active & /ai-logs/archive
- **File not found**: Create new log automatically
- **Permission denied**: Report error, suggest manual file creation
- **Disk space**: Warn and suggest archiving old logs
- **Corrupted log**: Create backup, start fresh with note

### Error Template:
```
⚠️ Log Error: {specific issue}
🔧 Fallback: {what Claude is doing instead}
💡 Suggestion: {how user can fix if needed}
```

## 9. Implementation Workflow

### Session Start:
```python
# 1. Check for existing project context
logs = list_directory(f"{LOG_DIR}/active")

# 2. Find relevant log (by name similarity or ask user)
current_log = find_or_create_project_log(project_name)

# 3. Read and summarize for context
content = read_file(current_log)
context = summarize_for_context(content)

# 4. Report to user
print(f"📋 Loaded context from: {current_log}")
print(f"🎯 Current focus: {extract_current_focus(content)}")
```

### After Each Exchange:
```python
# Append new entry
log_entry = format_log_entry(user_request, claude_response, outcomes)
write_file(current_log, log_entry, mode="append")
```

## 10. Success Metrics

### Effectiveness Indicators:
- **Context retention**: Can Claude resume work seamlessly?
- **File size management**: Logs stay under 50KB before rotation
- **User effort**: Zero manual file management required
- **Error recovery**: System works even when files are missing/corrupted

### Quality Checks:
- Log entries are scannable and informative
- Project context is preserved across sessions
- Old information is archived but not lost
- New users can understand project state from logs

## 11. Best Practices

### For Claude:
- **Always read logs first** before responding to new requests
- **Summarize rather than reproduce** when logs are long
- **Ask for clarification** if project context is unclear
- **Suggest rotation** when logs become unwieldy

### For Users:
- **Use descriptive project names** for easier log identification
- **Say "NEW PROJECT"** when switching to unrelated work
- **Confirm project name** if Claude asks (helps with accuracy)
- **Don't edit logs manually** (Claude handles all updates)