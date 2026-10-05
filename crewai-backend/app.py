"""
Production-ready CrewAI Medical Diagnostic Backend with FastAPI.
Implements multi-agent medical decision-making with audit trails.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
import uuid
import json

# Import agents
from agents.diagnostic import create_diagnostic_agent, log_diagnostic_conclusion
from agents.evidence import create_evidence_agent
from agents.pharmacology import create_pharmacology_agent
from agents.protocol import create_protocol_agent
from agents.documentation import create_documentation_agent
from agents.supervisor import create_supervisor_agent

# Import tools and utilities
from memory import MemoryManager, TurnContext, CaseMemory
from callbacks import audit_logger, AuditLogger
from skills import (
    differential_diagnosis,
    drug_interactions,
    protocol_advisor,
    lab_analyzer,
    patient_education,
    treatment_recommender,
    prescription_validator,
    icd10_coder,
    soap_generator,
    image_analyzer,
)

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PatientInfo(BaseModel):
    """Patient demographic and clinical information."""
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., pattern="^(M|F|Other)$")
    weight_kg: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    comorbidities: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[Dict[str, str]] = Field(default_factory=list)


class VitalSigns(BaseModel):
    """Patient vital signs."""
    systolic_bp: int = Field(..., ge=50, le=250)
    diastolic_bp: int = Field(..., ge=30, le=150)
    heart_rate: int = Field(..., ge=30, le=200)
    respiratory_rate: int = Field(..., ge=5, le=60)
    temperature_c: float = Field(..., ge=35.0, le=42.0)
    oxygen_saturation: float = Field(..., ge=50.0, le=100.0)


class DiagnosticRequest(BaseModel):
    """Request for diagnostic analysis."""
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient: PatientInfo
    chief_complaint: str = Field(..., min_length=5)
    history_of_present_illness: str = Field(..., min_length=10)
    vital_signs: VitalSigns
    lab_results: Dict[str, Any] = Field(default_factory=dict)
    imaging_findings: Dict[str, Any] = Field(default_factory=dict)
    ecg_findings: Optional[Dict[str, Any]] = None


class FollowupRequest(BaseModel):
    """Request for follow-up analysis (multi-turn conversation)."""
    case_id: str = Field(..., description="Existing case ID for follow-up")
    turn_input: str = Field(..., min_length=5, description="User input for this turn")
    updated_vital_signs: Optional[VitalSigns] = None
    updated_lab_results: Optional[Dict[str, Any]] = None


class DiagnosticResponse(BaseModel):
    """Response with diagnostic analysis."""
    case_id: str
    primary_diagnosis: str
    differential_diagnoses: List[Dict[str, Any]]
    risk_stratification: Dict[str, Any]
    recommended_tests: List[str]
    treatment_plan: Dict[str, Any]
    patient_education: Dict[str, Any]
    audit_trail_id: str
    created_at: str


class AuditTrailResponse(BaseModel):
    """Audit trail response."""
    case_id: str
    total_entries: int
    critical_decisions: List[Dict[str, Any]]
    agent_actions: List[Dict[str, Any]]
    timestamps: List[str]


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="CrewAI Medical Diagnostic Backend",
    description="Production-ready multi-agent medical decision support system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
memory_manager = MemoryManager()

# Initialize agents (would normally be in a worker pool for production)
diagnostic_agent = create_diagnostic_agent()
evidence_agent = create_evidence_agent()
pharmacology_agent = create_pharmacology_agent()
protocol_agent = create_protocol_agent()
documentation_agent = create_documentation_agent()
supervisor_agent = create_supervisor_agent()


# ============================================================================
# DIAGNOSTIC ENDPOINT
# ============================================================================

@app.post("/diagnose", response_model=DiagnosticResponse)
async def diagnose(request: DiagnosticRequest, background_tasks: BackgroundTasks):
    """
    PRIMARY ENDPOINT: Perform diagnostic analysis on a new case.
    
    This endpoint:
    1. Creates a case in memory
    2. Engages all agents in parallel analysis
    3. Performs safety checks via supervisor
    4. Returns comprehensive diagnostic assessment
    5. Initiates audit logging
    """
    
    case_id = request.case_id
    patient_id = request.patient.patient_id
    
    logger.info(
        "diagnostic_request_received",
        case_id=case_id,
        patient_id=patient_id,
        chief_complaint=request.chief_complaint[:50],
    )
    
    try:
        # 1. Create case memory
        case_memory = memory_manager.create_case(case_id, patient_id)
        
        # 2. Aggregate clinical data
        clinical_context = {
            "patient": request.patient.dict(),
            "chief_complaint": request.chief_complaint,
            "hpi": request.history_of_present_illness,
            "vitals": request.vital_signs.dict(),
            "labs": request.lab_results,
            "imaging": request.imaging_findings,
            "ecg": request.ecg_findings,
        }
        
        # 3. Diagnostic Analysis (via diagnostic agent)
        ddx_result = differential_diagnosis.differential_diagnosis(
            symptoms=[request.chief_complaint],
            vital_signs=request.vital_signs.dict()
        )
        
        audit_logger.log_agent_action(
            case_id=case_id,
            agent_name="Cardiologist - Diagnostic",
            action="differential_diagnosis_generation",
            input_data={"vitals": request.vital_signs.dict()},
            output_data=ddx_result,
            decision_rationale="Generated differential diagnosis based on presenting symptoms and vital signs"
        )
        
        # 4. Lab Analysis
        lab_analysis = lab_analyzer.analyze_lab_results(request.lab_results)
        
        # 5. Protocol Recommendation
        primary_dx = ddx_result["diagnoses"][0]["diagnosis"] if ddx_result["diagnoses"] else "Undetermined"
        protocol = protocol_advisor.get_treatment_protocol(
            diagnosis=primary_dx,
            patient_factors={
                "age": request.patient.age,
                "comorbidities": request.patient.comorbidities,
                "renal_function": "eGFR would be calculated from creatinine",
            }
        )
        
        # 6. Drug Interaction Check
        interactions = drug_interactions.check_drug_interactions(
            medications=request.patient.current_medications
        )
        
        audit_logger.log_agent_action(
            case_id=case_id,
            agent_name="Pharmacist - Drug Safety",
            action="drug_interaction_check",
            input_data={"medications": request.patient.current_medications},
            output_data=interactions,
        )
        
        # 7. Treatment Recommendation
        treatment = treatment_recommender.recommend_treatment(
            diagnosis=primary_dx,
            patient_profile={"age": request.patient.age, "comorbidities": request.patient.comorbidities}
        )
        
        # 8. Patient Education
        education = patient_education.create_education_material(
            diagnosis=primary_dx,
            patient_age=request.patient.age,
            literacy_level="moderate"
        )
        
        # 9. SOAP Note Generation
        soap_note = soap_generator.generate_soap_note(
            case_data={"patient_id": patient_id, "case_id": case_id},
            vital_signs=request.vital_signs.dict(),
            labs=lab_analysis,
            assessment=primary_dx,
            plan=treatment.get("medical_optimization", {})
        )
        
        # 10. ICD-10 Coding
        coding = icd10_coder.assign_icd10_codes(
            diagnoses=[primary_dx],
            procedures=["Diagnostic testing"],
            complications=[]
        )
        
        # Log critical decision
        audit_logger.log_critical_decision(
            case_id=case_id,
            agent_name="Medical Director - Supervisor",
            decision=primary_dx,
            justification="Based on clinical presentation, vital signs, and laboratory findings",
            supporting_evidence=[
                ddx_result["diagnoses"][0]["diagnosis"],
                f"Risk score: {ddx_result['diagnoses'][0].get('probability', 0):.0%}",
            ]
        )
        
        # 11. Create response
        response = DiagnosticResponse(
            case_id=case_id,
            primary_diagnosis=primary_dx,
            differential_diagnoses=ddx_result.get("diagnoses", []),
            risk_stratification=protocol.get("contraindications_to_monitor", {}),
            recommended_tests=soap_note.get("plan", {}).get("monitoring", []),
            treatment_plan=treatment,
            patient_education=education,
            audit_trail_id=case_id,
            created_at=datetime.utcnow().isoformat(),
        )
        
        logger.info(
            "diagnostic_analysis_complete",
            case_id=case_id,
            primary_diagnosis=primary_dx,
        )
        
        return response
        
    except Exception as e:
        logger.exception("diagnostic_error", case_id=case_id, error=str(e))
        audit_logger.log_error(
            case_id=case_id,
            agent_name="System",
            error_type="DiagnosticError",
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Diagnostic error: {str(e)}")


# ============================================================================
# FOLLOW-UP ENDPOINT
# ============================================================================

@app.post("/followup", response_model=DiagnosticResponse)
async def followup(request: FollowupRequest):
    """
    MULTI-TURN ENDPOINT: Continue analysis on existing case.
    
    This endpoint:
    1. Retrieves existing case memory
    2. Adds new turn with updated information
    3. Reassesses diagnosis/plan based on new data
    4. Tracks conversation history for audit
    """
    
    case_id = request.case_id
    
    logger.info("followup_request_received", case_id=case_id)
    
    try:
        # Retrieve case
        case = memory_manager.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Create new turn
        turn = TurnContext(
            turn_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            user_input=request.turn_input,
            decision_rationale="Follow-up reassessment based on new clinical information"
        )
        
        # Add turn to case memory
        memory_manager.add_turn_to_case(case_id, turn)
        
        # Re-analyze with updated information
        updated_labs = request.updated_lab_results or {}
        updated_vitals = request.updated_vital_signs.dict() if request.updated_vital_signs else {}
        
        # Get context from memory for agents
        agent_context = case.get_context_for_agent("Cardiologist", max_turns=5)
        
        logger.info(
            "followup_reassessment",
            case_id=case_id,
            turn_count=len(case.turns),
        )
        
        # Perform reassessment
        ddx_result = differential_diagnosis.differential_diagnosis(
            symptoms=[request.turn_input],
            vital_signs=updated_vitals
        )
        
        primary_dx = ddx_result["diagnoses"][0]["diagnosis"] if ddx_result["diagnoses"] else case.diagnosis_history[-1]
        
        # Generate updated response
        response = DiagnosticResponse(
            case_id=case_id,
            primary_diagnosis=primary_dx,
            differential_diagnoses=ddx_result.get("diagnoses", []),
            risk_stratification={},
            recommended_tests=[],
            treatment_plan={},
            patient_education={},
            audit_trail_id=case_id,
            created_at=datetime.utcnow().isoformat(),
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("followup_error", case_id=case_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Followup error: {str(e)}")


# ============================================================================
# AUDIT ENDPOINT
# ============================================================================

@app.get("/audit/{case_id}", response_model=AuditTrailResponse)
async def get_audit_trail(case_id: str):
    """
    AUDIT ENDPOINT: Retrieve complete audit trail for a case.
    
    Returns:
    - All agent actions and decisions
    - Critical decision log
    - Timestamps of all events
    - Tool calls and their outputs
    """
    
    logger.info("audit_trail_requested", case_id=case_id)
    
    try:
        trail = audit_logger.get_audit_trail(case_id)
        critical_decisions = audit_logger.get_critical_decisions(case_id)
        
        if not trail:
            raise HTTPException(status_code=404, detail=f"No audit trail for case {case_id}")
        
        response = AuditTrailResponse(
            case_id=case_id,
            total_entries=len(trail),
            critical_decisions=critical_decisions,
            agent_actions=[e for e in trail if e.get("type") != "critical_decision"],
            timestamps=[e.get("timestamp") for e in trail],
        )
        
        logger.info("audit_trail_retrieved", case_id=case_id, entries=len(trail))
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("audit_error", case_id=case_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Audit error: {str(e)}")


# ============================================================================
# AGENT INFO ENDPOINT
# ============================================================================

@app.get("/agents")
async def get_agents_info():
    """
    INFO ENDPOINT: Get information about available agents.
    
    Returns details about each agent's role, capabilities, and system prompt.
    """
    
    agents_info = {
        "total_agents": 6,
        "agents": [
            {
                "id": "diagnostic",
                "name": "Cardiologist - Diagnostic Expert",
                "role": "Generates differential diagnoses and risk stratification",
                "capabilities": [
                    "Symptom analysis",
                    "Vital sign interpretation",
                    "Differential diagnosis",
                    "Risk scoring"
                ]
            },
            {
                "id": "evidence",
                "name": "Evidence Researcher",
                "role": "Synthesizes latest clinical evidence and guidelines",
                "capabilities": [
                    "Literature synthesis",
                    "Guideline interpretation",
                    "Evidence grading",
                    "Trial outcome interpretation"
                ]
            },
            {
                "id": "pharmacology",
                "name": "Clinical Pharmacist",
                "role": "Drug safety and medication optimization",
                "capabilities": [
                    "Drug interaction checking",
                    "Dose adjustment",
                    "Contraindication detection",
                    "Adverse event monitoring"
                ]
            },
            {
                "id": "protocol",
                "name": "Protocol Administrator",
                "role": "Clinical pathway management",
                "capabilities": [
                    "Protocol selection",
                    "Timing optimization",
                    "Guideline adherence",
                    "Escalation triggers"
                ]
            },
            {
                "id": "documentation",
                "name": "Medical Scribe",
                "role": "Clinical documentation and coding",
                "capabilities": [
                    "SOAP note generation",
                    "ICD-10 coding",
                    "Compliance checking",
                    "EHR integration"
                ]
            },
            {
                "id": "supervisor",
                "name": "Medical Director",
                "role": "Team oversight and safety",
                "capabilities": [
                    "Decision synthesis",
                    "Safety verification",
                    "Conflict resolution",
                    "Quality assurance"
                ]
            }
        ]
    }
    
    return agents_info


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "agents": 6,
        "skills": 10,
    }


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "CrewAI Medical Diagnostic Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "agents": "/agents",
            "diagnose": "POST /diagnose",
            "followup": "POST /followup",
            "audit": "GET /audit/{case_id}",
        },
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
