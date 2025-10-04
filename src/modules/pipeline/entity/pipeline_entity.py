"""Entities for document processing results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProcessedDocument:
    filename: str | None
    content: str
    summary: str
