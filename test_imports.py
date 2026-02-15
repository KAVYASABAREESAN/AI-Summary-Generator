import sys
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

try:
    import streamlit
    print(f"✅ Streamlit found at: {streamlit.__file__}")
except ImportError as e:
    print(f"❌ Streamlit import failed: {e}")

try:
    import pymongo
    print(f"✅ PyMongo found at: {pymongo.__file__}")
except ImportError as e:
    print(f"❌ PyMongo import failed: {e}")