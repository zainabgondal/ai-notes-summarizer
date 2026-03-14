"""
flashcard_generator.py
-----------------------
Generates Q&A flashcards from notes using Groq API.
"""

import time


def generate_flashcards(client, text, language="English"):
    """Generate 8 Q&A flashcards from the given notes text."""
    lang_note = f" IMPORTANT: Respond entirely in {language}." if language != "English" else ""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=900,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a study assistant. Create exactly 8 clear Q&A flashcards from the notes. "
                        "Format STRICTLY as:\nQ: [question here]\nA: [answer here]\n\n"
                        "Each question should test understanding. Each answer should be 1-2 sentences max. "
                        "Do not add any intro text, numbering, or extra formatting."
                        + lang_note
                    ),
                },
                {
                    "role": "user",
                    "content": f"Create 8 flashcards from these notes:\n\n{text[:3500]}",
                },
            ],
        )
        raw = response.choices[0].message.content
        return _parse_flashcards(raw)
    except Exception:
        time.sleep(5)
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=900,
                messages=[
                    {
                        "role": "system",
                        "content": "Create 8 Q&A flashcards. Format each as:\nQ: question\nA: answer" + lang_note,
                    },
                    {"role": "user", "content": f"Notes:\n\n{text[:2000]}"},
                ],
            )
            raw = response.choices[0].message.content
            return _parse_flashcards(raw)
        except Exception as e:
            return [{"q": "Could not generate flashcards", "a": str(e)}]


def _parse_flashcards(raw: str):
    """Parse raw LLM output into list of {q, a} dicts."""
    cards = []
    current_q = None
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("q:"):
            current_q = line[2:].strip()
        elif line.lower().startswith("a:") and current_q:
            cards.append({"q": current_q, "a": line[2:].strip()})
            current_q = None
    # fallback if parsing fails
    if not cards:
        cards = [{"q": "See full notes for details", "a": raw[:200]}]
    return cards
