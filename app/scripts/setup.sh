#!/bin/bash
# 🚀 Aider-MCP One-Click Setup Script
# Automates the complete setup process for Aider-MCP with Claude Desktop

set -e  # Exit on any error

echo "🚀 Aider-MCP Setup Script"
echo "========================"
echo

# Check if we're in the right directory
if [[ ! -f "main.py" ]] || [[ ! -d "app" ]]; then
    echo "❌ Error: Please run this script from the aider-mcp project root directory"
    echo "💡 Usage: cd aider-mcp && ./scripts/setup.sh"
    exit 1
fi

# Get the absolute path of the project
PROJECT_ROOT=$(pwd)
echo "📁 Project Root: $PROJECT_ROOT"

# Check if .env exists
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        echo "📋 Creating .env from .env.example..."
        cp .env.example .env
    else
        echo "❌ Error: No .env or .env.example file found"
        exit 1
    fi
fi

# Update .env with correct paths
echo "🔧 Updating .env with current project paths..."

# Update MCP_SERVER_ROOT in .env
if grep -q "^MCP_SERVER_ROOT=" .env; then
    sed -i.bak "s|^MCP_SERVER_ROOT=.*|MCP_SERVER_ROOT=$PROJECT_ROOT|" .env
elif grep -q "PLACEHOLDER_PROJECT_ROOT" .env; then
    sed -i.bak "s|PLACEHOLDER_PROJECT_ROOT|$PROJECT_ROOT|" .env
else
    echo "MCP_SERVER_ROOT=$PROJECT_ROOT" >> .env
fi

# Find UV path
UV_PATH=$(which uv 2>/dev/null || echo "/Users/$(whoami)/.local/bin/uv")
if [[ ! -f "$UV_PATH" ]]; then
    echo "⚠️  Warning: UV not found at $UV_PATH"
    echo "💡 Please install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "📝 Or update UV_PATH in .env manually"
else
    echo "✅ Found UV at: $UV_PATH"
    if grep -q "^UV_PATH=" .env; then
        sed -i.bak "s|^UV_PATH=.*|UV_PATH=$UV_PATH|" .env
    elif grep -q "PLACEHOLDER_UV_PATH" .env; then
        sed -i.bak "s|PLACEHOLDER_UV_PATH|$UV_PATH|" .env
    else
        echo "UV_PATH=$UV_PATH" >> .env
    fi
fi

# Check for API keys
echo
echo "🔐 Checking API Keys..."
missing_keys=()

if ! grep -q "^ANTHROPIC_API_KEY=sk-" .env; then
    missing_keys+=("ANTHROPIC_API_KEY")
fi
if ! grep -q "^OPENAI_API_KEY=sk-" .env; then
    missing_keys+=("OPENAI_API_KEY") 
fi
if ! grep -q "^GEMINI_API_KEY=.*" .env; then
    missing_keys+=("GEMINI_API_KEY")
fi

if [[ ${#missing_keys[@]} -gt 0 ]]; then
    echo "⚠️  Missing API Keys: ${missing_keys[*]}"
    echo "📝 Please add your API keys to .env file before proceeding"
    echo "💡 Edit .env and add your keys, then run: python app/scripts/update_claude_config.py"
else
    echo "✅ All required API keys found"
    
    # Auto-update Claude config
    echo
    echo "🔄 Updating Claude Desktop configuration..."
    if python app/scripts/update_claude_config.py; then
        echo
        echo "🎉 Setup Complete!"
        echo "=================="
        echo "✅ Project paths configured in .env"
        echo "✅ Claude Desktop config updated"
        echo "✅ All API keys present"
        echo
        echo "🔄 Next Steps:"
        echo "   1. Restart Claude Desktop application"
        echo "   2. The aider-mcp server should connect automatically"
        echo "   3. Start using aider-mcp tools in Claude!"
    else
        echo "❌ Failed to update Claude config automatically"
        echo "💡 Run manually: python app/scripts/update_claude_config.py"
    fi
fi

echo
echo "📋 Configuration Summary:"
echo "   Project: $PROJECT_ROOT"
echo "   UV Path: $UV_PATH"
echo "   .env file: ✅ Updated"

# Clean up backup files
rm -f .env.bak 2>/dev/null || true
