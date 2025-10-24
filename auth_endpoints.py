"""
Authentication endpoints for the application
"""

import asyncio
from typing import Optional
import logging

from models.auth import (
    UserCreateWithAuth, LoginRequest, TokenResponse, 
    PasswordResetRequest, PasswordReset, ChangePassword,
    AuthResponse, UserWithAuth
)
from crud.auth_crud import auth_crud
from utils.password import check_password_strength
from utils.jwt import create_token_pair, verify_token
from utils.auth_middleware import require_auth, require_admin, AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)


class AuthEndpoints:
    """Authentication endpoints handler"""
    
    def __init__(self):
        self.auth_crud = auth_crud
    
    async def register(self, user_data: UserCreateWithAuth) -> AuthResponse:
        """
        Register a new user with authentication
        
        Args:
            user_data: User registration data
            
        Returns:
            Authentication response with user and tokens
            
        Raises:
            ValueError: If validation fails or user already exists
            Exception: If registration fails
        """
        try:
            # Check password strength
            password_check = check_password_strength(user_data.password)
            if not password_check["is_valid"]:
                raise ValueError(f"Password validation failed: {', '.join(password_check['issues'])}")
            
            # Create user
            user = await self.auth_crud.create_user_with_auth(user_data)
            
            # Create tokens
            tokens = create_token_pair(
                user_id=user.id,
                email=user.email,
                role=user.role.value
            )
            
            # Convert to response format
            user_with_auth = UserWithAuth(
                id=user.id,
                name=user.name,
                email=user.email,
                age=user.age,
                phone=user.phone,
                address=user.address,
                is_active=user.is_active,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            
            return AuthResponse(
                user=user_with_auth,
                token=TokenResponse(**tokens)
            )
            
        except ValueError as e:
            logger.error(f"Registration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise Exception(f"Registration failed: {str(e)}")
    
    async def login(self, login_data: LoginRequest) -> AuthResponse:
        """
        Login user with email and password
        
        Args:
            login_data: Login credentials
            
        Returns:
            Authentication response with user and tokens
            
        Raises:
            ValueError: If credentials are invalid
            Exception: If login fails
        """
        try:
            # Authenticate user
            auth_result = await self.auth_crud.authenticate_user(login_data)
            if not auth_result:
                raise ValueError("Invalid email or password")
            
            user = auth_result["user"]
            tokens = auth_result["tokens"]
            
            # Convert to response format
            user_with_auth = UserWithAuth(
                id=user.id,
                name=user.name,
                email=user.email,
                age=user.age,
                phone=user.phone,
                address=user.address,
                is_active=user.is_active,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            
            return AuthResponse(
                user=user_with_auth,
                token=TokenResponse(**tokens)
            )
            
        except ValueError as e:
            logger.error(f"Login validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise Exception(f"Login failed: {str(e)}")
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token
            
        Raises:
            ValueError: If refresh token is invalid
            Exception: If token refresh fails
        """
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, "refresh")
            if not payload:
                raise ValueError("Invalid or expired refresh token")
            
            user_id = payload.get("user_id")
            email = payload.get("email")
            role = payload.get("role")
            
            if not all([user_id, email, role]):
                raise ValueError("Invalid refresh token payload")
            
            # Create new access token
            tokens = create_token_pair(user_id, email, role)
            
            return TokenResponse(**tokens)
            
        except ValueError as e:
            logger.error(f"Token refresh validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")
    
    async def change_password(self, user_id: str, password_data: ChangePassword) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            password_data: Password change data
            
        Returns:
            True if password changed successfully
            
        Raises:
            ValueError: If validation fails
            Exception: If password change fails
        """
        try:
            # Check new password strength
            password_check = check_password_strength(password_data.new_password)
            if not password_check["is_valid"]:
                raise ValueError(f"New password validation failed: {', '.join(password_check['issues'])}")
            
            # Change password
            success = await self.auth_crud.change_password(
                user_id=user_id,
                current_password=password_data.current_password,
                new_password=password_data.new_password
            )
            
            if not success:
                raise ValueError("Current password is incorrect")
            
            return True
            
        except ValueError as e:
            logger.error(f"Password change validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise Exception(f"Password change failed: {str(e)}")
    
    async def get_current_user(self, token: str) -> UserWithAuth:
        """
        Get current user from token
        
        Args:
            token: JWT token
            
        Returns:
            Current user information
            
        Raises:
            ValueError: If token is invalid
            Exception: If user retrieval fails
        """
        try:
            user = await self.auth_crud.verify_token_user(token)
            if not user:
                raise ValueError("Invalid or expired token")
            
            return UserWithAuth(
                id=user.id,
                name=user.name,
                email=user.email,
                age=user.age,
                phone=user.phone,
                address=user.address,
                is_active=user.is_active,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            
        except ValueError as e:
            logger.error(f"Get user validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Get user error: {e}")
            raise Exception(f"Failed to get user: {str(e)}")
    
    async def update_user_role(self, user_id: str, new_role: str, admin_token: str) -> bool:
        """
        Update user role (admin only)
        
        Args:
            user_id: User ID to update
            new_role: New role
            admin_token: Admin authentication token
            
        Returns:
            True if role updated successfully
            
        Raises:
            ValueError: If validation fails
            AuthorizationError: If user is not admin
            Exception: If role update fails
        """
        try:
            # Verify admin token
            admin_user = await self.auth_crud.verify_token_user(admin_token)
            if not admin_user or admin_user.role.value != "admin":
                raise AuthorizationError("Admin privileges required")
            
            # Update role
            from models.auth import UserRole
            role_enum = UserRole(new_role)
            
            success = await self.auth_crud.update_user_role(user_id, role_enum)
            if not success:
                raise ValueError("User not found or role update failed")
            
            return True
            
        except ValueError as e:
            logger.error(f"Role update validation error: {e}")
            raise
        except AuthorizationError as e:
            logger.error(f"Role update authorization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Role update error: {e}")
            raise Exception(f"Role update failed: {str(e)}")


# Create global instance
auth_endpoints = AuthEndpoints()
