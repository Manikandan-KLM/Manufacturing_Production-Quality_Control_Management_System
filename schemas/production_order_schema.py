from datetime import date, datetime

from pydantic import BaseModel, Field


class ProductionOrderCreateRequest(BaseModel):

    product_id: int = Field(gt=0)

    quantity: float = Field(gt=0)

    target_date: date

    production_line_id: int = Field(gt=0)

    priority: str = "Medium"

    supervisor_id: int | None = Field(
        default=None,
        gt=0
    )


class ProductionOrderUpdateRequest(BaseModel):

    product_id: int | None = Field(
        default=None,
        gt=0
    )

    quantity: float | None = Field(
        default=None,
        gt=0
    )

    target_date: date | None = None

    production_line_id: int | None = Field(
        default=None,
        gt=0
    )

    priority: str | None = None

    supervisor_id: int | None = Field(
        default=None,
        gt=0
    )


class ProductionOrderStatusUpdateRequest(BaseModel):

    status: str


class ProductionOrderResponse(BaseModel):

    id: int
    order_number: str

    product_id: int
    quantity: float
    target_date: date

    production_line_id: int

    priority: str
    supervisor_id: int | None

    status: str

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProductionOrderListResponse(BaseModel):

    items: list[ProductionOrderResponse]

    total: int

    page: int
    page_size: int
    total_pages: int