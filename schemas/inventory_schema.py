from datetime import datetime

from pydantic import BaseModel, Field


class RawMaterialReceiptRequest(BaseModel):

    transaction_number: str = Field(
        min_length=2,
        max_length=50
    )

    material_id: int = Field(
        gt=0
    )

    quantity: float = Field(
        gt=0
    )

    reference_number: str | None = None

    reason: str | None = None


class MaterialConsumptionRequest(BaseModel):

    transaction_number: str = Field(
        min_length=2,
        max_length=50
    )

    material_id: int = Field(
        gt=0
    )

    quantity: float = Field(
        gt=0
    )

    production_batch_id: int = Field(
        gt=0
    )

    reference_number: str | None = None

    reason: str | None = None


class FinishedGoodsProductionRequest(BaseModel):

    transaction_number: str = Field(
        min_length=2,
        max_length=50
    )

    product_id: int = Field(
        gt=0
    )

    quantity: float = Field(
        gt=0
    )

    production_batch_id: int = Field(
        gt=0
    )

    reference_number: str | None = None

    reason: str | None = None


class RejectedGoodsRequest(BaseModel):

    transaction_number: str = Field(
        min_length=2,
        max_length=50
    )

    product_id: int = Field(
        gt=0
    )

    quantity: float = Field(
        gt=0
    )

    production_batch_id: int = Field(
        gt=0
    )

    reference_number: str | None = None

    reason: str | None = None


class StockAdjustmentRequest(BaseModel):

    transaction_number: str = Field(
        min_length=2,
        max_length=50
    )

    material_id: int = Field(
        gt=0
    )

    quantity: float

    reason: str = Field(
        min_length=2
    )

    reference_number: str | None = None


class InventoryMovementResponse(BaseModel):

    id: int

    transaction_number: str

    movement_type: str

    material_id: int | None

    product_id: int | None

    production_batch_id: int | None

    quantity: float

    quantity_before: float

    quantity_after: float

    reference_number: str | None

    reason: str | None

    performed_by: int

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class InventoryMovementListResponse(BaseModel):

    items: list[InventoryMovementResponse]

    total: int

    page: int

    page_size: int

    total_pages: int