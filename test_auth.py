#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import asyncio
import sys
from datetime import datetime

from database.connection import connect_to_mongo, close_mongo_connection
from models.auth import UserCreateWithAuth, LoginRequest, UserRole
from auth_endpoints import auth_endpoints
from utils.password import check_password_strength, hash_password, verify_password
from utils.jwt import create_token_pair, verify_token


async def test_password_utilities():
    """Test password hashing and verification"""
    print("🔐 Testing Password Utilities...")
    
    password = "TestPassword123!"
    print(f"Original password: {password}")
    
    # Test password strength
    strength = check_password_strength(password)
    print(f"Password strength: {strength['strength']} (score: {strength['score']})")
    print(f"Valid: {strength['is_valid']}")
    
    # Test password hashing
    hashed = hash_password(password)
    print(f"Password hashed: {hashed[:50]}...")
    
    # Test password verification
    is_valid = verify_password(password, hashed)
    print(f"Password verification: {is_valid}")
    
    # Test wrong password
    wrong_password = "WrongPassword123!"
    is_wrong = verify_password(wrong_password, hashed)
    print(f"Wrong password verification: {is_wrong}")
    
    print("✅ Password utilities test completed\n")


async def test_jwt_utilities():
    """Test JWT token creation and verification"""
    print("🎫 Testing JWT Utilities...")
    
    # Test token creation
    user_data = {
        "user_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "role": "user"
    }
    
    access_token = create_token_pair(**user_data)
    print(f"Access token created: {access_token['access_token'][:50]}...")
    print(f"Token type: {access_token['token_type']}")
    print(f"Expires in: {access_token['expires_in']} seconds")
    
    # Test token verification
    token_payload = verify_token(access_token['access_token'], "access")
    if token_payload:
        print(f"Token verified - User ID: {token_payload.get('user_id')}")
        print(f"Token verified - Email: {token_payload.get('email')}")
        print(f"Token verified - Role: {token_payload.get('role')}")
    else:
        print("❌ Token verification failed")
    
    print("✅ JWT utilities test completed\n")


async def test_authentication_flow():
    """Test complete authentication flow"""
    print("🔑 Testing Authentication Flow...")
    
    try:
        # Test user registration
        print("1. Testing user registration...")
        user_data = UserCreateWithAuth(
            name="Test User",
            email="test@example.com",
            password="TestPassword123!",
            age=25,
            phone="+1234567890",
            address="123 Test St, Test City",
            role=UserRole.USER
        )
        
        auth_response = await auth_endpoints.register(user_data)
        print(f"✅ User registered: {auth_response.user.name}")
        print(f"   User ID: {auth_response.user.id}")
        print(f"   User Role: {auth_response.user.role.value}")
        print(f"   Access Token: {auth_response.token.access_token[:50]}...")
        
        # Test user login
        print("\n2. Testing user login...")
        login_data = LoginRequest(
            email="test@example.com",
            password="TestPassword123!"
        )
        
        login_response = await auth_endpoints.login(login_data)
        print(f"✅ User logged in: {login_response.user.name}")
        print(f"   Last login: {login_response.user.last_login}")
        
        # Test token verification
        print("\n3. Testing token verification...")
        current_user = await auth_endpoints.get_current_user(login_response.token.access_token)
        print(f"✅ Current user verified: {current_user.name}")
        print(f"   User role: {current_user.role.value}")
        
        print("\n✅ Authentication flow test completed")
        
    except Exception as e:
        print(f"❌ Authentication flow test failed: {e}")


async def test_password_validation():
    """Test password validation with various passwords"""
    print("🔍 Testing Password Validation...")
    
    test_passwords = [
        "weak",           # Too short
        "password",       # Too common
        "12345678",       # No letters
        "Password",       # No numbers
        "Password123",    # No special chars
        "Password123!",   # Good password
        "MyStr0ng!Pass",  # Another good password
    ]
    
    for password in test_passwords:
        strength = check_password_strength(password)
        status = "✅" if strength['is_valid'] else "❌"
        print(f"{status} '{password}': {strength['strength']} - {', '.join(strength['issues']) if strength['issues'] else 'Valid'}")


async def main():
    """Main test function"""
    print("🚀 Starting Authentication System Tests...\n")
    
    try:
        # Connect to MongoDB
        connect_to_mongo()
        print("✅ Connected to MongoDB\n")
        
        # Run tests
        await test_password_utilities()
        await test_jwt_utilities()
        await test_password_validation()
        await test_authentication_flow()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_mongo_connection()
        print("✅ MongoDB connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
