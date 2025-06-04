#!/usr/bin/env python3
"""
JSON Log Metrics Extractor - Phase 2A Implementation

Automated analysis of JSON structured logs to extract:
- Performance analytics  
- Operational insights

NOTE: Cost management is handled by Aider-MCP built-in functions:
- get_cost_summary() - Cost analytics
- estimate_task_cost() - Pre-execution estimation
- get_budget_status() - Budget monitoring
- export_cost_report() - Detailed cost reports

Usage:
    python -m app.analytics.metrics_extractor --report=summary
"""

import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any
from pathlib import Path

class LogMetricsExtractor:
    """Extract metrics from JSON structured logs"""
    
    def __init__(self, log_file_path: str = "logs/operational.json"):
        self.log_file_path = Path(log_file_path)
        self.logs = []
        self.load_logs()
    
    def load_logs(self):
        """Load and parse JSON logs"""
        if not self.log_file_path.exists():
            print(f"⚠️  Log file not found: {self.log_file_path}")
            return
        
        try:
            with open(self.log_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            log_entry = json.loads(line)
                            self.logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
            return
        
        print(f"📊 Loaded {len(self.logs)} log entries")
    

    
    def extract_performance_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Extract performance-related metrics"""
        session_logs = [
            log for log in self.logs
            if "Aider coding session completed" in log.get("message", "") and log.get("data")
        ]
        
        if not session_logs:
            return {"error": "No performance data found"}
        
        durations = []
        success_count = 0
        
        for log in session_logs:
            data = log["data"]
            duration_str = str(data.get("duration", "0")).replace("s", "")
            try:
                duration = float(duration_str)
                durations.append(duration)
            except ValueError:
                continue
            
            if data.get("success", False):
                success_count += 1
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        success_rate = success_count / len(session_logs) if session_logs else 0
        
        return {
            "time_range_hours": time_range_hours,
            "total_sessions": len(session_logs),
            "avg_duration_seconds": round(avg_duration, 2),
            "success_rate": round(success_rate, 3)
        }
    
    def extract_operational_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Extract operational metrics"""
        level_counts = Counter(log.get("level") for log in self.logs)
        error_logs = [log for log in self.logs if log.get("level") == "ERROR"]
        warning_logs = [log for log in self.logs if log.get("level") == "WARNING"]
        
        return {
            "time_range_hours": time_range_hours,
            "total_log_entries": len(self.logs),
            "error_count": len(error_logs),
            "warning_count": len(warning_logs),
            "error_rate": round(len(error_logs) / len(self.logs), 3) if self.logs else 0
        }
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        performance_metrics = self.extract_performance_metrics()
        operational_metrics = self.extract_operational_metrics()
        
        # Assess health status
        error_rate = operational_metrics.get("error_rate", 0)
        if error_rate > 0.1:
            health_status = "DEGRADED"
        elif error_rate > 0.05:
            health_status = "WARNING"  
        else:
            health_status = "HEALTHY"
        
        return {
            "report_generated": datetime.utcnow().isoformat() + "Z",
            "performance_analysis": performance_metrics,
            "operational_analysis": operational_metrics,
            "summary": {
                "avg_task_duration": performance_metrics.get("avg_duration_seconds", 0),
                "success_rate": performance_metrics.get("success_rate", 0),
                "error_rate": operational_metrics.get("error_rate", 0),
                "health_status": health_status
            }
        }


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Extract metrics from JSON logs")
    parser.add_argument("--report", choices=["performance", "operational", "summary"],
                       default="summary", help="Type of report to generate")
    parser.add_argument("--hours", type=int, default=24, help="Time range in hours")
    parser.add_argument("--log-file", default="logs/operational.json", help="JSON log file path")
    parser.add_argument("--output", choices=["json", "pretty"], default="pretty", help="Output format")
    
    args = parser.parse_args()
    
    extractor = LogMetricsExtractor(args.log_file)
    
    if args.report == "performance":
        report = extractor.extract_performance_metrics(args.hours)
    elif args.report == "operational":
        report = extractor.extract_operational_metrics(args.hours)
    else:
        report = extractor.generate_summary_report()
    
    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        print_pretty_report(report, args.report)


def print_pretty_report(report: Dict[str, Any], report_type: str):
    """Print human-readable report"""
    print("=" * 60)
    print(f"📊 {report_type.upper()} METRICS REPORT")
    print("=" * 60)
    
    if report_type == "summary":
        summary = report.get('summary', {})
        print("📋 EXECUTIVE SUMMARY")
        print("-" * 40)
        print(f"⚡ Avg Task Duration: {summary.get('avg_task_duration', 0)}s")
        print(f"✅ Success Rate: {summary.get('success_rate', 0)*100:.1f}%")
        print(f"❌ Error Rate: {summary.get('error_rate', 0)*100:.1f}%")
        print(f"🏥 Health Status: {summary.get('health_status', 'UNKNOWN')}")
        
        # Show details
        perf_data = report.get('performance_analysis', {})
        if 'error' not in perf_data:
            print(f"\n⚡ Performance Details: {perf_data.get('total_sessions', 0)} sessions")
            
        ops_data = report.get('operational_analysis', {})
        print(f"🔧 Operational Details: {ops_data.get('total_log_entries', 0)} log entries")
    elif report_type == "performance":
        if 'error' in report:
            print(f"❌ {report['error']}")
        else:
            print(f"⚡ PERFORMANCE ANALYSIS")
            print(f"Total Sessions: {report.get('total_sessions', 0)}")
            print(f"Average Duration: {report.get('avg_duration_seconds', 0)}s")
            print(f"Success Rate: {report.get('success_rate', 0)*100:.1f}%")
    
    elif report_type == "operational":
        print(f"🔧 OPERATIONAL ANALYSIS")
        print(f"Total Log Entries: {report.get('total_log_entries', 0)}")
        print(f"Error Count: {report.get('error_count', 0)}")
        print(f"Warning Count: {report.get('warning_count', 0)}")
        print(f"Error Rate: {report.get('error_rate', 0)*100:.1f}%")


if __name__ == "__main__":
    main()
