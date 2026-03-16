# QWEN.md — LLM Chatbot Project


## Project Overview
A ChatGPT-style conversational AI app powered by a **local Ollama LLM** (`qwen3.5:0.8b`). 
Users can start new chats, switch between past conversations, and have persistent history — all via a clean two-panel UI.


---


## Tech Stack


| Layer      | Technology                     |
|------------|-------------------------------|
| Frontend   | Streamlit                     |
| Backend    | FastAPI                       |
| LLM        | Ollama (local) — `qwen3.5:0.8b` |
| Database   | SQLite (via `aiosqlite`)      |
| Package Mgr| `uv`                          |


---


## Project Structure
```
llm-chatbot/
├── QWEN.md
├── pyproject.toml          # uv project file
├── .python-version
├── backend/
│   ├── main.py             # FastAPI app entry point
│   ├── database.py         # SQLite setup & queries (aiosqlite)
│   ├── models.py           # Pydantic request/response schemas
│   ├── routers/
│   │   ├── chats.py        # CRUD endpoints for chat sessions
│   │   └── messages.py     # Send message, stream response
│   └── llm.py              # Ollama client wrapper
├── frontend/
│   └── app.py              # Streamlit UI
└── README.md
```


---


## Database Schema (SQLite)


### `chat_sessions`
| Column       | Type    | Notes                  |
|--------------|---------|------------------------|
| id           | INTEGER | Primary key, autoincrement |
| title        | TEXT    | Auto-generated from first message |
| created_at   | TEXT    | ISO timestamp          |
| updated_at   | TEXT    | ISO timestamp          |


### `messages`
| Column       | Type    | Notes                              |
|--------------|---------|-------------------------------------|
| id           | INTEGER | Primary key, autoincrement          |
| session_id   | INTEGER | FK → chat_sessions.id               |
| role         | TEXT    | `"user"` or `"assistant"`           |
| content      | TEXT    | Message text                        |
| created_at   | TEXT    | ISO timestamp                       |


---


## API Endpoints (FastAPI)


### Chats
- `GET    /chats`              — List all chat sessions (id, title, updated_at)
- `POST   /chats`              — Create new chat session → returns session id
- `DELETE /chats/{id}`         — Delete chat session + all its messages
- `PATCH  /chats/{id}/title`   — Rename a chat


### Messages
- `GET    /chats/{id}/messages`     — Fetch full message history for a session
- `POST   /chats/{id}/messages`     — Send a user message; streams back LLM response (SSE)


---


## LLM Integration (Ollama)


- **Model**: `qwen3.5:0.8b`
- **Mode**: Streaming via `httpx` or `ollama` Python SDK
- **Endpoint**: `http://localhost:11434/api/chat`
- Send full conversation history as context in every request
- Stream tokens back to Streamlit via **SSE (Server-Sent Events)**


---


## Frontend Layout (Streamlit)
```
┌─────────────────────────────────────────────────┐
│  Left Sidebar (300px)   │  Right Main Area       │
│  ─────────────────────  │  ──────────────────── │
│  [+ New Chat]           │  Chat messages          │
│                         │  (user = right bubble)  │
│  Chat History List:     │  (AI = left bubble)     │
│  • Chat 1 (today)       │                         │
│  • Chat 2 (yesterday)   │  [Streaming response]   │
│  • Chat 3               │                         │
│  ...                    │  ─────────────────────  │
│                         │  [ Type a message... ] [Send] │
└─────────────────────────────────────────────────┘
```


- Sidebar: scrollable list of past chats, clickable to switch
- "+ New Chat" button at top of sidebar
- Main area: scrollable message thread with role-based bubble styling
- Input: `st.chat_input` pinned at bottom
- Streaming: use `st.write_stream` to display tokens as they arrive
- State: `st.session_state` holds `current_session_id` and in-memory messages


---


## Key Behaviors


1. **New Chat**: Creates a session via `POST /chats`, title = "New Chat" until first message sent
2. **Auto-title**: After first message, title = first 40 chars of user message (PATCH via API)
3. **Switch Chat**: Clicking a sidebar item sets `current_session_id`, loads messages from `GET /chats/{id}/messages`
4. **Streaming**: FastAPI uses `StreamingResponse` with `text/event-stream`; Streamlit consumes with `requests` streaming iterator
5. **Delete Chat**: Trash icon next to each sidebar chat item → calls `DELETE /chats/{id}`


---


## Setup & Run
```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh


# 2. Init project
uv init llm-chatbot
cd llm-chatbot


# 3. Add dependencies
uv add fastapi uvicorn aiosqlite httpx streamlit requests pydantic


# 4. Start Ollama (separate terminal)
ollama serve
ollama pull qwen3.5:0.8b   # if not already pulled


# 5. Run backend
uv run uvicorn backend.main:app --reload --port 8000


# 6. Run frontend (separate terminal)
uv run streamlit run frontend/app.py
```


---


## Style Guide (Streamlit UI)


- Dark theme preferred (match `config.toml` → `[theme] base="dark"`)
- User messages: right-aligned, accent color background
- Assistant messages: left-aligned, neutral dark background
- Sidebar: compact, monospaced font for chat titles, truncated at 30 chars
- Animations: use `st.spinner` during LLM calls, streaming replaces it


---


## Error Handling


- If Ollama is not running → show friendly error: *"Local AI model is offline. Please start Ollama."*
- If DB is locked → retry once, then surface error
- Empty message guard on frontend before sending
- Session not found → auto-create new session


---


## Out of Scope (v1)


- User authentication
- File/image uploads
- Multi-model switching (hardcoded to `qwen3.5:0.8b`)
- Cloud sync
```




