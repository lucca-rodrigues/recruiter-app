"""Service responsible for orchestrating OCR, LLM and logging flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from src.modules.chatbot.chatbot_service import ChatbotService
from src.modules.chatbot.dto.chatbot_dto import ChatbotCreate
from src.modules.logs.dto.log_dto import UsageLogCreate
from src.modules.logs.log_service import UsageLogService
from src.modules.ocr.ocr_service import OCRService

from .dto.pipeline_dto import DocumentSummary, PipelineResponse
from .entity.pipeline_entity import ProcessedDocument


@dataclass(slots=True)
class PipelineCreate:
    request_id: str
    user_id: str
    query: str | None
    files: Sequence[tuple[bytes, str | None]]


class PipelineService:
    """Coordinates the resume processing pipeline."""

    def __init__(
        self,
        ocr_service: OCRService | None = None,
        chatbot_service: ChatbotService | None = None,
        log_service: UsageLogService | None = None,
    ) -> None:
        self._ocr_service = ocr_service or OCRService()
        self._chatbot_service = chatbot_service or ChatbotService()
        self._log_service = log_service or UsageLogService()

    def create(self, data: PipelineCreate) -> PipelineResponse:
        ocr_results = self._ocr_service.findAll(data.files)
        processed_docs: List[ProcessedDocument] = []

        for result in ocr_results:
            prompt = _build_summary_prompt(result.filename, result.content)
            completion = self._chatbot_service.create(ChatbotCreate(query=prompt))
            processed_docs.append(
                ProcessedDocument(
                    filename=result.filename,
                    content=result.content,
                    summary=completion.answer.strip(),
                )
            )

        answer: str | None = None
        if data.query:
            prompt = _build_query_prompt(data.query, processed_docs)
            response = self._chatbot_service.create(ChatbotCreate(query=prompt))
            answer = response.answer.strip()

        summaries: List[DocumentSummary] = []
        if not data.query:
            summaries = [
                DocumentSummary(filename=doc.filename, summary=doc.summary)
                for doc in processed_docs
            ]

        response_payload = PipelineResponse(
            request_id=data.request_id,
            user_id=data.user_id,
            summaries=summaries,
            answer=answer,
        )

        log_payload = UsageLogCreate(
            request_id=data.request_id,
            user_id=data.user_id,
            query=data.query,
            result=response_payload.model_dump_json(),
        )
        self._log_service.create(log_payload)

        return response_payload


def _build_summary_prompt(filename: str | None, content: str) -> str:
    name_section = f"Currículo: {filename or 'Documento sem nome'}"
    return (
        "Você é um assistente de recrutamento. Gere um resumo curto em português, "
        "destacando experiências, habilidades técnicas e soft skills do candidato que se adequa melhor aos requisitos da vaga informada.\n"
        f"{name_section}\n"
        "Conteúdo OCR:\n"
        f"{content}\n"
        "Resumo:"
    )


def _build_query_prompt(query: str, documents: Sequence[ProcessedDocument]) -> str:
    doc_sections = []
    for doc in documents:
        section = (
            f"Currículo: {doc.filename or 'Documento sem nome'}\n"
            f"Resumo: {doc.summary}\n"
            f"Texto OCR:\n{doc.content}\n"
        )
        doc_sections.append(section)

    joined_docs = "\n\n".join(doc_sections)
    return (
        "Você é um especialista em Talent Acquisition. Analise os currículos abaixo e responda "
        "em português atendendo às seguintes regras:\n"
        "1. Mencione apenas candidatos que realmente atendem aos requisitos da pergunta.\n"
        "2. Se um candidato não atender, simplesmente não o cite.\n"
        "3. Se nenhum candidato atender, responda exatamente 'Nenhum candidato atende aos requisitos atuais.'\n"
        "4. Para cada candidato mencionado, explique brevemente por que ele atende.\n"
        "5. Não crie comparativos ou tabelas com todos os currículos.\n"
        f"Pergunta: {query}\n"
        "Currículos analisados:\n"
        f"{joined_docs}\n"
        "Resposta:"
    )
