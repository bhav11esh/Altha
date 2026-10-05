"""
Unit tests for Conversation Service
Run with: pytest test_app.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app import app, get_db
from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class TestHealth:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestConversations:
    def test_start_conversation(self):
        """Test starting a new conversation"""
        response = client.post(
            "/conversations/start",
            json={
                "patient_id_hash": "test_patient_123",
                "doctor_id": "test_doctor_456"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id_hash"] == "test_patient_123"
        assert data["doctor_id"] == "test_doctor_456"
        assert "id" in data

class TestTurns:
    @pytest.fixture
    def conversation_id(self):
        """Create a test conversation"""
        response = client.post(
            "/conversations/start",
            json={
                "patient_id_hash": "test_patient_123",
                "doctor_id": "test_doctor_456"
            }
        )
        return response.json()["id"]

    def test_add_turn(self, conversation_id):
        """Test adding a turn to conversation"""
        response = client.post(
            "/turns/add",
            json={
                "conversation_id": conversation_id,
                "user_input": "Patient reports fever",
                "ai_response": '{"diagnosis": ["Common Cold"], "drugs": ["Paracetamol"]}'
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["turn_number"] == 1
        assert len(data["findings_extracted"]) > 0

    def test_get_turns(self, conversation_id):
        """Test retrieving all turns"""
        client.post(
            "/turns/add",
            json={
                "conversation_id": conversation_id,
                "user_input": "Patient reports fever",
                "ai_response": '{"diagnosis": ["Common Cold"]}'
            }
        )

        response = client.get(f"/turns/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["turn_number"] == 1

class TestFindings:
    @pytest.fixture
    def conversation_with_findings(self):
        """Create conversation with findings"""
        conv_response = client.post(
            "/conversations/start",
            json={
                "patient_id_hash": "test_patient_123",
                "doctor_id": "test_doctor_456"
            }
        )
        conversation_id = conv_response.json()["id"]

        client.post(
            "/turns/add",
            json={
                "conversation_id": conversation_id,
                "user_input": "Patient has symptoms",
                "ai_response": '{"diagnosis": ["Hypertension"], "drugs": ["Lisinopril"]}'
            }
        )

        return conversation_id

    def test_get_findings(self, conversation_with_findings):
        """Test retrieving findings"""
        response = client.get(f"/findings/{conversation_with_findings}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_findings"] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
