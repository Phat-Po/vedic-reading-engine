"""Minimal async LLM client wrapper."""

from __future__ import annotations

import os

import httpx


class LLMClient:
    def __init__(self, provider: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        self.provider = provider or os.getenv("LLM_PROVIDER", "offline")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model = model or os.getenv("LLM_MODEL", "claude-3-5-sonnet-latest")

    async def complete(self, prompt: str) -> str:
        if self.provider == "offline":
            raise RuntimeError("LLM_PROVIDER=offline; use InterpretationEngine.interpret_offline.")
        if self.provider == "openai-compatible":
            return await self._openai_compatible(prompt)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _openai_compatible(self, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        if not self.base_url:
            raise RuntimeError("Missing LLM_BASE_URL for openai-compatible provider.")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

