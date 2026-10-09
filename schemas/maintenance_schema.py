from datetime import date, datetime

from pydantic import BaseModel, Field


class MaintenanceScheduleCreateRequest(BaseModel):

    schedule_code: str = Field(
        min_length=2,
        max_length=50
    )

    machine_id: int = Field(gt=0)

    maintenance_type: str

    frequency_days: int | None = Field(
        default=None,
        gt=0
    )

    last_maintenance_date: date | None = None

    next_due_date: date


class MaintenanceScheduleUpdateRequest(BaseModel):

    maintenance_type: str | None = None

    frequency_days: int | None = Field(
        default=None,
        gt=0
    )

    last_maintenance_date: date | None = None

    next_due_date: date | None = None


class MaintenanceScheduleStatusRequest(BaseModel):

    status: str


class MaintenanceCreateRequest(BaseModel):

    maintenance_number: str = Field(
        min_length=2,
        max_length=50
    )

    machine_id: int = Field(gt=0)

    maintenance_type: str

    maintenance_date: date

    description: str = Field(
        min_length=2
    )

    technician_id: int | None = Field(
        default=None,
        gt=0
    )

    labor_cost: float = Field(
        default=0,
        ge=0
    )

    remarks: str | None = None


class MaintenanceUpdateRequest(BaseModel):

    description: str | None = None

    technician_id: int | None = Field(
        default=None,
        gt=0
    )

    labor_cost: float | None = Field(
        default=None,
        ge=0
    )

    remarks: str | None = None


class MaintenanceStatusRequest(BaseModel):

    status: str


class SparePartUsageRequest(BaseModel):

    material_id: int = Field(gt=0)

    quantity_used: float = Field(gt=0)

    unit_cost: float = Field(ge=0)


class MaintenanceResponse(BaseModel):

    id: int
    maintenance_number: str
    machine_id: int
    maintenance_type: str
    maintenance_date: date
    description: str
    technician_id: int | None
    status: str
    labor_cost: float
    spare_parts_cost: float
    total_cost: float
    remarks: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MaintenanceScheduleResponse(BaseModel):

    id: int
    schedule_code: str
    machine_id: int
    maintenance_type: str
    frequency_days: int | None
    last_maintenance_date: date | None
    next_due_date: date
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MaintenanceSparePartResponse(BaseModel):

    id: int
    maintenance_id: int
    material_id: int
    quantity_used: float
    unit_cost: float
    total_cost: float
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MaintenanceAlertResponse(BaseModel):

    id: int
    machine_id: int
    schedule_id: int
    alert_message: str
    due_date: datetime
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
    