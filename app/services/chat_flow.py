from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..config import settings
from ..schemas import SendMessageRequest, MessageOut, SendMessageResponse
from ..services.chat_context import build_openai_messages
from ..services.openai_client import OpenAIClient
from ..services.pricing import calc_cost_usd

class ChatFlowService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAIClient()

    def process_user_message(self, session_id: int, payload: SendMessageRequest) -> SendMessageResponse:
        session = crud.chat.get_session(self.db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        model = payload.model or session.model

        crud.chat.create_message(
            self.db,
            session_id=session.id,
            role="user",
            content=payload.message
        )

        history = crud.chat.get_session_messages(self.db, session.id)
        openai_messages = build_openai_messages(
            history,
            system_prompt=settings.system_prompt,
            limit=settings.context_limit,
        )

        reply = self.client.chat(model=model, messages=openai_messages)

        try:
            assistant_cost = calc_cost_usd(
                model=model,
                prompt_tokens=reply.prompt_tokens,
                completion_tokens=reply.completion_tokens,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        assistant_msg = crud.chat.create_message(
            self.db,
            session_id=session.id,
            role="assistant",
            content=reply.text,
            prompt_tokens=reply.prompt_tokens,
            completion_tokens=reply.completion_tokens,
            total_tokens=reply.total_tokens,
            cost=assistant_cost,
        )

        crud.chat.update_session_stats(
            self.db,
            session,
            model=model,
            prompt_tokens=reply.prompt_tokens,
            completion_tokens=reply.completion_tokens,
            total_tokens=reply.total_tokens,
            cost=assistant_cost
        )

        out_msg = MessageOut(
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
            session_id=session.id,
            assistant_message=out_msg,
            session_total_cost=session.total_cost,
            session_total_tokens=session.total_tokens,
        )