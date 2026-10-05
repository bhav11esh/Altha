from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PHIDetection(BaseModel):
    names: List[str] = []
    ids: List[str] = []
    emails: List[str] = []
    phones: List[str] = []
    medical_records: List[str] = []


class MessageCreate(BaseModel):
    content: str
    role: str = "user"
    model: Optional[str] = None
    file_ids: Optional[List[int]] = None


class AgentReasoningSchema(BaseModel):
    agent_name: str
    reasoning_text: str
    confidence_score: Optional[int] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    detected_phi: Optional[PHIDetection] = None
    is_anonymized: bool
    model_used: Optional[str] = None
    agent_reasoning: Optional[List[AgentReasoningSchema]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    model: str = "mistral"


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    model: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: int
    title: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    details: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    id: int
    conversation_id: Optional[int] = None
    filename: str
    file_type: str
    size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnonymizationRequest(BaseModel):
    message_id: int
    replacements: Dict[str, str]  # {original: replacement}


class ModelChangeRequest(BaseModel):
    model: str  # mistral, llama, gpt-4o


class PHIDetectionRequest(BaseModel):
    text: str


class ChatCompletionRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    model: str = "mistral"
    include_context: bool = True
    context_limit: int = 2  # Include last N turns
