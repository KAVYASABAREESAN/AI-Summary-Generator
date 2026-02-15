from src.summarizer.gemini_summarizer_v2 import GeminiSummarizer
import time

def test_summarizer():
    print("Testing Gemini 2.0 Flash...")
    
    summarizer = GeminiSummarizer()
    
    if summarizer.initialized:
        # Test chunks
        test_chunks = [{
            "text": """Artificial intelligence (AI) is transforming the world. 
            Machine learning, a subset of AI, enables computers to learn from data without explicit programming. 
            Deep learning uses neural networks with multiple layers to process information. 
            Natural language processing helps computers understand human language. 
            Computer vision allows machines to interpret images and videos.
            
            These technologies are being used in healthcare for disease diagnosis, 
            in finance for fraud detection, in transportation for self-driving cars, 
            and in entertainment for personalized recommendations.
            
            The future of AI includes advances in robotics, general intelligence, 
            and ethical considerations about privacy and job displacement.""",
            "score": 1.0,
            "book_title": "AI Basics"
        }]
        
        # Test different prompts
        prompts = [
            "Give me a bullet point summary",
            "What are the key applications?",
            "Explain the future of AI"
        ]
        
        for prompt in prompts:
            print(f"\n📝 Prompt: {prompt}")
            print("-" * 50)
            
            start = time.time()
            summary = summarizer.generate_summary(test_chunks, prompt)
            elapsed = time.time() - start
            
            print(f"⏱️ Generated in {elapsed:.1f} seconds")
            print(summary)
            print()
            
    else:
        print("❌ Summarizer not initialized")

if __name__ == "__main__":
    test_summarizer()