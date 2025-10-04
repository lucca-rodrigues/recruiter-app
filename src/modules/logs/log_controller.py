"""FastAPI router for usage log endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Path, status

from .dto.log_dto import UsageLogCreate, UsageLogResponse, UsageLogUpdate
from .log_service import UsageLogService

router = APIRouter(prefix="/logs", tags=["Logs"])


def get_service() -> UsageLogService:
    return UsageLogService()


@router.get(
    "/",
    response_model=list[UsageLogResponse],
    summary="Listar logs",
    description="Retorna todos os registros de uso ordenados do mais recente para o mais antigo.",
)
def findAll(service: UsageLogService = Depends(get_service)) -> list[UsageLogResponse]:
    return service.findAll()


@router.get(
    "/{log_id}",
    response_model=UsageLogResponse,
    summary="Consultar log",
    description="Consulta um registro específico pelo identificador do documento no MongoDB.",
    responses={404: {"description": "Log não encontrado"}},
)
def findOne(
    log_id: str = Path(..., description="Log identifier"),
    service: UsageLogService = Depends(get_service),
) -> UsageLogResponse:
    log = service.findOne(log_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Criar log",
    description="Cria manualmente um registro de uso (normalmente gerado automaticamente pela pipeline).",
    responses={201: {"description": "Log criado com sucesso"}},
)
def create(
    payload: UsageLogCreate,
    service: UsageLogService = Depends(get_service),
) -> dict[str, str]:
    log_id = service.create(payload)
    return {"id": log_id}


@router.put(
    "/{log_id}",
    summary="Atualizar log",
    description="Atualiza campos de um registro existente (resultado e/ou query).",
    responses={404: {"description": "Log não encontrado"}},
)
def update(
    log_id: str,
    payload: UsageLogUpdate,
    service: UsageLogService = Depends(get_service),
) -> dict[str, bool]:
    success = service.update(log_id, payload)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return {"updated": True}


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover log",
    description="Remove um registro específico do MongoDB.",
    responses={404: {"description": "Log não encontrado"}},
)
def delete(
    log_id: str,
    service: UsageLogService = Depends(get_service),
) -> None:
    success = service.delete(log_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
