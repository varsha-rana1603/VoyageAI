from pydantic import BaseModel
from typing import Optional
from app.conversation.user_profile import UserProfile


class StartChatResponse(BaseModel):
    session_id: str
    message: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    profile: UserProfile
    complete: bool