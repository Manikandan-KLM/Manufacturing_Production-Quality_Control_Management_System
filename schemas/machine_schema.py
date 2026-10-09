from datetime import date, datetime

from pydantic import BaseModel, Field


# =========================================
# CREATE MACHINE
# =========================================

class MachineCreateRequest(BaseModel):

    machine_code: str = Field(
        min_length=2,
        max_length=50
    )

    machine_name: str = Field(
        min_length=2,
        max_length=150
    )

    machine_type: str = Field(
        min_length=2,
        max_length=100
    )

    production_line_id: int = Field(
        gt=0
    )

    installation_date: date

    status: str = "Idle"

    operating_hours: float = Field(
        default=0,
        ge=0
    )


# =========================================
# UPDATE MACHINE
# =========================================

class MachineUpdateRequest(BaseModel):

    machine_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    machine_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    installation_date: date | None = None

    operating_hours: float | None = Field(
        default=None,
        ge=0
    )


# =========================================
# STATUS UPDATE
# =========================================

class MachineStatusUpdateRequest(BaseModel):

    status: str


# =========================================
# OPERATING HOURS
# =========================================

class MachineOperatingHoursRequest(BaseModel):

    operating_hours: float = Field(
        ge=0
    )


# =========================================
# PRODUCTION LINE
# =========================================

class MachineProductionLineRequest(BaseModel):

    production_line_id: int = Field(
        gt=0
    )


# =========================================
# RESPONSE
# =========================================

class MachineResponse(BaseModel):

    id: int

    machine_code: str
    machine_name: str

    machine_type: str

    production_line_id: int

    installation_date: date

    status: str

    operating_hours: float

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# LIST RESPONSE
# =========================================

class MachineListResponse(BaseModel):

    items: list[MachineResponse]

    total: int

    page: int

    page_size: int

    total_pages: int