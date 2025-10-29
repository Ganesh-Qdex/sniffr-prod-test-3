#!/usr/bin/env python3
"""
User CRUD Application with MongoDB
A comprehensive user management system with Create, Read, Update, Delete operations.
"""

import asyncio
import sys
from typing import Optional
import logging
from datetime import datetime

from database.connection import connect_to_mongo, close_mongo_connection
from crud.user_crud import user_crud
from models.user import UserCreate, UserUpdate
from config import DEBUG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserManagementApp:
    """Main application class for user management"""
    
    def __init__(self):
        self.running = True
    
    async def start(self):
        """Start the application"""
        try:
            # Connect to MongoDB
            connect_to_mongo()
            logger.info("User Management Application Started")
            
            # Main application loop
            while self.running:
                await self.show_menu()
                choice = input("\nEnter your choice: ").strip()
                await self.handle_choice(choice)
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            close_mongo_connection()
            logger.info("Application closed")
    
    async def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("           USER MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Create User")
        print("2. Get User by ID")
        print("3. Get User by Email")
        print("4. List All Users")
        print("5. Search Users")
        print("6. Update User")
        print("7. Delete User")
        print("8. Get User Statistics")
        print("9. Exit")
        print("="*50)
    
    async def handle_choice(self, choice: str):
        """Handle user menu choice"""
        try:
            if choice == "1":
                await self.create_user()
            elif choice == "2":
                await self.get_user_by_id()
            elif choice == "3":
                await self.get_user_by_email()
            elif choice == "4":
                await self.list_users()
            elif choice == "5":
                await self.search_users()
            elif choice == "6":
                await self.update_user()
            elif choice == "7":
                await self.delete_user()
            elif choice == "8":
                await self.get_statistics()
            elif choice == "9":
                self.running = False
                print("Goodbye!")
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")
            if DEBUG:
                logger.exception("Error in handle_choice")
    
    async def create_user(self):
        """Create a new user"""
        print("\n--- CREATE NEW USER ---")
        
        try:
            name = input("Enter name: ").strip()
            if not name:
                print("Name is required!")
                return
            
            email = input("Enter email: ").strip()
            if not email:
                print("Email is required!")
                return
            
            age_input = input("Enter age (optional): ").strip()
            age = int(age_input) if age_input else None
            
            phone = input("Enter phone (optional): ").strip() or None
            address = input("Enter address (optional): ").strip() or None
            
            # Create user data
            user_data = UserCreate(
                name=name,
                email=email,
                age=age,
                phone=phone,
                address=address
            )
            
            # Create user
            user = await user_crud.create_user(user_data)
            print(f"\n✅ User created successfully!")
            self._display_user(user)
            
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error creating user: {e}")
    
    async def get_user_by_id(self):
        """Get user by ID"""
        print("\n--- GET USER BY ID ---")
        
        user_id = input("Enter user ID: ").strip()
        if not user_id:
            print("User ID is required!")
            return
        
        try:
            user = await user_crud.get_user_by_id(user_id)
            if user:
                print("\n✅ User found:")
                self._display_user(user)
            else:
                print("❌ User not found!")
        except Exception as e:
            print(f"❌ Error getting user: {e}")
    
    async def get_user_by_email(self):
        """Get user by email"""
        print("\n--- GET USER BY EMAIL ---")
        
        email = input("Enter email: ").strip()
        if not email:
            print("Email is required!")
            return
        
        try:
            user = await user_crud.get_user_by_email(email)
            if user:
                print("\n✅ User found:")
                self._display_user(user)
            else:
                print("❌ User not found!")
        except Exception as e:
            print(f"❌ Error getting user: {e}")
    
    async def list_users(self):
        """List all users with pagination"""
        print("\n--- LIST USERS ---")
        
        try:
            # Get pagination parameters
            page = int(input("Enter page number (default 1): ").strip() or "1")
            limit = int(input("Enter users per page (default 10): ").strip() or "10")
            skip = (page - 1) * limit
            
            # Get filter option
            filter_choice = input("Filter by active status? (y/n): ").strip().lower()
            is_active = None
            if filter_choice == 'y':
                active_choice = input("Show active users? (y/n): ").strip().lower()
                is_active = active_choice == 'y'
            
            # Get users
            users = await user_crud.get_users(skip=skip, limit=limit, is_active=is_active)
            
            if users:
                print(f"\n📋 Found {len(users)} users (Page {page}):")
                for i, user in enumerate(users, 1):
                    print(f"\n{i}. {user.name} ({user.email})")
                    print(f"   ID: {user.id}")
                    print(f"   Active: {'Yes' if user.is_active else 'No'}")
                    print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("❌ No users found!")
                
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error listing users: {e}")
    
    async def search_users(self):
        """Search users by name or email"""
        print("\n--- SEARCH USERS ---")
        
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("Search term is required!")
            return
        
        try:
            users = await user_crud.search_users(search_term)
            
            if users:
                print(f"\n🔍 Found {len(users)} users matching '{search_term}':")
                for i, user in enumerate(users, 1):
                    print(f"\n{i}. {user.name} ({user.email})")
                    print(f"   ID: {user.id}")
                    print(f"   Active: {'Yes' if user.is_active else 'No'}")
            else:
                print(f"❌ No users found matching '{search_term}'!")
                
        except Exception as e:
            print(f"❌ Error searching users: {e}")
    
    async def update_user(self):
        """Update user"""
        print("\n--- UPDATE USER ---")
        
        user_id = input("Enter user ID: ").strip()
        if not user_id:
            print("User ID is required!")
            return
        
        try:
            # Get current user
            current_user = await user_crud.get_user_by_id(user_id)
            if not current_user:
                print("❌ User not found!")
                return
            
            print(f"\nCurrent user: {current_user.name} ({current_user.email})")
            print("Enter new values (press Enter to keep current value):")
            
            # Get update data
            name = input(f"Name [{current_user.name}]: ").strip() or current_user.name
            email = input(f"Email [{current_user.email}]: ").strip() or current_user.email
            
            age_input = input(f"Age [{current_user.age or 'None'}]: ").strip()
            age = int(age_input) if age_input else current_user.age
            
            phone = input(f"Phone [{current_user.phone or 'None'}]: ").strip() or current_user.phone
            address = input(f"Address [{current_user.address or 'None'}]: ").strip() or current_user.address
            
            active_input = input(f"Active (y/n) [{'y' if current_user.is_active else 'n'}]: ").strip().lower()
            is_active = active_input == 'y' if active_input else current_user.is_active
            
            # Create update data
            update_data = UserUpdate(
                name=name,
                email=email,
                age=age,
                phone=phone,
                address=address,
                is_active=is_active
            )
            
            # Update user
            updated_user = await user_crud.update_user(user_id, update_data)
            if updated_user:
                print(f"\n✅ User updated successfully!")
                self._display_user(updated_user)
            else:
                print("❌ Failed to update user!")
                
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error updating user: {e}")
    
    async def delete_user(self):
        """Delete user"""
        print("\n--- DELETE USER ---")
        
        user_id = input("Enter user ID: ").strip()
        if not user_id:
            print("User ID is required!")
            return
        
        try:
            # Get user first to show confirmation
            user = await user_crud.get_user_by_id(user_id)
            if not user:
                print("❌ User not found!")
                return
            
            print(f"\nUser to delete: {user.name} ({user.email})")
            confirm = input("Are you sure you want to delete this user? (y/n): ").strip().lower()
            
            if confirm == 'y':
                success = await user_crud.delete_user(user_id)
                if success:
                    print("✅ User deleted successfully!")
                else:
                    print("❌ Failed to delete user!")
            else:
                print("❌ Deletion cancelled!")
                
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
    
    async def get_statistics(self):
        """Get user statistics"""
        print("\n--- USER STATISTICS ---")
        
        try:
            total_users = await user_crud.get_user_count()
            active_users = await user_crud.get_user_count(is_active=True)
            inactive_users = await user_crud.get_user_count(is_active=False)
            
            print(f"\n📊 User Statistics:")
            print(f"Total Users: {total_users}")
            print(f"Active Users: {active_users}")
            print(f"Inactive Users: {inactive_users}")
            print(f"Active Percentage: {(active_users/total_users*100):.1f}%" if total_users > 0 else "N/A")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    def _display_user(self, user):
        """Display user information in a formatted way"""
        print(f"\n👤 User Details:")
        print(f"   ID: {user.id}")
        print(f"   Name: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Age: {user.age or 'Not specified'}")
        print(f"   Phone: {user.phone or 'Not specified'}")
        print(f"   Address: {user.address or 'Not specified'}")
        print(f"   Active: {'Yes' if user.is_active else 'No'}")
        print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Updated: {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")


async def main():
    """Main function"""
    app = UserManagementApp()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
