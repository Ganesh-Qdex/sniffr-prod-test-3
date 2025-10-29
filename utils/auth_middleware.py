"""
Authentication middleware and decorators
"""

from functools import wraps
from typing import Optional, Callable, Any
import logging

from models.auth import UserRole
from crud.auth_crud import auth_crud
from utils.jwt import verify_token, extract_user_from_token

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Authentication error exception"""
    pass


class AuthorizationError(Exception):
    """Authorization error exception"""
    pass


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for a function
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract token from kwargs or first argument if it's a dict
        token = None
        
        # Try to get token from kwargs
        if 'token' in kwargs:
            token = kwargs['token']
        elif 'authorization' in kwargs:
            auth_header = kwargs['authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        # Try to get token from first argument if it's a dict
        if not token and args and isinstance(args[0], dict):
            token = args[0].get('token') or args[0].get('authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]
        
        if not token:
            raise AuthenticationError("Authentication token required")
        
        # Verify token
        user = await auth_crud.verify_token_user(token)
        if not user:
            raise AuthenticationError("Invalid or expired token")
        
        # Add user to kwargs
        kwargs['current_user'] = user
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_role(required_role: UserRole):
    """
    Decorator to require specific role for a function
    
    Args:
        required_role: Required user role
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if user is authenticated
            if 'current_user' not in kwargs:
                raise AuthenticationError("Authentication required")
            
            user = kwargs['current_user']
            
            # Check role hierarchy
            role_hierarchy = {
                UserRole.USER: 1,
                UserRole.MODERATOR: 2,
                UserRole.ADMIN: 3
            }
            
            user_role_level = role_hierarchy.get(user.role, 0)
            required_role_level = role_hierarchy.get(required_role, 0)
            
            if user_role_level < required_role_level:
                raise AuthorizationError(f"Role {required_role.value} required, but user has {user.role.value}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin role
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    return require_auth(require_role(UserRole.ADMIN)(func))


def require_moderator_or_admin(func: Callable) -> Callable:
    """
    Decorator to require moderator or admin role
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    return require_auth(require_role(UserRole.MODERATOR)(func))


def optional_auth(func: Callable) -> Callable:
    """
    Decorator for optional authentication
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Try to get token
        token = None
        
        if 'token' in kwargs:
            token = kwargs['token']
        elif 'authorization' in kwargs:
            auth_header = kwargs['authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token and args and isinstance(args[0], dict):
            token = args[0].get('token') or args[0].get('authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]
        
        # Try to verify token if present
        current_user = None
        if token:
            try:
                current_user = await auth_crud.verify_token_user(token)
            except Exception:
                # If token is invalid, continue without authentication
                pass
        
        kwargs['current_user'] = current_user
        
        return await func(*args, **kwargs)
    
    return wrapper


class AuthContext:
    """Authentication context manager"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.user = None
    
    async def __aenter__(self):
        """Enter authentication context"""
        if self.token:
            try:
                self.user = await auth_crud.verify_token_user(self.token)
            except Exception as e:
                logger.warning(f"Failed to authenticate user: {e}")
                self.user = None
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit authentication context"""
        pass
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.user is not None
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has specific role"""
        if not self.user:
            return False
        return self.user.role == role
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.has_role(UserRole.ADMIN)
    
    def is_moderator(self) -> bool:
        """Check if user is moderator or admin"""
        return self.has_role(UserRole.MODERATOR) or self.has_role(UserRole.ADMIN)


def check_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Check if user role has permission for required role
    
    Args:
        user_role: User's role
        required_role: Required role
        
    Returns:
        True if user has permission, False otherwise
    """
    role_hierarchy = {
        UserRole.USER: 1,
        UserRole.MODERATOR: 2,
        UserRole.ADMIN: 3
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level


def get_user_from_token(token: str) -> Optional[dict]:
    """
    Get user information from token without database lookup
    
    Args:
        token: JWT token
        
    Returns:
        User information if token is valid, None otherwise
    """
    try:
        return extract_user_from_token(token)
    except Exception as e:
        logger.warning(f"Error extracting user from token: {e}")
        return None
