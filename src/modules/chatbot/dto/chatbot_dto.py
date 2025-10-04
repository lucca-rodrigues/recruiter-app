"""DTOs for chatbot interactions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatbotCreate(BaseModel):
    query: str = Field(..., description="Texto enviado para o LLM")


class ChatbotResponse(BaseModel):
    answer: str
