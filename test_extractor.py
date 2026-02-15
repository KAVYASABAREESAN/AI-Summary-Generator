from src.document_processor.extractor import DocumentExtractor

def test_extractor():
    extractor = DocumentExtractor()
    
    # Test if methods exist
    print("Testing DocumentExtractor methods:")
    print(f"✅ extract_text exists: {'extract_text' in dir(extractor)}")
    print(f"✅ clean_extracted_text exists: {'clean_extracted_text' in dir(extractor)}")
    print(f"✅ chunk_text exists: {'chunk_text' in dir(extractor)}")
    
    # Test cleaning
    test_text = "Page 1\nSubscribe\n\nReal content here.\n\nPage 2\nCopyright"
    cleaned = extractor.clean_extracted_text(test_text)
    print(f"\nCleaning test:\nOriginal: {test_text}\nCleaned: {cleaned}")

if __name__ == "__main__":
    test_extractor()