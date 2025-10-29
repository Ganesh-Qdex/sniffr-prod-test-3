"""
Performance dashboard for monitoring system metrics
"""
import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import time
from utils.performance import performance_metrics, rate_limiter
from utils.cache import cache_manager

logger = logging.getLogger(__name__)


class PerformanceDashboard:
    """Real-time performance dashboard"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history_size = 1000
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            # Get system metrics
            system_metrics = performance_metrics.get_system_metrics()
            
            # Get performance summary
            performance_summary = performance_metrics.get_summary()
            
            # Get cache statistics
            cache_stats = await self._get_cache_statistics()
            
            # Get rate limiting statistics
            rate_limit_stats = self._get_rate_limit_statistics()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'system': system_metrics,
                'performance': performance_summary,
                'cache': cache_stats,
                'rate_limiting': rate_limit_stats
            }
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}
    
    async def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # This would require Redis INFO command implementation
            # For now, return basic stats
            return {
                'status': 'connected' if cache_manager.redis_client else 'disconnected',
                'hit_rate': 0.0,  # Would need to track this
                'miss_rate': 0.0,  # Would need to track this
                'total_keys': 0,  # Would need to query Redis
                'memory_usage': 0  # Would need to query Redis
            }
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_rate_limit_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        try:
            return {
                'max_requests': rate_limiter.max_requests,
                'time_window': rate_limiter.time_window,
                'active_identifiers': len(rate_limiter.requests),
                'total_requests_tracked': sum(len(requests) for requests in rate_limiter.requests.values())
            }
        except Exception as e:
            logger.error(f"Error getting rate limit statistics: {e}")
            return {'error': str(e)}
    
    async def get_historical_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics for the specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter metrics within time range
        historical_metrics = [
            metric for metric in self.metrics_history
            if datetime.fromisoformat(metric['timestamp']) >= cutoff_time
        ]
        
        return historical_metrics
    
    async def record_metrics(self, metrics: Dict[str, Any]):
        """Record metrics for historical tracking"""
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    async def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds"""
        alerts = []
        current_metrics = await self.get_current_metrics()
        
        try:
            # CPU usage alert
            cpu_percent = current_metrics.get('system', {}).get('cpu_percent', 0)
            if cpu_percent > 80:
                alerts.append({
                    'type': 'high_cpu',
                    'severity': 'warning' if cpu_percent < 90 else 'critical',
                    'message': f'High CPU usage: {cpu_percent:.1f}%',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Memory usage alert
            memory_percent = current_metrics.get('system', {}).get('memory', {}).get('percent', 0)
            if memory_percent > 85:
                alerts.append({
                    'type': 'high_memory',
                    'severity': 'warning' if memory_percent < 95 else 'critical',
                    'message': f'High memory usage: {memory_percent:.1f}%',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Response time alerts
            avg_response_time = current_metrics.get('performance', {}).get('average_response_time', 0)
            if avg_response_time > 2.0:  # 2 seconds
                alerts.append({
                    'type': 'slow_response',
                    'severity': 'warning' if avg_response_time < 5.0 else 'critical',
                    'message': f'Slow average response time: {avg_response_time:.2f}s',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Error rate alerts
            for endpoint, metrics in current_metrics.get('performance', {}).get('endpoints', {}).items():
                error_rate = metrics.get('error_rate', 0)
                if error_rate > 5:  # 5% error rate
                    alerts.append({
                        'type': 'high_error_rate',
                        'severity': 'warning' if error_rate < 10 else 'critical',
                        'message': f'High error rate for {endpoint}: {error_rate:.1f}%',
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Error generating performance alerts: {e}")
        
        return alerts
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            current_metrics = await self.get_current_metrics()
            historical_metrics = await self.get_historical_metrics(24)
            alerts = await self.get_performance_alerts()
            
            # Calculate trends
            trends = self._calculate_trends(historical_metrics)
            
            return {
                'report_timestamp': datetime.utcnow().isoformat(),
                'current_metrics': current_metrics,
                'historical_metrics': historical_metrics,
                'alerts': alerts,
                'trends': trends,
                'summary': self._generate_summary(current_metrics, alerts)
            }
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    def _calculate_trends(self, historical_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance trends"""
        if len(historical_metrics) < 2:
            return {}
        
        try:
            # Calculate CPU trend
            cpu_values = [m.get('system', {}).get('cpu_percent', 0) for m in historical_metrics]
            cpu_trend = 'increasing' if cpu_values[-1] > cpu_values[0] else 'decreasing'
            
            # Calculate memory trend
            memory_values = [m.get('system', {}).get('memory', {}).get('percent', 0) for m in historical_metrics]
            memory_trend = 'increasing' if memory_values[-1] > memory_values[0] else 'decreasing'
            
            # Calculate response time trend
            response_times = [m.get('performance', {}).get('average_response_time', 0) for m in historical_metrics]
            response_trend = 'increasing' if response_times[-1] > response_times[0] else 'decreasing'
            
            return {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend,
                'response_time_trend': response_trend
            }
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
    
    def _generate_summary(self, current_metrics: Dict[str, Any], alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance summary"""
        try:
            critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
            warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
            
            return {
                'overall_status': 'healthy' if not critical_alerts else 'critical',
                'critical_alerts_count': len(critical_alerts),
                'warning_alerts_count': len(warning_alerts),
                'total_alerts': len(alerts),
                'system_health_score': self._calculate_health_score(current_metrics, alerts)
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}
    
    def _calculate_health_score(self, metrics: Dict[str, Any], alerts: List[Dict[str, Any]]) -> int:
        """Calculate overall system health score (0-100)"""
        try:
            score = 100
            
            # Deduct points for alerts
            for alert in alerts:
                if alert.get('severity') == 'critical':
                    score -= 20
                elif alert.get('severity') == 'warning':
                    score -= 10
            
            # Deduct points for high resource usage
            cpu_percent = metrics.get('system', {}).get('cpu_percent', 0)
            if cpu_percent > 90:
                score -= 15
            elif cpu_percent > 80:
                score -= 10
            
            memory_percent = metrics.get('system', {}).get('memory', {}).get('percent', 0)
            if memory_percent > 95:
                score -= 15
            elif memory_percent > 85:
                score -= 10
            
            return max(0, score)
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50  # Default score if calculation fails


# Global dashboard instance
performance_dashboard = PerformanceDashboard()


async def start_performance_monitoring():
    """Start continuous performance monitoring"""
    logger.info("Starting performance monitoring...")
    
    while True:
        try:
            # Get current metrics
            metrics = await performance_dashboard.get_current_metrics()
            
            # Record metrics for historical tracking
            await performance_dashboard.record_metrics(metrics)
            
            # Check for alerts
            alerts = await performance_dashboard.get_performance_alerts()
            if alerts:
                for alert in alerts:
                    logger.warning(f"Performance Alert: {alert['message']}")
            
            # Wait before next check
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in performance monitoring: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(start_performance_monitoring())
