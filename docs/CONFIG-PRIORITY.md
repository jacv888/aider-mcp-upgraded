# Aider Configuration Priority

## Environment Variable Loading Order

The aider integration now loads environment variables in this priority order:

### 1. **PRIMARY SOURCE** (Highest Priority)
**Location**: `/Users/jacquesv/MCP/aider-mcp/.env`
- This is your master configuration file
- Settings here OVERRIDE all other sources
- Edit this file for global aider settings

### 2. **Global Aider Config** (Medium Priority)  
**Location**: `~/.config/aider/.env`
- Standard aider global configuration
- Only used if variables are not set in primary source

### 3. **Project-Specific** (Lowest Priority)
**Location**: `[working-directory]/.env`
- Project-specific overrides
- Only used if variables are not set in higher priority sources

## Key Benefits

✅ **Centralized Control**: All your aider settings in one place
✅ **Override Capability**: Primary source always wins
✅ **Project Flexibility**: Can still override per-project if needed
✅ **Single Source of Truth**: `/Users/jacquesv/MCP/aider-mcp/.env`

## Usage

1. **Edit primary config**: Modify `/Users/jacquesv/MCP/aider-mcp/.env`
2. **API keys**: Set once in primary config, works everywhere
3. **Model selection**: Change `AIDER_MODEL` in primary config
4. **Project overrides**: Create `.env` in specific projects only if needed

## Example

```bash
# Primary config (/Users/jacquesv/MCP/aider-mcp/.env)
OPENAI_API_KEY=your-global-key
AIDER_MODEL=gpt-4-turbo

# Project override (optional: /path/to/project/.env)
AIDER_MODEL=claude-3.5-sonnet  # Only for this project
```
