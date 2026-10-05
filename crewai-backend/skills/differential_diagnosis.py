"""Differential Diagnosis Tool - Analyzes symptoms and generates DDx."""
from typing import List, Dict, Any
import json


def differential_diagnosis(symptoms: List[str], vital_signs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze symptoms and vital signs to generate differential diagnosis.
    
    Args:
        symptoms: List of patient symptoms
        vital_signs: Dictionary of vital signs (BP, HR, temp, RR, O2)
    
    Returns:
        Dictionary with differential diagnoses ranked by likelihood
    """
    
    # Mock differential diagnosis engine
    differentials = {
        "diagnoses": [
            {
                "diagnosis": "Acute Coronary Syndrome",
                "probability": 0.65,
                "supporting_findings": [
                    "Chest pain radiating to left arm",
                    "Elevated troponin",
                    "ST segment depression on ECG"
                ],
                "icd10": ["I21.0", "I21.1", "I21.2"],
                "next_steps": [
                    "Serial ECG every 10 minutes",
                    "Troponin recheck in 3 hours",
                    "Cardiology consultation",
                    "Antiplatelet therapy initiation"
                ]
            },
            {
                "diagnosis": "Pulmonary Embolism",
                "probability": 0.25,
                "supporting_findings": [
                    "Dyspnea",
                    "Elevated D-dimer",
                    "Low O2 saturation"
                ],
                "icd10": ["I26.0", "I26.9"],
                "next_steps": [
                    "CT pulmonary angiography (CTPA)",
                    "VTE prophylaxis consideration",
                    "Anticoagulation if confirmed"
                ]
            },
            {
                "diagnosis": "Anxiety/Panic Attack",
                "probability": 0.10,
                "supporting_findings": [
                    "Normal cardiac workup",
                    "Hyperventilation pattern"
                ],
                "icd10": ["F41.1"],
                "next_steps": [
                    "Reassurance and observation",
                    "Breathing exercises",
                    "Psychiatric evaluation if recurrent"
                ]
            }
        ],
        "clinical_context": {
            "vital_signs": vital_signs,
            "symptoms_count": len(symptoms),
            "severity_assessment": "High - requires urgent evaluation"
        }
    }
    
    return differentials


def analyze_lab_pattern(lab_results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze lab patterns for diagnostic clues."""
    return {
        "pattern": "Myocardial injury pattern",
        "key_findings": [
            "Elevated troponin I",
            "Elevated CK-MB",
            "Normal D-dimer"
        ],
        "differential_support": [
            "Strongly supports ACS",
            "Argues against PE",
            "Rules out DVT"
        ],
        "recommendations": [
            "Consider high-sensitivity troponin assay",
            "Echocardiography to assess wall motion",
            "Cardiology consultation urgently"
        ]
    }
