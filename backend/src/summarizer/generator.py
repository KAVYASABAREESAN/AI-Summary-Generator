from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import List, Dict
import time

class SummaryGenerator:
    def __init__(self):
        """Initialize the summarization model"""
        self.tokenizer = None
        self.model = None
        self.initialized = False
        
        try:
            print("Loading FLAN-T5 model (this may take a minute on first run)...")
            model_name = "google/flan-t5-base"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            self.initialized = True
            print("✅ Summary generator initialized!")
        except Exception as e:
            print(f"❌ Failed to load summarization model: {e}")
    
    def generate_summary(self, context_chunks: List[Dict], user_prompt: str, max_length: int = 300) -> str:
        """Generate a summary based on context chunks and user prompt"""
        if not self.initialized:
            return "Error: Summarization model not initialized. Please check the logs."
        
        try:
            # Combine the most relevant chunks (top 3 by score)
            context = " ".join([chunk["text"] for chunk in context_chunks[:3]])
            
            # Truncate if too long (FLAN-T5 has limit of 512 tokens)
            if len(context) > 2000:
                context = context[:2000]
            
            # Create prompt based on user request
            if "bullet" in user_prompt.lower():
                prompt = f"""Extract the main points from the following text and format them as bullet points:

Text: {context}

Bullet point summary:"""
            elif "chapter" in user_prompt.lower():
                prompt = f"""Summarize the following text chapter by chapter:

Text: {context}

Chapter summary:"""
            elif "key" in user_prompt.lower() or "main" in user_prompt.lower():
                prompt = f"""Identify and explain the key ideas from the following text:

Text: {context}

Key ideas:"""
            else:
                prompt = f"""Provide a concise summary of the following text:

Text: {context}

Summary:"""
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    min_length=50,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    temperature=0.7
                )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Format bullet points if requested
            if "bullet" in user_prompt.lower() and not summary.startswith("•"):
                points = summary.split(". ")
                formatted = "\n".join([f"• {point.strip()}" for point in points if point.strip()])
                return formatted
            
            return summary
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"