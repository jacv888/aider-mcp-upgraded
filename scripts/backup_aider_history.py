#!/usr/bin/env python3
"""
Aider Chat History Backup and Analytics Script

Provides intelligent backup, rotation, and cost analytics for .aider.chat.history.md
Integrates with existing ai-logs directory structure for consistency.
"""
import os
import sys
import json
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class AiderHistoryManager:
    """Manages Aider chat history backups with cost analytics extraction."""
    
    def __init__(self, workspace_dir: str = "/Users/jacquesv/MCP/aider-mcp"):
        self.workspace_dir = Path(workspace_dir)
        self.aider_history_file = self.workspace_dir / ".aider.chat.history.md"
        self.backup_dir = self.workspace_dir / "ai-logs" / "aider-history-archive"
        self.analytics_dir = self.workspace_dir / "ai-logs" / "aider-analytics"
        
        # Create directories if they don't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    def extract_cost_analytics(self) -> Dict:
        """Extract cost and usage analytics from the history file."""
        if not self.aider_history_file.exists():
            return {"error": "History file not found"}
        
        analytics = {
            "extraction_date": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_cost_usd": 0.0,
            "models_used": {},
            "daily_costs": {},
            "session_summary": [],
            "period_start": None,
            "period_end": None
        }
        
        try:
            with open(self.aider_history_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract session costs with regex
            cost_pattern = r'\$([0-9]+\.?[0-9]*) message.*?\$([0-9]+\.?[0-9]*) session'
            session_dates = re.findall(r'^# aider chat started at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content, re.MULTILINE)
            
            costs = re.findall(cost_pattern, content)
            analytics["total_sessions"] = len(costs)
            
            # Calculate total costs
            for message_cost, session_cost in costs:
                analytics["total_cost_usd"] += float(session_cost)
            
            # Extract model usage
            model_pattern = r'Model: ([\w\-\.\/]+)'
            models = re.findall(model_pattern, content)
            for model in models:
                analytics["models_used"][model] = analytics["models_used"].get(model, 0) + 1
            
            # Extract date range
            if session_dates:
                dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in session_dates]
                analytics["period_start"] = min(dates).isoformat()
                analytics["period_end"] = max(dates).isoformat()
            
            # Daily cost breakdown (simplified)
            analytics["daily_costs"] = self._calculate_daily_costs(content)
            
            print(f"📊 Analytics extracted: {analytics['total_sessions']} sessions, ${analytics['total_cost_usd']:.4f} total")
            
        except Exception as e:
            analytics["error"] = f"Failed to extract analytics: {str(e)}"
            print(f"⚠️ Analytics extraction failed: {e}")
        
        return analytics
    
    def _calculate_daily_costs(self, content: str) -> Dict[str, float]:
        """Calculate daily cost breakdown from history content."""
        daily_costs = {}
        lines = content.split('\n')
        current_date = None
        
        for line in lines:
            # Look for date headers
            date_match = re.match(r'^# aider chat started at (\d{4}-\d{2}-\d{2})', line)
            if date_match:
                current_date = date_match.group(1)
                if current_date not in daily_costs:
                    daily_costs[current_date] = 0.0
            
            # Look for session costs
            if current_date:
                cost_match = re.search(r'\$([0-9]+\.?[0-9]*) session', line)
                if cost_match:
                    daily_costs[current_date] += float(cost_match.group(1))
        
        return daily_costs
    
    def create_backup(self) -> str:
        """Create a timestamped backup of the history file."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"aider_history_{timestamp}.md"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Extract analytics before backup
            analytics = self.extract_cost_analytics()
            analytics_filename = f"aider_analytics_{timestamp}.json"
            analytics_path = self.analytics_dir / analytics_filename
            
            # Save analytics
            with open(analytics_path, 'w') as f:
                json.dump(analytics, f, indent=2)
            print(f"📊 Analytics saved: {analytics_path}")
            
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
        try:
            # Create backup first
            backup_path = self.create_backup()
            
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
                # Also remove corresponding analytics file
                timestamp = backup_file.stem.replace("aider_history_", "")
                analytics_file = self.analytics_dir / f"aider_analytics_{timestamp}.json"
                if analytics_file.exists():
                    analytics_file.unlink()
                removed_count += 1
            
            print(f"🗑️ Cleaned up {removed_count} old backups (keeping {keep_backups} most recent)")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def get_cost_summary(self, days: int = 30) -> Dict:
        """Get cost summary from recent analytics files."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            total_cost = 0.0
            total_sessions = 0
            models_used = {}
            
            # Scan analytics files
            for analytics_file in self.analytics_dir.glob("aider_analytics_*.json"):
                try:
                    # Extract timestamp from filename
                    timestamp_str = analytics_file.stem.replace("aider_analytics_", "")
                    file_date = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                    
                    if file_date >= cutoff_date:
                        with open(analytics_file, 'r') as f:
                            data = json.load(f)
                        
                        total_cost += data.get("total_cost_usd", 0.0)
                        total_sessions += data.get("total_sessions", 0)
                        
                        for model, count in data.get("models_used", {}).items():
                            models_used[model] = models_used.get(model, 0) + count
                            
                except Exception as e:
                    print(f"⚠️ Skipping malformed analytics file {analytics_file}: {e}")
            
            return {
                "period_days": days,
                "total_cost_usd": total_cost,
                "total_sessions": total_sessions,
                "models_used": models_used,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to generate cost summary: {e}"}


def main():
    """Main backup and rotation logic."""
    if len(sys.argv) > 1:
        workspace_dir = sys.argv[1]
    else:
        workspace_dir = "/Users/jacquesv/MCP/aider-mcp"
    
    print(f"🔧 Aider History Manager - Workspace: {workspace_dir}")
    print("=" * 60)
    
    manager = AiderHistoryManager(workspace_dir)
    
    # Check if file exists
    if not manager.aider_history_file.exists():
        print("📝 No .aider.chat.history.md file found - nothing to backup")
        return
    
    # Show current file status
    size_mb = manager.aider_history_file.stat().st_size / (1024 * 1024)
    print(f"📊 Current file size: {size_mb:.2f}MB")
    
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
    
    # Cleanup old backups
    manager.cleanup_old_backups()
    
    # Show cost summary
    print("\n📊 Cost Summary (Last 30 days):")
    print("-" * 40)
    summary = manager.get_cost_summary()
    if "error" not in summary:
        print(f"Total Sessions: {summary['total_sessions']}")
        print(f"Total Cost: ${summary['total_cost_usd']:.4f}")
        print(f"Models Used: {len(summary['models_used'])}")
        for model, count in summary['models_used'].items():
            print(f"  - {model}: {count} sessions")
    else:
        print(f"⚠️ {summary['error']}")
    
    print("\n✅ Aider history management complete!")


if __name__ == "__main__":
    main()
