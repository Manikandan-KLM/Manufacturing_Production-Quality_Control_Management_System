from datetime import date, datetime, time

from pydantic import BaseModel, Field


# -----------------------------------------
# CREATE
# -----------------------------------------

class ShiftCreateRequest(BaseModel):

    shift_code: str = Field(
        min_length=2,
        max_length=50
    )

    shift_name: str = Field(
        min_length=2,
        max_length=100
    )

    start_time: time

    end_time: time

    shift_type: str

    status: str = "Active"

    plant_id: int = Field(gt=0)


# -----------------------------------------
# UPDATE
# -----------------------------------------

class ShiftUpdateRequest(BaseModel):

    shift_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    start_time: time | None = None

    end_time: time | None = None

    shift_type: str | None = None

    plant_id: int | None = Field(
        default=None,
        gt=0
    )


# -----------------------------------------
# STATUS
# -----------------------------------------

class ShiftStatusUpdateRequest(BaseModel):

    status: str


# -----------------------------------------
# WORKER ASSIGNMENT
# -----------------------------------------

class ShiftWorkerAssignmentRequest(BaseModel):

    worker_id: int = Field(gt=0)

    work_date: date


# -----------------------------------------
# MACHINE USAGE
# -----------------------------------------

class ShiftMachineUsageRequest(BaseModel):

    machine_id: int = Field(gt=0)

    work_date: date

    operating_hours: float = Field(
        ge=0
    )

    idle_hours: float = Field(
        ge=0
    )

    breakdown_hours: float = Field(
        ge=0
    )

    remarks: str | None = None


# -----------------------------------------
# PRODUCTION OUTPUT
# -----------------------------------------

class ShiftProductionOutputRequest(BaseModel):

    production_batch_id: int = Field(gt=0)

    work_date: date

    planned_quantity: float = Field(
        gt=0
    )

    produced_quantity: float = Field(
        ge=0
    )

    rejected_quantity: float = Field(
        ge=0
    )


# -----------------------------------------
# RESPONSE
# -----------------------------------------

class ShiftResponse(BaseModel):

    id: int

    shift_code: str

    shift_name: str

    start_time: time

    end_time: time

    shift_type: str

    status: str

    plant_id: int

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ShiftListResponse(BaseModel):

    items: list[ShiftResponse]

    total: int

    page: int

    page_size: int

    total_pages: int


class ShiftWorkerResponse(BaseModel):

    id: int

    shift_id: int

    worker_id: int

    work_date: date

    assigned_at: datetime

    is_active: bool

    model_config = {
        "from_attributes": True
    }


class ShiftMachineUsageResponse(BaseModel):

    id: int

    shift_id: int

    machine_id: int

    work_date: date

    operating_hours: float

    idle_hours: float

    breakdown_hours: float

    remarks: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ShiftProductionOutputResponse(BaseModel):

    id: int

    shift_id: int

    production_batch_id: int

    work_date: date

    planned_quantity: float

    produced_quantity: float

    rejected_quantity: float

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ShiftPerformanceResponse(BaseModel):

    shift_id: int

    total_workers: int

    total_machines: int

    planned_quantity: float

    produced_quantity: float

    rejected_quantity: float

    production_completion_percentage: float

    rejection_percentage: float

    machine_operating_hours: float

    machine_idle_hours: float

    machine_breakdown_hours: float

    machine_utilization_percentage: float

    shift_performance_percentage: float