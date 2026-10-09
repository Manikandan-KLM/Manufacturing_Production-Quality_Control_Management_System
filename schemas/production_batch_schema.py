from datetime import datetime

from pydantic import BaseModel, Field


class ProductionBatchCreateRequest(BaseModel):

    production_order_id: int = Field(
        gt=0
    )

    planned_quantity: float = Field(
        gt=0
    )

    production_line_id: int = Field(
        gt=0
    )

    machine_id: int = Field(
        gt=0
    )

    supervisor_id: int | None = Field(
        default=None,
        gt=0
    )


class ProductionBatchUpdateRequest(BaseModel):

    planned_quantity: float | None = Field(
        default=None,
        gt=0
    )

    production_line_id: int | None = Field(
        default=None,
        gt=0
    )

    machine_id: int | None = Field(
        default=None,
        gt=0
    )

    supervisor_id: int | None = Field(
        default=None,
        gt=0
    )


class ProductionQuantityUpdateRequest(BaseModel):

    produced_quantity: float = Field(
        ge=0
    )

    rejected_quantity: float = Field(
        ge=0
    )


class ProductionBatchTimeRequest(BaseModel):

    start_time: datetime | None = None

    end_time: datetime | None = None


class ProductionBatchResponse(BaseModel):

    id: int

    batch_number: str

    production_order_id: int

    planned_quantity: float

    produced_quantity: float

    rejected_quantity: float

    start_time: datetime | None

    end_time: datetime | None

    production_line_id: int

    machine_id: int

    supervisor_id: int | None

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProductionBatchMetricsResponse(BaseModel):

    batch_id: int

    batch_number: str

    planned_quantity: float

    produced_quantity: float

    rejected_quantity: float

    good_quantity: float

    completion_percentage: float

    rejection_percentage: float

    production_efficiency: float


class ProductionBatchListResponse(BaseModel):

    items: list[ProductionBatchResponse]

    total: int

    page: int

    page_size: int

    total_pages: int