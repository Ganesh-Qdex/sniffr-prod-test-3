"""
Password hashing and verification utilities
"""

from passlib.context import CryptContext
from passlib.exc import InvalidTokenError, InvalidHashError
import logging

logger = logging.getLogger(__name__)

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    Raises:
        Exception: If hashing fails
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise Exception("Failed to hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
        
    Raises:
        Exception: If verification fails
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (InvalidTokenError, InvalidHashError) as e:
        logger.error(f"Invalid hash format: {e}")
        return False
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        raise Exception("Failed to verify password")


def check_password_strength(password: str) -> dict:
    """
    Check password strength and return validation results
    
    Args:
        password: Password to check
        
    Returns:
        Dictionary with strength analysis
    """
    result = {
        "is_valid": True,
        "score": 0,
        "issues": [],
        "suggestions": []
    }
    
    # Length check
    if len(password) < 8:
        result["is_valid"] = False
        result["issues"].append("Password must be at least 8 characters long")
    elif len(password) >= 12:
        result["score"] += 2
    else:
        result["score"] += 1
    
    # Character variety checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not has_lower:
        result["issues"].append("Password must contain at least one lowercase letter")
        result["suggestions"].append("Add lowercase letters")
    else:
        result["score"] += 1
    
    if not has_upper:
        result["issues"].append("Password must contain at least one uppercase letter")
        result["suggestions"].append("Add uppercase letters")
    else:
        result["score"] += 1
    
    if not has_digit:
        result["issues"].append("Password must contain at least one number")
        result["suggestions"].append("Add numbers")
    else:
        result["score"] += 1
    
    if not has_special:
        result["issues"].append("Password must contain at least one special character")
        result["suggestions"].append("Add special characters (!@#$%^&* etc.)")
    else:
        result["score"] += 1
    
    # Common password patterns
    common_patterns = [
        "password", "123456", "qwerty", "abc123", "password123",
        "admin", "letmein", "welcome", "monkey", "dragon"
    ]
    
    if password.lower() in common_patterns:
        result["is_valid"] = False
        result["issues"].append("Password is too common")
        result["suggestions"].append("Use a more unique password")
    
    # Sequential characters
    if any(password[i:i+3] in "abcdefghijklmnopqrstuvwxyz" or 
           password[i:i+3] in "0123456789" for i in range(len(password)-2)):
        result["score"] -= 1
        result["suggestions"].append("Avoid sequential characters")
    
    # Determine strength level
    if result["score"] >= 6:
        result["strength"] = "strong"
    elif result["score"] >= 4:
        result["strength"] = "medium"
    else:
        result["strength"] = "weak"
    
    return result
