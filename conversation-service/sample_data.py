"""
Sample Data and Usage Examples for Conversation Service

This module contains realistic medical conversation examples that demonstrate
the full capabilities of the Conversation Service.
"""

SAMPLE_CONVERSATIONS = {
    "migraine_case": {
        "conversation": {
            "patient_id_hash": "patient_hash_001",
            "doctor_id": "dr_alice_001"
        },
        "turns": [
            {
                "user_input": "Patient reports severe headache on left side, nausea, and sensitivity to light for 4 hours",
                "ai_response": """{
                    "diagnosis": "Migraine with aura",
                    "drugs": [
                        "Sumatriptan 100mg",
                        "Metoclopramide 10mg for nausea",
                        "Propranolol 40mg daily for prevention"
                    ],
                    "recommendations": [
                        "Rest in dark quiet room",
                        "Apply cold compress",
                        "Avoid triggers like bright lights",
                        "Stay hydrated"
                    ],
                    "labs": []
                }"""
            },
            {
                "user_input": "Headache improved with medication. Still some sensitivity to light. Nausea resolved.",
                "ai_response": "Diagnosis: Migraine in recovery phase. Continue Sumatriptan as needed. Prescribe preventive Propranolol 40mg daily. Recommend avoiding known triggers. Follow up if frequency increases. Order: MRI if frequency increases beyond 2 per week."
            },
            {
                "user_input": "Patient has had 3 migraines in past week. Concerned about increase in frequency.",
                "ai_response": """{
                    "diagnosis": "Chronic migraine disorder",
                    "drugs": [
                        "Botulinum toxin injections for prevention",
                        "Topiramate 25mg daily",
                        "Sumatriptan 100mg as needed",
                        "Amitriptyline 10mg at bedtime"
                    ],
                    "recommendations": [
                        "Refer to neurology specialist",
                        "Keep migraine diary",
                        "Identify and avoid triggers",
                        "Lifestyle modifications: exercise, sleep hygiene"
                    ],
                    "labs": [
                        "Brain MRI",
                        "Blood tests to rule out secondary causes"
                    ]
                }"""
            }
        ]
    },
    "diabetes_management": {
        "conversation": {
            "patient_id_hash": "patient_hash_002",
            "doctor_id": "dr_bob_002"
        },
        "turns": [
            {
                "user_input": "Type 2 diabetes patient. Recent HbA1c: 8.5%. Fasting glucose: 180 mg/dL. No current medication.",
                "ai_response": """{
                    "diagnosis": "Type 2 Diabetes Mellitus, poorly controlled",
                    "drugs": [
                        "Metformin 500mg twice daily",
                        "Glipizide 5mg twice daily with meals"
                    ],
                    "recommendations": [
                        "Dietary counseling with nutritionist",
                        "Start regular exercise: 150 min/week",
                        "Weight reduction goal: 5-10%",
                        "Regular glucose monitoring"
                    ],
                    "labs": [
                        "Repeat HbA1c in 3 months",
                        "Lipid panel",
                        "Kidney function tests",
                        "Urine microalbumin"
                    ]
                }"""
            },
            {
                "user_input": "3 months follow-up. HbA1c: 7.8%. Patient reports occasional hypoglycemic episodes. Weight down 4kg.",
                "ai_response": "Diagnosis: Type 2 Diabetes, improving but still suboptimal control. Reduce Glipizide to 2.5mg to prevent hypoglycemia. Continue Metformin 500mg twice daily. Patient showing good effort with lifestyle changes. Recommend diabetes education program. Order: Repeat HbA1c in 3 months. Continue glucose monitoring."
            }
        ]
    },
    "infection_case": {
        "conversation": {
            "patient_id_hash": "patient_hash_003",
            "doctor_id": "dr_carol_003"
        },
        "turns": [
            {
                "user_input": "Patient with fever (39.2C), cough, sore throat, and fatigue for 3 days",
                "ai_response": """{
                    "diagnosis": "Acute viral upper respiratory infection",
                    "drugs": [
                        "Paracetamol 500mg 6 hourly",
                        "Dextromethorphan for cough",
                        "Saline nasal spray"
                    ],
                    "recommendations": [
                        "Rest",
                        "Fluids",
                        "Use humidifier",
                        "Isolation for 48 hours"
                    ],
                    "labs": [
                        "Rapid flu test",
                        "Throat swab if symptoms persist"
                    ]
                }"""
            },
            {
                "user_input": "Fever persists. Now productive cough with yellowish sputum. Feeling worse.",
                "ai_response": """{
                    "diagnosis": "Bacterial secondary infection - likely acute bronchitis",
                    "drugs": [
                        "Amoxicillin-clavulanate 625mg three times daily",
                        "Salbutamol inhaler 2 puffs as needed",
                        "Guaifenesin for cough"
                    ],
                    "recommendations": [
                        "Continue rest",
                        "Monitor for signs of pneumonia",
                        "Return if fever doesn't improve in 48 hours",
                        "Do not return to work/school yet"
                    ],
                    "labs": [
                        "Chest X-ray if cough persists",
                        "Sputum culture if available"
                    ]
                }"""
            }
        ]
    }
}


def get_sample_conversation(case_name: str) -> dict:
    """Get a sample conversation by name"""
    return SAMPLE_CONVERSATIONS.get(case_name)


def get_all_samples() -> dict:
    """Get all sample conversations"""
    return SAMPLE_CONVERSATIONS


if __name__ == "__main__":
    import json
    
    print("Available Sample Conversations:")
    for name in SAMPLE_CONVERSATIONS.keys():
        conv = SAMPLE_CONVERSATIONS[name]
        num_turns = len(conv["turns"])
        print(f"  - {name}: {num_turns} turns")
    
    print("\nExample usage:")
    print("  from sample_data import get_sample_conversation")
    print("  conv = get_sample_conversation('migraine_case')")
    print("  print(conv)")
