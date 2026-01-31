from __future__ import annotations

from ..models import ChatMessage

_ALLOWED_ROLES: set[str] = {"system", "user", "assistant"}


def build_openai_messages(
    history: list[ChatMessage],
    *,
    system_prompt: str | None = None,
    limit: int = 30,
) -> list[dict[str, str]]:
    filtered = [m for m in history if m.role in _ALLOWED_ROLES]

    if limit > 0:
        filtered = filtered[-limit:]

    out: list[dict[str, str]] = []
    if system_prompt:
        out.append({"role": "system", "content": system_prompt})

    out.extend({"role": m.role, "content": m.content} for m in filtered)
    return out
