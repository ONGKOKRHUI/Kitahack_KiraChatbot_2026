## Instructions

3. How to Run the Complete Project
Follow these steps in order (based on your README.md and technical docs). Assumes you have Docker, Python, Bun/Node, and Git installed. Run in a terminal (e.g., VS Code integrated terminal).

Set Up and Start the Database (Phase 2):

Navigate to the database folder: cd database
Start Postgres with pgvector: docker-compose up -d
Verify: docker ps (should show meeting_knowledge_db).
Initialize tables: python ../backend/init_db.py (run from database or adjust path). You should see "Tables created successfully!"
Optional: Inspect DB connect to db : docker exec -it meeting_knowledge_db psql -U admin -d knowledge_base → Run \dt to confirm tables.
Set Up and Start the Backend (Phase 1/2):
 
Navigate to backend: cd ../backend
Install deps: pip install -r requirements.txt
Start FastAPI: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Verify: Open http://127.0.0.1:8000/docs (Swagger UI) to test endpoints like /api/v1/auth/token.
Test ingestion: Use python app/test_request.py or curl the webhook.
Set Up and Start the Frontend:

Navigate to frontend: cd ../frontend
Install deps: bun install (or npm install if not using Bun).
Start Vite dev server: bun dev (runs on http://localhost:5173).
Verify: Open the URL—Tailwind should now style the UI. Log in with admin/password (mock auth), then chat.
Full Workflow Test:

In frontend, log in → Select a project in Sidebar → Create a new chat → Send a message (e.g., "What are the decisions?").
Backend should call Cockpit (ensure your Cockpit API is running separately, as per your docs).
Check DB for saved messages: Use psql to query chat_messages.
Stop: docker-compose down (DB), Ctrl+C (backend/frontend).
Troubleshooting Tips:

If DB fails: Check .env and ports (5432).
If frontend APIs fail: Ensure backend is running and CORS allows localhost:5173.
If embeddings fail: Run python test_gpu.py to check MPS.
Logs: Check terminal output for errors.
Production: Use Docker Compose for all services (uncomment in docker-compose.yml).
If you apply these fixes and still encounter issues, share specific error messages or logs—I can refine further! Your project is solid once these are addressed.

Grok Code Fast 1 • 1x


#### Phase 1
- in from backend folder, run:  uvicorn app.main:app --reload
- go to swagger UI to test API at browser -> http://127.0.0.1:8000/docs

#### Phase 2
- go to database folder where docker-compose.yml sits
- run: docker-compose up -d
- create table by running: python backend/init_db.py
- wait until see Tables created successfully!
- run to check: docker exec -it meeting_knowledge_db psql -U admin -d knowledge_base
- use command \dt to see all tables

### **Project Architecture Overview**

The system is split into two distinct workflows: **Ingestion (Async)** and **Chat (Real-time)**. Your Python Backend acts as the "Traffic Controller" and "Memory Bank," while the Cockpit acts as the "Processor."

#### **1. The Ingestion Workflow (Meeting -> Knowledge)**

This runs automatically when a meeting ends.

1. **Trigger:** Microsoft Teams Graph API detects a "Meeting End" event.
2. **Filter (Python Backend):**
* Your script fetches the meeting `Subject`.
* **Condition:** Checks if `Subject` contains the specific `[Project-Code]`.
* *If False:* Stop.
* *If True:* Retrieve `Transcript` and `Metadata` (Date, Title, Type).


3. **Formatting (Python Backend):**
* Constructs the JSON string payload: `{"Title": "...", "Date": "...", "transcript": "..."}`.


4. **Processing (Cockpit Workflow A):**
* Python Backend calls **Cockpit API** (using the code you provided).
* Cockpit processes the text and returns the **Mixed-Format String** (`final_decision: ...`, `final_meeting_sum: ...`).


5. **Parsing & Storage (Python Backend):**
* Your Regex Parser (Phase 1) cleans this string into structured data.
* **Vectorization (Crucial):** Since you want `pgvector` but have no OpenAI API, the Python Backend will use a **local, offline library** (like `sentence-transformers` or `FastEmbed`) to turn these text chunks into vectors.
* **Storage:** Saves the Text + Metadata + Vector into PostgreSQL.



#### **2. The Chat Application Workflow (User -> Answer)**

This is the interactive web interface.

1. **Frontend (Vue.js):**
* **Login:** User authenticates (JWT).
* **Selection:** User picks a "Project" (e.g., Project A100) from a dropdown.
* **History:** Sidebar loads past conversation headers from the Python database.


2. **Orchestration (Python Backend):**
* Receives the user's message.
* **Context Assembly:** If the user is resuming an old chat, the Backend fetches the *entire* past conversation log from PostgreSQL and formats it as a context string.


3. **Reasoning (Cockpit Workflow B):**
* Python Backend calls a *different* **Cockpit Workflow** (The Chatbot).
* *Payload includes:* Current Question + Retrieved History Context.


4. **RAG Retrieval (Cockpit <-> Database):**
* *Note:* You mentioned the Cockpit "calls the database API."
* This implies your Python Backend must expose a **Search Endpoint** (`POST /api/search`).
* The Cockpit Workflow, during its execution, will hit this endpoint with a query to get relevant knowledge chunks from your `pgvector` store.


5. **Response:**
* Cockpit returns the final answer string.
* Python Backend saves the new User/Bot turn to the **Chat History Table**.
* Frontend displays the response.



---

### **Technology Stack & Tools**

| Component | Technology | Purpose |
| --- | --- | --- |
| **Frontend** | **Vue.js** (Tailwind CSS) | User Interface (Chat, Project Selection, Login). |
| **Backend API** | **FastAPI** (Python) | Orchestrates workflows, handles Auth, serves APIs. |
| **Database** | **PostgreSQL** + `pgvector` | Stores Knowledge Chunks (Vectors) and Chat Logs. |
| **Auth** | **JWT** (JSON Web Token) | Custom username/password authentication. |
| **AI Engine** | **Cockpit** (Dify-like) | **Workflow A:** Summarization. **Workflow B:** Chat/RAG. |
| **Embeddings** | **Sentence-Transformers** | *Local* Python library to generate vectors for `pgvector` without an API key. |
| **Integration** | **MS Graph API** | Fetching meeting transcripts. |

---

### **File Structure**

```txt
meeting-knowledge-automation/
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Application Entry Point
│   │   ├── core/                   # Core Infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Environment variables & Settings
│   │   │   ├── database.py         # DB connection & SessionLocal
│   │   │   └── security.py         # JWT Token & Password Hashing
│   │   ├── api/                    # API Route Controllers
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── ingestion.py    # Trigger, Webhook & Parsing endpoints
│   │   │       ├── chat.py         # RAG & Q&A endpoints
│   │   │       └── auth.py         # Login & User management
│   │   ├── services/               # Business Logic Layer
│   │   │   ├── __init__.py
│   │   │   ├── parser.py           # (Phase 1) Cockpit Regex Parser
│   │   │   ├── graph_connector.py  # MS Graph API interactions
│   │   │   └── vector_store.py     # Embedding generation & Search
│   │   ├── models/                 # Database Models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   └── knowledge.py        # Meeting & Chunk Tables
│   │   └── schemas/                # Pydantic Data Validation
│   │       ├── __init__.py
│   │       └── payload.py          # Request/Response schemas
│   ├── requirements.txt
│   └── .env                        # Secrets (DB URL, API Keys)
│
├── database/                       # Database Infrastructure
│   └── docker-compose.yml          # Postgres + pgvector configuration
│
├── frontend/                       # (Future Phase) Vue.js App
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── main.js
│   └── package.json
│
└── README.md
```


### **Workflow Summary (How it all connects)**

1. **User** clicks "New Chat" in Vue.js -> Calls `POST /chat/sessions`.
2. **User** types "What were the decisions?" -> Calls `POST /chat/send`.
3. **Python Backend**:
* Retrieves empty history (since it's new).
* Sends `{"context_history": "", "current_query": "What were the decisions?"}` to **Cockpit**.


4. **Cockpit**:
* Receives input.
* Needs facts? -> Calls your Python `POST /search/knowledge` API.
* Python API searches `pgvector` and returns chunks.
* Cockpit generates answer.


5. **Python Backend**:
* Receives answer.
* Saves "User: What..." and "Assistant: The decisions were..." to `chat_messages` table.
* Returns answer to Vue.js.



This completes the **Backend Architecture**. You now have:

* **Ingestion:** Teams -> Webhook -> Python -> Cockpit -> Parser -> Postgres (Vectors).
* **Search:** Cockpit -> Python Search API -> Postgres (Vectors).
* **Memory:** Vue -> Python Chat API -> Postgres (History) -> Cockpit.
