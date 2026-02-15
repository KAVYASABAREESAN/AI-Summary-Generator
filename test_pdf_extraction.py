from src.document_processor.extractor import DocumentExtractor
import os

def test_pdf_extraction():
    extractor = DocumentExtractor()
    
    # Ask for PDF path
    pdf_path = input("Enter path to a PDF book: ").strip()
    
    if not os.path.exists(pdf_path):
        print("❌ File not found!")
        return
    
    print(f"\n📄 Processing: {pdf_path}")
    
    # Extract text
    text = extractor.extract_text_from_pdf(pdf_path)
    
    if text:
        print(f"\n✅ Extracted {len(text)} characters")
        print("\n📝 First 500 characters:")
        print("-" * 40)
        print(text[:500])
        print("-" * 40)
        
        # Test chunking with smaller chunks (500 chars)
        chunks = extractor.chunk_text(text, chunk_size=500, overlap=50)
        print(f"\n✅ Created {len(chunks)} chunks (500 chars each)")
        
        if chunks:
            print("\n📚 First 3 chunks preview:")
            print("-" * 40)
            for i, chunk in enumerate(chunks[:3]):
                print(f"\nChunk {i+1}:")
                print(chunk[:200] + "...")
            print("-" * 40)
            
        # Also test with larger chunks for comparison
        chunks_large = extractor.chunk_text(text, chunk_size=1000, overlap=100)
        print(f"\n✅ Created {len(chunks_large)} chunks (1000 chars each)")
    else:
        print("❌ Failed to extract text")

if __name__ == "__main__":
    test_pdf_extraction()