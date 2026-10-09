from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.quality_schema import (
    QualityInspectionCreateRequest,
    QualityInspectionUpdateRequest,
    QualityParameterCreateRequest,
    QualityParameterUpdateRequest,
    QualityInspectionResponse,
    QualityInspectionListResponse,
    QualityParameterResponse,
    QualityInspectionDetailResponse
)

from services.quality_service import (
    QualityService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/quality",
    tags=["Quality Inspection"]
)


# =========================================
# CREATE INSPECTION
# =========================================

@router.post(
    "/inspections",
    response_model=QualityInspectionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_inspection(
    data: QualityInspectionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Quality Manager"
        )
    )
):

    service = QualityService(db)

    return service.create_inspection(
        data
    )


# =========================================
# LIST INSPECTIONS
# =========================================

@router.get(
    "/inspections",
    response_model=QualityInspectionListResponse
)
def get_inspections(
    inspection_type: str | None = None,
    overall_result: str | None = None,
    production_batch_id: int | None = Query(
        default=None,
        gt=0
    ),
    inspector_id: int | None = Query(
        default=None,
        gt=0
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = QualityService(db)

    return service.get_inspections(
        inspection_type=inspection_type,
        overall_result=overall_result,
        production_batch_id=production_batch_id,
        inspector_id=inspector_id,
        page=page,
        page_size=page_size
    )


# =========================================
# GET INSPECTION
# =========================================

@router.get(
    "/inspections/{inspection_id}",
    response_model=QualityInspectionResponse
)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = QualityService(db)

    return service.get_inspection(
        inspection_id
    )


# =========================================
# ADD PARAMETER
# =========================================

@router.post(
    "/inspections/{inspection_id}/parameters",
    response_model=QualityParameterResponse,
    status_code=status.HTTP_201_CREATED
)
def add_parameter(
    inspection_id: int,
    data: QualityParameterCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Quality Manager"
        )
    )
):

    service = QualityService(db)

    return service.add_parameter(
        inspection_id,
        data
    )


# =========================================
# UPDATE PARAMETER
# =========================================

@router.put(
    "/parameters/{parameter_id}",
    response_model=QualityParameterResponse
)
def update_parameter(
    parameter_id: int,
    data: QualityParameterUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Quality Manager"
        )
    )
):

    service = QualityService(db)

    return service.update_parameter(
        parameter_id,
        data
    )


# =========================================
# GET PARAMETERS
# =========================================

@router.get(
    "/inspections/{inspection_id}/parameters",
    response_model=list[QualityParameterResponse]
)
def get_parameters(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = QualityService(db)

    return service.get_parameters(
        inspection_id
    )


# =========================================
# GET COMPLETE INSPECTION
# =========================================

@router.get(
    "/inspections/{inspection_id}/details",
    response_model=QualityInspectionDetailResponse
)
def get_inspection_details(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = QualityService(db)

    inspection = service.get_inspection(
        inspection_id
    )

    parameters = service.get_parameters(
        inspection_id
    )

    return {
        "inspection": inspection,
        "parameters": parameters
    }