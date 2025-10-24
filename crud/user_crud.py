from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
import logging

from models.user import User, UserCreate, UserUpdate, UserResponse
from database.connection import get_collection
from config import USERS_COLLECTION

logger = logging.getLogger(__name__)


class UserCRUD:
    """User CRUD operations for MongoDB"""
    
    def __init__(self):
        self.collection = get_collection(USERS_COLLECTION)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            # Convert to dict and add timestamps
            user_dict = user_data.dict()
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            
            # Insert user into database
            result = self.collection.insert_one(user_dict)
            
            # Retrieve the created user
            created_user = self.collection.find_one({"_id": result.inserted_id})
            
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
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            
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
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            user = self.collection.find_one({"email": email})
            
            if not user:
                return None
            
            return self._convert_to_response(user)
            
        except PyMongoError as e:
            logger.error(f"Database error getting user by email: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by email: {e}")
            raise
    
    async def get_users(self, skip: int = 0, limit: int = 100, 
                       is_active: Optional[bool] = None) -> List[UserResponse]:
        """Get list of users with pagination and filtering"""
        try:
            # Build query
            query = {}
            if is_active is not None:
                query["is_active"] = is_active
            
            # Execute query with pagination
            cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            users = list(cursor)
            
            return [self._convert_to_response(user) for user in users]
            
        except PyMongoError as e:
            logger.error(f"Database error getting users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting users: {e}")
            raise
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user by ID"""
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
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return None
            
            # Retrieve updated user
            updated_user = self.collection.find_one({"_id": ObjectId(user_id)})
            
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
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            
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
    
    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Search users by name or email"""
        try:
            # Create text search query
            query = {
                "$or": [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            users = list(cursor)
            
            return [self._convert_to_response(user) for user in users]
            
        except PyMongoError as e:
            logger.error(f"Database error searching users: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error searching users: {e}")
            raise
    
    async def get_user_count(self, is_active: Optional[bool] = None) -> int:
        """Get total count of users"""
        try:
            query = {}
            if is_active is not None:
                query["is_active"] = is_active
            
            return self.collection.count_documents(query)
            
        except PyMongoError as e:
            logger.error(f"Database error getting user count: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user count: {e}")
            raise
    
    def _convert_to_response(self, user_doc: Dict[str, Any]) -> UserResponse:
        """Convert MongoDB document to UserResponse"""
        from models.auth import UserRole
        
        return UserResponse(
            id=str(user_doc["_id"]),
            name=user_doc["name"],
            email=user_doc["email"],
            age=user_doc.get("age"),
            phone=user_doc.get("phone"),
            address=user_doc.get("address"),
            is_active=user_doc.get("is_active", True),
            role=UserRole(user_doc.get("role", "user")),
            last_login=user_doc.get("last_login"),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )


# Create global instance
user_crud = UserCRUD()
