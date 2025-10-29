"""
JWT token utilities for authentication
"""

from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Raises:
        Exception: If token creation fails
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise Exception("Failed to create access token")


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token
        
    Returns:
        Encoded JWT refresh token string
        
    Raises:
        Exception: If token creation fails
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise Exception("Failed to create refresh token")


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload if valid, None otherwise
        
    Raises:
        Exception: If token verification fails
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise Exception("Failed to verify token")


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a token
    
    Args:
        token: JWT token
        
    Returns:
        Expiration datetime if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except Exception:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired
    
    Args:
        token: JWT token
        
    Returns:
        True if expired, False otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        exp = payload.get("exp")
        if exp:
            return datetime.utcnow() > datetime.fromtimestamp(exp)
        return True
    except Exception:
        return True


def create_token_pair(user_id: str, email: str, role: str) -> Dict[str, Any]:
    """
    Create both access and refresh tokens for a user
    
    Args:
        user_id: User ID
        email: User email
        role: User role
        
    Returns:
        Dictionary containing access_token, refresh_token, and expiration info
    """
    try:
        token_data = {
            "user_id": user_id,
            "email": email,
            "role": role
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
            "user_id": user_id,
            "user_email": email,
            "user_role": role
        }
        
    except Exception as e:
        logger.error(f"Error creating token pair: {e}")
        raise Exception("Failed to create token pair")


def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract user information from a token
    
    Args:
        token: JWT token
        
    Returns:
        User information dictionary if valid, None otherwise
    """
    try:
        payload = verify_token(token, "access")
        if payload:
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "role": payload.get("role")
            }
        return None
    except Exception as e:
        logger.error(f"Error extracting user from token: {e}")
        return None
