from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db, close_db
from backend.routers import chats, messages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await init_db()
    yield
    await close_db()


app = FastAPI(title="LLM Chatbot API", lifespan=lifespan)

# CORS middleware - allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers with /api prefix
app.include_router(chats.router, prefix="/api/chats", tags=["chats"])
app.include_router(messages.router, prefix="/api/chats/{session_id}/messages", tags=["messages"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "LLM Chatbot API is running"}
