"""Minimal OCR helpers used by the recruiter application."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, List, Sequence, Union

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter, ImageOps

FileInput = Union[str, Path, bytes, bytearray, BinaryIO, Image.Image]


def _read_all_bytes(file_obj: FileInput) -> bytes:
    """Return raw bytes from a supported input type."""
    if isinstance(file_obj, (bytes, bytearray)):
        return bytes(file_obj)

    if isinstance(file_obj, (str, Path)):
        return Path(file_obj).expanduser().read_bytes()

    if hasattr(file_obj, "read") and callable(file_obj.read):
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        data = file_obj.read()
        return data if isinstance(data, bytes) else data.encode()

    raise TypeError("Unsupported file input type for OCR")


def _load_image(image_input: FileInput) -> Image.Image:
    """Create a PIL image from bytes, file-like objects, or paths."""
    if isinstance(image_input, Image.Image):
        return image_input

    data = _read_all_bytes(image_input)
    return Image.open(io.BytesIO(data))


def _prepare_image_for_ocr(image: Image.Image) -> Image.Image:
    """Basic pre-processing to help Tesseract read noisy scans."""
    grayscale = ImageOps.grayscale(image)
    denoised = grayscale.filter(ImageFilter.MedianFilter(size=3))
    return ImageOps.autocontrast(denoised)


class OCRProcessor:
    """Simple OCR pipeline that handles images and PDFs."""

    def __init__(self, language: str = "por", psm: int = 6) -> None:
        self.language = language
        self.tesseract_config = f"--oem 3 --psm {psm}"

    def extract_text_from_image(self, image_input: FileInput) -> str:
        """Extract text from an image-like input."""
        pil_image = _load_image(image_input)
        preprocessed = _prepare_image_for_ocr(pil_image)
        text = pytesseract.image_to_string(
            preprocessed,
            lang=self.language,
            config=self.tesseract_config,
        )
        return text.strip()

    def extract_text_from_pdf(self, pdf_input: FileInput) -> str:
        """Extract and concatenate text from every page in a PDF."""
        pdf_bytes = _read_all_bytes(pdf_input)
        pages = convert_from_bytes(pdf_bytes)
        texts: List[str] = []
        for index, page in enumerate(pages, start=1):
            page_text = self.extract_text_from_image(page)
            texts.append(f"[page {index}]\n{page_text}")
        return "\n\n".join(texts).strip()

    def extract_text_from_file(self, file_obj: FileInput) -> str:
        """Heuristic helper that routes based on the provided data."""
        if isinstance(file_obj, Image.Image):
            return self.extract_text_from_image(file_obj)

        if isinstance(file_obj, (str, Path)):
            suffix = Path(file_obj).suffix.lower()
            if suffix == ".pdf":
                return self.extract_text_from_pdf(file_obj)
            return self.extract_text_from_image(file_obj)

        raw_bytes = _read_all_bytes(file_obj)
        if raw_bytes.startswith(b"%PDF"):
            return self.extract_text_from_pdf(raw_bytes)
        return self.extract_text_from_image(raw_bytes)

    def extract_many(self, files: Sequence[FileInput]) -> List[str]:
        """Run OCR on a sequence of inputs returning one text per file."""
        return [self.extract_text_from_file(file_obj) for file_obj in files]


def extract_text_from_image(
    image_input: FileInput, *, language: str = "por", psm: int = 6
) -> str:
    """Convenience wrapper around ``OCRProcessor.extract_text_from_image``."""
    return OCRProcessor(language=language, psm=psm).extract_text_from_image(image_input)


def extract_text_from_pdf(
    pdf_input: FileInput, *, language: str = "por", psm: int = 6
) -> str:
    """Convenience wrapper around ``OCRProcessor.extract_text_from_pdf``."""
    return OCRProcessor(language=language, psm=psm).extract_text_from_pdf(pdf_input)


__all__ = [
    "OCRProcessor",
    "extract_text_from_image",
    "extract_text_from_pdf",
]
