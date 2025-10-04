"""Service layer for chatbot interactions."""

from __future__ import annotations

from src.utils.llm_settings import LLMClient

from .dto.chatbot_dto import ChatbotCreate
from .entity.chatbot_entity import ChatCompletion


class ChatbotService:
    """Handles interaction with the LLM provider."""

    def __init__(self, client: LLMClient | None = None) -> None:
        self._client = client or LLMClient()

    def findAll(self):  # pragma: no cover - placeholder for future history listing
        raise NotImplementedError("Listing chatbot conversations is not implemented yet")

    def create(self, data: ChatbotCreate) -> ChatCompletion:
        answer = self._client.complete(data.query)
        return ChatCompletion(answer=answer)

    def update(self, *_args, **_kwargs):  # pragma: no cover - placeholder
        raise NotImplementedError("Chatbot update flow not implemented yet")

    def delete(self, *_args, **_kwargs):  # pragma: no cover - placeholder
        raise NotImplementedError("Chatbot delete flow not implemented yet")
