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
from crud.auth_crud import auth_crud
from models.user import UserCreate, UserUpdate
from models.auth import UserCreateWithAuth, LoginRequest, ChangePassword, UserRole
from auth_endpoints import auth_endpoints
from utils.password import check_password_strength
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
        self.current_user = None
        self.current_token = None
    
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
        
        if self.current_user:
            print(f"👤 Logged in as: {self.current_user.name} ({self.current_user.role.value})")
            print("="*50)
            print("AUTHENTICATION MENU:")
            print("1. Logout")
            print("2. Change Password")
            print("3. View Profile")
            print("4. Update Profile")
            print("="*50)
            print("USER MANAGEMENT MENU:")
            print("5. Create User")
            print("6. Get User by ID")
            print("7. Get User by Email")
            print("8. List All Users")
            print("9. Search Users")
            print("10. Update User")
            print("11. Delete User")
            print("12. Get User Statistics")
            if self.current_user.role in [UserRole.ADMIN, UserRole.MODERATOR]:
                print("13. Update User Role")
            print("14. Exit")
        else:
            print("AUTHENTICATION MENU:")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
        
        print("="*50)
    
    async def handle_choice(self, choice: str):
        """Handle user menu choice"""
        try:
            if self.current_user:
                # Authenticated user menu
                if choice == "1":
                    await self.logout()
                elif choice == "2":
                    await self.change_password()
                elif choice == "3":
                    await self.view_profile()
                elif choice == "4":
                    await self.update_profile()
                elif choice == "5":
                    await self.create_user()
                elif choice == "6":
                    await self.get_user_by_id()
                elif choice == "7":
                    await self.get_user_by_email()
                elif choice == "8":
                    await self.list_users()
                elif choice == "9":
                    await self.search_users()
                elif choice == "10":
                    await self.update_user()
                elif choice == "11":
                    await self.delete_user()
                elif choice == "12":
                    await self.get_statistics()
                elif choice == "13" and self.current_user.role in [UserRole.ADMIN, UserRole.MODERATOR]:
                    await self.update_user_role()
                elif choice == "14":
                    self.running = False
                    print("Goodbye!")
                else:
                    print("Invalid choice. Please try again.")
            else:
                # Unauthenticated user menu
                if choice == "1":
                    await self.register()
                elif choice == "2":
                    await self.login()
                elif choice == "3":
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
    
    async def register(self):
        """Register a new user"""
        print("\n--- USER REGISTRATION ---")
        
        try:
            name = input("Enter name: ").strip()
            if not name:
                print("Name is required!")
                return
            
            email = input("Enter email: ").strip()
            if not email:
                print("Email is required!")
                return
            
            password = input("Enter password: ").strip()
            if not password:
                print("Password is required!")
                return
            
            # Check password strength
            password_check = check_password_strength(password)
            if not password_check["is_valid"]:
                print(f"❌ Password validation failed:")
                for issue in password_check["issues"]:
                    print(f"   - {issue}")
                if password_check["suggestions"]:
                    print("Suggestions:")
                    for suggestion in password_check["suggestions"]:
                        print(f"   - {suggestion}")
                return
            
            age_input = input("Enter age (optional): ").strip()
            age = int(age_input) if age_input else None
            
            phone = input("Enter phone (optional): ").strip() or None
            address = input("Enter address (optional): ").strip() or None
            
            # Create user data
            user_data = UserCreateWithAuth(
                name=name,
                email=email,
                password=password,
                age=age,
                phone=phone,
                address=address,
                role=UserRole.USER
            )
            
            # Register user
            auth_response = await auth_endpoints.register(user_data)
            self.current_user = auth_response.user
            self.current_token = auth_response.token.access_token
            
            print(f"\n✅ Registration successful!")
            print(f"Welcome, {self.current_user.name}!")
            
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error registering user: {e}")
    
    async def login(self):
        """Login user"""
        print("\n--- USER LOGIN ---")
        
        try:
            email = input("Enter email: ").strip()
            if not email:
                print("Email is required!")
                return
            
            password = input("Enter password: ").strip()
            if not password:
                print("Password is required!")
                return
            
            # Create login data
            login_data = LoginRequest(email=email, password=password)
            
            # Login user
            auth_response = await auth_endpoints.login(login_data)
            self.current_user = auth_response.user
            self.current_token = auth_response.token.access_token
            
            print(f"\n✅ Login successful!")
            print(f"Welcome back, {self.current_user.name}!")
            
        except ValueError as e:
            print(f"❌ Login error: {e}")
        except Exception as e:
            print(f"❌ Error logging in: {e}")
    
    async def logout(self):
        """Logout current user"""
        print("\n--- LOGOUT ---")
        
        if self.current_user:
            print(f"Goodbye, {self.current_user.name}!")
            self.current_user = None
            self.current_token = None
        else:
            print("You are not logged in!")
    
    async def change_password(self):
        """Change current user password"""
        print("\n--- CHANGE PASSWORD ---")
        
        if not self.current_user:
            print("❌ You must be logged in to change password!")
            return
        
        try:
            current_password = input("Enter current password: ").strip()
            if not current_password:
                print("Current password is required!")
                return
            
            new_password = input("Enter new password: ").strip()
            if not new_password:
                print("New password is required!")
                return
            
            # Check new password strength
            password_check = check_password_strength(new_password)
            if not password_check["is_valid"]:
                print(f"❌ New password validation failed:")
                for issue in password_check["issues"]:
                    print(f"   - {issue}")
                return
            
            confirm_password = input("Confirm new password: ").strip()
            if new_password != confirm_password:
                print("❌ Passwords do not match!")
                return
            
            # Change password
            password_data = ChangePassword(
                current_password=current_password,
                new_password=new_password
            )
            
            success = await auth_endpoints.change_password(
                self.current_user.id, 
                password_data
            )
            
            if success:
                print("✅ Password changed successfully!")
            else:
                print("❌ Failed to change password!")
                
        except ValueError as e:
            print(f"❌ Password change error: {e}")
        except Exception as e:
            print(f"❌ Error changing password: {e}")
    
    async def view_profile(self):
        """View current user profile"""
        print("\n--- YOUR PROFILE ---")
        
        if not self.current_user:
            print("❌ You must be logged in to view profile!")
            return
        
        self._display_user(self.current_user)
    
    async def update_profile(self):
        """Update current user profile"""
        print("\n--- UPDATE PROFILE ---")
        
        if not self.current_user:
            print("❌ You must be logged in to update profile!")
            return
        
        try:
            print(f"Current profile: {self.current_user.name} ({self.current_user.email})")
            print("Enter new values (press Enter to keep current value):")
            
            # Get update data
            name = input(f"Name [{self.current_user.name}]: ").strip() or self.current_user.name
            email = input(f"Email [{self.current_user.email}]: ").strip() or self.current_user.email
            
            age_input = input(f"Age [{self.current_user.age or 'None'}]: ").strip()
            age = int(age_input) if age_input else self.current_user.age
            
            phone = input(f"Phone [{self.current_user.phone or 'None'}]: ").strip() or self.current_user.phone
            address = input(f"Address [{self.current_user.address or 'None'}]: ").strip() or self.current_user.address
            
            # Create update data
            update_data = UserUpdate(
                name=name,
                email=email,
                age=age,
                phone=phone,
                address=address
            )
            
            # Update user
            updated_user = await user_crud.update_user(self.current_user.id, update_data)
            if updated_user:
                self.current_user = updated_user
                print(f"\n✅ Profile updated successfully!")
                self._display_user(updated_user)
            else:
                print("❌ Failed to update profile!")
                
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error updating profile: {e}")
    
    async def update_user_role(self):
        """Update user role (admin/moderator only)"""
        print("\n--- UPDATE USER ROLE ---")
        
        if not self.current_user or self.current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
            print("❌ You don't have permission to update user roles!")
            return
        
        try:
            user_id = input("Enter user ID: ").strip()
            if not user_id:
                print("User ID is required!")
                return
            
            print("Available roles:")
            print("1. user")
            print("2. moderator")
            print("3. admin")
            
            role_choice = input("Select role (1-3): ").strip()
            role_map = {"1": "user", "2": "moderator", "3": "admin"}
            
            if role_choice not in role_map:
                print("❌ Invalid role choice!")
                return
            
            new_role = role_map[role_choice]
            
            # Update role
            success = await auth_endpoints.update_user_role(
                user_id, 
                new_role, 
                self.current_token
            )
            
            if success:
                print(f"✅ User role updated to {new_role}!")
            else:
                print("❌ Failed to update user role!")
                
        except ValueError as e:
            print(f"❌ Role update error: {e}")
        except Exception as e:
            print(f"❌ Error updating user role: {e}")
    
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
        print(f"   Role: {user.role.value}")
        print(f"   Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
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
