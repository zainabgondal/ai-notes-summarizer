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

# ── Dark Modern CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: #080b14 !important;
    color: #e2e8f0 !important;
}
.main { background-color: #080b14 !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Keyframes ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(139,92,246,0.3), 0 0 40px rgba(139,92,246,0.1); }
    50%       { box-shadow: 0 0 30px rgba(139,92,246,0.5), 0 0 60px rgba(139,92,246,0.2); }
}
@keyframes shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
@keyframes bounceIn {
    0%   { transform: scale(0.85); opacity: 0; }
    65%  { transform: scale(1.04); }
    100% { transform: scale(1); opacity: 1; }
}
@keyframes gradientMove {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes borderGlow {
    0%, 100% { border-color: rgba(139,92,246,0.4); }
    50%       { border-color: rgba(167,139,250,0.8); }
}
@keyframes slideRight {
    from { width: 0%; }
    to   { width: 100%; }
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0d0a1f 0%, #130d35 40%, #1a0a2e 100%);
    border: 1px solid rgba(139,92,246,0.35);
    border-radius: 24px;
    padding: 3rem 2.8rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.7s ease both;
    animation: glowPulse 4s ease-in-out infinite;
    box-shadow: 0 0 60px rgba(139,92,246,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}
.hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 15% 40%, rgba(99,102,241,0.18) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 60%, rgba(139,92,246,0.14) 0%, transparent 55%),
        radial-gradient(ellipse at 50% 100%, rgba(168,85,247,0.08) 0%, transparent 50%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.4);
    color: #c4b5fd;
    padding: 0.3rem 1rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    animation: fadeIn 0.8s ease 0.2s both;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1.05;
    background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 40%, #a78bfa 70%, #e879f9 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeInUp 0.7s ease 0.1s both, gradientMove 5s ease infinite;
    margin-bottom: 0.6rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: #94a3b8;
    font-weight: 400;
    margin-bottom: 1.8rem;
    animation: fadeInUp 0.7s ease 0.25s both;
    line-height: 1.6;
}
.hero-author {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7);
    background-size: 200% 200%;
    animation: fadeInUp 0.7s ease 0.4s both, gradientMove 4s ease infinite;
    color: white;
    padding: 0.5rem 1.4rem;
    border-radius: 100px;
    font-size: 0.9rem;
    font-weight: 700;
    box-shadow: 0 4px 24px rgba(139,92,246,0.5);
}
.hero-corner-dots {
    position: absolute; top: 20px; right: 24px;
    display: flex; gap: 7px; align-items: center;
}
.hero-corner-dot {
    width: 11px; height: 11px; border-radius: 50%;
}
.hero-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(139,92,246,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(139,92,246,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
}

/* ── Section headers ── */
.sec-head {
    display: flex; align-items: center; gap: 12px;
    margin: 2.2rem 0 1.2rem;
    animation: fadeInUp 0.5s ease both;
}
.sec-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    box-shadow: 0 4px 16px rgba(99,102,241,0.4);
    flex-shrink: 0;
}
.sec-title {
    font-size: 1.15rem; font-weight: 700; color: #f1f5f9;
}
.sec-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(139,92,246,0.4), transparent);
    margin-left: 4px;
}

/* ── Stat Cards ── */
.stat-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }
.stat-card {
    background: linear-gradient(135deg, #0f0c2a, #140e33);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 18px;
    padding: 1.5rem 1rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: fadeInUp 0.5s ease both;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
}
.stat-card::after {
    content: '';
    position: absolute; bottom: 0; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg, transparent, #7c3aed, transparent);
    border-radius: 2px;
}
.stat-card:hover {
    transform: translateY(-5px);
    border-color: rgba(139,92,246,0.65);
    box-shadow: 0 8px 32px rgba(139,92,246,0.25), inset 0 1px 0 rgba(255,255,255,0.06);
}
.stat-num {
    font-size: 2.1rem; font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1; margin-bottom: 0.35rem;
}
.stat-lbl {
    font-size: 0.7rem; font-weight: 700;
    color: #64748b; text-transform: uppercase; letter-spacing: 0.12em;
}

/* ── Output Cards ── */
.out-card {
    background: linear-gradient(145deg, #0d0b22, #100d2a);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    line-height: 1.85;
    font-size: 0.93rem;
    color: #cbd5e1;
    white-space: pre-wrap;
    word-wrap: break-word;
    animation: fadeInUp 0.5s ease both;
    transition: all 0.3s ease;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
}
.out-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 4px 0 0 4px;
}
.out-card.purple::before { background: linear-gradient(180deg, #4f46e5, #7c3aed, #a855f7); }
.out-card.green::before  { background: linear-gradient(180deg, #10b981, #059669); }
.out-card.amber::before  { background: linear-gradient(180deg, #f59e0b, #d97706); }
.out-card.rose::before   { background: linear-gradient(180deg, #f43f5e, #e11d48); }
.out-card.blue::before   { background: linear-gradient(180deg, #3b82f6, #2563eb); }
.out-card:hover {
    border-color: rgba(139,92,246,0.5);
    box-shadow: 0 8px 32px rgba(139,92,246,0.18), inset 0 1px 0 rgba(255,255,255,0.05);
    transform: translateY(-2px);
}

/* ── Progress ── */
.prog-box {
    background: linear-gradient(145deg, #0d0b22, #100d2a);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    animation: fadeInUp 0.4s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.prog-label {
    font-size: 0.72rem; font-weight: 700;
    color: #6366f1; text-transform: uppercase;
    letter-spacing: 0.1em; margin-bottom: 1rem;
}
.prog-step {
    display: flex; align-items: center; gap: 12px;
    padding: 0.55rem 0;
    font-size: 0.9rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.prog-step:last-child { border-bottom: none; }
.prog-step.done   { color: #34d399; }
.prog-step.active { color: #a78bfa; font-weight: 600; }
.prog-step.wait   { color: #334155; }
.prog-dot {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0; font-weight: 700;
}
.prog-dot.done   { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }
.prog-dot.active { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid rgba(139,92,246,0.5);
                   animation: glowPulse 1.5s ease infinite; }
.prog-dot.wait   { background: rgba(255,255,255,0.03); color: #334155; border: 1px solid rgba(255,255,255,0.07); }
.prog-bar-track {
    height: 3px; background: rgba(255,255,255,0.06);
    border-radius: 3px; margin-top: 1.2rem; overflow: hidden;
}
.prog-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #a855f7, #4f46e5);
    background-size: 300% 100%;
    border-radius: 3px;
    animation: gradientMove 2s ease infinite;
}

/* ── Chips ── */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.6rem; }
.chip {
    background: rgba(99,102,241,0.12);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 100px;
    padding: 0.28rem 0.9rem;
    font-size: 0.8rem; font-weight: 600;
    transition: all 0.25s ease;
    animation: bounceIn 0.4s ease both;
    cursor: default;
}
.chip:hover {
    background: rgba(99,102,241,0.28);
    border-color: rgba(139,92,246,0.7);
    color: #c4b5fd;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(99,102,241,0.3);
}

/* ── Know labels ── */
.know-lbl {
    font-size: 0.78rem; font-weight: 700;
    color: #64748b; text-transform: uppercase;
    letter-spacing: 0.09em; margin-bottom: 0.6rem;
    display: flex; align-items: center; gap: 6px;
}

/* ── Success banner ── */
.success-box {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(5,150,105,0.08));
    border: 1px solid rgba(16,185,129,0.35);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    display: flex; align-items: center; gap: 10px;
    font-size: 0.92rem; font-weight: 600; color: #34d399;
    animation: bounceIn 0.5s ease;
    box-shadow: 0 4px 20px rgba(16,185,129,0.1);
}

/* ── Divider ── */
.div { height: 1px; background: rgba(139,92,246,0.12); margin: 1.8rem 0; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    color: #64748b !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px solid rgba(139,92,246,0.25) !important;
    border-radius: 16px !important;
    color: #e2e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.93rem !important;
    resize: none !important;
    transition: border-color 0.25s ease !important;
}
.stTextArea textarea:focus {
    border-color: rgba(139,92,246,0.7) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stTextArea textarea::placeholder { color: #334155 !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] section {
    background: rgba(99,102,241,0.04) !important;
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 16px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(139,92,246,0.65) !important;
    background: rgba(99,102,241,0.08) !important;
}

/* ── Analyse button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7) !important;
    background-size: 200% 200% !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem 2.4rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.45) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.02em !important;
    animation: gradientMove 3s ease infinite !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.6) !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem 2.2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.4) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.55) !important;
}

/* ── Sidebar — solid dark, always visible on desktop + mobile ── */
section[data-testid="stSidebar"] {
    background-color: #0d0a1f !important;
    background-image:
        radial-gradient(ellipse 150% 40% at 50% 0%,  rgba(109,40,217,0.75) 0%, transparent 48%),
        radial-gradient(ellipse 110% 60% at 0%  90%,  rgba(168,85,247,0.4)  0%, transparent 58%),
        radial-gradient(ellipse 90%  50% at 100% 50%, rgba(56,189,248,0.15) 0%, transparent 55%) !important;
    border-right: 1px solid rgba(139,92,246,0.35) !important;
    min-width: 268px !important;
    max-width: 268px !important;
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
    min-height: 100vh !important;
}
/* ALL sidebar text visible */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] a {
    color: #c8d4e3 !important;
}
/* Sidebar input box */
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.08) !important;
    border: 1.5px solid rgba(139,92,246,0.4) !important;
    border-radius: 11px !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] input::placeholder { color: #374151 !important; }
section[data-testid="stSidebar"] input:focus {
    border-color: rgba(168,85,247,0.75) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
    background: rgba(255,255,255,0.1) !important;
}
/* Mobile — toggle button visible, sidebar as overlay */
@media screen and (max-width: 768px) {
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        background: linear-gradient(135deg,#3730a3,#7c3aed) !important;
        border-radius: 0 12px 12px 0 !important;
        border: 1px solid rgba(139,92,246,0.5) !important;
        box-shadow: 4px 0 20px rgba(99,102,241,0.4) !important;
        z-index: 9999 !important;
    }
    [data-testid="collapsedControl"] svg { fill: white !important; }
    section[data-testid="stSidebar"] {
        position: fixed !important;
        left: 0 !important; top: 0 !important;
        height: 100vh !important; z-index: 1000 !important;
        min-width: 270px !important; max-width: 88vw !important;
        box-shadow: 8px 0 40px rgba(0,0,0,0.7) !important;
    }
    section[data-testid="stSidebar"] > div {
        overflow-y: auto !important; height: 100vh !important;
    }
}

/* ── Radio ── */
[data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Footer ── */
.app-footer {
    background: linear-gradient(135deg, #0d0b22, #100d2a);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 16px;
    padding: 1.2rem 2rem;
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.82rem;
    color: #475569;
    animation: fadeIn 0.5s ease;
}
.app-footer strong { color: #7c3aed; }
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

    # Brand header
    st.markdown(
        "<div style=\"text-align:center;padding:1.3rem 0.3rem 1rem;"
        "border-bottom:1px solid rgba(139,92,246,0.28);margin-bottom:0.8rem;\">"
        "<div style=\"width:56px;height:56px;"
        "background:linear-gradient(135deg,#3730a3,#7c3aed,#a855f7,#ec4899);"
        "border-radius:16px;display:flex;align-items:center;justify-content:center;"
        "margin:0 auto 0.65rem;font-size:27px;"
        "box-shadow:0 6px 24px rgba(139,92,246,0.65);\">🧠</div>"
        "<div style=\"font-size:0.97rem;font-weight:800;"
        "background:linear-gradient(135deg,#f1f5f9,#c4b5fd);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        "background-clip:text;margin-bottom:0.22rem;\">AI Notes Summarizer</div>"
        "<div style=\"font-size:0.68rem;font-weight:700;"
        "background:linear-gradient(90deg,#a78bfa,#e879f9);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        "background-clip:text;margin-bottom:0.38rem;\">✨ by Zainab Gondal · v2.0</div>"
        "<div style=\"display:inline-block;background:rgba(16,185,129,0.15);"
        "border:1px solid rgba(16,185,129,0.38);border-radius:100px;"
        "padding:2px 12px;font-size:0.61rem;font-weight:700;color:#34d399;\">"
        "💚 100% Free · No Key Needed</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # API Key (optional)
    st.markdown(
        "<div style=\"font-size:0.62rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.1em;color:#a78bfa;margin-bottom:5px;\">"
        "🔑 API Key <span style=\"color:#475569;font-weight:500;text-transform:none;\">(optional)</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    sidebar_key = st.text_input("key", type="password",
                                placeholder="gsk_...  (leave empty = free)",
                                label_visibility="collapsed",
                                help="Free key at console.groq.com")
    st.markdown(
        "<div style=\"font-size:0.61rem;color:#475569;margin-top:3px;margin-bottom:0.7rem;\">"
        "Leave empty — app works 100% free ✅</div>",
        unsafe_allow_html=True,
    )

    # Input method
    st.markdown(
        "<div style=\"font-size:0.62rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.1em;color:#a78bfa;margin-bottom:6px;\">📥 Input Method</div>",
        unsafe_allow_html=True,
    )
    input_mode = st.radio("", ["📋 Paste Text", "📁 Upload File"],
                          label_visibility="collapsed")

    st.markdown("<div style=\"height:0.5rem\"></div>", unsafe_allow_html=True)

    # What you get
    st.markdown(
        "<div style=\"background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(168,85,247,0.06));"
        "border:1px solid rgba(139,92,246,0.22);border-radius:13px;"
        "padding:0.8rem 0.95rem;margin-bottom:0.55rem;\">"
        "<div style=\"font-size:0.6rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.1em;color:#a78bfa;margin-bottom:0.45rem;\">⚡ What You Get</div>"
        "<div style=\"display:flex;flex-direction:column;gap:4px;font-size:0.72rem;color:#c4b5fd;\">"
        "<div>📝 Quick · Detailed · Key Points</div>"
        "<div>🔬 Concepts · Definitions · Facts</div>"
        "<div>❓ 13 Study Questions (MCQ + more)</div>"
        "<div>🃏 Flashcards auto-generated</div>"
        "<div>📄 PDF + TXT download</div>"
        "<div>🏷️ NLP Keywords</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    # Formats + tip
    st.markdown(
        "<div style=\"background:rgba(255,255,255,0.03);"
        "border:1px solid rgba(139,92,246,0.15);border-radius:13px;"
        "padding:0.75rem 0.95rem;margin-bottom:0.55rem;\">"
        "<div style=\"font-size:0.6rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.1em;color:#a78bfa;margin-bottom:0.4rem;\">📂 Formats</div>"
        "<div style=\"display:flex;gap:5px;flex-wrap:wrap;margin-bottom:0.4rem;\">"
        "<span style=\"background:rgba(99,102,241,0.18);color:#c4b5fd;"
        "border:1px solid rgba(99,102,241,0.32);border-radius:100px;"
        "padding:2px 10px;font-size:0.67rem;font-weight:700;\">📄 PDF</span>"
        "<span style=\"background:rgba(99,102,241,0.18);color:#c4b5fd;"
        "border:1px solid rgba(99,102,241,0.32);border-radius:100px;"
        "padding:2px 10px;font-size:0.67rem;font-weight:700;\">📝 DOCX</span>"
        "<span style=\"background:rgba(99,102,241,0.18);color:#c4b5fd;"
        "border:1px solid rgba(99,102,241,0.32);border-radius:100px;"
        "padding:2px 10px;font-size:0.67rem;font-weight:700;\">📃 TXT</span>"
        "</div>"
        "<div style=\"font-size:0.68rem;color:#6ee7b7;line-height:1.45;\">"
        "💡 Best: 200–2000 words · Full pack in 60 sec!"
        "</div></div>",
        unsafe_allow_html=True,
    )

    # Footer
    st.markdown(
        "<div style=\"border-top:1px solid rgba(139,92,246,0.18);"
        "padding-top:0.75rem;text-align:center;\">"
        "<div style=\"font-size:0.63rem;color:#475569;margin-bottom:0.55rem;\">"
        "Crafted with 💜 by "
        "<span style=\"font-weight:800;"
        "background:linear-gradient(90deg,#a78bfa,#e879f9);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        "background-clip:text;\">Zainab Gondal</span></div>"
        "<a href=\"https://www.linkedin.com/in/zainabgondal/\" target=\"_blank\" "
        "style=\"display:block;background:rgba(10,102,194,0.18);"
        "border:1px solid rgba(10,102,194,0.4);color:#93c5fd;"
        "padding:7px;border-radius:10px;font-size:0.7rem;font-weight:700;"
        "margin-bottom:5px;text-decoration:none;text-align:center;\">💼 LinkedIn</a>"
        "<a href=\"https://github.com/zainabgondal\" target=\"_blank\" "
        "style=\"display:block;background:rgba(255,255,255,0.05);"
        "border:1px solid rgba(255,255,255,0.12);color:#e2e8f0;"
        "padding:7px;border-radius:10px;font-size:0.7rem;font-weight:700;"
        "text-decoration:none;text-align:center;\">🐙 GitHub</a>"
        "</div>",
        unsafe_allow_html=True,
    )


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
