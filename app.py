import streamlit as st
from src.auth.database import AuthDatabase
from config import MONGODB_URI, MONGODB_DB_NAME
import time
import tempfile
import os
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="BookSum - AI Book Summarizer",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Lucide icon utility
def lucide_icon(name, size=20, color="currentColor"):
    """Return HTML for Lucide icon"""
    icons = {
        "home": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
        "book": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/></svg>',
        "history": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        "user": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        "upload": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
        "settings": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H5.78a1.65 1.65 0 0 0-1.51 1 1.65 1.65 0 0 0 .33 1.82l.02.02A10 10 0 0 0 12 17.66a10 10 0 0 0 6.36-2.64z"/></svg>',
        "logout": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" x2="9"/></svg>',
        "login": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" x2="3"/></svg>',
        "mail": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/></svg>',
        "lock": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        "check": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
        "x": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
        "search": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        "filter": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 13 10 21 14 18 14 13 22 3"/></svg>',
        "calendar": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "trending": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
        "file": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>',
        "download": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
        "chevron-right": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
        "sparkles": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A6.002 6.002 0 0 0 15 9.5"/><path d="M8 4v3"/><path d="M12 4v3"/><path d="M12 16v3"/><path d="M4 12h3"/><path d="M16 12h3"/><path d="M9.937 9.5A6.002 6.002 0 0 0 15 15.5"/></svg>',
    }
    return icons.get(name, f'<span>🔹</span>')

# Custom CSS for aesthetic UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #fafafa;
    }
    
    /* Modern container */
    .modern-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Header */
    .modern-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #eaeaea;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1a1a1a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-links {
        display: flex;
        gap: 0.5rem;
    }
    
    .nav-item {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #666;
        transition: all 0.2s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: transparent;
        border: none;
    }
    
    .nav-item:hover {
        background: #f0f0f0;
        color: #1a1a1a;
    }
    
    .nav-item.active {
        background: #1a1a1a;
        color: white;
    }
    
    /* Auth card */
    .auth-card {
        max-width: 400px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
        border: 1px solid #eaeaea;
    }
    
    .auth-title {
        font-size: 2rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .auth-subtitle {
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    
    /* Form elements */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        color: #1a1a1a;
    }
    
    .form-input {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 1px solid #eaeaea;
        border-radius: 12px;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        background: white;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #1a1a1a;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
    }
    
    /* Button */
    .modern-button {
        width: 100%;
        padding: 0.875rem;
        background: #1a1a1a;
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .modern-button:hover {
        background: #333;
        transform: translateY(-1px);
    }
    
    .modern-button.secondary {
        background: white;
        color: #1a1a1a;
        border: 1px solid #eaeaea;
    }
    
    .modern-button.secondary:hover {
        background: #fafafa;
    }
    
    /* Upload area */
    .upload-area {
        background: white;
        border: 2px dashed #eaeaea;
        border-radius: 24px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        border-color: #1a1a1a;
        background: #fafafa;
    }
    
    .upload-icon {
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    .upload-title {
        font-size: 1.25rem;
        font-weight: 500;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        color: #666;
        font-size: 0.95rem;
    }
    
    /* Card */
    .modern-card {
        background: white;
        border: 1px solid #eaeaea;
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .modern-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-item {
        background: white;
        border: 1px solid #eaeaea;
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid #eaeaea;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #666;
    }
    
    .stTabs [aria-selected="true"] {
        background: #f0f0f0 !important;
        color: #1a1a1a !important;
    }
    
    /* File info */
    .file-info {
        background: #f5f5f5;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'session_token' not in st.session_state:
    st.session_state.session_token = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'user_history' not in st.session_state:
    st.session_state.user_history = []

# Initialize database connection
@st.cache_resource
def init_database():
    return AuthDatabase()

db = init_database()

# Render header
def render_header():
    cols = st.columns([1, 2, 1])
    
    with cols[0]:
        st.markdown(f'<div class="logo">{lucide_icon("book", 24)} BookSum</div>', unsafe_allow_html=True)
    
    with cols[1]:
        if st.session_state.logged_in:
            nav_cols = st.columns(4)
            pages = [
                ("home", "Home", "home"),
                ("history", "History", "history"),
                ("stats", "Stats", "trending"),
                ("settings", "Settings", "settings"),
            ]
            for i, (page, label, icon) in enumerate(pages):
                with nav_cols[i]:
                    if st.button(
                        f"{label}",
                        key=f"nav_{page}",
                        use_container_width=True
                    ):
                        st.session_state.current_page = page
                        st.rerun()
    
    with cols[2]:
        if st.session_state.logged_in:
            user_display = st.session_state.user_email.split('@')[0] if st.session_state.user_email else "User"
            st.markdown(f'<div style="display: flex; align-items: center; gap: 0.5rem; justify-content: flex-end;">👤 {user_display}</div>', unsafe_allow_html=True)

# Auth page
def show_auth_page():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-title">Welcome back</h1>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">Sign in to continue to BookSum</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Sign In", "Create account"])
    
    with tab1:
        with st.form("login_form"):
            login_email = st.text_input("Email", placeholder="hello@example.com")
            login_password = st.text_input("Password", type="password", placeholder="••••••••")
            
            if st.form_submit_button("Sign in", use_container_width=True):
                if login_email and login_password:
                    success, result = db.login_user(login_email, login_password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_email = login_email
                        st.session_state.session_token = result
                        st.session_state.current_page = "home"
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.warning("Please fill in all fields")
    
    with tab2:
        with st.form("register_form"):
            reg_name = st.text_input("Full name", placeholder="John Doe")
            reg_email = st.text_input("Email", placeholder="hello@example.com")
            reg_password = st.text_input("Password", type="password", placeholder="Create a password")
            reg_confirm = st.text_input("Confirm password", type="password", placeholder="Confirm your password")
            
            if st.form_submit_button("Create account", use_container_width=True):
                if reg_email and reg_password and reg_confirm:
                    if reg_password != reg_confirm:
                        st.error("Passwords do not match")
                    else:
                        success, message = db.register_user(reg_email, reg_password, reg_name)
                        if success:
                            st.success("Account created! Please sign in.")
                        else:
                            st.error(message)
                else:
                    st.warning("Please fill in all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Home page
def show_home_page():
    st.markdown('<div class="modern-container">', unsafe_allow_html=True)
    
    st.markdown("## Upload your book")
    st.markdown("Upload a PDF or TXT file and get an AI-generated summary in seconds.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        file_size = uploaded_file.size / (1024 * 1024)
        st.markdown(f"""
        <div class="file-info">
            <span style="display: flex; align-items: center; gap: 0.5rem;">
                📄 {uploaded_file.name}
            </span>
            <span>{file_size:.2f} MB</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Process book", use_container_width=True):
                st.session_state.uploaded_file = uploaded_file
                st.session_state.current_page = "processing"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Processing page with SARVAM AI SUMMARIZATION
def show_processing_page():
    st.markdown('<div class="modern-container">', unsafe_allow_html=True)
    
    st.markdown("## Generate summary")
    
    if 'uploaded_file' in st.session_state:
        from src.document_processor.extractor import DocumentExtractor
        from src.embeddings.vector_store_simple import VectorStore
        from src.summarizer.groq_summarizer import GroqSummarizer
        
        # User prompt
        st.markdown("### What kind of summary would you like?")
        user_prompt = st.text_area(
            "Summary prompt",
            value="Provide a comprehensive summary covering the main ideas, key arguments, and important conclusions.",
            height=100,
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate summary", use_container_width=True):
                st.session_state.generate_summary = True
        
        with col2:
            if st.button("Back", use_container_width=True):
                del st.session_state.uploaded_file
                st.session_state.current_page = "home"
                st.rerun()
        
        if st.session_state.get('generate_summary', False):
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{st.session_state.uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(st.session_state.uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                with st.spinner("Processing your book..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Initialize components
                    extractor = DocumentExtractor()
                    vector_store = VectorStore()
                    summarizer = GroqSummarizer()

                    if not summarizer.initialized:
                        st.error("❌ Failed to initialize Sarvam AI summarizer. Check your API key.")
                        st.stop()
                    
                    # Step 1: Extract text
                    status_text.text("📄 Extracting text from file...")
                    progress_bar.progress(10)
                    
                    file_type = st.session_state.uploaded_file.name.split('.')[-1].lower()
                    text = extractor.extract_text(tmp_path, file_type)
                    
                    if text:
                        st.info(f"📊 Extracted {len(text)} characters")
                        
                        # Step 2: Split into chunks
                        status_text.text("✂️ Creating chunks...")
                        progress_bar.progress(30)
                        
                        chunks = extractor.chunk_text(text)
                        st.info(f"📑 Created {len(chunks)} chunks")
                        
                        # Step 3: Store in vector database
                        status_text.text("📦 Storing in vector database...")
                        progress_bar.progress(50)
                        
                        store_success = vector_store.store_chunks(
                            chunks=chunks,
                            metadata={"source": "upload"},
                            user_email=st.session_state.user_email,
                            book_title=st.session_state.uploaded_file.name
                        )
                        
                        if store_success:
                            st.success("✅ Text stored in vector database")
                            
                            # Step 4: Search for relevant chunks
                            status_text.text("🔍 Finding relevant sections...")
                            progress_bar.progress(70)
                            
                            results = vector_store.search_similar_chunks(
                                query=user_prompt,
                                user_email=st.session_state.user_email,
                                top_k=5
                            )
                            
                            if results:
                                st.info(f"🔍 Found {len(results)} relevant sections")
                                
                                # Step 5: Generate summary with Sarvam AI
                                status_text.text("🤖 Generating summary with Sarvam AI...")
                                progress_bar.progress(90)
                                
                                summary = summarizer.generate_summary(results, user_prompt)
                                
                                # Step 6: Display result
                                progress_bar.progress(100)
                                status_text.text("✅ Done!")
                                
                                st.success("✅ Summary generated successfully!")
                                
                                # Display the summary
                                st.markdown("### 📋 Your Summary")
                                st.markdown(summary)
                                
                                # Show source chunks in expander
                                with st.expander("View source chunks"):
                                    for i, r in enumerate(results):
                                        st.markdown(f"**Chunk {i+1}** (Score: {r['score']:.3f})")
                                        st.markdown(f">{r['text'][:300]}...")
                                        st.markdown("---")
                                
                                # Save to history
                                history_item = {
                                    "title": st.session_state.uploaded_file.name,
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "chunks": len(chunks),
                                    "prompt": user_prompt,
                                    "summary": summary[:200] + "...",
                                    "preview": summary[:200]
                                }
                                
                                if 'user_history' not in st.session_state:
                                    st.session_state.user_history = []
                                st.session_state.user_history.insert(0, history_item)
                                
                                # Update user stats
                                db.increment_books_processed(st.session_state.user_email)
                            else:
                                st.warning("No relevant sections found. Try a different prompt.")
                        else:
                            st.error("❌ Failed to store chunks in vector database")
                    else:
                        st.error("❌ Failed to extract text from file")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
            
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
                st.session_state.generate_summary = False
    
    st.markdown('</div>', unsafe_allow_html=True)

# History page
def show_history_page():
    st.markdown('<div class="modern-container">', unsafe_allow_html=True)
    
    st.markdown("## Your history")
    
    # Get user history
    history = st.session_state.get('user_history', [])
    
    if not history:
        st.info("No summaries yet. Upload a book to get started!")
        if st.button("Upload your first book", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    else:
        # Search
        search = st.text_input("Search summaries", placeholder="Search by title or content...")
        
        # Display history
        for item in history:
            st.markdown(f"""
            <div class="modern-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; font-weight: 600;">{item['title']}</h3>
                        <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">
                            {item['date']} · {item['chunks']} chunks
                        </p>
                        <p style="color: #888; font-size: 0.95rem; margin-top: 1rem;">
                            {item['preview']}
                        </p>
                        <p style="color: #999; font-size: 0.9rem; margin-top: 1rem;">
                            Prompt: {item['prompt']}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Stats page
def show_stats_page():
    st.markdown('<div class="modern-container">', unsafe_allow_html=True)
    
    st.markdown("## Statistics")
    
    # Get user stats
    user_stats = db.get_user_stats(st.session_state.user_email)
    history = st.session_state.get('user_history', [])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Books processed", user_stats.get('books_processed', 0) if user_stats else 0)
    
    with col2:
        total_chunks = sum(item.get('chunks', 0) for item in history)
        st.metric("Total chunks", total_chunks)
    
    with col3:
        st.metric("Member since", user_stats.get('created_at', datetime.now()).strftime('%b %Y') if user_stats else 'N/A')
    
    with col4:
        last_7_days = len([item for item in history if (datetime.now() - datetime.strptime(item['date'].split()[0], '%Y-%m-%d')).days <= 7]) if history else 0
        st.metric("Last 7 days", last_7_days)
    
    # Activity chart
    st.markdown("### Activity")
    chart_data = [1, 3, 2, 4, 3, 5, 4]
    st.line_chart(chart_data)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Settings page
def show_settings_page():
    st.markdown('<div class="modern-container">', unsafe_allow_html=True)
    
    st.markdown("## Settings")
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Preferences", "Account"])
    
    with tab1:
        st.markdown("### Profile information")
        st.text_input("Display name", value=st.session_state.user_email.split('@')[0] if st.session_state.user_email else "")
        st.text_input("Email", value=st.session_state.user_email if st.session_state.user_email else "", disabled=True)
        if st.button("Update profile", use_container_width=True):
            st.success("Profile updated!")
    
    with tab2:
        st.markdown("### Summary preferences")
        st.selectbox("Default summary type", ["Detailed", "Bullet points", "Chapter-wise", "Key takeaways"])
        st.slider("Summary length", min_value=100, max_value=2000, value=500, step=100)
        st.checkbox("Include page numbers", value=True)
        st.checkbox("Auto-save summaries", value=True)
    
    with tab3:
        st.markdown("### Account management")
        if st.button("Change password", use_container_width=True):
            st.info("Password change coming soon!")
        if st.button("Export data", use_container_width=True):
            st.info("Export functionality coming soon!")
        if st.button("Delete account", use_container_width=True):
            st.warning("This action cannot be undone.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main app logic
render_header()

if not st.session_state.logged_in:
    show_auth_page()
else:
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "processing":
        show_processing_page()
    elif st.session_state.current_page == "history":
        show_history_page()
    elif st.session_state.current_page == "stats":
        show_stats_page()
    elif st.session_state.current_page == "settings":
        show_settings_page()

# Logout in sidebar
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown("---")
        if st.button("Sign out", use_container_width=True):
            if st.session_state.session_token:
                db.logout_user(st.session_state.session_token)
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.session_token = None
            st.session_state.current_page = "home"
            st.rerun()       
