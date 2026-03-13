"""
question_generator.py
---------------------
Generates study questions from lecture notes using Groq (free API).
"""

from groq import Groq
from utils import truncate_text


def _chat(client: Groq, system_prompt: str, user_prompt: str,
          temperature: float = 0.5) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_conceptual_questions(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = (
        "You are an experienced university professor creating exam questions "
        "that test deep understanding, not just memorisation."
    )
    user = (
        "Based on the lecture notes below, write exactly 5 conceptual "
        "questions that require the student to think critically and "
        "demonstrate understanding. "
        "Number them 1 through 5.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def generate_mcq_questions(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = (
        "You are an expert at writing multiple-choice exam questions for "
        "university students."
    )
    user = (
        "Create exactly 5 multiple-choice questions from the lecture notes "
        "below. For each question:\n"
        "  - Write the question numbered Q1-Q5.\n"
        "  - Provide four answer options labelled A), B), C), D).\n"
        "  - On the next line, state: Correct Answer: [Letter]) [Text]\n"
        "  - Leave a blank line between questions.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def generate_short_answer_questions(client: Groq, text: str) -> str:
    safe_text = truncate_text(text, max_words=2000)
    system = (
        "You are an academic tutor who creates concise revision questions "
        "to help students review key information quickly."
    )
    user = (
        "Write exactly 3 short-answer revision questions from the lecture "
        "notes below. For each question, also provide a concise model "
        "answer (2-4 sentences).\n\n"
        "Format:\n"
        "  Q[n]. [Question text]\n"
        "  Model Answer: [Answer text]\n\n"
        "Leave a blank line between each question.\n\n"
        f"NOTES:\n{safe_text}"
    )
    return _chat(client, system, user)


def generate_all_questions(client: Groq, text: str) -> dict:
    return {
        "conceptual":   generate_conceptual_questions(client, text),
        "mcq":          generate_mcq_questions(client, text),
        "short_answer": generate_short_answer_questions(client, text),
    }
