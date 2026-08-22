"""
src/utils.py
-------------
Safe JSON parsing (never crashes the app on malformed model output),
a guaranteed-shape fallback assessment, and small formatting helpers.
"""

import json
import re

from src.config import MIN_DIFFERENTIALS

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_code_fences(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text or "").strip()


def _generic_filler_condition(n: int) -> dict:
    """A clearly-labelled generic differential used only to pad the list
    up to MIN_DIFFERENTIALS if the model returns fewer than required."""
    return {
        "name": f"Additional generalist differential #{n}",
        "specialty": "General Medicine",
        "likelihood": "Low",
        "reason": "Insufficient model output to generate a specific differential here; "
                  "kept as a placeholder so at least the minimum number of "
                  "differentials is always shown for review.",
        "key_features": "N/A - regenerate the assessment for a fuller differential.",
        "treatment": "N/A - re-run the assessment for a specific recommendation.",
        "treatment_reason": "N/A",
    }


def empty_assessment_fallback() -> dict:
    """A safe, fully-shaped assessment used when parsing fails entirely."""
    return {
        "summary": "The assessment could not be generated. Please try again.",
        "possible_conditions": [_generic_filler_condition(i) for i in range(1, MIN_DIFFERENTIALS + 1)],
        "diagnostic_confidence": "Low",
        "clarifying_questions": [
            "Please re-submit the form with more detail so a working diagnosis can be proposed."
        ],
        "diagnostic_narrowing_questions": [],
        "urgency_level": "MEDIUM",
        "recommended_next_steps": ["Re-run the assessment; if symptoms are severe, seek medical care."],
        "warning_signs": [],
    }


def safe_parse_assessment(raw_output: str):
    """
    Parse the model's JSON output defensively.
    Returns (assessment_dict, error_message_or_None).
    Guarantees possible_conditions has >= MIN_DIFFERENTIALS entries.
    """
    if not raw_output or not raw_output.strip():
        return empty_assessment_fallback(), "⚠️ Empty response from the model."

    cleaned = _strip_code_fences(raw_output)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to salvage the largest {...} block in the text.
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return empty_assessment_fallback(), (
                    "⚠️ Could not parse the model's JSON output. Showing a safe "
                    "placeholder assessment instead. Raw output is available below."
                )
        else:
            return empty_assessment_fallback(), (
                "⚠️ Could not parse the model's JSON output. Showing a safe "
                "placeholder assessment instead. Raw output is available below."
            )

    if not isinstance(data, dict):
        return empty_assessment_fallback(), "⚠️ Unexpected JSON shape from the model."

    # --- Defensive defaults for every expected key ---
    data.setdefault("summary", "")
    data.setdefault("possible_conditions", [])
    data.setdefault("diagnostic_confidence", "Moderate")
    data.setdefault("clarifying_questions", [])
    data.setdefault("diagnostic_narrowing_questions", [])
    data.setdefault("urgency_level", "MEDIUM")
    data.setdefault("recommended_next_steps", [])
    data.setdefault("warning_signs", [])

    # --- Enforce the minimum differential-diagnosis count ---
    conditions = data.get("possible_conditions") or []
    if not isinstance(conditions, list):
        conditions = []
    if len(conditions) < MIN_DIFFERENTIALS:
        needed = MIN_DIFFERENTIALS - len(conditions)
        conditions = conditions + [_generic_filler_condition(i) for i in range(1, needed + 1)]
    data["possible_conditions"] = conditions

    return data, None


def format_symptoms(selected: list, free_text: str) -> str:
    parts = list(selected) if selected else []
    if free_text and free_text.strip():
        parts.extend([p.strip() for p in free_text.split(",") if p.strip()])
    return ", ".join(parts) if parts else "None reported"


def urgency_to_streamlit_kind(urgency: str) -> str:
    return {
        "LOW": "success",
        "MEDIUM": "info",
        "HIGH": "warning",
        "EMERGENCY": "error",
    }.get((urgency or "").upper(), "info")
