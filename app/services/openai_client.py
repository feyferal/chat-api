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


class OpenAIServiceError(RuntimeError):
    pass


class OpenAIAuthError(OpenAIServiceError):
    pass


class OpenAIRateLimitError(OpenAIServiceError):
    pass


class OpenAIUpstreamError(OpenAIServiceError):
    pass


def _extract_status_code(exc: Exception) -> int | None:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status

    resp = getattr(exc, "response", None)
    status = getattr(resp, "status_code", None)
    if isinstance(status, int):
        return status

    return None


class OpenAIClient:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)

    def chat(self, model: str, messages: list[dict[str, str]]) -> OpenAIReply:
        try:
            resp = self._client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except Exception as e:
            status = _extract_status_code(e)

            if status == 401:
                raise OpenAIAuthError("OpenAI authentication failed") from e
            if status == 429:
                raise OpenAIRateLimitError("OpenAI rate limit exceeded") from e

            raise OpenAIUpstreamError(str(e)) from e

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
