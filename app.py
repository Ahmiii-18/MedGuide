"""
app.py
------
MediGuide AI - Modern Clinical UI & Assessment Engine.

Features:
- Real inline-SVG brand logo (header + sidebar)
- High-contrast dark theme (fixed invisible-text bug)
- Interactive Intake with History of Presenting Complaint (HOP)
- Multi-specialty Differential Diagnosis (always >= 5 differentials),
  each with a treatment suggestion + clinical rationale
- Tick-to-confirm clarifying questions whenever the AI's confidence
  in the leading diagnosis is Moderate/Low
- Targeted Single-Diagnosis Narrowing Protocol
- Real-Time Token Streaming Narrative Engine
- MCQ-style progressive clinical-vignette practice mode
"""

import json
import time
import streamlit as st

from src.config import (
    GENDER_OPTIONS, DURATION_OPTIONS, COMMON_SYMPTOMS,
    LANGUAGE_OPTIONS, AVAILABLE_MODELS, DEFAULT_MODEL,
    DISCLAIMER_SHORT, DISCLAIMER_LONG, URGENCY_COLOURS, OPENAI_API_KEY,
    MIN_DIFFERENTIALS, logo_html,
)
from src.cache_manager import configure_cache, CACHE_EXPLANATIONS
from src.chains import build_llm, build_assessment_chain, run_assessment, stream_narrative
from src.utils import safe_parse_assessment, empty_assessment_fallback, format_symptoms, urgency_to_streamlit_kind
from src.case_bank import list_cases, get_case

# -----------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="MediGuide AI | Clinical Decision Support System",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------
# STYLING - high-contrast dark theme
# (Broad `.stApp *` colour fallback fixes text disappearing against the
#  dark background; specific inline `style="color:...`" rules elsewhere
#  still win because inline styles always beat these class rules.)
# -----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    :root {
        --mg-bg: #faf9f6;
        --mg-bg-soft: #f2f0ea;
        --mg-text: #2b2f38;
        --mg-text-muted: #6b7280;
        --mg-border: rgba(43, 47, 56, 0.12);
        --mg-accent: #0284c7;
        --mg-accent-2: #4f46e5;
    }

    /* Main Background & Typography (off-white, not stark white) */
    .stApp {
        background-color: var(--mg-bg);
        color: var(--mg-text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Safety net: force readable colour on any un-styled text so nothing
       disappears against the background. Elements with their own inline
       colour (badges, headings, etc.) are unaffected because inline style wins. */
    .stApp, .stApp p, .stApp span, .stApp li, .stApp label,
    .stApp div, .stApp small, .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp h5, .stApp h6 {
        color: var(--mg-text);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--mg-bg-soft);
        border-right: 1px solid var(--mg-border);
    }
    section[data-testid="stSidebar"] * { color: var(--mg-text); }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
        color: var(--mg-text-muted) !important;
    }

    /* Widget labels (selectbox/slider/text input/textarea/radio/checkbox) */
    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] label {
        color: var(--mg-text) !important;
        font-weight: 500 !important;
    }

    /* Text inputs / text areas */
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    textarea, input[type="text"] {
        color: var(--mg-text) !important;
        background-color: #ffffff !important;
        border-color: var(--mg-border) !important;
    }
    ::placeholder { color: #9aa1ad !important; opacity: 1 !important; }

    /* Select / multiselect */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: var(--mg-border) !important;
        color: var(--mg-text) !important;
    }
    div[data-baseweb="select"] * { color: var(--mg-text) !important; }
    span[data-baseweb="tag"] {
        color: #ffffff !important;
        background-color: #0284c7 !important;
    }
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid var(--mg-border);
    }
    ul[role="listbox"] li { color: var(--mg-text) !important; }

    /* Slider */
    div[data-testid="stSlider"] label, div[data-testid="stSlider"] div {
        color: var(--mg-text) !important;
    }

    /* Checkbox / radio labels */
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        color: var(--mg-text) !important;
    }

    /* Metric */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: var(--mg-text) !important;
    }

    /* Expander */
    div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid var(--mg-border) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary p {
        background-color: #ffffff !important;
        color: var(--mg-text) !important;
    }

    /* Caption */
    .stCaption, small { color: var(--mg-text-muted) !important; }

    /* Top Dashboard Header Banner */
    .modern-header {
        position: relative;
        background: linear-gradient(135deg, #0f2942 0%, #14406b 100%);
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.10);
        display: flex;
        align-items: center;
        gap: 2rem;
        overflow: hidden;
    }

    .header-logo {
        position: relative;
        z-index: 1;
        width: 78px;
        height: 78px;
        background: rgba(255, 255, 255, 0.10);
        padding: 0.5rem;
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .header-content { position: relative; z-index: 1; }

    .modern-header * {
    color: #ffffff !important;
}

.header-content h1 {
    color: #ffffff !important;
    font-size: 2.3rem !important;
    margin: 0 !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}

.header-content p {
    color: #f1f5f9 !important;
    font-size: 1.02rem !important;
    margin: 0.4rem 0 0 0 !important;
    font-weight: 400 !important;
    max-width: 680px;
}
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 0.9rem;
        background: rgba(255, 255, 255, 0.12);
        color: #a7f3d0 !important;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.2);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .status-badge * { color: #a7f3d0 !important; }

    .status-dot {
        width: 8px; height: 8px;
        background-color: #34d399;
        border-radius: 50%;
    }

    /* Cards */
    .glass-card {
        background: #ffffff;
        border: 1px solid var(--mg-border);
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }
    .glass-card, .glass-card * { color: var(--mg-text); }

    /* Input Form Custom Frame */
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid var(--mg-border);
        border-radius: 18px;
        padding: 1.8rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }

    /* Primary Interactive Buttons - flat, no glow/shine */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.3rem !important;
        transition: background-color 0.15s ease !important;
        box-shadow: none !important;
    }
    .stButton > button *, div[data-testid="stFormSubmitButton"] > button * { color: #ffffff !important; }

    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: #0369a1 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .stButton > button:active, div[data-testid="stFormSubmitButton"] > button:active {
        background: #075985 !important;
        box-shadow: none !important;
    }
    .stButton > button:focus, div[data-testid="stFormSubmitButton"] > button:focus {
        box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.35) !important;
    }

    /* Specialty / status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-cardiology { background: #fef2f2; color: #b91c1c !important; border: 1px solid #fca5a5; }
    .badge-surgery { background: #fffbeb; color: #92400e !important; border: 1px solid #fcd34d; }
    .badge-neurology { background: #faf5ff; color: #6b21a8 !important; border: 1px solid #d8b4fe; }
    .badge-general { background: #f0f9ff; color: #075985 !important; border: 1px solid #7dd3fc; }
    .badge-high { background: #fef2f2; color: #b91c1c !important; border: 1px solid #fca5a5; }
    .badge-moderate { background: #fffbeb; color: #92400e !important; border: 1px solid #fcd34d; }
    .badge-low { background: #f0fdf4; color: #166534 !important; border: 1px solid #86efac; }
    .badge * { color: inherit !important; }

    /* Confidence banner */
    .confidence-banner-high { border-left: 6px solid #22c55e; }
    .confidence-banner-moderate { border-left: 6px solid #f59e0b; }
    .confidence-banner-low { border-left: 6px solid #ef4444; }

    /* Custom Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: #ffffff;
        border-radius: 10px;
        color: var(--mg-text-muted) !important;
        font-size: 0.88rem;
        font-weight: 500;
        border: 1px solid var(--mg-border);
    }
    .stTabs [data-baseweb="tab"] p { color: inherit !important; }
    .stTabs [aria-selected="true"] {
        background: #e0f2fe !important;
        color: #0369a1 !important;
        border: 1px solid #7dd3fc !important;
    }
    .stTabs [aria-selected="true"] p { color: #0369a1 !important; }

    /* Header Bar Cleanup */
    header[data-testid="stHeader"] { background: var(--mg-bg); }

    /* Alerts stay readable regardless of theme */
    div[data-testid="stAlert"] p { color: inherit !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------
# SIDEBAR CONTROL PANEL
# -----------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.7rem; margin-bottom:0.2rem;">
            <div style="width:38px;height:38px;">{logo_html(38)}</div>
            <div style="font-size:1.3rem; font-weight:800; color:#0369a1;">MediGuide AI</div>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Clinical Assessment Engine v3.0 - Educational Prototype")

    st.markdown("""
        <div class="glass-card" style="padding: 0.85rem; font-size: 0.82rem; margin-top: 0.5rem;">
            <b>Knowledge Standard:</b> Cross-referenced against Oxford, Harrison's, Robbins, and Davidson's medical guidelines.
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### ⚙️ Engine Settings")

    if not OPENAI_API_KEY:
        st.error("⚠️ OPENAI_API_KEY missing! Add it to `.env` (never commit real keys).")

    model_name = st.selectbox("LLM Architecture", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(DEFAULT_MODEL))
    temperature = st.slider("Diagnostic Creativity", 0.0, 1.0, 0.2, 0.05)
    cache_mode = st.selectbox("Cache Layer", ["None", "In-Memory", "SQLite"], index=1)
    cache_status = configure_cache(cache_mode)
    st.caption(f"💾 {cache_status}")

    st.divider()
    answer_language = st.selectbox("Translation Language", LANGUAGE_OPTIONS, index=0)

    st.divider()
    st.markdown(f'<div style="font-size: 0.78rem; color: var(--mg-text-muted);">{DISCLAIMER_SHORT}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------
# TOP DASHBOARD HEADER
# -----------------------------------------------------------------------
st.markdown(f"""
    <div class="modern-header">
        <div class="header-logo">{logo_html(56)}</div>
        <div class="header-content">
            <h1>MediGuide Clinical Engine</h1>
            <p>Multi-specialty diagnostic reasoning across Cardiology, Surgery, Neurology, and Internal Medicine.</p>
            <div class="status-badge">
                <div class="status-dot"></div>
                AI Diagnostic Engine Active
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Prominent, always-visible educational disclaimer (main area, not just sidebar)
st.warning(
    "🎓 **Educational prototype only.** MediGuide AI is **not a real doctor** and does not "
    "provide a real diagnosis. If this may be a medical emergency, call your local "
    "emergency number or go to the nearest emergency room immediately."
)

# -----------------------------------------------------------------------
# MCQ PRACTICE MODE - progressive clinical vignettes (independent of the
# main assessment engine; uses a local case bank, no API call needed)
# -----------------------------------------------------------------------
with st.expander("🎓 Practice Cases - Progressive Clinical Vignettes (MCQ Mode)", expanded=False):
    st.markdown(
        "Work through a case the way it unfolds in real life: you start with **minimal "
        "symptoms**, answer a multiple-choice question, then more findings are revealed "
        "and the question sharpens - just like stepwise clinical-reasoning exam questions."
    )

    cases = list_cases()
    case_labels = [f"{title} — {spec}" for _, title, spec in cases]
    case_ids = [cid for cid, _, _ in cases]

    chosen_label = st.selectbox("Choose a practice case", case_labels, key="practice_case_select")
    chosen_id = case_ids[case_labels.index(chosen_label)]

    if st.button("▶️ Start / Restart This Case", key="practice_start_btn"):
        st.session_state["practice_case_id"] = chosen_id
        st.session_state["practice_step"] = 0
        st.session_state.pop("practice_feedback", None)

    active_id = st.session_state.get("practice_case_id")
    if active_id:
        case = get_case(active_id)
        step_idx = st.session_state.get("practice_step", 0)

        if case and step_idx < len(case["steps"]):
            st.markdown(f"#### {case['title']}")

            # Accumulate all symptoms revealed so far (this step and earlier ones)
            revealed_symptoms = []
            for s in case["steps"][: step_idx + 1]:
                revealed_symptoms.extend(s["add_symptoms"])

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Step {step_idx + 1} of {len(case['steps'])} — Symptoms so far:**")
            for sym in revealed_symptoms:
                st.markdown(f"- {sym}")
            st.markdown("---")

            step = case["steps"][step_idx]
            answer_key = f"practice_answer_{case['id']}_{step_idx}"
            choice = st.radio(step["question"], step["options"], key=answer_key, index=None)

            col_a, col_b = st.columns([1, 1])
            with col_a:
                check_clicked = st.button("Check Answer", key=f"check_{case['id']}_{step_idx}")
            with col_b:
                next_disabled = f"feedback_{case['id']}_{step_idx}" not in st.session_state
                next_clicked = st.button(
                    "Next ➜ Reveal More Findings" if step_idx < len(case["steps"]) - 1 else "Finish Case",
                    key=f"next_{case['id']}_{step_idx}",
                    disabled=next_disabled,
                )

            if check_clicked:
                if choice is None:
                    st.warning("Pick an option first.")
                else:
                    correct = step["options"][step["correct_index"]]
                    is_correct = choice == correct
                    st.session_state[f"feedback_{case['id']}_{step_idx}"] = True
                    if is_correct:
                        st.success(f"✅ Correct. {step['explanation']}")
                    else:
                        st.error(f"❌ Not quite. The best answer was: **{correct}**\n\n{step['explanation']}")

            if next_clicked:
                st.session_state["practice_step"] = step_idx + 1
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
        elif case:
            st.success("🎉 Case complete! Choose another case above to keep practicing.")
    else:
        st.caption("Select a case and click **Start** to begin.")

# -----------------------------------------------------------------------
# PATIENT INTAKE FORM
# -----------------------------------------------------------------------
with st.form("clinical_intake_form"):
    st.markdown("#### 👤 Patient Demographics & Baseline")
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.text_input("Age", placeholder="e.g. 58")
    with c2:
        gender = st.selectbox("Gender", GENDER_OPTIONS)
    with c3:
        duration = st.selectbox("Symptom Duration", DURATION_OPTIONS)

    st.markdown("#### 🩺 Presenting Symptoms")
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        symptoms_selected = st.multiselect("Primary Symptoms", COMMON_SYMPTOMS)
    with col_s2:
        symptoms_free_text = st.text_input("Unlisted / Free-text Symptoms", placeholder="e.g. diaphoresis, jaw pain")

    severity = st.slider("Pain / Distress Severity (1 = Mild, 10 = Maximum)", 1, 10, 5)

    st.markdown("#### 📜 History of Presenting Complaint (HOP)")
    hop = st.text_area(
        "Narrative Symptom Progression (SOCRATES / OPQRST Framework)",
        placeholder=(
            "Detail narrative details:\n"
            "• Onset & Quality (e.g. sudden crushing, gradual dull ache)\n"
            "• Radiation & Triggers (e.g. radiates to jaw/shoulder, worse on exertion)\n"
            "• Associated Features & Relief (e.g. diaphoresis, nausea, relief with rest)"
        ),
        height=120,
    )

    st.markdown("#### 📋 Medical History & Profile")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        existing_conditions = st.text_area("Pre-existing Conditions", placeholder="e.g. HTN, T2DM, Asthma", height=70)
    with col_m2:
        medications = st.text_area("Current Active Medications", placeholder="e.g. Aspirin, Metformin, Amlodipine", height=70)

    notes = st.text_input("Vitals / Clinical Notes", placeholder="e.g. BP 155/95, HR 104, SpO2 95%")

    submitted = st.form_submit_button("🚀 Run Multi-Domain Assessment", use_container_width=True)

# -----------------------------------------------------------------------
# FORM EXECUTION & CHAIN CALL
# -----------------------------------------------------------------------
if submitted:
    symptoms_str = format_symptoms(symptoms_selected, symptoms_free_text)

    if symptoms_str == "None reported" and not hop.strip():
        st.warning("⚠️ Please select symptoms or provide a History of Presenting Complaint (HOP).")
    elif not age.strip():
        st.warning("⚠️ Please specify patient age.")
    elif not OPENAI_API_KEY:
        st.error("❌ OpenAI API key missing. Configure your environment variables.")
    else:
        chain_inputs = {
            "age": age.strip(),
            "gender": gender,
            "symptoms": symptoms_str,
            "duration": duration,
            "severity": str(severity),
            "hop": hop.strip() or "None reported",
            "existing_conditions": existing_conditions.strip() or "None reported",
            "medications": medications.strip() or "None reported",
            "notes": notes.strip() or "None",
            "answer_language": answer_language,
        }

        with st.spinner("🧠 Synthesizing diagnostic rationale across medical disciplines..."):
            start_time = time.time()
            llm = build_llm(model_name, temperature=temperature, streaming=False)
            chain = build_assessment_chain(llm)
            raw_output = run_assessment(chain, chain_inputs)
            elapsed = time.time() - start_time

        assessment, error = safe_parse_assessment(raw_output)
        st.caption(f"⚡ Synthesis completed in {elapsed:.2f}s | Engine: {model_name} | Cache: {cache_mode}")

        if error:
            st.error(error)
            with st.expander("Raw model output"):
                st.code(raw_output or "(empty)")

        st.session_state["assessment"] = assessment
        st.session_state["chain_inputs"] = chain_inputs
        st.session_state["model_name"] = model_name

# -----------------------------------------------------------------------
# RESULTS DASHBOARD
# -----------------------------------------------------------------------
if "assessment" in st.session_state:
    assessment = st.session_state["assessment"]
    chain_inputs = st.session_state["chain_inputs"]
    model_name = st.session_state["model_name"]
    urgency = assessment.get("urgency_level", "MEDIUM")
    confidence = assessment.get("diagnostic_confidence", "Moderate")

    st.divider()

    # Clinical Urgency Header
    urgency_color = URGENCY_COLOURS.get(urgency, "🟡")
    st.markdown(f"""
        <div class="glass-card" style="border-left: 6px solid #38bdf8;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.6rem;">
                <div>
                    <span style="font-size: 0.85rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">Evaluation Status</span>
                    <h2 style="margin: 0; color: #1e293b;">{urgency_color} {urgency} URGENCY</h2>
                </div>
                <div>
                    <span class="badge badge-cardiology" style="font-size: 0.9rem; padding: 0.45rem 0.9rem;">Reported Severity: {chain_inputs['severity']}/10</span>
                    <span class="badge badge-general" style="font-size: 0.9rem; padding: 0.45rem 0.9rem;">Diagnostic Confidence: {confidence}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # NOTE: order per current requirements -> Differentials, Narrowing,
    # Live Stream, then Clinical Summary (4th), then Next Steps, then Red Flags.
    tab_differential, tab_narrowing, tab_stream, tab_summary, tab_next, tab_warnings = st.tabs([
        "🩺 Multi-Domain Differentials",
        "🎯 Narrowing Protocol",
        "⚡ Live Narrative Stream",
        "📋 Clinical Summary",
        "🧪 Workup & Next Steps",
        "⚠️ Red Flags",
    ])

    # Tab 1: Differentials (>= MIN_DIFFERENTIALS, each with treatment + reason)
    with tab_differential:
        st.markdown(f"#### Multi-Specialty Differential Diagnoses (minimum {MIN_DIFFERENTIALS} shown)")
        conditions = assessment.get("possible_conditions", [])

        for idx, cond in enumerate(conditions, 1):
            spec = cond.get("specialty", "General Medicine")
            spec_badge = "badge-cardiology" if "Cardio" in spec else "badge-surgery" if "Surg" in spec else "badge-neurology" if "Neuro" in spec else "badge-general"
            likelihood = cond.get("likelihood", "Moderate").lower()
            like_badge = "badge-high" if "high" in likelihood else "badge-low" if "low" in likelihood else "badge-moderate"

            st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.4rem;">
                        <h3 style="margin: 0; font-size: 1.15rem; color: #1e293b;">{idx}. {cond.get('name', 'Condition')}</h3>
                        <div>
                            <span class="badge {spec_badge}">{spec}</span>
                            <span class="badge {like_badge}">Likelihood: {cond.get('likelihood', 'N/A')}</span>
                        </div>
                    </div>
                    <p style="color: #374151; font-size: 0.92rem; margin-bottom: 0.5rem;"><b>Pathophysiology:</b> {cond.get('reason', '')}</p>
                    <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.6rem;"><b>Key Features:</b> {cond.get('key_features', 'N/A')}</div>
                    <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 0.7rem 0.9rem;">
                        <div style="font-size: 0.88rem; color: #075985;"><b>💊 Suggested Treatment:</b> {cond.get('treatment', 'N/A')}</div>
                        <div style="font-size: 0.82rem; color: #475569; margin-top: 0.3rem;"><b>Why:</b> {cond.get('treatment_reason', 'N/A')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Tick-to-confirm clarifying questions whenever the AI isn't confident
        if confidence.strip().lower() in ("moderate", "low"):
            clarifying_qs = assessment.get("clarifying_questions", [])
            if clarifying_qs:
                st.markdown('<div class="glass-card confidence-banner-moderate">', unsafe_allow_html=True)
                st.markdown(
                    f"#### 🔎 Confidence is **{confidence}** — confirm the leading diagnosis\n"
                    "The AI has still committed to a working diagnosis above, but wants these "
                    "points checked. Tick each one off as you confirm it with the patient/records:"
                )
                ticked = 0
                for q_idx, q in enumerate(clarifying_qs, 1):
                    checked = st.checkbox(q, key=f"clarify_{q_idx}_{hash(q) % 10_000}")
                    if checked:
                        ticked += 1
                st.progress(ticked / max(len(clarifying_qs), 1))
                st.caption(f"{ticked} of {len(clarifying_qs)} confirmation points checked.")
                st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Narrowing Protocol
    with tab_narrowing:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Diagnostic Narrowing Protocol")
        st.markdown("Answer these discriminating clinical questions to isolate **one primary diagnosis**:")

        questions = assessment.get("diagnostic_narrowing_questions", [])
        for q_idx, q in enumerate(questions, 1):
            st.markdown(f"**Q{q_idx}:** {q}")

        st.markdown("---")
        with st.form("narrowing_refinement_form"):
            refine_answers = st.text_area("Clinical Clarifications & Observations", placeholder="Provide responses to the discriminating questions above...")
            submit_refine = st.form_submit_button("Refine & Isolate Primary Diagnosis", use_container_width=True)

        if submit_refine:
            if not refine_answers.strip():
                st.warning("Please enter observations to narrow the diagnosis.")
            else:
                with st.spinner("Narrowing to primary diagnosis..."):
                    refine_prompt = f"""
                    Patient History: {json.dumps(chain_inputs)}
                    Differentials: {json.dumps(assessment.get("possible_conditions", []))}
                    Clarifying Responses: {refine_answers.strip()}

                    Return ONLY JSON:
                    {{
                        "primary_diagnosis": {{
                            "name": "Primary Diagnosis Name",
                            "specialty": "Domain",
                            "confidence": "High / Moderate",
                            "justification": "Pathophysiological justification.",
                            "ruled_out": "Reasoning for excluding competing differentials.",
                            "treatment": "Recommended treatment for this confirmed diagnosis",
                            "treatment_reason": "Why this treatment is appropriate"
                        }}
                    }}
                    """
                    refine_llm = build_llm(model_name, temperature=0.1, streaming=False)
                    ref_raw = refine_llm.invoke(refine_prompt).content
                    ref_data, _ = safe_parse_assessment(ref_raw)

                primary = ref_data.get("primary_diagnosis", {}) if isinstance(ref_data, dict) else {}
                if not primary:
                    primary = {}
                st.markdown(f"""
                    <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 12px; padding: 1.2rem; margin-top: 1rem;">
                        <h3 style="color: #15803d; margin: 0;">🏆 Primary Working Diagnosis: {primary.get('name', 'Resolved Diagnosis')}</h3>
                        <p style="margin: 0.4rem 0; color: #1e293b;"><b>Specialty Domain:</b> {primary.get('specialty', 'Internal Medicine')} | <b>Confidence:</b> {primary.get('confidence', 'High')}</p>
                        <p style="font-size: 0.92rem; color: #374151;"><b>Clinical Rationale:</b> {primary.get('justification', '')}</p>
                        <p style="font-size: 0.85rem; color: #6b7280;"><b>Excluded Differentials:</b> {primary.get('ruled_out', '')}</p>
                        <p style="font-size: 0.88rem; color: #075985;"><b>💊 Treatment:</b> {primary.get('treatment', 'N/A')}</p>
                        <p style="font-size: 0.82rem; color: #6b7280;"><b>Why:</b> {primary.get('treatment_reason', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: Live Narrative Stream
    with tab_stream:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Real-Time Narrative Explanation Stream")
        st.caption("Streams token-by-token patient explanation via LangChain `.stream()` and Streamlit `st.write_stream()`.")

        if st.button("▶️ Start Live Narrative Stream"):
            streaming_llm = build_llm(model_name, streaming=True)
            stream_inputs = dict(chain_inputs)
            stream_inputs["structured_summary"] = json.dumps(assessment)

            st.write_stream(stream_narrative(streaming_llm, stream_inputs))
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 4: Clinical Summary (moved here, after the live stream)
    with tab_summary:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📜 Case Presentation Summary")
        st.write(assessment.get("summary", ""))
        st.markdown("---")
        st.markdown(f"**History of Presenting Complaint (HOP):**\n_{chain_inputs.get('hop', 'None reported')}_")
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 5: Recommended Workup
    with tab_next:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🧪 Recommended Workup & Investigations")
        for step in assessment.get("recommended_next_steps", []):
            st.markdown(f"• {step}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 6: Red Flags
    with tab_warnings:
        st.markdown('<div class="glass-card" style="border: 1px solid rgba(239, 68, 68, 0.4);">', unsafe_allow_html=True)
        st.markdown("<h4 style='color: #b91c1c;'>⚠️ Emergency Red Flag Warnings</h4>", unsafe_allow_html=True)
        for w in assessment.get("warning_signs", []):
            st.markdown(f"• <span style='color: #b91c1c;'>{w}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown(f'<div style="text-align: center; color: #97a3b6; font-size: 0.8rem; max-width: 900px; margin: 0 auto;">{DISCLAIMER_LONG}</div>', unsafe_allow_html=True)
