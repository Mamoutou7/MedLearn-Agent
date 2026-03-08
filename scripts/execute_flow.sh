#!/usr/bin/env bash

BASE_URL="http://127.0.0.1:8000/api/v1"

SESSION_ID=$(curl -s -X POST "$BASE_URL/sessions" | python -c 'import sys, json; print(json.load(sys.stdin)["session_id"])')
echo "SESSION_ID=$SESSION_ID"

echo
echo "== CHAT =="
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"question\":\"SIDA\"}" | python -m json.tool

echo
echo "== QUIZ APPROVAL =="
curl -s -X POST "$BASE_URL/quiz/approval" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"approved\":true}" | python -m json.tool

echo
echo "== QUIZ ANSWER =="
curl -s -X POST "$BASE_URL/quiz/answer" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"answer\":\"C\"}" | python -m json.tool