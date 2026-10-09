from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from models.user_model import User

from schemas.production_line_schema import (
    ProductionLineCreateRequest,
    ProductionLineUpdateRequest,
    ProductionLineResponse,
    ProductionLineListResponse,
    ProductionLineStatusUpdateRequest,
    ProductionLineSupervisorUpdateRequest
)

from services.production_line_service import (
    ProductionLineService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/production-lines",
    tags=["Production Lines"]
)


# ==================================================
# CREATE
# ==================================================

@router.post(
    "",
    response_model=ProductionLineResponse,
    status_code=status.HTTP_201_CREATED
)
def create_production_line(
    request: ProductionLineCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ProductionLineService(db)

    return service.create_line(request)


# ==================================================
# LIST
# SEARCH + FILTER + PAGINATION
# ==================================================

@router.get(
    "",
    response_model=ProductionLineListResponse
)
def get_production_lines(
    search: str | None = Query(
        default=None
    ),

    status: str | None = Query(
        default=None
    ),

    plant_id: int | None = Query(
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

    current_user: User = Depends(
        get_current_user
    )
):

    service = ProductionLineService(db)

    return service.get_lines(
        search=search,
        status=status,
        plant_id=plant_id,
        page=page,
        page_size=page_size
    )


# ==================================================
# GET DETAILS
# ==================================================

@router.get(
    "/{line_id}",
    response_model=ProductionLineResponse
)
def get_production_line(
    line_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    service = ProductionLineService(db)

    return service.get_line(line_id)


# ==================================================
# UPDATE
# ==================================================

@router.put(
    "/{line_id}",
    response_model=ProductionLineResponse
)
def update_production_line(
    line_id: int,

    request: ProductionLineUpdateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ProductionLineService(db)

    return service.update_line(
        line_id,
        request
    )


# ==================================================
# DELETE
# ==================================================

@router.delete(
    "/{line_id}"
)
def delete_production_line(
    line_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles("Super Admin")
    )
):

    service = ProductionLineService(db)

    return service.delete_line(line_id)


# ==================================================
# UPDATE STATUS
# ==================================================

@router.patch(
    "/{line_id}/status",
    response_model=ProductionLineResponse
)
def update_production_line_status(
    line_id: int,

    request: ProductionLineStatusUpdateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ProductionLineService(db)

    return service.update_status(
        line_id,
        request.status
    )


# ==================================================
# ASSIGN SUPERVISOR
# ==================================================

@router.patch(
    "/{line_id}/supervisor",
    response_model=ProductionLineResponse
)
def assign_supervisor(
    line_id: int,

    request: ProductionLineSupervisorUpdateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ProductionLineService(db)

    return service.assign_supervisor(
        line_id,
        request.supervisor_id
    )