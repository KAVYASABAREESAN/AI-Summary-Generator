from src.summarizer.generator import SummaryGenerator

def test_summarizer():
    print("Testing summarizer...")
    
    # Initialize summarizer
    summarizer = SummaryGenerator()
    
    if summarizer.initialized:
        # Test with sample chunks
        test_chunks = [
            {
                "text": "Machine learning is a subset of artificial intelligence that enables systems to automatically learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
                "score": 0.95,
                "book_title": "AI Book"
            },
            {
                "text": "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These neural networks attempt to simulate the behavior of the human brain, allowing it to learn from large amounts of data.",
                "score": 0.92,
                "book_title": "AI Book"
            },
            {
                "text": "Natural Language Processing (NLP) is a field of AI that gives machines the ability to read, understand and derive meaning from human languages. It combines computational linguistics with statistical and machine learning models.",
                "score": 0.88,
                "book_title": "AI Book"
            }
        ]
        
        # Test different prompts
        prompts = [
            "Give me a bullet point summary",
            "Explain the key concepts",
            "What are the main ideas?"
        ]
        
        for prompt in prompts:
            print(f"\n📝 Prompt: {prompt}")
            print("-" * 50)
            summary = summarizer.generate_summary(test_chunks, prompt)
            print(summary)
            print()
    else:
        print("❌ Summarizer not initialized")

if __name__ == "__main__":
    test_summarizer()