from datetime import datetime

from pydantic import BaseModel, Field


# =========================================
# BOM CREATE
# =========================================

class BOMCreateRequest(BaseModel):

    product_id: int = Field(
        gt=0
    )

    version: str = Field(
        min_length=1,
        max_length=20
    )

    status: str = "Inactive"

    description: str | None = Field(
        default=None,
        max_length=500
    )


# =========================================
# BOM UPDATE
# =========================================

class BOMUpdateRequest(BaseModel):

    version: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )


# =========================================
# BOM STATUS
# =========================================

class BOMStatusUpdateRequest(BaseModel):

    status: str


# =========================================
# ADD MATERIAL
# =========================================

class BOMItemCreateRequest(BaseModel):

    material_id: int = Field(
        gt=0
    )

    quantity_required: float = Field(
        gt=0
    )


# =========================================
# UPDATE MATERIAL
# =========================================

class BOMItemUpdateRequest(BaseModel):

    quantity_required: float = Field(
        gt=0
    )


# =========================================
# MATERIAL RESPONSE
# =========================================

class BOMItemResponse(BaseModel):

    id: int

    bom_id: int

    material_id: int

    quantity_required: float

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# BOM RESPONSE
# =========================================

class BOMResponse(BaseModel):

    id: int

    product_id: int

    version: str

    status: str

    description: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# =========================================
# BOM DETAILS RESPONSE
# =========================================

class BOMDetailResponse(BaseModel):

    id: int

    product_id: int

    version: str

    status: str

    description: str | None

    items: list[BOMItemResponse] = []

    model_config = {
        "from_attributes": True
    }


# =========================================
# BOM LIST
# =========================================

class BOMListResponse(BaseModel):

    items: list[BOMResponse]

    total: int

    page: int

    page_size: int

    total_pages: int