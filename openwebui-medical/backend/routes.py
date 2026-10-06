import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from chat import anonymize_message, get_conversation_context, process_message
from database import get_db
from models import AuditLog, Conversation, FileUpload, Message, User
from phi_detector import PHIDetector
from schemas import (
    AuditLogResponse,
    ConversationCreate,
    ConversationListItem,
    ConversationResponse,
    FileUploadResponse,
    MessageResponse,
    PHIDetectionRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter()
phi_detector = PHIDetector()

UPLOAD_DIR = Path("/app/uploads")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_BYTES = 72


class ChatRequest(BaseModel):
    content: str
    role: str = "user"
    model: Optional[str] = None
    conversation_id: Optional[int] = None


def current_user(email: str = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user


def owned_conversation(db: Session, user: User, conversation_id: int) -> Conversation:
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if not (MIN_PASSWORD_LENGTH <= len(payload.password) and len(payload.password.encode()) <= MAX_PASSWORD_BYTES):
        raise HTTPException(
            status_code=400,
            detail=f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_BYTES} bytes",
        )
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db.add(AuditLog(user_id=user.id, action="login", details={}))
    db.commit()
    return TokenResponse(access_token=create_access_token({"sub": user.email}))


@router.get("/conversations", response_model=List[ConversationListItem])
def list_conversations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id,
    ).order_by(Conversation.updated_at.desc()).all()
    return [
        ConversationListItem(
            id=c.id,
            title=c.title,
            model=c.model,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages),
        )
        for c in conversations
    ]


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    conversation = Conversation(
        user_id=user.id,
        title=payload.title or "New Conversation",
        model=payload.model,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return owned_conversation(db, user, conversation_id)


@router.get("/conversations/{conversation_id}/context")
def get_context(conversation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned_conversation(db, user, conversation_id)
    return {"context": get_conversation_context(db, conversation_id, user.id)}


@router.post("/chat", response_model=MessageResponse)
def chat(payload: ChatRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content is required")
    try:
        return process_message(db, payload.conversation_id, user.id, content)
    except LookupError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/messages/{message_id}/anonymize")
def anonymize(message_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        return anonymize_message(db, message_id, user.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Message not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/phi/detect")
def detect_phi(payload: PHIDetectionRequest):
    phi = phi_detector.detect_phi(payload.text)
    detected = {
        "names": phi.names,
        "ids": phi.ids,
        "emails": phi.emails,
        "phones": phi.phones,
        "medical_records": phi.medical_records,
    }
    return {"has_phi": any(detected.values()), "phi": detected, "text": payload.text}


@router.get("/phi/preview")
def preview_phi(text: str = Query(...)):
    anonymized, _ = phi_detector.anonymize_text(text, phi_detector.detect_phi(text))
    return {"anonymized": anonymized}


@router.post("/files/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: Optional[int] = Form(None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if conversation_id is not None:
        owned_conversation(db, user, conversation_id)

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    original_name = file.filename or "upload"
    extension = Path(original_name).suffix.lower().lstrip(".") or "bin"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.{extension}"
    stored_path.write_bytes(data)

    record = FileUpload(
        conversation_id=conversation_id,
        filename=original_name,
        file_type=extension,
        file_path=str(stored_path),
        size_bytes=len(data),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def audit_logs(limit: int = Query(100, ge=1, le=500), user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(AuditLog).filter(
        AuditLog.user_id == user.id,
    ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
