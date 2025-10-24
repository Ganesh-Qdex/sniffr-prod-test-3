"""
Performance monitoring and metrics collection utilities
"""
import time
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import psutil
import os
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Performance metrics collector"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.request_times = deque(maxlen=1000)  # Keep last 1000 requests
        self.error_counts = defaultdict(int)
        self.start_time = time.time()
    
    def record_request_time(self, endpoint: str, duration: float, status: str = "success"):
        """Record request timing metrics"""
        self.request_times.append({
            'endpoint': endpoint,
            'duration': duration,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Update metrics
        self.metrics[f"{endpoint}_times"].append(duration)
        if status != "success":
            self.error_counts[endpoint] += 1
    
    def get_average_response_time(self, endpoint: Optional[str] = None) -> float:
        """Get average response time for endpoint or all endpoints"""
        if endpoint:
            times = self.metrics.get(f"{endpoint}_times", [])
        else:
            times = [req['duration'] for req in self.request_times]
        
        return sum(times) / len(times) if times else 0.0
    
    def get_percentile_response_time(self, endpoint: str, percentile: float = 95.0) -> float:
        """Get percentile response time for endpoint"""
        times = self.metrics.get(f"{endpoint}_times", [])
        if not times:
            return 0.0
        
        sorted_times = sorted(times)
        index = int((percentile / 100.0) * len(sorted_times))
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def get_error_rate(self, endpoint: str) -> float:
        """Get error rate for endpoint"""
        total_requests = len(self.metrics.get(f"{endpoint}_times", []))
        errors = self.error_counts.get(endpoint, 0)
        return (errors / total_requests * 100) if total_requests > 0 else 0.0
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process info
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': process.cpu_percent()
                },
                'uptime': time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {
            'total_requests': len(self.request_times),
            'average_response_time': self.get_average_response_time(),
            'system_metrics': self.get_system_metrics(),
            'endpoints': {}
        }
        
        # Per-endpoint metrics
        for endpoint in set(req['endpoint'] for req in self.request_times):
            summary['endpoints'][endpoint] = {
                'request_count': len(self.metrics.get(f"{endpoint}_times", [])),
                'average_time': self.get_average_response_time(endpoint),
                'p95_time': self.get_percentile_response_time(endpoint, 95.0),
                'p99_time': self.get_percentile_response_time(endpoint, 99.0),
                'error_rate': self.get_error_rate(endpoint)
            }
        
        return summary


# Global metrics instance
performance_metrics = PerformanceMetrics()


def monitor_performance(endpoint: str = "unknown"):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Error in {func.__name__}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                performance_metrics.record_request_time(endpoint, duration, status)
                logger.info(f"{func.__name__} ({endpoint}) completed in {duration:.4f}s")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Error in {func.__name__}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                performance_metrics.record_request_time(endpoint, duration, status)
                logger.info(f"{func.__name__} ({endpoint}) completed in {duration:.4f}s")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class RateLimiter:
    """Rate limiter for request throttling"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""
        now = time.time()
        user_requests = self.requests[identifier]
        
        # Remove old requests outside time window
        while user_requests and user_requests[0] <= now - self.time_window:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        now = time.time()
        user_requests = self.requests[identifier]
        
        # Remove old requests outside time window
        while user_requests and user_requests[0] <= now - self.time_window:
            user_requests.popleft()
        
        return max(0, self.max_requests - len(user_requests))
    
    def get_reset_time(self, identifier: str) -> float:
        """Get time when rate limit resets for identifier"""
        user_requests = self.requests[identifier]
        if not user_requests:
            return 0
        
        return user_requests[0] + self.time_window


# Global rate limiter
rate_limiter = RateLimiter(
    max_requests=int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")),
    time_window=int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60"))
)


def rate_limit(identifier_func: Optional[Callable] = None):
    """Decorator for rate limiting"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get identifier (default to IP or user ID)
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = "default"
            
            if not rate_limiter.is_allowed(identifier):
                remaining = rate_limiter.get_remaining_requests(identifier)
                reset_time = rate_limiter.get_reset_time(identifier)
                raise Exception(f"Rate limit exceeded. Try again in {reset_time:.0f} seconds")
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get identifier (default to IP or user ID)
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = "default"
            
            if not rate_limiter.is_allowed(identifier):
                remaining = rate_limiter.get_remaining_requests(identifier)
                reset_time = rate_limiter.get_reset_time(identifier)
                raise Exception(f"Rate limit exceeded. Try again in {reset_time:.0f} seconds")
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
