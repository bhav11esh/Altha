#!/bin/bash

# Conversation Service Test Script
# This script tests all endpoints of the conversation service

set -e

API_URL="${API_URL:-http://localhost:8000}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Conversation Service Test Suite ===${NC}"
echo "API URL: $API_URL"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}[TEST 1] Health Check${NC}"
HEALTH=$(curl -s -X GET $API_URL/health)
echo "Response: $HEALTH"
echo ""

# Test 2: Start Conversation
echo -e "${YELLOW}[TEST 2] Start Conversation${NC}"
CONV_RESPONSE=$(curl -s -X POST $API_URL/conversations/start \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id_hash": "patient_test_12345",
    "doctor_id": "dr_alice_001"
  }')

CONV_ID=$(echo $CONV_RESPONSE | jq -r '.id')
echo "Created conversation ID: $CONV_ID"
echo "Response: $CONV_RESPONSE" | jq .
echo ""

# Test 3: Add First Turn with JSON Response
echo -e "${YELLOW}[TEST 3] Add First Turn (JSON Response)${NC}"
TURN1_RESPONSE=$(curl -s -X POST $API_URL/turns/add \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"user_input\": \"Patient reports persistent headache for 3 days, fever 38.5C, sensitivity to light\",
    \"ai_response\": \"{\\\"diagnosis\\": \\\"Migraine with fever\\", \\\"drugs\\": [\\\"Paracetamol 500mg twice daily\\", \\\"Ibuprofen 200mg if needed\\"], \\\"recommendations\\": [\\\"Rest in dark room\\", \\\"Stay well hydrated\\", \\\"Avoid screens\\"], \\\"labs\\": [\\\"Complete blood count\\", \\\"Blood culture test\\\"]}\\"
  }")

TURN1_ID=$(echo $TURN1_RESPONSE | jq -r '.turn_id')
TURN1_NUM=$(echo $TURN1_RESPONSE | jq -r '.turn_number')
echo "Created turn ID: $TURN1_ID (Turn #$TURN1_NUM)"
echo "Findings extracted: $(echo $TURN1_RESPONSE | jq '.findings_extracted | length')"
echo "Response: $TURN1_RESPONSE" | jq .
echo ""

# Test 4: Add Second Turn (with previous context)
echo -e "${YELLOW}[TEST 4] Add Second Turn (Text Response with Context)${NC}"
TURN2_RESPONSE=$(curl -s -X POST $API_URL/turns/add \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"user_input\": \"Fever subsided after medication but headache persists. Lab results: CBC normal, blood culture negative\",
    \"ai_response\": \"Based on test results showing no infection, this appears to be tension headache exacerbated by stress. Diagnosis: Tension-type headache. Recommend switching to Ibuprofen 200mg three times daily. Continue rest and hydration. Order follow-up appointment in 1 week.\"
  }")

TURN2_ID=$(echo $TURN2_RESPONSE | jq -r '.turn_id')
TURN2_NUM=$(echo $TURN2_RESPONSE | jq -r '.turn_number')
echo "Created turn ID: $TURN2_ID (Turn #$TURN2_NUM)"
echo "Context linked: $(echo $TURN2_RESPONSE | jq '.context_linked')"
echo "Response: $TURN2_RESPONSE" | jq .
echo ""

# Test 5: Get All Turns
echo -e "${YELLOW}[TEST 5] Get All Turns${NC}"
TURNS=$(curl -s -X GET $API_URL/turns/$CONV_ID)
TURN_COUNT=$(echo $TURNS | jq '. | length')
echo "Total turns: $TURN_COUNT"
echo "Response: $TURNS" | jq .
echo ""

# Test 6: Get Enriched Context for Turn 2
echo -e "${YELLOW}[TEST 6] Get Enriched Context for Turn 2${NC}"
CONTEXT=$(curl -s -X GET "$API_URL/context/$TURN2_ID?conversation_id=$CONV_ID")
echo "Response: $CONTEXT" | jq .
echo ""

# Test 7: Get All Findings
echo -e "${YELLOW}[TEST 7] Get All Findings${NC}"
FINDINGS=$(curl -s -X GET $API_URL/findings/$CONV_ID)
TOTAL_FINDINGS=$(echo $FINDINGS | jq '.total_findings')
echo "Total findings: $TOTAL_FINDINGS"
echo "Response: $FINDINGS" | jq .
echo ""

# Test 8: Get Audit Log for First Turn
echo -e "${YELLOW}[TEST 8] Get Audit Log for Turn 1${NC}"
AUDIT=$(curl -s -X GET $API_URL/audit/$TURN1_ID)
AUDIT_COUNT=$(echo $AUDIT | jq '. | length')
echo "Total audit entries: $AUDIT_COUNT"
echo "Response: $AUDIT" | jq .
echo ""

# Test 9: Get Conversation Audit Trail
echo -e "${YELLOW}[TEST 9] Get Conversation Audit Trail${NC}"
CONV_AUDIT=$(curl -s -X GET $API_URL/audit/conversation/$CONV_ID)
echo "Response: $CONV_AUDIT" | jq .
echo ""

# Test 10: Get Context Chains
echo -e "${YELLOW}[TEST 10] Get Context Chains${NC}"
CHAINS=$(curl -s -X GET $API_URL/context-chains/$CONV_ID)
echo "Response: $CHAINS" | jq .
echo ""

# Test 11: Get Findings by Type (Filter)
echo -e "${YELLOW}[TEST 11] Get Findings by Type${NC}"
DIAG_FINDINGS=$(curl -s -X GET "$API_URL/findings/$CONV_ID?finding_type=diagnosis")
echo "Response: $DIAG_FINDINGS" | jq .
echo ""

echo -e "${GREEN}=== All tests completed successfully ===${NC}"
echo ""
echo "Test Summary:"
echo "- Conversation ID: $CONV_ID"
echo "- Turn 1 ID: $TURN1_ID"
echo "- Turn 2 ID: $TURN2_ID"
echo "- Total turns: $TURN_COUNT"
echo "- Total findings: $TOTAL_FINDINGS"
