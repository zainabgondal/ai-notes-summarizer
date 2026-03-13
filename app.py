import os
import time
import datetime
import streamlit as st
from groq import Groq

# Ensure these helper files exist in your directory
from file_handler       import extract_text_from_file
from utils              import clean_text, count_words, estimate_read_time, extract_keywords
from summarizer         import generate_quick_summary, generate_detailed_summary, generate_key_points
from extractor          import run_full_extraction
from question_generator import generate_all_questions

st.set_page_config(
    page_title="AI Notes Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Cosmic UI CSS (Fixed & Responsive) ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* Base Theme */
html, body, .stApp {
    background: #02030d !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #e2e8f0 !important;
}

/* Cosmic Background */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: -1;
    background: radial-gradient(circle at 50% 50%, rgba(88,28,220,0.15), #02030d);
    background-attachment: fixed;
}

/* Container Tuning */
.block-container { 
    padding-top: 2rem !important; 
    max-width: 1100px !important; 
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, rgba(10,6,30,0.9) 0%, rgba(18,10,48,0.9) 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 24px; padding: 3rem;
    margin-bottom: 2rem; text-align: center;
}

.hero-title {
    font-size: 3.5rem; font-weight: 800;
    background: linear-gradient(120deg, #ffffff, #c4b5fd);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* ════════════════════════════════════════════
   MOBILE ADAPTATION (The "100%" Fix)
════════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .hero {
        padding: 2rem 1rem !important;
    }
    .hero-title {
        font-size: 2rem !important;
    }
    /* Force all columns to be full width on mobile */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    /* Make buttons easy to tap */
    .stButton>button {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_value=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">AI Notes Summarizer</div>
    <p style="color: #b8c8dc;">Created by Zainab Gondal</p>
</div>
""", unsafe_allow_value=True)

# ── Main Logic ───────────────────────────────────────────────────────────────
# Note: Ensure your Groq API Key is set in your environment variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "your_key_here"))

uploaded_file = st.file_uploader("Upload your notes (PDF, TXT, DOCX)", type=['pdf', 'txt', 'docx'])

if uploaded_file:
    with st.spinner("Processing document..."):
        raw_text = extract_text_from_file(uploaded_file)
        text = clean_text(raw_text)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", count_words(text))
        with col2:
            st.metric("Read Time", estimate_read_time(text))
        with col3:
            st.metric("Keywords", len(extract_keywords(text)))

        if st.button("🚀 Generate AI Insights"):
            # Summarization calls
            quick = generate_quick_summary(client, text)
            
            st.markdown("### ✨ Quick Summary")
            st.info(quick)
            
            # Additional features can be added here
else:
    st.info("Please upload a file to begin.")
