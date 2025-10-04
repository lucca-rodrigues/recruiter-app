"""Pydantic schemas for usage logs."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UsageLogCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "f8aba745-2332-4031-bb42-8de4d72035f4",
                "user_id": "fabio",
                "result": '{"request_id":"f8aba745-2332-4031-bb42-8de4d72035f4","user_id":"fabio","answer":"Lucas Rodrigues atende..."}',
                "query": "Qual desses currículos se enquadra melhor para a vaga de Tech Lead...",
            }
        }
    )
    request_id: str
    user_id: str
    result: str
    query: Optional[str] = None
    timestamp: Optional[datetime] = None


class UsageLogUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"result": '{"answer": "Atualização de resultado"}'}}
    )
    result: Optional[str] = None
    query: Optional[str] = None

    def dict_without_none(self) -> dict:
        return {key: value for key, value in self.model_dump().items() if value is not None}


class UsageLogResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "68e123a2f64bf992a678aaa9",
                "request_id": "f8aba745-2332-4031-bb42-8de4d72035f4",
                "user_id": "fabio",
                "result": '{"answer":"Lucas Rodrigues é o candidato mais aderente..."}',
                "query": "Qual desses currículos se enquadra melhor...",
                "timestamp": "2025-10-04T13:39:46.920000",
            }
        }
    )
    id: str = Field(..., description="Mongo document identifier")
    request_id: str
    user_id: str
    result: str
    query: Optional[str] = None
    timestamp: datetime
