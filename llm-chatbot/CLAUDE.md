# Local LLM Chatbot (ChatGPT UI clone)

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **LLM:** Ollama running locally with model `qwen3.5:0.8b`
- **Database:** SQLite with aiosqlite
- **Package manager:** uv

## Project Structure

```
llm-chatbot/
├── pyproject.toml
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── llm.py
│   └── routers/
│       ├── chats.py
│       └── messages.py
├── frontend/
│   ├── app.py
│   └── .streamlit/config.toml
└── CLAUDE.md
```

## Commands

- **Install dependencies:** `uv add <package>`
- **Run backend:** `uv run uvicorn backend.main:app --reload --port 8000`
- **Run frontend:** `uv run streamlit run frontend/app.py`
- **Sync dependencies:** `uv sync`
