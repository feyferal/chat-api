from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from .. import crud
from ..services.chat_flow import ChatFlowService
from ..schemas import (
    MessageOut,
    SendMessageRequest,
    SendMessageResponse,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionHistoryResponse,
    SessionListItem,
    SessionListResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
def create_session(
        payload: SessionCreateRequest,
        db: Session = Depends(get_db)
):
    model = payload.model or settings.default_model
    session = crud.chat.create_session(db, model)

    return SessionCreateResponse(
        session_id=session.id,
        model=session.model,
        created_at=session.created_at
    )


@router.post("/{session_id}/messages", response_model=SendMessageResponse)
def send_message(
        session_id: int,
        payload: SendMessageRequest,
        db: Session = Depends(get_db)
):
    service = ChatFlowService(db)
    return service.process_user_message(session_id, payload)


@router.get("/{session_id}", response_model=SessionHistoryResponse)
def get_history(session_id: int, db: Session = Depends(get_db)):
    session = crud.chat.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = crud.chat.get_session_messages(db, session_id)

    msgs_out = [
        MessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at,
            prompt_tokens=m.prompt_tokens,
            completion_tokens=m.completion_tokens,
            total_tokens=m.total_tokens,
            cost=m.cost,
        )
        for m in messages
    ]

    return SessionHistoryResponse(
        session_id=session.id,
        model=session.model,
        created_at=session.created_at,
        total_prompt_tokens=session.total_prompt_tokens,
        total_completion_tokens=session.total_completion_tokens,
        total_tokens=session.total_tokens,
        total_cost=session.total_cost,
        messages=msgs_out,
    )


@router.get("", response_model=SessionListResponse)
def list_sessions(
        limit: int = 50,
        offset: int = 0,
        db: Session = Depends(get_db),
):
    sessions = crud.chat.list_sessions(db, limit, offset)

    out: list[SessionListItem] = []
    for s in sessions:
        message_count = crud.chat.count_messages_in_session(db, s.id)

        out.append(
            SessionListItem(
                session_id=s.id,
                model=s.model,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=message_count,
                total_tokens=int(s.total_tokens),
                total_cost=float(s.total_cost),
            )
        )

    return SessionListResponse(sessions=out)