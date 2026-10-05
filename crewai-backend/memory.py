"""
Memory management for multi-turn conversations and audit trails.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field
import structlog

logger = structlog.get_logger()


@dataclass
class TurnContext:
    """Single turn context in a multi-turn conversation."""
    turn_id: str
    timestamp: str
    user_input: str
    agent_responses: Dict[str, str] = field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    decision_rationale: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CaseMemory:
    """Long-term memory for a patient case."""
    case_id: str
    patient_id: str
    created_at: str
    updated_at: str
    diagnosis_history: List[str] = field(default_factory=list)
    treatment_history: List[str] = field(default_factory=list)
    medication_history: List[Dict[str, Any]] = field(default_factory=list)
    lab_results: List[Dict[str, Any]] = field(default_factory=list)
    turns: List[TurnContext] = field(default_factory=list)
    
    def add_turn(self, turn: TurnContext) -> None:
        """Add a new turn to the memory."""
        self.turns.append(turn)
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_context_for_agent(self, agent_name: str, max_turns: int = 5) -> str:
        """Get relevant context from recent turns for an agent."""
        context = f"Patient ID: {self.patient_id}\n"
        context += f"Case ID: {self.case_id}\n"
        context += f"Created: {self.created_at}\n\n"
        
        # Add diagnosis history
        if self.diagnosis_history:
            context += f"Diagnosis History:\n"
            for dx in self.diagnosis_history[-3:]:
                context += f"  - {dx}\n"
            context += "\n"
        
        # Add recent medication history
        if self.medication_history:
            context += f"Current Medications:\n"
            for med in self.medication_history[-5:]:
                context += f"  - {med.get('name', '')}: {med.get('dose', '')} {med.get('frequency', '')}\n"
            context += "\n"
        
        # Add recent lab results
        if self.lab_results:
            context += f"Recent Lab Results:\n"
            for lab in self.lab_results[-3:]:
                context += f"  - {lab.get('test_name', '')}: {lab.get('value', '')} (Normal: {lab.get('normal_range', '')})\n"
            context += "\n"
        
        # Add recent turns
        recent_turns = self.turns[-max_turns:]
        if recent_turns:
            context += f"Recent Conversation ({len(recent_turns)} turns):\n"
            for turn in recent_turns:
                context += f"  Turn {turn.turn_id}:\n"
                context += f"    User: {turn.user_input[:100]}...\n" if len(turn.user_input) > 100 else f"    User: {turn.user_input}\n"
                context += f"    Rationale: {turn.decision_rationale[:100]}...\n" if turn.decision_rationale else ""
        
        return context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "patient_id": self.patient_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "diagnosis_history": self.diagnosis_history,
            "treatment_history": self.treatment_history,
            "medication_history": self.medication_history,
            "lab_results": self.lab_results,
            "turns": [turn.to_dict() for turn in self.turns],
        }


class MemoryManager:
    """Manages case memory and conversation context."""
    
    def __init__(self):
        self.cases: Dict[str, CaseMemory] = {}
    
    def create_case(self, case_id: str, patient_id: str) -> CaseMemory:
        """Create a new case memory."""
        now = datetime.utcnow().isoformat()
        case = CaseMemory(
            case_id=case_id,
            patient_id=patient_id,
            created_at=now,
            updated_at=now,
        )
        self.cases[case_id] = case
        logger.info("case_created", case_id=case_id, patient_id=patient_id)
        return case
    
    def get_case(self, case_id: str) -> Optional[CaseMemory]:
        """Retrieve case memory."""
        return self.cases.get(case_id)
    
    def add_turn_to_case(self, case_id: str, turn: TurnContext) -> None:
        """Add a turn to a case."""
        case = self.get_case(case_id)
        if case:
            case.add_turn(turn)
            logger.info("turn_added", case_id=case_id, turn_id=turn.turn_id)
    
    def update_diagnosis_history(self, case_id: str, diagnosis: str) -> None:
        """Update diagnosis history for a case."""
        case = self.get_case(case_id)
        if case:
            case.diagnosis_history.append(diagnosis)
            case.updated_at = datetime.utcnow().isoformat()
            logger.info("diagnosis_added", case_id=case_id, diagnosis=diagnosis)
    
    def update_medication_history(self, case_id: str, medication: Dict[str, Any]) -> None:
        """Update medication history for a case."""
        case = self.get_case(case_id)
        if case:
            case.medication_history.append(medication)
            case.updated_at = datetime.utcnow().isoformat()
            logger.info("medication_added", case_id=case_id, medication=medication.get("name", ""))
    
    def export_case(self, case_id: str) -> Optional[str]:
        """Export case as JSON string."""
        case = self.get_case(case_id)
        if case:
            return json.dumps(case.to_dict(), indent=2, default=str)
        return None
