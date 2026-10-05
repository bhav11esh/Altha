from typing import List, Dict, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from models import Turn, Finding, FindingType
from schemas import ExtractedFinding

class TurnLinker:
    """Link current turn findings to previous context and findings"""

    @staticmethod
    def get_previous_findings(db: Session, conversation_id: UUID, current_turn_number: int) -> List[Finding]:
        """Get all findings from previous turns"""
        previous_findings = (
            db.query(Finding)
            .join(Turn)
            .filter(
                Turn.conversation_id == conversation_id,
                Turn.turn_number < current_turn_number
            )
            .order_by(Turn.turn_number.desc(), Finding.created_at.desc())
            .all()
        )
        return previous_findings

    @staticmethod
    def find_related_findings(
        db: Session,
        conversation_id: UUID,
        new_findings: List[ExtractedFinding],
        confidence_threshold: float = 0.5
    ) -> Dict[str, List[Finding]]:
        """Find related previous findings that match the new findings"""
        related = {
            'exact_matches': [],
            'semantic_matches': [],
            'by_type': {}
        }
        
        previous_findings = (
            db.query(Finding)
            .join(Turn)
            .filter(
                Turn.conversation_id == conversation_id,
                Finding.confidence >= confidence_threshold
            )
            .all()
        )
        
        for prev_finding in previous_findings:
            ftype = str(prev_finding.finding_type)
            if ftype not in related['by_type']:
                related['by_type'][ftype] = []
            related['by_type'][ftype].append(prev_finding)
        
        for new_finding in new_findings:
            ftype = str(new_finding.finding_type)
            
            for prev_finding in previous_findings:
                if prev_finding.finding_type == new_finding.finding_type:
                    if TurnLinker._is_similar(prev_finding.value, new_finding.value):
                        if prev_finding not in related['exact_matches']:
                            related['exact_matches'].append(prev_finding)
                    elif TurnLinker._is_semantically_similar(prev_finding.value, new_finding.value):
                        if prev_finding not in related['semantic_matches']:
                            related['semantic_matches'].append(prev_finding)
        
        return related

    @staticmethod
    def _is_similar(value1: str, value2: str, similarity_threshold: float = 0.8) -> bool:
        """Check if two values are similar"""
        v1_lower = value1.lower().strip()
        v2_lower = value2.lower().strip()
        
        if v1_lower == v2_lower:
            return True
        
        if v1_lower in v2_lower or v2_lower in v1_lower:
            return True
        
        return False

    @staticmethod
    def _is_semantically_similar(value1: str, value2: str) -> bool:
        """Check if two values are semantically similar"""
        v1_lower = value1.lower().strip()
        v2_lower = value2.lower().strip()
        
        words1 = set(v1_lower.split())
        words2 = set(v2_lower.split())
        
        if not words1 or not words2:
            return False
        
        overlap = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity_score = len(overlap) / len(union) if union else 0
        return similarity_score > 0.5

    @staticmethod
    def build_turn_context(
        db: Session,
        conversation_id: UUID,
        current_turn_number: int,
        limit_previous: int = 10
    ) -> Dict:
        """Build enriched context for a turn"""
        previous_findings = TurnLinker.get_previous_findings(
            db, conversation_id, current_turn_number
        )
        
        context = {
            'previous_findings_count': len(previous_findings),
            'by_type': {
                'diagnosis': [],
                'drug': [],
                'lab': [],
                'recommendation': []
            },
            'timeline': []
        }
        
        for finding in previous_findings[:limit_previous]:
            ftype_key = finding.finding_type.value
            context['by_type'][ftype_key].append({
                'value': finding.value,
                'confidence': finding.confidence,
                'from_turn': finding.turn.turn_number,
                'created_at': finding.created_at.isoformat()
            })
            context['timeline'].append({
                'turn': finding.turn.turn_number,
                'type': ftype_key,
                'value': finding.value
            })
        
        return context

    @staticmethod
    def get_finding_chains(
        db: Session,
        conversation_id: UUID
    ) -> Dict[str, List[Dict]]:
        """Get chains of related findings across turns"""
        all_findings = (
            db.query(Finding)
            .join(Turn)
            .filter(Turn.conversation_id == conversation_id)
            .order_by(Turn.turn_number.asc(), Finding.created_at.asc())
            .all()
        )
        
        chains = {
            'diagnosis_to_treatment': [],
            'diagnosis_to_lab': [],
            'lab_to_diagnosis': [],
            'all_findings_timeline': []
        }
        
        for finding in all_findings:
            chains['all_findings_timeline'].append({
                'turn': finding.turn.turn_number,
                'type': finding.finding_type.value,
                'value': finding.value,
                'confidence': finding.confidence
            })
        
        diagnoses = [f for f in all_findings if f.finding_type == FindingType.DIAGNOSIS]
        drugs = [f for f in all_findings if f.finding_type == FindingType.DRUG]
        labs = [f for f in all_findings if f.finding_type == FindingType.LAB]
        
        for diag in diagnoses:
            for drug in drugs:
                if drug.turn.turn_number > diag.turn.turn_number:
                    chains['diagnosis_to_treatment'].append({
                        'diagnosis': diag.value,
                        'diagnosis_turn': diag.turn.turn_number,
                        'treatment': drug.value,
                        'treatment_turn': drug.turn.turn_number,
                        'gap_turns': drug.turn.turn_number - diag.turn.turn_number
                    })
                    break
        
        for diag in diagnoses:
            for lab in labs:
                if lab.turn.turn_number > diag.turn.turn_number:
                    chains['diagnosis_to_lab'].append({
                        'diagnosis': diag.value,
                        'diagnosis_turn': diag.turn.turn_number,
                        'lab': lab.value,
                        'lab_turn': lab.turn.turn_number,
                        'gap_turns': lab.turn.turn_number - diag.turn.turn_number
                    })
                    break
        
        return chains
