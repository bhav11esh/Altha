from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from models import FindingType

# ============ Request Models ============

class StartConversationRequest(BaseModel):
    patient_id_hash: str = Field(..., description="Hashed patient ID for privacy")
    doctor_id: str = Field(..., description="Doctor identifier")

class AddTurnRequest(BaseModel):
    conversation_id: UUID = Field(..., description="Conversation ID")
    user_input: str = Field(..., description="Patient/user input")
    ai_response: str = Field(..., description="AI response (JSON string or plain text)")

class ExtractedFinding(BaseModel):
    finding_type: FindingType
    value: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Optional[dict] = None

# ============ Response Models ============

class ConversationResponse(BaseModel):
    id: UUID
    patient_id_hash: str
    doctor_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class FindingResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    turn_id: UUID
    finding_type: FindingType
    value: str
    confidence: float
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: UUID
    turn_id: UUID
    action: str
    details: Optional[dict] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class TurnResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    turn_number: int
    user_input: str
    ai_response: str
    timestamp: datetime
    findings: List[FindingResponse] = []
    audit_logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True

class EnrichedContextResponse(BaseModel):
    current_turn: TurnResponse
    previous_findings: List[FindingResponse] = []
    related_findings: List[FindingResponse] = []

    class Config:
        from_attributes = True

class ConversationHistoryResponse(BaseModel):
    conversation: ConversationResponse
    turns: List[TurnResponse] = []
    total_turns: int
    findings_count: int

    class Config:
        from_attributes = True

class FindingListResponse(BaseModel):
    conversation_id: UUID
    findings: List[FindingResponse] = []
    total_findings: int
    by_type: dict = Field(default_factory=dict, description="Count of findings by type")

    class Config:
        from_attributes = True

class AddTurnResponse(BaseModel):
    turn_id: UUID
    conversation_id: UUID
    turn_number: int
    timestamp: datetime
    findings_extracted: List[FindingResponse] = []
    context_linked: bool = False

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    error: str
    details: Optional[dict] = None
