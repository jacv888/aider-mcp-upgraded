#!/usr/bin/env python3
"""
🔄 Claude Desktop Config Auto-Updater for Aider-MCP
Automatically updates the Claude Desktop configuration with the correct
aider-mcp server settings from .env file.

Usage:
    python app/scripts/update_claude_config.py
    
This will automatically update your Claude Desktop config file.
"""

import os
import sys
import json
import platform
from pathlib import Path
from dotenv import load_dotenv


def get_claude_config_path():
    """
    Get Claude Desktop configuration file path based on operating system.
    
    Returns:
        Path: Path to claude_desktop_config.json
    """
    system = platform.system().lower()
    home = Path.home()
    
    if system == "darwin":  # macOS
        return home / "Library/Application Support/Claude/claude_desktop_config.json"
    elif system == "windows":  # Windows
        return home / "AppData/Roaming/Claude/claude_desktop_config.json"
    elif system == "linux":  # Linux
        # Try XDG config first, fall back to .config
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "claude/claude_desktop_config.json"
        else:
            return home / ".config/claude/claude_desktop_config.json"
    else:
        raise OSError(f"Unsupported operating system: {system}")


# Get the project root directory
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

# Load environment variables from .env
if env_file.exists():
    load_dotenv(env_file)
else:
    print(f"❌ Error: .env file not found at {env_file}")
    sys.exit(1)

# Get configuration values from environment
mcp_server_root = os.getenv("MCP_SERVER_ROOT", str(project_root))
mcp_entry_point = os.getenv("MCP_SERVER_ENTRY_POINT", "app/core/aider_mcp.py")
uv_path = os.getenv("UV_PATH", "/Users/jacquesv/.local/bin/uv")

# Claude Desktop config file path (cross-platform)
# Check for custom path first
custom_config_path = os.getenv("CLAUDE_CONFIG_PATH")
if custom_config_path:
    claude_config_path = Path(custom_config_path)
    print(f"📁 Using custom Claude config path: {claude_config_path}")
else:
    try:
        claude_config_path = get_claude_config_path()
        print(f"📁 Detected Claude config path for {platform.system()}: {claude_config_path}")
    except OSError as e:
        print(f"❌ Error: {e}")
        print("💡 You can override the path by setting CLAUDE_CONFIG_PATH environment variable.")
        sys.exit(1)

if not claude_config_path.exists():
    print(f"❌ Error: Claude Desktop config not found at {claude_config_path}")
    print(f"💡 Expected location for {platform.system()}: {claude_config_path}")
    print("💡 Make sure Claude Desktop is installed and has been run at least once.")
    print("💡 Alternative locations to check:")
    
    # Show alternative paths based on OS
    system = platform.system().lower()
    if system == "darwin":
        print("   - ~/Library/Application Support/Claude/claude_desktop_config.json")
    elif system == "windows": 
        print("   - %APPDATA%/Claude/claude_desktop_config.json")
        print("   - C:/Users/[username]/AppData/Roaming/Claude/claude_desktop_config.json")
    elif system == "linux":
        print("   - ~/.config/claude/claude_desktop_config.json")
        print("   - $XDG_CONFIG_HOME/claude/claude_desktop_config.json")
    
    sys.exit(1)

try:
    # Read existing config
    with open(claude_config_path, 'r') as f:
        config = json.load(f)
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Update aider-mcp configuration
    config["mcpServers"]["aider-mcp"] = {
        "command": "/bin/sh",
        "args": [
            "-c",
            f"cd {mcp_server_root} && PYTHONPATH={mcp_server_root} {uv_path} run --with mcp[cli] mcp run {mcp_entry_point}"
        ]
    }
    
    # Write back the updated config
    with open(claude_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Successfully updated Claude Desktop configuration!")
    print()
    print("📁 Configuration Details:")
    print(f"   Server Root: {mcp_server_root}")
    print(f"   Entry Point: {mcp_entry_point}")
    print(f"   UV Path: {uv_path}")
    print()
    print("🔄 Next Steps:")
    print("   1. Restart Claude Desktop application")
    print("   2. The aider-mcp server should connect automatically")
    print("   3. You should see aider-mcp tools available in Claude")

except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in Claude config file: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error updating config: {e}")
    sys.exit(1)
