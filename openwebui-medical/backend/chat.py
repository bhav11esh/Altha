import httpx
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models import Message, Conversation, AgentReasoning, AuditLog
from schemas import MessageResponse, AgentReasoningSchema
from phi_detector import PHIDetector
import asyncio

# CrewAI backend URL
CREWAI_BACKEND_URL = "http://localhost:8001"
TIMEOUT = 60.0

phi_detector = PHIDetector()


async def send_to_crewai(
    message: str,
    conversation_history: List[Dict[str, str]],
    model: str = "mistral",
) -> Dict[str, Any]:
    """Send message to CrewAI backend and get response with reasoning"""
    payload = {
        "message": message,
        "history": conversation_history,
        "model": model,
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{CREWAI_BACKEND_URL}/chat",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        # Return mock response if CrewAI is not available
        print(f"Error contacting CrewAI: {e}")
        return get_mock_crewai_response(message, model)


def get_mock_crewai_response(message: str, model: str) -> Dict[str, Any]:
    """Return mock CrewAI response for demo purposes"""
    return {
        "response": f"I'm analyzing your medical query about: {message[:50]}... As a medical AI assistant, I would need to consult with multiple agents for a comprehensive answer.",
        "agents": [
            {
                "name": "Diagnostic",
                "reasoning": "Initial symptom analysis and differential diagnosis",
                "confidence": 85,
            },
            {
                "name": "Evidence",
                "reasoning": "Reviewing clinical evidence and medical literature",
                "confidence": 78,
            },
            {
                "name": "Pharmacology",
                "reasoning": "Analyzing medication interactions and treatment options",
                "confidence": 82,
            },
            {
                "name": "Risk Assessment",
                "reasoning": "Evaluating patient risk factors and safety concerns",
                "confidence": 88,
            },
        ],
        "model": model,
    }


async def process_message(
    db: Session,
    conversation_id: Optional[int],
    user_id: int,
    message_text: str,
    model: str = "mistral",
    user_email: str = "",
) -> MessageResponse:
    """Process a user message: detect PHI, send to CrewAI, store response"""

    # Detect PHI in the message
    phi = phi_detector.detect_phi(message_text)
    is_anonymized = False
    original_content = None

    # Get or create conversation
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        ).first()
        if not conversation:
            raise ValueError("Conversation not found")
    else:
        conversation = Conversation(
            user_id=user_id,
            title=message_text[:50] + "...",
            model=model,
        )
        db.add(conversation)
        db.flush()

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message_text,
        detected_phi={
            "names": phi.names,
            "ids": phi.ids,
            "emails": phi.emails,
            "phones": phi.phones,
            "medical_records": phi.medical_records,
        } if phi.names or phi.ids or phi.emails else None,
        is_anonymized=False,
    )
    db.add(user_message)
    db.flush()

    # Log PHI detection if found
    if phi.names or phi.ids or phi.emails:
        audit_log = AuditLog(
            user_id=user_id,
            action="phi_detected",
            details={
                "message_id": user_message.id,
                "phi_types": {
                    "names": len(phi.names),
                    "ids": len(phi.ids),
                    "emails": len(phi.emails),
                    "phones": len(phi.phones),
                    "medical_records": len(phi.medical_records),
                },
            },
        )
        db.add(audit_log)

    # Get conversation history for context (last 2 turns)
    history_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id,
    ).order_by(Message.created_at.desc()).limit(4).all()

    history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history_messages)
    ]

    # Send to CrewAI
    crewai_response = await send_to_crewai(
        message_text,
        history,
        model=model,
    )

    # Parse response
    response_text = crewai_response.get("response", "No response")
    agents = crewai_response.get("agents", [])

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        model_used=model,
        agent_reasoning=[
            {
                "agent_name": agent["name"],
                "reasoning_text": agent.get("reasoning", ""),
                "confidence_score": agent.get("confidence", None),
            }
            for agent in agents
        ] if agents else None,
    )
    db.add(assistant_message)

    # Store agent reasoning details
    for agent in agents:
        reasoning = AgentReasoning(
            message_id=assistant_message.id,
            agent_name=agent["name"],
            reasoning_text=agent.get("reasoning", ""),
            confidence_score=agent.get("confidence", None),
        )
        db.add(reasoning)

    # Log message sent
    audit_log = AuditLog(
        user_id=user_id,
        action="message_sent",
        details={
            "conversation_id": conversation.id,
            "message_id": user_message.id,
            "model": model,
            "has_phi": phi.names or phi.ids or phi.emails or False,
        },
    )
    db.add(audit_log)

    # Update conversation model
    conversation.model = model
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assistant_message)

    # Format response with agent reasoning
    agent_reasoning = [
        AgentReasoningSchema(
            agent_name=r.agent_name,
            reasoning_text=r.reasoning_text,
            confidence_score=r.confidence_score,
        )
        for r in assistant_message.reasoning_details
    ]

    return MessageResponse(
        id=assistant_message.id,
        conversation_id=assistant_message.conversation_id,
        role=assistant_message.role,
        content=assistant_message.content,
        detected_phi=None,
        is_anonymized=False,
        model_used=model,
        agent_reasoning=agent_reasoning if agent_reasoning else None,
        created_at=assistant_message.created_at,
    )


def anonymize_message(
    db: Session,
    message_id: int,
    user_id: int,
) -> Dict[str, Any]:
    """Anonymize a message and store original"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == Conversation.id,
        Conversation.user_id == user_id,
    ).first()

    if not message:
        raise ValueError("Message not found")

    if message.role != "user":
        raise ValueError("Can only anonymize user messages")

    # Detect PHI again
    phi = phi_detector.detect_phi(message.content)

    # Anonymize
    anonymized, replacements = phi_detector.anonymize_text(message.content, phi)

    # Store original and mark as anonymized
    message.original_content = message.content
    message.content = anonymized
    message.is_anonymized = True

    # Log anonymization
    audit_log = AuditLog(
        user_id=user_id,
        action="anonymized",
        details={
            "message_id": message_id,
            "items_anonymized": len(replacements),
        },
    )
    db.add(audit_log)
    db.commit()

    return {
        "message_id": message_id,
        "anonymized_content": anonymized,
        "replacements": replacements,
    }


def get_conversation_context(
    db: Session,
    conversation_id: int,
    user_id: int,
    limit: int = 2,
) -> List[MessageResponse]:
    """Get the last N turns from a conversation"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.conversation.has(Conversation.user_id == user_id),
    ).order_by(Message.created_at.desc()).limit(limit * 2).all()

    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            detected_phi=msg.detected_phi,
            is_anonymized=msg.is_anonymized,
            model_used=msg.model_used,
            created_at=msg.created_at,
        )
        for msg in reversed(messages)
    ]
