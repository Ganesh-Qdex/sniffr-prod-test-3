"""
Custom exceptions for the user CRUD application
"""


class UserCRUDException(Exception):
    """Base exception for user CRUD operations"""
    pass


class UserNotFoundError(UserCRUDException):
    """Raised when a user is not found"""
    pass


class UserAlreadyExistsError(UserCRUDException):
    """Raised when trying to create a user that already exists"""
    pass


class DatabaseConnectionError(UserCRUDException):
    """Raised when there's a database connection issue"""
    pass


class ValidationError(UserCRUDException):
    """Raised when input validation fails"""
    pass


class DuplicateEmailError(UserCRUDException):
    """Raised when trying to create a user with an existing email"""
    pass


class InvalidUserIDError(UserCRUDException):
    """Raised when an invalid user ID is provided"""
    pass


class DatabaseOperationError(UserCRUDException):
    """Raised when a database operation fails"""
    pass
