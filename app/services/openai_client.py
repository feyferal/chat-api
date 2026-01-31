from __future__ import annotations

from dataclasses import dataclass
from openai import OpenAI

from ..config import settings


@dataclass(frozen=True)
class OpenAIReply:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAIClient:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)

    def chat(self, model: str, messages: list[dict[str, str]]) -> OpenAIReply:
        resp = self._client.chat.completions.create(
            model=model,
            messages=messages,
        )
        text = resp.choices[0].message.content or ""

        usage = getattr(resp, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        total_tokens = int(getattr(usage, "total_tokens", 0) or 0)

        return OpenAIReply(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
