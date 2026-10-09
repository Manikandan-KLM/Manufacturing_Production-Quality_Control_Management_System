from pydantic import BaseModel, Field


class MaterialCreateRequest(BaseModel):

    material_code: str = Field(
        min_length=2,
        max_length=50
    )

    material_name: str = Field(
        min_length=2,
        max_length=150
    )

    category: str = Field(
        min_length=2,
        max_length=100
    )

    unit: str = Field(
        min_length=1,
        max_length=50
    )

    available_quantity: float = Field(
        default=0,
        ge=0
    )

    minimum_stock_level: float = Field(
        default=0,
        ge=0
    )

    reorder_level: float = Field(
        default=0,
        ge=0
    )

    supplier_reference: str | None = Field(
        default=None,
        max_length=150
    )

    status: str = "Active"

    description: str | None = None


class MaterialUpdateRequest(BaseModel):

    material_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    unit: str | None = Field(
        default=None,
        max_length=50
    )

    minimum_stock_level: float | None = Field(
        default=None,
        ge=0
    )

    reorder_level: float | None = Field(
        default=None,
        ge=0
    )

    supplier_reference: str | None = Field(
        default=None,
        max_length=150
    )

    status: str | None = None

    description: str | None = None


class MaterialStatusUpdateRequest(BaseModel):

    status: str


class StockInRequest(BaseModel):

    quantity: float = Field(
        gt=0
    )

    reference: str | None = Field(
        default=None,
        max_length=150
    )

    remarks: str | None = None


class StockOutRequest(BaseModel):

    quantity: float = Field(
        gt=0
    )

    reference: str | None = Field(
        default=None,
        max_length=150
    )

    remarks: str | None = None


class MaterialAdjustmentRequest(BaseModel):

    quantity: float

    reference: str | None = Field(
        default=None,
        max_length=150
    )

    remarks: str | None = None


class MaterialResponse(BaseModel):

    id: int

    material_code: str
    material_name: str

    category: str
    unit: str

    available_quantity: float

    minimum_stock_level: float
    reorder_level: float

    supplier_reference: str | None

    status: str

    description: str | None

    model_config = {
        "from_attributes": True
    }


class MaterialListResponse(BaseModel):

    items: list[MaterialResponse]

    total: int

    page: int

    page_size: int

    total_pages: int


class MaterialHistoryResponse(BaseModel):

    id: int

    material_id: int

    transaction_type: str

    quantity: float

    previous_quantity: float
    new_quantity: float

    reference: str | None
    remarks: str | None

    performed_by: int

    created_at: object

    model_config = {
        "from_attributes": True
    }