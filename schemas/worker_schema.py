from datetime import date, datetime

from pydantic import BaseModel, Field


# =========================================
# CREATE
# =========================================

class WorkerCreateRequest(BaseModel):

    employee_code: str = Field(
        min_length=2,
        max_length=50
    )

    full_name: str = Field(
        min_length=2,
        max_length=150
    )

    skill: str = Field(
        min_length=2,
        max_length=150
    )

    department: str = Field(
        min_length=2,
        max_length=100
    )

    shift: str = "General"

    production_line_id: int | None = Field(
        default=None,
        gt=0
    )

    status: str = "Active"

    joining_date: date | None = None


# =========================================
# UPDATE
# =========================================

class WorkerUpdateRequest(BaseModel):

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    skill: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    department: str | None = None

    shift: str | None = None

    production_line_id: int | None = Field(
        default=None,
        gt=0
    )

    joining_date: date | None = None


# =========================================
# STATUS
# =========================================

class WorkerStatusUpdateRequest(BaseModel):

    status: str


# =========================================
# BATCH ASSIGNMENT
# =========================================

class WorkerBatchAssignmentRequest(BaseModel):

    worker_id: int = Field(
        gt=0
    )

    production_batch_id: int = Field(
        gt=0
    )


# =========================================
# RESPONSE
# =========================================

class WorkerResponse(BaseModel):

    id: int

    employee_code: str

    full_name: str

    skill: str

    department: str

    shift: str

    production_line_id: int | None

    status: str

    joining_date: date | None

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# ASSIGNMENT RESPONSE
# =========================================

class WorkerBatchAssignmentResponse(BaseModel):

    id: int

    worker_id: int

    production_batch_id: int

    assigned_at: datetime

    removed_at: datetime | None

    is_active: bool

    model_config = {
        "from_attributes": True
    }


# =========================================
# LIST
# =========================================

class WorkerListResponse(BaseModel):

    items: list[WorkerResponse]

    total: int

    page: int

    page_size: int

    total_pages: int