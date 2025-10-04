"""Entities for chatbot responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChatCompletion:
    answer: str
