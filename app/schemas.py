from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    model: str | None = None


class SessionCreateResponse(BaseModel):
    session_id: int
    model: str
    created_at: datetime


class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    model: str | None = None


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float


class SendMessageResponse(BaseModel):
    session_id: int
    assistant_message: MessageOut
    session_total_cost: float
    session_total_tokens: int


class SessionHistoryResponse(BaseModel):
    session_id: int
    model: str
    created_at: datetime
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost: float
    messages: list[MessageOut]


class SessionListItem(BaseModel):
    session_id: int
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    total_tokens: int
    total_cost: float


class SessionListResponse(BaseModel):
    sessions: list[SessionListItem]
