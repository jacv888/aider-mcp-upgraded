#!/bin/bash
# Quick Bootstrap Commands
# Add these to your shell profile for easy access

# Use MCP_SERVER_ROOT env var or fallback to current directory
MCP_ROOT="${MCP_SERVER_ROOT:-$PWD}"

# Alias for quick bootstrap
alias bootstrap="cd \"$MCP_ROOT\" && python3 app/scripts/complete_bootstrap.py"

# Alias for bootstrap validation
alias check-bootstrap="cd \"$MCP_ROOT\" && python3 app/scripts/validate_bootstrap.py --check"

# Alias for enforced validation
alias require-bootstrap="cd \"$MCP_ROOT\" && python3 app/scripts/validate_bootstrap.py --enforce"

# Function for AI coding with automatic bootstrap
ai-code() {
    cd "$MCP_ROOT"
    
    # Automatically ensure bootstrap is complete
    if ! python3 app/scripts/validate_bootstrap.py --enforce; then
        echo "🔧 Running automatic bootstrap..."
        python3 app/scripts/complete_bootstrap.py
    fi
    
    echo "✅ Bootstrap validated - ready for AI coding!"
}

# Function to check system status before coding
status-check() {
    cd "$MCP_ROOT"
    echo "📊 System Status Check:"
    python3 app/scripts/validate_bootstrap.py --check
    # Add health check if available
    # get_system_health() 
}

# Add to your ~/.bashrc or ~/.zshrc:
# source "$MCP_ROOT/app/scripts/bootstrap_aliases.sh"
