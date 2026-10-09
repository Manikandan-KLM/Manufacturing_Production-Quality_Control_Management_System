from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.shift_schema import (
    ShiftCreateRequest,
    ShiftUpdateRequest,
    ShiftStatusUpdateRequest,
    ShiftWorkerAssignmentRequest,
    ShiftMachineUsageRequest,
    ShiftProductionOutputRequest,
    ShiftResponse,
    ShiftListResponse,
    ShiftWorkerResponse,
    ShiftMachineUsageResponse,
    ShiftProductionOutputResponse,
    ShiftPerformanceResponse
)

from services.shift_service import ShiftService

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/shifts",
    tags=["Shifts"]
)


# =========================================
# CREATE SHIFT
# =========================================

@router.post(
    "",
    response_model=ShiftResponse,
    status_code=status.HTTP_201_CREATED
)
def create_shift(
    data: ShiftCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ShiftService(db)

    return service.create_shift(data)


# =========================================
# LIST SHIFTS
# =========================================

@router.get(
    "",
    response_model=ShiftListResponse
)
def get_shifts(
    search: str | None = None,
    shift_type: str | None = None,
    status: str | None = None,
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
    current_user=Depends(get_current_user)
):

    service = ShiftService(db)

    return service.get_shifts(
        search=search,
        shift_type=shift_type,
        status=status,
        plant_id=plant_id,
        page=page,
        page_size=page_size
    )


# =========================================
# GET SHIFT
# =========================================

@router.get(
    "/{shift_id}",
    response_model=ShiftResponse
)
def get_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = ShiftService(db)

    return service.get_shift(
        shift_id
    )


# =========================================
# UPDATE SHIFT
# =========================================

@router.put(
    "/{shift_id}",
    response_model=ShiftResponse
)
def update_shift(
    shift_id: int,
    data: ShiftUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ShiftService(db)

    return service.update_shift(
        shift_id,
        data
    )


# =========================================
# UPDATE STATUS
# =========================================

@router.patch(
    "/{shift_id}/status",
    response_model=ShiftResponse
)
def update_shift_status(
    shift_id: int,
    data: ShiftStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = ShiftService(db)

    return service.update_status(
        shift_id,
        data.status
    )


# =========================================
# ASSIGN WORKER
# =========================================

@router.post(
    "/{shift_id}/workers",
    response_model=ShiftWorkerResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_worker(
    shift_id: int,
    data: ShiftWorkerAssignmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = ShiftService(db)

    return service.assign_worker(
        shift_id=shift_id,
        worker_id=data.worker_id,
        work_date=data.work_date
    )


# =========================================
# REMOVE WORKER
# =========================================

@router.delete(
    "/{shift_id}/workers/{worker_id}",
    response_model=ShiftWorkerResponse
)
def remove_worker(
    shift_id: int,
    worker_id: int,
    work_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = ShiftService(db)

    return service.remove_worker(
        shift_id,
        worker_id,
        work_date
    )


# =========================================
# MACHINE USAGE
# =========================================

@router.post(
    "/{shift_id}/machine-usage",
    response_model=ShiftMachineUsageResponse,
    status_code=status.HTTP_201_CREATED
)
def add_machine_usage(
    shift_id: int,
    data: ShiftMachineUsageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Production Manager",
            "Maintenance Engineer"
        )
    )
):

    service = ShiftService(db)

    return service.add_machine_usage(
        shift_id,
        data
    )


# =========================================
# PRODUCTION OUTPUT
# =========================================

@router.post(
    "/{shift_id}/production-output",
    response_model=ShiftProductionOutputResponse,
    status_code=status.HTTP_201_CREATED
)
def add_production_output(
    shift_id: int,
    data: ShiftProductionOutputRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Production Manager"
        )
    )
):

    service = ShiftService(db)

    return service.add_production_output(
        shift_id,
        data
    )


# =========================================
# SHIFT PERFORMANCE
# =========================================

@router.get(
    "/{shift_id}/performance",
    response_model=ShiftPerformanceResponse
)
def get_shift_performance(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = ShiftService(db)

    return service.get_shift_performance(
        shift_id
    )