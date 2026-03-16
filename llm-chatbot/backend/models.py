from pydantic import BaseModel


class ChatSession(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str


class Message(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: str


class CreateMessageRequest(BaseModel):
    content: str


class UpdateTitleRequest(BaseModel):
    title: str
