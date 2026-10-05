"""Patient Education Tool - Creates patient-friendly education materials."""
from typing import Dict, Any, List


def create_education_material(diagnosis: str, patient_age: int, literacy_level: str) -> Dict[str, Any]:
    """
    Create tailored patient education materials.
    
    Args:
        diagnosis: Patient diagnosis
        patient_age: Patient age for age-appropriate content
        literacy_level: Reading level (high, moderate, basic)
    
    Returns:
        Patient education material with explanations and resources
    """
    
    education = {
        "diagnosis": "Heart Attack (Myocardial Infarction)",
        "reading_level": literacy_level,
        "content": {
            "what_happened": "Your heart muscle didn't get enough blood because a blood clot blocked an artery. This damaged part of your heart.",
            "why_it_happened": [
                "Fatty buildup (plaque) in your arteries over time",
                "A blood clot formed and blocked the artery",
                "Your heart couldn't pump blood normally"
            ],
            "warning_signs": [
                "Chest pain or pressure",
                "Pain in arm, jaw, neck, or back",
                "Shortness of breath",
                "Nausea or sweating"
            ],
            "recovery_timeline": {
                "first_week": "Rest and hospital care",
                "1_month": "Gradual activity increase, home recovery",
                "3_months": "Return to most activities",
                "6_12_months": "Full recovery for most people"
            }
        },
        "medications_explained": [
            {
                "name": "Aspirin",
                "purpose": "Prevents blood clots",
                "side_effects": "Stomach upset, bleeding",
                "do_not": "Skip doses without doctor approval"
            },
            {
                "name": "Beta-blocker",
                "purpose": "Protects heart, lowers heart rate and blood pressure",
                "side_effects": "Fatigue, low heart rate",
                "do_not": "Stop suddenly without doctor approval"
            }
        ],
        "lifestyle_changes": [
            "Heart-healthy diet (low salt, low fat)",
            "Gradual exercise program (cardiac rehab)",
            "Stop smoking",
            "Manage stress",
            "Control blood pressure and diabetes"
        ],
        "when_to_call_doctor": [
            "Chest pain returns",
            "Shortness of breath increases",
            "Signs of infection (fever, redness)",
            "Unusual bleeding"
        ],
        "resources": [
            {"type": "Booklet", "title": "Life After Heart Attack"},
            {"type": "Video", "title": "Cardiac Rehabilitation Guide"},
            {"type": "Support Group", "title": "Heart Attack Survivors Support"}
        ]
    }
    
    return education


def create_medication_reminder(medications: List[Dict[str, str]]) -> Dict[str, Any]:
    """Create medication reminder chart."""
    return {
        "format": "Simple daily chart",
        "medications": medications,
        "instructions": "Take each medication at the times marked with X"
    }
