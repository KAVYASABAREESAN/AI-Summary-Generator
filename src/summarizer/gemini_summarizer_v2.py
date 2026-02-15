from google import genai
import os
import time
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class GeminiSummarizer:
    def __init__(self):
        """Initialize the Google Gen AI SDK with Gemini 2.0 Flash"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.initialized = False
        self.client = None
        self.model_name = "gemini-2.0-flash"  # Fast and free model
        
        if not self.api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            print("Get a free key from: https://aistudio.google.com/")
            return
            
        try:
            # Initialize the client
            self.client = genai.Client(api_key=self.api_key)
            self.initialized = True
            print(f"✅ Gemini initialized with model: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
    
    def generate_summary(self, context_chunks: List[Dict], user_prompt: str, max_chunks: int = 3, max_retries: int = 3) -> str:
        """Generate summary using Gemini API with automatic retry on quota errors"""
        if not self.initialized or not self.client:
            return "Error: Gemini not initialized. Please check your API key."
        
        for attempt in range(max_retries):
            try:
                # Combine relevant chunks (limit to save tokens)
                context = " ".join([chunk["text"] for chunk in context_chunks[:max_chunks]])
                
                # Truncate if too long (Gemini 2.0 has 1M token limit, but let's be reasonable)
                if len(context) > 50000:
                    context = context[:50000] + "... [truncated]"
                
                # Create prompt based on user request
                if "bullet" in user_prompt.lower():
                    prompt = f"""You are an expert book summarizer. Based on the following book excerpt, create a bullet-point summary.

BOOK EXCERPT:
{context}

INSTRUCTIONS:
- Create a bullet-point summary using • for each point
- Focus on the main ideas and key arguments only
- Keep each bullet point concise but informative (1-2 sentences)
- Organize related points together
- Do not include any introductory or concluding text

BULLET POINT SUMMARY:"""
                
                elif "chapter" in user_prompt.lower():
                    prompt = f"""You are an expert book summarizer. Summarize this text in a chapter-by-chapter style.

BOOK EXCERPT:
{context}

INSTRUCTIONS:
- Organize the summary by logical sections or chapters
- For each section, provide a brief overview
- Highlight the key developments and plot points
- Keep the summary coherent and easy to follow

CHAPTER SUMMARY:"""
                
                elif "key" in user_prompt.lower() or "main" in user_prompt.lower() or "idea" in user_prompt.lower():
                    prompt = f"""You are an expert book summarizer. Extract the key ideas and main takeaways from this text.

BOOK EXCERPT:
{context}

INSTRUCTIONS:
- Identify the 3-5 most important ideas or concepts
- Explain each key idea clearly and concisely
- Show how these ideas connect to each other
- Focus on the core message or thesis

KEY IDEAS AND TAKEAWAYS:"""
                
                elif "short" in user_prompt.lower() or "brief" in user_prompt.lower():
                    prompt = f"""You are an expert book summarizer. Provide a very brief, concise summary of this text.

BOOK EXCERPT:
{context}

INSTRUCTIONS:
- Keep it to 2-3 sentences maximum
- Capture only the absolute main point
- Be extremely concise

BRIEF SUMMARY:"""
                
                else:
                    prompt = f"""You are an expert book summarizer. Based on the following book excerpt, provide a comprehensive summary.

BOOK EXCERPT:
{context}

USER REQUEST: {user_prompt}

INSTRUCTIONS:
- Address the user's specific request
- Provide a well-structured summary
- Include the most important information
- Be clear and easy to understand

SUMMARY:"""
                
                # Generate content using Gemini
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                return response.text
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error (429)
                if "429" in error_str and "RESOURCE_EXHAUSTED" in error_str:
                    # Try to extract wait time from error message
                    wait_time = 60  # default wait time
                    match = re.search(r'retry in (\d+\.?\d*)s', error_str)
                    if match:
                        wait_time = float(match.group(1)) + 1  # Add 1 second buffer
                    
                    if attempt < max_retries - 1:
                        print(f"⏳ Rate limit hit. Waiting {wait_time:.0f} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"Error: Still hitting rate limits after {max_retries} retries. Please try again in a few minutes.\n\nDetails: The Gemini API free tier has limits. Wait about 60 seconds and try again."
                
                # Other errors
                elif "404" in error_str and "not found" in error_str.lower():
                    return f"Error: Model '{self.model_name}' not found. Please check available models in your account."
                
                elif "403" in error_str:
                    return f"Error: Authentication failed. Please check your API key."
                
                else:
                    return f"Error generating summary: {error_str}"
        
        return "Error: Maximum retries exceeded. Please try again later."
    
    def generate_quick_summary(self, context_chunks: List[Dict]) -> str:
        """Quick summary with default settings"""
        return self.generate_summary(
            context_chunks, 
            "provide a concise summary of the main ideas"
        )
    
    def generate_bullet_points(self, context_chunks: List[Dict]) -> str:
        """Generate bullet point summary"""
        return self.generate_summary(
            context_chunks,
            "give me a bullet point summary"
        )
    
    def check_quota_status(self) -> dict:
        """Check current quota status (simplified - just tests connection)"""
        try:
            # Make a minimal test request
            test_prompt = "Hello"
            self.client.models.generate_content(
                model=self.model_name,
                contents=test_prompt
            )
            return {"status": "ok", "message": "API is working normally"}
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                return {"status": "rate_limited", "message": "Rate limit hit. Please wait a minute."}
            else:
                return {"status": "error", "message": str(e)}