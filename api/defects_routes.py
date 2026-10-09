from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.defect_schema import (
    DefectCreateRequest,
    DefectUpdateRequest,
    DefectStatusUpdateRequest,
    DefectResponse,
    DefectListResponse
)

from services.defect_service import (
    DefectService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/defects",
    tags=["Defect Management"]
)


# =========================================
# CREATE DEFECT
# =========================================

@router.post(
    "",
    response_model=DefectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_defect(
    data: DefectCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Quality Manager",
            "Production Manager"
        )
    )
):

    service = DefectService(db)

    return service.create_defect(
        data=data,
        reported_by=current_user.id
    )


# =========================================
# LIST DEFECTS
# =========================================

@router.get(
    "",
    response_model=DefectListResponse
)
def get_defects(
    search: str | None = None,
    defect_type: str | None = None,
    severity: str | None = None,
    resolution_status: str | None = None,
    production_batch_id: int | None = Query(
        default=None,
        gt=0
    ),
    product_id: int | None = Query(
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

    service = DefectService(db)

    return service.get_defects(
        search=search,
        defect_type=defect_type,
        severity=severity,
        resolution_status=resolution_status,
        production_batch_id=production_batch_id,
        product_id=product_id,
        page=page,
        page_size=page_size
    )


# =========================================
# GET DEFECT
# =========================================

@router.get(
    "/{defect_id}",
    response_model=DefectResponse
)
def get_defect(
    defect_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = DefectService(db)

    return service.get_defect(
        defect_id
    )


# =========================================
# UPDATE DEFECT
# =========================================

@router.put(
    "/{defect_id}",
    response_model=DefectResponse
)
def update_defect(
    defect_id: int,
    data: DefectUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Quality Manager",
            "Production Manager"
        )
    )
):

    service = DefectService(db)

    return service.update_defect(
        defect_id,
        data
    )


# =========================================
# UPDATE STATUS
# =========================================

@router.patch(
    "/{defect_id}/status",
    response_model=DefectResponse
)
def update_status(
    defect_id: int,
    data: DefectStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Quality Manager",
            "Production Manager"
        )
    )
):

    service = DefectService(db)

    return service.update_status(
        defect_id=defect_id,
        resolution_status=data.resolution_status,
        user_id=current_user.id
    )