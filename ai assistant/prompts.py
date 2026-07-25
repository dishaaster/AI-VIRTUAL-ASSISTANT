"""
prompts.py
----------
Central prompt library for the AI Assistant.

Per the assignment's "Prompt Design" requirement, each function has at least
three distinct prompt templates that vary in length/specificity, tone/style,
and complexity/context. These are the exact strings that get sent to the
language model when an API key is configured (see ai_logic.py). They are
also shown in the UI so the grader/user can see the prompt engineering work
behind each function, even when the app is running in offline demo mode.
"""

PROMPTS = {
    "qa": [
        {
            "id": "qa_concise",
            "label": "Concise factual",
            "style": "Short, specificity-first",
            "template": "Answer the following question in 1-2 factual sentences, "
                         "no preamble: {question}"
        },
        {
            "id": "qa_explained",
            "label": "Explained answer",
            "style": "Conversational, adds context",
            "template": "You are a helpful, friendly tutor. A student asked: "
                         "\"{question}\". Give the correct answer, then briefly "
                         "explain why it's true in a way a beginner would understand."
        },
        {
            "id": "qa_listed",
            "label": "Structured facts",
            "style": "Formal, structured, high specificity",
            "template": "Provide exactly three verified facts that answer or relate to "
                         "this question: \"{question}\". Return them as a numbered list, "
                         "one short sentence each, no extra commentary."
        },
    ],
    "summarize": [
        {
            "id": "sum_brief",
            "label": "One-line brief",
            "style": "Extremely concise",
            "template": "Summarize the following text in a single sentence, "
                         "capturing only the main idea:\n\n{text}"
        },
        {
            "id": "sum_bullets",
            "label": "Key points",
            "style": "Structured, scannable",
            "template": "Read the following text and extract the 3-5 most important "
                         "points as short bullet points. Preserve the original meaning "
                         "and do not add outside information:\n\n{text}"
        },
        {
            "id": "sum_detailed",
            "label": "Paragraph overview",
            "style": "Formal, moderate length, more context",
            "template": "Provide a brief overview (3-4 sentences) of the following "
                         "document for someone who has not read it. Mention the topic, "
                         "the main argument or finding, and any conclusion:\n\n{text}"
        },
    ],
    "creative": [
        {
            "id": "creative_story",
            "label": "Short story",
            "style": "Narrative, imaginative",
            "template": "Write a short, creative story (150-200 words) in the "
                         "{genre} genre. It should involve a character described as "
                         "\"{character}\" and explore the theme of {theme}. "
                         "Give it a clear beginning, middle, and end."
        },
        {
            "id": "creative_poem",
            "label": "Poem",
            "style": "Lyrical, compact",
            "template": "Write a short original poem (4-8 lines) about {theme}, "
                         "written in a {genre}-inspired mood, featuring or addressed "
                         "to \"{character}\"."
        },
        {
            "id": "creative_pitch",
            "label": "Story idea / pitch",
            "style": "High-level, generative, low word count",
            "template": "Generate one original story idea / one-paragraph pitch for a "
                         "{genre} story. Include a premise, the character "
                         "\"{character}\", and how the theme of {theme} drives the plot."
        },
    ],
    "advice": [
        {
            "id": "advice_tips",
            "label": "Quick tips",
            "style": "Actionable, list format",
            "template": "Give 3 practical, actionable tips for someone who wants "
                         "advice on: {topic}. Keep each tip to one sentence."
        },
        {
            "id": "advice_stepbystep",
            "label": "Step-by-step plan",
            "style": "Structured, sequential",
            "template": "Create a simple step-by-step plan (4-5 steps) to help "
                         "someone with: {topic}. Order the steps logically."
        },
        {
            "id": "advice_encouraging",
            "label": "Encouraging coach",
            "style": "Warm, motivational tone",
            "template": "As a supportive coach, give encouraging and realistic advice "
                         "to someone dealing with: {topic}. Acknowledge that it can be "
                         "difficult, then offer 2-3 concrete suggestions."
        },
    ],
}


def get_prompt(function, variant_index, **kwargs):
    """Return (prompt_id, filled_prompt_text) for a given function + variant."""
    variants = PROMPTS.get(function, [])
    if not variants:
        raise ValueError(f"Unknown function: {function}")
    variant_index = max(0, min(variant_index, len(variants) - 1))
    variant = variants[variant_index]
    return variant["id"], variant["template"].format(**kwargs)
