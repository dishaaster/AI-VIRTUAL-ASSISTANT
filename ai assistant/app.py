import json
import os
from datetime import datetime

from flask import Flask, request, jsonify, render_template

from prompts import PROMPTS, get_prompt
from ai_logic import run_function

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FEEDBACK_LOG = os.path.join(DATA_DIR, "feedback_log.json")
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(FEEDBACK_LOG):
    with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
        json.dump([], f)


def _load_feedback():
    try:
        with open(FEEDBACK_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_feedback(entries):
    with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html", prompts=PROMPTS)


@app.route("/api/prompts")
def api_prompts():
    return jsonify(PROMPTS)


@app.route("/api/process", methods=["POST"])
def api_process():
    data = request.get_json(force=True) or {}
    function = data.get("function")
    variant_index = int(data.get("variant_index", 0))

    if function not in PROMPTS:
        return jsonify({"error": f"Unknown function '{function}'"}), 400

    try:
        if function == "qa":
            question = (data.get("question") or "").strip()
            if not question:
                return jsonify({"error": "Please enter a question."}), 400
            prompt_id, prompt_text = get_prompt(function, variant_index, question=question)
            params = {"question": question}

        elif function == "summarize":
            text = (data.get("text") or "").strip()
            if not text:
                return jsonify({"error": "Please paste some text to summarize."}), 400
            prompt_id, prompt_text = get_prompt(function, variant_index, text=text)
            params = {"text": text}

        elif function == "creative":
            genre = (data.get("genre") or "fantasy").strip()
            character = (data.get("character") or "a curious traveler").strip()
            theme = (data.get("theme") or "change").strip()
            prompt_id, prompt_text = get_prompt(
                function, variant_index, genre=genre, character=character, theme=theme
            )
            params = {"genre": genre, "character": character, "theme": theme, "variant_id": prompt_id}

        elif function == "advice":
            topic = (data.get("topic") or "").strip()
            if not topic:
                return jsonify({"error": "Please enter a topic you'd like advice on."}), 400
            prompt_id, prompt_text = get_prompt(function, variant_index, topic=topic)
            params = {"topic": topic}

        else:
            return jsonify({"error": "Unsupported function."}), 400

    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Could not build prompt: {exc}"}), 400

    response_text, mode = run_function(function, prompt_text, params)

    return jsonify({
        "function": function,
        "prompt_id": prompt_id,
        "prompt_text": prompt_text,
        "response": response_text,
        "mode": mode,  # 'live' (real API) or 'offline' (local demo logic)
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json(force=True) or {}
    required = ["function", "prompt_id", "response", "helpful"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing feedback fields."}), 400

    entries = _load_feedback()
    entries.append({
        "function": data["function"],
        "prompt_id": data["prompt_id"],
        "prompt_text": data.get("prompt_text", ""),
        "response": data["response"],
        "helpful": bool(data["helpful"]),
        "comment": data.get("comment", ""),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    _save_feedback(entries)
    return jsonify({"status": "ok", "total_feedback": len(entries)})


@app.route("/api/feedback/stats")
def api_feedback_stats():
    entries = _load_feedback()
    total = len(entries)
    helpful = sum(1 for e in entries if e.get("helpful"))
    by_function = {}
    for e in entries:
        fn = e.get("function", "unknown")
        by_function.setdefault(fn, {"total": 0, "helpful": 0})
        by_function[fn]["total"] += 1
        if e.get("helpful"):
            by_function[fn]["helpful"] += 1
    return jsonify({
        "total": total,
        "helpful": helpful,
        "helpful_rate": round(helpful / total * 100, 1) if total else None,
        "by_function": by_function,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
