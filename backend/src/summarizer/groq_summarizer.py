from groq import Groq
import os
import time
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class GroqSummarizer:
    def __init__(self):
        """Initialize Groq client with free models"""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.initialized = False
        self.client = None
        
        if not self.api_key:
            print("❌ GROQ_API_KEY not found in .env file")
            print("Get your free key from: https://console.groq.com")
            return
            
        try:
            self.client = Groq(api_key=self.api_key)
            self.model_name = "llama-3.1-8b-instant"
            self.initialized = True
            print(f"✅ Groq initialized with model: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Groq: {e}")
    
    def analyze_prompt_intent(self, prompt: str) -> dict:
        """Analyze the user's prompt to understand what kind of summary they want"""
        prompt_lower = prompt.lower()
        
        # Define intent patterns
        intents = {
            "format": {
                "bullet": ["bullet", "points", "list", "•", "-", "point-wise"],
                "paragraph": ["paragraph", "detailed", "comprehensive", "full"],
                "chapter": ["chapter", "chapters", "section", "parts"],
                "short": ["short", "brief", "quick", "concise", "tl;dr", "summary"],
            },
            "focus": {
                "characters": ["character", "person", "protagonist", "antagonist", "cast"],
                "themes": ["theme", "message", "moral", "lesson", "meaning"],
                "plot": ["plot", "story", "narrative", "events", "happens"],
                "analysis": ["analyze", "analysis", "critical", "review", "critique"],
                "key_points": ["key", "main", "important", "essential", "core"],
            }
        }
        
        # Detect format
        format_type = "comprehensive"  # default
        for fmt, keywords in intents["format"].items():
            if any(keyword in prompt_lower for keyword in keywords):
                format_type = fmt
                break
        
        # Detect focus
        focus_type = "general"  # default
        for focus, keywords in intents["focus"].items():
            if any(keyword in prompt_lower for keyword in keywords):
                focus_type = focus
                break
        
        return {
            "format": format_type,
            "focus": focus_type,
            "original": prompt
        }
    
    def build_system_prompt(self, intent: dict) -> str:
        """Build a system prompt based on the detected intent"""
        base_prompt = "You are an expert literary analyst and book summarizer. "
        
        # Add focus-specific instructions
        focus_instructions = {
            "characters": "Focus on character development, motivations, relationships, and arcs.",
            "themes": "Identify and analyze the main themes, symbols, and underlying messages.",
            "plot": "Trace the narrative structure, key events, and plot developments.",
            "analysis": "Provide critical analysis, evaluate the writing style, and discuss significance.",
            "key_points": "Extract and highlight the most important ideas and takeaways.",
            "general": "Provide a balanced, comprehensive overview."
        }
        
        base_prompt += focus_instructions.get(intent["focus"], focus_instructions["general"])
        
        # Add format-specific instructions
        format_instructions = {
            "bullet": "\n\nFormat your response as clear bullet points using •. Be concise but informative.",
            "paragraph": "\n\nWrite in well-structured paragraphs with clear transitions between ideas.",
            "chapter": "\n\nOrganize your summary by chapters or major sections. For each chapter, provide a brief overview.",
            "short": "\n\nKeep your response extremely concise - no more than 3-4 sentences.",
            "comprehensive": "\n\nProvide a detailed, well-structured summary covering all major aspects."
        }
        
        base_prompt += format_instructions.get(intent["format"], format_instructions["comprehensive"])
        
        return base_prompt
    
    def generate_summary(self, context_chunks: List[Dict], user_prompt: str, max_retries: int = 3) -> str:
        """Generate summary based on user's specific prompt"""
        if not self.initialized or not self.client:
            return "Error: Groq not initialized. Please check your API key."
        
        for attempt in range(max_retries):
            try:
                # Combine relevant chunks (up to 15 for better context)
                context_parts = []
                for i, chunk in enumerate(context_chunks[:15]):
                    context_parts.append(chunk["text"])
                
                context = " ".join(context_parts)
                
                # Truncate if too long
                if len(context) > 50000:
                    context = context[:50000] + "..."
                
                # Analyze the user's prompt to understand intent
                intent = self.analyze_prompt_intent(user_prompt)
                
                # Build appropriate system prompt
                system_prompt = self.build_system_prompt(intent)
                
                # Create user message that incorporates their exact prompt
                user_message = f"""Based on the following book excerpt, please respond to this specific request:

USER REQUEST: {user_prompt}

BOOK EXCERPT:
{context}

Your response should directly address the user's request above."""

                # Call Groq API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=2048,
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e)
                
                if "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"⏳ Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "Error: Rate limit exceeded. Please wait a minute and try again."
                else:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Error: {error_str[:100]}. Retrying...")
                        time.sleep(2)
                        continue
                    else:
                        return f"Error generating summary: {error_str}"
        
        return "Error: Maximum retries exceeded. Please try again later."
    
    def test_connection(self):
        """Quick test to verify API is working"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Say 'OK' if you can hear me"}],
                max_tokens=10
            )
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)