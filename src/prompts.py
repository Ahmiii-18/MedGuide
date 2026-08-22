"""
src/prompts.py
--------------
Defines PromptTemplates using langchain_core.prompts.
"""
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

ASSESSMENT_PROMPT_TEMPLATE = """
You are MediGuide AI, an expert multi-specialty clinical decision support assistant.
Analyse the following patient information step-by-step and produce a JSON response adhering EXACTLY to the specified schema.

Patient Details:
- Age: {age}
- Gender: {gender}
- Primary Symptoms: {symptoms}
- Symptom Duration: {duration}
- Severity (1-10): {severity}
- History of Presenting Complaint (HOP): {hop}
- Pre-existing Conditions: {existing_conditions}
- Current Active Medications: {medications}
- Vitals / Clinical Notes: {notes}
- Preferred Response Language: {answer_language}

CRITICAL INSTRUCTIONS:
1. Provide at least 5 plausible differential diagnoses in `possible_conditions`.
2. For EACH condition, provide name, specialty, likelihood, pathophysiological reasoning, key features, suggested treatment, and rationale for treatment.
3. If diagnostic confidence is Moderate or Low, include a list of tick-to-confirm clarifying questions in `clarifying_questions`.
4. Return strictly VALID JSON without Markdown wrapper ticks (```json ... ```).

JSON Schema Required:
{{
  "summary": "Clinical summary of presentation",
  "urgency_level": "LOW | MEDIUM | HIGH | EMERGENCY",
  "diagnostic_confidence": "High | Moderate | Low",
  "possible_conditions": [
    {{
      "name": "Condition Name",
      "specialty": "Cardiology | Surgery | Neurology | Internal Medicine",
      "likelihood": "High | Moderate | Low",
      "reason": "Pathophysiological justification",
      "key_features": "Distinguishing signs/symptoms",
      "treatment": "First-line management / treatment suggestion",
      "treatment_reason": "Clinical rationale for treatment"
    }}
  ],
  "clarifying_questions": ["Question 1", "Question 2"],
  "diagnostic_narrowing_questions": ["Discriminating Question 1", "Discriminating Question 2"],
  "recommended_next_steps": ["Step 1", "Step 2"],
  "warning_signs": ["Red Flag 1", "Red Flag 2"]
}}
"""

ASSESSMENT_PROMPT = PromptTemplate(
    input_variables=[
        "age", "gender", "symptoms", "duration", "severity",
        "hop", "existing_conditions", "medications", "notes", "answer_language"
    ],
    template=ASSESSMENT_PROMPT_TEMPLATE,
)

NARRATIVE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an empathetic, clear medical communicator explaining a clinical assessment directly to a patient in language: {answer_language}."),
    ("human", "Explain the following clinical assessment structured data in friendly, easy-to-understand terms:\n\n{structured_summary}")
])