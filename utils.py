"""
utils.py
--------
Shared utility functions used across all modules.

Responsibilities:
  - Text cleaning and pre-processing
  - Token / word-count estimation
  - Keyword extraction via NLTK
  - Formatting helpers
"""

import re
import string
from typing import List

# ---------------------------------------------------------------------------
# NLTK setup (downloads happen once at runtime)
# ---------------------------------------------------------------------------
import nltk

def _ensure_nltk_data():
    """Download required NLTK corpora if they are not already present."""
    packages = [
        ("tokenizers/punkt",           "punkt"),
        ("tokenizers/punkt_tab",       "punkt_tab"),
        ("corpora/stopwords",          "stopwords"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ]
    for path, name in packages:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)

_ensure_nltk_data()

from nltk.tokenize import word_tokenize
from nltk.corpus   import stopwords

STOP_WORDS = set(stopwords.words("english"))


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Remove excessive whitespace and non-printable characters.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned text string.
    """
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove stray carriage returns
    text = text.replace("\r", "")
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def truncate_text(text: str, max_words: int = 2500) -> str:
    """
    Truncate text to a maximum word count to stay within LLM token limits.

    Args:
        text:      Input text.
        max_words: Maximum number of words to keep (default 2 500 ≈ ~3 000 tokens).

    Returns:
        Truncated text string (whole words only).
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "\n\n[... text truncated for processing ...]"


# ---------------------------------------------------------------------------
# Word / token counting
# ---------------------------------------------------------------------------

def count_words(text: str) -> int:
    """Return the approximate word count of a string."""
    return len(text.split())


def estimate_read_time(text: str, wpm: int = 200) -> str:
    """
    Estimate human reading time.

    Args:
        text: Input text.
        wpm:  Average words per minute (default 200).

    Returns:
        Human-friendly string like "3 min read".
    """
    words   = count_words(text)
    minutes = max(1, round(words / wpm))
    return f"{minutes} min read"


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """
    Extract the most frequent non-stop-word tokens using NLTK.

    Strategy:
      1. Tokenise the text.
      2. Lower-case every token.
      3. Keep only alphabetic tokens longer than 2 characters.
      4. Remove English stop-words.
      5. Rank by frequency and return the top N.

    Args:
        text:  Input text to analyse.
        top_n: Number of keywords to return.

    Returns:
        List of keyword strings ordered by frequency (highest first).
    """
    tokens = word_tokenize(text.lower())

    # Keep only meaningful alphabetic tokens
    filtered = [
        t for t in tokens
        if t.isalpha()
        and len(t) > 2
        and t not in STOP_WORDS
        and t not in string.punctuation
    ]

    # Frequency count
    freq: dict = {}
    for token in filtered:
        freq[token] = freq.get(token, 0) + 1

    # Sort by frequency descending
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_keywords[:top_n]]


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_bullet_list(items: List[str]) -> str:
    """Convert a Python list into a markdown bullet list."""
    return "\n".join(f"• {item}" for item in items)


def section_divider(title: str) -> str:
    """Return a simple text section header."""
    bar = "─" * 60
    return f"\n{bar}\n  {title.upper()}\n{bar}\n"
