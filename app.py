"""
app.py
------
AI Notes Summarizer & Knowledge Extraction System
Dark & Modern UI — glowing cards, purple gradients, smooth animations.
Powered by Groq API (100% free).
"""

import os
import time
import datetime
import streamlit as st
from groq import Groq

from file_handler       import extract_text_from_file
from utils              import clean_text, count_words, estimate_read_time, extract_keywords
from summarizer         import generate_quick_summary, generate_detailed_summary, generate_key_points
from extractor          import run_full_extraction
from question_generator import generate_all_questions


st.set_page_config(
    page_title="AI Notes Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Ultra Modern CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #e2e8f0 !important;
}
.main {
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(120,40,200,0.22) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 10%, rgba(56,189,248,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 50% 100%, rgba(236,72,153,0.12) 0%, transparent 60%),
        linear-gradient(160deg, #04050f 0%, #07091a 40%, #090714 100%) !important;
    background-attachment: fixed !important;
}
.block-container { padding-top: 1.8rem !important; padding-bottom: 4rem !important; max-width: 1100px !important; }
#MainMenu, footer, header { visibility: hidden; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes floatUp {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 30px rgba(139,92,246,0.25), 0 0 60px rgba(139,92,246,0.08); }
    50% { box-shadow: 0 0 50px rgba(139,92,246,0.45), 0 0 90px rgba(139,92,246,0.15); }
}
@keyframes bounceIn {
    0% { transform: scale(0.82); opacity: 0; }
    65% { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
}
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* HERO */
.hero {
    background: linear-gradient(135deg, rgba(15,10,40,0.97) 0%, rgba(20,12,50,0.97) 50%, rgba(12,8,35,0.97) 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 28px; padding: 3.2rem 3rem 2.8rem; margin-bottom: 2.2rem;
    position: relative; overflow: hidden;
    animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) both;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset, 0 30px 80px rgba(0,0,0,0.6), 0 0 100px rgba(99,102,241,0.1);
}
.hero::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 0%, #6366f1 20%, #a855f7 40%, #ec4899 60%, #38bdf8 80%, transparent 100%);
    background-size: 300% 100%;
    animation: gradientMove 4s ease infinite;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 60% 70% at 5% 50%, rgba(99,102,241,0.16) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 95% 50%, rgba(168,85,247,0.12) 0%, transparent 60%);
    pointer-events: none;
}
.hero-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(139,92,246,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(139,92,246,0.035) 1px, transparent 1px);
    background-size: 44px 44px; pointer-events: none;
}
.hero-corner-dots { position: absolute; top: 22px; right: 26px; display: flex; gap: 8px; align-items: center; }
.hero-corner-dot { width: 12px; height: 12px; border-radius: 50%; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(168,85,247,0.12));
    border: 1px solid rgba(139,92,246,0.45); color: #c4b5fd;
    padding: 0.32rem 1.1rem; border-radius: 100px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 1.3rem; animation: fadeIn 0.9s ease 0.15s both;
}
.hero-title {
    font-size: 3.4rem; font-weight: 900; line-height: 1.04;
    background: linear-gradient(125deg, #ffffff 0%, #e0d7ff 25%, #a78bfa 55%, #f0abfc 80%, #67e8f9 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: fadeInUp 0.7s ease 0.08s both, gradientMove 6s ease infinite;
    margin-bottom: 0.7rem; letter-spacing: -0.02em;
}
.hero-sub {
    font-size: 1.05rem; color: #7c8fa8; font-weight: 400; margin-bottom: 2rem;
    animation: fadeInUp 0.7s ease 0.22s both; line-height: 1.7; max-width: 580px;
}
.hero-author {
    display: inline-flex; align-items: center; gap: 10px;
    background: linear-gradient(135deg, #4338ca, #7c3aed, #a855f7, #ec4899);
    background-size: 300% 300%;
    animation: fadeInUp 0.7s ease 0.35s both, gradientMove 5s ease infinite;
    color: white; padding: 0.55rem 1.6rem; border-radius: 100px;
    font-size: 0.88rem; font-weight: 700;
    box-shadow: 0 6px 30px rgba(139,92,246,0.55), 0 2px 8px rgba(0,0,0,0.3);
}

/* SECTION HEADERS */
.sec-head {
    display: flex; align-items: center; gap: 14px; margin: 2.4rem 0 1.3rem;
    animation: fadeInUp 0.5s ease both;
}
.sec-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #4338ca, #7c3aed, #a855f7);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 18px; box-shadow: 0 6px 20px rgba(99,102,241,0.45); flex-shrink: 0;
    animation: floatUp 4s ease-in-out infinite;
}
.sec-title { font-size: 1.18rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.01em; }
.sec-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(139,92,246,0.45), rgba(236,72,153,0.2), transparent);
    margin-left: 6px;
}

/* STAT CARDS */
.stat-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.stat-card {
    background: linear-gradient(145deg, rgba(15,12,40,0.9), rgba(20,14,50,0.9));
    border: 1px solid rgba(139,92,246,0.22); border-radius: 20px;
    padding: 1.7rem 1.2rem; text-align: center;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1);
    animation: fadeInUp 0.6s ease both; position: relative; overflow: hidden;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.03) inset;
}
.stat-card::after {
    content: ''; position: absolute; bottom: 0; left: 12%; right: 12%; height: 2px;
    background: linear-gradient(90deg, transparent, #7c3aed, #ec4899, transparent); border-radius: 2px;
}
.stat-card:hover {
    transform: translateY(-7px) scale(1.02); border-color: rgba(139,92,246,0.55);
    box-shadow: 0 20px 50px rgba(99,102,241,0.2), 0 0 0 1px rgba(139,92,246,0.15) inset;
}
.stat-num {
    font-size: 2.3rem; font-weight: 900;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1; margin-bottom: 0.4rem; letter-spacing: -0.02em;
}
.stat-lbl { font-size: 0.68rem; font-weight: 700; color: #4e5d73; text-transform: uppercase; letter-spacing: 0.14em; }

/* OUTPUT CARDS */
.out-card {
    background: linear-gradient(160deg, rgba(13,11,34,0.95), rgba(16,12,40,0.95));
    border: 1px solid rgba(139,92,246,0.2); border-radius: 20px; padding: 1.8rem 2rem;
    line-height: 1.9; font-size: 0.92rem; color: #c8d4e3;
    white-space: pre-wrap; word-wrap: break-word;
    animation: fadeInUp 0.55s ease both;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1);
    position: relative; overflow: hidden; backdrop-filter: blur(10px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.025) inset;
}
.out-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; border-radius: 4px 0 0 4px;
}
.out-card.purple::before { background: linear-gradient(180deg, #4338ca, #7c3aed, #a855f7, #c084fc); }
.out-card.green::before  { background: linear-gradient(180deg, #059669, #10b981, #34d399); }
.out-card.amber::before  { background: linear-gradient(180deg, #d97706, #f59e0b, #fbbf24); }
.out-card.rose::before   { background: linear-gradient(180deg, #e11d48, #f43f5e, #fb7185); }
.out-card.blue::before   { background: linear-gradient(180deg, #2563eb, #3b82f6, #60a5fa); }
.out-card:hover {
    border-color: rgba(139,92,246,0.42);
    box-shadow: 0 16px 50px rgba(99,102,241,0.16), 0 0 0 1px rgba(139,92,246,0.1) inset;
    transform: translateY(-3px);
}

/* PROGRESS */
.prog-box {
    background: linear-gradient(145deg, rgba(13,11,34,0.95), rgba(16,12,40,0.95));
    border: 1px solid rgba(139,92,246,0.28); border-radius: 20px; padding: 1.8rem 2.2rem;
    animation: fadeInUp 0.45s ease; backdrop-filter: blur(12px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 60px rgba(99,102,241,0.06);
}
.prog-label {
    font-size: 0.7rem; font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 1.1rem;
}
.prog-step {
    display: flex; align-items: center; gap: 14px; padding: 0.6rem 0; font-size: 0.88rem;
    border-bottom: 1px solid rgba(255,255,255,0.035);
}
.prog-step:last-child { border-bottom: none; }
.prog-step.done   { color: #34d399; }
.prog-step.active { color: #c084fc; font-weight: 700; }
.prog-step.wait   { color: #2d3748; }
.prog-dot {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0; font-weight: 700;
}
.prog-dot.done   { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.38); }
.prog-dot.active { background: rgba(168,85,247,0.14); color: #c084fc; border: 1px solid rgba(168,85,247,0.5); animation: glowPulse 1.8s ease infinite; }
.prog-dot.wait   { background: rgba(255,255,255,0.025); color: #2d3748; border: 1px solid rgba(255,255,255,0.06); }
.prog-bar-track { height: 4px; background: rgba(255,255,255,0.05); border-radius: 4px; margin-top: 1.3rem; overflow: hidden; }
.prog-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #4338ca, #7c3aed, #a855f7, #ec4899, #4338ca);
    background-size: 400% 100%; border-radius: 4px;
    animation: gradientMove 2.5s ease infinite;
    box-shadow: 0 0 12px rgba(139,92,246,0.6);
}

/* CHIPS */
.chips { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 0.7rem; }
.chip {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.07));
    color: #a5b4fc; border: 1px solid rgba(99,102,241,0.28); border-radius: 100px;
    padding: 0.3rem 1rem; font-size: 0.78rem; font-weight: 700;
    transition: all 0.28s cubic-bezier(0.16,1,0.3,1);
    animation: bounceIn 0.45s ease both; cursor: default;
}
.chip:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.18));
    border-color: rgba(139,92,246,0.65); color: #d8b4fe;
    transform: translateY(-3px) scale(1.04); box-shadow: 0 6px 18px rgba(99,102,241,0.28);
}

/* KNOW LABELS */
.know-lbl {
    font-size: 0.72rem; font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.65rem;
    display: flex; align-items: center; gap: 7px;
}

/* SUCCESS */
.success-box {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(5,150,105,0.06));
    border: 1px solid rgba(16,185,129,0.32); border-radius: 16px; padding: 1.1rem 1.7rem;
    display: flex; align-items: center; gap: 12px;
    font-size: 0.9rem; font-weight: 700; color: #34d399;
    animation: bounceIn 0.55s ease;
    box-shadow: 0 6px 24px rgba(16,185,129,0.1); backdrop-filter: blur(8px);
}

/* DIVIDER */
.div {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.2), rgba(236,72,153,0.1), transparent);
    margin: 2rem 0;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.025) !important; border-radius: 16px !important;
    padding: 5px !important; gap: 4px !important;
    border: 1px solid rgba(139,92,246,0.18) !important; backdrop-filter: blur(10px) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 11px !important; font-weight: 700 !important; font-size: 0.82rem !important;
    color: #4e5d73 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.52rem 1.3rem !important; transition: all 0.22s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4338ca, #7c3aed, #a855f7) !important;
    color: white !important; box-shadow: 0 4px 18px rgba(99,102,241,0.45) !important;
}

/* TEXTAREA */
.stTextArea textarea {
    background: rgba(255,255,255,0.025) !important;
    border: 1.5px solid rgba(139,92,246,0.22) !important; border-radius: 18px !important;
    color: #dde4ef !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important; resize: none !important;
    transition: all 0.28s ease !important; backdrop-filter: blur(8px) !important; line-height: 1.7 !important;
}
.stTextArea textarea:focus {
    border-color: rgba(139,92,246,0.65) !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.1), 0 8px 30px rgba(0,0,0,0.3) !important;
    background: rgba(255,255,255,0.035) !important;
}
.stTextArea textarea::placeholder { color: #2d3748 !important; }

/* FILE UPLOADER */
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, rgba(99,102,241,0.04), rgba(168,85,247,0.03)) !important;
    border: 2px dashed rgba(99,102,241,0.28) !important; border-radius: 18px !important;
    transition: all 0.28s ease !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(168,85,247,0.6) !important;
    background: linear-gradient(135deg, rgba(99,102,241,0.09), rgba(168,85,247,0.06)) !important;
    box-shadow: 0 0 30px rgba(99,102,241,0.12) !important;
}

/* ANALYSE BUTTON */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #4338ca, #7c3aed, #a855f7, #ec4899) !important;
    background-size: 300% 300% !important; color: white !important; border: none !important;
    border-radius: 16px !important; padding: 0.78rem 2.6rem !important;
    font-weight: 800 !important; font-size: 1rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 6px 30px rgba(99,102,241,0.5), 0 2px 8px rgba(0,0,0,0.3) !important;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
    letter-spacing: 0.02em !important; animation: gradientMove 4s ease infinite !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 12px 40px rgba(99,102,241,0.65), 0 4px 12px rgba(0,0,0,0.3) !important;
}

/* DOWNLOAD BUTTON */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1e1b4b, #4338ca, #7c3aed) !important;
    color: white !important; border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 16px !important; padding: 0.75rem 2.4rem !important;
    font-weight: 800 !important; font-size: 0.95rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 6px 28px rgba(99,102,241,0.38) !important;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 12px 40px rgba(99,102,241,0.55) !important;
    border-color: rgba(168,85,247,0.6) !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: transparent !important;
    border-right: 1px solid rgba(139,92,246,0.14) !important;
}
[data-testid="stSidebar"] > div {
    background:
        radial-gradient(ellipse 80% 40% at 50% 0%, rgba(99,102,241,0.1) 0%, transparent 60%),
        linear-gradient(180deg, #060814 0%, #080a18 100%) !important;
    backdrop-filter: blur(20px) !important;
}

/* RADIO */
[data-testid="stRadio"] label {
    color: #7c8fa8 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 600 !important;
}

/* FOOTER */
.app-footer {
    background: linear-gradient(135deg, rgba(13,11,34,0.9), rgba(16,12,40,0.9));
    border: 1px solid rgba(139,92,246,0.18); border-radius: 18px;
    padding: 1.3rem 2rem; text-align: center; margin-top: 3rem;
    font-size: 0.82rem; color: #3d4f66; animation: fadeIn 0.6s ease; backdrop-filter: blur(12px);
    position: relative; overflow: hidden;
}
.app-footer::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), rgba(236,72,153,0.3), transparent);
}
.app-footer strong { color: #9333ea; }
</style>
""", unsafe_allow_html=True)


# ── Groq client ───────────────────────────────────────────────────────────────
def get_groq_client(sidebar_key=""):
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key: return Groq(api_key=key)
    except (KeyError, FileNotFoundError):
        pass
    key = os.environ.get("GROQ_API_KEY", "")
    if key: return Groq(api_key=key)
    if sidebar_key.strip(): return Groq(api_key=sidebar_key.strip())
    return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 0.8rem;'>
        <div style='width:52px;height:52px;
                    background:linear-gradient(135deg,#4f46e5,#7c3aed,#a855f7);
                    border-radius:15px;display:flex;align-items:center;
                    justify-content:center;margin:0 auto 0.8rem;
                    font-size:26px;box-shadow:0 4px 20px rgba(99,102,241,0.5);'>
            🧠
        </div>
        <div style='font-size:0.95rem;font-weight:700;color:#e2e8f0;'>AI Notes Summarizer</div>
        <div style='font-size:0.75rem;color:#475569;margin-top:3px;'>by Zainab Gondal</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;'>API Key</div>", unsafe_allow_html=True)
    sidebar_key = st.text_input("key", type="password", placeholder="gsk_...",
                                label_visibility="collapsed",
                                help="Free key at console.groq.com")
    st.markdown("<div style='font-size:0.75rem;color:#334155;margin-top:4px;'>🔑 Get free key at console.groq.com</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>Input Method</div>", unsafe_allow_html=True)
    input_mode = st.radio("", ["📋 Paste Text", "📁 Upload File"], label_visibility="collapsed")

    st.divider()

    st.markdown("""
    <div style='background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                border-radius:14px;padding:1rem;'>
        <div style='font-size:0.75rem;font-weight:700;color:#6366f1;
                    text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>
            Supported Formats
        </div>
        <div style='display:flex;flex-wrap:wrap;gap:6px;'>
            <span style='background:rgba(99,102,241,0.15);color:#a5b4fc;
                         border:1px solid rgba(99,102,241,0.3);border-radius:100px;
                         padding:2px 10px;font-size:0.72rem;font-weight:600;'>PDF</span>
            <span style='background:rgba(99,102,241,0.15);color:#a5b4fc;
                         border:1px solid rgba(99,102,241,0.3);border-radius:100px;
                         padding:2px 10px;font-size:0.72rem;font-weight:600;'>DOCX</span>
            <span style='background:rgba(99,102,241,0.15);color:#a5b4fc;
                         border:1px solid rgba(99,102,241,0.3);border-radius:100px;
                         padding:2px 10px;font-size:0.72rem;font-weight:600;'>TXT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-grid"></div>
    <div class="hero-corner-dots">
        <div class="hero-corner-dot" style="background:#ef4444;opacity:0.8;"></div>
        <div class="hero-corner-dot" style="background:#f59e0b;opacity:0.8;"></div>
        <div class="hero-corner-dot" style="background:#10b981;opacity:0.8;"></div>
    </div>
    <div class="hero-eyebrow">✦ Powered by Groq + Llama3 &nbsp;·&nbsp; 100% Free</div>
    <div class="hero-title">🧠 AI Notes Summarizer<br><span style="font-size:65%;">& Knowledge Extraction System</span></div>
    <div class="hero-sub">
        Transform raw lecture notes into structured summaries, key concepts<br>
        and study questions — intelligently, in seconds.
    </div>
    <div class="hero-author">✨ Created by Zainab Gondal</div>
</div>
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
raw_text = ""

if input_mode == "📋 Paste Text":
    st.markdown("""
    <div class="sec-head">
        <div class="sec-icon">📝</div>
        <div class="sec-title">Paste Your Lecture Notes</div>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)
    raw_text = st.text_area("", placeholder="Paste your lecture notes here...",
                            height=280, label_visibility="collapsed")
else:
    st.markdown("""
    <div class="sec-head">
        <div class="sec-icon">📁</div>
        <div class="sec-title">Upload Your Notes File</div>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf","docx","txt"],
                                     label_visibility="collapsed")
    if uploaded_file:
        with st.spinner("Extracting text..."):
            try:
                raw_text = extract_text_from_file(uploaded_file)
                st.markdown(f'<div class="success-box">✅ Extracted text from <strong>{uploaded_file.name}</strong></div>',
                            unsafe_allow_html=True)
                with st.expander("👀 Preview"):
                    st.code(raw_text[:600] + ("..." if len(raw_text)>600 else ""), language=None)
            except Exception as e:
                st.error(f"Could not read file: {e}")

st.markdown("<div style='margin:1.2rem 0'></div>", unsafe_allow_html=True)
analyse_clicked = st.button("🔍 Analyse Notes", type="primary")
st.markdown("<div class='div'></div>", unsafe_allow_html=True)


# ── Pipeline ──────────────────────────────────────────────────────────────────
if analyse_clicked:

    if not raw_text.strip():
        st.warning("Please paste some text or upload a file first.")
        st.stop()

    client = get_groq_client(sidebar_key)
    if client is None:
        st.error("Groq API key not found. Get your free key from console.groq.com")
        st.stop()

    clean      = clean_text(raw_text)
    word_count = count_words(clean)
    read_time  = estimate_read_time(clean)
    char_count = len(clean)

    # Progress tracker
    prog = st.empty()

    def show_step(n):
        steps = [
            ("Analysing document",       1),
            ("Generating summaries",     2),
            ("Extracting knowledge",     3),
            ("Building study questions", 4),
            ("Extracting keywords",      5),
        ]
        pct = int((n - 1) / len(steps) * 100)
        rows = ""
        for label, s in steps:
            if s < n:   cls, dot, txt = "done",  "✓", f"{label} — done"
            elif s == n: cls, dot, txt = "active", "●", f"{label}..."
            else:        cls, dot, txt = "wait",  "○", label
            rows += f'<div class="prog-step {cls}"><div class="prog-dot {cls}">{dot}</div>{txt}</div>'
        prog.markdown(f"""
        <div class="prog-box">
            <div class="prog-label">⚡ Processing your notes</div>
            {rows}
            <div class="prog-bar-track">
                <div class="prog-bar-fill" style="width:{pct}%"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Stats
    show_step(1)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">📊</div><div class="sec-title">Document Statistics</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-card"><div class="stat-num">{word_count:,}</div><div class="stat-lbl">Words</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-num">{char_count:,}</div><div class="stat-lbl">Characters</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-num">{read_time}</div><div class="stat-lbl">Read Time</div></div>', unsafe_allow_html=True)

    # Summaries
    show_step(2)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">📝</div><div class="sec-title">Summaries</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⚡ Quick Summary","📖 Detailed Summary","🎯 Key Points"])
    with tab1:
        with st.spinner(""):
            quick = generate_quick_summary(client, clean)
        st.markdown(f'<div class="out-card purple">{quick}</div>', unsafe_allow_html=True)
    with tab2:
        with st.spinner(""):
            time.sleep(4)
            detailed = generate_detailed_summary(client, clean)
        st.markdown(f'<div class="out-card green">{detailed}</div>', unsafe_allow_html=True)
    with tab3:
        with st.spinner(""):
            time.sleep(4)
            key_points = generate_key_points(client, clean)
        st.markdown(f'<div class="out-card amber">{key_points}</div>', unsafe_allow_html=True)

    # Knowledge
    show_step(3)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">🔬</div><div class="sec-title">Knowledge Extraction</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    with st.spinner(""):
        time.sleep(5)
        knowledge = run_full_extraction(client, clean)

    ke1, ke2 = st.columns(2)
    with ke1:
        st.markdown('<div class="know-lbl">🧩 Important Concepts</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="out-card purple">{knowledge["concepts"]}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="know-lbl">🏷️ Key Terms</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip">{t.strip()}</span>' for t in knowledge["key_terms"].split(",") if t.strip())
        st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)
    with ke2:
        st.markdown('<div class="know-lbl">📖 Definitions</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="out-card green">{knowledge["definitions"]}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="know-lbl">📌 Important Facts</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="out-card amber">{knowledge["important_facts"]}</div>', unsafe_allow_html=True)

    # Questions
    show_step(4)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">❓</div><div class="sec-title">Study Questions</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    with st.spinner(""):
        time.sleep(5)
        questions = generate_all_questions(client, clean)

    qt1, qt2, qt3 = st.tabs(["💭 Conceptual (5)","🔢 Multiple Choice (5)","✏️ Short Answer (3)"])
    with qt1:
        st.markdown(f'<div class="out-card purple">{questions["conceptual"]}</div>', unsafe_allow_html=True)
    with qt2:
        st.markdown(f'<div class="out-card green">{questions["mcq"]}</div>', unsafe_allow_html=True)
    with qt3:
        st.markdown(f'<div class="out-card rose">{questions["short_answer"]}</div>', unsafe_allow_html=True)

    # Keywords
    show_step(5)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">🏷️</div><div class="sec-title">NLP Keyword Extraction</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    st.caption("Extracted using NLTK frequency analysis · stop-words removed")
    keywords = extract_keywords(clean, top_n=25)
    if keywords:
        kchips = "".join(f'<span class="chip">{kw}</span>' for kw in keywords)
        st.markdown(f'<div class="chips">{kchips}</div>', unsafe_allow_html=True)

    # Done!
    prog.markdown('<div class="success-box">✅ Analysis complete — all sections generated successfully!</div>',
                  unsafe_allow_html=True)

    # Download
    st.markdown("""<div class="sec-head" style="margin-top:2rem;">
        <div class="sec-icon">⬇️</div><div class="sec-title">Download Your Summary</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)

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

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    🧠 AI Notes Summarizer &amp; Knowledge Extraction System &nbsp;·&nbsp;
    Created by <strong>Zainab Gondal</strong> &nbsp;·&nbsp;
    Powered by Groq + Llama3 &nbsp;·&nbsp; 100% Free
</div>
""", unsafe_allow_html=True)
