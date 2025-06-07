#!/usr/bin/env python3
"""
Real-time Analytics Dashboard Generator

Creates automated reports from JSON logs focusing on performance and operational metrics.
For cost management, use Aider-MCP built-in functions:
- get_cost_summary() - Cost analytics
- estimate_task_cost() - Pre-execution estimation  
- get_budget_status() - Budget monitoring
- export_cost_report() - Detailed cost reports

Usage:
    python generate_reports.py                    # Generate all reports
    python generate_reports.py --watch           # Continuous monitoring mode
    python generate_reports.py --export=html     # Export to HTML format
"""

import json
import time
import os
import argparse
from datetime import datetime
from pathlib import Path
from .metrics_extractor import LogMetricsExtractor

# Helper to get the current month's operational log file path
def _get_current_operational_log_path():
    current_month = datetime.now().strftime("%Y-%m")
    return f"logs/current/operational_{current_month}.json"

class ReportGenerator:
    """Generate automated analytics reports"""
    
    def __init__(self, log_file: str = None, output_dir: str = "logs/reports"):
        # If log_file is not provided, use the current month's log file
        if log_file is None:
            self.log_file = _get_current_operational_log_path()
        else:
            self.log_file = log_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.extractor = LogMetricsExtractor(self.log_file)
    
    def generate_all_reports(self, export_format: str = "json"):
        """Generate comprehensive analytics reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("🔄 Generating analytics reports...")
        
        # Generate individual reports
        reports = {
            "performance": self.extractor.extract_performance_metrics(), 
            "operational": self.extractor.extract_operational_metrics(),
            "summary": self.extractor.generate_summary_report()
        }
        
        # Save reports
        for report_type, data in reports.items():
            if export_format == "html":
                self._save_html_report(report_type, data, timestamp)
            else:
                self._save_json_report(report_type, data, timestamp)
        
        # Create latest symlinks
        self._create_latest_symlinks(reports, export_format)
        
        print(f"✅ Reports generated in {self.output_dir}")
        return reports
    
    def _save_json_report(self, report_type: str, data: dict, timestamp: str):
        """Save report as JSON file"""
        filename = f"{report_type}_report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save as latest
        latest_path = self.output_dir / f"{report_type}_latest.json"
        with open(latest_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_html_report(self, report_type: str, data: dict, timestamp: str):
        """Save report as HTML file"""
        html_content = self._generate_html_report(report_type, data)
        
        filename = f"{report_type}_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        # Also save as latest
        latest_path = self.output_dir / f"{report_type}_latest.html"
        with open(latest_path, 'w') as f:
            f.write(html_content)
    
    def _generate_html_report(self, report_type: str, data: dict) -> str:
        """Generate HTML report from data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report_type.title()} Report - Aider MCP Analytics</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem; }}
        .header {{ background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }}
        .metric-card {{ background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: #0d6efd; }}
        .metric-label {{ color: #6c757d; font-size: 0.9rem; }}
        .error {{ color: #dc3545; }}
        .warning {{ color: #fd7e14; }}
        .success {{ color: #198754; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; }}
        .json-data {{ background: #f8f9fa; padding: 1rem; border-radius: 4px; font-family: monospace; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {report_type.title()} Report</h1>
        <p>Generated: {timestamp}</p>
        <p>Data Source: {self.log_file}</p>
    </div>
"""
        
        if report_type == "summary":
            html += self._generate_summary_html(data)
        elif report_type == "performance":
            html += self._generate_performance_html(data)
        elif report_type == "operational":
            html += self._generate_operational_html(data)
        
        html += """
    <div class="metric-card">
        <h3>Raw Data (JSON)</h3>
        <div class="json-data">
            <pre>""" + json.dumps(data, indent=2) + """</pre>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_summary_html(self, data: dict) -> str:
        """Generate HTML for summary report"""
        summary = data.get('summary', {})
        
        return f"""
    <div class="metric-card">
        <h2>Executive Summary</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div>
                <div class="metric-value">{summary.get('avg_task_duration', 0)}s</div>
                <div class="metric-label">Avg Task Duration</div>
            </div>
            <div>
                <div class="metric-value">{summary.get('success_rate', 0)*100:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div>
                <div class="metric-value {self._get_health_class(summary.get('health_status', 'UNKNOWN'))}">{summary.get('health_status', 'UNKNOWN')}</div>
                <div class="metric-label">Health Status</div>
            </div>
        </div>
        <div class="metric-card">
            <h3>💰 Cost Management</h3>
            <p>For cost analysis, use Aider-MCP built-in functions:</p>
            <ul>
                <li><code>get_cost_summary()</code> - Cost analytics and trends</li>
                <li><code>estimate_task_cost()</code> - Pre-execution cost estimation</li>
                <li><code>get_budget_status()</code> - Budget monitoring</li>
                <li><code>export_cost_report()</code> - Detailed cost reports</li>
            </ul>
        </div>
    </div>
"""

    
    def _generate_performance_html(self, data: dict) -> str:
        """Generate HTML for performance report"""
        if 'error' in data:
            return f'<div class="metric-card error"><h2>Performance Analysis</h2><p>{data["error"]}</p></div>'
        
        html = f"""
    <div class="metric-card">
        <h2>⚡ Performance Analysis</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
            <div>
                <div class="metric-value">{data.get('total_sessions', 0)}</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            <div>
                <div class="metric-value">{data.get('avg_duration_seconds', 0)}s</div>
                <div class="metric-label">Avg Duration</div>
            </div>
            <div>
                <div class="metric-value">{data.get('success_rate', 0)*100:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
        
        <h3>Performance by Model</h3>
        <table>
            <tr><th>Model</th><th>Avg Duration</th><th>Sessions</th><th>Min</th><th>Max</th></tr>
"""
        
        for model, stats in data.get('performance_by_model', {}).items():
            html += f"""
            <tr>
                <td>{model}</td>
                <td>{stats['avg_duration']}s</td>
                <td>{stats['session_count']}</td>
                <td>{stats['min_duration']}s</td>
                <td>{stats['max_duration']}s</td>
            </tr>"""
        
        html += "</table>"
        
        # Add bottlenecks
        bottlenecks = data.get('bottlenecks', [])
        if bottlenecks:
            html += "<h3>🚨 Identified Bottlenecks</h3><ul>"
            for bottleneck in bottlenecks:
                html += f"<li>{bottleneck}</li>"
            html += "</ul>"
        
        html += "</div>"
        return html
    
    def _generate_operational_html(self, data: dict) -> str:
        """Generate HTML for operational report"""
        html = f"""
    <div class="metric-card">
        <h2>🔧 Operational Analysis</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
            <div>
                <div class="metric-value">{data.get('total_log_entries', 0)}</div>
                <div class="metric-label">Log Entries</div>
            </div>
            <div>
                <div class="metric-value error">{data.get('error_count', 0)}</div>
                <div class="metric-label">Errors</div>
            </div>
            <div>
                <div class="metric-value warning">{data.get('warning_count', 0)}</div>
                <div class="metric-label">Warnings</div>
            </div>
            <div>
                <div class="metric-value">{data.get('error_rate', 0)*100:.1f}%</div>
                <div class="metric-label">Error Rate</div>
            </div>
        </div>
    </div>
"""
        return html
    
    def _get_health_class(self, status: str) -> str:
        """Get CSS class for health status"""
        if status == "HEALTHY":
            return "success"
        elif status == "WARNING":
            return "warning"
        else:
            return "error"
    
    def _create_latest_symlinks(self, reports: dict, export_format: str):
        """Create latest report symlinks for easy access"""
        pass  # Implemented above with direct latest file creation
    
    def watch_mode(self, interval_seconds: int = 300):
        """Continuous monitoring mode"""
        print(f"🔄 Starting continuous monitoring (updates every {interval_seconds}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Generating reports...")
                self.generate_all_reports()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Generate analytics reports from JSON logs")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=300, help="Update interval in seconds (watch mode)")
    parser.add_argument("--export", choices=["json", "html"], default="json", help="Export format")
    parser.add_argument("--log-file", default=_get_current_operational_log_path(), help="JSON log file path")
    parser.add_argument("--output-dir", default="logs/reports", help="Output directory for reports")
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.log_file, args.output_dir)
    
    if args.watch:
        generator.watch_mode(args.interval)
    else:
        reports = generator.generate_all_reports(args.export)
        
        # Print quick summary
        summary = reports.get('summary', {}).get('summary', {})
        print(f"\n📊 Quick Summary:")
        print(f"⚡ Performance: {summary.get('avg_task_duration', 0)}s avg")
        print(f"🏥 Health: {summary.get('health_status', 'UNKNOWN')}")
        print(f"💰 Cost Management: Use Aider-MCP functions (get_cost_summary, etc.)")


if __name__ == "__main__":
    main()
