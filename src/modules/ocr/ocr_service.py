"""Domain service responsible for OCR operations."""

from __future__ import annotations

from typing import Any, Sequence, Tuple

from src.utils.ocr import OCRProcessor

from .entity.ocr_entity import OCRResult

FileWithName = Tuple[Any, str | None]


class OCRService:
    """Wrapper around ``OCRProcessor`` to be consumed by controllers."""

    def __init__(self, processor: OCRProcessor | None = None) -> None:
        self._processor = processor or OCRProcessor()

    def create(self, file_obj: object, filename: str | None = None) -> OCRResult:
        """Process a single file and return the OCR result."""
        text = self._processor.extract_text_from_file(file_obj)
        return OCRResult(content=text, filename=filename)

    def findOne(self, file_obj: object, filename: str | None = None) -> OCRResult:
        """Alias for ``create`` to keep uniform naming."""
        return self.create(file_obj, filename)

    def findAll(self, files: Sequence[FileWithName]) -> list[OCRResult]:
        """Process multiple files sequentially."""
        results: list[OCRResult] = []
        for file_obj, filename in files:
            results.append(self.create(file_obj, filename))
        return results

    def update(self, *_args, **_kwargs):
        raise NotImplementedError("OCR update flow not implemented yet")

    def delete(self, *_args, **_kwargs):
        raise NotImplementedError("OCR delete flow not implemented yet")
