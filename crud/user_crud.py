from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
import logging
import asyncio
from functools import wraps
import time

from models.user import User, UserCreate, UserUpdate, UserResponse
from database.connection import get_collection_async, get_collection
from config import USERS_COLLECTION

logger = logging.getLogger(__name__)


def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    return wrapper


class UserCRUD:
    """User CRUD operations for MongoDB with performance optimizations"""
    
    def __init__(self):
        self.collection = None
        self._initialized = False
    
    async def _ensure_collection(self):
        """Ensure collection is initialized"""
        if not self._initialized:
            self.collection = await get_collection_async(USERS_COLLECTION)
            self._initialized = True
    
    @performance_monitor
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user with performance monitoring"""
        await self._ensure_collection()
        try:
            # Convert to dict and add timestamps
            user_dict = user_data.dict()
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            
            # Insert user into database
            result = await self.collection.insert_one(user_dict)
            
            # Retrieve the created user
            created_user = await self.collection.find_one({"_id": result.inserted_id})
            
            if not created_user:
                raise Exception("Failed to retrieve created user")
            
            # Convert to response format
            return self._convert_to_response(created_user)
            
        except DuplicateKeyError:
            logger.error(f"User with email {user_data.email} already exists")
            raise ValueError(f"User with email {user_data.email} already exists")
        except PyMongoError as e:
            logger.error(f"Database error creating user: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            raise
    
    @performance_monitor
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID with performance monitoring"""
        await self._ensure_collection()
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return None
            
            return self._convert_to_response(user)
            
        except ValueError as e:
            logger.error(f"Invalid user ID: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error getting user: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user: {e}")
            raise
    
    @performance_monitor
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email with performance monitoring"""
        await self._ensure_collection()
        try:
            user = await self.collection.find_one({"email": email})
            
            if not user:
                return None
            
            return self._convert_to_response(user)
            
        except PyMongoError as e:
            logger.error(f"Database error getting user by email: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by email: {e}")
            raise
    
    @performance_monitor
    async def get_users(self, skip: int = 0, limit: int = 100, 
                       is_active: Optional[bool] = None) -> List[UserResponse]:
        """Get list of users with pagination and filtering with performance monitoring"""
        await self._ensure_collection()
        try:
            # Build query
            query = {}
            if is_active is not None:
                query["is_active"] = is_active
            
            # Execute query with pagination
            cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            users = await cursor.to_list(length=limit)
            
            return [self._convert_to_response(user) for user in users]
            
        except PyMongoError as e:
            logger.error(f"Database error getting users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting users: {e}")
            raise
    
    @performance_monitor
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user by ID with performance monitoring"""
        await self._ensure_collection()
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            # Prepare update data
            update_data = {k: v for k, v in user_data.dict().items() if v is not None}
            
            if not update_data:
                raise ValueError("No valid fields to update")
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update user
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return None
            
            # Retrieve updated user
            updated_user = await self.collection.find_one({"_id": ObjectId(user_id)})
            
            if not updated_user:
                raise Exception("Failed to retrieve updated user")
            
            return self._convert_to_response(updated_user)
            
        except ValueError as e:
            logger.error(f"Invalid user ID or update data: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error updating user: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating user: {e}")
            raise
    
    @performance_monitor
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID with performance monitoring"""
        await self._ensure_collection()
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            
            return result.deleted_count > 0
            
        except ValueError as e:
            logger.error(f"Invalid user ID: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error deleting user: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting user: {e}")
            raise
    
    @performance_monitor
    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Search users by name or email with performance monitoring"""
        await self._ensure_collection()
        try:
            # Create text search query
            query = {
                "$or": [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            users = await cursor.to_list(length=limit)
            
            return [self._convert_to_response(user) for user in users]
            
        except PyMongoError as e:
            logger.error(f"Database error searching users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error searching users: {e}")
            raise
    
    @performance_monitor
    async def get_user_count(self, is_active: Optional[bool] = None) -> int:
        """Get total count of users with performance monitoring"""
        await self._ensure_collection()
        try:
            query = {}
            if is_active is not None:
                query["is_active"] = is_active
            
            return await self.collection.count_documents(query)
            
        except PyMongoError as e:
            logger.error(f"Database error getting user count: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user count: {e}")
            raise
    
    @performance_monitor
    async def bulk_create_users(self, users_data: List[UserCreate]) -> List[UserResponse]:
        """Bulk create users for better performance"""
        await self._ensure_collection()
        try:
            # Prepare documents
            documents = []
            for user_data in users_data:
                user_dict = user_data.dict()
                user_dict["created_at"] = datetime.utcnow()
                user_dict["updated_at"] = datetime.utcnow()
                documents.append(user_dict)
            
            # Bulk insert
            result = await self.collection.insert_many(documents)
            
            # Retrieve created users
            created_users = await self.collection.find(
                {"_id": {"$in": result.inserted_ids}}
            ).to_list(length=None)
            
            return [self._convert_to_response(user) for user in created_users]
            
        except PyMongoError as e:
            logger.error(f"Database error bulk creating users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error bulk creating users: {e}")
            raise
    
    @performance_monitor
    async def bulk_update_users(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update users for better performance"""
        await self._ensure_collection()
        try:
            # Prepare bulk operations
            operations = []
            for update in updates:
                user_id = update.pop("user_id")
                if not ObjectId.is_valid(user_id):
                    continue
                
                update["updated_at"] = datetime.utcnow()
                operations.append({
                    "updateOne": {
                        "filter": {"_id": ObjectId(user_id)},
                        "update": {"$set": update}
                    }
                })
            
            if not operations:
                return 0
            
            # Execute bulk operations
            result = await self.collection.bulk_write(operations)
            return result.modified_count
            
        except PyMongoError as e:
            logger.error(f"Database error bulk updating users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error bulk updating users: {e}")
            raise
    
    @performance_monitor
    async def bulk_delete_users(self, user_ids: List[str]) -> int:
        """Bulk delete users for better performance"""
        await self._ensure_collection()
        try:
            # Validate and convert ObjectIds
            valid_object_ids = []
            for user_id in user_ids:
                if ObjectId.is_valid(user_id):
                    valid_object_ids.append(ObjectId(user_id))
            
            if not valid_object_ids:
                return 0
            
            # Bulk delete
            result = await self.collection.delete_many({"_id": {"$in": valid_object_ids}})
            return result.deleted_count
            
        except PyMongoError as e:
            logger.error(f"Database error bulk deleting users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error bulk deleting users: {e}")
            raise

    def _convert_to_response(self, user_doc: Dict[str, Any]) -> UserResponse:
        """Convert MongoDB document to UserResponse"""
        return UserResponse(
            id=str(user_doc["_id"]),
            name=user_doc["name"],
            email=user_doc["email"],
            age=user_doc.get("age"),
            phone=user_doc.get("phone"),
            address=user_doc.get("address"),
            is_active=user_doc.get("is_active", True),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )


# Create global instance
user_crud = UserCRUD()
