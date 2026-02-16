from openai import OpenAI
import os
import random
from typing import List, Dict
from dotenv import load_dotenv
import time  # ← ADD THIS MISSING IMPORT

load_dotenv()

class DeepSeekFreeSummarizer:
    def __init__(self):
        """Initialize OpenRouter client with fallback free models"""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.initialized = False
        self.client = None
        self.current_model_index = 0
        
        # List of working free models (in order of preference)
        self.free_models = [
            "nex-agi/deepseek-v3.1-nex-n1:free",  # Best for summarization [citation:6]
            "qwen/qwen3-4b:free",                  # Fast and reliable
            "google/gemma-3-4b-it:free",           # Google's lightweight model
            "meta-llama/llama-3.3-70b-instruct:free",  # High quality
            "mistralai/mistral-7b-instruct:free",  # Balanced
            "microsoft/phi-3-mini-128k-instruct:free",  # Long context
        ]
        
        if not self.api_key:
            print("❌ OPENROUTER_API_KEY not found in .env file")
            print("Get your free key from: https://openrouter.ai/keys")
            return
            
        try:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "BookSum AI Summarizer",
                }
            )
            
            # Test first model
            self.model_name = self.free_models[0]
            self.initialized = True
            print(f"✅ Free AI initialized with fallback models")
            print(f"🚀 Primary model: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
    
    def _try_with_fallback(self, messages, max_retries=3):
        """Try multiple models if one fails"""
        for attempt in range(max_retries):
            # Try each model starting from current index
            for i in range(len(self.free_models)):
                model_idx = (self.current_model_index + i) % len(self.free_models)
                model = self.free_models[model_idx]
                
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1500,
                        timeout=30
                    )
                    # If successful, update current index for next time
                    self.current_model_index = model_idx
                    return response
                    
                except Exception as e:
                    print(f"⚠️ Model {model} failed: {str(e)[:50]}...")
                    continue
            
            # If all models failed, wait and retry
            if attempt < max_retries - 1:
                print(f"⏳ All models failed, retrying in 2 seconds... (attempt {attempt+2}/{max_retries})")
                time.sleep(2)
            else:
                raise Exception("All free models failed after multiple attempts")
    
    def generate_summary(self, context_chunks: List[Dict], user_prompt: str) -> str:
        """Generate summary with automatic model fallback"""
        if not self.initialized or not self.client:
            return "Error: Summarizer not initialized. Check your OpenRouter API key."
        
        try:
            # Combine relevant chunks
            context = " ".join([chunk["text"] for chunk in context_chunks[:5]])
            if len(context) > 40000:  # Stay within context limits
                context = context[:40000]
            
            # Create messages
            system_msg = "You are an expert book summarizer. Create clear, concise summaries."
            
            if "bullet" in user_prompt.lower():
                user_msg = f"Create a bullet-point summary of this text using • for each point:\n\n{context}"
            elif "chapter" in user_prompt.lower():
                user_msg = f"Summarize this text chapter by chapter:\n\n{context}"
            elif "key" in user_prompt.lower() or "main" in user_prompt.lower():
                user_msg = f"What are the key ideas and main takeaways from this text?\n\n{context}"
            else:
                user_msg = f"{user_prompt}\n\n{context}"
            
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
            
            # Try with fallback models
            response = self._try_with_fallback(messages)
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return "Error: Rate limit reached. Please wait a minute and try again."
            else:
                return f"Error: All free models are currently unavailable. Please try again later.\nDetails: {error_msg[:100]}"
    
    def test_connection(self):
        """Test connection with all fallback models"""
        try:
            test_msg = [{"role": "user", "content": "Say 'OK' if you can hear me"}]
            response = self._try_with_fallback(test_msg, max_retries=1)
            return True, f"Working model: {self.free_models[self.current_model_index]}"
        except Exception as e:
            return False, str(e)