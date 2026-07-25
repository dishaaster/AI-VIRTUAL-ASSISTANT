# Prompt Bench — AI Assistant

Major Project: "AI Assistant Development" (Prompt Engineering)
Author: Disha Tripathi

A small web-based AI Assistant with four functions (Answer Questions, Summarize
Text, Generate Creative Content, Give Advice), three engineered prompt variants
per function, a working feedback loop, and a Flask + vanilla JS front end.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## Optional: connect a real model

By default the app runs fully offline using built-in logic (a mini knowledge
base, an extractive summarizer, template-based creative generation, and a tip
bank) so it can be graded/demoed without any paid API access. To route the
exact same engineered prompts to a real OpenAI model instead:

```bash
export OPENAI_API_KEY=sk-...      # macOS/Linux
set OPENAI_API_KEY=sk-...         # Windows (cmd)
python app.py
```

The UI badge on each response shows whether it came from the "live model" or
"offline demo" logic.

## Project structure

```
app.py            Flask routes (UI, /api/process, /api/feedback)
ai_logic.py        Offline fallback logic + optional OpenAI call
prompts.py          Prompt library (3 variants x 4 functions)
templates/index.html   Single-page UI
static/style.css        Styling
static/app.js            Front-end logic
data/feedback_log.json    Feedback records (created at runtime)
```

## Assignment mapping

- **Functionality (3+ functions):** Answer Questions, Summarize Text, Generate
  Creative Content, plus a bonus Give Advice function.
- **Prompt design (3+ prompts per function):** see `prompts.py` — each set
  varies length/specificity, tone/style, and complexity/context.
- **User interaction:** web UI lets users choose a function, choose a prompt
  style, submit input, and view the response.
- **Feedback loop:** Yes/No "Was this helpful?" after every response, logged
  to `data/feedback_log.json` with the prompt and response, plus a live
  helpful-rate stat in the sidebar.
- **Documentation:** see the accompanying PPT user guide.
