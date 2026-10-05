from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models import Conversation, Turn, Finding, AuditLog
from schemas import ExtractedFinding
from context_extractor import ContextExtractor
from turn_linker import TurnLinker
import json

class StateManager:
    """Manage conversation state persistence"""

    @staticmethod
    def create_conversation(db: Session, patient_id_hash: str, doctor_id: str) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            patient_id_hash=patient_id_hash,
            doctor_id=doctor_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def add_turn(
        db: Session,
        conversation_id: UUID,
        user_input: str,
        ai_response: str
    ) -> tuple[Turn, List[Finding], int]:
        """Add a new turn to a conversation with context extraction"""
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        last_turn = db.query(Turn).filter(
            Turn.conversation_id == conversation_id
        ).order_by(Turn.turn_number.desc()).first()
        
        turn_number = (last_turn.turn_number + 1) if last_turn else 1
        
        parsed_json, cleaned_response = ContextExtractor.parse_ai_response(ai_response)
        
        extracted_findings = ContextExtractor.extract_findings(ai_response, parsed_json)
        
        turn = Turn(
            conversation_id=conversation_id,
            turn_number=turn_number,
            user_input=user_input,
            ai_response=ai_response,
            ai_response_json=parsed_json
        )
        db.add(turn)
        db.flush()
        
        created_findings = []
        for extracted_finding in extracted_findings:
            finding = Finding(
                conversation_id=conversation_id,
                turn_id=turn.id,
                finding_type=extracted_finding.finding_type,
                value=extracted_finding.value,
                confidence=extracted_finding.confidence,
                metadata=extracted_finding.metadata
            )
            db.add(finding)
            created_findings.append(finding)
        
        db.flush()
        
        if created_findings:
            audit_log = AuditLog(
                turn_id=turn.id,
                action="findings_extracted",
                details={
                    "count": len(created_findings),
                    "types": [str(f.finding_type) for f in created_findings]
                }
            )
            db.add(audit_log)
        
        audit_log = AuditLog(
            turn_id=turn.id,
            action="turn_created",
            details={
                "turn_number": turn_number,
                "has_previous_context": turn_number > 1
            }
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(turn)
        
        return turn, created_findings, turn_number

    @staticmethod
    def get_conversation_turns(db: Session, conversation_id: UUID) -> List[Turn]:
        """Get all turns for a conversation"""
        turns = db.query(Turn).filter(
            Turn.conversation_id == conversation_id
        ).order_by(Turn.turn_number.asc()).all()
        
        return turns

    @staticmethod
    def get_turn_enriched_context(
        db: Session,
        turn_id: UUID,
        conversation_id: UUID
    ) -> Dict:
        """Get enriched context for a specific turn"""
        turn = db.query(Turn).filter(Turn.id == turn_id).first()
        if not turn:
            raise ValueError(f"Turn {turn_id} not found")
        
        previous_findings = TurnLinker.get_previous_findings(
            db, conversation_id, turn.turn_number
        )
        
        current_findings = db.query(Finding).filter(
            Finding.turn_id == turn_id
        ).all()
        
        extracted_findings = [
            ExtractedFinding(
                finding_type=f.finding_type,
                value=f.value,
                confidence=f.confidence,
                metadata=f.metadata
            )
            for f in current_findings
        ]
        
        related = TurnLinker.find_related_findings(
            db, conversation_id, extracted_findings
        )
        
        context = {
            'turn_id': str(turn_id),
            'turn_number': turn.turn_number,
            'timestamp': turn.timestamp.isoformat(),
            'current_findings': [
                {
                    'id': str(f.id),
                    'type': str(f.finding_type),
                    'value': f.value,
                    'confidence': f.confidence
                }
                for f in current_findings
            ],
            'previous_findings': [
                {
                    'id': str(f.id),
                    'type': str(f.finding_type),
                    'value': f.value,
                    'confidence': f.confidence,
                    'from_turn': f.turn.turn_number
                }
                for f in previous_findings[:10]
            ],
            'related_findings': {
                'exact_matches': [
                    {
                        'id': str(f.id),
                        'type': str(f.finding_type),
                        'value': f.value,
                        'from_turn': f.turn.turn_number
                    }
                    for f in related['exact_matches']
                ],
                'semantic_matches': [
                    {
                        'id': str(f.id),
                        'type': str(f.finding_type),
                        'value': f.value,
                        'from_turn': f.turn.turn_number
                    }
                    for f in related['semantic_matches']
                ]
            },
            'conversation_context': TurnLinker.build_turn_context(
                db, conversation_id, turn.turn_number
            )
        }
        
        return context

    @staticmethod
    def get_conversation_findings(
        db: Session,
        conversation_id: UUID
    ) -> Dict:
        """Get all findings for a conversation grouped by type"""
        findings = db.query(Finding).filter(
            Finding.conversation_id == conversation_id
        ).order_by(Finding.created_at.desc()).all()
        
        result = {
            'conversation_id': str(conversation_id),
            'total_findings': len(findings),
            'by_type': {},
            'findings': []
        }
        
        for finding in findings:
            ftype = finding.finding_type.value
            if ftype not in result['by_type']:
                result['by_type'][ftype] = 0
            result['by_type'][ftype] += 1
            
            result['findings'].append({
                'id': str(finding.id),
                'type': ftype,
                'value': finding.value,
                'confidence': finding.confidence,
                'from_turn': finding.turn.turn_number,
                'created_at': finding.created_at.isoformat()
            })
        
        return result

    @staticmethod
    def get_audit_log(
        db: Session,
        turn_id: UUID
    ) -> List[Dict]:
        """Get audit log for a turn"""
        logs = db.query(AuditLog).filter(
            AuditLog.turn_id == turn_id
        ).order_by(AuditLog.timestamp.asc()).all()
        
        return [
            {
                'id': str(log.id),
                'action': log.action,
                'details': log.details,
                'timestamp': log.timestamp.isoformat()
            }
            for log in logs
        ]

    @staticmethod
    def get_conversation_audit_trail(
        db: Session,
        conversation_id: UUID
    ) -> List[Dict]:
        """Get complete audit trail for a conversation"""
        logs = db.query(AuditLog).join(Turn).filter(
            Turn.conversation_id == conversation_id
        ).order_by(AuditLog.timestamp.asc()).all()
        
        return [
            {
                'id': str(log.id),
                'turn_number': log.turn.turn_number,
                'action': log.action,
                'details': log.details,
                'timestamp': log.timestamp.isoformat()
            }
            for log in logs
        ]
