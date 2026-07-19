from __future__ import annotations

import json
from dataclasses import dataclass

from openai import AsyncOpenAI

from src.conf.config import config


@dataclass(frozen=True)
class GenerationResult:
    content: dict
    input_tokens: int | None
    output_tokens: int | None
    model: str


class OpenAIClient:
    def __init__(self, client: AsyncOpenAI | None = None, model: str | None = None):
        self._client = client or AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self._model = model or config.OPENAI_MODEL

    async def generate_json(self, system: str, user: str) -> GenerationResult:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        message = response.choices[0].message.content or "{}"
        usage = response.usage
        return GenerationResult(
            content=json.loads(message),
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            model=response.model or self._model,
        )
