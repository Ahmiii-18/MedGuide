"""
src/case_bank.py
-----------------
Static bank of USMLE-style progressive clinical vignettes for the
"Practice Cases" mode: each case starts with minimal symptoms, the
learner answers an MCQ, then more symptoms are revealed and the
question sharpens, step by step, ending on the case's true diagnosis.

This is a teaching aid layered on top of the main AI assessment tool -
it uses a fixed local case bank rather than calling the API, so it
works instantly and offline.
"""

CASE_BANK = [
    {
        "id": "case_chest",
        "title": "A 54-year-old with chest discomfort",
        "specialty": "Cardiology",
        "steps": [
            {
                "add_symptoms": ["Mild central chest discomfort that started this morning"],
                "question": "Based only on this, what's the single most useful next question to ask?",
                "options": [
                    "Does the discomfort radiate to the arm/jaw, and what brings it on?",
                    "What did they eat for breakfast?",
                    "Do they have a rash anywhere?",
                    "Have they travelled recently?",
                ],
                "correct_index": 0,
                "explanation": "Radiation, triggers, and relieving factors are the highest-yield "
                               "discriminators between cardiac and non-cardiac chest pain at this stage.",
            },
            {
                "add_symptoms": ["Pain radiates to the left jaw", "Worse on exertion, eases with rest",
                                  "Associated sweating and mild nausea"],
                "question": "With this additional history, what is the LEADING working diagnosis?",
                "options": [
                    "Acute coronary syndrome",
                    "Gastro-oesophageal reflux",
                    "Costochondritis",
                    "Generalized anxiety",
                ],
                "correct_index": 0,
                "explanation": "Exertional, radiating pain with diaphoresis and nausea is the classic "
                               "pattern for cardiac ischemia and should be treated as ACS until proven otherwise.",
            },
            {
                "add_symptoms": ["BP 150/95, HR 104", "ECG shows ST depression in leads V4-V6"],
                "question": "Given the vitals and ECG, what is the MOST appropriate immediate step?",
                "options": [
                    "Emergency referral for ACS work-up (troponin, cardiology, aspirin per protocol)",
                    "Reassure and discharge with antacids",
                    "Book a routine outpatient cardiology visit in 2 weeks",
                    "Prescribe a muscle relaxant and review in a week",
                ],
                "correct_index": 0,
                "explanation": "ST depression plus this history is a red flag: this needs emergency-level "
                               "work-up, not a routine or reassurance-only pathway.",
            },
        ],
    },
    {
        "id": "case_headache",
        "title": "A 29-year-old with a headache",
        "specialty": "Neurology",
        "steps": [
            {
                "add_symptoms": ["Sudden, severe headache that started 20 minutes ago"],
                "question": "What historical detail matters MOST right now?",
                "options": [
                    "Whether this is the 'worst headache of their life' and how suddenly it peaked",
                    "Their favourite pain medication",
                    "Whether they have insurance",
                    "What time they usually wake up",
                ],
                "correct_index": 0,
                "explanation": "A 'thunderclap' onset (peak intensity within seconds to minutes) is the "
                               "single most important red-flag feature for headache.",
            },
            {
                "add_symptoms": ["Neck stiffness", "Sensitivity to light", "No history of migraines"],
                "question": "What is the LEADING differential now?",
                "options": [
                    "Subarachnoid haemorrhage / meningitis until proven otherwise",
                    "Tension headache",
                    "Sinus congestion",
                    "Dehydration",
                ],
                "correct_index": 0,
                "explanation": "Thunderclap onset with meningismus (neck stiffness, photophobia) demands "
                               "urgent imaging +/- lumbar puncture to rule out haemorrhage or infection.",
            },
            {
                "add_symptoms": ["Brief loss of consciousness at onset", "BP 168/100"],
                "question": "What is the MOST appropriate next step?",
                "options": [
                    "Emergency CT head (non-contrast) and emergency department referral",
                    "Over-the-counter analgesia and rest at home",
                    "Routine neurology outpatient booking",
                    "Physiotherapy referral for neck stiffness",
                ],
                "correct_index": 0,
                "explanation": "Loss of consciousness with thunderclap headache and hypertension is an "
                               "emergency presentation requiring immediate imaging.",
            },
        ],
    },
    {
        "id": "case_fever",
        "title": "An 8-year-old with fever",
        "specialty": "Paediatrics / Infectious Disease",
        "steps": [
            {
                "add_symptoms": ["Fever of 38.9°C for 1 day", "Mild sore throat"],
                "question": "At this early stage, what's the best next question?",
                "options": [
                    "Any rash, difficulty breathing, or reduced fluid intake?",
                    "Has the child had a haircut recently?",
                    "What's the child's favourite food?",
                    "Do they own a pet?",
                ],
                "correct_index": 0,
                "explanation": "Rash, breathing difficulty, and hydration status are the key screening "
                               "questions for a febrile child to catch anything serious early.",
            },
            {
                "add_symptoms": ["Fine sandpaper-like rash on the trunk", "Red, swollen tongue ('strawberry tongue')"],
                "question": "What is the LEADING diagnosis now?",
                "options": [
                    "Scarlet fever (Group A Streptococcus)",
                    "Chickenpox",
                    "Contact dermatitis",
                    "Heat rash",
                ],
                "correct_index": 0,
                "explanation": "A sandpaper rash plus strawberry tongue with sore throat and fever is "
                               "the classic triad for scarlet fever.",
            },
            {
                "add_symptoms": ["Child is drinking fluids well, alert and playful between fevers"],
                "question": "Given the child is otherwise well, what's the MOST appropriate plan?",
                "options": [
                    "Start an appropriate antibiotic course and review in 24-48 hours",
                    "Admit immediately to intensive care",
                    "No treatment needed at all",
                    "Refer for surgery",
                ],
                "correct_index": 0,
                "explanation": "Scarlet fever is treated with antibiotics to reduce complications and "
                               "shorten the infectious period, with safety-netting to review if the child worsens.",
            },
        ],
    },
]


def list_cases():
    return [(c["id"], c["title"], c["specialty"]) for c in CASE_BANK]


def get_case(case_id: str):
    for c in CASE_BANK:
        if c["id"] == case_id:
            return c
    return None
