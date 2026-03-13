"""
summarizer.py
-------------
Handles all AI-powered summarization tasks using Groq (free API).
"""

from groq import Groq
from utils import truncate_text


def _chat(client: Groq, system_prompt: str, user_prompt: str,
          temperature: float = 0.4) -> str:
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_quick_summary(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2500)
    system = (
        "You are an expert academic assistant specialising in summarising "
        "lecture notes clearly and concisely for university students."
    )
    user = (
        "Please write a quick summary of the following lecture notes in "
        "exactly 3 to 5 sentences. The summary must capture the core topic, "
        "the main argument or concept, and why it matters.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user, temperature=0.3)


def generate_detailed_summary(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2500)
    system = (
        "You are an expert academic assistant. Your task is to write "
        "comprehensive, well-organised summaries that help students deeply "
        "understand the subject matter."
    )
    user = (
        "Write a detailed summary of the lecture notes below. "
        "Structure your response in clear paragraphs using descriptive "
        "sub-headings where appropriate. Explain each major concept fully "
        "and show how ideas connect to each other. "
        "Aim for 200-350 words.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user, temperature=0.4)


def generate_key_points(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2500)
    system = (
        "You are an expert academic assistant who excels at distilling "
        "complex material into clear, memorable bullet points."
    )
    user = (
        "Extract the 8-12 most important key points from the lecture notes "
        "below. Format each point as a concise bullet starting with '• '. "
        "Each bullet should be a complete, standalone idea.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user, temperature=0.3)
