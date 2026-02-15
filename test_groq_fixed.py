from src.summarizer.groq_summarizer import GroqSummarizer
from src.document_processor.extractor import DocumentExtractor
from dotenv import load_dotenv
import time

load_dotenv()

def quick_test():
    print("="*60)
    print("QUICK TEST - Groq Summarizer")
    print("="*60)
    
    # Test 1: Initialize Groq
    print("\n📡 Initializing Groq...")
    start = time.time()
    summarizer = GroqSummarizer()
    
    if not summarizer.initialized:
        print("❌ Failed to initialize Groq")
        return
    
    print(f"✅ Initialized in {time.time()-start:.1f} seconds")
    print(f"✅ Using model: {summarizer.model_name}")
    
    # Test 2: Simple summarization with small text
    print("\n📝 Testing summarization...")
    
    # Very small test text
    test_text = """
    Artificial intelligence (AI) is transforming healthcare. 
    Machine learning helps doctors diagnose diseases from medical images. 
    Deep learning, a type of ML, uses neural networks for complex pattern recognition. 
    AI can analyze X-rays, MRIs, and CT scans faster than humans. 
    It also helps in drug discovery by predicting molecular interactions. 
    Natural language processing reads medical records to extract insights. 
    These technologies are saving lives and reducing costs.
    """
    
    test_chunks = [{
        "text": test_text,
        "score": 0.9,
        "book_title": "AI in Healthcare"
    }]
    
    print("⏳ Generating bullet point summary...")
    start = time.time()
    summary = summarizer.generate_summary(test_chunks, "Give me a bullet point summary")
    elapsed = time.time() - start
    
    print(f"✅ Generated in {elapsed:.1f} seconds")
    print("\n" + "-"*40)
    print(summary)
    print("-"*40)
    
    # Test 3: Test text cleaning quickly
    print("\n🧹 Testing text cleaning...")
    extractor = DocumentExtractor()
    
    noisy = "Page 1\nSubscribe\n\nReal content here.\n\nPage 2\nCopyright"
    cleaned = extractor.clean_extracted_text(noisy)
    print(f"Original: {noisy}")
    print(f"Cleaned: {cleaned}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    quick_test()