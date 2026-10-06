import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from models import AuditLog, Conversation, Message
from phi_detector import PHIDetector
from schemas import MessageResponse

logger = logging.getLogger(__name__)

phi_detector = PHIDetector()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
HISTORY_LIMIT = 10
SYSTEM_PROMPT = (
    "You are a medical information assistant. You do not replace a licensed clinician. "
    "Give clear, cautious, evidence-based information and state when a clinician must decide."
)


def _phi_dict(text: str) -> Dict[str, List[str]]:
    phi = phi_detector.detect_phi(text)
    return {
        "names": phi.names,
        "ids": phi.ids,
        "emails": phi.emails,
        "phones": phi.phones,
        "medical_records": phi.medical_records,
    }


def _redact(text: str) -> str:
    redacted, _ = phi_detector.anonymize_text(text, phi_detector.detect_phi(text))
    return redacted


def generate_reply(history: List[Dict[str, str]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
        )
    except Exception:
        logger.exception("openai_request_failed")
        raise HTTPException(status_code=502, detail="AI provider request failed")
    return completion.choices[0].message.content or ""


def process_message(
    db: Session,
    conversation_id: int | None,
    user_id: int,
    message_text: str,
) -> MessageResponse:
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        ).first()
        if not conversation:
            raise LookupError("Conversation not found")
    else:
        conversation = Conversation(
            user_id=user_id,
            title=message_text[:50] or "New Conversation",
            model=OPENAI_MODEL,
        )
        db.add(conversation)
        db.flush()

    phi = _phi_dict(message_text)
    has_phi = any(phi.values())
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message_text,
        detected_phi=phi if has_phi else None,
        is_anonymized=False,
    )
    db.add(user_message)
    db.flush()

    if has_phi:
        db.add(AuditLog(
            user_id=user_id,
            action="phi_detected",
            details={
                "message_id": user_message.id,
                "phi_types": {key: len(values) for key, values in phi.items()},
            },
        ))

    recent = db.query(Message).filter(
        Message.conversation_id == conversation.id,
    ).order_by(Message.created_at.desc(), Message.id.desc()).limit(HISTORY_LIMIT).all()
    history: List[Dict[str, Any]] = [
        {"role": m.role, "content": _redact(m.content)} for m in reversed(recent)
    ]

    reply = generate_reply(history)

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply,
        model_used=OPENAI_MODEL,
        is_anonymized=False,
    )
    db.add(assistant_message)
    db.add(AuditLog(
        user_id=user_id,
        action="message_sent",
        details={
            "conversation_id": conversation.id,
            "message_id": user_message.id,
            "model": OPENAI_MODEL,
            "has_phi": has_phi,
        },
    ))
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assistant_message)

    return MessageResponse.model_validate(assistant_message)


def anonymize_message(db: Session, message_id: int, user_id: int) -> Dict[str, Any]:
    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Conversation.user_id == user_id,
    ).first()
    if not message:
        raise LookupError("Message not found")
    if message.role != "user":
        raise ValueError("Only user messages can be anonymized")

    anonymized, replacements = phi_detector.anonymize_text(
        message.content, phi_detector.detect_phi(message.content)
    )
    message.original_content = message.content
    message.content = anonymized
    message.is_anonymized = True
    message.detected_phi = _phi_dict(message.original_content)
    db.add(AuditLog(
        user_id=user_id,
        action="anonymized",
        details={"message_id": message_id, "items_anonymized": len(replacements)},
    ))
    db.commit()

    return {"message_id": message_id, "anonymized_content": anonymized}


def get_conversation_context(db: Session, conversation_id: int, user_id: int, limit: int = 2) -> List[MessageResponse]:
    messages = db.query(Message).join(Conversation).filter(
        Message.conversation_id == conversation_id,
        Conversation.user_id == user_id,
    ).order_by(Message.created_at.desc(), Message.id.desc()).limit(limit * 2).all()
    return [MessageResponse.model_validate(m) for m in reversed(messages)]
