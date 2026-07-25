const FN_META = {
  qa: {
    title: "Answer Questions",
    desc: "Ask a factual question. Pick a prompt style below to see how phrasing changes the assistant's approach.",
  },
  summarize: {
    title: "Summarize Text",
    desc: "Paste any block of text. Choose how compact or detailed you want the summary to be.",
  },
  creative: {
    title: "Generate Creative Content",
    desc: "Give the assistant a genre, character, and theme — it will generate a story, poem, or pitch depending on the prompt style you pick.",
  },
  advice: {
    title: "Give Advice",
    desc: "Describe what you'd like advice on. The assistant can respond with quick tips, a step-by-step plan, or an encouraging coach-style answer.",
  },
};

let PROMPTS = {};
let currentFn = "qa";
let currentVariant = 0;
let lastResult = null;

async function loadPrompts() {
  const res = await fetch("/api/prompts");
  PROMPTS = await res.json();
  renderVariantPicker();
}

function renderVariantPicker() {
  const container = document.getElementById("variant-picker");
  container.innerHTML = "";
  const variants = PROMPTS[currentFn] || [];
  variants.forEach((v, idx) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "variant-chip" + (idx === currentVariant ? " active" : "");
    chip.innerHTML = `${v.label}<span class="chip-style">${v.style}</span>`;
    chip.addEventListener("click", () => {
      currentVariant = idx;
      renderVariantPicker();
    });
    container.appendChild(chip);
  });
}

function switchFunction(fn) {
  currentFn = fn;
  currentVariant = 0;
  document.querySelectorAll(".fn-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.fn === fn);
  });
  document.getElementById("fn-title").textContent = FN_META[fn].title;
  document.getElementById("fn-desc").textContent = FN_META[fn].desc;

  document.querySelectorAll("[data-field]").forEach((el) => {
    el.hidden = el.dataset.field !== fn;
  });

  document.getElementById("prompt-panel").hidden = true;
  document.getElementById("response-panel").hidden = true;
  document.getElementById("error-panel").hidden = true;

  renderVariantPicker();
}

function collectInputs() {
  if (currentFn === "qa") return { question: document.getElementById("input-question").value };
  if (currentFn === "summarize") return { text: document.getElementById("input-text").value };
  if (currentFn === "creative")
    return {
      genre: document.getElementById("input-genre").value,
      character: document.getElementById("input-character").value,
      theme: document.getElementById("input-theme").value,
    };
  if (currentFn === "advice") return { topic: document.getElementById("input-topic").value };
  return {};
}

async function runAssistant(e) {
  e.preventDefault();
  const btn = document.getElementById("run-btn");
  btn.disabled = true;
  btn.textContent = "Running…";
  document.getElementById("error-panel").hidden = true;

  const payload = { function: currentFn, variant_index: currentVariant, ...collectInputs() };

  try {
    const res = await fetch("/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Something went wrong.");
    }

    lastResult = data;

    document.getElementById("prompt-panel").hidden = false;
    document.getElementById("prompt-text").textContent = data.prompt_text;

    document.getElementById("response-panel").hidden = false;
    document.getElementById("response-text").textContent = data.response;

    const badge = document.getElementById("response-mode-badge");
    badge.textContent = data.mode === "live" ? "live model" : "offline demo";
    badge.className = "mode-badge " + data.mode;

    document.getElementById("fb-yes").classList.remove("selected");
    document.getElementById("fb-no").classList.remove("selected");
    document.getElementById("feedback-thanks").hidden = true;
    document.getElementById("feedback-row").style.display = "flex";
  } catch (err) {
    document.getElementById("error-panel").hidden = false;
    document.getElementById("error-panel").textContent = err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = "Run assistant →";
  }
}

async function sendFeedback(helpful) {
  if (!lastResult) return;
  document.getElementById("fb-yes").classList.toggle("selected", helpful);
  document.getElementById("fb-no").classList.toggle("selected", !helpful);

  await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      function: lastResult.function,
      prompt_id: lastResult.prompt_id,
      prompt_text: lastResult.prompt_text,
      response: lastResult.response,
      helpful,
    }),
  });

  document.getElementById("feedback-thanks").hidden = false;
  loadStats();
}

async function loadStats() {
  const res = await fetch("/api/feedback/stats");
  const data = await res.json();
  document.getElementById("stat-total").textContent = data.total;
  document.getElementById("stat-rate").textContent = data.helpful_rate === null ? "—" : data.helpful_rate + "%";
}

document.querySelectorAll(".fn-btn").forEach((btn) => {
  btn.addEventListener("click", () => switchFunction(btn.dataset.fn));
});

document.getElementById("fn-form").addEventListener("submit", runAssistant);
document.getElementById("fb-yes").addEventListener("click", () => sendFeedback(true));
document.getElementById("fb-no").addEventListener("click", () => sendFeedback(false));

loadPrompts();
loadStats();
