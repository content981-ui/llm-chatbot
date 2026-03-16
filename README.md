# Local LLM Chatbot

A ChatGPT-like UI clone powered by a local LLM (Ollama). Built with Streamlit frontend and FastAPI backend.

![Screenshot](screenshot.png)

## Features

- 💬 Create and manage multiple chat sessions
- 🗑️ Delete chat history
- 🔄 Real-time streaming responses from local LLM
- 🌙 Dark theme UI
- 📱 Responsive chat interface

## Prerequisites

- **Python 3.11+**
- **uv** - Fast Python package manager
- **Ollama** - Local LLM runner with model `qwen3.5:0.8b`

### Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Pull the required model
ollama pull qwen3.5:0.8b
```

## Installation

1. **Clone or navigate to the project directory**

```bash
cd llm-chatbot
```

2. **Install dependencies with uv**

```bash
uv sync
```

## Running the Application

### 1. Start Ollama

Make sure Ollama is running:

```bash
ollama serve
```

### 2. Start the Backend (FastAPI)

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Start the Frontend (Streamlit)

In a new terminal:

```bash
uv run streamlit run frontend/app.py --server.port 8501
```

The UI will open at `http://localhost:8501`

## Project Structure

```
llm-chatbot/
├── pyproject.toml           # Project dependencies
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLite database helpers
│   ├── models.py            # Pydantic models
│   ├── llm.py               # Ollama client
│   └── routers/
│       ├── chats.py         # Chat session endpoints
│       └── messages.py      # Message endpoints
├── frontend/
│   ├── app.py               # Streamlit application
│   └── .streamlit/
│       └── config.toml      # Streamlit theme config
├── chatbot.db               # SQLite database (created on startup)
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chats` | List all chat sessions |
| POST | `/api/chats` | Create new chat session |
| DELETE | `/api/chats/{id}` | Delete a chat session |
| PATCH | `/api/chats/{id}/title` | Update chat title |
| GET | `/api/chats/{id}/messages` | Get messages for a session |
| POST | `/api/chats/{id}/messages` | Send message (streaming) |

## Troubleshooting

### Ollama Connection Error

If you see "⚠️ Ollama is not running", start Ollama:

```bash
ollama serve
```

### Backend Not Responding

Ensure the backend is running on port 8000:

```bash
curl http://localhost:8000
```

### Database Issues

Delete the database file to reset:

```bash
rm chatbot.db
```

## License

MIT
