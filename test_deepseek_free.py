from src.summarizer.deepseek_free_summarizer import DeepSeekFreeSummarizer
from dotenv import load_dotenv
import os

load_dotenv()

print("Testing FREE DeepSeek via OpenRouter...")
print(f"API Key exists: {'Yes' if os.getenv('OPENROUTER_API_KEY') else 'No'}")

summarizer = DeepSeekFreeSummarizer()

if summarizer.initialized:
    # Test connection
    success, message = summarizer.test_connection()
    print(f"Connection test: {message}")
    
    # Test with sample text
    test_chunks = [{
        "text": "Artificial intelligence is transforming the world. Machine learning enables computers to learn from data. Deep learning uses neural networks with multiple layers. These technologies are being used in healthcare, finance, and transportation.",
        "score": 1.0,
        "book_title": "AI Basics"
    }]
    
    print("\n⏳ Generating test summary...")
    summary = summarizer.generate_summary(test_chunks, "Give me a bullet point summary")
    
    print("\n" + "="*60)
    print(summary)
    print("="*60)
else:
    print("❌ Check your API key")