"""
src/config.py
--------------
Static configuration: form options, model list, colour tokens, the
disclaimer copy, and the app's logo (a real inline SVG mark, not an emoji).
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_OVERRIDE = os.getenv("OPENAI_MODEL", "")

# -----------------------------------------------------------------------
# Form options
# -----------------------------------------------------------------------
GENDER_OPTIONS = ["Female", "Male", "Non-binary", "Prefer not to say"]

DURATION_OPTIONS = [
    "< 24 hours",
    "1-3 days",
    "4-7 days",
    "1-2 weeks",
    "2-4 weeks",
    "> 1 month (chronic)",
]

COMMON_SYMPTOMS = [
    "Fever", "Chills", "Cough", "Sore throat", "Runny nose",
    "Shortness of breath", "Chest pain", "Palpitations",
    "Headache", "Dizziness", "Fatigue", "Nausea", "Vomiting",
    "Diarrhea", "Abdominal pain", "Back pain", "Joint pain",
    "Muscle aches", "Rash", "Numbness / tingling", "Blurred vision",
    "Loss of appetite", "Unintentional weight loss", "Night sweats",
]

LANGUAGE_OPTIONS = ["English", "Urdu", "Spanish", "French", "Arabic", "Hindi"]

AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
DEFAULT_MODEL = OPENAI_MODEL_OVERRIDE if OPENAI_MODEL_OVERRIDE in AVAILABLE_MODELS else "gpt-4o-mini"

# Minimum number of differential diagnoses the assessment must contain.
MIN_DIFFERENTIALS = 5

URGENCY_COLOURS = {
    "LOW": "🟢",
    "MEDIUM": "🟡",
    "HIGH": "🟠",
    "EMERGENCY": "🔴",
}

# -----------------------------------------------------------------------
# Disclaimers (refined per project safety requirements)
# -----------------------------------------------------------------------
DISCLAIMER_SHORT = (
    "🎓 Educational prototype only — not a real doctor, not a diagnosis, "
    "not a substitute for professional medical care."
)

DISCLAIMER_LONG = (
    "MediGuide AI is an educational software prototype built for a "
    "LangChain/Streamlit programming assignment. It is **not a real doctor, "
    "not a licensed clinician, and not a certified medical device.** Every "
    "diagnosis, urgency rating, and treatment suggestion shown here is a "
    "machine-generated educational estimate and can be wrong or incomplete. "
    "It must never be used to make real medical decisions. If you or "
    "someone near you may be having a medical emergency, call your local "
    "emergency number or go to the nearest emergency room immediately. "
    "Always consult a qualified, licensed healthcare professional for any "
    "real health concern."
)

# -----------------------------------------------------------------------
# Logo — a real inline SVG mark (rounded badge + caduceus/pulse motif),
# used in place of the emoji placeholder. Colour follows the app's
# blue -> indigo brand gradient so it matches the header/sidebar.
# -----------------------------------------------------------------------
LOGO_SVG = """
<svg width="100%" height="100%" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="MediGuide AI logo">
  <defs>
    <linearGradient id="mgBadge" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7"/>
      <stop offset="100%" stop-color="#4f46e5"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="62" height="62" rx="16" fill="url(#mgBadge)"/>
  <rect x="1" y="1" width="62" height="62" rx="16" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1.5"/>
  <path d="M20 34 L26 34 L29 24 L34 44 L38 34 L44 34"
        fill="none" stroke="#ffffff" stroke-width="3.2"
        stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="32" cy="16" r="3.2" fill="#ffffff"/>
  <path d="M32 19.5 V27" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M25 20 C27 22, 29 22.5, 32 22.5 C35 22.5, 37 22, 39 20"
        fill="none" stroke="#e0f2fe" stroke-width="1.6" stroke-linecap="round" opacity="0.85"/>
</svg>
"""

def logo_html(size_px: int = 46) -> str:
    """Return the logo SVG wrapped so it can be dropped straight into st.markdown."""
    return f'<div style="width:{size_px}px;height:{size_px}px;">{LOGO_SVG}</div>'
