#!/usr/bin/env python3
"""
Performance CLI tool for monitoring and testing
"""
import asyncio
import argparse
import json
import sys
from datetime import datetime
from utils.performance_dashboard import performance_dashboard
from utils.performance_test import performance_test, run_user_crud_performance_tests
from utils.performance import performance_metrics
from database.connection import connect_to_mongo, close_mongo_connection

logger = logging.getLogger(__name__)


async def show_current_metrics():
    """Show current performance metrics"""
    print("🔍 Fetching current performance metrics...")
    
    try:
        metrics = await performance_dashboard.get_current_metrics()
        
        print("\n📊 Current Performance Metrics:")
        print("=" * 50)
        
        # System metrics
        system = metrics.get('system', {})
        print(f"💻 CPU Usage: {system.get('cpu_percent', 0):.1f}%")
        print(f"🧠 Memory Usage: {system.get('memory', {}).get('percent', 0):.1f}%")
        print(f"💾 Disk Usage: {system.get('disk', {}).get('percent', 0):.1f}%")
        
        # Performance metrics
        performance = metrics.get('performance', {})
        print(f"⚡ Average Response Time: {performance.get('average_response_time', 0):.3f}s")
        print(f"📈 Total Requests: {performance.get('total_requests', 0)}")
        
        # Cache metrics
        cache = metrics.get('cache', {})
        print(f"🗄️ Cache Status: {cache.get('status', 'unknown')}")
        
        # Rate limiting
        rate_limit = metrics.get('rate_limiting', {})
        print(f"🚦 Active Rate Limit Identifiers: {rate_limit.get('active_identifiers', 0)}")
        
    except Exception as e:
        print(f"❌ Error fetching metrics: {e}")


async def show_alerts():
    """Show performance alerts"""
    print("🚨 Checking for performance alerts...")
    
    try:
        alerts = await performance_dashboard.get_performance_alerts()
        
        if not alerts:
            print("✅ No performance alerts")
            return
        
        print(f"\n⚠️ Found {len(alerts)} alerts:")
        print("=" * 50)
        
        for alert in alerts:
            severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
            print(f"{severity_icon} {alert['type'].upper()}: {alert['message']}")
            print(f"   Time: {alert['timestamp']}")
            print()
        
    except Exception as e:
        print(f"❌ Error fetching alerts: {e}")


async def show_health_score():
    """Show system health score"""
    print("🏥 Calculating system health score...")
    
    try:
        metrics = await performance_dashboard.get_current_metrics()
        alerts = await performance_dashboard.get_performance_alerts()
        
        summary = performance_dashboard._generate_summary(metrics, alerts)
        health_score = summary.get('system_health_score', 0)
        
        print(f"\n💚 System Health Score: {health_score}/100")
        
        if health_score >= 90:
            print("🟢 System is healthy")
        elif health_score >= 70:
            print("🟡 System has some issues")
        else:
            print("🔴 System needs attention")
        
        print(f"📊 Status: {summary.get('overall_status', 'unknown')}")
        print(f"🚨 Critical Alerts: {summary.get('critical_alerts_count', 0)}")
        print(f"⚠️ Warning Alerts: {summary.get('warning_alerts_count', 0)}")
        
    except Exception as e:
        print(f"❌ Error calculating health score: {e}")


async def run_performance_tests():
    """Run performance tests"""
    print("🧪 Running performance tests...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        
        # Run tests
        await run_user_crud_performance_tests()
        
        print("✅ Performance tests completed")
        print("📄 Report saved as 'user_crud_performance_report.json'")
        
    except Exception as e:
        print(f"❌ Error running performance tests: {e}")
    finally:
        await close_mongo_connection()


async def generate_report():
    """Generate performance report"""
    print("📋 Generating performance report...")
    
    try:
        report = await performance_dashboard.generate_performance_report()
        
        # Save report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Performance report generated: {filename}")
        
        # Show summary
        summary = report.get('summary', {})
        print(f"🏥 Health Score: {summary.get('system_health_score', 0)}/100")
        print(f"📊 Status: {summary.get('overall_status', 'unknown')}")
        print(f"🚨 Alerts: {summary.get('total_alerts', 0)}")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")


async def monitor_continuous():
    """Start continuous monitoring"""
    print("📡 Starting continuous performance monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
            
            # Show current metrics
            await show_current_metrics()
            
            # Show alerts
            await show_alerts()
            
            # Wait 30 seconds
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Performance CLI Tool")
    parser.add_argument('command', choices=[
        'metrics', 'alerts', 'health', 'test', 'report', 'monitor'
    ], help='Command to execute')
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        if args.command == 'metrics':
            asyncio.run(show_current_metrics())
        elif args.command == 'alerts':
            asyncio.run(show_alerts())
        elif args.command == 'health':
            asyncio.run(show_health_score())
        elif args.command == 'test':
            asyncio.run(run_performance_tests())
        elif args.command == 'report':
            asyncio.run(generate_report())
        elif args.command == 'monitor':
            asyncio.run(monitor_continuous())
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
