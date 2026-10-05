from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from database import get_db, init_db
from models import Conversation, Turn, Finding
from schemas import (
    StartConversationRequest,
    AddTurnRequest,
    ConversationResponse,
    TurnResponse,
    FindingResponse,
    EnrichedContextResponse,
    FindingListResponse,
    AddTurnResponse,
    ErrorResponse,
    AuditLogResponse
)
from state_manager import StateManager
from turn_linker import TurnLinker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Conversation Service",
    description="Medical conversation context manager with finding extraction",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# ============ Health Check ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "conversation-service"}

# ============ Conversation Endpoints ============

@app.post(
    "/conversations/start",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Conversations"],
    summary="Start a new conversation"
)
async def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db)
):
    """Start a new conversation between a doctor and patient"""
    try:
        conversation = StateManager.create_conversation(
            db,
            patient_id_hash=request.patient_id_hash,
            doctor_id=request.doctor_id
        )
        logger.info(f"Created conversation {conversation.id} for patient {request.patient_id_hash}")
        
        return ConversationResponse.model_validate(conversation)
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

# ============ Turn Endpoints ============

@app.post(
    "/turns/add",
    response_model=AddTurnResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Turns"],
    summary="Add a new turn to conversation"
)
async def add_turn(
    request: AddTurnRequest,
    db: Session = Depends(get_db)
):
    """Add a new turn to a conversation with automatic context extraction"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )
        
        turn, findings, turn_number = StateManager.add_turn(
            db,
            conversation_id=request.conversation_id,
            user_input=request.user_input,
            ai_response=request.ai_response
        )
        
        logger.info(
            f"Added turn {turn_number} to conversation {request.conversation_id} "
            f"with {len(findings)} extracted findings"
        )
        
        return AddTurnResponse(
            turn_id=turn.id,
            conversation_id=turn.conversation_id,
            turn_number=turn_number,
            timestamp=turn.timestamp,
            findings_extracted=[FindingResponse.model_validate(f) for f in findings],
            context_linked=turn_number > 1
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding turn: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add turn"
        )

@app.get(
    "/turns/{conversation_id}",
    response_model=list[TurnResponse],
    tags=["Turns"],
    summary="Get all turns in a conversation"
)
async def get_conversation_turns(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all turns for a specific conversation in chronological order"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        turns = StateManager.get_conversation_turns(db, conversation_id)
        
        return [TurnResponse.model_validate(turn) for turn in turns]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting turns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve turns"
        )

# ============ Context & Finding Endpoints ============

@app.get(
    "/context/{turn_id}",
    tags=["Context"],
    summary="Get enriched context for a turn"
)
async def get_enriched_context(
    turn_id: UUID,
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get enriched context for a specific turn"""
    try:
        turn = db.query(Turn).filter(Turn.id == turn_id).first()
        if not turn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Turn {turn_id} not found"
            )
        
        context_data = StateManager.get_turn_enriched_context(db, turn_id, conversation_id)
        
        return {
            "conversation_id": str(conversation_id),
            "turn_id": str(turn_id),
            "context": context_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enriched context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve context"
        )

@app.get(
    "/findings/{conversation_id}",
    response_model=FindingListResponse,
    tags=["Findings"],
    summary="Get all findings in a conversation"
)
async def get_conversation_findings(
    conversation_id: UUID,
    finding_type: str = None,
    db: Session = Depends(get_db)
):
    """Get all extracted findings for a conversation"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        findings_data = StateManager.get_conversation_findings(db, conversation_id)
        
        if finding_type:
            findings_data['findings'] = [
                f for f in findings_data['findings']
                if f['type'] == finding_type
            ]
        
        return FindingListResponse(
            conversation_id=conversation_id,
            findings=[],
            total_findings=len(findings_data['findings']),
            by_type=findings_data['by_type']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting findings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve findings"
        )

# ============ Audit Log Endpoints ============

@app.get(
    "/audit/{turn_id}",
    response_model=list[AuditLogResponse],
    tags=["Audit"],
    summary="Get audit log for a turn"
)
async def get_turn_audit_log(
    turn_id: UUID,
    db: Session = Depends(get_db)
):
    """Get the immutable audit trail for a specific turn"""
    try:
        audit_logs = StateManager.get_audit_log(db, turn_id)
        
        return [
            AuditLogResponse(
                id=UUID(log['id']),
                turn_id=turn_id,
                action=log['action'],
                details=log['details'],
                timestamp=log['timestamp']
            )
            for log in audit_logs
        ]
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit log"
        )

@app.get(
    "/audit/conversation/{conversation_id}",
    tags=["Audit"],
    summary="Get audit trail for entire conversation"
)
async def get_conversation_audit_trail(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get the complete immutable audit trail for a conversation"""
    try:
        audit_logs = StateManager.get_conversation_audit_trail(db, conversation_id)
        
        return {
            "conversation_id": str(conversation_id),
            "total_entries": len(audit_logs),
            "audit_logs": audit_logs
        }
    except Exception as e:
        logger.error(f"Error getting conversation audit trail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit trail"
        )

# ============ Utility Endpoints ============

@app.get(
    "/context-chains/{conversation_id}",
    tags=["Analysis"],
    summary="Get finding chains and relationships"
)
async def get_context_chains(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get chains of related findings across turns"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        chains = TurnLinker.get_finding_chains(db, conversation_id)
        
        return {
            "conversation_id": str(conversation_id),
            "chains": chains
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting finding chains: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve finding chains"
        )

# ============ Error Handlers ============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Generic exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
