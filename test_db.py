from src.auth.database import AuthDatabase
from config import MONGODB_URI

def test_connection():
    # Initialize database
    db = AuthDatabase()
    
    if db.client and db.db is not None:
        print("✅ MongoDB connection successful!")
        
        # Test registration
        success, message = db.register_user("test@example.com", "password123", "Test User")
        print(f"Registration: {message}")
        
        if success:
            # Test login
            success, result = db.login_user("test@example.com", "password123")
            if success:
                print(f"✅ Login successful! Session token: {result[:20]}...")
            else:
                print(f"❌ Login failed: {result}")
        else:
            # If registration failed because user exists, try login
            print("User might already exist, trying login...")
            success, result = db.login_user("test@example.com", "password123")
            if success:
                print(f"✅ Login successful! Session token: {result[:20]}...")
            else:
                print(f"❌ Login failed: {result}")
        
        # Close connection
        db.close_connection()
    else:
        print("❌ MongoDB connection failed!")

if __name__ == "__main__":
    test_connection()