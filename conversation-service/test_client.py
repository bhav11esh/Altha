"""
Conversation Service Test Client

A Python client for testing the Conversation Service API with sample data.
Usage: python test_client.py
"""

import requests
import json
from typing import Optional
import time

class ConversationServiceClient:
    """Client for interacting with Conversation Service API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def health_check(self) -> dict:
        """Check service health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def start_conversation(self, patient_id_hash: str, doctor_id: str) -> dict:
        """Start a new conversation"""
        data = {
            "patient_id_hash": patient_id_hash,
            "doctor_id": doctor_id
        }
        response = self.session.post(
            f"{self.base_url}/conversations/start",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def add_turn(self, conversation_id: str, user_input: str, ai_response: str) -> dict:
        """Add a turn to a conversation"""
        data = {
            "conversation_id": conversation_id,
            "user_input": user_input,
            "ai_response": ai_response
        }
        response = self.session.post(
            f"{self.base_url}/turns/add",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_turns(self, conversation_id: str) -> list:
        """Get all turns in a conversation"""
        response = self.session.get(
            f"{self.base_url}/turns/{conversation_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_enriched_context(self, turn_id: str, conversation_id: str) -> dict:
        """Get enriched context for a turn"""
        params = {"conversation_id": conversation_id}
        response = self.session.get(
            f"{self.base_url}/context/{turn_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_findings(self, conversation_id: str, finding_type: Optional[str] = None) -> dict:
        """Get all findings in a conversation"""
        params = {}
        if finding_type:
            params["finding_type"] = finding_type
        
        response = self.session.get(
            f"{self.base_url}/findings/{conversation_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_audit_log(self, turn_id: str) -> list:
        """Get audit log for a turn"""
        response = self.session.get(
            f"{self.base_url}/audit/{turn_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_conversation_audit_trail(self, conversation_id: str) -> dict:
        """Get audit trail for entire conversation"""
        response = self.session.get(
            f"{self.base_url}/audit/conversation/{conversation_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_context_chains(self, conversation_id: str) -> dict:
        """Get finding chains"""
        response = self.session.get(
            f"{self.base_url}/context-chains/{conversation_id}"
        )
        response.raise_for_status()
        return response.json()


def run_demo():
    """Run a demonstration of the Conversation Service"""
    
    print("=" * 60)
    print("CONVERSATION SERVICE DEMO")
    print("=" * 60)
    print()
    
    client = ConversationServiceClient()
    
    # Test 1: Health Check
    print("[1] Health Check")
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
        print()
    except Exception as e:
        print(f"ERROR: {e}")
        print()
        return
    
    # Test 2: Start Conversation
    print("[2] Starting Conversation")
    conv = client.start_conversation(
        patient_id_hash="demo_patient_001",
        doctor_id="dr_smith_001"
    )
    conv_id = conv['id']
    print(f"Conversation ID: {conv_id}")
    print(f"Created at: {conv['created_at']}")
    print()
    
    # Test 3: Add First Turn (JSON Response)
    print("[3] Adding First Turn - JSON Response Format")
    ai_response_json = json.dumps({
        "diagnosis": "Upper respiratory tract infection",
        "drugs": [
            "Amoxicillin 500mg three times daily",
            "Paracetamol 500mg for fever"
        ],
        "recommendations": [
            "Rest for 2-3 days",
            "Increase fluid intake",
            "Use saline nasal drops"
        ],
        "labs": [
            "Throat swab for culture",
            "Complete blood count"
        ]
    })
    
    turn1 = client.add_turn(
        conversation_id=conv_id,
        user_input="Patient has sore throat, cough, and mild fever (37.8C) for 2 days",
        ai_response=ai_response_json
    )
    turn1_id = turn1['turn_id']
    print(f"Turn 1 ID: {turn1_id}")
    print(f"Turn Number: {turn1['turn_number']}")
    print(f"Findings Extracted: {len(turn1['findings_extracted'])}")
    for finding in turn1['findings_extracted']:
        print(f"  - {finding['finding_type']}: {finding['value']}")
    print()
    
    # Test 4: Add Second Turn (Text Response)
    print("[4] Adding Second Turn - Text Response Format")
    ai_response_text = """
    The patient's condition has improved slightly. Lab results show bacterial infection.
    Diagnosis: Acute pharyngitis with bacterial infection
    Continue with Amoxicillin as prescribed
    Recommend throat lozenges for pain relief
    Follow-up appointment in 3 days
    Order: Repeat throat culture if symptoms persist
    """
    
    turn2 = client.add_turn(
        conversation_id=conv_id,
        user_input="Follow-up: Throat pain reduced. Lab results came back showing bacterial infection",
        ai_response=ai_response_text
    )
    turn2_id = turn2['turn_id']
    print(f"Turn 2 ID: {turn2_id}")
    print(f"Turn Number: {turn2['turn_number']}")
    print(f"Context Linked: {turn2['context_linked']}")
    print(f"Findings Extracted: {len(turn2['findings_extracted'])}")
    print()
    
    # Small delay
    time.sleep(1)
    
    # Test 5: Get All Turns
    print("[5] Getting All Turns")
    turns = client.get_turns(conv_id)
    print(f"Total Turns: {len(turns)}")
    for turn in turns:
        print(f"  Turn {turn['turn_number']}: {len(turn['findings'])} findings")
    print()
    
    # Test 6: Get Enriched Context
    print("[6] Getting Enriched Context for Turn 2")
    context = client.get_enriched_context(turn2_id, conv_id)
    ctx = context['context']
    print(f"Current Findings: {len(ctx['current_findings'])}")
    print(f"Previous Findings: {len(ctx['previous_findings'])}")
    print(f"Related Findings (Exact): {len(ctx['related_findings']['exact_matches'])}")
    print(f"Related Findings (Semantic): {len(ctx['related_findings']['semantic_matches'])}")
    print()
    
    # Test 7: Get All Findings
    print("[7] Getting All Findings")
    findings = client.get_findings(conv_id)
    print(f"Total Findings: {findings['total_findings']}")
    print("By Type:")
    for ftype, count in findings['by_type'].items():
        print(f"  {ftype}: {count}")
    print()
    
    # Test 8: Get Audit Log
    print("[8] Getting Audit Log for Turn 1")
    audit = client.get_audit_log(turn1_id)
    print(f"Audit Entries: {len(audit)}")
    for entry in audit:
        print(f"  - {entry['action']} @ {entry['timestamp']}")
    print()
    
    # Test 9: Get Conversation Audit Trail
    print("[9] Getting Conversation Audit Trail")
    conv_audit = client.get_conversation_audit_trail(conv_id)
    print(f"Total Audit Entries: {conv_audit['total_entries']}")
    print()
    
    # Test 10: Get Context Chains
    print("[10] Getting Context Chains")
    chains = client.get_context_chains(conv_id)
    chain_data = chains['chains']
    print(f"Diagnosis to Treatment: {len(chain_data['diagnosis_to_treatment'])}")
    print(f"Diagnosis to Lab: {len(chain_data['diagnosis_to_lab'])}")
    print(f"All Findings Timeline: {len(chain_data['all_findings_timeline'])}")
    print()
    
    print("=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
