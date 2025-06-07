#!/usr/bin/env python3
"""
Aider Chat History Backup and Rotation Script

Provides intelligent backup and rotation for .aider.chat.history.md
Integrates with existing ai-logs directory structure for consistency.
"""
import os
import sys
import shutil
import argparse # Import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv # Import load_dotenv

def _get_workspace_dir() -> Path:
    """
    Loads the workspace directory from the MCP_SERVER_ROOT environment variable.
    Falls back to the current working directory if not found.
    """
    load_dotenv() # Load environment variables from .env file
    workspace_root = os.getenv("MCP_SERVER_ROOT")
    if workspace_root:
        print(f"Using workspace from MCP_SERVER_ROOT: {workspace_root}")
        return Path(workspace_root)
    else:
        current_dir = Path.cwd()
        print(f"MCP_SERVER_ROOT not set, using current working directory: {current_dir}")
        return current_dir

class AiderHistoryManager:
    """Manages Aider chat history backups and rotation."""
    
    def __init__(self, workspace_dir: Path = None):
        self.workspace_dir = workspace_dir if workspace_dir is not None else _get_workspace_dir()
        self.aider_history_file = self.workspace_dir / ".aider.chat.history.md"
        self.backup_dir = self.workspace_dir / "ai-logs" / "aider-history-archive"
        
        # Create directories if they don't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def should_rotate(self, max_size_mb: float = 5.0, max_age_days: int = 30) -> bool:
        """Check if the history file should be rotated based on size or age."""
        if not self.aider_history_file.exists():
            return False
        
        # Check file size
        size_mb = self.aider_history_file.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            print(f"📏 File size ({size_mb:.1f}MB) exceeds threshold ({max_size_mb}MB)")
            return True
        
        # Check file age  
        age_days = (datetime.now().timestamp() - self.aider_history_file.stat().st_mtime) / (24 * 3600)
        if age_days > max_age_days:
            print(f"📅 File age ({age_days:.1f} days) exceeds threshold ({max_age_days} days)")
            return True
        
        return False
    
    def create_backup(self) -> str:
        """Create a timestamped backup of the history file."""
        if not self.aider_history_file.exists():
            print("📝 No .aider.chat.history.md file found to backup.")
            return ""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"aider_history_{timestamp}.md"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Create backup
            shutil.copy2(self.aider_history_file, backup_path)
            print(f"💾 Backup created: {backup_path}")
            
            # Get file size for reporting
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            print(f"📏 Backup size: {size_mb:.2f}MB")
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise
    
    def rotate_history(self, keep_recent_entries: int = 50) -> bool:
        """Rotate the history file, keeping only recent entries."""
        if not self.aider_history_file.exists():
            print("📝 No .aider.chat.history.md file found to rotate.")
            return False

        try:
            # Create backup first
            backup_path = self.create_backup()
            if not backup_path: # If backup failed or no file to backup
                return False
            
            # Read current file
            with open(self.aider_history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find session boundaries (lines starting with "# aider chat started")
            session_starts = []
            for i, line in enumerate(lines):
                if line.startswith("# aider chat started"):
                    session_starts.append(i)
            
            if len(session_starts) <= keep_recent_entries:
                print(f"📝 Only {len(session_starts)} sessions found, no rotation needed")
                return False
            
            # Keep only the last N sessions
            keep_from_line = session_starts[-keep_recent_entries]
            new_content = "".join(lines[keep_from_line:])
            
            # Write truncated file
            with open(self.aider_history_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            old_sessions = len(session_starts)
            new_size_mb = self.aider_history_file.stat().st_size / (1024 * 1024)
            
            print(f"✂️ Rotated: {old_sessions} → {keep_recent_entries} sessions")
            print(f"📏 New size: {new_size_mb:.2f}MB")
            print(f"💾 Full history preserved in: {backup_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Rotation failed: {e}")
            return False
    
    def cleanup_old_backups(self, keep_backups: int = 10) -> None:
        """Remove old backup files, keeping only the most recent ones."""
        try:
            backup_files = sorted(
                [f for f in self.backup_dir.glob("aider_history_*.md")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if len(backup_files) <= keep_backups:
                print(f"🗂️ Only {len(backup_files)} backups found, no cleanup needed")
                return
            
            # Remove old backups
            removed_count = 0
            for backup_file in backup_files[keep_backups:]:
                backup_file.unlink()
                removed_count += 1
            
            print(f"🗑️ Cleaned up {removed_count} old backups (keeping {keep_backups} most recent)")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    def get_backup_metrics(self) -> Dict[str, Any]:
        """
        Analyzes the backup directory and history file to provide metrics.
        Returns a dictionary with backed_up_sessions count, current_backup_size_mb,
        and backup_health status.
        """
        metrics = {
            "backed_up_sessions": 0,
            "current_backup_size_mb": 0.0,
            "backup_health": "No History File"
        }

        if not self.aider_history_file.exists():
            return metrics
        
        try:
            # Current history file size
            metrics["current_backup_size_mb"] = self.aider_history_file.stat().st_size / (1024 * 1024)

            # Count sessions in current history file
            session_starts = 0
            with open(self.aider_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("# aider chat started"):
                        session_starts += 1
            metrics["backed_up_sessions"] = session_starts

            # Determine backup health
            if self.should_rotate():
                metrics["backup_health"] = "Needs Rotation"
            else:
                metrics["backup_health"] = "Healthy"

        except Exception as e:
            print(f"⚠️ Error collecting backup metrics: {e}")
            metrics["backup_health"] = f"Error: {e}"
        
        return metrics


def main():
    """Main backup and rotation logic."""
    parser = argparse.ArgumentParser(
        description="Aider Chat History Backup and Rotation Script."
    )
    parser.add_argument(
        "--rotate-if-needed",
        action="store_true",
        help="Only perform backup and rotation if the history file exceeds size or age thresholds."
    )
    parser.add_argument(
        "--get-metrics",
        action="store_true",
        help="Only display current Aider history metrics and exit."
    )
    parser.add_argument(
        "workspace_dir",
        nargs="?", # 0 or 1 argument
        default=None,
        help="Optional: The workspace directory. Defaults to MCP_SERVER_ROOT env var or current working directory."
    )
    args = parser.parse_args()

    # Determine workspace_dir based on CLI arg or environment/cwd
    if args.workspace_dir:
        workspace_dir = Path(args.workspace_dir)
        print(f"Using workspace from command line argument: {workspace_dir}")
    else:
        workspace_dir = _get_workspace_dir()
    
    print(f"🔧 Aider History Manager - Workspace: {workspace_dir}")
    print("=" * 60)
    
    manager = AiderHistoryManager(workspace_dir)
    
    if args.get_metrics:
        metrics = manager.get_backup_metrics()
        print("\n💾 Aider History Status...")
        print(f"📊 Sessions in current file: {metrics['backed_up_sessions']}")
        print(f"📏 Current file size: {metrics['current_backup_size_mb']:.2f}MB")
        print(f"🏥 Backup Health Status: {metrics['backup_health']}")
        print("-" * 60)
        return # Exit after displaying metrics

    # If --rotate-if-needed is specified
    if args.rotate_if_needed:
        if not manager.aider_history_file.exists():
            print("📝 No .aider.chat.history.md file found - nothing to backup or rotate.")
        elif manager.should_rotate():
            print("🔄 Rotation needed - creating backup and rotating...")
            success = manager.rotate_history()
            if success:
                print("✅ Rotation completed successfully")
            else:
                print("❌ Rotation failed")
        else:
            print("📝 No rotation needed based on size or age thresholds.")
            print("💾 Creating backup (as part of conditional run)...")
            manager.create_backup() # Still create a backup even if no rotation
    else: # Default behavior if no specific flags are passed
        # Check if file exists
        if not manager.aider_history_file.exists():
            print("📝 No .aider.chat.history.md file found - nothing to backup or rotate.")
            print("\n✅ Aider history management complete!")
            return
        
        # Check if rotation is needed
        if manager.should_rotate():
            print("🔄 Rotation needed - creating backup and rotating...")
            success = manager.rotate_history()
            if success:
                print("✅ Rotation completed successfully")
            else:
                print("❌ Rotation failed")
        else:
            print("💾 Creating backup (no rotation needed)...")
            manager.create_backup()
    
    # Cleanup old backups always runs unless --get-metrics was the only flag
    manager.cleanup_old_backups()
    
    print("\n✅ Aider history management complete!")


def get_backup_metrics() -> dict:
    """Standalone function to get backup metrics for session bootstrap."""
    # This function is called from other modules, so it needs to determine the workspace itself.
    manager = AiderHistoryManager(_get_workspace_dir())
    return manager.get_backup_metrics()


if __name__ == "__main__":
    main()
