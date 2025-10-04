"""Entities for OCR results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class OCRResult:
    content: str
    filename: Optional[str] = None
