import requests
import os
from typing import List, Dict
from dotenv import load_dotenv
import json

load_dotenv()

class SarvamSummarizer:
    def __init__(self):
        """Initialize Sarvam AI client with correct API endpoint"""
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.initialized = False
        
        if not self.api_key:
            print("❌ SARVAM_API_KEY not found in .env file")
            print("Get your key from: https://dashboard.sarvam.ai/")
            return
        
        # Correct base URL from docs
        self.base_url = "https://api.sarvam.ai"
        self.chat_endpoint = f"{self.base_url}/chat/completions"  # Correct endpoint [citation:10]
        
        # Correct header format - using api-subscription-key [citation:2]
        self.headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Test connection
        try:
            # Simple test request to check API key
            test_payload = {
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "model": "sarvam-m"  # Correct model name from docs [citation:10]
            }
            
            response = requests.post(
                self.chat_endpoint,
                headers=self.headers,
                json=test_payload
            )
            
            if response.status_code == 200:
                self.initialized = True
                print("✅ Sarvam AI initialized successfully!")
            else:
                print(f"❌ Failed to initialize: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def generate_summary(self, context_chunks: List[Dict], user_prompt: str) -> str:
        """Generate summary using Sarvam-M API [citation:10]"""
        if not self.initialized:
            return "Error: Sarvam AI not initialized. Please check your API key."
        
        try:
            # Combine relevant chunks (limit to save tokens)
            context = " ".join([chunk["text"] for chunk in context_chunks[:5]])
            if len(context) > 30000:
                context = context[:30000]
            
            # Create system message for summarization
            system_message = "You are an expert book summarizer. Provide clear, concise summaries based on the user's request."
            
            # Create user message based on prompt type
            if "bullet" in user_prompt.lower():
                user_message = f"""Based on the following book excerpt, create a bullet-point summary:

{context}

Create a bullet-point summary using • for each point. Focus on main ideas only."""

            elif "chapter" in user_prompt.lower():
                user_message = f"""Summarize this text chapter by chapter:

{context}

Chapter summary:"""

            elif "key" in user_prompt.lower() or "main" in user_prompt.lower():
                user_message = f"""Extract the key ideas and main takeaways:

{context}

Key ideas:"""

            else:
                user_message = f"""{user_prompt}

{context}

Summary:"""
            
            # Prepare payload according to Sarvam docs [citation:10]
            payload = {
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "model": "sarvam-m",  # Model name from docs
                "temperature": 0.3,    # Lower for focused summaries
                "max_tokens": 1024,
                "top_p": 0.9
            }
            
            # Make API request
            response = requests.post(
                self.chat_endpoint,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse response according to docs format [citation:10]
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "No summary generated"
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(error_msg)
                
                if response.status_code == 403:
                    return "Error: Invalid API key. Please check your Sarvam AI API key."
                elif response.status_code == 429:
                    return "Error: Rate limit exceeded. Please try again later."
                else:
                    return f"Error: {error_msg}"
                    
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def test_connection(self):
        """Test the API connection"""
        try:
            test_payload = {
                "messages": [
                    {"role": "user", "content": "Say 'API is working' in one word"}
                ],
                "model": "sarvam-m",
                "max_tokens": 10
            }
            
            response = requests.post(
                self.chat_endpoint,
                headers=self.headers,
                json=test_payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, "Connection successful"
            else:
                return False, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)