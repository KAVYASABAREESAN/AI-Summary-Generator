import PyPDF2
import pdfplumber
import os
import re
from typing import List, Optional, Generator

class DocumentExtractor:
    def __init__(self):
        self.supported_formats = ['pdf', 'txt']
        self.chunk_size = 500
        self.overlap = 50
    
    def clean_extracted_text(self, text: str) -> str:
        """Remove repetitive headers, footers, and noise from extracted text"""
        if not text:
            return text
        
        # Split into lines
        lines = text.split('\n')
        cleaned_lines = []
        
        # Common noise patterns to filter out
        noise_patterns = [
            r'^page\s+\d+$', r'^\d+$',           # Page numbers
            r'copyright\s+©', r'all rights reserved',  # Copyright
            r'www\.', r'http', r'@',              # URLs and emails
            r'newsletter', r'subscribe',          # Newsletter signups
            r'terms of service', r'privacy policy',
            r'ebook', r'kindle', r'epub',         # Ebook metadata
            r'chapter\s+\d+',                     # Chapter headers (keep if you want)
            r'prologue', r'epilogue', r'appendix',
            r'illustration', r'figure', r'table',
            r'[•\-*]\s*',                          # Bullet points (keep content)
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip very short lines (likely noise)
            if len(line) < 20:
                continue
            
            # Check if line matches any noise pattern
            is_noise = False
            for pattern in noise_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # But keep if it has substantial content
                    if len(line) > 50:
                        continue
                    is_noise = True
                    break
            
            # Skip lines with too many special characters
            special_chars = sum(not c.isalnum() and not c.isspace() for c in line)
            if special_chars > len(line) * 0.3:
                continue
            
            # Skip lines that are mostly uppercase (often headers)
            words = line.split()
            if words:
                uppercase_words = sum(1 for w in words if w.isupper() and len(w) > 2)
                if uppercase_words > len(words) * 0.7:
                    continue
            
            if not is_noise:
                cleaned_lines.append(line)
        
        # If we removed too much, be less aggressive
        if len(cleaned_lines) < 20:
            return text
        
        return '\n'.join(cleaned_lines)
    
    def extract_text_from_pdf_pypdf2(self, file_path: str) -> Optional[str]:
        """Extract text using PyPDF2 (fast but basic)"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    if page_num % 10 == 0:
                        import gc
                        gc.collect()
            
            return text
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
            return None
    
    def extract_text_from_pdf_plumber(self, file_path: str) -> Optional[str]:
        """Extract text using pdfplumber (better formatting)"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"pdfplumber extraction error: {e}")
            return None
    
    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """Extract text using multiple methods and take the best result"""
        
        # Try pdfplumber first (better formatting)
        text = self.extract_text_from_pdf_plumber(file_path)
        
        # If pdfplumber fails or returns little text, try PyPDF2
        if not text or len(text) < 100:
            print("pdfplumber extracted little text, trying PyPDF2...")
            text = self.extract_text_from_pdf_pypdf2(file_path)
        
        # If both fail, return None
        if not text:
            return None
        
        # Clean the extracted text
        cleaned_text = self.clean_extracted_text(text)
        
        print(f"✅ Extracted {len(cleaned_text)} characters after cleaning")
        return cleaned_text
    
    def extract_text_from_txt(self, file_path: str) -> Optional[str]:
        """Extract text from TXT file"""
        try:
            text = ""
            with open(file_path, 'r', encoding='utf-8') as file:
                while True:
                    chunk = file.read(1024 * 1024)
                    if not chunk:
                        break
                    text += chunk
            
            cleaned_text = self.clean_extracted_text(text)
            return cleaned_text
            
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                cleaned_text = self.clean_extracted_text(text)
                return cleaned_text
            except Exception as e:
                print(f"Error extracting TXT text: {e}")
                return None
        except Exception as e:
            print(f"Error extracting TXT text: {e}")
            return None
    
    def extract_text(self, file_path: str, file_type: str) -> Optional[str]:
        """Extract text based on file type"""
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type == 'txt':
            return self.extract_text_from_txt(file_path)
        else:
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks intelligently"""
        if not text:
            return []
        
        chunks = []
        
        # First split by paragraphs
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size, save current chunk and start new
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap from end of previous chunk
                words = current_chunk.split()
                overlap_text = ' '.join(words[-int(len(words) * overlap/100):]) if words else ""
                current_chunk = overlap_text + " " + para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        file_name = os.path.basename(file_path)
        file_ext = file_name.split('.')[-1].lower()
        
        return {
            'name': file_name,
            'size_mb': round(file_size, 2),
            'type': file_ext,
            'path': file_path
        }