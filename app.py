"""
app.py
------
AI Notes Summarizer & Knowledge Extraction System
Fully Responsive & Dynamic UI for all devices.
Powered by Groq API.
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
    initial_sidebar_state="collapsed", # Better for mobile first-view
)

# ── Cosmic UI CSS + JS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* ════════════════════════════════════════════
   NUCLEAR BACKGROUND OVERRIDE — ALL LAYERS
════════════════════════════════════════════ */

html { background: #02030d !important; }
body { background: #02030d !important; }
.stApp { background: #02030d !important; }

/* Step 2: Font + color on everything */
html, body, [class*="css"], [data-testid] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #e2e8f0 !important;
}

/* Step 3: THE REAL COSMIC BACKGROUND */
body::before {
    content: '';
    position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background:
        radial-gradient(ellipse 90% 55% at 0%    0%,   rgba(88,28,220,0.4)   0%, transparent 52%),
        radial-gradient(ellipse 70% 50% at 100%  0%,   rgba(14,165,233,0.22) 0%, transparent 50%),
        radial-gradient(ellipse 65% 55% at 100% 100%,  rgba(236,72,153,0.22) 0%, transparent 52%),
        radial-gradient(ellipse 80% 50% at 0%   100%,  rgba(99,102,241,0.2)  0%, transparent 52%),
        radial-gradient(ellipse 50% 40% at 50%   50%,  rgba(139,92,246,0.12) 0%, transparent 60%),
        linear-gradient(145deg, #02030d 0%, #06071a 30%, #0a0520 60%, #050210 100%);
    background-attachment: fixed;
    animation: orbDrift 20s ease-in-out infinite alternate;
}

@keyframes orbDrift {
    0%   { transform: translate(0px, 0px) scale(1); }
    100% { transform: translate(18px, -12px) scale(1.03); }
}

[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
.block-container { 
    padding-top: 1.8rem !important; 
    padding-bottom: 4rem !important; 
    max-width: 1100px !important; 
}

/* ════════════════════════════════════════════
   MOBILE RESPONSIVENESS OVERRIDE
════════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    .hero {
        padding: 2rem 1.5rem !important;
    }
    .hero-title {
        font-size: 2.2rem !important;
        line-height: 1.1;
    }
    .feat-row {
        grid-template-columns: repeat(2, 1fr) !important;
    }
    .stat-row {
        grid-template-columns: 1fr !important;
    }
    .out-card, .prog-box {
        padding: 1.5rem !important;
    }
    div[data-testid="stButton"] > button, 
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important;
    }
    /* Stop heavy animations on mobile for performance */
    body::before { animation: none !important; }
}

/* ════════════════════════════════════════════
   EXISTING UI COMPONENTS (HERO, CARDS, ETC)
════════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg, rgba(10,6,30,0.96) 0%, rgba(18,10,48,0.96) 45%);
    border: 1px solid rgba(139,92,246,0.32);
    border-radius: 28px; padding: 3.4rem 3.2rem 3rem;
    margin-bottom: 2.4rem; position: relative;
    box-shadow: 0 40px 100px rgba(0,0,0,0.7);
}

.hero-title {
    font-size: 3.5rem; font-weight: 900;
    background: linear-gradient(120deg, #ffffff, #c4b5fd);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.feat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 2rem; }
.feat-card {
    background: rgba(12,9,32,0.85); border: 1px solid rgba(139,92,246,0.18);
    border-radius: 16px; padding: 1.1rem; text-align: center;
}

.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-card {
    background: rgba(12,9,32,0.88); border: 1px solid rgba(139,92,246,0.2);
    border-radius: 22px; padding: 1.8rem 1.2rem; text-align: center;
}

.out-card {
    background: rgba(10,8,28,0.94); border: 1px solid rgba(139,92,246,0.18);
    border-radius: 20px; padding: 1.9rem 2.1rem; color: #b8c8dc;
}

/* ════════════════════════════════════════════
   TABS & INPUTS
════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02) !important; border-radius: 18px !important;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.022) !important;
    border: 1.5px solid rgba(139,92,246,0.2) !important; border-radius: 18px !important;
}

</style>
""", unsafe_allow_value=True)

# ── Header Section ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">✨ Next-Gen Knowledge Engine</div>
    <div class="hero-title">AI Notes Summarizer</div>
    <div class="hero-sub">Transform complex documents into structured insights and study materials instantly.</div>
    <div class="hero-author">Created by Zainab Gondal</div>
</div>
""", unsafe_allow_value=True)

# ── Main Application Logic ────────────────────────────────────────────────────
# [Insert your core processing logic here from the original app.py]
