# MedGuide AI

# Streamlit Demo @ [mediguide-clinical-aii.streamlit.app](https://mediguide-clinical-aii.streamlit.app/)
# Video link: [Click Here](https://drive.google.com/file/d/1K3Ra6LYFH3YQjia-evowuEHZ-FLIf_QH/view?usp=sharing)

An educational Streamlit + LangChain prototype that turns a patient's
self-reported symptoms into structured, safety-first guidance.

> ⚠️ **This is an educational prototype only.** MedGuide AI is **not a real
> doctor**, not a licensed clinician, not a diagnostic tool, and not a
> substitute for professional medical advice. Every diagnosis, urgency
> rating, and treatment suggestion is a machine-generated educational
> estimate that can be wrong or incomplete. If you think you may have a
> medical emergency, call your local emergency number or go to the nearest
> emergency room immediately.

## 🔐 About the `.env` file

`.env.example` in this repo is a **placeholder template only** — it does not
contain a real key. Copy it to `.env` and paste your own key there; `.env`
is already git-ignored. **Never** paste a real API key into a file you
upload or share with anyone (including an AI assistant) — if a real key is
ever exposed, treat it as compromised and rotate it immediately at
https://platform.openai.com/api-keys.

## What's new in this version

- **Real logo**: an inline SVG brand mark (rounded badge + pulse/caduceus
  motif) in the header and sidebar, replacing the emoji placeholder.
- **High-contrast theme fix**: widget labels, inputs, selects, sliders,
  checkboxes, and expander text are all explicitly styled so nothing
  renders dark-on-dark or disappears against the background.
- **≥ 5 differential diagnoses, always**: the prompt requires at least
  five plausible differentials, and `safe_parse_assessment` pads the list
  if the model ever returns fewer, so the UI never shows less than that.
- **Treatment + rationale per differential**: each condition card now
  includes a suggested treatment and the clinical reasoning behind it.
- **Tick-to-confirm clarifying questions**: when the AI's
  `diagnostic_confidence` is Moderate/Low, it still commits to a leading
  diagnosis but surfaces a checklist of confirmation questions you can
  tick off, with a live progress bar.
- **MCQ-style practice mode**: a new "Practice Cases" panel with USMLE-style
  progressive vignettes — minimal symptoms first, an MCQ, then more findings
  revealed step by step, ending on the true diagnosis with an explanation.
- **Reordered results tabs**: Differentials → Narrowing Protocol → Live
  Narrative Stream → Clinical Summary → Workup & Next Steps → Red Flags.

## Features

- Patient intake form (age, gender, symptoms, duration, severity, existing
  conditions, medications, notes, answer language).
- Structured JSON assessment (summary, possible conditions, urgency level,
  next steps, doctor questions, warning signs) generated via a LangChain
  `LLMChain`.
- Live-streamed, human-readable narrative using `.stream()` +
  `st.write_stream()`.
- Results dashboard with `st.metric`, `st.warning/info/error/success`,
  `st.expander`, and tabs.
- Safe JSON parsing - malformed model output never crashes the app.
- Both `InMemoryCache` and `SQLiteCache` are supported and switchable from
  the sidebar.
- A small demo of `SystemMessage` / `HumanMessage` / `AIMessage` used
  directly (separate from the main chain), for learning purposes.

## Project structure

```
medical_ai_assistant/
├── app.py                 # Streamlit UI - run this
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── __init__.py
    ├── config.py           # settings + form options
    ├── prompts.py          # PromptTemplate + ChatPromptTemplate + JSON schema
    ├── chains.py            # ChatOpenAI, LLMChain, streaming, message demo
    ├── cache_manager.py     # in-memory + SQLite caching switches
    └── utils.py             # safe JSON parsing + helpers
```

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and paste your key from https://platform.openai.com/api-keys:
   ```
   OPENAI_API_KEY=sk-...
   ```
   `.env` is already listed in `.gitignore` - never commit your real key.

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## How it works (data flow)

```
form input → build prompt inputs → select cache → build LLM + LLMChain
→ run chain → parse JSON safely → stream narrative → render dashboard
```

1. The Streamlit form collects patient data.
2. `src/prompts.py` builds a `PromptTemplate` prompt from that data and asks
   the model to return **only** valid JSON matching a fixed schema.
3. `src/chains.py` runs that prompt through a `ChatOpenAI` model wrapped in
   an `LLMChain`.
4. `src/utils.py` strips any stray code fences and safely parses the JSON,
   falling back to a friendly error + raw output view if parsing fails.
5. On request, a second call uses a `ChatPromptTemplate` (System + Human
   messages) and `.stream()` to narrate the same assessment in plain
   language, rendered live with `st.write_stream()`.

## Caching: InMemoryCache vs SQLiteCache

Both are implemented in `src/cache_manager.py` and can be switched from the
sidebar. LangChain checks whichever cache is registered via
`set_llm_cache(...)` automatically before every model call - identical
requests are served from the cache instead of calling the API again.

| | InMemoryCache | SQLiteCache |
|---|---|---|
| Storage | RAM | A file on disk (`medguide_cache.db`) |
| Speed | Fastest | Fast, slightly slower |
| Survives restart? | No | Yes |
| Best for | One session / quick testing | Reusing results across sessions |

**To test it:** submit the exact same form twice with caching set to
"In-Memory" or "SQLite". The second submission should return noticeably
faster (see the elapsed-time caption under the spinner), because the
identical request is served from the cache instead of calling OpenAI again.

## Testing scenarios

| # | Input | Expected behaviour |
|---|---|---|
| 1 | Age 25, runny nose + sore throat, 1-3 days, severity 2 | Urgency LOW; calm monitoring advice |
| 2 | Age 40, fever + cough, 4-7 days, severity 6 | Urgency MEDIUM/HIGH; advises seeing a professional |
| 3 | Severe chest pain + shortness of breath | Urgency HIGH/EMERGENCY; urges immediate help |
| 4 | Submit the same form twice (cache on) | Second run is faster; identical result |
| 5 | Empty symptoms | App warns the user and does not call the API |
| 6 | Language = Urdu | Guidance text returns in Urdu |

## Safety notes

- The app is clearly labelled an educational AI system, never a doctor.
- It never presents a confirmed diagnosis - only educational "possible
  conditions".
- The disclaimer appears in the sidebar, the main area, and the results
  dashboard.
- EMERGENCY-level output always tells the user to seek emergency help
  immediately.
- The system prompt (`SAFETY_SYSTEM_RULES` in `src/prompts.py`) encodes
  these constraints so the model itself is instructed to behave safely.

## Disclaimer

This project was built for a LangChain/Streamlit programming assignment.
It is **not a medical device** and must not be used for real diagnosis or
treatment. Always consult a qualified healthcare professional.

Some new line of text

Some new line of text

Some new line of text
