from fastapi import APIRouter, HTTPException
from backend.database import (
    create_session,
    list_sessions,
    delete_session,
    rename_session,
)
from backend.models import ChatSession, UpdateTitleRequest

router = APIRouter()


@router.get("", response_model=list[ChatSession])
async def get_chats():
    """List all chat sessions ordered by updated_at DESC."""
    sessions = await list_sessions()
    return sessions


@router.post("", response_model=ChatSession)
async def create_chat():
    """Create a new chat session with title 'New Chat'."""
    session_id = await create_session("New Chat")
    sessions = await list_sessions()
    for session in sessions:
        if session["id"] == session_id:
            return ChatSession(**session)
    raise HTTPException(status_code=500, detail="Failed to create session")


@router.delete("/{session_id}")
async def delete_chat(session_id: int):
    """Delete a chat session and all its messages."""
    await delete_session(session_id)
    return {"message": "Session deleted"}


@router.patch("/{session_id}/title")
async def update_chat_title(session_id: int, request: UpdateTitleRequest):
    """Update a chat session title."""
    await rename_session(session_id, request.title)
    return {"message": "Title updated"}
