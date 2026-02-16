import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Imports from existing logic
from src.auth.database import AuthDatabase
from src.document_processor.extractor import DocumentExtractor
from src.embeddings.vector_store_simple import VectorStore
from src.summarizer.groq_summarizer import GroqSummarizer

app = FastAPI(title="BookSum API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
db = AuthDatabase()
vector_store = VectorStore()
summarizer = GroqSummarizer()

# Pydantic Models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class GenerateRequest(BaseModel):
    prompt: str
    email: str # In a real app, extract from token
    # file_name/book_title needed to filter stats? 
    # For simplicity, we just search all chunks for the user or specific book if we tracked it.
    # The original app searched: `vector_store.search_similar_chunks(query=user_prompt, user_email=..., top_k=5)`
    # It seems to search ALL chunks for that user? 
    # Wait, `store_chunks` takes `book_title`. `search_similar_chunks` filters by `user_email`.
    # So it searches ACROSS books? 
    # Let's check `search_similar_chunks` in `VectorStore`.
    # `results = self.index.query(..., filter={"user_email": {"$eq": user_email}}, ...)`
    # Yes, it searches all user's chunks.

class SummaryResponse(BaseModel):
    summary: str
    chunks: List[dict]

# Dependencies
def get_current_user_email(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    # Expecting "Bearer <token>"
    if not authorization.startswith("Bearer "):
         raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = authorization.split(" ")[1]
    is_valid, email = db.validate_session(token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return email

# Routes

@app.get("/")
def read_root():
    return {"message": "BookSum API is running"}

@app.post("/auth/register")
def register(req: RegisterRequest):
    success, message = db.register_user(req.email, req.password, req.name)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.post("/auth/login")
def login(req: LoginRequest):
    success, result = db.login_user(req.email, req.password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    return {"token": result, "email": req.email}

@app.post("/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        db.logout_user(token)
    return {"message": "Logged out"}

@app.get("/stats")
def get_stats(email: str = Depends(get_current_user_email)):
    stats = db.get_user_stats(email)
    if not stats:
        return {"books_processed": 0, "created_at": None}
    # Convert datetime to string
    return {
        "books_processed": stats.get("books_processed", 0),
        "created_at": stats.get("created_at").isoformat() if stats.get("created_at") else None
    }

@app.get("/history")
def get_history(email: str = Depends(get_current_user_email)):
    history = db.get_user_history(email)
    # Sanitize for JSON
    for h in history:
        if "timestamp" in h and h["timestamp"]:
            h["timestamp"] = h["timestamp"].isoformat()
    return history

@app.post("/process")
async def process_book(
    file: UploadFile = File(...),
    email: str = Depends(get_current_user_email)
):
    # Save to temp file
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['pdf', 'txt']:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        extractor = DocumentExtractor()
        text = extractor.extract_text(tmp_path, file_ext)
        
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text")
        
        chunks = extractor.chunk_text(text)
        
        # Store in vector store
        success = vector_store.store_chunks(
            chunks=chunks,
            metadata={"source": "api_upload"},
            user_email=email,
            book_title=file.filename
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store chunks in vector db")
            
        # Update stats
        db.increment_books_processed(email)
        
        return {
            "message": "Book processed successfully",
            "filename": file.filename,
            "chunks_count": len(chunks),
            "text_length": len(text)
        }
        
    finally:
        os.unlink(tmp_path)

@app.post("/generate")
def generate_summary(
    req: GenerateRequest,
    email: str = Depends(get_current_user_email)
):
    # Check if summarizer is ready
    if not summarizer.initialized:
         raise HTTPException(status_code=503, detail="Summarizer service not available (Check API Key)")

    # Search relevant chunks
    results = vector_store.search_similar_chunks(
        query=req.prompt,
        user_email=email,
        top_k=5
    )
    
    if not results:
         raise HTTPException(status_code=404, detail="No relevant context found. Try processing a book first.")
         
    # Generate summary
    summary_text = summarizer.generate_summary(results, req.prompt)
    
    # Save to history
    # We need to know the book title. 
    # The search results have book_title in metadata. We can pick the most proper one or just "Mixed Sources" if multiple.
    # Logic: usually for a summary request, users might want summary of a specific book, 
    # but the current logic searches ALL user's books. 
    # The `app.py` logic was tied to the `uploaded_file` in session state for the title.
    # Implicitly, the `vector_store.search` returns chunks from potentially ANY book of the user.
    # To mimic `app.py` exactly, `app.py` only allowed generating summary IMMEDIATELY after upload, 
    # and it used `st.session_state.uploaded_file.name` as title.
    # BUT, the `search_similar_chunks` searches EVERYTHING.
    # If the user uploaded Book A, then Book B, then searches "Summary", it might get chunks from both?
    # Actually `vector_store` filter is just `user_email`. So yes.
    # However in `app.py`, `show_processing_page` is ONLY reachable after file upload.
    # So usually the user just uploaded a file.
    # But `VectorStore` persists data? `app.py` doesn't clear Pinecone on new upload.
    # So `app.py` technically searched all history. 
    # WE WILL KEEP THIS BEHAVIOR.
    
    # Derive title from most top result
    title = results[0].get('book_title', 'Unknown Title') if results else "Generated Summary"
    
    history_item = {
        "title": title,
        "date": None, # Will be set by db
        "chunks": len(results), # This isn't total chunks of book, but chunks used? 
        # app.py: "chunks": len(chunks) (Total chunks of the file just processed)
        # Wait, app.py uses `len(chunks)` from the extraction step!
        # In this stateless API, `/generate` doesn't know about the recent `/process` call details unless passed.
        # But for the history feature, keeping it simple: just store number of *used* chunks or request client to pass detail?
        # Let's just say "Relevant Chunks found: X".
        "prompt": req.prompt,
        "summary": summary_text[:200] + "...",
        "preview": summary_text[:200],
        "full_summary": summary_text # Storing full summary for potential view
    }
    
    db.save_history(email, history_item)
    
    return {
        "summary": summary_text,
        "results": results,
        "history_id": "saved"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
