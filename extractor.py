"""
extractor.py
------------
Extracts structured knowledge elements from lecture notes using Groq (free API).
"""

from groq import Groq
from utils import truncate_text


def _chat(client: Groq, system_prompt: str, user_prompt: str,
          temperature: float = 0.3) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def extract_important_concepts(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = (
        "You are a knowledge-extraction expert. Your job is to identify the "
        "core academic or technical concepts within a body of text."
    )
    user = (
        "From the lecture notes below, list the 5-8 most important concepts. "
        "Format each as:\n"
        "  [Number]. **Concept Name** - one-sentence explanation.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def extract_definitions(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = (
        "You are an expert at identifying and extracting definitions from "
        "academic and technical documents."
    )
    user = (
        "Identify all terms that are defined or explained in the lecture "
        "notes below. For each one, provide the term and its definition "
        "in the format:\n"
        "  **Term**: clear, concise definition.\n\n"
        "If no explicit definitions exist, infer them from context.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def extract_key_terms(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = "You are an expert vocabulary analyst for academic content."
    user = (
        "From the lecture notes below, identify 10-15 important key terms "
        "or vocabulary words that a student should know. "
        "Return them as a comma-separated list. "
        "Do not add explanations, just the terms.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def extract_important_facts(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = (
        "You are a fact-extraction specialist trained to identify the most "
        "significant, memorable, and exam-relevant facts in academic notes."
    )
    user = (
        "List the 6-10 most important facts, statistics, dates, or notable "
        "statements from the lecture notes below. "
        "Format each as a bullet point starting with '• '.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def run_full_extraction(client: Groq, text: str) -> dict:
    return {
        "concepts":        extract_important_concepts(client, text),
        "definitions":     extract_definitions(client, text),
        "key_terms":       extract_key_terms(client, text),
        "important_facts": extract_important_facts(client, text),
    }
