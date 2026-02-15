from src.embeddings.vector_store_simple import VectorStore
from src.document_processor.extractor import DocumentExtractor
import os

def test_vector_store():
    print("Testing Vector Store...")
    
    # Initialize components
    vs = VectorStore()
    extractor = DocumentExtractor()
    
    if not vs.initialized:
        print("❌ Vector store not initialized")
        return
    
    # Test with a sample text
    sample_text = """Artificial intelligence (AI) is intelligence demonstrated by machines, 
    as opposed to natural intelligence displayed by animals including humans. 
    AI research has been defined as the field of study of intelligent agents, 
    which refers to any system that perceives its environment and takes actions 
    that maximize its chance of achieving its goals. Machine learning is a subset 
    of AI that enables systems to learn and improve from experience. Deep learning, 
    a subset of machine learning, uses neural networks with multiple layers to 
    progressively extract higher-level features from raw input."""
    
    # Split into chunks
    chunks = extractor.chunk_text(sample_text, chunk_size=100, overlap=20)
    print(f"Created {len(chunks)} test chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {chunk[:50]}...")
    
    # Store chunks in Pinecone
    success = vs.store_chunks(
        chunks=chunks,
        metadata={"test": "true", "source": "test_file"},
        user_email="test@example.com",
        book_title="AI Introduction"
    )
    
    if success:
        print("✅ Successfully stored chunks in Pinecone")
        
        # Test search
        results = vs.search_similar_chunks(
            query="What is machine learning and how does it work?",
            user_email="test@example.com",
            top_k=3
        )
        
        print("\n📊 Search Results:")
        for i, r in enumerate(results):
            print(f"\n{i+1}. Score: {r['score']:.3f}")
            print(f"   Book: {r['book_title']}")
            print(f"   Text: {r['text'][:150]}...")
    
    # Get stats
    stats = vs.get_index_stats()
    print(f"\n📈 Index stats: Total vectors: {stats.get('total_vector_count', 0)}")

if __name__ == "__main__":
    test_vector_store()