Sure! Let’s go **step by step** and explain how the **Cockpit answer flows from your backend to the Vue frontend (`homeview.vue`)**.

---

## **1️⃣ User submits a message in the frontend**

In `homeview.vue`:

```javascript
<input v-model="userInput" @keyup.enter="sendMessage" ... />
<button @click="sendMessage">Send</button>
```

* When the user hits **Enter** or clicks **Send**, the `sendMessage()` function is triggered.
* `userInput.value` contains the user’s message.
* It immediately pushes the message to the `messages` array for **optimistic UI**, so the user sees their message instantly:

```javascript
messages.value.push({ role: 'user', content: text });
```

---

## **2️⃣ Frontend sends the request to backend**

Still inside `sendMessage()`:

```javascript
const res = await axios.post('http://localhost:8000/api/v1/chat/send', {
  session_id: currentSessionId.value,
  user_query: text
});
```

* `axios.post` sends a JSON payload containing:

```json
{
  "session_id": "<current session id>",
  "user_query": "<user's message>"
}
```

* The backend endpoint that receives this is:

```python
@router.post("/chat/send")
def send_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
```

---

## **3️⃣ Backend fetches context + calls Cockpit**

Inside `send_message()`:

1. **Retrieve last 5 messages** from the database:

```python
history = (
    db.query(ChatMessage)
    .filter(ChatMessage.session_id == req.session_id)
    .order_by(ChatMessage.id.desc())
    .limit(5)
    .all()
)
history = list(reversed(history))
```

2. **Format context for Cockpit**:

```python
context_str = ""
for msg in history:
    context_str += f"{msg.role.capitalize()}: {msg.content}\n"
```

Example `context_str`:

```
User: What were the decisions in the last meeting?
Assistant: The last meeting approved the project plan.
```

3. **Prepare payload for Cockpit**:

```python
full_prompt_payload = {
    "context_history": context_str,
    "current_query": req.user_query,
    "project_code": project_code
}
```

* This includes the **conversation history**, **user query**, and the **project code**.
* Then it’s converted to JSON:

```python
cockpit_input_str = json.dumps(full_prompt_payload)
```

4. **Call Cockpit workflow**:

```python
ai_response_text = CockpitRAG.run_workflow(cockpit_input_str)
```

* Cockpit runs the **RAG + final-answer workflow**:

  * Retrieves relevant meeting knowledge (`knowledge_chunks`) for that project.
  * Synthesizes a response based on context and user query.
  * Returns a **string** → this is `ai_response_text`.

---

## **4️⃣ Save messages to database**

After Cockpit responds:

```python
user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.user_query)
ai_msg = ChatMessage(session_id=req.session_id, role="assistant", content=ai_response_text)

db.add(user_msg)
db.add(ai_msg)
db.commit()
```

* Both the **user message** and the **AI response** are saved in the `ChatMessage` table for **future retrieval**.

---

## **5️⃣ Backend sends response to frontend**

Finally, the backend **returns the AI response** as JSON:

```python
return {"role": "assistant", "content": ai_response_text}
```

* Example JSON sent back:

```json
{
  "role": "assistant",
  "content": "The decisions in the [A100] S1 Chatbot Meeting were: ...\n- Approve initial chatbot flow\n- Assign design review task to Lee Sze Yuan"
}
```

---

## **6️⃣ Frontend receives response and updates UI**

Back in `homeview.vue`:

```javascript
messages.value.push(res.data);
```

* `res.data` is the JSON object returned by the backend.
* `messages.value` now contains **both the user message and the AI response**.
* Vue **reactively updates the chat window**, showing the new assistant message in the proper styling (white bubble for assistant, blue for user):

```vue
<div :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
  <div :class="['max-w-2xl px-5 py-3 rounded-2xl text-sm leading-6 shadow-sm', 
                msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white border text-gray-800 rounded-bl-none']">
    <p class="whitespace-pre-wrap font-sans">{{ msg.content }}</p>
  </div>
</div>
```

* While the response is loading, a **“Retrieving knowledge…”** placeholder is shown:

```vue
<div v-if="loading" class="flex justify-start mb-6">
   <div class="px-5 py-3 text-sm text-gray-500 bg-white border rounded-2xl animate-pulse">
     Retrieving knowledge...
   </div>
</div>
```

* Once `loading.value = false`, the placeholder disappears.

---

## ✅ **Flow Summary**

1. User types → `sendMessage()` → message pushed to UI.
2. Frontend sends `user_query + session_id` → backend `/chat/send`.
3. Backend fetches last 5 messages, formats context.
4. Backend calls `CockpitRAG.run_workflow()` → AI answer returned.
5. Backend saves user + AI messages to DB.
6. Backend returns JSON: `{"role":"assistant","content":<AI text>}`
7. Frontend pushes AI message to `messages.value` → chat UI updates.

---

In short:

**Frontend** → POST `user_query` → **Backend fetches context** → **Cockpit generates answer** → **Backend saves + returns answer** → **Frontend displays answer**.

---

If you want, I can also **draw a simple diagram of this flow**, showing **Frontend ↔ Backend ↔ Cockpit ↔ DB ↔ Frontend**, which helps a lot for documentation and debugging.

Do you want me to do that?
