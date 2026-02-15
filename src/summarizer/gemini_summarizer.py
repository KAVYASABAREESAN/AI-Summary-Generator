import google.generativeai as genai
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class GeminiSummarizer:
    def __init__(self):
        """Initialize Gemini API"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.initialized = False
        
        if not self.api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            print("Get a free key from: https://aistudio.google.com/")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            # Using flash model for speed and free tier
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.initialized = True
            print("✅ Gemini summarizer initialized!")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
    
    def generate_summary(self, context_chunks: List[Dict], user_prompt: str, max_chunks: int = 3) -> str:
        """Generate summary using Gemini API"""
        if not self.initialized:
            return "Error: Gemini not initialized. Please check your API key in .env file."
        
        try:
            # Combine relevant chunks (limit to save tokens)
            context = " ".join([chunk["text"] for chunk in context_chunks[:max_chunks]])
            
            # Truncate if too long (Gemini has 1M token limit, but let's be reasonable)
            if len(context) > 50000:
                context = context[:50000] + "... [truncated]"
            
            # Create prompt based on user request
            if "bullet" in user_prompt.lower():
                prompt = f"""You are an expert book summarizer. Based on the following book excerpt, create a bullet-point summary:

EXCERPT:
{context}

INSTRUCTIONS:
- Create a bullet-point summary using • for each point
- Focus on the main ideas and key arguments
- Keep each bullet point concise but informative
- Organize related points together

BULLET POINT SUMMARY:
"""
            elif "chapter" in user_prompt.lower():
                prompt = f"""You are an expert book summarizer. Summarize this text in a chapter-by-chapter style:

EXCERPT:
{context}

CHAPTER SUMMARY:
"""
            elif "key" in user_prompt.lower() or "main" in user_prompt.lower():
                prompt = f"""You are an expert book summarizer. Extract the key ideas and main takeaways:

EXCERPT:
{context}

KEY IDEAS AND TAKEAWAYS:
"""
            else:
                prompt = f"""You are an expert book summarizer. Based on the following book excerpt, {user_prompt}

EXCERPT:
{context}

SUMMARY:
"""
            
            # Generate with Gemini
            response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def generate_quick_summary(self, context_chunks: List[Dict]) -> str:
        """Quick summary with default settings"""
        return self.generate_summary(
            context_chunks, 
            "provide a concise summary of the main ideas"
        )