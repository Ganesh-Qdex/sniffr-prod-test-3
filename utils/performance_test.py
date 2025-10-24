"""
Performance testing utilities and benchmarks
"""
import asyncio
import time
import statistics
import logging
from typing import List, Dict, Any, Callable, Optional
import json
from datetime import datetime
import random
import string

logger = logging.getLogger(__name__)


class PerformanceTest:
    """Performance testing framework"""
    
    def __init__(self):
        self.results = []
    
    async def run_load_test(self, 
                           func: Callable, 
                           args: List[Any] = None, 
                           kwargs: Dict[str, Any] = None,
                           concurrent_users: int = 10,
                           duration_seconds: int = 60) -> Dict[str, Any]:
        """Run load test on a function"""
        args = args or []
        kwargs = kwargs or {}
        
        start_time = time.time()
        results = []
        errors = 0
        
        async def worker():
            nonlocal errors
            while time.time() - start_time < duration_seconds:
                try:
                    worker_start = time.time()
                    await func(*args, **kwargs)
                    worker_duration = time.time() - worker_start
                    results.append(worker_duration)
                except Exception as e:
                    errors += 1
                    logger.error(f"Load test error: {e}")
        
        # Start concurrent workers
        tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]
        
        # Wait for duration
        await asyncio.sleep(duration_seconds)
        
        # Cancel remaining tasks
        for task in tasks:
            task.cancel()
        
        # Calculate metrics
        if results:
            avg_response_time = statistics.mean(results)
            p95_response_time = statistics.quantiles(results, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(results, n=100)[98]  # 99th percentile
            min_response_time = min(results)
            max_response_time = max(results)
            requests_per_second = len(results) / duration_seconds
        else:
            avg_response_time = p95_response_time = p99_response_time = 0
            min_response_time = max_response_time = 0
            requests_per_second = 0
        
        test_result = {
            'test_type': 'load_test',
            'concurrent_users': concurrent_users,
            'duration_seconds': duration_seconds,
            'total_requests': len(results),
            'errors': errors,
            'requests_per_second': requests_per_second,
            'response_times': {
                'average': avg_response_time,
                'p95': p95_response_time,
                'p99': p99_response_time,
                'min': min_response_time,
                'max': max_response_time
            },
            'error_rate': (errors / (len(results) + errors)) * 100 if (len(results) + errors) > 0 else 0
        }
        
        self.results.append(test_result)
        return test_result
    
    async def run_stress_test(self, 
                             func: Callable, 
                             args: List[Any] = None, 
                             kwargs: Dict[str, Any] = None,
                             max_concurrent_users: int = 100,
                             step_size: int = 10) -> Dict[str, Any]:
        """Run stress test to find breaking point"""
        args = args or []
        kwargs = kwargs or {}
        
        stress_results = []
        
        for concurrent_users in range(step_size, max_concurrent_users + 1, step_size):
            logger.info(f"Testing with {concurrent_users} concurrent users")
            
            start_time = time.time()
            results = []
            errors = 0
            
            async def worker():
                nonlocal errors
                try:
                    worker_start = time.time()
                    await func(*args, **kwargs)
                    worker_duration = time.time() - worker_start
                    results.append(worker_duration)
                except Exception as e:
                    errors += 1
                    logger.error(f"Stress test error: {e}")
            
            # Run for 30 seconds per step
            tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]
            await asyncio.sleep(30)
            
            # Cancel remaining tasks
            for task in tasks:
                task.cancel()
            
            # Calculate metrics for this step
            if results:
                avg_response_time = statistics.mean(results)
                requests_per_second = len(results) / 30
                error_rate = (errors / (len(results) + errors)) * 100 if (len(results) + errors) > 0 else 0
            else:
                avg_response_time = 0
                requests_per_second = 0
                error_rate = 100
            
            step_result = {
                'concurrent_users': concurrent_users,
                'total_requests': len(results),
                'errors': errors,
                'requests_per_second': requests_per_second,
                'average_response_time': avg_response_time,
                'error_rate': error_rate
            }
            
            stress_results.append(step_result)
            
            # Stop if error rate is too high
            if error_rate > 50:
                logger.info(f"Breaking point reached at {concurrent_users} concurrent users")
                break
        
        test_result = {
            'test_type': 'stress_test',
            'max_concurrent_users': max_concurrent_users,
            'step_size': step_size,
            'steps': stress_results
        }
        
        self.results.append(test_result)
        return test_result
    
    async def run_benchmark(self, 
                           func: Callable, 
                           args: List[Any] = None, 
                           kwargs: Dict[str, Any] = None,
                           iterations: int = 1000) -> Dict[str, Any]:
        """Run benchmark test"""
        args = args or []
        kwargs = kwargs or {}
        
        results = []
        
        for i in range(iterations):
            start_time = time.time()
            try:
                await func(*args, **kwargs)
                duration = time.time() - start_time
                results.append(duration)
            except Exception as e:
                logger.error(f"Benchmark error: {e}")
                results.append(float('inf'))  # Mark as failed
        
        # Calculate statistics
        valid_results = [r for r in results if r != float('inf')]
        failed_count = len(results) - len(valid_results)
        
        if valid_results:
            avg_time = statistics.mean(valid_results)
            median_time = statistics.median(valid_results)
            p95_time = statistics.quantiles(valid_results, n=20)[18]
            p99_time = statistics.quantiles(valid_results, n=100)[98]
            min_time = min(valid_results)
            max_time = max(valid_results)
            std_dev = statistics.stdev(valid_results) if len(valid_results) > 1 else 0
        else:
            avg_time = median_time = p95_time = p99_time = 0
            min_time = max_time = std_dev = 0
        
        test_result = {
            'test_type': 'benchmark',
            'iterations': iterations,
            'successful_iterations': len(valid_results),
            'failed_iterations': failed_count,
            'success_rate': (len(valid_results) / iterations) * 100,
            'response_times': {
                'average': avg_time,
                'median': median_time,
                'p95': p95_time,
                'p99': p99_time,
                'min': min_time,
                'max': max_time,
                'std_deviation': std_dev
            }
        }
        
        self.results.append(test_result)
        return test_result
    
    def generate_report(self) -> str:
        """Generate performance test report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': len(self.results),
            'tests': self.results
        }
        
        return json.dumps(report, indent=2)
    
    def save_report(self, filename: str = None):
        """Save performance test report to file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Performance report saved to {filename}")


# Global performance test instance
performance_test = PerformanceTest()


def generate_test_data(num_users: int = 100) -> List[Dict[str, Any]]:
    """Generate test data for performance testing"""
    test_users = []
    
    for i in range(num_users):
        user = {
            'name': f"Test User {i}",
            'email': f"testuser{i}@example.com",
            'age': random.randint(18, 80),
            'phone': f"+1{random.randint(1000000000, 9999999999)}",
            'address': f"{random.randint(1, 9999)} Test Street, Test City, TS {random.randint(10000, 99999)}",
            'is_active': random.choice([True, False])
        }
        test_users.append(user)
    
    return test_users


async def run_user_crud_performance_tests():
    """Run comprehensive performance tests for user CRUD operations"""
    from crud.user_crud import user_crud
    from models.user import UserCreate
    
    logger.info("Starting User CRUD Performance Tests")
    
    # Test data
    test_users = generate_test_data(100)
    user_creates = [UserCreate(**user) for user in test_users]
    
    # Test 1: Create user benchmark
    logger.info("Running create user benchmark...")
    await performance_test.run_benchmark(
        user_crud.create_user,
        args=[user_creates[0]],
        iterations=100
    )
    
    # Test 2: Get user by ID benchmark
    logger.info("Running get user by ID benchmark...")
    # First create a user to test with
    created_user = await user_crud.create_user(user_creates[0])
    await performance_test.run_benchmark(
        user_crud.get_user_by_id,
        args=[created_user.id],
        iterations=100
    )
    
    # Test 3: Bulk create load test
    logger.info("Running bulk create load test...")
    await performance_test.run_load_test(
        user_crud.bulk_create_users,
        args=[user_creates[:10]],  # Create 10 users at a time
        concurrent_users=5,
        duration_seconds=30
    )
    
    # Test 4: Get users stress test
    logger.info("Running get users stress test...")
    await performance_test.run_stress_test(
        user_crud.get_users,
        kwargs={'skip': 0, 'limit': 20},
        max_concurrent_users=50,
        step_size=5
    )
    
    # Generate and save report
    performance_test.save_report("user_crud_performance_report.json")
    logger.info("Performance tests completed. Report saved.")


if __name__ == "__main__":
    asyncio.run(run_user_crud_performance_tests())
