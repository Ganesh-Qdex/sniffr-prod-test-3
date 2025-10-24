"""
Performance configuration settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Performance Settings
MONGODB_MAX_POOL_SIZE = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
MONGODB_MIN_POOL_SIZE = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
MONGODB_MAX_IDLE_TIME_MS = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000"))

# Redis Cache Settings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
CACHE_USER_TTL = int(os.getenv("CACHE_USER_TTL", "1800"))  # 30 minutes
CACHE_STATS_TTL = int(os.getenv("CACHE_STATS_TTL", "300"))  # 5 minutes

# Rate Limiting Settings
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
RATE_LIMIT_TIME_WINDOW = int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60"))

# Performance Monitoring Settings
PERFORMANCE_MONITORING_ENABLED = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
PERFORMANCE_LOG_LEVEL = os.getenv("PERFORMANCE_LOG_LEVEL", "INFO")

# Bulk Operations Settings
BULK_OPERATION_BATCH_SIZE = int(os.getenv("BULK_OPERATION_BATCH_SIZE", "100"))
BULK_OPERATION_MAX_RETRIES = int(os.getenv("BULK_OPERATION_MAX_RETRIES", "3"))

# Query Optimization Settings
QUERY_TIMEOUT_MS = int(os.getenv("QUERY_TIMEOUT_MS", "30000"))  # 30 seconds
MAX_QUERY_RESULTS = int(os.getenv("MAX_QUERY_RESULTS", "1000"))

# Connection Settings
CONNECTION_TIMEOUT_MS = int(os.getenv("CONNECTION_TIMEOUT_MS", "10000"))  # 10 seconds
SOCKET_TIMEOUT_MS = int(os.getenv("SOCKET_TIMEOUT_MS", "20000"))  # 20 seconds
SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("SERVER_SELECTION_TIMEOUT_MS", "5000"))  # 5 seconds

# Performance Testing Settings
PERFORMANCE_TEST_DURATION = int(os.getenv("PERFORMANCE_TEST_DURATION", "60"))  # 60 seconds
PERFORMANCE_TEST_CONCURRENT_USERS = int(os.getenv("PERFORMANCE_TEST_CONCURRENT_USERS", "10"))
PERFORMANCE_TEST_ITERATIONS = int(os.getenv("PERFORMANCE_TEST_ITERATIONS", "1000"))

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'performance': {
            'format': '%(asctime)s - PERFORMANCE - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'performance': {
            'level': 'INFO',
            'formatter': 'performance',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'performance.log',
            'mode': 'a',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'performance': {
            'handlers': ['performance', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
