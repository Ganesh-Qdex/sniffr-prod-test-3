import os
import asyncio
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None
    sync_client: Optional[MongoClient] = None  # Keep sync client for migrations


# Global database instance
db = Database()


def get_database():
    """Get database connection"""
    return db.database


async def connect_to_mongo():
    """Create async database connection with connection pooling"""
    try:
        # MongoDB connection string
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "sniffr_users")
        
        # Connection pool settings for performance
        max_pool_size = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
        min_pool_size = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
        max_idle_time_ms = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000"))
        
        # Create async MongoDB client with connection pooling
        db.client = AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=max_idle_time_ms,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second timeout
            socketTimeoutMS=20000,  # 20 second timeout
            retryWrites=True,
            retryReads=True,
        )
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB with connection pooling")
        
        # Set the database
        db.database = db.client[database_name]
        
        # Create indexes for better performance
        await create_indexes()
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise


def connect_to_mongo_sync():
    """Create synchronous database connection for migrations and setup"""
    try:
        # MongoDB connection string
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "sniffr_users")
        
        # Create sync MongoDB client
        db.sync_client = MongoClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second timeout
            socketTimeoutMS=20000,  # 20 second timeout
        )
        
        # Test the connection
        db.sync_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB (sync)")
        
        # Set the database
        db.database = db.sync_client[database_name]
        
        # Create indexes for better performance
        create_indexes_sync()
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")
    if db.sync_client:
        db.sync_client.close()
        logger.info("MongoDB sync connection closed")


async def create_indexes():
    """Create database indexes for better performance (async)"""
    try:
        # Create unique index on email
        await db.database.users.create_index("email", unique=True)
        
        # Create index on name for faster searches
        await db.database.users.create_index("name")
        
        # Create index on is_active for filtering
        await db.database.users.create_index("is_active")
        
        # Create compound index for common queries
        await db.database.users.create_index([("is_active", 1), ("created_at", -1)])
        
        # Create text index for full-text search
        await db.database.users.create_index([("name", "text"), ("email", "text")])
        
        # Create index on created_at for sorting
        await db.database.users.create_index("created_at")
        
        # Create index on updated_at for sorting
        await db.database.users.create_index("updated_at")
        
        logger.info("Database indexes created successfully (async)")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def create_indexes_sync():
    """Create database indexes for better performance (sync)"""
    try:
        # Create unique index on email
        db.database.users.create_index("email", unique=True)
        
        # Create index on name for faster searches
        db.database.users.create_index("name")
        
        # Create index on is_active for filtering
        db.database.users.create_index("is_active")
        
        # Create compound index for common queries
        db.database.users.create_index([("is_active", 1), ("created_at", -1)])
        
        # Create text index for full-text search
        db.database.users.create_index([("name", "text"), ("email", "text")])
        
        # Create index on created_at for sorting
        db.database.users.create_index("created_at")
        
        # Create index on updated_at for sorting
        db.database.users.create_index("updated_at")
        
        logger.info("Database indexes created successfully (sync)")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def get_collection(collection_name: str):
    """Get a specific collection from the database"""
    if not db.database:
        # Use sync connection for backward compatibility
        connect_to_mongo_sync()
    return db.database[collection_name]


async def get_collection_async(collection_name: str):
    """Get a specific collection from the database (async)"""
    if not db.database:
        await connect_to_mongo()
    return db.database[collection_name]
