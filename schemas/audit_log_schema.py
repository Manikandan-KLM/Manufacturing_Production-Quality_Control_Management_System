from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogCreateRequest(BaseModel):
    user_id: int | None = None
    action: str
    entity: str
    entity_id: str | None = None

    previous_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None

    description: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class AuditLogResponse(BaseModel):
    id: int

    user_id: int | None

    action: str
    entity: str
    entity_id: str | None

    timestamp: datetime

    previous_value: dict[str, Any] | None
    new_value: dict[str, Any] | None

    description: str | None

    ip_address: str | None
    user_agent: str | None

    model_config = ConfigDict(
        from_attributes=True
    )