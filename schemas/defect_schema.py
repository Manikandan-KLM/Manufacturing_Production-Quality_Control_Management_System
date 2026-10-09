from datetime import datetime

from pydantic import BaseModel, Field


# =========================================
# CREATE DEFECT
# =========================================

class DefectCreateRequest(BaseModel):

    defect_number: str = Field(
        min_length=2,
        max_length=50
    )

    defect_type: str = Field(
        min_length=2,
        max_length=150
    )

    severity: str

    production_batch_id: int = Field(
        gt=0
    )

    product_id: int = Field(
        gt=0
    )

    quality_inspection_id: int | None = Field(
        default=None,
        gt=0
    )

    quantity_affected: float = Field(
        gt=0
    )

    root_cause: str = Field(
        min_length=2
    )

    corrective_action: str | None = None


# =========================================
# UPDATE DEFECT
# =========================================

class DefectUpdateRequest(BaseModel):

    defect_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    severity: str | None = None

    quantity_affected: float | None = Field(
        default=None,
        gt=0
    )

    root_cause: str | None = None

    corrective_action: str | None = None


# =========================================
# STATUS UPDATE
# =========================================

class DefectStatusUpdateRequest(BaseModel):

    resolution_status: str


# =========================================
# RESPONSE
# =========================================

class DefectResponse(BaseModel):

    id: int

    defect_number: str

    defect_type: str

    severity: str

    production_batch_id: int

    product_id: int

    quality_inspection_id: int | None

    quantity_affected: float

    root_cause: str

    corrective_action: str | None

    resolution_status: str

    reported_by: int

    resolved_by: int | None

    resolved_at: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# LIST RESPONSE
# =========================================

class DefectListResponse(BaseModel):

    items: list[DefectResponse]

    total: int

    page: int

    page_size: int

    total_pages: int