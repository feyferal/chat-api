from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenRates:
    input_per_1m: float
    output_per_1m: float


RATES: dict[str, TokenRates] = {
    "gpt-4o-mini": TokenRates(input_per_1m=0.15, output_per_1m=0.60),
    "gpt-4o": TokenRates(input_per_1m=5.0, output_per_1m=15.0),
}


def calc_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = RATES.get(model)
    if rates is None:
        raise ValueError(f"Unknown model rates: {model}")
    cost = (prompt_tokens / 1_000_000) * rates.input_per_1m + (completion_tokens / 1_000_000) * rates.output_per_1m
    return round(cost, 10)
