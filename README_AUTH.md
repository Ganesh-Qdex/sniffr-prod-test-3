# Authentication System

This document describes the authentication system added to the Sniffr User Management application.

## Features

### 🔐 Authentication Features
- **User Registration**: Create new user accounts with password validation
- **User Login**: Secure login with email and password
- **Password Management**: Change passwords with strength validation
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access Control**: User, Moderator, and Admin roles
- **Session Management**: Track user sessions and last login

### 🛡️ Security Features
- **Password Hashing**: Bcrypt password hashing
- **Password Strength Validation**: Comprehensive password requirements
- **JWT Token Security**: Secure token generation and validation
- **Role-Based Permissions**: Different access levels for different roles
- **Token Expiration**: Automatic token expiration for security

## User Roles

### 👤 User (Default)
- View and update own profile
- Change own password
- Basic user management operations

### 🔧 Moderator
- All User permissions
- Update user roles
- Advanced user management

### 👑 Admin
- All Moderator permissions
- Full system access
- User role management

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one lowercase letter
- At least one uppercase letter
- At least one number
- At least one special character (!@#$%^&* etc.)
- Not a common password

## JWT Token Configuration

The system uses JWT tokens with the following configuration:
- **Access Token**: 30 minutes (configurable)
- **Refresh Token**: 7 days (configurable)
- **Algorithm**: HS256
- **Secret Key**: Configurable via environment variable

## Environment Variables

Create a `.env` file with the following variables:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sniffr_users

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Usage

### 1. Start the Application
```bash
python main.py
```

### 2. Register a New User
- Select option 1 (Register)
- Enter your details
- Choose a strong password
- You'll be automatically logged in

### 3. Login
- Select option 2 (Login)
- Enter your email and password
- Access the full user management system

### 4. User Management
Once logged in, you can:
- View and update your profile
- Change your password
- Manage other users (if you have permissions)
- Update user roles (if you're a moderator or admin)

## API Endpoints

The authentication system provides the following endpoints:

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `POST /auth/refresh` - Refresh access token

### User Management
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update current user
- `POST /auth/change-password` - Change password
- `PUT /auth/users/{user_id}/role` - Update user role (admin only)

## Security Best Practices

1. **Change Default Secret Key**: Always change the JWT secret key in production
2. **Use HTTPS**: Always use HTTPS in production
3. **Regular Token Rotation**: Implement token rotation for enhanced security
4. **Monitor Login Attempts**: Log and monitor failed login attempts
5. **Password Policies**: Enforce strong password policies
6. **Role-Based Access**: Implement proper role-based access control

## Database Schema

The user collection now includes additional fields:

```javascript
{
  "_id": ObjectId,
  "name": String,
  "email": String,
  "password_hash": String,  // Hashed password
  "age": Number,
  "phone": String,
  "address": String,
  "is_active": Boolean,
  "role": String,           // "user", "moderator", "admin"
  "last_login": Date,
  "created_at": Date,
  "updated_at": Date
}
```

## Error Handling

The system includes comprehensive error handling:
- **Validation Errors**: Input validation with detailed error messages
- **Authentication Errors**: Clear authentication failure messages
- **Authorization Errors**: Permission-based error handling
- **Database Errors**: Database operation error handling

## Logging

The system includes detailed logging for:
- Authentication attempts
- Password changes
- Role updates
- Security events
- Error tracking

## Dependencies

The authentication system requires the following additional packages:
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT token handling
- `python-multipart` - Form data handling
- `email-validator` - Email validation

Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection**: Ensure MongoDB is running and accessible
2. **JWT Secret Key**: Make sure to set a secure JWT secret key
3. **Password Validation**: Check password meets all requirements
4. **Role Permissions**: Verify user has required permissions for operations

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your environment variables for detailed error messages and logging.

## Security Considerations

1. **Token Storage**: Store tokens securely (not in localStorage for web apps)
2. **Token Expiration**: Use short-lived access tokens
3. **Password Hashing**: Never store plain text passwords
4. **Input Validation**: Always validate and sanitize user input
5. **Rate Limiting**: Implement rate limiting for authentication endpoints
6. **Audit Logging**: Log all authentication and authorization events

## Future Enhancements

Potential future enhancements:
- Two-factor authentication (2FA)
- OAuth integration
- Password reset via email
- Account lockout after failed attempts
- Session management
- API rate limiting
- Audit logging
