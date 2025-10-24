"""
Validation utilities for user data
"""

import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_name(name: str) -> str:
    """Validate user name"""
    if not name or not name.strip():
        raise ValidationError("Name is required")
    
    name = name.strip()
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters long")
    
    if len(name) > 100:
        raise ValidationError("Name must be less than 100 characters")
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes")
    
    return name


def validate_email_address(email: str) -> str:
    """Validate email address"""
    if not email or not email.strip():
        raise ValidationError("Email is required")
    
    email = email.strip().lower()
    
    try:
        # Use email-validator library for comprehensive validation
        validated_email = validate_email(email)
        return validated_email.email
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email address: {str(e)}")


def validate_age(age: Optional[int]) -> Optional[int]:
    """Validate age"""
    if age is None:
        return None
    
    if not isinstance(age, int):
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValidationError("Age must be a number")
    
    if age < 0:
        raise ValidationError("Age cannot be negative")
    
    if age > 150:
        raise ValidationError("Age cannot be greater than 150")
    
    return age


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate phone number"""
    if not phone:
        return None
    
    phone = phone.strip()
    
    # Remove common phone number formatting
    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits
    if not phone_clean.isdigit():
        raise ValidationError("Phone number can only contain digits, spaces, hyphens, parentheses, and plus signs")
    
    # Check length (assuming US format, but flexible)
    if len(phone_clean) < 10:
        raise ValidationError("Phone number must be at least 10 digits")
    
    if len(phone_clean) > 15:
        raise ValidationError("Phone number must be less than 15 digits")
    
    return phone


def validate_address(address: Optional[str]) -> Optional[str]:
    """Validate address"""
    if not address:
        return None
    
    address = address.strip()
    
    if len(address) > 500:
        raise ValidationError("Address must be less than 500 characters")
    
    return address


def validate_user_id(user_id: str) -> str:
    """Validate MongoDB ObjectId format"""
    if not user_id or not user_id.strip():
        raise ValidationError("User ID is required")
    
    user_id = user_id.strip()
    
    # Check if it's a valid ObjectId format (24 hex characters)
    if not re.match(r'^[0-9a-fA-F]{24}$', user_id):
        raise ValidationError("Invalid user ID format")
    
    return user_id


def validate_pagination_params(skip: int, limit: int) -> tuple:
    """Validate pagination parameters"""
    if not isinstance(skip, int) or skip < 0:
        raise ValidationError("Skip must be a non-negative integer")
    
    if not isinstance(limit, int) or limit < 1:
        raise ValidationError("Limit must be a positive integer")
    
    if limit > 1000:
        raise ValidationError("Limit cannot exceed 1000")
    
    return skip, limit


def validate_search_term(search_term: str) -> str:
    """Validate search term"""
    if not search_term or not search_term.strip():
        raise ValidationError("Search term is required")
    
    search_term = search_term.strip()
    
    if len(search_term) < 2:
        raise ValidationError("Search term must be at least 2 characters")
    
    if len(search_term) > 100:
        raise ValidationError("Search term must be less than 100 characters")
    
    return search_term
