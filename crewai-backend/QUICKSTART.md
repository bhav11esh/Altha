# Quick Start Guide

## Installation & Running

### Option 1: Local Development (Recommended for testing)

```bash
# 1. Navigate to project
cd /Users/pocketfm/Desktop/Personal\ /Althea/crewai-backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python app.py
# Server will start at http://localhost:8000
```

### Option 2: Docker Deployment (Production)

```bash
# Build image
docker build -t crewai-medical-backend:1.0.0 .

# Run container
docker run -p 8000:8000 \
  --name crewai-backend \
  crewai-medical-backend:1.0.0

# Access at http://localhost:8000
```

## Test the System

In a new terminal:

```bash
# Make sure server is running first!

# Run sample test case
python test_sample_case.py

# Or manually test an endpoint:
curl http://localhost:8000/health

# Or test with JSON:
curl -X POST http://localhost:8000/agents
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/agents` | GET | List all agents |
| `/diagnose` | POST | Submit new diagnostic case |
| `/followup` | POST | Follow-up analysis (multi-turn) |
| `/audit/{case_id}` | GET | Get audit trail |
| `/docs` | GET | Interactive API documentation |

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Sample Request

```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "patient_id": "PT_001",
      "age": 65,
      "gender": "M",
      "weight_kg": 85,
      "height_cm": 175,
      "comorbidities": ["hypertension"],
      "allergies": [],
      "current_medications": []
    },
    "chief_complaint": "Chest pain",
    "history_of_present_illness": "Acute onset substernal chest pain",
    "vital_signs": {
      "systolic_bp": 145,
      "diastolic_bp": 88,
      "heart_rate": 105,
      "respiratory_rate": 20,
      "temperature_c": 37.2,
      "oxygen_saturation": 96.0
    },
    "lab_results": {
      "troponin_i": 0.045
    },
    "imaging_findings": {},
    "ecg_findings": null
  }'
```

## Project Structure

```
crewai-backend/
├── app.py                    # Main FastAPI application
├── memory.py                 # Case memory management
├── callbacks.py              # Audit logging
├── requirements.txt          # Dependencies
├── Dockerfile                # Docker configuration
├── agents/                   # 6 specialized agents
│   ├── diagnostic.py         # Cardiologist
│   ├── evidence.py           # Evidence researcher
│   ├── pharmacology.py       # Pharmacist
│   ├── protocol.py           # Protocol admin
│   ├── documentation.py      # Medical scribe
│   └── supervisor.py         # Medical director
└── skills/                   # 10 clinical tools
    ├── differential_diagnosis.py
    ├── drug_interactions.py
    ├── protocol_advisor.py
    ├── lab_analyzer.py
    ├── patient_education.py
    ├── treatment_recommender.py
    ├── prescription_validator.py
    ├── icd10_coder.py
    ├── soap_generator.py
    └── image_analyzer.py
```

## What Each Agent Does

1. **Cardiologist (Diagnostic)** - Analyzes symptoms, generates differential diagnoses
2. **Evidence Researcher** - Finds and synthesizes clinical evidence
3. **Pharmacist (Drug Safety)** - Checks drug interactions and dosing
4. **Protocol Administrator** - Selects evidence-based clinical pathways
5. **Medical Scribe** - Documents in SOAP format, generates ICD-10 codes
6. **Medical Director (Supervisor)** - Oversees all decisions for safety

## Clinical Tools (Skills)

The system includes 10 integrated medical tools:

1. **Differential Diagnosis** - Analyzes symptoms for possible diagnoses
2. **Drug Interactions** - Screens for medication interactions
3. **Protocol Advisor** - Recommends evidence-based treatment protocols
4. **Lab Analyzer** - Interprets laboratory results
5. **Patient Education** - Creates patient-friendly materials
6. **Treatment Recommender** - Ranks treatment options by evidence
7. **Prescription Validator** - Checks prescriptions for safety
8. **ICD-10 Coder** - Assigns diagnostic codes
9. **SOAP Generator** - Creates structured clinical notes
10. **Image Analyzer** - Analyzes medical images (ECG, X-ray, ultrasound)

## Troubleshooting

### Port Already in Use
```bash
# Kill existing process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app:app --port 8001
```

### Module Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### API Not Responding
```bash
# Check if server is running
curl http://localhost:8000/health

# Check logs for errors
tail -f app.log
```

## Next Steps

1. ✅ Run `test_sample_case.py` to see end-to-end workflow
2. ✅ Visit `/docs` for interactive API documentation
3. ✅ Review `README.md` for full documentation
4. ✅ Explore agent prompts in `agents/` directory
5. ✅ Integrate with your patient data systems

## Production Deployment

For production use, consider:

- [ ] Set up proper database (PostgreSQL/MongoDB)
- [ ] Configure authentication & authorization
- [ ] Set up monitoring & alerting (Prometheus/DataDog)
- [ ] Implement rate limiting
- [ ] Configure centralized logging
- [ ] Set up health checks & auto-recovery
- [ ] Implement backup & disaster recovery
- [ ] Configure CI/CD pipeline
- [ ] Set up proper error handling
- [ ] Add compliance & audit logging

## Support

For questions or issues:
1. Check the README.md for detailed documentation
2. Review test_sample_case.py for usage examples
3. Check the FastAPI docs at http://localhost:8000/docs

---

**Ready to go!** Start with: `python app.py`
