"""Treatment Recommender Tool - Recommends evidence-based treatments."""
from typing import Dict, Any, List


def recommend_treatment(diagnosis: str, patient_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend evidence-based treatment options.
    
    Args:
        diagnosis: Primary diagnosis
        patient_profile: Patient characteristics for individualization
    
    Returns:
        Ranked treatment recommendations with evidence
    """
    
    recommendations = {
        "diagnosis": "Acute Coronary Syndrome",
        "treatment_options": [
            {
                "rank": 1,
                "treatment": "Primary Percutaneous Coronary Intervention (PCI)",
                "evidence_level": "Level A",
                "timeline": "Within 90 minutes",
                "success_rate": "95%",
                "mortality_reduction": "25-30%",
                "considerations": [
                    "Requires cath lab availability",
                    "Lower rebleeding risk than thrombolytics",
                    "Can treat multiple vessels"
                ],
                "contraindications": [],
                "alternatives": ["Fibrinolysis if no PCI available"]
            },
            {
                "rank": 2,
                "treatment": "Fibrinolytic Therapy (Thrombolysis)",
                "evidence_level": "Level A",
                "timeline": "Within 30 minutes",
                "success_rate": "85%",
                "mortality_reduction": "20%",
                "considerations": [
                    "Used when PCI not available",
                    "Higher rebleeding risk",
                    "Faster door-to-drug time possible"
                ],
                "agents": ["Alteplase (tPA)", "Streptokinase"],
                "contraindications": ["Active bleeding", "Recent surgery", "Intracranial pathology"]
            }
        ],
        "medical_optimization": {
            "antiplatelet_agents": [
                {"drug": "Aspirin", "dose": "325 mg loading, 81 mg daily"},
                {"drug": "Clopidogrel (Plavix)", "dose": "600 mg loading, 75 mg daily x 12 mo"},
                {"drug": "Prasugrel", "dose": "60 mg loading, 5 mg daily x 12 mo"}
            ],
            "anticoagulation": [
                {"drug": "Unfractionated heparin", "dose": "Weight-based IV infusion"},
                {"drug": "Enoxaparin", "dose": "0.5 mg/kg IV", "preferred": True}
            ],
            "beta_blockers": [
                {"drug": "Metoprolol", "target_HR": "55-60 bpm", "caution": "HF with EF <40%"}
            ],
            "acei_arb": [
                {"drug": "Lisinopril", "dose": "Titrated up", "indication": "All patients"}
            ],
            "statins": [
                {"drug": "Atorvastatin", "dose": "80 mg daily", "LDL_target": "<70 mg/dL"}
            ]
        },
        "interventional_considerations": patient_profile.get("interventional_flags", []),
        "next_steps": [
            "Urgent cardiology consultation",
            "Pre-procedure risk stratification",
            "Consent and counseling for revascularization"
        ]
    }
    
    return recommendations


def assess_treatment_efficacy(diagnosis: str, baseline_status: Dict[str, Any], current_status: Dict[str, Any]) -> Dict[str, Any]:
    """Assess how well current treatment is working."""
    return {
        "treatment_response": "Improving",
        "metrics": {
            "troponin_trend": "Declining as expected",
            "ejection_fraction": "Improved from 30% to 35%",
            "symptom_improvement": "Good improvement in chest pain"
        },
        "recommendations": [
            "Continue current regimen",
            "Monitor for signs of cardiogenic shock",
            "Arrange stress testing at 6 weeks"
        ]
    }
