import pymongo
from pymongo import MongoClient
import bcrypt
from datetime import datetime
import os
from config import MONGODB_URI, MONGODB_DB_NAME

# Try to import streamlit, but don't fail if it's not available
try:
    import streamlit as st
    has_streamlit = True
except ImportError:
    has_streamlit = False
    # Create a simple mock for st when not available
    class MockStreamlit:
        @staticmethod
        def error(msg):
            print(f"ERROR: {msg}")
    st = MockStreamlit()

class AuthDatabase:
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            print(f"Attempting to connect to MongoDB at {MONGODB_URI}")
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[MONGODB_DB_NAME]
            self.users_collection = self.db["users"]
            self.sessions_collection = self.db["sessions"]
            
            # Create unique index on email
            self.users_collection.create_index("email", unique=True)
            print("✅ MongoDB connected successfully!")
        except Exception as e:
            error_msg = f"Failed to connect to MongoDB: {str(e)}"
            print(f"❌ {error_msg}")
            if has_streamlit:
                st.error(error_msg)
            self.client = None
            self.db = None
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    def register_user(self, email, password, name=""):
        """Register a new user"""
        try:
            # Fix: Check if db is None instead of using truth value testing
            if self.db is None:
                return False, "Database not connected"
            
            # Check if user already exists
            if self.users_collection.find_one({"email": email}):
                return False, "Email already registered"
            
            # Hash password and create user
            hashed = self.hash_password(password)
            user = {
                "email": email,
                "password": hashed,
                "name": name,
                "created_at": datetime.now(),
                "last_login": None,
                "books_processed": 0
            }
            
            result = self.users_collection.insert_one(user)
            print(f"✅ User registered: {email}")
            return True, "Registration successful!"
            
        except Exception as e:
            error_msg = f"Registration failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def login_user(self, email, password):
        """Login user and create session"""
        try:
            # Fix: Check if db is None instead of using truth value testing
            if self.db is None:
                return False, "Database not connected"
            
            # Find user by email
            user = self.users_collection.find_one({"email": email})
            
            if not user:
                return False, "User not found"
            
            # Verify password
            if self.verify_password(password, user["password"]):
                # Update last login
                self.users_collection.update_one(
                    {"email": email},
                    {"$set": {"last_login": datetime.now()}}
                )
                
                # Create session token (simple version - in production use JWT)
                session_token = bcrypt.gensalt().hex()
                
                # Store session
                self.sessions_collection.insert_one({
                    "email": email,
                    "token": session_token,
                    "created_at": datetime.now()
                })
                
                print(f"✅ User logged in: {email}")
                return True, session_token
            else:
                return False, "Invalid password"
                
        except Exception as e:
            error_msg = f"Login failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def validate_session(self, session_token):
        """Validate if session token is valid"""
        try:
            if self.db is None:
                return False, None
            session = self.sessions_collection.find_one({"token": session_token})
            if session:
                return True, session["email"]
            return False, None
        except Exception:
            return False, None
    
    def logout_user(self, session_token):
        """Logout user by removing session"""
        try:
            if self.db is None:
                return False
            self.sessions_collection.delete_one({"token": session_token})
            return True
        except Exception:
            return False
    
    def get_user_stats(self, email):
        """Get user statistics"""
        try:
            if self.db is None:
                return None
            user = self.users_collection.find_one(
                {"email": email},
                {"password": 0}  # Exclude password
            )
            return user
        except Exception:
            return None
    
    def increment_books_processed(self, email):
        """Increment the count of books processed by user"""
        try:
            if self.db is None:
                return False
            self.users_collection.update_one(
                {"email": email},
                {"$inc": {"books_processed": 1}}
            )
            return True
        except Exception:
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔒 MongoDB connection closed")

    def save_history(self, email, history_item):
        """Save summary history to database"""
        try:
            if self.db is None:
                return False
            
            # Add timestamp if not present
            if "timestamp" not in history_item:
                history_item["timestamp"] = datetime.now()
            
            self.db["history"].insert_one({
                "email": email,
                **history_item
            })
            return True
        except Exception as e:
            print(f"❌ Failed to save history: {e}")
            return False

    def get_user_history(self, email):
        """Get user history from database"""
        try:
            if self.db is None:
                return []
            
            cursor = self.db["history"].find(
                {"email": email}
            ).sort("timestamp", -1)
            
            history = []
            for item in cursor:
                item["_id"] = str(item["_id"])  # Convert ObjectId to string
                history.append(item)
            
            return history
        except Exception as e:
            print(f"❌ Failed to get history: {e}")
            return []