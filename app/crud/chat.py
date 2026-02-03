from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import ChatSession, ChatMessage

def create_session(db: Session, model: str) -> ChatSession:
    session = ChatSession(model=model)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db: Session, session_id: int) -> ChatSession | None:
    return db.get(ChatSession, session_id)

def get_session_messages(db: Session, session_id: int) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )

def create_message(
    db: Session,
    session_id: int,
    role: str,
    content: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    cost: float = 0.0
) -> ChatMessage:
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost=cost
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def update_session_stats(
    db: Session,
    session: ChatSession,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cost: float
):
    session.model = model
    session.updated_at = func.now()
    session.total_prompt_tokens += prompt_tokens
    session.total_completion_tokens += completion_tokens
    session.total_tokens += total_tokens
    session.total_cost = float(session.total_cost) + float(cost)
    db.add(session)
    db.commit()
    db.refresh(session)

def list_sessions(db: Session, limit: int, offset: int) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def count_messages_in_session(db: Session, session_id: int) -> int:
    return (
        db.query(func.count(ChatMessage.id))
        .filter(ChatMessage.session_id == session_id)
        .scalar()
        or 0
    )