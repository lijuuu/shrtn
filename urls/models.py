"""
URL models for ScyllaDB operations.
"""
import uuid
from datetime import datetime
from typing import List, Optional


class ShortUrl:
    """
    Represents a short URL entry in ScyllaDB.
    This is a conceptual model, not a Django ORM model.
    """
    def __init__(
        self,
        namespace_id: uuid.UUID,
        shortcode: str,
        original_url: str,
        created_by_user_id: uuid.UUID,
        id: Optional[uuid.UUID] = None,
        expiry: Optional[datetime] = None,
        click_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_private: bool = False,
        tags: Optional[List[str]] = None,
    ):
        self.id = id if id is not None else uuid.uuid4()
        self.namespace_id = namespace_id
        self.shortcode = shortcode
        self.original_url = original_url
        self.created_by_user_id = created_by_user_id
        self.expiry = expiry
        self.click_count = click_count
        self.created_at = created_at if created_at is not None else datetime.now()
        self.updated_at = updated_at if updated_at is not None else datetime.now()
        self.is_private = is_private
        self.tags = tags if tags is not None else []

    def to_dict(self):
        return {
            "id": str(self.id),
            "namespace_id": self.namespace_id,
            "shortcode": self.shortcode,
            "original_url": self.original_url,
            "created_by_user_id": self.created_by_user_id,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "click_count": self.click_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_private": self.is_private,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=uuid.UUID(data["id"]) if "id" in data else None,
            namespace_id=data["namespace_id"],
            shortcode=data["shortcode"],
            original_url=data["original_url"],
            created_by_user_id=data["created_by_user_id"],
            expiry=datetime.fromisoformat(data["expiry"]) if data.get("expiry") else None,
            click_count=data.get("click_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            is_private=data.get("is_private", False),
            tags=data.get("tags", []),
        )


class BulkMapping:
    """
    Represents a bulk URL mapping for Excel operations.
    This is an in-memory data structure.
    """
    def __init__(self, shortcode: str, original_url: str):
        self.shortcode = shortcode
        self.original_url = original_url

    def to_dict(self):
        return {
            "shortcode": self.shortcode,
            "original_url": self.original_url,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            shortcode=data["shortcode"],
            original_url=data["original_url"],
        )
