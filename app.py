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

# ── Cosmic UI CSS + JS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* ════════════════════════════════════════════
   FORCE DARK BACKGROUND — ALL STREAMLIT LAYERS
════════════════════════════════════════════ */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
.main,
[class*="css"] {
    background: transparent !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #e2e8f0 !important;
}

/* THE REAL BACKGROUND — painted on stApp */
.stApp {
    background:
        radial-gradient(ellipse 90% 55% at 0% 0%,   rgba(88,28,220,0.35)  0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 100% 0%,  rgba(14,165,233,0.22) 0%, transparent 50%),
        radial-gradient(ellipse 60% 55% at 100% 100%,rgba(236,72,153,0.2)  0%, transparent 55%),
        radial-gradient(ellipse 80% 50% at 0%   100%,rgba(99,102,241,0.18) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50%  50%, rgba(139,92,246,0.1)  0%, transparent 60%),
        linear-gradient(145deg, #02030d 0%, #06071a 30%, #0a0520 60%, #050210 100%) !important;
    background-attachment: fixed !important;
    min-height: 100vh !important;
}

/* Animated floating orbs layer */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(circle 280px at 15% 25%,  rgba(99,102,241,0.12)  0%, transparent 70%),
        radial-gradient(circle 380px at 85% 20%,  rgba(139,92,246,0.09)  0%, transparent 70%),
        radial-gradient(circle 240px at 70% 75%,  rgba(236,72,153,0.1)   0%, transparent 70%),
        radial-gradient(circle 320px at 25% 80%,  rgba(56,189,248,0.07)  0%, transparent 70%);
    animation: orbDrift 18s ease-in-out infinite alternate;
}
@keyframes orbDrift {
    0%   { transform: translate(0px, 0px) scale(1); }
    33%  { transform: translate(30px, -20px) scale(1.05); }
    66%  { transform: translate(-20px, 30px) scale(0.97); }
    100% { transform: translate(15px, -10px) scale(1.02); }
}

/* NOISE TEXTURE OVERLAY */
.stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: 0.025;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 200px 200px;
}

[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
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
    background: rgba(255,255,255,0.022) !important;
    border: 1.5px solid rgba(139,92,246,0.2) !important; border-radius: 18px !important;
    color: #d8e0ec !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important; resize: none !important;
    transition: all 0.3s ease !important; backdrop-filter: blur(10px) !important; line-height: 1.75 !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.2) !important;
}
.stTextArea textarea:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.1), 0 10px 40px rgba(0,0,0,0.35), inset 0 2px 8px rgba(0,0,0,0.2) !important;
    background: rgba(255,255,255,0.032) !important;
}
.stTextArea textarea::placeholder { color: #1e293b !important; }

/* ════════════════════════════════════════════
   FILE UPLOADER
════════════════════════════════════════════ */
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, rgba(99,102,241,0.04), rgba(168,85,247,0.03)) !important;
    border: 2px dashed rgba(99,102,241,0.26) !important; border-radius: 20px !important;
    transition: all 0.3s ease !important; backdrop-filter: blur(8px) !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(168,85,247,0.6) !important;
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.07)) !important;
    box-shadow: 0 0 40px rgba(99,102,241,0.15) !important;
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
[data-testid="stSidebar"] {
    background: transparent !important;
    border-right: 1px solid rgba(139,92,246,0.3) !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] > div {
    background:
        radial-gradient(ellipse 120% 35% at 50% 0%,  rgba(109,40,217,0.55)  0%, transparent 50%),
        radial-gradient(ellipse 90%  50% at 0%   80%, rgba(168,85,247,0.25)  0%, transparent 60%),
        radial-gradient(ellipse 70%  40% at 100% 50%, rgba(56,189,248,0.12)  0%, transparent 55%),
        linear-gradient(160deg, #0d0a1f 0%, #120e2e 40%, #0a0818 100%) !important;
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
   RADIO
════════════════════════════════════════════ */
[data-testid="stRadio"] label {
    color: #6b7d96 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; transition: color 0.2s ease !important;
}
[data-testid="stRadio"] label:hover { color: #a78bfa !important; }

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

/* ════════════════════════════════════════════
   EXPANDER / OTHER STREAMLIT BITS
════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(139,92,246,0.16) !important;
    border-radius: 16px !important; backdrop-filter: blur(8px) !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(139,92,246,0.35) !important;
}
.stAlert {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 14px !important; backdrop-filter: blur(8px) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Canvas Particle System ─────────────────────────────────────────────────────
st.markdown("""
<canvas id="cosmic-canvas" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;"></canvas>
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

    # ── Brand Header ────────────────────────────────────────────
    st.markdown("""
    <div style='
        text-align:center;
        padding: 2rem 1rem 1.4rem;
        position: relative;
        border-bottom: 1px solid rgba(139,92,246,0.2);
        margin-bottom: 1rem;
    '>
        <!-- Glow blob behind icon -->
        <div style='
            position:absolute; top:20px; left:50%; transform:translateX(-50%);
            width:80px; height:80px;
            background: radial-gradient(circle, rgba(139,92,246,0.45) 0%, transparent 70%);
            border-radius:50%; pointer-events:none;
        '></div>

        <!-- App Icon -->
        <div style='
            width:64px; height:64px;
            background: linear-gradient(135deg, #3730a3, #7c3aed, #a855f7, #ec4899);
            border-radius:20px; display:flex; align-items:center; justify-content:center;
            margin: 0 auto 1rem; font-size:30px;
            box-shadow: 0 8px 30px rgba(139,92,246,0.6), 0 0 0 1px rgba(255,255,255,0.08) inset;
            position: relative; z-index:1;
        '>🧠</div>

        <!-- App Name -->
        <div style='
            font-size:1.05rem; font-weight:800; letter-spacing:-0.01em;
            background: linear-gradient(135deg, #e2e8f0, #c4b5fd);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text; margin-bottom:0.3rem;
        '>AI Notes Summarizer</div>

        <!-- Creator Badge -->
        <div style='
            display:inline-flex; align-items:center; gap:6px;
            background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.15));
            border: 1px solid rgba(139,92,246,0.4);
            border-radius:100px; padding:0.28rem 1rem;
            font-size:0.72rem; font-weight:700; color:#d8b4fe;
            letter-spacing:0.04em;
        '>✨ by Zainab Gondal</div>

        <!-- Version tag -->
        <div style='
            margin-top:0.6rem;
            font-size:0.65rem; font-weight:600; color:#334155;
            letter-spacing:0.08em; text-transform:uppercase;
        '>v2.0 · Powered by Groq + Llama3</div>
    </div>
    """, unsafe_allow_html=True)

    # ── API Key Section ──────────────────────────────────────────
    st.markdown("""
    <div class='sb-section'>
        <span class='sb-label'>🔑 &nbsp;Groq API Key</span>
    </div>
    """, unsafe_allow_html=True)
    sidebar_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_••••••••••••••",
        label_visibility="collapsed",
        help="Get your free key at console.groq.com"
    )
    st.markdown("""
    <div class='sb-tip'>
        <strong>Free &amp; Unlimited</strong> — Get your key at
        <span style='color:#a78bfa;'>console.groq.com</span><br>
        <span style='color:#475569;font-size:0.72rem;'>Your key is never stored or shared.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # ── Input Method ─────────────────────────────────────────────
    st.markdown("<span class='sb-label'>📥 &nbsp;Input Method</span>", unsafe_allow_html=True)
    input_mode = st.radio(
        "Input Method",
        ["📋 Paste Text", "📁 Upload File"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    # ── Supported Formats ────────────────────────────────────────
    st.markdown("""
    <div class='sb-section'>
        <span class='sb-label'>📂 &nbsp;Supported Formats</span>
        <div style='display:flex; flex-wrap:wrap; gap:7px; margin-top:2px;'>
            <span class='sb-format-chip'>📄 PDF</span>
            <span class='sb-format-chip'>📝 DOCX</span>
            <span class='sb-format-chip'>📃 TXT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── What This App Does ───────────────────────────────────────
    st.markdown("""
    <div class='sb-section'>
        <span class='sb-label'>⚡ &nbsp;What You Get</span>
        <div style='display:flex; flex-direction:column; gap:0;'>
            <div class='sb-stat'><span class='sb-stat-label'>⚡ Quick Summary</span><span class='sb-stat-val'>✓</span></div>
            <div class='sb-stat'><span class='sb-stat-label'>📖 Detailed Summary</span><span class='sb-stat-val'>✓</span></div>
            <div class='sb-stat'><span class='sb-stat-label'>🎯 Key Points</span><span class='sb-stat-val'>✓</span></div>
            <div class='sb-stat'><span class='sb-stat-label'>🔬 Knowledge Extract</span><span class='sb-stat-val'>✓</span></div>
            <div class='sb-stat'><span class='sb-stat-label'>❓ Study Questions</span><span class='sb-stat-val'>✓</span></div>
            <div class='sb-stat'><span class='sb-stat-label'>🏷️ NLP Keywords</span><span class='sb-stat-val'>✓</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How To Use ───────────────────────────────────────────────
    st.markdown("""
    <div class='sb-section'>
        <span class='sb-label'>📖 &nbsp;How To Use</span>
        <div style='display:flex; flex-direction:column; gap:6px; margin-top:2px;'>
            <div style='display:flex; align-items:flex-start; gap:8px; font-size:0.78rem; color:#94a3b8;'>
                <span style='color:#a78bfa; font-weight:800; min-width:18px;'>1.</span>
                <span>Enter your <strong style='color:#c4b5fd;'>Groq API key</strong> above</span>
            </div>
            <div style='display:flex; align-items:flex-start; gap:8px; font-size:0.78rem; color:#94a3b8;'>
                <span style='color:#a78bfa; font-weight:800; min-width:18px;'>2.</span>
                <span>Choose <strong style='color:#c4b5fd;'>Paste Text</strong> or <strong style='color:#c4b5fd;'>Upload File</strong></span>
            </div>
            <div style='display:flex; align-items:flex-start; gap:8px; font-size:0.78rem; color:#94a3b8;'>
                <span style='color:#a78bfa; font-weight:800; min-width:18px;'>3.</span>
                <span>Hit <strong style='color:#c4b5fd;'>🔍 Analyse Notes</strong></span>
            </div>
            <div style='display:flex; align-items:flex-start; gap:8px; font-size:0.78rem; color:#94a3b8;'>
                <span style='color:#a78bfa; font-weight:800; min-width:18px;'>4.</span>
                <span>Download your <strong style='color:#c4b5fd;'>full summary</strong> as .txt</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tech Stack ───────────────────────────────────────────────
    st.markdown("""
    <div class='sb-section'>
        <span class='sb-label'>🛠 &nbsp;Tech Stack</span>
        <div style='display:flex; flex-wrap:wrap; gap:6px; margin-top:2px;'>
            <span class='sb-format-chip'>🐍 Python</span>
            <span class='sb-format-chip'>🚀 Groq</span>
            <span class='sb-format-chip'>🦙 Llama3</span>
            <span class='sb-format-chip'>🌊 Streamlit</span>
            <span class='sb-format-chip'>🔤 NLTK</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Footer Credit ─────────────────────────────────────────────
    st.markdown("""
    <div style='
        margin-top: 1rem;
        padding: 1.1rem 1rem;
        text-align: center;
        border-top: 1px solid rgba(139,92,246,0.15);
    '>
        <div style='font-size:0.72rem; color:#334155; line-height:1.7;'>
            Crafted with 💜 by<br>
            <span style='
                font-size:0.88rem; font-weight:800;
                background: linear-gradient(135deg, #a78bfa, #f0abfc, #67e8f9);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                background-clip:text;
            '>Zainab Gondal</span><br>
            <span style='color:#1e293b; font-size:0.68rem;'>Computer Engineering Student · Pakistan</span>
        </div>
        <div style='
            margin-top: 0.7rem;
            display: flex; justify-content:center; gap: 8px; flex-wrap:wrap;
        '>
            <a href="https://zainab-notes-summarizer.streamlit.app/" target="_blank" style='
                display:inline-flex; align-items:center; gap:4px;
                background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.15));
                border: 1px solid rgba(139,92,246,0.4);
                color:#c4b5fd; text-decoration:none;
                padding:4px 12px; border-radius:100px;
                font-size:0.68rem; font-weight:700;
                transition: all 0.2s ease;
            '>🌐 Live App</a>
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
