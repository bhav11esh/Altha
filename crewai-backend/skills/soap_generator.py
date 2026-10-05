"""SOAP Note Generator Tool - Creates structured clinical notes."""
from typing import Dict, Any, List
from datetime import datetime


def generate_soap_note(
    case_data: Dict[str, Any],
    vital_signs: Dict[str, float],
    labs: Dict[str, Any],
    assessment: str,
    plan: str
) -> Dict[str, Any]:
    """
    Generate a structured SOAP note.
    
    Args:
        case_data: Patient and presentation data
        vital_signs: Patient vital signs
        labs: Laboratory results
        assessment: Clinical assessment
        plan: Treatment plan
    
    Returns:
        Complete SOAP note structured for documentation
    """
    
    soap_note = {
        "date": datetime.utcnow().isoformat(),
        "patient_id": case_data.get("patient_id", ""),
        "case_id": case_data.get("case_id", ""),
        
        "subjective": {
            "chief_complaint": "Chest pain",
            "history_of_present_illness": 
                "65-year-old male presents with acute onset chest pain this morning. "
                "Describes as substernal, crushing pressure radiating to left arm, "
                "associated with diaphoresis and dyspnea. Pain started at 8 AM, "
                "currently 8/10 in severity. No relief with rest.",
            "past_medical_history": [
                "Hypertension (10 years)",
                "Type 2 diabetes mellitus (5 years)",
                "Hyperlipidemia (3 years)",
                "Prior MI 2005 - anterior wall, treated with CABG"
            ],
            "medications": [
                "Lisinopril 20 mg daily",
                "Metoprolol 50 mg BID",
                "Atorvastatin 80 mg daily",
                "Aspirin 81 mg daily"
            ],
            "allergies": ["NKDA"],
            "social_history": "Retired, quit smoking 10 years ago, rare alcohol",
            "family_history": "Father died of MI at age 60; mother hypertension"
        },
        
        "objective": {
            "vital_signs": vital_signs,
            "physical_exam": {
                "general": "Anxious male, diaphoretic, in distress",
                "cardiac": "Tachycardic, regular rhythm, no murmurs",
                "lungs": "Clear to auscultation bilaterally",
                "extremities": "Normal perfusion, no edema"
            },
            "laboratory_results": labs,
            "imaging": {
                "EKG": "ST elevation in V1-V3, reciprocal ST depression in II, III, aVF",
                "Troponin_I": "0.045 ng/mL (elevated)",
                "CK_MB": "8.5 ng/mL (elevated)"
            }
        },
        
        "assessment": {
            "primary_diagnosis": "Acute STEMI - Anterior wall, first episode",
            "icd10_code": "I21.02",
            "differential_diagnoses": [
                "Unstable angina",
                "Pulmonary embolism",
                "Aortic dissection",
                "Myocarditis"
            ],
            "severity": "CRITICAL - STEMI requiring urgent intervention",
            "risk_stratification": "High risk - extensive anterior MI with hemodynamic consequences"
        },
        
        "plan": {
            "urgent_actions": [
                "Activate chest pain protocol - STEMI alert to cardiology",
                "Prepare for emergent cardiac catheterization",
                "Initiate dual antiplatelet therapy",
                "Obtain 12-lead EKG x 3",
                "Cardiology consultation STAT"
            ],
            "immediate_medications": [
                {"drug": "Aspirin", "dose": "325 mg", "route": "PO"},
                {"drug": "Clopidogrel", "dose": "600 mg", "route": "PO"},
                {"drug": "Enoxaparin", "dose": "0.5 mg/kg", "route": "IV"},
                {"drug": "Morphine", "dose": "2-4 mg", "route": "IV", "indication": "Pain"}
            ],
            "interventions": [
                "Primary PCI within 90 minutes",
                "Left heart catheterization",
                "Stent placement to LAD",
                "IABP if cardiogenic shock develops"
            ],
            "monitoring": [
                "Continuous cardiac monitoring",
                "Serial EKGs",
                "Serial troponins (0, 3, 6 hours)",
                "Blood pressure and HR monitoring"
            ],
            "follow_up": [
                "Cardiology to manage post-MI care",
                "Cardiac rehabilitation referral",
                "Risk factor modification counseling",
                "Stress test at 6 weeks"
            ]
        },
        
        "disposition": "Admission to Coronary Care Unit (CCU)",
        "attending_physician": "Dr. John Smith, Cardiology",
        "documented_by": "Resident - Mary Johnson, MD"
    }
    
    return soap_note


def format_soap_for_ehr(soap_data: Dict[str, Any]) -> str:
    """Format SOAP note for EHR export."""
    return f"""
PATIENT: {soap_data.get('patient_id')}
CASE: {soap_data.get('case_id')}
DATE: {soap_data.get('date')}

SUBJECTIVE:
{soap_data['subjective'].get('history_of_present_illness', '')}

OBJECTIVE:
Vitals: {soap_data['objective'].get('vital_signs', {})}
Physical Exam: {soap_data['objective'].get('physical_exam', {})}

ASSESSMENT:
{soap_data['assessment'].get('primary_diagnosis', '')}

PLAN:
- {', '.join(soap_data['plan'].get('urgent_actions', []))}

DISPOSITION: {soap_data.get('disposition', '')}
"""
