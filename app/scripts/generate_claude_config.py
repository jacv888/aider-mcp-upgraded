#!/usr/bin/env python3
"""
🔧 Claude Desktop Config Generator for Aider-MCP
Generates the correct aider-mcp server configuration for Claude Desktop
by reading values from .env file.

Usage:
    python app/scripts/generate_claude_config.py
    
This will output the correct configuration block that you can copy-paste
into your Claude Desktop config file.
"""

import os
import sys
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

# Generate the configuration
claude_config = f'''    "aider-mcp": {{
      "command": "/bin/sh",
      "args": [
        "-c",
        "cd {mcp_server_root} && PYTHONPATH={mcp_server_root} {uv_path} run --with mcp[cli] --with python-dotenv --with psutil --with tiktoken --with httpx mcp run {mcp_entry_point}"
      ]
    }}'''

print("🔧 Aider-MCP Configuration for Claude Desktop")
print("=" * 50)
print()
print("📁 Configuration Details:")
print(f"   Server Root: {mcp_server_root}")
print(f"   Entry Point: {mcp_entry_point}")
print(f"   UV Path: {uv_path}")
print()
print("📋 Add this configuration to your Claude Desktop config:")

# Get the config path for the current platform
custom_config_path = os.getenv("CLAUDE_CONFIG_PATH")
if custom_config_path:
    config_file_path = custom_config_path
else:
    try:
        config_file_path = str(get_claude_config_path())
    except OSError:
        config_file_path = "your Claude Desktop config file"

print(f"   File: {config_file_path}")
print()
print("🔧 Configuration Block:")
print(claude_config)
print()
print("💡 Tips:")
print("   1. Copy the configuration block above")
print("   2. Add it to the 'mcpServers' section of your Claude config")
print("   3. Restart Claude Desktop")
print("   4. The aider-mcp server should connect successfully")
