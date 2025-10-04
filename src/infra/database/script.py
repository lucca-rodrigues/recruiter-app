"""Database utilities for MongoDB connections."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB = "recruiter"


@lru_cache(maxsize=1)
def get_client(uri: Optional[str] = None) -> MongoClient:
    """Return a cached MongoClient using env vars or provided URI."""
    mongo_uri = uri or os.getenv("MONGODB_URI", DEFAULT_URI)
    return MongoClient(mongo_uri)


def get_database(name: Optional[str] = None) -> Database:
    """Return a Database instance using configured client."""
    db_name = name or os.getenv("MONGODB_DB", DEFAULT_DB)
    return get_client()[db_name]


def get_collection(collection_name: str) -> Collection:
    """Return a collection from the configured database."""
    return get_database()[collection_name]


__all__ = ["get_client", "get_database", "get_collection"]
