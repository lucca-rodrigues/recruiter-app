"""Domain service that orchestrates usage log persistence."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from src.infra.database.script import get_collection

from .dto.log_dto import UsageLogCreate, UsageLogResponse, UsageLogUpdate
from .entity.log_entity import UsageLog


class UsageLogService:
    """Handles creation, retrieval, update and deletion of usage logs."""

    def __init__(self, collection: Optional[Collection] = None) -> None:
        collection_name = os.getenv("MONGODB_COLLECTION", "usage_logs")
        self._collection: Collection = collection or get_collection(collection_name)

    def create(self, data: UsageLogCreate) -> str:
        timestamp = data.timestamp or datetime.utcnow()
        log = UsageLog(
            request_id=data.request_id,
            user_id=data.user_id,
            result=data.result,
            query=data.query,
            timestamp=timestamp,
        )
        inserted = self._collection.insert_one(log.to_document())
        return str(inserted.inserted_id)

    def findAll(self) -> List[UsageLogResponse]:
        documents = self._collection.find().sort("timestamp", -1)
        return [self._map_document(doc) for doc in documents]

    def findOne(self, log_id: str) -> Optional[UsageLogResponse]:
        try:
            document = self._collection.find_one({"_id": ObjectId(log_id)})
        except InvalidId:
            return None
        if document is None:
            return None
        return self._map_document(document)

    def update(self, log_id: str, update_data: UsageLogUpdate) -> bool:
        update_doc = update_data.dict_without_none()
        if not update_doc:
            return False
        try:
            result = self._collection.update_one(
                {"_id": ObjectId(log_id)},
                {"$set": update_doc},
            )
        except InvalidId:
            return False
        return result.modified_count > 0

    def delete(self, log_id: str) -> bool:
        try:
            result = self._collection.delete_one({"_id": ObjectId(log_id)})
        except InvalidId:
            return False
        return result.deleted_count > 0

    @staticmethod
    def _map_document(document: dict) -> UsageLogResponse:
        return UsageLogResponse(
            id=str(document.get("_id")),
            request_id=document.get("request_id", ""),
            user_id=document.get("user_id", ""),
            result=document.get("result", ""),
            query=document.get("query"),
            timestamp=document.get("timestamp"),
        )
