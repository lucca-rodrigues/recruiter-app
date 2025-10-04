"""Pydantic DTOs for OCR operations."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class OCRRequest(BaseModel):
    filename: Optional[str] = None


class OCRResponse(BaseModel):
    filename: Optional[str] = None
    content: str
