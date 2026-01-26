Based on your provided code structure, README.md, and project architecture, here's a breakdown of the webhook trigger and Cockpit workflows. I'll reference specific files and code sections for clarity.

1. Webhook Trigger for Processing and Saving Meeting Transcripts (Ingestion Workflow)
Where It Happens: The webhook is defined in ingestion.py. This endpoint receives data from the Microsoft Teams Graph API when a meeting ends (e.g., via a "Meeting End" event).
Process:
The webhook checks if the meeting subject contains a specific [Project-Code] (filtering logic in the endpoint).
If valid, it fetches the transcript and metadata, formats a JSON payload, and calls Cockpit Workflow A (via CockpitClient.run_workflow in cockpit_client.py) to process the text into a mixed-format string (e.g., final_decision: ...).
The response is parsed using regex (in parser.py), vectorized (in vector_store.py using local embeddings like sentence-transformers), and stored in PostgreSQL (tables in knowledge.py).
Key Code Snippets:
Webhook endpoint: ingestion.py (look for @router.post("/webhook/meeting")).
Cockpit call: ingestion.py calls CockpitClient.run_workflow(input_json_string) with the formatted payload.
Storage: After parsing, it saves to DB using SQLAlchemy models (e.g., Meeting and KnowledgeChunk in knowledge.py).
Trigger Source: Externally from MS Graph API (not in your code), but your backend exposes the webhook URL for it to POST to.
2. Separate Cockpit Workflow for Answering User Questions (Chat/RAG Workflow)
Where It Happens: When a user sends a message in the chat UI (HomeView.vue), it calls POST /api/v1/chat/send in chat.py.
Process:
The backend assembles context (past chat history from DB), formats a payload ({"context_history": "...", "current_query": "..."}), and calls Cockpit Workflow B (the Chatbot, via the same CockpitClient.run_workflow in cockpit_client.py).
During Cockpit Workflow B's execution, it performs RAG by calling your backend's Search API to retrieve relevant knowledge chunks.
Where the 2nd Cockpit Workflow Calls the Database API:
The Search API is POST /api/v1/search/knowledge in search.py.
Cockpit Workflow B (externally configured in your Cockpit setup) makes an HTTP call to this endpoint with a query (e.g., {"query": "user question", "project_code": "..."}).
The endpoint uses VectorService.search (in vector_store.py) to query pgvector for similar chunks, then returns results to Cockpit.
Cockpit uses these chunks to generate the answer, which is sent back to your backend and saved/displayed.
Key Code Snippets:
Chat send: chat.py (look for @router.post("/chat/send") and the CockpitClient.run_workflow call).
Search endpoint: search.py (look for @router.post("/search/knowledge") and the vector search logic).
Vector search: vector_store.py (e.g., search method using pgvector similarity).
This setup ensures ingestion is async (webhook-triggered) and chat is real-time with RAG. If Cockpit's workflows are misconfigured externally, the calls will fail—verify your Cockpit setup matches these endpoints. Let me know if you need code excerpts or fixes!

Grok Code Fast 1 • 1x