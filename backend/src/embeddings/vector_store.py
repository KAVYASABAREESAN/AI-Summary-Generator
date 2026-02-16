import time
import hashlib
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL

class VectorStore:
    def __init__(self):
        """Initialize Pinecone connection and embedding model"""
        self.embedding_model = None
        self.index = None
        self.initialized = False
        self.pc = None
        
        try:
            # Initialize embedding model
            print(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            
            # Initialize Pinecone with just the API key
            print(f"Connecting to Pinecone...")
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            
            # List existing indexes
            indexes = self.pc.list_indexes()
            existing_indexes = [idx.name for idx in indexes]
            
            # Check if index exists, create if not
            if PINECONE_INDEX_NAME not in existing_indexes:
                print(f"Creating index: {PINECONE_INDEX_NAME}")
                
                # Create index
                self.pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                
                # Wait for index to be ready
                print("Waiting for index to initialize...")
                time.sleep(10)
            
            # Connect to the index
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
            self.initialized = True
            print("✅ Vector store initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize vector store: {e}")
            self.initialized = False
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.embedding_model:
            raise Exception("Embedding model not initialized")
        
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def store_chunks(self, chunks: List[str], metadata: Dict[str, Any], user_email: str, book_title: str) -> bool:
        """Store text chunks with embeddings in Pinecone"""
        if not self.initialized:
            print("Vector store not initialized")
            return False
        
        try:
            # Generate embeddings for all chunks
            print(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = self.generate_embeddings(chunks)
            
            # Prepare vectors for upsert
            vectors = []
            book_id = hashlib.md5(f"{user_email}_{book_title}_{time.time()}".encode()).hexdigest()
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{book_id}_chunk_{i}"
                
                # Create metadata
                chunk_metadata = {
                    "user_email": user_email,
                    "book_title": book_title[:100],
                    "book_id": book_id,
                    "chunk_index": i,
                    "text": chunk[:1000],
                    "timestamp": time.time(),
                    **metadata
                }
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": chunk_metadata
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
            
            print(f"✅ Stored {len(chunks)} chunks for book: {book_title}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store chunks: {e}")
            return False
    
    def search_similar_chunks(self, query: str, user_email: str, top_k: int = 5) -> List[Dict]:
        """Search for chunks similar to the query"""
        if not self.initialized:
            print("Vector store not initialized")
            return []
        
        try:
            # Generate embedding for query
            print(f"Searching for: {query[:50]}...")
            query_embedding = self.generate_embeddings([query])[0]
            
            # Search in Pinecone with metadata filter
            results = self.index.query(
                vector=query_embedding,
                filter={"user_email": {"$eq": user_email}},
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            chunks = []
            for match in results.matches:
                chunks.append({
                    "text": match.metadata.get("text", ""),
                    "book_title": match.metadata.get("book_title", "Unknown"),
                    "chunk_index": match.metadata.get("chunk_index", 0),
                    "score": match.score
                })
            
            print(f"✅ Found {len(chunks)} relevant chunks")
            return chunks
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def delete_book_chunks(self, book_id: str, user_email: str) -> bool:
        """Delete all chunks for a specific book"""
        try:
            self.index.delete(
                filter={
                    "book_id": {"$eq": book_id},
                    "user_email": {"$eq": user_email}
                }
            )
            print(f"✅ Deleted chunks for book: {book_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete chunks: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the index"""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"❌ Failed to get stats: {e}")
            return {}