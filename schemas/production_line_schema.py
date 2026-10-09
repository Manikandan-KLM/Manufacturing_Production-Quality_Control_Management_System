from pydantic import BaseModel, Field


class ProductionLineCreateRequest(BaseModel):

    line_code: str = Field(
        min_length=2,
        max_length=50
    )

    line_name: str = Field(
        min_length=2,
        max_length=150
    )

    production_capacity: float = Field(
        gt=0
    )

    capacity_unit: str = Field(
        default="units/day",
        max_length=50
    )

    plant_id: int = Field(
        gt=0
    )

    status: str = "Active"

    supervisor_id: int | None = None


class ProductionLineUpdateRequest(BaseModel):

    line_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    production_capacity: float | None = Field(
        default=None,
        gt=0
    )

    capacity_unit: str | None = None

    plant_id: int | None = Field(
        default=None,
        gt=0
    )

    status: str | None = None

    supervisor_id: int | None = None


class ProductionLineStatusUpdateRequest(BaseModel):

    status: str


class ProductionLineSupervisorUpdateRequest(BaseModel):

    supervisor_id: int


class ProductionLineResponse(BaseModel):

    id: int
    line_code: str
    line_name: str

    production_capacity: float
    capacity_unit: str

    plant_id: int
    status: str

    supervisor_id: int | None

    model_config = {
        "from_attributes": True
    }


class ProductionLineListResponse(BaseModel):

    items: list[ProductionLineResponse]

    total: int
    page: int
    page_size: int
    total_pages: int