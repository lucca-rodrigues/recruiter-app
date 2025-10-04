"""DTOs used by the document processing pipeline."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class DocumentSummary(BaseModel):
    filename: Optional[str]
    summary: str


class PipelineResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "f8aba745-2332-4031-bb42-8de4d72035f4",
                "user_id": "fabio",
                "summaries": [
                    {
                        "filename": "curriculo_lucas.pdf",
                        "summary": "Resumo conciso destacando habilidades e experiência do candidato."
                    }
                ],
                "answer": "Lucas Rodrigues atende aos requisitos de Tech Lead em IA graças à experiência com LangChain, RAG e MLOps."
            }
        }
    )
    request_id: str
    user_id: str
    summaries: List[DocumentSummary] = Field(
        default_factory=list,
        description="Lista de sumários. Retornada apenas quando nenhuma query é enviada.",
    )
    answer: Optional[str] = Field(
        default=None,
        description="Resposta contextualizada para a query, quando informada.",
    )
