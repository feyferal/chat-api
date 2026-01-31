from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ChatSession, ChatMessage
from ..schemas import (
    SessionCreateRequest, SessionCreateResponse,
    SendMessageRequest, SendMessageResponse,
    SessionHistoryResponse, MessageOut
)
from ..services.openai_client import OpenAIClient
from ..services.chat_context import build_openai_messages
from ..services.pricing import calc_cost_usd

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    model = payload.model or "gpt-4o-mini"
    s = ChatSession(model=model)
    db.add(s)
    db.commit()
    db.refresh(s)
    return SessionCreateResponse(session_id=s.id, model=s.model, created_at=s.created_at)


@router.post("/{session_id}/messages", response_model=SendMessageResponse)
def send_message(session_id: int, payload: SendMessageRequest, db: Session = Depends(get_db)):
    s = db.get(ChatSession, session_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Session not found")

    model = payload.model or s.model

    user_msg = ChatMessage(session_id=s.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    history = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.id.asc()).all()
    openai_messages = build_openai_messages(history)

    client = OpenAIClient()
    reply = client.chat(model=model, messages=openai_messages)

    assistant_cost = calc_cost_usd(model=model, prompt_tokens=reply.prompt_tokens, completion_tokens=reply.completion_tokens)

    assistant_msg = ChatMessage(
        session_id=s.id,
        role="assistant",
        content=reply.text,
        prompt_tokens=reply.prompt_tokens,
        completion_tokens=reply.completion_tokens,
        total_tokens=reply.total_tokens,
        cost=assistant_cost,
    )
    db.add(assistant_msg)

    s.model = model
    s.total_prompt_tokens += reply.prompt_tokens
    s.total_completion_tokens += reply.completion_tokens
    s.total_tokens += reply.total_tokens
    s.total_cost = float(s.total_cost) + float(assistant_cost)

    db.commit()
    db.refresh(assistant_msg)
    db.refresh(s)

    out = MessageOut(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        created_at=assistant_msg.created_at,
        prompt_tokens=assistant_msg.prompt_tokens,
        completion_tokens=assistant_msg.completion_tokens,
        total_tokens=assistant_msg.total_tokens,
        cost=assistant_msg.cost,
    )

    return SendMessageResponse(
        session_id=s.id,
        assistant_message=out,
        session_total_cost=s.total_cost,
        session_total_tokens=s.total_tokens,
    )


@router.get("/{session_id}", response_model=SessionHistoryResponse)
def get_history(session_id: int, db: Session = Depends(get_db)):
    s = db.get(ChatSession, session_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.id.asc()).all()

    return SessionHistoryResponse(
        session_id=s.id,
        model=s.model,
        created_at=s.created_at,
        total_prompt_tokens=s.total_prompt_tokens,
        total_completion_tokens=s.total_completion_tokens,
        total_tokens=s.total_tokens,
        total_cost=s.total_cost,
        messages=[
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
        ],
    )
