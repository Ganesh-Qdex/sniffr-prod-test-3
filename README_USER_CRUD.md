# User CRUD Application with MongoDB

A comprehensive Python application for managing users with MongoDB, featuring full CRUD (Create, Read, Update, Delete) operations.

## Features

- ✅ **Create Users**: Add new users with validation
- ✅ **Read Users**: Get users by ID, email, or list all users
- ✅ **Update Users**: Modify existing user information
- ✅ **Delete Users**: Remove users from the database
- ✅ **Search Users**: Find users by name or email
- ✅ **Pagination**: Efficient handling of large datasets
- ✅ **Validation**: Comprehensive input validation
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Statistics**: User count and analytics
- ✅ **Interactive CLI**: User-friendly command-line interface

## Project Structure

```
sniffr-prod-test-3/
├── README.md
├── README_USER_CRUD.md          # This file
├── requirements.txt              # Python dependencies
├── config.py                     # Application configuration
├── main.py                       # Main application entry point
├── example_usage.py              # Example usage script
├── models/
│   └── user.py                   # User data models
├── database/
│   └── connection.py             # MongoDB connection management
├── crud/
│   └── user_crud.py              # User CRUD operations
└── utils/
    ├── validators.py             # Input validation utilities
    └── exceptions.py              # Custom exceptions
```

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd sniffr-prod-test-3
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MongoDB**:
   - **Windows**: Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - **macOS**: `brew install mongodb-community`
   - **Linux**: Follow [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/)

4. **Start MongoDB**:
   ```bash
   # Windows
   mongod
   
   # macOS/Linux
   sudo systemctl start mongod
   # or
   mongod --config /usr/local/etc/mongod.conf
   ```

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sniffr_users

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
```

## Usage

### 1. Interactive CLI Application

Run the main application for an interactive user management interface:

```bash
python main.py
```

This will start an interactive menu where you can:
- Create new users
- View user details
- Update user information
- Delete users
- Search users
- View statistics

### 2. Programmatic Usage

Use the CRUD operations in your own code:

```python
import asyncio
from database.connection import connect_to_mongo, close_mongo_connection
from crud.user_crud import user_crud
from models.user import UserCreate, UserUpdate

async def example():
    # Connect to database
    connect_to_mongo()
    
    # Create a user
    user_data = UserCreate(
        name="John Doe",
        email="john@example.com",
        age=30,
        phone="+1-555-0123",
        address="123 Main St"
    )
    user = await user_crud.create_user(user_data)
    print(f"Created user: {user.name}")
    
    # Get user by ID
    user = await user_crud.get_user_by_id(user.id)
    print(f"Found user: {user.name}")
    
    # Update user
    update_data = UserUpdate(name="John Smith", age=31)
    updated_user = await user_crud.update_user(user.id, update_data)
    print(f"Updated user: {updated_user.name}")
    
    # Close connection
    close_mongo_connection()

# Run the example
asyncio.run(example())
```

### 3. Example Usage Script

Run the provided example script to see all features in action:

```bash
python example_usage.py
```

## API Reference

### User Model

```python
class UserCreate:
    name: str                    # Required, 2-100 characters
    email: str                   # Required, valid email format
    age: Optional[int]           # Optional, 0-150
    phone: Optional[str]         # Optional, 10-15 characters
    address: Optional[str]       # Optional, max 500 characters
    is_active: bool = True       # Default: True

class UserUpdate:
    name: Optional[str]          # Optional, 2-100 characters
    email: Optional[str]         # Optional, valid email format
    age: Optional[int]           # Optional, 0-150
    phone: Optional[str]         # Optional, 10-15 characters
    address: Optional[str]       # Optional, max 500 characters
    is_active: Optional[bool]    # Optional
```

### CRUD Operations

```python
# Create a user
user = await user_crud.create_user(user_data: UserCreate) -> UserResponse

# Get user by ID
user = await user_crud.get_user_by_id(user_id: str) -> Optional[UserResponse]

# Get user by email
user = await user_crud.get_user_by_email(email: str) -> Optional[UserResponse]

# Get users with pagination
users = await user_crud.get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[UserResponse]

# Search users
users = await user_crud.search_users(
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[UserResponse]

# Update user
user = await user_crud.update_user(
    user_id: str,
    user_data: UserUpdate
) -> Optional[UserResponse]

# Delete user
success = await user_crud.delete_user(user_id: str) -> bool

# Get user count
count = await user_crud.get_user_count(is_active: Optional[bool] = None) -> int
```

## Database Schema

The application uses the following MongoDB collection structure:

```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique)",
  "age": "number (optional)",
  "phone": "string (optional)",
  "address": "string (optional)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Indexes

The following indexes are automatically created for optimal performance:

- `email` (unique)
- `name`
- `is_active`
- `(is_active, created_at)` (compound)

## Error Handling

The application includes comprehensive error handling:

- **ValidationError**: Input validation failures
- **UserNotFoundError**: User not found in database
- **UserAlreadyExistsError**: Duplicate email addresses
- **DatabaseConnectionError**: MongoDB connection issues
- **InvalidUserIDError**: Invalid ObjectId format

## Logging

The application uses Python's logging module with configurable levels:

- **INFO**: General application flow
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging information (when DEBUG=True)

## Performance Considerations

- **Pagination**: Use `skip` and `limit` parameters for large datasets
- **Indexes**: Automatic index creation for common queries
- **Connection Pooling**: Efficient MongoDB connection management
- **Async Operations**: Non-blocking database operations

## Security Features

- **Input Validation**: Comprehensive validation of all inputs
- **SQL Injection Protection**: Using parameterized queries
- **Email Validation**: RFC-compliant email validation
- **Data Sanitization**: Automatic data cleaning and formatting

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**:
   - Ensure MongoDB is running: `mongod`
   - Check connection string in `.env` file
   - Verify MongoDB is accessible on the specified port

2. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and virtual environment

3. **Validation Errors**:
   - Check input format (email, phone, etc.)
   - Ensure required fields are provided
   - Verify data types and constraints

### Debug Mode

Enable debug mode for detailed logging:

```python
# In config.py or .env file
DEBUG = True
LOG_LEVEL = DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Sniffr production testing suite.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information
4. Include system information and error messages
