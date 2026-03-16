import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.database import (
    get_messages as db_get_messages,
    add_message,
    update_session_timestamp,
)
from backend.models import Message, CreateMessageRequest
from backend.llm import stream_chat

router = APIRouter()


@router.get("", response_model=list[Message])
async def get_messages(session_id: int):
    """Get all messages for a session."""
    messages = await db_get_messages(session_id)
    return messages


@router.post("")
async def create_message(session_id: int, request: CreateMessageRequest):
    """
    Create a new message and get streaming response from LLM.
    
    - Saves user message to DB
    - Fetches full message history
    - Calls LLM stream function
    - Returns StreamingResponse with SSE
    """
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    # Save user message to DB
    await add_message(session_id, "user", request.content)
    
    # Fetch full message history
    messages = await get_messages(session_id)
    message_history = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    # Create async generator for SSE streaming
    async def generate():
        full_response = ""
        async for token in stream_chat(message_history):
            full_response += token
            # SSE format: data: <token>\n\n
            yield f"data: {json.dumps({'token': token})}\n\n"
        
        # Save assistant response to DB
        await add_message(session_id, "assistant", full_response)
        
        # Update session timestamp
        await update_session_timestamp(session_id)
        
        # Send end marker
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
