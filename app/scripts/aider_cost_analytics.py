import os
import sys
import json
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any

class AiderHistoryManager:
    """
    Manages Aider chat history files and extracts cost analytics.
    This class is adapted from scripts/backup_aider_history.py.
    """
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
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
        
        size_mb = self.aider_history_file.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return True
        
        age_days = (datetime.now().timestamp() - self.aider_history_file.stat().st_mtime) / (24 * 3600)
        if age_days > max_age_days:
            return True
        
        return False
    
    def extract_cost_analytics(self) -> Dict[str, Any]:
        """
        Extracts cost and usage analytics from the history file.
        Parses each session to get accurate cost and model usage.
        """
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
            
            # Pattern to capture a full session block: header and content
            session_pattern = re.compile(
                r'(# aider chat started at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}))\n'
                r'(.*?)(?=\n# aider chat started at|\Z)',
                re.DOTALL
            )
            
            sessions = session_pattern.findall(content)
            analytics["total_sessions"] = len(sessions)
            
            all_session_dates = []
            
            for session_header, session_date_str, session_content in sessions:
                session_cost_match = re.search(r'\$([0-9]+\.?[0-9]*) session', session_content)
                session_cost = float(session_cost_match.group(1)) if session_cost_match else 0.0
                
                model_match = re.search(r'Model: ([\w\-\.\/]+)', session_content)
                model_name = model_match.group(1) if model_match else "unknown"
                
                session_date = datetime.strptime(session_date_str, "%Y-%m-%d %H:%M:%S")
                all_session_dates.append(session_date)
                
                analytics["total_cost_usd"] += session_cost
                analytics["models_used"][model_name] = analytics["models_used"].get(model_name, 0) + 1
                
                analytics["session_summary"].append({
                    "date": session_date.isoformat(),
                    "cost_usd": session_cost,
                    "model": model_name
                })
            
            if all_session_dates:
                analytics["period_start"] = min(all_session_dates).isoformat()
                analytics["period_end"] = max(all_session_dates).isoformat()
            
            analytics["daily_costs"] = self._calculate_daily_costs(content)
            
        except Exception as e:
            analytics["error"] = f"Failed to extract analytics: {str(e)}"
        
        return analytics
    
    def _calculate_daily_costs(self, content: str) -> Dict[str, float]:
        """Calculate daily cost breakdown from history content."""
        daily_costs = {}
        
        session_pattern = re.compile(
            r'(# aider chat started at (\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2})\n'
            r'(.*?)(?=\n# aider chat started at|\Z)',
            re.DOTALL
        )
        
        sessions = session_pattern.findall(content)
        
        for session_header, session_date_str, session_content in sessions:
            current_date = session_date_str # YYYY-MM-DD
            cost_match = re.search(r'\$([0-9]+\.?[0-9]*) session', session_content)
            if cost_match:
                daily_costs[current_date] = daily_costs.get(current_date, 0.0) + float(cost_match.group(1))
        
        return daily_costs
    
    def create_backup(self) -> str:
        """Create a timestamped backup of the history file and save analytics."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"aider_history_{timestamp}.md"
        backup_path = self.backup_dir / backup_filename
        
        try:
            analytics = self.extract_cost_analytics()
            analytics_filename = f"aider_analytics_{timestamp}.json"
            analytics_path = self.analytics_dir / analytics_filename
            
            with open(analytics_path, 'w') as f:
                json.dump(analytics, f, indent=2)
            
            shutil.copy2(self.aider_history_file, backup_path)
            
            return str(backup_path)
            
        except Exception as e:
            raise RuntimeError(f"Backup failed: {e}") from e
    
    def rotate_history(self, keep_recent_entries: int = 50) -> bool:
        """Rotate the history file, keeping only recent entries."""
        try:
            self.create_backup() # Ensure backup is created before rotation
            
            with open(self.aider_history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            session_starts = []
            for i, line in enumerate(lines):
                if line.startswith("# aider chat started"):
                    session_starts.append(i)
            
            if len(session_starts) <= keep_recent_entries:
                return False
            
            keep_from_line = session_starts[-keep_recent_entries]
            new_content = "".join(lines[keep_from_line:])
            
            with open(self.aider_history_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Rotation failed: {e}") from e
    
    def cleanup_old_backups(self, keep_backups: int = 10) -> None:
        """Remove old backup files, keeping only the most recent ones."""
        try:
            backup_files = sorted(
                [f for f in self.backup_dir.glob("aider_history_*.md")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if len(backup_files) <= keep_backups:
                return
            
            for backup_file in backup_files[keep_backups:]:
                backup_file.unlink()
                timestamp = backup_file.stem.replace("aider_history_", "")
                analytics_file = self.analytics_dir / f"aider_analytics_{timestamp}.json"
                if analytics_file.exists():
                    analytics_file.unlink()
            
        except Exception:
            pass # Suppress errors for cleanup, it's a best-effort operation
    
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get cost summary from recent analytics files."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            total_cost = 0.0
            total_sessions = 0
            models_used = {}
            
            for analytics_file in self.analytics_dir.glob("aider_analytics_*.json"):
                try:
                    timestamp_str = analytics_file.stem.replace("aider_analytics_", "")
                    file_date = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                    
                    if file_date >= cutoff_date:
                        with open(analytics_file, 'r') as f:
                            data = json.load(f)
                        
                        total_cost += data.get("total_cost_usd", 0.0)
                        total_sessions += data.get("total_sessions", 0)
                        
                        for model, count in data.get("models_used", {}).items():
                            models_used[model] = models_used.get(model, 0) + count
                            
                except Exception:
                    pass # Skip malformed or unreadable analytics files
            
            return {
                "period_days": days,
                "total_cost_usd": total_cost,
                "total_sessions": total_sessions,
                "models_used": models_used,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to generate cost summary: {e}"}

    def calculate_estimated_savings(self, efficiency_factor: float = 2.5) -> Dict[str, float]:
        """
        Estimates cost savings based on an assumed efficiency factor (e.g., from context pruning).
        
        Args:
            efficiency_factor (float): The factor by which context-aware features
                                       are assumed to reduce token usage/cost.
                                       A factor of 2.5 means 2.5x reduction.
                                       (e.g., if actual cost is X, baseline would be X * 2.5)
        Returns:
            Dict[str, float]: Contains 'total_actual_cost', 'estimated_baseline_cost', 'estimated_savings'.
        """
        analytics = self.extract_cost_analytics()
        total_actual_cost = analytics.get("total_cost_usd", 0.0)
        
        if total_actual_cost == 0:
            return {
                "total_actual_cost": 0.0,
                "estimated_baseline_cost": 0.0,
                "estimated_savings": 0.0,
                "efficiency_factor_used": efficiency_factor,
                "note": "No cost data available to calculate savings."
            }

        estimated_baseline_cost = total_actual_cost * efficiency_factor
        estimated_savings = estimated_baseline_cost - total_actual_cost
        
        return {
            "total_actual_cost": total_actual_cost,
            "estimated_baseline_cost": estimated_baseline_cost,
            "estimated_savings": estimated_savings,
            "efficiency_factor_used": efficiency_factor,
            "note": f"Savings estimated assuming a {efficiency_factor}x reduction in cost due to efficiency features (e.g., context pruning)."
        }

    def get_token_efficiency_metrics(self) -> Dict[str, Any]:
        """
        Provides proxy metrics for token efficiency based on cost per session/model.
        
        Note: Aider's history file does not directly log token counts.
        These metrics use cost as a proxy for token usage.
        """
        analytics = self.extract_cost_analytics()
        
        total_sessions = analytics.get("total_sessions", 0)
        total_cost = analytics.get("total_cost_usd", 0.0)
        models_used = analytics.get("models_used", {})
        
        cost_per_session = total_cost / total_sessions if total_sessions > 0 else 0.0
        
        model_usage_summary = {}
        for model, count in models_used.items():
            model_usage_summary[model] = {
                "sessions_count": count,
            }

        return {
            "cost_per_session_avg": cost_per_session,
            "models_usage_summary": model_usage_summary,
            "note": "Token efficiency is approximated using cost per session/model usage, as raw token counts are not available in .aider.chat.history.md."
        }

    def extract_target_elements_identified(self) -> Dict[str, Any]:
        """
        Extracts potential 'target elements' (e.g., file paths, function names)
        from the Aider chat history. This is an approximation based on common patterns.
        
        Returns:
            Dict[str, Any]: A dictionary containing lists of identified file paths,
                            and a count of potential code element mentions.
        """
        if not self.aider_history_file.exists():
            return {"error": "History file not found", "identified_files": [], "potential_code_elements_count": 0}
        
        identified_files: Set[str] = set()
        potential_code_elements_count = 0
        
        try:
            with open(self.aider_history_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Regex for file paths (e.g., in diffs, or mentioned in conversation)
            # Looks for paths starting with a common directory structure or relative path indicators
            # and ending with a common file extension.
            file_path_pattern = re.compile(r'(?:^|\s)([\w./_-]+(?:/\w[\w./_-]*)+\.(py|js|ts|md|json|yaml|yml|sh|txt|html|css|java|c|cpp|h|hpp|go|rb|php|xml|toml|ini|conf|env|dockerfile|gitignore|gitattributes|editorconfig|prettierrc|eslintrc|npmrc|yarnrc|package.json|tsconfig.json|webpack.config.js|rollup.config.js|vite.config.js|tailwind.config.js|jest.config.js|babel.config.js|next.config.js|nuxt.config.js|svelte.config.js|vue.config.js|angular.json|pom.xml|build.gradle|Gemfile|Rakefile|Cargo.toml|requirements.txt|setup.py|Makefile|Dockerfile|Jenkinsfile|README|LICENSE|CONTRIBUTING|CHANGELOG|SECURITY|CODE_OF_CONDUCT|PULL_REQUEST_TEMPLATE|ISSUE_TEMPLATE|FUNDING|CODEOWNERS|config|data|src|test|lib|bin|docs|examples|assets|public|private|tmp|var|log|cache|node_modules|dist|build|out|target|vendor|__pycache__)\b)')
            
            # Regex for potential code elements (e.g., function/class definitions, variable names)
            # This is very broad and might catch non-code text.
            code_element_pattern = re.compile(r'\b(?:def|class|function|const|let|var|import|export|public|private|protected|static|async|await|return|if|for|while|try|except|finally|with|as|from|in|is|not|and|or|self|this|super|new|yield|lambda|enum|struct|interface|type|module|package|namespace)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b')
            
            # Extract file paths
            for match in file_path_pattern.finditer(content):
                identified_files.add(match.group(1).strip())
            
            # Count potential code elements (very rough)
            potential_code_elements_count = len(code_element_pattern.findall(content))
            
        except Exception as e:
            return {"error": f"Failed to extract target elements: {str(e)}", "identified_files": [], "potential_code_elements_count": 0}
        
        return {
            "identified_files": sorted(list(identified_files)),
            "potential_code_elements_count": potential_code_elements_count,
            "note": "Target elements are approximated by parsing file paths and common code keywords from the chat history. This is not a precise measure of context extraction."
        }


def get_session_bootstrap_metrics(workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates a comprehensive set of metrics for the Session Bootstrap,
    including cost, savings, and efficiency.
    
    Args:
        workspace_dir (Optional[str]): The base directory where .aider.chat.history.md is located.
                                       Defaults to current working directory.
                                       
    Returns:
        Dict[str, Any]: A dictionary containing all requested metrics.
    """
    manager = AiderHistoryManager(workspace_dir)
    
    if not manager.aider_history_file.exists():
        return {
            "status": "error",
            "message": "Aider chat history file not found. Cannot generate metrics.",
            "file_path": str(manager.aider_history_file)
        }

    all_analytics = manager.extract_cost_analytics()
    recent_summary = manager.get_cost_summary(days=7) # Last 7 days for "recent costs"
    savings_metrics = manager.calculate_estimated_savings() # Default efficiency factor
    token_efficiency_metrics = manager.get_token_efficiency_metrics()
    target_elements_metrics = manager.extract_target_elements_identified()

    metrics = {
        "status": "success",
        "generated_at": datetime.now().isoformat(),
        "history_file_path": str(manager.aider_history_file),
        "backed_up_sessions_count": all_analytics.get("total_sessions", 0),
        "total_cost_usd": all_analytics.get("total_cost_usd", 0.0),
        "recent_cost_usd_7_days": recent_summary.get("total_cost_usd", 0.0),
        "cost_savings_estimation": savings_metrics,
        "token_efficiency_metrics": token_efficiency_metrics,
        "target_elements_identified": target_elements_metrics,
        "models_used_summary": all_analytics.get("models_used", {}),
        "daily_cost_breakdown": all_analytics.get("daily_costs", {}),
        "period_start": all_analytics.get("period_start"),
        "period_end": all_analytics.get("period_end"),
        "notes": [
            "Cost savings are estimated based on an assumed efficiency factor, as direct token savings are not logged.",
            "Token efficiency is approximated using cost per session/model usage, as raw token counts are not available.",
            "Target elements identified are approximated by parsing file paths and common code keywords from the chat history."
        ]
    }
    
    if "error" in all_analytics:
        metrics["notes"].append(f"Error during core analytics extraction: {all_analytics['error']}")
        metrics["status"] = "partial_success"
    if "error" in recent_summary:
        metrics["notes"].append(f"Error during recent cost summary: {recent_summary['error']}")
        metrics["status"] = "partial_success"
    if "error" in target_elements_metrics:
        metrics["notes"].append(f"Error during target elements extraction: {target_elements_metrics['error']}")
        metrics["status"] = "partial_success"

    return metrics

def main():
    """
    Main function to run the analytics and print the results as JSON.
    """
    workspace_dir = None
    if len(sys.argv) > 1:
        workspace_dir = sys.argv[1]

    metrics = get_session_bootstrap_metrics(workspace_dir)
    
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
def get_cost_metrics() -> Dict[str, Any]:
    """
    Extracts cost metrics from the Aider chat history, including:
    - cost_today: total cost for the current day
    - cost_month: total cost for the current month
    - total_savings: estimated savings based on optimization data
    - target_elements_identified: number of target elements parsed
    - token_efficiency_metrics: token efficiency proxy metrics
    
    Returns:
        Dict[str, Any]: Dictionary with the above metrics.
    """
    manager = AiderHistoryManager()
    analytics = manager.extract_cost_analytics()
    history_path = manager.aider_history_file
    
    cost_today = 0.0
    cost_month = 0.0
    total_savings = 0.0
    target_elements = 0
    token_efficiency_metrics = {}
    
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Extract session dates and costs
        session_pattern = re.compile(
            r'(# aider chat started at (\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2})\n'
            r'(.*?)(?=\n# aider chat started at|\Z)',
            re.DOTALL
        )
        sessions = session_pattern.findall(content)
        now = datetime.now()
        for header, date_str, session_content in sessions:
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            cost_match = re.search(r'\$([0-9]+\.?[0-9]*) session', session_content)
            session_cost = float(cost_match.group(1)) if cost_match else 0.0
            if session_date.date() == now.date():
                cost_today += session_cost
            if session_date.year == now.year and session_date.month == now.month:
                cost_month += session_cost
        # Use analytics for total cost
        total_cost = analytics.get("total_cost_usd", 0.0)
        # For savings, assume a fixed efficiency factor (e.g., 2.5x)
        efficiency_factor = 2.5
        total_savings = total_cost * (efficiency_factor - 1)
        # Extract target elements
        target_elements = len(analytics.get("session_summary", []))
        # Token efficiency proxy
        token_efficiency_metrics = manager.get_token_efficiency_metrics()
    except Exception:
        pass
    
    return {
        "cost_today": cost_today,
        "cost_month": cost_month,
        "total_savings": total_savings,
        "target_elements_identified": target_elements,
        "token_efficiency_metrics": token_efficiency_metrics
    }
