import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    client: MongoClient = None
    database = None


# Global database instance
db = Database()


def get_database():
    """Get database connection"""
    return db.database


def connect_to_mongo():
    """Create database connection"""
    try:
        # MongoDB connection string
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "sniffr_users")
        
        # Create MongoDB client
        db.client = MongoClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second timeout
            socketTimeoutMS=20000,  # 20 second timeout
        )
        
        # Test the connection
        db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Set the database
        db.database = db.client[database_name]
        
        # Create indexes for better performance
        create_indexes()
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise


def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Create unique index on email
        db.database.users.create_index("email", unique=True)
        
        # Create index on name for faster searches
        db.database.users.create_index("name")
        
        # Create index on is_active for filtering
        db.database.users.create_index("is_active")
        
        # Create compound index for common queries
        db.database.users.create_index([("is_active", 1), ("created_at", -1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def get_collection(collection_name: str):
    """Get a specific collection from the database"""
    if not db.database:
        connect_to_mongo()
    return db.database[collection_name]
