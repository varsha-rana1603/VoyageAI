import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    StartChatResponse,
)

from app.conversation.manager import (
    process_message,
    start_conversation,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

# Temporary in-memory session store.
# TODO: Replace with Redis or database-backed sessions.
sessions = {}


@router.post(
    "/start",
    response_model=StartChatResponse,
)
def start_chat():

    state = start_conversation()

    session_id = str(uuid.uuid4())

    sessions[session_id] = state

    print("CREATED:", session_id)
    print("ALL SESSIONS:", list(sessions.keys()))

    return StartChatResponse(
        session_id=session_id,
        message=state.messages[-1]["content"],
    )


@router.post(
    "/message",
    response_model=ChatResponse,
)
def send_message(
    request: ChatRequest,
):
    print("REQUEST:", request.session_id)

    state = sessions.get(request.session_id)
    print("STATE:", state)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    state = process_message(
        state=state,
        message=request.message,
    )

    sessions[request.session_id] = state

    return ChatResponse(
        session_id=request.session_id,
        message=state.messages[-1]["content"],
        profile=state.profile,
        complete=state.is_complete,
    )