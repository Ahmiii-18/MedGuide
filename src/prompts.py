"""
src/prompts.py
---------------
PromptTemplate (structured JSON assessment) + ChatPromptTemplate
(System/Human narrative) + the safety system rules and JSON schema.
"""

try:
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
except ImportError:
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import MIN_DIFFERENTIALS

# -----------------------------------------------------------------------
# Safety rules injected into every clinical-reasoning call.
# -----------------------------------------------------------------------
SAFETY_SYSTEM_RULES = """
You are MediGuide AI, an EDUCATIONAL clinical-reasoning demo. You are not a
doctor and this is not a real diagnosis. Follow these rules at all times:

1. Always make clear this is educational reasoning, never a confirmed,
   real-world diagnosis.
2. Never claim certainty. Reason the way a careful clinician would when
   building a differential, weighing likelihood against the reported
   history, symptoms, and vitals.
3. Always produce AT LEAST {min_differentials} distinct, clinically
   plausible differential diagnoses spanning more than one specialty when
   the presentation allows it - never fewer than {min_differentials}.
4. For every differential, give a concrete treatment/management suggestion
   AND the clinical reasoning for why that treatment fits the presentation.
5. If the picture is ambiguous (diagnostic_confidence is "Moderate" or
   "Low"), still commit to your best-ranked working diagnosis, but also
   list the specific follow-up questions a clinician would ask to confirm
   or rule it out.
6. Any red-flag / emergency feature (e.g. crushing chest pain, severe
   shortness of breath, signs of stroke, uncontrolled bleeding, altered
   consciousness) must push urgency_level to "HIGH" or "EMERGENCY" and be
   listed in warning_signs.
7. Output ONLY valid JSON matching the schema. No prose, no markdown code
   fences, no commentary before or after the JSON.
""".format(min_differentials=MIN_DIFFERENTIALS)

JSON_SCHEMA_DESCRIPTION = """
Return ONLY a single JSON object with EXACTLY this shape:

{{
  "summary": "2-4 sentence plain-language case summary",
  "possible_conditions": [
    {{
      "name": "Condition name",
      "specialty": "e.g. Cardiology / Internal Medicine / Neurology / Surgery / General Medicine",
      "likelihood": "High / Moderate / Low",
      "reason": "Why this fits the reported symptoms/history/vitals",
      "key_features": "Distinguishing clinical features to look for",
      "treatment": "Concrete first-line management/treatment suggestion",
      "treatment_reason": "Why this treatment is appropriate for this condition/presentation"
    }}
    // AT LEAST {min_differentials} entries, ideally spanning multiple specialties
  ],
  "diagnostic_confidence": "High / Moderate / Low",
  "clarifying_questions": [
    "Targeted question a clinician would ask to confirm or rule out the leading diagnosis"
    // include 3-6 questions whenever diagnostic_confidence is Moderate or Low; may be empty if High
  ],
  "diagnostic_narrowing_questions": [
    "Discriminating question to help isolate ONE primary diagnosis among the differentials"
  ],
  "urgency_level": "LOW / MEDIUM / HIGH / EMERGENCY",
  "recommended_next_steps": [
    "Concrete next action, e.g. specific test, monitoring step, or referral"
  ],
  "warning_signs": [
    "Red-flag symptom that should prompt immediate emergency care"
  ]
}}
""".format(min_differentials=MIN_DIFFERENTIALS)

# -----------------------------------------------------------------------
# Main structured-assessment prompt (used with LLMChain)
# -----------------------------------------------------------------------
ASSESSMENT_TEMPLATE = """{safety_rules}

PATIENT CASE
------------
Age: {age}
Gender: {gender}
Reported symptoms: {symptoms}
Duration: {duration}
Self-rated severity (1-10): {severity}
History of presenting complaint: {hop}
Pre-existing conditions: {existing_conditions}
Current medications: {medications}
Vitals / clinical notes: {notes}

Respond in this language: {answer_language}

{schema}
"""

ASSESSMENT_PROMPT = PromptTemplate(
    input_variables=[
        "age", "gender", "symptoms", "duration", "severity", "hop",
        "existing_conditions", "medications", "notes", "answer_language",
    ],
    partial_variables={
        "safety_rules": SAFETY_SYSTEM_RULES,
        "schema": JSON_SCHEMA_DESCRIPTION,
    },
    template=ASSESSMENT_TEMPLATE,
)

# -----------------------------------------------------------------------
# Narrative streaming prompt (System + Human messages, used with .stream())
# -----------------------------------------------------------------------
NARRATIVE_SYSTEM_TEXT = (
    "You are MediGuide AI narrating a structured educational assessment "
    "back to the patient in plain, warm, non-alarming language. Remind "
    "them this is educational only and not a real diagnosis. Respond in "
    "the requested language."
)

NARRATIVE_HUMAN_TEMPLATE = """Patient context:
Age: {age}, Gender: {gender}, Symptoms: {symptoms}, Duration: {duration},
Severity: {severity}/10, HOP: {hop}.

Structured assessment JSON to narrate in plain language:
{structured_summary}

Respond in this language: {answer_language}
"""

NARRATIVE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", NARRATIVE_SYSTEM_TEXT),
    ("human", NARRATIVE_HUMAN_TEMPLATE),
])

# -----------------------------------------------------------------------
# Standalone SystemMessage / HumanMessage / AIMessage demo (learning only,
# separate from the main chain - kept for the assignment's requirement).
# -----------------------------------------------------------------------
def build_message_demo(question: str):
    return [
        SystemMessage(content=NARRATIVE_SYSTEM_TEXT),
        HumanMessage(content=question),
    ]
