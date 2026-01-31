from __future__ import annotations

from ..models import ChatMessage


def build_openai_messages(history: list[ChatMessage]) -> list[dict[str, str]]:
    return [{"role": m.role, "content": m.content} for m in history]
