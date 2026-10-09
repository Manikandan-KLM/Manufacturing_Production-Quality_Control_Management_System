from pydantic import BaseModel, Field


class PlantCreateRequest(BaseModel):
    plant_code: str = Field(
        min_length=2,
        max_length=50
    )

    plant_name: str = Field(
        min_length=2,
        max_length=150
    )

    address: str = Field(
        min_length=5
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    state: str = Field(
        min_length=2,
        max_length=100
    )

    country: str = Field(
        default="India",
        max_length=100
    )

    production_capacity: float = Field(
        gt=0
    )

    capacity_unit: str = Field(
        default="units/day",
        max_length=50
    )

    status: str = "Active"

    manager_id: int | None = None


class PlantUpdateRequest(BaseModel):
    plant_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    address: str | None = None

    city: str | None = None

    state: str | None = None

    country: str | None = None

    production_capacity: float | None = Field(
        default=None,
        gt=0
    )

    capacity_unit: str | None = None

    status: str | None = None

    manager_id: int | None = None


class PlantStatusUpdateRequest(BaseModel):
    status: str


class PlantCapacityUpdateRequest(BaseModel):
    production_capacity: float = Field(
        gt=0
    )

    capacity_unit: str = Field(
        default="units/day"
    )


class PlantManagerUpdateRequest(BaseModel):
    manager_id: int


class PlantResponse(BaseModel):
    id: int
    plant_code: str
    plant_name: str

    address: str
    city: str
    state: str
    country: str

    production_capacity: float
    capacity_unit: str

    status: str
    manager_id: int | None

    model_config = {
        "from_attributes": True
    }