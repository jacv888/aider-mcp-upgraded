"""
💾 Persistent Cost Storage for Aider-MCP
Saves cost data to JSON file for persistence across sessions.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List
from app.cost.cost_manager import TaskCostResult

class CostStorage:
    """Handles persistent storage of cost data."""
    
    def __init__(self, storage_file: str = None):
        if storage_file is None:
            # Store in project root costs directory
            project_root = Path(__file__).parent.parent.parent  # Go up to actual project root
            costs_dir = project_root / "costs"
            costs_dir.mkdir(exist_ok=True)
            
            # Monthly cost files for better organization
            from datetime import datetime
            current_month = datetime.now().strftime("%Y-%m")
            self.storage_file = costs_dir / f"costs_{current_month}.json"
            self.costs_dir = costs_dir
        else:
            self.storage_file = Path(storage_file)
            self.costs_dir = self.storage_file.parent
    
    def load_cost_history(self) -> List[TaskCostResult]:
        """Load cost history from current month and optionally previous months."""
        all_costs = []
        
        # Load current month
        if self.storage_file.exists():
            all_costs.extend(self._load_from_file(self.storage_file))
        
        # Optionally load recent months for comprehensive history
        from datetime import datetime, timedelta
        current_date = datetime.now()
        
        # Load previous 2 months for better analytics
        for months_back in range(1, 3):
            prev_month = current_date.replace(day=1) - timedelta(days=months_back * 31)
            prev_month_str = prev_month.strftime("%Y-%m")
            prev_file = self.costs_dir / f"costs_{prev_month_str}.json"
            
            if prev_file.exists():
                all_costs.extend(self._load_from_file(prev_file))
        
        # Sort by timestamp (newest first)
        all_costs.sort(key=lambda x: x.timestamp, reverse=True)
        return all_costs
    
    def _load_from_file(self, file_path: Path) -> List[TaskCostResult]:
        """Load cost data from a specific file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert back to TaskCostResult objects
            cost_history = []
            for item in data:
                result = TaskCostResult(
                    input_tokens=item['input_tokens'],
                    output_tokens=item['output_tokens'],
                    total_tokens=item['total_tokens'],
                    input_cost=item['input_cost'],
                    output_cost=item['output_cost'],
                    total_cost=item['total_cost'],
                    model=item['model'],
                    duration_seconds=item['duration_seconds'],
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    task_id=item['task_id']
                )
                cost_history.append(result)
            
            return cost_history
            
        except Exception as e:
            print(f"Warning: Could not load cost history from {file_path}: {e}")
            return []
    
    def save_cost_history(self, cost_history: List[TaskCostResult]):
        """Save current month's cost history to storage file."""
        try:
            # Only save costs from current month to current file
            from datetime import datetime
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            current_month_costs = [
                cost for cost in cost_history 
                if cost.timestamp >= current_month
            ]
            
            # Convert TaskCostResult objects to JSON-serializable format
            data = []
            for result in current_month_costs:
                data.append({
                    'input_tokens': result.input_tokens,
                    'output_tokens': result.output_tokens,
                    'total_tokens': result.total_tokens,
                    'input_cost': round(result.input_cost, 8),  # Round to avoid scientific notation
                    'output_cost': round(result.output_cost, 8),
                    'total_cost': round(result.total_cost, 8),
                    'model': result.model,
                    'duration_seconds': result.duration_seconds,
                    'timestamp': result.timestamp.isoformat(),
                    'task_id': result.task_id,
                    'task_name': getattr(result, 'task_name', 'Unnamed Task')  # Backward compatibility
                })
            
            # Write to file with backup
            backup_file = self.storage_file.with_suffix('.json.bak')
            if self.storage_file.exists():
                # Create backup of existing file
                import shutil
                shutil.copy2(self.storage_file, backup_file)
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save cost history: {e}")
    
    def export_to_csv(self, cost_history: List[TaskCostResult], output_file: str = None) -> str:
        """Export cost history to CSV format in costs directory."""
        if output_file is None:
            # Generate timestamped filename in costs directory
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.costs_dir / f"cost_export_{timestamp}.csv"
        else:
            # Ensure output is in costs directory
            output_file = self.costs_dir / output_file
        
        try:
            import csv
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = [
                    'timestamp', 'task_id', 'task_name', 'model', 'input_tokens', 'output_tokens',
                    'total_tokens', 'input_cost', 'output_cost', 'total_cost', 
                    'duration_seconds'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in cost_history:
                    writer.writerow({
                        'timestamp': result.timestamp.isoformat(),
                        'task_id': result.task_id,
                        'task_name': getattr(result, 'task_name', 'Unnamed Task'),  # Backward compatibility
                        'model': result.model,
                        'input_tokens': result.input_tokens,
                        'output_tokens': result.output_tokens,
                        'total_tokens': result.total_tokens,
                        'input_cost': round(result.input_cost, 8),  # Round to avoid scientific notation
                        'output_cost': round(result.output_cost, 8),
                        'total_cost': round(result.total_cost, 8),
                        'duration_seconds': result.duration_seconds
                    })
            
            return str(output_file)
            
        except Exception as e:
            raise Exception(f"Failed to export CSV: {e}")

# Global storage instance
cost_storage = CostStorage()
