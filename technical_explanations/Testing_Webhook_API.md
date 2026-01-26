### To Test API request

in the backend/end -> same folder as main.py -> run: uvicorn main:app --reload
Command	What Happens
python main.py	Runs the script. Inside it, uvicorn starts once, no reload.
uvicorn main:app --reload	Uvicorn loads FastAPI only, watches file changes, restarts automatically.

1) 
- in the backend/end -> same folder as main.py -> run: uvicorn main:app --reload
- go to swagger UI to test API at browser -> http://127.0.0.1:8000/docs
- we can see POST /webhook/meeting-end
- test with a request body for example:
{
  "meeting_id": "12345",
  "subject": "A100-S1-Chatbot-Meeting",
  "transcript_text": "final_decision: [Meeting: A100-S1-Chatbot-Meeting | Date: 1-Jan-2026] {\"result\":\"### Decisions...\n- Focus on rolling out...\"} final_meeting_sum: [Meeting: A100...] {\"result\":\"### Summary...\"} final_actions: [Meeting: A100...] {\"result\":\"### Actions...\"}"
}
- we get a curl format and a response body

2) 
curl -X POST "http://127.0.0.1:8000/webhook/meeting-end" \
-H "Content-Type: application/json" \
-d '{
  "meeting_id": "12345",
  "subject": "A100-S1-Chatbot-Meeting",
  "transcript_text": "final_decision: [Meeting: A100-S1-Chatbot-Meeting | Date: 1-Jan-2026] {\"result\":\"### Decisions...\"} final_meeting_sum: [Meeting: A100...] {\"result\":\"### Summary...\"} final_actions: [Meeting: A100...] {\"result\":\"### Actions...\"}"
}'

3) Python Script -> test_request.py
response: 
{
  "status": "success",
  "processed_chunks": {
    "decisions": {
      "metadata": {
        "Meeting": "A100-S1-Chatbot-Meeting",
        "Date": "1-Jan-2026"
      },
      "content": []
    },
    "summary": {
      "metadata": {},
      "content": [
        "### Summary..."
      ]
    },
    "actions": {
      "metadata": {},
      "content": [
        "### Actions..."
      ]
    }
  }
}
