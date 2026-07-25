import os
import re
import random
import string

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

# --------------------------------------------------------------------------
# Optional: real LLM call
# --------------------------------------------------------------------------

def _call_openai(prompt_text):
    """Try a real API call. Returns response text, or None if unavailable/failed."""
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=400,
            temperature=0.8,
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001 - want any failure to fall back gracefully
        print(f"[ai_logic] OpenAI call failed, falling back to offline mode: {exc}")
        return None


# --------------------------------------------------------------------------
# Offline fallback: Answer Questions
# --------------------------------------------------------------------------

_KNOWLEDGE_BASE = {
    "capital of france": "The capital of France is Paris.",
    "capital of india": "The capital of India is New Delhi.",
    "capital of japan": "The capital of Japan is Tokyo.",
    "capital of italy": "The capital of Italy is Rome.",
    "capital of usa": "The capital of the USA is Washington, D.C.",
    "capital of united states": "The capital of the USA is Washington, D.C.",
    "eiffel tower": "The Eiffel Tower is a 330m iron lattice tower in Paris, built "
                     "in 1889 by Gustave Eiffel's company as the entrance to the "
                     "1889 World's Fair. It's now one of the most visited landmarks "
                     "in the world.",
    "who invented python": "Python was created by Guido van Rossum and first "
                            "released in 1991.",
    "what is photosynthesis": "Photosynthesis is the process by which plants use "
                               "sunlight, water, and carbon dioxide to create "
                               "glucose and oxygen.",
    "largest planet": "Jupiter is the largest planet in our solar system.",
    "speed of light": "The speed of light in a vacuum is approximately "
                       "299,792 kilometers per second (about 186,282 miles/second).",
    "who wrote romeo and juliet": "Romeo and Juliet was written by William "
                                   "Shakespeare, believed to have been written "
                                   "between 1591 and 1596.",
    "tallest mountain": "Mount Everest, at 8,849 meters, is the tallest mountain "
                         "above sea level, located in the Himalayas.",
}


def answer_question(question):
    q = question.lower().strip(string.punctuation + " ")
    for key, fact in _KNOWLEDGE_BASE.items():
        if key in q:
            return fact
    # crude keyword fallback
    for key, fact in _KNOWLEDGE_BASE.items():
        keywords = key.split()
        if all(k in q for k in keywords if len(k) > 3):
            return fact
    return (
        "I don't have that fact in my offline knowledge base yet "
        "(this demo mode only covers a small set of sample facts). "
        "Connect an OPENAI_API_KEY to let the assistant answer any question "
        "using a real language model."
    )


# --------------------------------------------------------------------------
# Offline fallback: Summarize Text
# --------------------------------------------------------------------------

_STOPWORDS = set("""
a an the and or but if while is are was were be been being to of in on for
with as at by from that this these those it its it's their his her they he
she we you i our your not no so than then there here can could will would
should may might do does did have has had into about over under out up down
""".split())


def _split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def summarize_text(text, max_sentences=3):
    sentences = _split_sentences(text)
    if len(sentences) <= max_sentences:
        return text.strip()

    words = re.findall(r"[a-zA-Z']+", text.lower())
    freq = {}
    for w in words:
        if w in _STOPWORDS or len(w) <= 2:
            continue
        freq[w] = freq.get(w, 0) + 1

    if not freq:
        return " ".join(sentences[:max_sentences])

    max_freq = max(freq.values())
    for w in freq:
        freq[w] /= max_freq

    scores = []
    for idx, sentence in enumerate(sentences):
        s_words = re.findall(r"[a-zA-Z']+", sentence.lower())
        if not s_words:
            score = 0
        else:
            score = sum(freq.get(w, 0) for w in s_words) / len(s_words)
        # slight boost for earlier sentences (topic sentences)
        position_boost = 1.15 if idx == 0 else 1.0
        scores.append((score * position_boost, idx, sentence))

    top = sorted(scores, key=lambda x: x[0], reverse=True)[:max_sentences]
    top_in_order = [s for _, _, s in sorted(top, key=lambda x: x[1])]
    return " ".join(top_in_order)


# --------------------------------------------------------------------------
# Offline fallback: Generate Creative Content
# --------------------------------------------------------------------------

_OPENINGS = [
    "The old town was quiet the night everything changed.",
    "No one believed the legends were true — until now.",
    "It began, as most strange things do, with a locked door that shouldn't exist.",
    "Long before the maps were drawn, this was already someone's story.",
]

_TWISTS = [
    "a secret that had been buried for generations resurfaced",
    "a stranger arrived carrying more questions than answers",
    "the rules everyone trusted turned out to be wrong",
    "a small, ordinary choice changed everything that followed",
]

_ENDINGS = [
    "In the end, nothing was quite the same — and that was the point.",
    "It wasn't the ending anyone expected, but it was the one that felt true.",
    "And so the story that began in silence closed with something like hope.",
    "What remained was smaller than a triumph, but it was enough.",
]


def generate_story(genre, character, theme):
    opening = random.choice(_OPENINGS)
    twist = random.choice(_TWISTS)
    ending = random.choice(_ENDINGS)
    return (
        f"[{genre.title()} | offline demo generator]\n\n"
        f"{opening} At the center of it all was {character}, who never expected "
        f"to be tested this way. As the story unfolded, {twist}, forcing "
        f"{character} to confront the theme of {theme} head-on. "
        f"{ending}"
    )


def generate_poem(genre, character, theme):
    lines = [
        f"For {character}, beneath a {genre}-tinted sky,",
        f"the meaning of {theme} was never asked, only lived.",
        "Some truths arrive slowly, like light through old glass,",
        f"and some, like {theme}, arrive all at once.",
        f"Still, {character} walked on — unfinished, unafraid.",
    ]
    return "\n".join(lines)


def generate_pitch(genre, character, theme):
    return (
        f"[{genre.title()} pitch | offline demo generator]\n\n"
        f"When {character} discovers that everything they believed about "
        f"{theme} was incomplete, they're forced into a journey that blurs the "
        f"line between what they wanted and what they actually need. "
        f"A story about {theme}, told through the eyes of someone who never "
        f"planned to be the one who changed things."
    )


# --------------------------------------------------------------------------
# Offline fallback: Advice
# --------------------------------------------------------------------------

_ADVICE_BANK = {
    "study": [
        "Break study sessions into 25-minute focused blocks with short breaks "
        "(the Pomodoro technique).",
        "Test yourself actively (flashcards, practice questions) instead of "
        "just re-reading notes.",
        "Teach the material out loud to someone else — it exposes gaps fast.",
    ],
    "time management": [
        "Write tomorrow's top 3 priorities the night before.",
        "Batch similar small tasks (emails, messages) into one time block.",
        "Protect one distraction-free block each day for your hardest task.",
    ],
    "productivity": [
        "Start with the hardest task while your energy is highest.",
        "Turn off non-essential notifications during focus blocks.",
        "Review what worked at the end of each day, not just what's left to do.",
    ],
    "stress": [
        "Name the specific worry instead of letting it stay vague — it's easier "
        "to act on.",
        "Take short movement breaks; even a 5-minute walk resets focus.",
        "Separate what's in your control today from what isn't, and act only "
        "on the first list.",
    ],
    "public speaking": [
        "Practice out loud, not just in your head — timing surprises people "
        "who skip this.",
        "Open with your strongest point; audiences remember beginnings.",
        "Pause instead of filling silence with 'um' — it reads as confidence.",
    ],
}

_GENERIC_ADVICE = [
    "Break the goal into the smallest next action you can take today.",
    "Track progress somewhere visible — momentum is easier to see than to feel.",
    "Ask someone who has already done this for the one thing they'd do differently.",
]


def give_advice(topic):
    t = topic.lower()
    for key, tips in _ADVICE_BANK.items():
        if key in t:
            return tips
    for key, tips in _ADVICE_BANK.items():
        if any(word in t for word in key.split()):
            return tips
    return _GENERIC_ADVICE


# --------------------------------------------------------------------------
# Public dispatch used by app.py
# --------------------------------------------------------------------------

def run_function(function, prompt_text, params):
    """
    Try the real model first (if configured); otherwise use offline logic.
    Returns (response_text, mode) where mode is 'live' or 'offline'.
    """
    live_response = _call_openai(prompt_text)
    if live_response:
        return live_response, "live"

    if function == "qa":
        return answer_question(params.get("question", "")), "offline"

    if function == "summarize":
        return summarize_text(params.get("text", "")), "offline"

    if function == "creative":
        variant = params.get("variant_id", "")
        genre = params.get("genre", "fantasy")
        character = params.get("character", "a curious traveler")
        theme = params.get("theme", "change")
        if variant == "creative_poem":
            return generate_poem(genre, character, theme), "offline"
        if variant == "creative_pitch":
            return generate_pitch(genre, character, theme), "offline"
        return generate_story(genre, character, theme), "offline"

    if function == "advice":
        tips = give_advice(params.get("topic", ""))
        return "\n".join(f"• {t}" for t in tips), "offline"

    return "Unknown function requested.", "offline"
