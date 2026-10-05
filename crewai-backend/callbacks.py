"""
Callback hooks for audit logging and monitoring.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog
import json

logger = structlog.get_logger()


class AuditLogger:
    """Audit trail for all medical decisions and recommendations."""
    
    def __init__(self):
        self.audit_log: Dict[str, List[Dict[str, Any]]] = {}
    
    def log_agent_action(
        self,
        case_id: str,
        agent_name: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        decision_rationale: str = "",
    ) -> None:
        """Log an agent action for audit trail."""
        if case_id not in self.audit_log:
            self.audit_log[case_id] = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "action": action,
            "input": input_data,
            "output": output_data or {},
            "rationale": decision_rationale,
        }
        
        self.audit_log[case_id].append(entry)
        logger.info(
            "audit_log",
            case_id=case_id,
            agent=agent_name,
            action=action,
            rationale=decision_rationale,
        )
    
    def log_tool_call(
        self,
        case_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a tool call for audit trail."""
        if case_id not in self.audit_log:
            self.audit_log[case_id] = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "tool_call",
            "tool": tool_name,
            "input": tool_input,
            "output": tool_output or {},
        }
        
        self.audit_log[case_id].append(entry)
        logger.info(
            "tool_call",
            case_id=case_id,
            tool=tool_name,
        )
    
    def log_critical_decision(
        self,
        case_id: str,
        agent_name: str,
        decision: str,
        justification: str,
        supporting_evidence: List[str],
    ) -> None:
        """Log critical medical decisions with full justification."""
        if case_id not in self.audit_log:
            self.audit_log[case_id] = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "critical_decision",
            "agent": agent_name,
            "decision": decision,
            "justification": justification,
            "supporting_evidence": supporting_evidence,
        }
        
        self.audit_log[case_id].append(entry)
        logger.warning(
            "critical_decision",
            case_id=case_id,
            agent=agent_name,
            decision=decision,
        )
    
    def log_error(
        self,
        case_id: str,
        agent_name: str,
        error_type: str,
        error_message: str,
        recovery_action: str = "",
    ) -> None:
        """Log errors and recovery actions."""
        if case_id not in self.audit_log:
            self.audit_log[case_id] = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error",
            "agent": agent_name,
            "error_type": error_type,
            "error_message": error_message,
            "recovery_action": recovery_action,
        }
        
        self.audit_log[case_id].append(entry)
        logger.error(
            "agent_error",
            case_id=case_id,
            agent=agent_name,
            error=error_message,
        )
    
    def get_audit_trail(self, case_id: str) -> List[Dict[str, Any]]:
        """Retrieve audit trail for a case."""
        return self.audit_log.get(case_id, [])
    
    def export_audit_trail(self, case_id: str) -> str:
        """Export audit trail as JSON."""
        return json.dumps(self.get_audit_trail(case_id), indent=2, default=str)
    
    def get_critical_decisions(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all critical decisions from audit log."""
        trail = self.get_audit_trail(case_id)
        return [entry for entry in trail if entry.get("type") == "critical_decision"]
    
    def get_agent_actions(self, case_id: str, agent_name: str) -> List[Dict[str, Any]]:
        """Get all actions by a specific agent."""
        trail = self.get_audit_trail(case_id)
        return [entry for entry in trail if entry.get("agent") == agent_name]


# Global audit logger instance
audit_logger = AuditLogger()
