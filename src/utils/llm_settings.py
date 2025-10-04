"""Utilities to configure and access the LLM provider."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()


DEFAULT_BASE_URLS: Dict[str, str] = {
    "openrouter": "https://openrouter.ai/api/v1",
    "groq": "https://api.groq.com/openai/v1",
    "deepseek": "https://api.deepseek.com",
    "perplexity": "https://api.perplexity.ai",
    "anthropic": "https://api.anthropic.com/v1",
}


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM client cannot be configured properly."""


@dataclass(slots=True)
class LLMSettings:
    api_key: str
    model: str
    base_url: Optional[str] = None
    provider: str = "openai"
    headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "LLMSettings":
        api_key = os.getenv("LLM_API_KEY") or os.getenv("AI_SDK_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "Environment variable LLM_API_KEY (or legacy AI_SDK_API_KEY) is required"
            )

        model = os.getenv("LLM_MODEL") or os.getenv("AI_SDK_MODEL", "gpt-4o-mini")
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("AI_SDK_BASE_URL")
        provider = (os.getenv("LLM_PROVIDER", "openai") or "openai").lower()

        raw_headers = os.getenv("LLM_HEADERS") or os.getenv("LLM_ADDITIONAL_HEADERS")
        headers: Dict[str, str] = {}
        if raw_headers:
            try:
                headers = json.loads(raw_headers)
            except json.JSONDecodeError as exc:  # pragma: no cover - config error
                raise LLMConfigurationError("LLM_HEADERS must be valid JSON") from exc

        if not base_url:
            base_url = DEFAULT_BASE_URLS.get(provider)

        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url,
            provider=provider,
            headers=headers,
        )


def _load_ai_sdk_client(settings: LLMSettings) -> Tuple[str, Any]:
    try:
        import ai_sdk  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        raise LLMConfigurationError("ai-sdk provider not installed") from exc

    client_cls = getattr(ai_sdk, "Client", None)
    if client_cls is None:  # pragma: no cover - safety branch
        raise LLMConfigurationError("ai_sdk.Client class not found; check ai-sdk docs")

    kwargs: Dict[str, Any] = {"api_key": settings.api_key}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    if settings.headers:
        kwargs["default_headers"] = settings.headers
    client = client_cls(**kwargs)
    return "ai_sdk", client


def _load_openai_client(settings: LLMSettings) -> Tuple[str, Any]:
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:  # pragma: no cover - should be installed
        raise LLMConfigurationError("openai package is not installed") from exc

    kwargs: Dict[str, Any] = {"api_key": settings.api_key}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    if settings.headers:
        kwargs["default_headers"] = settings.headers
    client = OpenAI(**kwargs)
    return "openai", client


class LLMClient:
    """Thin wrapper over LLM providers used throughout the application."""

    def __init__(self, settings: Optional[LLMSettings] = None) -> None:
        self.settings = settings or LLMSettings.from_env()
        self.provider, self._client = self._initialize_client()

    def _initialize_client(self) -> Tuple[str, Any]:
        loaders: Dict[str, Callable[[LLMSettings], Tuple[str, Any]]] = {
            "ai_sdk": _load_ai_sdk_client,
            "openai": _load_openai_client,
        }

        if self.settings.provider in loaders:
            return loaders[self.settings.provider](self.settings)

        # auto-detect order: ai_sdk -> openai
        for name in ("ai_sdk", "openai"):
            loader = loaders[name]
            try:
                return loader(self.settings)
            except LLMConfigurationError:
                continue

        raise LLMConfigurationError(
            "No supported LLM provider installed. Install ai-sdk or openai packages."
        )

    def complete(self, prompt: str) -> str:
        """Generate a completion from the configured LLM."""
        if self.provider == "ai_sdk":
            response = self._client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "user", "content": prompt}],
            )
            choice = getattr(response, "choices", [None])[0]
            if not choice:
                return ""
            message = getattr(choice, "message", None) or {}
            return message.get("content", "")

        if hasattr(self._client, "responses"):
            response_call = getattr(self._client.responses, "create")
            response = response_call(model=self.settings.model, input=prompt)
            output_text = getattr(response, "output_text", None)
            if output_text is not None:
                return output_text
            if getattr(response, "choices", None):  # pragma: no cover - safety
                first = response.choices[0]
                return getattr(first, "message", {}).get("content", "")
            return str(response)

        if hasattr(self._client, "chat"):
            response = self._client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "user", "content": prompt}],
            )
            choice = getattr(response, "choices", [None])[0]
            if not choice:
                return ""
            message = getattr(choice, "message", None) or {}
            return message.get("content", "")

        if hasattr(self._client, "complete"):
            response = self._client.complete(
                model=self.settings.model,
                prompt=prompt,
            )
            return getattr(response, "text", str(response))

        raise LLMConfigurationError("Unsupported LLM provider configured")


__all__ = ["LLMClient", "LLMSettings", "LLMConfigurationError"]
