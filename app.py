"""
app.py
------
Main Streamlit application — AI Notes Summarizer & Knowledge Extraction System.
Uses Groq API (completely free, no credit card needed).

Run with:
    streamlit run app.py
"""

import os
import datetime
import streamlit as st
from groq import Groq

from file_handler       import extract_text_from_file
from utils              import clean_text, count_words, estimate_read_time, extract_keywords
from summarizer         import generate_quick_summary, generate_detailed_summary, generate_key_points
from extractor          import run_full_extraction
from question_generator import generate_all_questions


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Notes Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem; font-weight: 700;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #A855F7 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.2; margin-bottom: 0.2rem;
}
.subtitle { font-size: 1rem; color: #6B7280; margin-top: 0; }
.author-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white; padding: 0.3rem 1rem; border-radius: 20px;
    font-size: 0.85rem; font-weight: 600; margin-top: 0.6rem;
}
.stat-card {
    background: #F9FAFB; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 1rem 1.2rem; text-align: center;
}
.stat-number { font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; color: #4F46E5; }
.stat-label { font-size: 0.78rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.06em; }
.section-header {
    font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 700;
    color: #1F2937; padding: 0.5rem 0; border-bottom: 3px solid #4F46E5; margin-bottom: 1rem;
}
.output-box {
    background: #FAFAFA; border: 1px solid #E5E7EB; border-left: 4px solid #4F46E5;
    border-radius: 8px; padding: 1.2rem 1.4rem; line-height: 1.75;
    font-size: 0.95rem; color: #374151; white-space: pre-wrap; word-wrap: break-word;
}
.output-box-green { border-left-color: #10B981; }
.output-box-amber { border-left-color: #F59E0B; }
.output-box-rose  { border-left-color: #F43F5E; }
.keyword-container { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
.keyword-chip {
    background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE;
    border-radius: 20px; padding: 0.25rem 0.75rem; font-size: 0.82rem; font-weight: 500;
}
.custom-divider {
    height: 1px; background: linear-gradient(90deg, #4F46E5 0%, transparent 100%);
    margin: 1.5rem 0; border: none;
}
.footer { text-align: center; color: #9CA3AF; font-size: 0.8rem; padding: 1.5rem 0 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Groq client setup ─────────────────────────────────────────────────────────
def get_groq_client(sidebar_key: str = ""):
    # 1. Streamlit secrets
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return Groq(api_key=key)
    except (KeyError, FileNotFoundError):
        pass
    # 2. Environment variable
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return Groq(api_key=key)
    # 3. Sidebar input
    if sidebar_key.strip():
        return Groq(api_key=sidebar_key.strip())
    return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.divider()
    sidebar_key = st.text_input(
        "Groq API Key (Free)",
        type="password",
        placeholder="gsk_...",
        help="Get your FREE key from console.groq.com",
    )
    st.divider()
    st.markdown("### 📂 Input Method")
    input_mode = st.radio(
        "Choose how to provide notes:",
        ["📋 Paste Text", "📁 Upload File"],
        index=0,
    )
    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown(
        "**AI Notes Summarizer** uses Llama3 (via Groq) to transform raw "
        "lecture notes into structured summaries, knowledge extractions, "
        "and study questions — completely free!"
    )
    st.markdown(
        "<div style='font-size:0.8rem;color:#9CA3AF;margin-top:1rem;'>"
        "Supports PDF · DOCX · TXT · Plain text</div>",
        unsafe_allow_html=True,
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="main-title">🧠 AI Notes Summarizer</p>'
    '<p class="main-title" style="font-size:1.5rem;">& Knowledge Extraction System</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">Transform raw lecture notes into structured summaries, '
    'key concepts & study questions — instantly.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<span class="author-badge">✨ Created by Zainab Gondal</span>',
    unsafe_allow_html=True,
)
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)


# ── Input section ─────────────────────────────────────────────────────────────
raw_text = ""

if input_mode == "📋 Paste Text":
    st.markdown("### 📝 Paste Your Lecture Notes")
    raw_text = st.text_area(
        label="",
        placeholder="Paste your lecture notes here...",
        height=300,
        label_visibility="collapsed",
    )
else:
    st.markdown("### 📁 Upload Your Notes File")
    uploaded_file = st.file_uploader(
        label="",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )
    if uploaded_file is not None:
        with st.spinner("📖 Extracting text from your file…"):
            try:
                raw_text = extract_text_from_file(uploaded_file)
                st.success(f"✅ Extracted text from **{uploaded_file.name}**")
                with st.expander("👀 Preview extracted text"):
                    st.text(raw_text[:500] + ("…" if len(raw_text) > 500 else ""))
            except Exception as e:
                st.error(f"⚠️ Could not read file: {e}")

st.markdown("")
analyse_clicked = st.button("🔍 Analyse Notes", type="primary")
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)


# ── Processing pipeline ───────────────────────────────────────────────────────
if analyse_clicked:

    if not raw_text.strip():
        st.warning("⚠️ Please paste some text or upload a file first.")
        st.stop()

    client = get_groq_client(sidebar_key)
    if client is None:
        st.error(
            "🔑 **Groq API key not found.**\n\n"
            "Get your FREE key from **console.groq.com** → API Keys → Create Key\n\n"
            "Then paste it in the sidebar."
        )
        st.stop()

    clean  = clean_text(raw_text)
    word_count = count_words(clean)
    read_time  = estimate_read_time(clean)
    char_count = len(clean)

    # Stats
    st.markdown("### 📊 Document Statistics")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-card"><div class="stat-number">{word_count:,}</div><div class="stat-label">Words</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-number">{char_count:,}</div><div class="stat-label">Characters</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-number">{read_time}</div><div class="stat-label">Est. Read Time</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Summaries
    st.markdown('<p class="section-header">📝 Summaries</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["⚡ Quick Summary", "📖 Detailed Summary", "🎯 Key Points"])

    with tab1:
        with st.spinner("Generating quick summary…"):
            quick = generate_quick_summary(client, clean)
        st.markdown(f'<div class="output-box">{quick}</div>', unsafe_allow_html=True)

    with tab2:
        with st.spinner("Generating detailed summary…"):
            detailed = generate_detailed_summary(client, clean)
        st.markdown(f'<div class="output-box output-box-green">{detailed}</div>', unsafe_allow_html=True)

    with tab3:
        with st.spinner("Extracting key points…"):
            key_points = generate_key_points(client, clean)
        st.markdown(f'<div class="output-box output-box-amber">{key_points}</div>', unsafe_allow_html=True)

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Knowledge extraction
    st.markdown('<p class="section-header">🔬 Knowledge Extraction</p>', unsafe_allow_html=True)
    with st.spinner("Extracting knowledge elements…"):
        knowledge = run_full_extraction(client, clean)

    ke1, ke2 = st.columns(2)
    with ke1:
        st.markdown("**🧩 Important Concepts**")
        st.markdown(f'<div class="output-box">{knowledge["concepts"]}</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**🏷️ Key Terms**")
        terms_html = "".join(
            f'<span class="keyword-chip">{t.strip()}</span>'
            for t in knowledge["key_terms"].split(",") if t.strip()
        )
        st.markdown(f'<div class="keyword-container">{terms_html}</div>', unsafe_allow_html=True)

    with ke2:
        st.markdown("**📖 Definitions**")
        st.markdown(f'<div class="output-box output-box-green">{knowledge["definitions"]}</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**📌 Important Facts**")
        st.markdown(f'<div class="output-box output-box-amber">{knowledge["important_facts"]}</div>', unsafe_allow_html=True)

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Study questions
    st.markdown('<p class="section-header">❓ Study Questions</p>', unsafe_allow_html=True)
    with st.spinner("Generating study questions…"):
        questions = generate_all_questions(client, clean)

    qtab1, qtab2, qtab3 = st.tabs(["💭 Conceptual (5)", "🔢 Multiple Choice (5)", "✏️ Short Answer (3)"])
    with qtab1:
        st.markdown(f'<div class="output-box">{questions["conceptual"]}</div>', unsafe_allow_html=True)
    with qtab2:
        st.markdown(f'<div class="output-box output-box-green">{questions["mcq"]}</div>', unsafe_allow_html=True)
    with qtab3:
        st.markdown(f'<div class="output-box output-box-rose">{questions["short_answer"]}</div>', unsafe_allow_html=True)

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # NLP Keywords
    st.markdown('<p class="section-header">🏷️ NLP Keyword Extraction</p>', unsafe_allow_html=True)
    st.caption("Extracted using NLTK frequency analysis")
    keywords = extract_keywords(clean, top_n=25)
    if keywords:
        chips = "".join(f'<span class="keyword-chip">{kw}</span>' for kw in keywords)
        st.markdown(f'<div class="keyword-container">{chips}</div>', unsafe_allow_html=True)

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Download
    st.markdown('<p class="section-header">⬇️ Download Summary</p>', unsafe_allow_html=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    download_content = f"""AI NOTES SUMMARIZER & KNOWLEDGE EXTRACTION SYSTEM
Created by Zainab Gondal
Generated on: {timestamp}
{'='*70}

DOCUMENT STATISTICS
  Words      : {word_count:,}
  Characters : {char_count:,}
  Read time  : {read_time}
{'='*70}

QUICK SUMMARY
{'-'*40}
{quick}

DETAILED SUMMARY
{'-'*40}
{detailed}

KEY POINTS
{'-'*40}
{key_points}

{'='*70}
KNOWLEDGE EXTRACTION
{'='*70}

IMPORTANT CONCEPTS
{'-'*40}
{knowledge['concepts']}

DEFINITIONS
{'-'*40}
{knowledge['definitions']}

KEY TERMS
{'-'*40}
{knowledge['key_terms']}

IMPORTANT FACTS
{'-'*40}
{knowledge['important_facts']}

{'='*70}
STUDY QUESTIONS
{'='*70}

CONCEPTUAL QUESTIONS
{'-'*40}
{questions['conceptual']}

MULTIPLE-CHOICE QUESTIONS
{'-'*40}
{questions['mcq']}

SHORT-ANSWER QUESTIONS
{'-'*40}
{questions['short_answer']}

{'='*70}
NLP KEYWORDS
{'-'*40}
{', '.join(keywords)}

{'='*70}
AI Notes Summarizer  |  Created by Zainab Gondal
"""
    st.download_button(
        label="⬇️ Download Full Summary (.txt)",
        data=download_content.encode("utf-8"),
        file_name=f"notes_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
    )
    st.success("✅ Analysis complete!")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">🧠 AI Notes Summarizer | Created by <strong>Zainab Gondal</strong> | Powered by Groq + Llama3 (Free)</div>',
    unsafe_allow_html=True,
)
