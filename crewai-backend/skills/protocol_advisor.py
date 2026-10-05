"""Protocol Advisor Tool - Recommends clinical protocols and guidelines."""
from typing import Dict, Any, List


def get_treatment_protocol(diagnosis: str, patient_factors: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get evidence-based treatment protocol for a diagnosis.
    
    Args:
        diagnosis: Primary diagnosis or condition
        patient_factors: Comorbidities, age, renal/hepatic function, etc.
    
    Returns:
        Treatment protocol with phases and alternatives
    """
    
    protocols = {
        "diagnosis": "Acute Myocardial Infarction (STEMI)",
        "evidence_level": "A - Randomized Controlled Trials",
        "protocol_phases": {
            "acute_phase": {
                "duration": "0-72 hours",
                "objectives": [
                    "Restore coronary perfusion urgently",
                    "Limit myocardial necrosis",
                    "Prevent complications"
                ],
                "interventions": [
                    {
                        "intervention": "Primary PCI",
                        "timing": "Within 90 minutes of first medical contact",
                        "agents": ["Aspirin 325 mg", "P2Y12 inhibitor"],
                        "evidence": "Preferred over fibrinolysis"
                    },
                    {
                        "intervention": "Fibrinolytic therapy",
                        "timing": "Within 30 minutes if no PCI available",
                        "agents": ["tPA", "Streptokinase"],
                        "evidence": "Second-line if no access to PCI"
                    }
                ]
            },
            "recovery_phase": {
                "duration": "Days 3-30",
                "medications": [
                    {"drug": "Aspirin", "dose": "81 mg daily", "duration": "Lifelong"},
                    {"drug": "P2Y12 inhibitor", "dose": "Variable", "duration": "12 months"},
                    {"drug": "ACE inhibitor", "dose": "Titrated", "duration": "Lifelong"},
                    {"drug": "Beta-blocker", "dose": "Titrated", "duration": "Lifelong"}
                ],
                "monitoring": ["ECG daily", "Troponin serial", "Ejection fraction assessment"]
            },
            "long_term_phase": {
                "duration": "1+ years",
                "lifestyle": ["Cardiac rehabilitation", "Diet modification", "Exercise"],
                "medications": ["ASA", "P2Y12i", "ACEi", "Statin", "Beta-blocker"],
                "monitoring": ["Stress test at 6 weeks", "Annual cardiology follow-up"]
            }
        },
        "contraindications_to_monitor": patient_factors,
        "guideline_sources": ["ACC/AHA 2024", "ESC 2023"]
    }
    
    return protocols


def get_risk_stratification(diagnosis: str, risk_factors: List[str]) -> Dict[str, Any]:
    """Stratify patient risk using validated scoring systems."""
    return {
        "score_name": "TIMI Risk Score",
        "risk_factors_present": risk_factors,
        "total_points": len(risk_factors),
        "risk_category": "High risk" if len(risk_factors) >= 3 else "Intermediate risk",
        "30_day_mortality": "2.8-4.0%",
        "recommended_intensity": "Aggressive medical management + interventional cardiology"
    }
