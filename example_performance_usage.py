#!/usr/bin/env python3
"""
Example usage of performance features
"""
import asyncio
import logging
from datetime import datetime
from crud.user_crud import user_crud
from models.user import UserCreate, UserUpdate
from database.connection import connect_to_mongo, close_mongo_connection
from utils.performance import performance_metrics, rate_limiter
from utils.cache import cache_manager
from utils.performance_dashboard import performance_dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_performance_features():
    """Demonstrate various performance features"""
    
    print("🚀 Sniffr Performance Implementation Demo")
    print("=" * 50)
    
    try:
        # Connect to database with performance optimizations
        print("📡 Connecting to database with connection pooling...")
        await connect_to_mongo()
        
        # Demonstrate caching
        print("\n🗄️ Testing cache functionality...")
        test_key = "demo_user_123"
        test_data = {"name": "Demo User", "email": "demo@example.com"}
        
        # Set cache
        await cache_manager.set(test_key, test_data, ttl=300)
        print(f"✅ Cached data for key: {test_key}")
        
        # Get from cache
        cached_data = await cache_manager.get(test_key)
        print(f"📥 Retrieved from cache: {cached_data}")
        
        # Demonstrate rate limiting
        print("\n🚦 Testing rate limiting...")
        for i in range(5):
            allowed = rate_limiter.is_allowed("demo_user")
            print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Rate limited'}")
        
        # Demonstrate performance monitoring
        print("\n📊 Testing performance monitoring...")
        
        # Create a test user with monitoring
        print("👤 Creating test user with performance monitoring...")
        user_data = UserCreate(
            name="Performance Test User",
            email="perf.test@example.com",
            age=25,
            phone="+1234567890",
            address="123 Performance St, Test City, TC 12345"
        )
        
        start_time = datetime.now()
        created_user = await user_crud.create_user(user_data)
        end_time = datetime.now()
        
        print(f"✅ User created in {(end_time - start_time).total_seconds():.4f} seconds")
        print(f"🆔 User ID: {created_user.id}")
        
        # Demonstrate bulk operations
        print("\n📦 Testing bulk operations...")
        bulk_users = []
        for i in range(5):
            bulk_users.append(UserCreate(
                name=f"Bulk User {i}",
                email=f"bulk{i}@example.com",
                age=20 + i,
                is_active=True
            ))
        
        start_time = datetime.now()
        bulk_created = await user_crud.bulk_create_users(bulk_users)
        end_time = datetime.now()
        
        print(f"✅ Created {len(bulk_created)} users in bulk in {(end_time - start_time).total_seconds():.4f} seconds")
        
        # Demonstrate performance metrics
        print("\n📈 Performance Metrics:")
        summary = performance_metrics.get_summary()
        print(f"📊 Total requests: {summary.get('total_requests', 0)}")
        print(f"⚡ Average response time: {summary.get('average_response_time', 0):.4f}s")
        
        # Demonstrate performance dashboard
        print("\n🏥 System Health Check:")
        current_metrics = await performance_dashboard.get_current_metrics()
        
        system_metrics = current_metrics.get('system', {})
        print(f"💻 CPU Usage: {system_metrics.get('cpu_percent', 0):.1f}%")
        print(f"🧠 Memory Usage: {system_metrics.get('memory', {}).get('percent', 0):.1f}%")
        
        # Check for alerts
        alerts = await performance_dashboard.get_performance_alerts()
        if alerts:
            print(f"🚨 Found {len(alerts)} performance alerts")
            for alert in alerts:
                print(f"   ⚠️ {alert['message']}")
        else:
            print("✅ No performance alerts")
        
        # Demonstrate search with performance monitoring
        print("\n🔍 Testing search performance...")
        start_time = datetime.now()
        search_results = await user_crud.search_users("Performance")
        end_time = datetime.now()
        
        print(f"🔍 Found {len(search_results)} users matching 'Performance' in {(end_time - start_time).total_seconds():.4f} seconds")
        
        # Demonstrate bulk update
        print("\n✏️ Testing bulk update...")
        updates = []
        for user in bulk_created:
            updates.append({
                "user_id": user.id,
                "phone": f"+1{5550000000 + int(user.id[-4:])}",
                "address": f"Updated Address for {user.name}"
            })
        
        start_time = datetime.now()
        updated_count = await user_crud.bulk_update_users(updates)
        end_time = datetime.now()
        
        print(f"✅ Updated {updated_count} users in bulk in {(end_time - start_time).total_seconds():.4f} seconds")
        
        # Generate performance report
        print("\n📋 Generating performance report...")
        report = await performance_dashboard.generate_performance_report()
        
        summary = report.get('summary', {})
        health_score = summary.get('system_health_score', 0)
        print(f"🏥 System Health Score: {health_score}/100")
        print(f"📊 Overall Status: {summary.get('overall_status', 'unknown')}")
        
        print("\n✅ Performance demonstration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        logger.exception("Error in performance demonstration")
    
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        await close_mongo_connection()
        await cache_manager.close()
        print("✅ Cleanup completed")


async def run_performance_benchmark():
    """Run a simple performance benchmark"""
    
    print("\n🏃‍♂️ Running Performance Benchmark")
    print("=" * 40)
    
    try:
        await connect_to_mongo()
        
        # Benchmark user creation
        print("📝 Benchmarking user creation...")
        start_time = datetime.now()
        
        for i in range(10):
            user_data = UserCreate(
                name=f"Benchmark User {i}",
                email=f"benchmark{i}@example.com",
                age=25 + i,
                is_active=True
            )
            await user_crud.create_user(user_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Created 10 users in {duration:.4f} seconds")
        print(f"⚡ Average time per user: {duration/10:.4f} seconds")
        print(f"🚀 Users per second: {10/duration:.2f}")
        
        # Benchmark user retrieval
        print("\n📖 Benchmarking user retrieval...")
        start_time = datetime.now()
        
        users = await user_crud.get_users(skip=0, limit=20)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Retrieved {len(users)} users in {duration:.4f} seconds")
        print(f"⚡ Average time per user: {duration/len(users):.4f} seconds")
        
    except Exception as e:
        print(f"❌ Error during benchmark: {e}")
        logger.exception("Error in performance benchmark")
    
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    print("🎯 Sniffr Performance Implementation Demo")
    print("This demo showcases the performance optimizations implemented in the system.")
    print()
    
    # Run the demonstration
    asyncio.run(demonstrate_performance_features())
    
    # Run benchmark
    asyncio.run(run_performance_benchmark())
    
    print("\n🎉 Demo completed! Check the performance logs for detailed metrics.")
    print("💡 Use 'python performance_cli.py' for more performance tools.")
