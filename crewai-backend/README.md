# CrewAI Medical Diagnostic Backend

Production-ready multi-agent medical decision support system powered by CrewAI and FastAPI.

## Overview

This backend implements a comprehensive medical decision-making system with six specialized agents:

1. **Cardiologist (Diagnostic)** - Generates differential diagnoses and risk stratification
2. **Evidence Researcher** - Synthesizes clinical evidence and guidelines  
3. **Clinical Pharmacist** - Drug safety, interactions, and dosing optimization
4. **Protocol Administrator** - Clinical pathway management and protocol adherence
5. **Medical Scribe** - Clinical documentation, SOAP notes, and ICD-10 coding
6. **Medical Director (Supervisor)** - Oversees team decisions and ensures safety

## Features

✅ Multi-agent collaboration with specialized roles
✅ Comprehensive audit trail for all decisions
✅ Drug interaction checking and dose validation
✅ Evidence-based treatment recommendations
✅ Multi-turn conversation support with memory
✅ SOAP note generation and ICD-10 coding
✅ Production-ready with FastAPI and Pydantic
✅ Structured logging with structlog
✅ Docker-ready deployment
✅ 10 integrated clinical skills/tools

## Project Structure

```
crewai-backend/
├── app.py                      # Main FastAPI application
├── agents/                     # Agent definitions
│   ├── diagnostic.py          # Cardiologist agent
│   ├── evidence.py            # Evidence researcher agent
│   ├── pharmacology.py        # Pharmacist agent
│   ├── protocol.py            # Protocol administrator agent
│   ├── documentation.py       # Medical scribe agent
│   └── supervisor.py          # Medical director supervisor agent
├── skills/                    # Clinical tools (10 total)
│   ├── differential_diagnosis.py
│   ├── drug_interactions.py
│   ├── protocol_advisor.py
│   ├── lab_analyzer.py
│   ├── patient_education.py
│   ├── treatment_recommender.py
│   ├── prescription_validator.py
│   ├── icd10_coder.py
│   ├── soap_generator.py
│   └── image_analyzer.py
├── memory.py                  # Case memory and conversation context
├── callbacks.py               # Audit logging callbacks
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```

## Installation

### Local Development

1. Clone the repository
```bash
git clone <repo-url>
cd crewai-backend
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python app.py
# or
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Deployment

1. Build image
```bash
docker build -t crewai-backend:1.0.0 .
```

2. Run container
```bash
docker run -p 8000:8000 \
  -e LOG_LEVEL=info \
  crewai-backend:1.0.0
```

## API Endpoints

### Health Check
```
GET /health
```
Returns system status and version info.

### Agent Information
```
GET /agents
```
Lists all available agents and their capabilities.

### Diagnostic Analysis (Primary Endpoint)
```
POST /diagnose

Request Body:
{
  "case_id": "unique-case-id",
  "patient": {
    "patient_id": "patient-123",
    "age": 65,
    "gender": "M",
    "weight_kg": 85,
    "height_cm": 175,
    "comorbidities": ["hypertension", "diabetes"],
    "allergies": [],
    "current_medications": [
      {"name": "Lisinopril", "dose": "20 mg", "frequency": "daily"}
    ]
  },
  "chief_complaint": "Chest pain",
  "history_of_present_illness": "Acute onset substernal chest pain...",
  "vital_signs": {
    "systolic_bp": 145,
    "diastolic_bp": 88,
    "heart_rate": 105,
    "respiratory_rate": 20,
    "temperature_c": 37.2,
    "oxygen_saturation": 96.0
  },
  "lab_results": {
    "troponin_i": 0.045,
    "creatinine": 1.8,
    "bnp": 450
  },
  "imaging_findings": {},
  "ecg_findings": {
    "st_elevation": "V1-V3",
    "interpretation": "Anterior STEMI"
  }
}

Response:
{
  "case_id": "unique-case-id",
  "primary_diagnosis": "Acute STEMI - Anterior wall",
  "differential_diagnoses": [...],
  "risk_stratification": {...},
  "recommended_tests": [...],
  "treatment_plan": {...},
  "patient_education": {...},
  "audit_trail_id": "unique-case-id",
  "created_at": "2024-10-04T10:30:00Z"
}
```

### Follow-up Analysis (Multi-turn)
```
POST /followup

Request Body:
{
  "case_id": "existing-case-id",
  "turn_input": "Patient's troponin has increased. What does this mean?",
  "updated_vital_signs": {...},
  "updated_lab_results": {...}
}

Response: Same as /diagnose
```

### Audit Trail Retrieval
```
GET /audit/{case_id}

Response:
{
  "case_id": "case-id",
  "total_entries": 25,
  "critical_decisions": [...],
  "agent_actions": [...],
  "timestamps": [...]
}
```

## Agent Capabilities

### Cardiologist (Diagnostic Agent)
- Synthesizes clinical data (history, vitals, labs, imaging)
- Generates ranked differential diagnoses
- Performs risk stratification (TIMI, GRACE, etc.)
- Identifies gaps requiring additional testing
- **Critical Rules**: Documents reasoning, considers contraindications, escalates red flags

### Evidence Researcher
- Synthesizes highest-level clinical evidence
- Interprets clinical trials and meta-analyses
- Grades recommendations using GRADE methodology
- Identifies evidence gaps and areas of uncertainty

### Pharmacist (Drug Safety Expert)
- Comprehensive drug interaction checking
- Dose adjustment for renal/hepatic function
- Contraindication detection
- Adverse event monitoring and counseling
- **Safety Protocols**: Mandatory screening for QT-prolonging drugs, NSAIDs in renal failure, etc.

### Protocol Administrator
- Selects appropriate clinical pathways
- Ensures guideline adherence
- Identifies timing-critical interventions (e.g., STEMI PCI <90 min)
- Escalates protocol deviations

### Medical Scribe (Documentation)
- Generates structured SOAP notes
- Assigns ICD-10 codes
- Ensures regulatory compliance (HIPAA, state requirements)
- Validates coding accuracy

### Medical Director (Supervisor)
- Synthesizes all team recommendations
- Performs comprehensive safety review
- Makes final clinical decisions
- Resolves disagreements using evidence
- Approves all critical decisions

## Clinical Tools (Skills)

1. **Differential Diagnosis** - Analyzes symptoms for diagnostic possibilities
2. **Drug Interactions** - Checks for medication interactions
3. **Protocol Advisor** - Recommends evidence-based protocols
4. **Lab Analyzer** - Interprets laboratory results
5. **Patient Education** - Creates patient-friendly materials
6. **Treatment Recommender** - Ranks evidence-based treatments
7. **Prescription Validator** - Validates prescriptions for safety
8. **ICD-10 Coder** - Assigns appropriate diagnostic codes
9. **SOAP Generator** - Creates structured clinical notes
10. **Image Analyzer** - Analyzes medical images (ECG, X-ray, echo)

## Memory Management

Cases are maintained in memory with full conversation history:

- **Turn Context**: Captures each user interaction and agent responses
- **Case Memory**: Stores diagnosis history, medications, lab results, imaging
- **Context Retrieval**: Agents can access relevant prior conversation for context

```python
# Example: Get case memory
case = memory_manager.get_case(case_id)
context = case.get_context_for_agent("Cardiologist", max_turns=5)
```

## Audit Logging

All decisions are logged for compliance and quality review:

```python
# Critical decision logging
audit_logger.log_critical_decision(
    case_id="case-123",
    agent_name="Cardiologist",
    decision="Recommend emergent PCI",
    justification="STEMI with hemodynamic compromise",
    supporting_evidence=["ST elevation V1-V3", "Troponin 0.045"]
)

# Tool call logging
audit_logger.log_tool_call(
    case_id="case-123",
    tool_name="drug_interactions",
    tool_input={"medications": [...]},
    tool_output={...}
)
```

## Testing

Run the included sample test case:

```bash
python test_sample_case.py
```

This runs a complete diagnostic workflow on a simulated acute MI case.

## Configuration

Environment variables can be set:

```bash
export LOG_LEVEL=info
export UVICORN_PORT=8000
export UVICORN_HOST=0.0.0.0
```

## Safety Features

✅ **Contraindication Checking** - Pharmacist validates all medications
✅ **Drug Interaction Screening** - Comprehensive checking before recommendations
✅ **Dose Validation** - Age, renal, hepatic adjustments automatically applied
✅ **Red Flag Detection** - Automatic escalation for critical findings
✅ **Audit Trail** - Complete decision documentation for compliance
✅ **Multi-Agent Review** - All critical decisions reviewed by medical director
✅ **Error Handling** - Comprehensive error logging and recovery

## Production Deployment

For production use:

1. **Set up proper error handling and monitoring**
2. **Configure real database storage** (currently in-memory)
3. **Implement authentication and authorization**
4. **Set up proper logging to centralized service**
5. **Configure rate limiting and request throttling**
6. **Implement CI/CD pipeline**
7. **Set up health monitoring and alerting**
8. **Configure backup and disaster recovery**

## Dependencies

- **crewai** - Multi-agent orchestration framework
- **fastapi** - Modern web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **structlog** - Structured logging

See `requirements.txt` for full dependency list and versions.

## License

This software is provided as-is for educational and healthcare purposes.
Ensure compliance with local medical regulations and standards.

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Note**: This is a demonstration system. Production medical AI systems require:
- Validation by medical professionals
- Compliance with healthcare regulations
- Integration with verified medical databases
- Appropriate liability insurance and disclaimers
- Human oversight for all clinical decisions
