import json
import re
from typing import List, Tuple, Optional, Dict, Any
from models import FindingType
from schemas import ExtractedFinding

class ContextExtractor:
    """Extract structured findings from AI responses"""

    @staticmethod
    def parse_ai_response(response_text: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Parse AI response as JSON or plain text"""
        response_text = response_text.strip()
        
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return parsed, response_text
            except json.JSONDecodeError:
                pass
        
        return None, response_text

    @staticmethod
    def extract_findings(ai_response: str, parsed_json: Optional[Dict]) -> List[ExtractedFinding]:
        """Extract findings from AI response"""
        findings = []
        
        if parsed_json:
            findings.extend(ContextExtractor._extract_from_json(parsed_json))
        
        findings.extend(ContextExtractor._extract_from_text(ai_response))
        
        unique_findings = {}
        for finding in findings:
            key = (finding.finding_type, finding.value)
            if key not in unique_findings or finding.confidence > unique_findings[key].confidence:
                unique_findings[key] = finding
        
        return list(unique_findings.values())

    @staticmethod
    def _extract_from_json(parsed_json: Dict) -> List[ExtractedFinding]:
        """Extract findings from parsed JSON"""
        findings = []
        
        key_mappings = {
            'diagnosis': FindingType.DIAGNOSIS,
            'diagnoses': FindingType.DIAGNOSIS,
            'condition': FindingType.DIAGNOSIS,
            'drug': FindingType.DRUG,
            'drugs': FindingType.DRUG,
            'medication': FindingType.DRUG,
            'medications': FindingType.DRUG,
            'lab': FindingType.LAB,
            'labs': FindingType.LAB,
            'test': FindingType.LAB,
            'tests': FindingType.LAB,
            'recommendation': FindingType.RECOMMENDATION,
            'recommendations': FindingType.RECOMMENDATION,
            'advice': FindingType.RECOMMENDATION,
        }
        
        for key, value in parsed_json.items():
            key_lower = key.lower()
            
            finding_type = None
            for json_key, ftype in key_mappings.items():
                if json_key in key_lower:
                    finding_type = ftype
                    break
            
            if finding_type:
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            text = item.get('name') or item.get('value') or str(item)
                            confidence = float(item.get('confidence', 1.0))
                            findings.append(ExtractedFinding(
                                finding_type=finding_type,
                                value=str(text),
                                confidence=confidence,
                                metadata=item if isinstance(item, dict) else None
                            ))
                        else:
                            findings.append(ExtractedFinding(
                                finding_type=finding_type,
                                value=str(item),
                                confidence=1.0
                            ))
                elif isinstance(value, dict):
                    text = value.get('name') or value.get('value') or str(value)
                    confidence = float(value.get('confidence', 1.0))
                    findings.append(ExtractedFinding(
                        finding_type=finding_type,
                        value=str(text),
                        confidence=confidence,
                        metadata=value
                    ))
                else:
                    findings.append(ExtractedFinding(
                        finding_type=finding_type,
                        value=str(value),
                        confidence=1.0
                    ))
        
        return findings

    @staticmethod
    def _extract_from_text(text: str) -> List[ExtractedFinding]:
        """Extract findings from plain text using pattern matching"""
        findings = []
        
        patterns = {
            FindingType.DIAGNOSIS: [
                r'(?:diagnosed? with|diagnosis:?)\s+([^.,\n]+)',
                r'(?:condition|disease|disorder):?\s+([^.,\n]+)',
                r'Patient has\s+([^.,\n]+)',
            ],
            FindingType.DRUG: [
                r'(?:prescribe|medication|drug):?\s+([^.,\n]+)',
                r'(?:take|administer)\s+([^.,\n]+)',
                r'Recommend\s+(?:taking|using)\s+([^.,\n]+)',
            ],
            FindingType.LAB: [
                r'(?:lab|test|result):?\s+([^.,\n]+)',
                r'(?:order|request)\s+(?:lab|test)\s+([^.,\n]+)',
                r'Check\s+([^.,\n]+)',
            ],
            FindingType.RECOMMENDATION: [
                r'(?:recommend|suggest):?\s+([^.,\n]+)',
                r'Patient should\s+([^.,\n]+)',
                r'Advise\s+(?:patient\s+)?(?:to\s+)?([^.,\n]+)',
            ]
        }
        
        for finding_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()
                    if value and len(value) > 3:
                        findings.append(ExtractedFinding(
                            finding_type=finding_type,
                            value=value,
                            confidence=0.7
                        ))
        
        return findings

    @staticmethod
    def get_conversation_context(findings_history: List[ExtractedFinding]) -> Dict[str, Any]:
        """Build context summary from findings history"""
        context = {
            'diagnoses': [],
            'drugs': [],
            'labs': [],
            'recommendations': []
        }
        
        for finding in findings_history:
            if finding.finding_type == FindingType.DIAGNOSIS:
                context['diagnoses'].append(finding.value)
            elif finding.finding_type == FindingType.DRUG:
                context['drugs'].append(finding.value)
            elif finding.finding_type == FindingType.LAB:
                context['labs'].append(finding.value)
            elif finding.finding_type == FindingType.RECOMMENDATION:
                context['recommendations'].append(finding.value)
        
        return context
