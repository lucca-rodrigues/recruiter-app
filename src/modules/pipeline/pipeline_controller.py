"""Endpoints for the recruitment processing pipeline."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from .dto.pipeline_dto import PipelineResponse
from .pipeline_service import PipelineCreate, PipelineService

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


def get_service() -> PipelineService:
    return PipelineService()


@router.post(
    "/",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Executar pipeline",
    description=(
        "Recebe currículos em PDF/imagem, extrai texto por OCR, utiliza um LLM para gerar resumos "
        "ou responder perguntas e registra o log de uso. Envie `query` para receber apenas a "
        "resposta contextualizada; deixe em branco para obter os sumários individuais."
    ),
    responses={
        201: {
            "description": "Processamento concluído com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "request_id": "f8aba745-2332-4031-bb42-8de4d72035f4",
                        "user_id": "fabio",
                        "summaries": [],
                        "answer": "Lucas Rodrigues atende aos requisitos de Tech Lead em IA...",
                    }
                }
            },
        }
    },
)
async def create(
    request_id: str = Form(...),
    user_id: str = Form(...),
    query: Optional[str] = Form(default=None),
    files: List[UploadFile] = File(...),
    service: PipelineService = Depends(get_service),
) -> PipelineResponse:
    file_inputs: List[tuple[bytes, str | None]] = []
    for file in files:
        content = await file.read()
        file_inputs.append((content, file.filename))

    payload = PipelineCreate(
        request_id=request_id,
        user_id=user_id,
        query=query.strip() if query else None,
        files=file_inputs,
    )
    return service.create(payload)
