from datetime import date, datetime

from pydantic import BaseModel, Field


# =========================================
# CREATE INSPECTION
# =========================================

class QualityInspectionCreateRequest(BaseModel):

    inspection_number: str = Field(
        min_length=2,
        max_length=50
    )

    inspection_type: str

    production_batch_id: int = Field(
        gt=0
    )

    inspector_id: int = Field(
        gt=0
    )

    inspection_date: date

    remarks: str | None = None


# =========================================
# UPDATE INSPECTION
# =========================================

class QualityInspectionUpdateRequest(BaseModel):

    inspection_type: str | None = None

    inspector_id: int | None = Field(
        default=None,
        gt=0
    )

    inspection_date: date | None = None

    remarks: str | None = None


# =========================================
# PARAMETER CREATE
# =========================================

class QualityParameterCreateRequest(BaseModel):

    parameter_name: str = Field(
        min_length=2,
        max_length=150
    )

    unit: str | None = Field(
        default=None,
        max_length=50
    )

    expected_value: float

    actual_value: float

    remarks: str | None = None


# =========================================
# PARAMETER UPDATE
# =========================================

class QualityParameterUpdateRequest(BaseModel):

    parameter_name: str | None = None

    unit: str | None = None

    expected_value: float | None = None

    actual_value: float | None = None

    remarks: str | None = None


# =========================================
# INSPECTION RESPONSE
# =========================================

class QualityInspectionResponse(BaseModel):

    id: int

    inspection_number: str

    inspection_type: str

    production_batch_id: int

    inspector_id: int

    inspection_date: date

    overall_result: str

    remarks: str | None

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# PARAMETER RESPONSE
# =========================================

class QualityParameterResponse(BaseModel):

    id: int

    inspection_id: int

    parameter_name: str

    unit: str | None

    expected_value: float

    actual_value: float

    result: str

    remarks: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# LIST RESPONSE
# =========================================

class QualityInspectionListResponse(BaseModel):

    items: list[QualityInspectionResponse]

    total: int

    page: int

    page_size: int

    total_pages: int


# =========================================
# COMPLETE INSPECTION RESPONSE
# =========================================

class QualityInspectionDetailResponse(BaseModel):

    inspection: QualityInspectionResponse

    parameters: list[QualityParameterResponse]