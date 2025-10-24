#!/usr/bin/env python3
"""
Example usage of the User CRUD application
This script demonstrates how to use the user management system programmatically.
"""

import asyncio
import logging
from datetime import datetime

from database.connection import connect_to_mongo, close_mongo_connection
from crud.user_crud import user_crud
from models.user import UserCreate, UserUpdate
from utils.exceptions import UserCRUDException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_create_users():
    """Example: Create multiple users"""
    print("\n=== CREATING USERS ===")
    
    users_data = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "phone": "+1-555-0123",
            "address": "123 Main St, Anytown, USA",
            "is_active": True
        },
        {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "age": 25,
            "phone": "+1-555-0456",
            "address": "456 Oak Ave, Somewhere, USA",
            "is_active": True
        },
        {
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "age": 35,
            "phone": "+1-555-0789",
            "address": "789 Pine Rd, Elsewhere, USA",
            "is_active": False
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            user_create = UserCreate(**user_data)
            user = await user_crud.create_user(user_create)
            created_users.append(user)
            print(f"✅ Created user: {user.name} ({user.email})")
        except UserCRUDException as e:
            print(f"❌ Failed to create user {user_data['name']}: {e}")
    
    return created_users


async def example_get_users():
    """Example: Get and display users"""
    print("\n=== GETTING USERS ===")
    
    try:
        # Get all users
        users = await user_crud.get_users(limit=10)
        print(f"📋 Found {len(users)} users:")
        
        for user in users:
            print(f"  - {user.name} ({user.email}) - {'Active' if user.is_active else 'Inactive'}")
        
        # Get active users only
        active_users = await user_crud.get_users(is_active=True, limit=10)
        print(f"\n📋 Found {len(active_users)} active users:")
        
        for user in active_users:
            print(f"  - {user.name} ({user.email})")
            
    except UserCRUDException as e:
        print(f"❌ Error getting users: {e}")


async def example_search_users():
    """Example: Search users"""
    print("\n=== SEARCHING USERS ===")
    
    search_terms = ["John", "jane", "bob", "example.com"]
    
    for term in search_terms:
        try:
            users = await user_crud.search_users(term)
            print(f"🔍 Search for '{term}': {len(users)} results")
            
            for user in users:
                print(f"  - {user.name} ({user.email})")
                
        except UserCRUDException as e:
            print(f"❌ Error searching for '{term}': {e}")


async def example_update_user():
    """Example: Update a user"""
    print("\n=== UPDATING USER ===")
    
    try:
        # Get first user
        users = await user_crud.get_users(limit=1)
        if not users:
            print("❌ No users found to update")
            return
        
        user = users[0]
        print(f"📝 Updating user: {user.name}")
        
        # Update user data
        update_data = UserUpdate(
            name=f"{user.name} (Updated)",
            age=user.age + 1 if user.age else 30,
            address=f"{user.address} - Updated on {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        updated_user = await user_crud.update_user(user.id, update_data)
        if updated_user:
            print(f"✅ User updated successfully:")
            print(f"  - Name: {updated_user.name}")
            print(f"  - Age: {updated_user.age}")
            print(f"  - Address: {updated_user.address}")
        else:
            print("❌ Failed to update user")
            
    except UserCRUDException as e:
        print(f"❌ Error updating user: {e}")


async def example_get_user_by_email():
    """Example: Get user by email"""
    print("\n=== GETTING USER BY EMAIL ===")
    
    emails = ["john.doe@example.com", "jane.smith@example.com", "nonexistent@example.com"]
    
    for email in emails:
        try:
            user = await user_crud.get_user_by_email(email)
            if user:
                print(f"✅ Found user: {user.name} ({user.email})")
            else:
                print(f"❌ User not found: {email}")
        except UserCRUDException as e:
            print(f"❌ Error getting user by email {email}: {e}")


async def example_get_statistics():
    """Example: Get user statistics"""
    print("\n=== USER STATISTICS ===")
    
    try:
        total_users = await user_crud.get_user_count()
        active_users = await user_crud.get_user_count(is_active=True)
        inactive_users = await user_crud.get_user_count(is_active=False)
        
        print(f"📊 User Statistics:")
        print(f"  - Total Users: {total_users}")
        print(f"  - Active Users: {active_users}")
        print(f"  - Inactive Users: {inactive_users}")
        
        if total_users > 0:
            active_percentage = (active_users / total_users) * 100
            print(f"  - Active Percentage: {active_percentage:.1f}%")
        
    except UserCRUDException as e:
        print(f"❌ Error getting statistics: {e}")


async def example_delete_user():
    """Example: Delete a user"""
    print("\n=== DELETING USER ===")
    
    try:
        # Get first user
        users = await user_crud.get_users(limit=1)
        if not users:
            print("❌ No users found to delete")
            return
        
        user = users[0]
        print(f"🗑️ Deleting user: {user.name} ({user.email})")
        
        success = await user_crud.delete_user(user.id)
        if success:
            print(f"✅ User deleted successfully")
        else:
            print(f"❌ Failed to delete user")
            
    except UserCRUDException as e:
        print(f"❌ Error deleting user: {e}")


async def main():
    """Main example function"""
    print("🚀 User CRUD Example Usage")
    print("=" * 50)
    
    try:
        # Connect to database
        connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Run examples
        await example_create_users()
        await example_get_users()
        await example_search_users()
        await example_get_user_by_email()
        await example_get_statistics()
        await example_update_user()
        await example_delete_user()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"❌ Example failed: {e}")
    finally:
        close_mongo_connection()
        print("🔌 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
