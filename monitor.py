"""
Monitoring Script for Labib Bot
سكريبت المراقبة لبوت لبيب
"""

import os
import time
import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
from config import Config

class BotMonitor:
    """Monitor bot performance and usage"""
    
    def __init__(self):
        self.stats_file = "bot_stats.json"
        self.logs_dir = "logs"
        self.stats = self.load_stats()
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def load_stats(self):
        """Load existing statistics"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_interactions": 0,
            "daily_stats": {},
            "subject_stats": {},
            "grade_stats": {},
            "error_count": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def save_stats(self):
        """Save statistics to file"""
        self.stats["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving stats: {e}")
    
    def update_interaction_stats(self, grade, subject, success=True):
        """Update interaction statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update daily stats
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {
                "total": 0,
                "successful": 0,
                "failed": 0
            }
        
        self.stats["daily_stats"][today]["total"] += 1
        if success:
            self.stats["daily_stats"][today]["successful"] += 1
        else:
            self.stats["daily_stats"][today]["failed"] += 1
            self.stats["error_count"] += 1
        
        # Update subject stats
        if subject not in self.stats["subject_stats"]:
            self.stats["subject_stats"][subject] = 0
        self.stats["subject_stats"][subject] += 1
        
        # Update grade stats
        if grade not in self.stats["grade_stats"]:
            self.stats["grade_stats"][grade] = 0
        self.stats["grade_stats"][grade] += 1
        
        self.stats["total_interactions"] += 1
        self.save_stats()
    
    def get_daily_summary(self, days=7):
        """Get summary of last N days"""
        today = datetime.now()
        summary = []
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in self.stats["daily_stats"]:
                day_stats = self.stats["daily_stats"][date]
                summary.append({
                    "date": date,
                    "total": day_stats["total"],
                    "successful": day_stats["successful"],
                    "failed": day_stats["failed"],
                    "success_rate": (day_stats["successful"] / day_stats["total"] * 100) if day_stats["total"] > 0 else 0
                })
        
        return summary
    
    def get_top_subjects(self, limit=5):
        """Get top subjects by usage"""
        sorted_subjects = sorted(
            self.stats["subject_stats"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_subjects[:limit]
    
    def get_top_grades(self, limit=5):
        """Get top grades by usage"""
        sorted_grades = sorted(
            self.stats["grade_stats"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_grades[:limit]
    
    def generate_report(self):
        """Generate a comprehensive report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_interactions": self.stats["total_interactions"],
                "total_errors": self.stats["error_count"],
                "error_rate": (self.stats["error_count"] / self.stats["total_interactions"] * 100) if self.stats["total_interactions"] > 0 else 0
            },
            "daily_summary": self.get_daily_summary(7),
            "top_subjects": self.get_top_subjects(5),
            "top_grades": self.get_top_grades(5),
            "recent_activity": self.get_daily_summary(1)
        }
        
        return report
    
    def print_report(self):
        """Print a formatted report to console"""
        report = self.generate_report()
        
        print("📊 Labib Bot Performance Report")
        print("=" * 50)
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Overview
        print("📈 Overview")
        print(f"   Total Interactions: {report['overview']['total_interactions']:,}")
        print(f"   Total Errors: {report['overview']['total_errors']:,}")
        print(f"   Error Rate: {report['overview']['error_rate']:.1f}%")
        print()
        
        # Daily summary
        print("📅 Last 7 Days Activity")
        for day in report['daily_summary']:
            print(f"   {day['date']}: {day['total']} interactions ({day['success_rate']:.1f}% success)")
        print()
        
        # Top subjects
        print("📚 Top Subjects")
        for subject, count in report['top_subjects']:
            print(f"   {subject}: {count} interactions")
        print()
        
        # Top grades
        print("🎓 Top Grades")
        for grade, count in report['top_grades']:
            print(f"   Grade {grade}: {count} interactions")
        print()
        
        # Recent activity
        if report['recent_activity']:
            today = report['recent_activity'][0]
            print("🔥 Today's Activity")
            print(f"   Total: {today['total']} interactions")
            print(f"   Successful: {today['successful']}")
            print(f"   Failed: {today['failed']}")
            print(f"   Success Rate: {today['success_rate']:.1f}%")
    
    def export_csv(self, filename=None):
        """Export daily statistics to CSV"""
        if not filename:
            filename = f"bot_stats_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date', 'total_interactions', 'successful', 'failed', 'success_rate']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for day in self.get_daily_summary(30):  # Last 30 days
                    writer.writerow(day)
            
            print(f"✅ Statistics exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting CSV: {e}")
            return False

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Labib Bot Monitor")
    parser.add_argument("--report", action="store_true", help="Generate and print report")
    parser.add_argument("--export", type=str, help="Export statistics to CSV file")
    parser.add_argument("--watch", action="store_true", help="Watch mode - update every 5 minutes")
    
    args = parser.parse_args()
    
    monitor = BotMonitor()
    
    if args.report:
        monitor.print_report()
    elif args.export:
        monitor.export_csv(args.export)
    elif args.watch:
        print("👀 Watch mode enabled. Press Ctrl+C to stop.")
        try:
            while True:
                monitor.print_report()
                print("\n" + "="*50)
                print("⏳ Waiting 5 minutes...")
                time.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped.")
    else:
        monitor.print_report()

if __name__ == "__main__":
    main()
