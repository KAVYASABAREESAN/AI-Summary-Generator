import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

# Load environment variables
load_dotenv()

print("Testing Pinecone v8 connection...")

# Get API key
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "book-summaries")

if not api_key:
    print("❌ No PINECONE_API_KEY found in .env file")
    print("Please add your API key to .env file")
    exit(1)

print(f"API Key: {api_key[:10]}... (first 10 chars)")
print(f"Index name: {index_name}")

try:
    # Initialize Pinecone with just the API key
    pc = Pinecone(api_key=api_key)
    print("✅ Pinecone client initialized!")
    
    # List indexes
    indexes = pc.list_indexes()
    print(f"Available indexes: {[idx.name for idx in indexes]}")
    
    # Check if our index exists
    index_exists = any(idx.name == index_name for idx in indexes)
    
    if not index_exists:
        print(f"Index '{index_name}' doesn't exist. Creating it...")
        
        # Create index (serverless spec is optional)
        pc.create_index(
            name=index_name,
            dimension=384,  # for all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"✅ Index '{index_name}' creation initiated!")
        print("Waiting 10 seconds for index to initialize...")
        time.sleep(10)
    else:
        print(f"✅ Index '{index_name}' already exists")
    
    # Connect to the index
    index = pc.Index(index_name)
    print(f"✅ Connected to index '{index_name}'")
    
    # Get index stats
    stats = index.describe_index_stats()
    print(f"Index stats: {stats}")
    
    # Test with a sample embedding
    print("\nTesting with sample embedding...")
    test_vector = [0.1] * 384  # dummy vector of correct dimension
    
    # Upsert a test vector
    index.upsert(
        vectors=[
            {
                "id": "test-1",
                "values": test_vector,
                "metadata": {"text": "This is a test", "user": "test"}
            }
        ]
    )
    print("✅ Test vector upserted")
    
    # Query the test vector
    results = index.query(
        vector=test_vector,
        top_k=1,
        include_metadata=True
    )
    print(f"✅ Query results: {results}")
    
    print("\n🎉 Pinecone is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()