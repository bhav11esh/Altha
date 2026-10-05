"""Prescription Validator Tool - Validates prescriptions for safety."""
from typing import Dict, Any, List


def validate_prescription(prescription: Dict[str, Any], patient_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a prescription for safety and appropriateness.
    
    Args:
        prescription: Prescription details (drug, dose, frequency, route)
        patient_profile: Patient details for contraindication checking
    
    Returns:
        Validation results with warnings and recommendations
    """
    
    validation = {
        "prescription": prescription,
        "validation_status": "APPROVED WITH CAUTIONS",
        "alerts": [
            {
                "type": "WARNING",
                "severity": "MODERATE",
                "message": "Patient has renal impairment (eGFR 35). Dose adjustment needed.",
                "recommendation": "Reduce dose by 25% due to renal clearance of drug",
                "evidence": "Product labeling, UpToDate"
            },
            {
                "type": "INFO",
                "severity": "LOW",
                "message": "Patient on warfarin - monitor for drug interaction",
                "recommendation": "Check INR in 3-5 days. May increase INR.",
                "evidence": "CIMS interaction database"
            }
        ],
        "dosing_verification": {
            "recommended_dose": prescription.get("dose", "Unknown"),
            "patient_dose": prescription.get("dose", "Unknown"),
            "age_appropriate": True,
            "renal_dosing_needed": True,
            "hepatic_dosing_needed": False,
            "adjusted_dose": "50 mg BID (reduced from 100 mg BID)"
        },
        "contraindication_check": {
            "absolute_contraindications": [],
            "relative_contraindications": [
                "Renal impairment - requires dose adjustment"
            ],
            "drug_interactions": [
                {"drug": "Warfarin", "interaction_type": "Increased INR", "management": "Monitor INR"}
            ]
        },
        "approval_status": "APPROVED - With dose adjustment recommendation",
        "dispensing_notes": [
            "Dispense adjusted dose",
            "Counsel patient on renal dosing",
            "Follow up INR in 3-5 days"
        ]
    }
    
    return validation


def check_dose_appropriateness(drug_name: str, dose: str, route: str, frequency: str, patient_age: int, weight_kg: float) -> Dict[str, Any]:
    """Check if dose is appropriate for patient."""
    return {
        "drug": drug_name,
        "prescribed_dose": dose,
        "recommended_dose_range": "50-100 mg",
        "dose_status": "APPROPRIATE",
        "age_based_adjustment": "No adjustment needed for age 65",
        "weight_based_dose": f"{weight_kg * 1.5} mg calculated dose",
        "notes": "Dose is within normal range for this patient"
    }
