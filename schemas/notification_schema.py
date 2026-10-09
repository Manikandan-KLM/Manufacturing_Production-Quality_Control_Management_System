from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    user_id: int
    notification_type: str
    title: str
    message: str
    severity: str = "Medium"
    entity: str | None = None
    entity_id: str | None = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    severity: str
    entity: str | None
    entity_id: str | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )