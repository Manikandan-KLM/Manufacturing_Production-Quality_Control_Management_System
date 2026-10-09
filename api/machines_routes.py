from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.machine_schema import (
    MachineCreateRequest,
    MachineUpdateRequest,
    MachineStatusUpdateRequest,
    MachineOperatingHoursRequest,
    MachineProductionLineRequest,
    MachineResponse,
    MachineListResponse
)

from services.machine_service import (
    MachineService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/machines",
    tags=["Machines"]
)


# =========================================
# CREATE
# =========================================

@router.post(
    "",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED
)
def create_machine(
    data: MachineCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = MachineService(db)

    return service.create_machine(
        data
    )


# =========================================
# LIST
# =========================================

@router.get(
    "",
    response_model=MachineListResponse
)
def get_machines(
    search: str | None = None,
    machine_type: str | None = None,
    machine_status: str | None = Query(
        default=None,
        alias="status"
    ),
    production_line_id: int | None = None,
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

    service = MachineService(db)

    return service.get_machines(
        search=search,
        machine_type=machine_type,
        status=machine_status,
        production_line_id=(
            production_line_id
        ),
        page=page,
        page_size=page_size
    )


# =========================================
# GET SINGLE
# =========================================

@router.get(
    "/{machine_id}",
    response_model=MachineResponse
)
def get_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MachineService(db)

    return service.get_machine(
        machine_id
    )


# =========================================
# UPDATE
# =========================================

@router.put(
    "/{machine_id}",
    response_model=MachineResponse
)
def update_machine(
    machine_id: int,
    data: MachineUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = MachineService(db)

    return service.update_machine(
        machine_id,
        data
    )


# =========================================
# DELETE
# =========================================

@router.delete(
    "/{machine_id}"
)
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = MachineService(db)

    return service.delete_machine(
        machine_id
    )


# =========================================
# STATUS
# =========================================

@router.patch(
    "/{machine_id}/status",
    response_model=MachineResponse
)
def update_machine_status(
    machine_id: int,
    data: MachineStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Maintenance Engineer"
        )
    )
):

    service = MachineService(db)

    return service.update_status(
        machine_id,
        data.status
    )


# =========================================
# OPERATING HOURS
# =========================================

@router.patch(
    "/{machine_id}/operating-hours",
    response_model=MachineResponse
)
def update_operating_hours(
    machine_id: int,
    data: MachineOperatingHoursRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MachineService(db)

    return service.update_operating_hours(
        machine_id,
        data.operating_hours
    )


# =========================================
# PRODUCTION LINE
# =========================================

@router.patch(
    "/{machine_id}/production-line",
    response_model=MachineResponse
)
def update_production_line(
    machine_id: int,
    data: MachineProductionLineRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = MachineService(db)

    return service.update_production_line(
        machine_id,
        data.production_line_id
    )