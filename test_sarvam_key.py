from src.summarizer.sarvam_summarizer import SarvamSummarizer
from dotenv import load_dotenv
import os

load_dotenv()

print("Testing Sarvam AI with corrected implementation...")
print(f"API Key exists: {'Yes' if os.getenv('SARVAM_API_KEY') else 'No'}")

# Initialize summarizer
summarizer = SarvamSummarizer()

if summarizer.initialized:
    print("\n✅ Summarizer initialized!")
    
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
    print("\n❌ Summarizer not initialized")
    print("\nTroubleshooting steps:")
    print("1. Go to https://dashboard.sarvam.ai/ and check your API key")
    print("2. Verify you have credits available")
    print("3. Make sure your account is activated")