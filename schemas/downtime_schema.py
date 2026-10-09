from datetime import datetime

from pydantic import BaseModel, Field


class DowntimeCreateRequest(BaseModel):

    downtime_number: str = Field(
        min_length=2,
        max_length=50
    )

    machine_id: int = Field(
        gt=0
    )

    production_line_id: int = Field(
        gt=0
    )

    responsible_person_id: int = Field(
        gt=0
    )

    category: str

    reason: str = Field(
        min_length=2
    )

    start_time: datetime


class DowntimeEndRequest(BaseModel):

    end_time: datetime


class DowntimeUpdateRequest(BaseModel):

    category: str | None = None

    reason: str | None = Field(
        default=None,
        min_length=2
    )

    responsible_person_id: int | None = Field(
        default=None,
        gt=0
    )


class DowntimeResponse(BaseModel):

    id: int

    downtime_number: str

    machine_id: int

    production_line_id: int

    responsible_person_id: int

    category: str

    reason: str

    start_time: datetime

    end_time: datetime | None

    duration_minutes: float

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class DowntimeListResponse(BaseModel):

    items: list[DowntimeResponse]

    total: int

    page: int

    page_size: int

    total_pages: int


class DowntimePercentageResponse(BaseModel):

    machine_id: int

    total_period_minutes: float

    downtime_minutes: float

    downtime_percentage: float