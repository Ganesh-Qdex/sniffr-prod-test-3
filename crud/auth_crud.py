"""
Authentication CRUD operations
"""

from typing import Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
import logging

from models.user import UserResponse
from models.auth import UserCreateWithAuth, LoginRequest, UserWithAuth, UserRole
from database.connection import get_collection
from config import USERS_COLLECTION
from utils.password import hash_password, verify_password
from utils.jwt import create_token_pair, verify_token

logger = logging.getLogger(__name__)


class AuthCRUD:
    """Authentication CRUD operations for MongoDB"""
    
    def __init__(self):
        self.collection = get_collection(USERS_COLLECTION)
    
    async def create_user_with_auth(self, user_data: UserCreateWithAuth) -> UserResponse:
        """
        Create a new user with authentication
        
        Args:
            user_data: User creation data with authentication
            
        Returns:
            Created user response
            
        Raises:
            ValueError: If user already exists or validation fails
            Exception: If database operation fails
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ValueError(f"User with email {user_data.email} already exists")
            
            # Hash the password
            hashed_password = hash_password(user_data.password)
            
            # Prepare user document
            user_dict = user_data.dict()
            user_dict.pop("password")  # Remove plain password
            user_dict["password_hash"] = hashed_password
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            user_dict["last_login"] = None
            
            # Insert user into database
            result = self.collection.insert_one(user_dict)
            
            # Retrieve the created user
            created_user = self.collection.find_one({"_id": result.inserted_id})
            
            if not created_user:
                raise Exception("Failed to retrieve created user")
            
            # Convert to response format
            return self._convert_to_response(created_user)
            
        except ValueError as e:
            logger.error(f"Validation error creating user: {e}")
            raise
        except DuplicateKeyError:
            logger.error(f"User with email {user_data.email} already exists")
            raise ValueError(f"User with email {user_data.email} already exists")
        except PyMongoError as e:
            logger.error(f"Database error creating user: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            raise
    
    async def authenticate_user(self, login_data: LoginRequest) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password
        
        Args:
            login_data: Login credentials
            
        Returns:
            User data with tokens if authentication successful, None otherwise
            
        Raises:
            Exception: If authentication fails
        """
        try:
            # Get user by email
            user = await self.get_user_by_email(login_data.email)
            if not user:
                logger.warning(f"Login attempt with non-existent email: {login_data.email}")
                return None
            
            # Get full user document with password hash
            user_doc = self.collection.find_one({"email": login_data.email})
            if not user_doc:
                return None
            
            # Verify password
            if not verify_password(login_data.password, user_doc["password_hash"]):
                logger.warning(f"Invalid password for user: {login_data.email}")
                return None
            
            # Check if user is active
            if not user_doc.get("is_active", True):
                logger.warning(f"Login attempt for inactive user: {login_data.email}")
                return None
            
            # Update last login
            self.collection.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Create tokens
            token_data = create_token_pair(
                user_id=str(user_doc["_id"]),
                email=user_doc["email"],
                role=user_doc.get("role", "user")
            )
            
            return {
                "user": self._convert_to_response(user_doc),
                "tokens": token_data
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Get user by email (without password hash)
        
        Args:
            email: User email
            
        Returns:
            User response if found, None otherwise
        """
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
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID (without password hash)
        
        Args:
            user_id: User ID
            
        Returns:
            User response if found, None otherwise
        """
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
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            # Get user document with password hash
            user_doc = self.collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return False
            
            # Verify current password
            if not verify_password(current_password, user_doc["password_hash"]):
                logger.warning(f"Invalid current password for user: {user_id}")
                return False
            
            # Hash new password
            new_password_hash = hash_password(new_password)
            
            # Update password
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except ValueError as e:
            logger.error(f"Invalid user ID: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error changing password: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error changing password: {e}")
            raise
    
    async def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """
        Update user role
        
        Args:
            user_id: User ID
            new_role: New user role
            
        Returns:
            True if role updated successfully, False otherwise
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "role": new_role.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except ValueError as e:
            logger.error(f"Invalid user ID: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error updating role: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating role: {e}")
            raise
    
    async def verify_token_user(self, token: str) -> Optional[UserResponse]:
        """
        Verify token and return user information
        
        Args:
            token: JWT token
            
        Returns:
            User information if token is valid, None otherwise
        """
        try:
            payload = verify_token(token, "access")
            if not payload:
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            return await self.get_user_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
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
            role=UserRole(user_doc.get("role", "user")),
            last_login=user_doc.get("last_login"),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )


# Create global instance
auth_crud = AuthCRUD()
