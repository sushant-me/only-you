"""Frontier-model adapter: the same gate, any OpenAI-compatible provider.

The authority layer is model-agnostic by design — the model proposes, the gate
decides. This module only resolves provider credentials and reuses the
OpenAI-compatible client, so Muse Spark, GPT, Gemini, Claude, OpenRouter or a
local Ollama endpoint can be swapped without touching the gate.

Environment (first match wins, FRONTIER_* overrides everything):

    FRONTIER_API_BASE / FRONTIER_API_KEY / FRONTIER_MODEL   explicit
    OPENAI_API_BASE / OPENAI_API_KEY / OPENAI_MODEL         default api.openai.com/v1
    GEMINI_API_KEY / GEMINI_MODEL                           Gemini OpenAI-compat endpoint
    ANTHROPIC_API_KEY / ANTHROPIC_MODEL                     Anthropic OpenAI-compat endpoint
    DEEPSEEK_API_KEY / DEEPSEEK_MODEL                       api.deepseek.com/v1
    OPENROUTER_API_KEY / OPENROUTER_MODEL                   openrouter.ai/api/v1

Nothing here is called unless a key is present; the benchmark refuses to run
with `--model frontier` otherwise, so no simulated numbers can be mislabelled.
"""

from __future__ import annotations

import os
from typing import Any

from .model import MetaModelClient

PROVIDERS: dict[str, dict[str, str]] = {
    "openai": {
        "base_env": "OPENAI_API_BASE",
        "key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "base": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "gemini": {
        "base_env": "GEMINI_API_BASE",
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.0-flash",
    },
    "anthropic": {
        "base_env": "ANTHROPIC_API_BASE",
        "key_env": "ANTHROPIC_API_KEY",
        "model_env": "ANTHROPIC_MODEL",
        "base": "https://api.anthropic.com/v1",
        "model": "claude-3-5-sonnet-latest",
    },
    "deepseek": {
        "base_env": "DEEPSEEK_API_BASE",
        "key_env": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL",
        "base": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    "openrouter": {
        "base_env": "OPENROUTER_API_BASE",
        "key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "base": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o-mini",
    },
}


class FrontierModel(MetaModelClient):
    """An OpenAI-compatible client for a non-Meta model, same gate and receipts."""

    provider = "frontier"

    @classmethod
    def resolve(cls) -> dict[str, str] | None:
        """Return {provider, base, key, model} for the first configured provider."""
        explicit_key = os.environ.get("FRONTIER_API_KEY", "").strip()
        if explicit_key:
            return {
                "provider": os.environ.get("FRONTIER_PROVIDER", "frontier"),
                "base": os.environ.get("FRONTIER_API_BASE", "").rstrip("/"),
                "key": explicit_key,
                "model": os.environ.get("FRONTIER_MODEL", "gpt-4o-mini"),
            }
        for name, spec in PROVIDERS.items():
            key = os.environ.get(spec["key_env"], "").strip()
            if not key:
                continue
            return {
                "provider": name,
                "base": os.environ.get(spec["base_env"], spec["base"]).rstrip("/"),
                "key": key,
                "model": os.environ.get(spec["model_env"], spec["model"]),
            }
        return None

    @classmethod
    def available(cls) -> bool:
        return cls.resolve() is not None

    def __init__(self) -> None:
        config = self.resolve()
        if config is None:
            raise RuntimeError("no frontier API key configured (OPENAI_API_KEY / GEMINI_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY / FRONTIER_API_KEY)")
        super().__init__(base_url=config["base"], api_key=config["key"], model=config["model"])
        self.provider = config["provider"]

    def identity(self) -> dict[str, str]:
        return {"provider": self.provider, "model": self.model, "base_url": self.base_url}
