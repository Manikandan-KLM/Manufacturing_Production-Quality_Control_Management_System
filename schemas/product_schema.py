from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):

    product_code: str = Field(
        min_length=2,
        max_length=50
    )

    product_name: str = Field(
        min_length=2,
        max_length=150
    )

    category: str = Field(
        min_length=2,
        max_length=100
    )

    sku: str = Field(
        min_length=2,
        max_length=100
    )

    unit_of_measurement: str = Field(
        min_length=1,
        max_length=50
    )

    status: str = "Active"

    standard_production_time: float = Field(
        gt=0
    )

    production_time_unit: str = Field(
        default="minutes",
        max_length=50
    )

    description: str | None = None


class ProductUpdateRequest(BaseModel):

    product_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    unit_of_measurement: str | None = None

    status: str | None = None

    standard_production_time: float | None = Field(
        default=None,
        gt=0
    )

    production_time_unit: str | None = None

    description: str | None = None


class ProductStatusUpdateRequest(BaseModel):

    status: str


class ProductResponse(BaseModel):

    id: int

    product_code: str
    product_name: str

    category: str
    sku: str

    unit_of_measurement: str

    status: str

    standard_production_time: float
    production_time_unit: str

    description: str | None

    model_config = {
        "from_attributes": True
    }


class ProductListResponse(BaseModel):

    items: list[ProductResponse]

    total: int

    page: int

    page_size: int

    total_pages: int