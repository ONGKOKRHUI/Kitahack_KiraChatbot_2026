import requests

payload = {
    "meeting_id": "12345",
    "subject": "A100-S1-Chatbot-Meeting",
    "transcript_text": (
        "final_decision: [Meeting: A100-S1-Chatbot-Meeting | Date: 1-Jan-2026] "
        "{\"result\":\"### Decisions...\"} "
        "final_meeting_sum: [Meeting: A100...] {\"result\":\"### Summary...\"} "
        "final_actions: [Meeting: A100...] {\"result\":\"### Actions...\"}"
    )
}

res = requests.post("http://127.0.0.1:8000/webhook/meeting-end", json=payload)
print(res.json())

#just run python test_request.py to test