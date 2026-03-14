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
from flashcard_generator import generate_flashcards

# ── Session state defaults ────────────────────────────────────────────────────



st.set_page_config(
    page_title="AI Notes Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Cosmic UI CSS + JS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* ════════════════════════════════════════════
   NUCLEAR BACKGROUND OVERRIDE — ALL LAYERS
════════════════════════════════════════════ */

/* Base dark background — overridden by light theme CSS when active */
html, body { background: #02030d !important; }
#root, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[class*="appview"] { background: #02030d !important; }
[data-testid="stHeader"],
[data-testid="stDecoration"],
section[data-testid="stSidebar"] + div,
.main > div, section.main, .main,
[class*="block-container"],
[class*="stMarkdown"],
[class*="element-container"] { background: transparent !important; }

/* Step 2: Font + color on everything */
html, body, [class*="css"], [data-testid] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #e2e8f0 !important;
}

/* Step 3: THE REAL COSMIC BACKGROUND — fixed to viewport */
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

/* Step 4: Floating animated orbs */
body::after {
    content: '';
    position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background:
        radial-gradient(circle 300px at 15% 25%,  rgba(99,102,241,0.14)  0%, transparent 70%),
        radial-gradient(circle 400px at 85% 20%,  rgba(139,92,246,0.1)   0%, transparent 70%),
        radial-gradient(circle 260px at 70% 75%,  rgba(236,72,153,0.11)  0%, transparent 70%),
        radial-gradient(circle 340px at 25% 80%,  rgba(56,189,248,0.08)  0%, transparent 70%);
    animation: orbDrift2 25s ease-in-out infinite alternate;
}

@keyframes orbDrift {
    0%   { transform: translate(0px,    0px)   scale(1);    }
    33%  { transform: translate(35px,  -25px)  scale(1.06); }
    66%  { transform: translate(-25px,  35px)  scale(0.96); }
    100% { transform: translate(18px,  -12px)  scale(1.03); }
}
@keyframes orbDrift2 {
    0%   { transform: translate(0px,   0px)   scale(1);    }
    50%  { transform: translate(-30px, 25px)  scale(1.04); }
    100% { transform: translate(20px, -20px)  scale(0.98); }
}

[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
/* Re-assert sidebar AFTER nuclear reset */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(ellipse 120% 35% at 50% 0%,  rgba(109,40,217,0.6)  0%, transparent 50%),
        radial-gradient(ellipse 90%  50% at 0%   80%, rgba(168,85,247,0.3)  0%, transparent 60%),
        linear-gradient(160deg, #0d0a1f 0%, #120e2e 40%, #0a0818 100%) !important;
}
.block-container { padding-top: 1.8rem !important; padding-bottom: 4rem !important; max-width: 1100px !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ════════════════════════════════════════════
   KEYFRAMES
════════════════════════════════════════════ */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes floatUpDown {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-7px); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 25px rgba(139,92,246,0.3), 0 0 50px rgba(139,92,246,0.1); }
    50%       { box-shadow: 0 0 45px rgba(139,92,246,0.55), 0 0 80px rgba(139,92,246,0.18); }
}
@keyframes bounceIn {
    0%   { transform: scale(0.8); opacity: 0; }
    65%  { transform: scale(1.06); }
    100% { transform: scale(1);   opacity: 1; }
}
@keyframes gradientMove {
    0%   { background-position: 0%   50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0%   50%; }
}
@keyframes borderSpin {
    to { --angle: 360deg; }
}
@keyframes scanPulse {
    0%   { opacity: 0;   top: 0%; }
    10%  { opacity: 0.6; }
    90%  { opacity: 0.6; }
    100% { opacity: 0;   top: 100%; }
}
@keyframes ripple {
    0%   { transform: scale(0.8); opacity: 1; }
    100% { transform: scale(2.2); opacity: 0; }
}
@keyframes starTwinkle {
    0%, 100% { opacity: 0.2; transform: scale(1); }
    50%       { opacity: 1;   transform: scale(1.4); }
}

/* ════════════════════════════════════════════
   FLOATING STAR PARTICLES (CSS-only)
════════════════════════════════════════════ */
.stars-layer {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}
.star {
    position: absolute; border-radius: 50%;
    background: white; animation: starTwinkle linear infinite;
}

/* ════════════════════════════════════════════
   HERO
════════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg,
        rgba(10,6,30,0.96) 0%,
        rgba(18,10,48,0.96) 45%,
        rgba(8,5,25,0.96) 100%);
    border: 1px solid rgba(139,92,246,0.32);
    border-radius: 28px; padding: 3.4rem 3.2rem 3rem;
    margin-bottom: 2.4rem; position: relative; overflow: hidden;
    animation: fadeInUp 0.9s cubic-bezier(0.16,1,0.3,1) both;
    box-shadow:
        0 0 0 1px rgba(255,255,255,0.045) inset,
        0 40px 100px rgba(0,0,0,0.7),
        0 0 120px rgba(99,102,241,0.12),
        0 0 60px  rgba(168,85,247,0.08);
}
/* Rainbow animated top border */
.hero::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg,
        #6366f1, #8b5cf6, #a855f7, #ec4899, #f43f5e,
        #fb923c, #facc15, #4ade80, #38bdf8, #6366f1);
    background-size: 400% 100%;
    animation: gradientMove 5s linear infinite;
    border-radius: 28px 28px 0 0;
}
/* Mesh grid */
.hero-grid {
    position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(139,92,246,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(139,92,246,0.04) 1px, transparent 1px);
    background-size: 44px 44px;
}
/* Inner radial glows */
.hero::before {
    content: '';
    position: absolute; inset: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 55% 70% at 3%   50%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 97%  50%, rgba(168,85,247,0.13) 0%, transparent 60%),
        radial-gradient(ellipse 40% 50% at 50% 110%, rgba(236,72,153,0.09) 0%, transparent 55%);
}
/* Scan line */
.hero-scan {
    position: absolute; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), rgba(236,72,153,0.3), transparent);
    animation: scanPulse 5s ease-in-out infinite;
    pointer-events: none;
}
.hero-corner-dots { position: absolute; top: 22px; right: 26px; display: flex; gap: 8px; align-items: center; }
.hero-corner-dot  { width: 12px; height: 12px; border-radius: 50%; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.13));
    border: 1px solid rgba(139,92,246,0.5); color: #c4b5fd;
    padding: 0.34rem 1.2rem; border-radius: 100px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
    margin-bottom: 1.4rem; animation: fadeIn 0.9s ease 0.15s both;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 16px rgba(99,102,241,0.2), inset 0 1px 0 rgba(255,255,255,0.06);
}
.hero-title {
    font-size: 3.5rem; font-weight: 900; line-height: 1.03;
    background: linear-gradient(120deg,
        #ffffff 0%, #f0e8ff 18%, #c4b5fd 38%,
        #f0abfc 58%, #67e8f9 78%, #a5f3fc 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: fadeInUp 0.7s ease 0.08s both, gradientMove 7s ease infinite;
    margin-bottom: 0.8rem; letter-spacing: -0.025em;
}
.hero-sub {
    font-size: 1.06rem; color: #6b7d96; font-weight: 400; margin-bottom: 2.2rem;
    animation: fadeInUp 0.7s ease 0.22s both; line-height: 1.75; max-width: 560px;
}
.hero-badges {
    display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 1.8rem;
    animation: fadeInUp 0.7s ease 0.3s both;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    color: #94a3b8; padding: 0.3rem 0.9rem; border-radius: 100px;
    font-size: 0.72rem; font-weight: 600; backdrop-filter: blur(8px);
    transition: all 0.25s ease;
}
.hero-badge:hover { border-color: rgba(139,92,246,0.5); color: #c4b5fd; background: rgba(99,102,241,0.1); }
.hero-author {
    display: inline-flex; align-items: center; gap: 10px;
    background: linear-gradient(135deg, #3730a3, #6d28d9, #9333ea, #db2777);
    background-size: 300% 300%;
    animation: fadeInUp 0.7s ease 0.4s both, gradientMove 6s ease infinite;
    color: white; padding: 0.6rem 1.8rem; border-radius: 100px;
    font-size: 0.88rem; font-weight: 800;
    box-shadow: 0 8px 35px rgba(139,92,246,0.55), 0 2px 8px rgba(0,0,0,0.4),
                inset 0 1px 0 rgba(255,255,255,0.15);
    letter-spacing: 0.01em; position: relative; overflow: hidden;
}
.hero-author::after {
    content: '';
    position: absolute; top: -50%; left: -60%; width: 40%; height: 200%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transform: skewX(-20deg);
    animation: shimmerBtn 3s ease infinite;
}
@keyframes shimmerBtn {
    0%   { left: -60%; }
    100% { left: 160%; }
}

/* ════════════════════════════════════════════
   FEATURE BADGES ROW (new element)
════════════════════════════════════════════ */
.feat-row {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
    margin-bottom: 2rem; animation: fadeInUp 0.6s ease 0.1s both;
}
.feat-card {
    background: linear-gradient(145deg, rgba(12,9,32,0.85), rgba(16,12,40,0.85));
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 16px; padding: 1.1rem 1rem; text-align: center;
    backdrop-filter: blur(12px); cursor: default;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
    position: relative; overflow: hidden;
}
.feat-card::before {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(139,92,246,0.05) 0%, transparent 60%);
    border-radius: inherit; pointer-events: none;
}
.feat-card:hover {
    transform: translateY(-5px) scale(1.02);
    border-color: rgba(139,92,246,0.45);
    box-shadow: 0 16px 40px rgba(99,102,241,0.18), inset 0 1px 0 rgba(255,255,255,0.05);
}
.feat-icon { font-size: 1.6rem; margin-bottom: 0.5rem; display: block; animation: floatUpDown 3s ease-in-out infinite; }
.feat-label { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; }
.feat-val {
    font-size: 0.88rem; font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #e879f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-top: 0.2rem;
}

/* ════════════════════════════════════════════
   SECTION HEADERS
════════════════════════════════════════════ */
.sec-head {
    display: flex; align-items: center; gap: 14px; margin: 2.6rem 0 1.4rem;
    animation: fadeInUp 0.5s ease both;
}
.sec-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #3730a3, #7c3aed, #a855f7);
    border-radius: 13px; display: flex; align-items: center; justify-content: center;
    font-size: 19px; flex-shrink: 0;
    box-shadow: 0 8px 24px rgba(99,102,241,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    animation: floatUpDown 4s ease-in-out infinite; position: relative;
}
/* Ripple ring on icon */
.sec-icon::after {
    content: ''; position: absolute; inset: -4px;
    border-radius: 17px; border: 1px solid rgba(139,92,246,0.3);
    animation: ripple 2.5s ease-out infinite;
}
.sec-title { font-size: 1.2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.015em; }
.sec-line {
    flex: 1; height: 1px; margin-left: 6px;
    background: linear-gradient(90deg, rgba(139,92,246,0.5), rgba(236,72,153,0.25), rgba(56,189,248,0.1), transparent);
}

/* ════════════════════════════════════════════
   STAT CARDS
════════════════════════════════════════════ */
.stat-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.stat-card {
    background: linear-gradient(145deg, rgba(12,9,32,0.88), rgba(18,12,44,0.88));
    border: 1px solid rgba(139,92,246,0.2); border-radius: 22px;
    padding: 1.8rem 1.2rem; text-align: center;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1);
    animation: fadeInUp 0.6s ease both; position: relative; overflow: hidden;
    backdrop-filter: blur(14px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
}
.stat-card::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99,102,241,0.08) 0%, transparent 70%);
    border-radius: inherit; pointer-events: none;
}
.stat-card::after {
    content: ''; position: absolute; bottom: 0; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg, transparent, #7c3aed, #ec4899, #38bdf8, transparent);
    border-radius: 2px;
}
.stat-card:hover {
    transform: translateY(-8px) scale(1.03); border-color: rgba(139,92,246,0.5);
    box-shadow: 0 24px 60px rgba(99,102,241,0.22), inset 0 1px 0 rgba(255,255,255,0.07);
}
.stat-num {
    font-size: 2.5rem; font-weight: 900;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc, #e879f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1; margin-bottom: 0.45rem; letter-spacing: -0.025em;
}
.stat-lbl {
    font-size: 0.67rem; font-weight: 700; color: #3d4f66;
    text-transform: uppercase; letter-spacing: 0.15em;
}

/* ════════════════════════════════════════════
   OUTPUT CARDS
════════════════════════════════════════════ */
.out-card {
    background: linear-gradient(155deg, rgba(10,8,28,0.94), rgba(14,10,36,0.94));
    border: 1px solid rgba(139,92,246,0.18); border-radius: 20px;
    padding: 1.9rem 2.1rem; line-height: 1.95; font-size: 0.92rem; color: #b8c8dc;
    white-space: pre-wrap; word-wrap: break-word;
    animation: fadeInUp 0.55s ease both;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1);
    position: relative; overflow: hidden; backdrop-filter: blur(12px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.025);
}
/* Shimmer on load */
.out-card::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.022) 50%, transparent 65%);
    background-size: 600px 100%; animation: shimmerSweep 2.5s ease 0.3s both;
    pointer-events: none;
}
@keyframes shimmerSweep {
    0%   { background-position: -600px 0; }
    100% { background-position: 600px  0; }
}
.out-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; border-radius: 4px 0 0 4px;
}
.out-card.purple::before { background: linear-gradient(180deg, #3730a3, #7c3aed, #a855f7, #c084fc); }
.out-card.green::before  { background: linear-gradient(180deg, #047857, #10b981, #34d399); }
.out-card.amber::before  { background: linear-gradient(180deg, #b45309, #f59e0b, #fcd34d); }
.out-card.rose::before   { background: linear-gradient(180deg, #9f1239, #f43f5e, #fda4af); }
.out-card.blue::before   { background: linear-gradient(180deg, #1d4ed8, #3b82f6, #93c5fd); }
.out-card:hover {
    border-color: rgba(139,92,246,0.4);
    box-shadow: 0 20px 55px rgba(99,102,241,0.16), inset 0 1px 0 rgba(255,255,255,0.04);
    transform: translateY(-3px); color: #d0dcea;
}

/* ════════════════════════════════════════════
   PROGRESS TRACKER
════════════════════════════════════════════ */
.prog-box {
    background: linear-gradient(145deg, rgba(10,8,28,0.94), rgba(14,10,36,0.94));
    border: 1px solid rgba(139,92,246,0.26); border-radius: 22px; padding: 2rem 2.4rem;
    animation: fadeInUp 0.45s ease; backdrop-filter: blur(14px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.55), 0 0 80px rgba(99,102,241,0.06);
    position: relative; overflow: hidden;
}
.prog-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #6366f1, #a855f7, #ec4899, transparent);
    background-size: 300% 100%; animation: gradientMove 3s ease infinite;
}
.prog-label {
    font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1.2rem;
    background: linear-gradient(90deg, #818cf8, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.prog-step {
    display: flex; align-items: center; gap: 14px; padding: 0.65rem 0; font-size: 0.88rem;
    border-bottom: 1px solid rgba(255,255,255,0.03);
}
.prog-step:last-child { border-bottom: none; }
.prog-step.done   { color: #34d399; }
.prog-step.active { color: #d8b4fe; font-weight: 700; }
.prog-step.wait   { color: #1e293b; }
.prog-dot {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0; font-weight: 700;
}
.prog-dot.done   { background: rgba(16,185,129,0.1);  color: #34d399; border: 1px solid rgba(16,185,129,0.35); }
.prog-dot.active { background: rgba(168,85,247,0.14); color: #d8b4fe; border: 1px solid rgba(168,85,247,0.55); animation: glowPulse 1.8s ease infinite; }
.prog-dot.wait   { background: rgba(255,255,255,0.02); color: #1e293b; border: 1px solid rgba(255,255,255,0.05); }
.prog-bar-track { height: 5px; background: rgba(255,255,255,0.04); border-radius: 5px; margin-top: 1.4rem; overflow: hidden; }
.prog-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #3730a3, #7c3aed, #a855f7, #ec4899, #f43f5e, #3730a3);
    background-size: 400% 100%; border-radius: 5px;
    animation: gradientMove 3s ease infinite;
    box-shadow: 0 0 16px rgba(139,92,246,0.65);
}

/* ════════════════════════════════════════════
   CHIPS / TAGS
════════════════════════════════════════════ */
.chips { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 0.8rem; }
.chip {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.07));
    color: #a5b4fc; border: 1px solid rgba(99,102,241,0.26); border-radius: 100px;
    padding: 0.32rem 1.05rem; font-size: 0.77rem; font-weight: 700;
    transition: all 0.28s cubic-bezier(0.16,1,0.3,1);
    animation: bounceIn 0.45s ease both; cursor: default; backdrop-filter: blur(6px);
}
.chip:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.26), rgba(168,85,247,0.2));
    border-color: rgba(139,92,246,0.65); color: #ddd6fe;
    transform: translateY(-3px) scale(1.05); box-shadow: 0 6px 20px rgba(99,102,241,0.3);
}

/* ════════════════════════════════════════════
   KNOWLEDGE LABELS
════════════════════════════════════════════ */
.know-lbl {
    font-size: 0.71rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.11em; margin-bottom: 0.7rem;
    background: linear-gradient(90deg, #818cf8, #c084fc, #e879f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    display: flex; align-items: center; gap: 7px;
}

/* ════════════════════════════════════════════
   SUCCESS BOX
════════════════════════════════════════════ */
.success-box {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(5,150,105,0.06));
    border: 1px solid rgba(16,185,129,0.3); border-radius: 18px; padding: 1.2rem 1.8rem;
    display: flex; align-items: center; gap: 12px;
    font-size: 0.9rem; font-weight: 700; color: #34d399;
    animation: bounceIn 0.55s ease;
    box-shadow: 0 6px 30px rgba(16,185,129,0.1), 0 0 60px rgba(16,185,129,0.05);
    backdrop-filter: blur(8px); position: relative; overflow: hidden;
}
.success-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(52,211,153,0.5), transparent);
}

/* ════════════════════════════════════════════
   DIVIDER
════════════════════════════════════════════ */
.div {
    height: 1px; margin: 2.2rem 0;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.22), rgba(236,72,153,0.12), rgba(56,189,248,0.08), transparent);
}

/* ════════════════════════════════════════════
   GLASSMORPHISM INFO BOX (new)
════════════════════════════════════════════ */
.glass-box {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 20px;
    padding: 1.4rem 1.8rem; backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06);
    animation: fadeInUp 0.5s ease both;
}

/* ════════════════════════════════════════════
   TABS
════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02) !important; border-radius: 18px !important;
    padding: 6px !important; gap: 5px !important;
    border: 1px solid rgba(139,92,246,0.16) !important; backdrop-filter: blur(12px) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important; font-weight: 700 !important; font-size: 0.82rem !important;
    color: #3d4f66 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.54rem 1.4rem !important; transition: all 0.22s ease !important; letter-spacing: 0.01em !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #94a3b8 !important; background: rgba(255,255,255,0.04) !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3730a3, #7c3aed, #a855f7) !important;
    color: white !important; box-shadow: 0 4px 20px rgba(99,102,241,0.5) !important;
}

/* ════════════════════════════════════════════
   TEXTAREA
════════════════════════════════════════════ */
.stTextArea textarea {
    background: #0d0b22 !important;
    background-color: #0d0b22 !important;
    border: 1.5px solid rgba(139,92,246,0.35) !important;
    border-radius: 18px !important;
    color: #e2e8f0 !important;
    caret-color: #a78bfa !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    resize: none !important;
    transition: all 0.3s ease !important;
    line-height: 1.75 !important;
    box-shadow: inset 0 2px 12px rgba(0,0,0,0.4) !important;
}
.stTextArea textarea:focus {
    background: #100e28 !important;
    background-color: #100e28 !important;
    color: #f1f5f9 !important;
    border-color: rgba(139,92,246,0.7) !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.12), inset 0 2px 12px rgba(0,0,0,0.4) !important;
}
.stTextArea textarea::placeholder { color: #3d4f66 !important; }
/* Force dark on every possible Streamlit textarea wrapper */
[data-testid="stTextArea"] textarea,
[data-baseweb="textarea"] textarea,
div[class*="stTextArea"] textarea {
    background: #0d0b22 !important;
    background-color: #0d0b22 !important;
    color: #e2e8f0 !important;
}

/* ════════════════════════════════════════════
   FILE UPLOADER — full dark theme
════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, rgba(99,102,241,0.06), rgba(168,85,247,0.04)) !important;
    border: 2px dashed rgba(99,102,241,0.32) !important;
    border-radius: 20px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(168,85,247,0.65) !important;
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.07)) !important;
    box-shadow: 0 0 40px rgba(99,102,241,0.15) !important;
}
/* Upload area label text */
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploadDropzone"] span {
    color: #94a3b8 !important;
}
/* BROWSE FILES button — was white */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploadDropzone"] button,
[data-testid="stFileUploader"] section button {
    background: linear-gradient(135deg, #3730a3, #6d28d9) !important;
    color: #ffffff !important;
    border: 1px solid rgba(139,92,246,0.5) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 1.1rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.4) !important;
}
[data-testid="stFileUploader"] section button:hover {
    background: linear-gradient(135deg, #4338ca, #7c3aed) !important;
    box-shadow: 0 6px 22px rgba(99,102,241,0.55) !important;
    transform: translateY(-2px) !important;
}
/* Uploaded file name pill */
[data-testid="stFileUploader"] [data-testid="stUploadedFile"] {
    background: rgba(99,102,241,0.1) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #c4b5fd !important;
}
[data-testid="stFileUploader"] [data-testid="stUploadedFile"] span {
    color: #c4b5fd !important;
}
/* Delete (×) button on uploaded file */
[data-testid="stFileUploader"] [data-testid="stUploadedFile"] button {
    background: rgba(244,63,94,0.15) !important;
    border: 1px solid rgba(244,63,94,0.3) !important;
    color: #fda4af !important;
    border-radius: 6px !important;
    padding: 0.2rem 0.4rem !important;
    box-shadow: none !important;
}

/* ════════════════════════════════════════════
   SPINNER
════════════════════════════════════════════ */
[data-testid="stSpinner"] > div,
.stSpinner > div {
    border-top-color: #7c3aed !important;
    border-color: rgba(139,92,246,0.2) !important;
}
[data-testid="stSpinner"] p,
.stSpinner p {
    color: #94a3b8 !important;
}

/* ════════════════════════════════════════════
   CAPTION
════════════════════════════════════════════ */
[data-testid="stCaptionContainer"] p,
.stCaption, caption, small {
    color: #4a5568 !important;
    font-size: 0.78rem !important;
}

/* ════════════════════════════════════════════
   CODE BLOCK — dark background
════════════════════════════════════════════ */
[data-testid="stCode"],
.stCode,
[data-testid="stCodeBlock"],
pre, code {
    background: #0a0818 !important;
    background-color: #0a0818 !important;
    color: #c4b5fd !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 12px !important;
}
[data-testid="stCode"] code,
pre code {
    background: transparent !important;
    color: #c4b5fd !important;
}
/* Copy button on code block */
[data-testid="stCode"] button {
    background: rgba(99,102,241,0.15) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    padding: 0.25rem 0.5rem !important;
}

/* ════════════════════════════════════════════
   WARNING / ERROR / INFO / SUCCESS ALERTS
════════════════════════════════════════════ */
[data-testid="stAlert"] {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.28) !important;
    border-radius: 14px !important;
    color: #c4b5fd !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #c4b5fd !important;
}
/* Warning — amber tint */
div[data-baseweb="notification"][kind="warning"],
[data-testid="stAlert"][data-type="warning"] {
    background: rgba(245,158,11,0.1) !important;
    border-color: rgba(245,158,11,0.35) !important;
}
[data-testid="stAlert"][data-type="warning"] p,
[data-testid="stAlert"][data-type="warning"] span {
    color: #fcd34d !important;
}
/* Error — red tint */
[data-testid="stAlert"][data-type="error"],
div[data-baseweb="notification"][kind="error"] {
    background: rgba(244,63,94,0.1) !important;
    border-color: rgba(244,63,94,0.35) !important;
}
[data-testid="stAlert"][data-type="error"] p,
[data-testid="stAlert"][data-type="error"] span {
    color: #fda4af !important;
}
/* Success — green tint */
[data-testid="stAlert"][data-type="success"] {
    background: rgba(16,185,129,0.08) !important;
    border-color: rgba(16,185,129,0.3) !important;
}
[data-testid="stAlert"][data-type="success"] p,
[data-testid="stAlert"][data-type="success"] span {
    color: #6ee7b7 !important;
}

/* ════════════════════════════════════════════
   EXPANDER — dark bg + visible header text
════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: rgba(13,11,34,0.85) !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 16px !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(139,92,246,0.4) !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: #a5b4fc !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary svg {
    fill: #7c3aed !important;
    color: #7c3aed !important;
}
/* Content inside expander */
[data-testid="stExpander"] > div > div {
    background: transparent !important;
    color: #cbd5e1 !important;
}

/* ════════════════════════════════════════════
   ALL SECONDARY / GHOST BUTTONS (non-primary)
════════════════════════════════════════════ */
div[data-testid="stButton"] > button:not([kind="primary"]) {
    background: rgba(99,102,241,0.1) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stButton"] > button:not([kind="primary"]):hover {
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(139,92,246,0.55) !important;
    color: #c4b5fd !important;
}

/* ════════════════════════════════════════════
   GENERAL TEXT INPUTS (non-sidebar)
════════════════════════════════════════════ */
[data-testid="stTextInput"] input {
    background: #0d0b22 !important;
    background-color: #0d0b22 !important;
    color: #e2e8f0 !important;
    border: 1.5px solid rgba(139,92,246,0.28) !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    caret-color: #a78bfa !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(139,92,246,0.65) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    background: #100e28 !important;
}
[data-testid="stTextInput"] input::placeholder { color: #334155 !important; }

/* ════════════════════════════════════════════
   RADIO BUTTONS — main content area
════════════════════════════════════════════ */
[data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stRadio"] label:hover { color: #a78bfa !important; }
[data-testid="stRadio"] [data-baseweb="radio"] div {
    border-color: rgba(139,92,246,0.5) !important;
    background: transparent !important;
}

/* ════════════════════════════════════════════
   DIVIDER LINE
════════════════════════════════════════════ */
hr {
    border-color: rgba(139,92,246,0.15) !important;
}

/* ════════════════════════════════════════════
   TOOLTIP
════════════════════════════════════════════ */
[data-testid="stTooltipIcon"] svg {
    color: #6366f1 !important;
    fill: #6366f1 !important;
}

/* ════════════════════════════════════════════
   ANALYSE BUTTON
════════════════════════════════════════════ */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #3730a3, #6d28d9, #9333ea, #db2777) !important;
    background-size: 300% 300% !important; color: white !important; border: none !important;
    border-radius: 18px !important; padding: 0.85rem 3rem !important;
    font-weight: 800 !important; font-size: 1.02rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 8px 35px rgba(99,102,241,0.55), 0 2px 8px rgba(0,0,0,0.4),
                inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
    letter-spacing: 0.025em !important; animation: gradientMove 5s ease infinite !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-5px) scale(1.03) !important;
    box-shadow: 0 16px 50px rgba(99,102,241,0.7), 0 4px 16px rgba(0,0,0,0.4),
                inset 0 1px 0 rgba(255,255,255,0.2) !important;
}

/* ════════════════════════════════════════════
   DOWNLOAD BUTTON
════════════════════════════════════════════ */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1e1b4b, #3730a3, #6d28d9) !important;
    color: white !important; border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 18px !important; padding: 0.78rem 2.6rem !important;
    font-weight: 800 !important; font-size: 0.95rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 6px 30px rgba(99,102,241,0.4) !important;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: 0 14px 44px rgba(99,102,241,0.6) !important;
    border-color: rgba(168,85,247,0.65) !important;
}

/* ════════════════════════════════════════════
   SIDEBAR — FULLY VISIBLE & STYLED
════════════════════════════════════════════ */
/* SIDEBAR — visible, rich dark purple background */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(ellipse 120% 35% at 50% 0%,  rgba(109,40,217,0.6)  0%, transparent 50%),
        radial-gradient(ellipse 90%  50% at 0%   80%, rgba(168,85,247,0.3)  0%, transparent 60%),
        radial-gradient(ellipse 70%  40% at 100% 50%, rgba(56,189,248,0.15) 0%, transparent 55%),
        linear-gradient(160deg, #0d0a1f 0%, #120e2e 40%, #0a0818 100%) !important;
    border-right: 1px solid rgba(139,92,246,0.35) !important;
    min-width: 280px !important;
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
    backdrop-filter: blur(30px) !important;
    padding: 0 !important;
}
/* Sidebar scrollbar */
[data-testid="stSidebar"] ::-webkit-scrollbar { width: 4px; }
[data-testid="stSidebar"] ::-webkit-scrollbar-track { background: transparent; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 2px; }

/* All text inside sidebar clearly visible */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #c8d4e3 !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid rgba(139,92,246,0.4) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.25s ease !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: rgba(168,85,247,0.8) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.18), 0 4px 20px rgba(0,0,0,0.3) !important;
    background: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: #4a5568 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 0.8rem !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: #c4b5fd !important;
    background: rgba(139,92,246,0.12) !important;
    border-color: rgba(139,92,246,0.25) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(139,92,246,0.2) !important;
    margin: 0.8rem 0 !important;
}
/* Sidebar section labels */
.sb-label {
    font-size: 0.68rem !important; font-weight: 800 !important;
    text-transform: uppercase !important; letter-spacing: 0.14em !important;
    background: linear-gradient(90deg, #a78bfa, #e879f9) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 8px !important; display: block !important;
}
.sb-section {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(139,92,246,0.18) !important;
    border-radius: 16px !important;
    padding: 1rem 1.1rem !important;
    margin-bottom: 0.9rem !important;
    transition: border-color 0.25s ease !important;
}
.sb-section:hover { border-color: rgba(139,92,246,0.38) !important; }
.sb-stat {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.8rem;
}
.sb-stat:last-child { border-bottom: none; }
.sb-stat-label { color: #64748b; font-weight: 600; }
.sb-stat-val {
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.sb-tip {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.07));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 12px; padding: 0.75rem 1rem;
    font-size: 0.78rem; color: #94a3b8; line-height: 1.6;
    margin-top: 0.6rem;
}
.sb-tip strong { color: #c4b5fd; }
.sb-format-chip {
    display: inline-flex; align-items: center; gap: 4px;
    background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(168,85,247,0.12));
    color: #c4b5fd; border: 1px solid rgba(139,92,246,0.35);
    border-radius: 100px; padding: 4px 12px;
    font-size: 0.72rem; font-weight: 700;
    transition: all 0.2s ease;
}
.sb-format-chip:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(168,85,247,0.2));
    border-color: rgba(168,85,247,0.6);
    transform: translateY(-2px);
}

/* ════════════════════════════════════════════
   RADIO — big white bullets, card style
════════════════════════════════════════════ */
/* Hide tiny default circle */
[data-testid="stRadio"] [data-baseweb="radio"] [role="radio"] {
    display: none !important;
}
/* Card-style option row */
[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px solid rgba(139,92,246,0.22) !important;
    border-radius: 13px !important;
    padding: 0.7rem 1rem !important;
    margin-bottom: 8px !important;
    color: #94a3b8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
[data-testid="stRadio"] label:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: rgba(139,92,246,0.55) !important;
    color: #e2e8f0 !important;
    transform: translateX(3px);
}
/* BIG WHITE BULLET */
[data-testid="stRadio"] label::before {
    content: "●";
    font-size: 1.1rem;
    color: rgba(255,255,255,0.6);
    flex-shrink: 0;
    line-height: 1;
    transition: all 0.2s ease;
}
[data-testid="stRadio"] label:hover::before {
    color: white;
    transform: scale(1.2);
}
/* Selected — purple bullet + glowing card */
[data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) label {
    background: linear-gradient(135deg,rgba(79,70,229,0.2),rgba(124,58,237,0.13)) !important;
    border-color: rgba(139,92,246,0.8) !important;
    color: #e2e8f0 !important;
    box-shadow: 0 3px 16px rgba(99,102,241,0.25) !important;
}
[data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) label::before {
    color: #a78bfa !important;
    font-size: 1.2rem;
}

/* ════════════════════════════════════════════
   SCROLLBAR
════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #6d28d9, #9333ea);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #7c3aed, #a855f7); }

/* ════════════════════════════════════════════
   FOOTER
════════════════════════════════════════════ */
.app-footer {
    background: linear-gradient(135deg, rgba(10,8,28,0.88), rgba(14,10,36,0.88));
    border: 1px solid rgba(139,92,246,0.16); border-radius: 20px;
    padding: 1.5rem 2rem; text-align: center; margin-top: 3.5rem;
    font-size: 0.82rem; color: #2d3f55; animation: fadeIn 0.6s ease;
    backdrop-filter: blur(14px); position: relative; overflow: hidden;
}
.app-footer::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.45), rgba(168,85,247,0.35), rgba(236,72,153,0.25), transparent);
}
.app-footer strong { color: #9333ea; }

/* old stAlert + expander replaced below */

/* ════════════════════════════════════════════
   SIDEBAR TOGGLE BUTTON
   — hidden on desktop (stays open)
   — VISIBLE on mobile (needed to open sidebar)
════════════════════════════════════════════ */

/* Desktop: hide the arrow (sidebar always open) */
@media screen and (min-width: 769px) {
    [data-testid="collapsedControl"]                { display: none !important; }
    [data-testid="stSidebarCollapseButton"]         { display: none !important; }
    [data-testid="stSidebarNavCollapseIcon"]        { display: none !important; }
    button[data-testid="baseButton-headerNoPadding"]{ display: none !important; }
    .st-emotion-cache-1rtdyuf, .st-emotion-cache-pkbazv { display: none !important; }
}

/* Mobile: SHOW the toggle button — styled nicely */
@media screen and (max-width: 768px) {
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999 !important;
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.5) !important;
        border: none !important;
    }
    [data-testid="collapsedControl"] svg {
        color: white !important;
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        border-radius: 10px !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.5) !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        color: white !important;
        fill: white !important;
    }
}

/* ════════════════════════════════════════════
   SIDEBAR — MINIMAL, NEVER SCROLLS SEPARATELY
════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
section[data-testid="stSidebar"] > div {
    height: auto !important;
    overflow-y: auto !important;
    padding-bottom: 1rem !important;
}
section[data-testid="stSidebar"] > div > div[data-testid="stVerticalBlock"] {
    padding: 0 0.6rem 1rem !important;
}
/* Sidebar button styles */
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.45rem 0.5rem !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(99,102,241,0.08) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(99,102,241,0.15) !important;
    color: #c4b5fd !important;
    border-color: rgba(139,92,246,0.4) !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(99,102,241,0.4) !important;
}
/* Sidebar text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] strong {
    color: #c4b5fd !important;
    font-size: 0.8rem !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { color: #c4b5fd !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(139,92,246,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.82rem !important;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #475569 !important;
    font-size: 0.65rem !important;
}

/* ════════════════════════════════════════════
   MOBILE & TABLET — FULLY RESPONSIVE
════════════════════════════════════════════ */

/* Tablet ≤ 1024px */
@media screen and (max-width: 1024px) {
    .block-container { max-width: 100% !important; padding-left: 1.2rem !important; padding-right: 1.2rem !important; }
    .feat-row { grid-template-columns: repeat(2,1fr) !important; gap: 10px !important; }
    .hero-title { font-size: 2.4rem !important; }
}

/* Mobile ≤ 768px */
@media screen and (max-width: 768px) {
    /* Block container — tighter padding */
    .block-container { padding: 0.8rem 0.7rem 3rem !important; max-width: 100% !important; }

    /* Hero */
    .hero { padding: 1.8rem 1.2rem 1.6rem !important; border-radius: 18px !important; margin-bottom: 1.4rem !important; }
    .hero-title { font-size: 1.75rem !important; line-height: 1.18 !important; letter-spacing: -0.01em !important; }
    .hero-sub { font-size: 0.85rem !important; margin-bottom: 1.2rem !important; }
    .hero-sub br { display: none !important; }
    .hero-eyebrow { font-size: 0.62rem !important; padding: 0.25rem 0.75rem !important; }
    .hero-author { font-size: 0.75rem !important; padding: 0.4rem 1rem !important; }
    .hero-corner-dots { top: 14px !important; right: 14px !important; }
    .hero-corner-dot { width: 9px !important; height: 9px !important; }

    /* Feature row */
    .feat-row { grid-template-columns: repeat(2,1fr) !important; gap: 8px !important; margin-bottom: 1.2rem !important; }
    .feat-card { padding: 0.85rem 0.6rem !important; border-radius: 12px !important; }
    .feat-icon { font-size: 1.25rem !important; margin-bottom: 0.3rem !important; }
    .feat-val { font-size: 0.78rem !important; }
    .feat-label { font-size: 0.62rem !important; }

    /* Stat cards */
    .stat-row { grid-template-columns: repeat(3,1fr) !important; gap: 8px !important; }
    .stat-card { padding: 1.1rem 0.6rem !important; border-radius: 14px !important; }
    .stat-num { font-size: 1.6rem !important; }
    .stat-lbl { font-size: 0.58rem !important; }

    /* Section headers */
    .sec-head { gap: 8px !important; margin: 1.6rem 0 0.9rem !important; }
    .sec-icon { width: 32px !important; height: 32px !important; font-size: 14px !important; border-radius: 9px !important; }
    .sec-title { font-size: 0.95rem !important; }

    /* Output cards */
    .out-card { padding: 1.2rem 1rem !important; font-size: 0.85rem !important; border-radius: 14px !important; line-height: 1.75 !important; }

    /* Progress */
    .prog-box { padding: 1.2rem 1rem !important; border-radius: 14px !important; }
    .prog-step { font-size: 0.8rem !important; gap: 9px !important; padding: 0.5rem 0 !important; }
    .prog-dot { width: 24px !important; height: 24px !important; font-size: 11px !important; }
    .prog-label { font-size: 0.62rem !important; margin-bottom: 0.8rem !important; }

    /* Chips */
    .chips { gap: 6px !important; }
    .chip { font-size: 0.7rem !important; padding: 0.22rem 0.65rem !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { padding: 4px !important; gap: 3px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.72rem !important; padding: 0.4rem 0.7rem !important; }

    /* Buttons — full width */
    div[data-testid="stButton"] > button[kind="primary"] {
        width: 100% !important; padding: 0.75rem 1rem !important; font-size: 0.92rem !important;
    }
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important; font-size: 0.88rem !important;
    }

    /* Textarea */
    .stTextArea textarea { font-size: 0.88rem !important; }

    /* Divider */
    .div { margin: 1.4rem 0 !important; }

    /* Knowledge grid — stack */
    [data-testid="column"] { min-width: 100% !important; }

    /* Success box */
    .success-box { padding: 0.9rem 1rem !important; font-size: 0.82rem !important; border-radius: 12px !important; }

    /* Footer */
    .app-footer { padding: 1rem 1.2rem !important; font-size: 0.75rem !important; border-radius: 14px !important; }
}

/* Small phones ≤ 480px */
@media screen and (max-width: 480px) {
    .block-container { padding: 0.6rem 0.5rem 2.5rem !important; }
    .hero { padding: 1.5rem 1rem 1.3rem !important; }
    .hero-title { font-size: 1.45rem !important; }
    .hero-sub { font-size: 0.82rem !important; }
    .feat-row { gap: 6px !important; }
    .stat-row { grid-template-columns: repeat(3,1fr) !important; gap: 6px !important; }
    .stat-num { font-size: 1.35rem !important; }
    .out-card { padding: 1rem 0.85rem !important; font-size: 0.82rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.65rem !important; padding: 0.35rem 0.5rem !important; }
    .sec-title { font-size: 0.88rem !important; }
    .prog-step { font-size: 0.75rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── New feature CSS (copy buttons, flashcards, theme selector, lang badge) ────
st.markdown("""<style>
/* COPY BUTTON */
.out-card { position: relative !important; }
.copy-btn {
    position: absolute; top: 10px; right: 10px;
    background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.32);
    color: #a5b4fc; border-radius: 8px; padding: 3px 10px;
    font-size: 0.68rem; font-weight: 700; cursor: pointer;
    transition: all 0.2s ease; z-index: 10;
    font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: 0.04em;
}
.copy-btn:hover { background: rgba(99,102,241,0.3); color: #c4b5fd; transform: translateY(-1px); }

/* FLASHCARD GRID */
.fc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; margin-top: 1rem; }
.fc-item {
    background: linear-gradient(145deg, rgba(10,8,28,0.94), rgba(14,10,36,0.94));
    border: 1px solid rgba(139,92,246,0.22); border-radius: 18px; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
    animation: fadeInUp 0.5s ease both;
}
.fc-item:hover { border-color: rgba(139,92,246,0.55); transform: translateY(-5px) scale(1.02); box-shadow: 0 16px 40px rgba(99,102,241,0.22); }
.fc-q { padding: 1rem 1.2rem 0.9rem; font-size: 0.86rem; font-weight: 700; color: #e2e8f0; line-height: 1.55; border-bottom: 1px solid rgba(139,92,246,0.15); }
.fc-q-lbl { font-size: 0.58rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: #a78bfa; margin-bottom: 5px; display: block; }
.fc-a { padding: 0.85rem 1.2rem 1rem; font-size: 0.82rem; color: #94a3b8; line-height: 1.65; }
.fc-a-lbl { font-size: 0.58rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: #34d399; margin-bottom: 5px; display: block; }

/* THEME SELECTOR */
.theme-row { display: flex; gap: 7px; flex-wrap: nowrap; margin-bottom: 0.8rem; }
.theme-pill { flex: 1; background: rgba(255,255,255,0.03); border: 1.5px solid rgba(139,92,246,0.18); border-radius: 12px; padding: 0.55rem 0.2rem; text-align: center; cursor: pointer; font-size: 1.1rem; transition: all 0.22s ease; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.theme-pill span { font-size: 0.5rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
.theme-pill:hover { border-color: rgba(139,92,246,0.5); background: rgba(139,92,246,0.1); transform: translateY(-2px); }
.theme-pill.active { border-color: rgba(139,92,246,0.75); background: rgba(139,92,246,0.2); box-shadow: 0 4px 16px rgba(99,102,241,0.3); }
.theme-pill.active span { color: #c4b5fd; }

/* LANG BADGE */
.lang-pill { display: inline-flex; align-items: center; gap: 5px; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.28); border-radius: 100px; padding: 0.2rem 0.75rem; font-size: 0.7rem; font-weight: 700; color: #a5b4fc; }

/* DL ROW */
.dl-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 0.5rem; }
.dl-row > div[data-testid="stDownloadButton"] { flex: 1; min-width: 170px; }

@media screen and (max-width: 600px) {
    .fc-grid { grid-template-columns: 1fr !important; }
    .theme-row { gap: 4px; }
    .fc-item { border-radius: 14px; }
}
</style>""", unsafe_allow_html=True)

# ── Canvas Particle System + Background Enforcer ──────────────────────────────
st.markdown("""
<canvas id="cosmic-canvas" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;"></canvas>
<script>
// ── BACKGROUND ENFORCER — theme-aware ─────────────────────────────────────────
(function enforceBackground() {
    const DARK = '#02030d';
    const selectors = [
        'body','#root','.stApp',
        '[data-testid="stAppViewContainer"]',
        '[data-testid="stMain"]',
        '[data-testid="stMainBlockContainer"]',
        '[data-testid="stAppViewBlockContainer"]',
        '[data-testid="stBottom"]',
        'section.main','.main'
    ];
    function applyBg() {
        document.body.style.setProperty('background', DARK, 'important');
        document.body.style.setProperty('background-color', DARK, 'important');
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                el.style.setProperty('background', 'transparent', 'important');
                el.style.setProperty('background-color', 'transparent', 'important');
            });
        });
    }
    applyBg();
    new MutationObserver(applyBg).observe(document.documentElement, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['style','class']
    });
    let t = 0; const iv = setInterval(() => { applyBg(); if(++t > 16) clearInterval(iv); }, 300);
})();
</script>
<script>
(function() {
    const canvas = document.getElementById('cosmic-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W = window.innerWidth, H = window.innerHeight;
    canvas.width = W; canvas.height = H;
    window.addEventListener('resize', () => {
        W = window.innerWidth; H = window.innerHeight;
        canvas.width = W; canvas.height = H;
    });

    // Particles
    const PARTICLES = 110;
    const particles = Array.from({length: PARTICLES}, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.6 + 0.3,
        vx: (Math.random() - 0.5) * 0.18,
        vy: (Math.random() - 0.5) * 0.18,
        alpha: Math.random() * 0.6 + 0.1,
        color: ['#818cf8','#a78bfa','#c084fc','#e879f9','#67e8f9','#34d399'][Math.floor(Math.random()*6)],
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinkleDir: Math.random() > 0.5 ? 1 : -1,
    }));

    // Shooting stars
    const shootingStars = [];
    function spawnShootingStar() {
        shootingStars.push({
            x: Math.random() * W * 0.7,
            y: Math.random() * H * 0.4,
            len: Math.random() * 120 + 60,
            speed: Math.random() * 6 + 4,
            angle: Math.PI / 4 + (Math.random() - 0.5) * 0.3,
            alpha: 1,
            life: 0,
            maxLife: Math.random() * 40 + 25,
        });
    }
    setInterval(spawnShootingStar, 2800);

    function draw() {
        ctx.clearRect(0, 0, W, H);

        // Particles
        particles.forEach(p => {
            p.x += p.vx; p.y += p.vy;
            p.alpha += p.twinkleSpeed * p.twinkleDir;
            if (p.alpha >= 0.75 || p.alpha <= 0.05) p.twinkleDir *= -1;
            if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
            if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.alpha;
            ctx.fill();

            // Glow for larger particles
            if (p.r > 1.2) {
                const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 5);
                g.addColorStop(0, p.color + '55');
                g.addColorStop(1, 'transparent');
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r * 5, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.globalAlpha = p.alpha * 0.35;
                ctx.fill();
            }
        });

        // Shooting stars
        for (let i = shootingStars.length - 1; i >= 0; i--) {
            const s = shootingStars[i];
            s.x += Math.cos(s.angle) * s.speed;
            s.y += Math.sin(s.angle) * s.speed;
            s.life++;
            s.alpha = Math.max(0, 1 - s.life / s.maxLife);
            if (s.life >= s.maxLife) { shootingStars.splice(i, 1); continue; }

            const tailX = s.x - Math.cos(s.angle) * s.len;
            const tailY = s.y - Math.sin(s.angle) * s.len;
            const grad = ctx.createLinearGradient(tailX, tailY, s.x, s.y);
            grad.addColorStop(0, 'transparent');
            grad.addColorStop(1, 'rgba(255,255,255,' + s.alpha + ')');
            ctx.beginPath();
            ctx.moveTo(tailX, tailY);
            ctx.lineTo(s.x, s.y);
            ctx.strokeStyle = grad;
            ctx.lineWidth = 1.5;
            ctx.globalAlpha = s.alpha;
            ctx.stroke();
        }

        ctx.globalAlpha = 1;
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
<script>
/* ── COPY BUTTON INJECTOR ── */
(function() {
    const done = new WeakSet();
    function inject() {
        document.querySelectorAll('.out-card').forEach(function(card) {
            if (done.has(card)) return;
            done.add(card);
            var btn = document.createElement('button');
            btn.className = 'copy-btn';
            btn.textContent = '📋 Copy';
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                var txt = card.innerText.replace(/^📋 Copy$/mg,'').replace(/^✓ Copied!$/mg,'').trim();
                navigator.clipboard.writeText(txt).then(function() {
                    btn.textContent = '✓ Copied!';
                    btn.classList.add('copied');
                    setTimeout(function(){ btn.textContent = '📋 Copy'; btn.classList.remove('copied'); }, 2200);
                }).catch(function(){
                    btn.textContent = '✓'; setTimeout(function(){ btn.textContent = '📋 Copy'; }, 1500);
                });
            });
            card.appendChild(btn);
        });
    }
    new MutationObserver(inject).observe(document.body, {childList:true, subtree:true});
    setInterval(inject, 800);
})();
</script>
""", unsafe_allow_html=True)


# ── Groq client ───────────────────────────────────────────────────────────────
def get_groq_client(visitor_key):
    """Try visitor key first, then app owner key, then env var."""
    if visitor_key.strip():
        return Groq(api_key=visitor_key.strip())
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key: return Groq(api_key=key)
    except (KeyError, FileNotFoundError):
        pass
    key = os.environ.get("GROQ_API_KEY", "")
    if key: return Groq(api_key=key)
    return None


# ── Language-aware AI wrappers ────────────────────────────────────────────────
def _groq_call(client, system, user, max_tokens=700):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant", max_tokens=max_tokens,
        messages=[{"role":"system","content":system},{"role":"user","content":user}]
    )
    return r.choices[0].message.content

def _urdu_sys(task):
    return (
        f"آپ ایک ماہر {task} ہیں۔ "
        "آپ کو لازمی طور پر اپنا پورا جواب صرف اردو زبان میں لکھنا ہے۔ "
        "ایک بھی انگریزی لفظ استعمال نہ کریں۔ "
        "مکمل طور پر اردو رسم الخط میں لکھیں۔"
    )


def get_quick_summary(client, text, language):
    if language == "English": return generate_quick_summary(client, text)
    return _groq_call(client, _urdu_sys("خلاصہ نویس"),
        f"ان نوٹس کا 3-5 جملوں میں خلاصہ صرف اردو میں لکھیں:\n\n{text[:4000]}", 450)

def get_detailed_summary(client, text, language):
    if language == "English": return generate_detailed_summary(client, text)
    return _groq_call(client, _urdu_sys("خلاصہ نویس"),
        f"ان نوٹس کا تفصیلی خلاصہ صرف اردو میں لکھیں، تمام موضوعات شامل کریں:\n\n{text[:4000]}", 900)

def get_key_points(client, text, language):
    if language == "English": return generate_key_points(client, text)
    return _groq_call(client, _urdu_sys("استاد"),
        f"ان نوٹس کے 8 اہم نکات صرف اردو میں لکھیں، ہر نکتہ • سے شروع ہو:\n\n{text[:4000]}", 550)

def get_knowledge(client, text, language):
    if language == "English": return run_full_extraction(client, text)
    t = text[:3000]
    concepts    = _groq_call(client, _urdu_sys("ماہر"),
        f"5-6 اہم تصورات صرف اردو میں بیان کریں:\n{t}", 450)
    time.sleep(3)
    definitions = _groq_call(client, _urdu_sys("ماہر"),
        f"اہم اصطلاحات کی تعریف صرف اردو میں لکھیں:\n{t}", 450)
    time.sleep(3)
    key_terms   = _groq_call(client, _urdu_sys("ماہر"),
        f"10 اہم اصطلاحات کامہ سے الگ صرف اردو میں لکھیں:\n{t}", 180)
    time.sleep(3)
    facts       = _groq_call(client, _urdu_sys("ماہر"),
        f"5-6 اہم حقائق صرف اردو میں بیان کریں:\n{t}", 400)
    return {"concepts":concepts,"definitions":definitions,"key_terms":key_terms,"important_facts":facts}

def get_questions(client, text, language):
    if language == "English": return generate_all_questions(client, text)
    t = text[:3000]
    conceptual   = _groq_call(client, _urdu_sys("استاد"),
        f"5 تصوراتی سوالات صرف اردو میں لکھیں:\n{t}", 450)
    time.sleep(3)
    mcq          = _groq_call(client, _urdu_sys("استاد"),
        f"4 آپشنز کے ساتھ 5 MCQ سوالات صرف اردو میں لکھیں:\n{t}", 600)
    time.sleep(3)
    short_answer = _groq_call(client, _urdu_sys("استاد"),
        f"3 مختصر جوابی سوالات صرف اردو میں لکھیں:\n{t}", 350)
    return {"conceptual":conceptual,"mcq":mcq,"short_answer":short_answer}


# ── PDF generator ─────────────────────────────────────────────────────────────
def create_pdf(word_count, char_count, read_time, quick, key_points_txt,
               knowledge, questions, keywords, timestamp):
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()
        pdf.set_margins(18, 18, 18)

        def safe(t):
            return t.encode("latin-1", "replace").decode("latin-1") if t else ""

        def heading(txt, size=13, color=(167,139,250)):
            pdf.set_font("Helvetica","B", size)
            pdf.set_text_color(*color)
            pdf.cell(0, 8, safe(txt), ln=True)
            pdf.set_text_color(180, 180, 200)

        def body(txt, size=9):
            pdf.set_font("Helvetica","", size)
            pdf.set_text_color(200, 210, 230)
            pdf.multi_cell(0, 5.5, safe(txt))
            pdf.ln(2)

        def divider():
            pdf.set_draw_color(80, 60, 130)
            pdf.line(18, pdf.get_y(), 192, pdf.get_y())
            pdf.ln(4)

        # Header
        pdf.set_fill_color(10, 8, 28)
        pdf.rect(0, 0, 210, 297, "F")
        pdf.set_font("Helvetica","B", 20)
        pdf.set_text_color(196, 181, 253)
        pdf.cell(0, 14, "AI Notes Summarizer", ln=True, align="C")
        pdf.set_font("Helvetica","", 9)
        pdf.set_text_color(100, 100, 140)
        pdf.cell(0, 6, f"Generated by Zainab Gondal  |  {timestamp}", ln=True, align="C")
        pdf.ln(4)
        divider()

        # Stats
        heading("Document Statistics", 11, (139, 92, 246))
        body(f"Words: {word_count:,}   |   Characters: {char_count:,}   |   Read Time: {read_time}")
        divider()

        # Quick Summary
        heading("Quick Summary")
        body(quick)
        divider()

        # Key Points
        heading("Key Points")
        body(key_points_txt)
        divider()

        # Concepts
        heading("Important Concepts")
        body(knowledge.get("concepts",""))
        divider()

        # Definitions
        heading("Definitions")
        body(knowledge.get("definitions",""))
        divider()

        # Questions
        heading("Conceptual Questions")
        body(questions.get("conceptual",""))
        divider()

        # Keywords
        heading("NLP Keywords")
        body(", ".join(keywords))

        # Footer
        pdf.set_y(-18)
        pdf.set_font("Helvetica","", 8)
        pdf.set_text_color(80, 60, 120)
        pdf.cell(0, 6, "AI Notes Summarizer  |  Created by Zainab Gondal  |  Powered by Groq + Llama3", align="C")

        return bytes(pdf.output())
    except Exception as e:
        return None


# ── Sidebar — ONLY controls, no scroll needed ───────────────────────────────
with st.sidebar:

    # Logo
    st.markdown("""
    <div style="text-align:center;padding:1.4rem 0.5rem 0.9rem;
                border-bottom:1px solid rgba(139,92,246,0.2);margin-bottom:0.9rem;">
        <div style="width:58px;height:58px;
                    background:linear-gradient(135deg,#3730a3,#7c3aed,#a855f7,#ec4899);
                    border-radius:18px;display:flex;align-items:center;justify-content:center;
                    margin:0 auto 0.7rem;font-size:28px;
                    box-shadow:0 6px 24px rgba(139,92,246,0.6);">🧠</div>
        <div style="font-size:1rem;font-weight:800;
                    background:linear-gradient(135deg,#e2e8f0,#c4b5fd);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;margin-bottom:0.25rem;">AI Notes Summarizer</div>
        <div style="font-size:0.65rem;color:#6366f1;font-weight:700;">
            ✨ by Zainab Gondal · v3.0 · Free
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── INPUT METHOD — first and most important ───────────────────────────────
    st.markdown("""
    <div style="font-size:0.62rem;font-weight:800;text-transform:uppercase;
                letter-spacing:0.1em;color:#a78bfa;margin-bottom:7px;">
        📥 Choose How to Add Notes
    </div>
    """, unsafe_allow_html=True)
    input_mode = st.radio("Input", ["📋 Paste Text", "📁 Upload File"],
                          label_visibility="collapsed")

    st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)

    # ── API KEY ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.62rem;font-weight:800;text-transform:uppercase;
                letter-spacing:0.1em;color:#a78bfa;margin-bottom:5px;">
        🔑 API Key <span style="color:#475569;font-weight:500;text-transform:none;letter-spacing:0;">(optional)</span>
    </div>
    """, unsafe_allow_html=True)
    visitor_key = st.text_input("API Key", type="password",
                                placeholder="gsk_...  (leave empty = free)",
                                label_visibility="collapsed",
                                help="Free key at console.groq.com")
    st.markdown('<div style="font-size:0.62rem;color:#475569;margin-top:2px;">Leave empty — app works 100% free ✅</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)

    # ── WHAT YOU GET ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(168,85,247,0.06));
                border:1px solid rgba(139,92,246,0.22);border-radius:14px;
                padding:0.85rem 1rem;margin-bottom:0.6rem;">
        <div style="font-size:0.6rem;font-weight:800;text-transform:uppercase;
                    letter-spacing:0.1em;color:#a78bfa;margin-bottom:0.55rem;">
            ⚡ What You Get
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;">
            <div style="display:flex;align-items:center;gap:8px;font-size:0.73rem;color:#c4b5fd;">
                <span style="font-size:0.9rem;">📝</span> 3 types of summaries
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.73rem;color:#c4b5fd;">
                <span style="font-size:0.9rem;">🔬</span> Knowledge extraction
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.73rem;color:#c4b5fd;">
                <span style="font-size:0.9rem;">❓</span> 13 study questions
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.73rem;color:#c4b5fd;">
                <span style="font-size:0.9rem;">🃏</span> 8 flashcards
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.73rem;color:#c4b5fd;">
                <span style="font-size:0.9rem;">📄</span> PDF + TXT download
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PRO TIP ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.22);
                border-radius:14px;padding:0.75rem 1rem;margin-bottom:0.8rem;">
        <div style="font-size:0.6rem;font-weight:800;text-transform:uppercase;
                    letter-spacing:0.1em;color:#34d399;margin-bottom:0.3rem;">💡 Pro Tip</div>
        <div style="font-size:0.7rem;color:#6ee7b7;line-height:1.5;">
            Best with 200–2000 words. Get your full study pack in under 60 sec!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── LINKS ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(139,92,246,0.15);padding-top:0.7rem;text-align:center;">
        <div style="font-size:0.63rem;color:#475569;margin-bottom:0.55rem;">
            Crafted with 💜 by <strong style="color:#a78bfa;">Zainab Gondal</strong>
        </div>
        <a href="https://www.linkedin.com/in/zainabgondal/" target="_blank"
           style="display:block;text-decoration:none;
                  background:rgba(10,102,194,0.15);border:1px solid rgba(10,102,194,0.35);
                  color:#93c5fd;padding:6px;border-radius:9px;
                  font-size:0.7rem;font-weight:700;margin-bottom:5px;text-align:center;">
            💼 LinkedIn
        </a>
        <a href="https://github.com/zainabgondal" target="_blank"
           style="display:block;text-decoration:none;
                  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                  color:#e2e8f0;padding:6px;border-radius:9px;
                  font-size:0.7rem;font-weight:700;text-align:center;">
            🐙 GitHub
        </a>
    </div>
    """, unsafe_allow_html=True)


# ── Mobile hint — only shows on small screens ────────────────────────────────
st.markdown("""
<style>
.mobile-hint {
    display: none;
    background: linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1));
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
    color: #c4b5fd;
    font-weight: 600;
    margin-bottom: 0.8rem;
    align-items: center;
    gap: 8px;
}
@media screen and (max-width: 768px) {
    .mobile-hint { display: flex !important; }
}
</style>
<div class="mobile-hint">
    ☰ &nbsp;Tap the <strong style="color:#a78bfa;">purple button</strong> (top-left) to open settings &amp; input options
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
    <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
        <div class="hero-author">✨ Created by Zainab Gondal</div>
        <a href="https://www.linkedin.com/in/zainabgondal/" target="_blank"
           style="display:inline-flex;align-items:center;gap:7px;
                  background:rgba(10,102,194,0.25);border:1px solid rgba(10,102,194,0.5);
                  color:white;text-decoration:none;padding:0.45rem 1.2rem;border-radius:100px;
                  font-size:0.8rem;font-weight:700;backdrop-filter:blur(8px);">
            💼 Connect on LinkedIn
        </a>
    </div>
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
        st.warning("⚠️ Please paste some text or upload a file first.")
        st.stop()

    client = get_groq_client(visitor_key)
    if client is None:
        st.error("🔑 Groq API key not found. Get your free key at console.groq.com and paste it in the sidebar.")
        st.stop()

    language   = "English"
    clean      = clean_text(raw_text)
    word_count = count_words(clean)
    read_time  = estimate_read_time(clean)
    char_count = len(clean)

    # ── Progress tracker ──────────────────────────────────────────────────────
    prog = st.empty()

    def show_step(n, total=7):
        labels = [
            "Analysing document",
            "Generating summaries",
            "Extracting knowledge",
            "Building study questions",
            "Extracting keywords",
            "Generating flashcards",
            "Preparing downloads",
        ]
        pct = int((n - 1) / total * 100)
        rows = ""
        for i, label in enumerate(labels, 1):
            if i < n:    cls, dot, txt = "done",  "✓", f"{label} — done"
            elif i == n: cls, dot, txt = "active", "●", f"{label}..."
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

    # ── Language badge ────────────────────────────────────────────────────────
    lang_short = language.split(" ")[0]
    if language != "English":
        st.markdown(
            f'<div style="margin-bottom:0.8rem;">'
            f'<span class="lang-pill">🌐 Output Language: <strong>{lang_short}</strong></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Stats ─────────────────────────────────────────────────────────────────
    show_step(1)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">📊</div><div class="sec-title">Document Statistics</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-card"><div class="stat-num">{word_count:,}</div><div class="stat-lbl">Words</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-num">{char_count:,}</div><div class="stat-lbl">Characters</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-num">{read_time}</div><div class="stat-lbl">Read Time</div></div>', unsafe_allow_html=True)

    # ── Summaries ─────────────────────────────────────────────────────────────
    show_step(2)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">📝</div><div class="sec-title">Summaries</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⚡ Quick Summary", "📖 Detailed Summary", "🎯 Key Points"])
    with tab1:
        with st.spinner("Generating quick summary..."):
            quick = get_quick_summary(client, clean, language)
        st.markdown(f'<div class="out-card purple">{quick}</div>', unsafe_allow_html=True)
    with tab2:
        with st.spinner("Writing detailed summary..."):
            time.sleep(4)
            detailed = get_detailed_summary(client, clean, language)
        st.markdown(f'<div class="out-card green">{detailed}</div>', unsafe_allow_html=True)
    with tab3:
        with st.spinner("Extracting key points..."):
            time.sleep(4)
            key_points = get_key_points(client, clean, language)
        st.markdown(f'<div class="out-card amber">{key_points}</div>', unsafe_allow_html=True)

    # ── Knowledge Extraction ──────────────────────────────────────────────────
    show_step(3)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">🔬</div><div class="sec-title">Knowledge Extraction</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    with st.spinner("Extracting knowledge — takes ~15 seconds..."):
        time.sleep(5)
        knowledge = get_knowledge(client, clean, language)

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

    # ── Study Questions ───────────────────────────────────────────────────────
    show_step(4)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">❓</div><div class="sec-title">Study Questions</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    with st.spinner("Building study questions..."):
        time.sleep(5)
        questions = get_questions(client, clean, language)

    qt1, qt2, qt3 = st.tabs(["💭 Conceptual (5)", "🔢 Multiple Choice (5)", "✏️ Short Answer (3)"])
    with qt1:
        st.markdown(f'<div class="out-card purple">{questions["conceptual"]}</div>', unsafe_allow_html=True)
    with qt2:
        st.markdown(f'<div class="out-card green">{questions["mcq"]}</div>', unsafe_allow_html=True)
    with qt3:
        st.markdown(f'<div class="out-card rose">{questions["short_answer"]}</div>', unsafe_allow_html=True)

    # ── NLP Keywords ──────────────────────────────────────────────────────────
    show_step(5)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">🏷️</div><div class="sec-title">NLP Keyword Extraction</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    st.caption("Extracted using NLTK frequency analysis · stop-words removed")
    keywords = extract_keywords(clean, top_n=25)
    if keywords:
        kchips = "".join(f'<span class="chip">{kw}</span>' for kw in keywords)
        st.markdown(f'<div class="chips">{kchips}</div>', unsafe_allow_html=True)

    # ── Flashcards ────────────────────────────────────────────────────────────
    show_step(6)
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">🃏</div><div class="sec-title">Flashcards</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    st.caption("Tap a card to study · Auto-generated from your notes")
    with st.spinner("Generating flashcards..."):
        time.sleep(4)
        flashcards = generate_flashcards(client, clean, language)

    cards_html = '<div class="fc-grid">'
    for fc in flashcards:
        cards_html += (
            '<div class="fc-item">'
            f'<div class="fc-q"><span class="fc-q-lbl">❓ Question</span>{fc["q"]}</div>'
            f'<div class="fc-a"><span class="fc-a-lbl">✅ Answer</span>{fc["a"]}</div>'
            '</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Done! ─────────────────────────────────────────────────────────────────
    show_step(7)
    prog.markdown(
        '<div class="success-box">✅ All done! Summaries, flashcards, questions &amp; keywords generated successfully.</div>',
        unsafe_allow_html=True,
    )

    # ── Downloads ─────────────────────────────────────────────────────────────
    st.markdown("""<div class="sec-head" style="margin-top:2rem;">
        <div class="sec-icon">⬇️</div><div class="sec-title">Download Your Summary</div>
        <div class="sec-line"></div></div>""", unsafe_allow_html=True)
    st.caption("Download your full study pack — TXT works everywhere, PDF looks great!")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ts_file   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    download_content = f"""AI NOTES SUMMARIZER & KNOWLEDGE EXTRACTION SYSTEM
Created by Zainab Gondal  |  Language: {language}
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
FLASHCARDS
{'='*70}
""" + "\n".join([f"Q: {fc['q']}\nA: {fc['a']}\n" for fc in flashcards]) + f"""
{'='*70}
NLP KEYWORDS
{'-'*40}
{', '.join(keywords)}

{'='*70}
AI Notes Summarizer  |  Zainab Gondal  |  Powered by Groq + Llama3
"""

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label="📄 Download as TXT",
            data=download_content.encode("utf-8"),
            file_name=f"notes_summary_{ts_file}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl2:
        pdf_bytes = create_pdf(
            word_count, char_count, read_time, quick, key_points,
            knowledge, questions, keywords, timestamp,
        )
        if pdf_bytes:
            st.download_button(
                label="📑 Download as PDF",
                data=pdf_bytes,
                file_name=f"notes_summary_{ts_file}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.info("💡 Install fpdf2 for PDF export: `pip install fpdf2`")

# ── Contact & Feedback — bottom of page ──────────────────────────────────────
st.markdown("""<div class="sec-head" style="margin-top:2.5rem;">
    <div class="sec-icon">📬</div><div class="sec-title">Contact & Feedback</div>
    <div class="sec-line"></div></div>""", unsafe_allow_html=True)

bot1, bot2 = st.columns([1, 1])

with bot1:
    st.markdown("""
    <div style="background:linear-gradient(145deg,rgba(10,8,28,0.94),rgba(14,10,36,0.94));
                border:1px solid rgba(139,92,246,0.22);border-radius:18px;padding:1.3rem 1.5rem;
                box-shadow:0 4px 24px rgba(0,0,0,0.4);">
        <div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;
                    background:linear-gradient(90deg,#a78bfa,#e879f9);-webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.8rem;">
            📬 Contact the Developer
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <a href="mailto:gondalzainab34@gmail.com"
               style="display:flex;align-items:center;gap:10px;text-decoration:none;
                      background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);
                      border-radius:12px;padding:0.55rem 0.9rem;transition:all 0.2s;">
                <span style="font-size:1.1rem;">📧</span>
                <span style="font-size:0.76rem;font-weight:600;color:#c4b5fd;">gondalzainab34@gmail.com</span>
            </a>
            <a href="https://wa.me/92113430370" target="_blank"
               style="display:flex;align-items:center;gap:10px;text-decoration:none;
                      background:rgba(37,211,102,0.1);border:1px solid rgba(37,211,102,0.25);
                      border-radius:12px;padding:0.55rem 0.9rem;">
                <span style="font-size:1.1rem;">💬</span>
                <span style="font-size:0.76rem;font-weight:600;color:#6ee7b7;">WhatsApp: +92 113 430 370</span>
            </a>
            <a href="https://www.linkedin.com/in/zainabgondal/" target="_blank"
               style="display:flex;align-items:center;gap:10px;text-decoration:none;
                      background:rgba(10,102,194,0.12);border:1px solid rgba(10,102,194,0.3);
                      border-radius:12px;padding:0.55rem 0.9rem;">
                <span style="font-size:1.1rem;">💼</span>
                <span style="font-size:0.76rem;font-weight:600;color:#93c5fd;">linkedin.com/in/zainabgondal</span>
            </a>
            <a href="https://github.com/zainabgondal" target="_blank"
               style="display:flex;align-items:center;gap:10px;text-decoration:none;
                      background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);
                      border-radius:12px;padding:0.55rem 0.9rem;">
                <span style="font-size:1.1rem;">🐙</span>
                <span style="font-size:0.76rem;font-weight:600;color:#e2e8f0;">github.com/zainabgondal</span>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

with bot2:
    st.markdown("""
    <div style="background:linear-gradient(145deg,rgba(10,8,28,0.94),rgba(14,10,36,0.94));
                border:1px solid rgba(139,92,246,0.22);border-radius:18px;padding:1.3rem 1.5rem;
                box-shadow:0 4px 24px rgba(0,0,0,0.4);margin-bottom:0.6rem;">
        <div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;
                    background:linear-gradient(90deg,#a78bfa,#e879f9);-webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.4rem;">
            💬 Feedback & Suggestions
        </div>
        <div style="font-size:0.75rem;color:#64748b;line-height:1.6;">
            Loved the app? Found a bug? Want a new feature?<br>
            <strong style="color:#a78bfa;">I read every single message!</strong> 🙏
        </div>
    </div>
    """, unsafe_allow_html=True)
    suggestion = st.text_area(
        "feedback",
        placeholder="Write your review, suggestion or idea here... 💭\n\nExamples:\n• 'Love the flashcards feature!'\n• 'Can you add dark mode for cards?'\n• 'Please add more languages'",
        height=140,
        label_visibility="collapsed",
        key="suggestion_input",
    )
    if st.button("📨 Send Feedback", use_container_width=True, type="primary"):
        if suggestion.strip():
            st.success("✅ Thank you so much! Your feedback means everything 💜")
        else:
            st.warning("Please write something before sending!")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    🧠 AI Notes Summarizer &amp; Knowledge Extraction System &nbsp;·&nbsp;
    Created by <strong>Zainab Gondal</strong> &nbsp;·&nbsp;
    Powered by Groq + Llama3 &nbsp;·&nbsp; 100% Free &nbsp;·&nbsp;
    <a href="https://www.linkedin.com/in/zainabgondal/" target="_blank"
       style="color:#a78bfa;text-decoration:none;font-weight:700;">💼 LinkedIn</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/zainabgondal" target="_blank"
       style="color:#a78bfa;text-decoration:none;font-weight:700;">🐙 GitHub</a>
</div>
""", unsafe_allow_html=True)
