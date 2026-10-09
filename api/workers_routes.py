from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.worker_schema import (
    WorkerCreateRequest,
    WorkerUpdateRequest,
    WorkerStatusUpdateRequest,
    WorkerBatchAssignmentRequest,
    WorkerResponse,
    WorkerBatchAssignmentResponse,
    WorkerListResponse
)

from services.worker_service import (
    WorkerService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/workers",
    tags=["Workers"]
)


# =================================================
# CREATE WORKER
# =================================================

@router.post(
    "",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_worker(

    data: WorkerCreateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = WorkerService(db)

    return service.create_worker(
        data
    )


# =================================================
# LIST WORKERS
# =================================================

@router.get(
    "",
    response_model=WorkerListResponse
)
def get_workers(

    search: str | None = None,

    department: str | None = None,

    shift: str | None = None,

    worker_status: str | None = Query(
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

    current_user=Depends(
        get_current_user
    )
):

    service = WorkerService(db)

    return service.get_workers(

        search=search,

        department=department,

        shift=shift,

        status=worker_status,

        production_line_id=(
            production_line_id
        ),

        page=page,

        page_size=page_size
    )


# =================================================
# GET WORKER
# =================================================

@router.get(
    "/{worker_id}",
    response_model=WorkerResponse
)
def get_worker(

    worker_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = WorkerService(db)

    return service.get_worker(
        worker_id
    )


# =================================================
# UPDATE WORKER
# =================================================

@router.put(
    "/{worker_id}",
    response_model=WorkerResponse
)
def update_worker(

    worker_id: int,

    data: WorkerUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = WorkerService(db)

    return service.update_worker(
        worker_id,
        data
    )


# =================================================
# UPDATE STATUS
# =================================================

@router.patch(
    "/{worker_id}/status",
    response_model=WorkerResponse
)
def update_worker_status(

    worker_id: int,

    data: WorkerStatusUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = WorkerService(db)

    return service.update_status(
        worker_id,
        data.status
    )


# =================================================
# ASSIGN WORKER TO BATCH
# =================================================

@router.post(
    "/assign-batch",
    response_model=WorkerBatchAssignmentResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_worker_to_batch(

    data: WorkerBatchAssignmentRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = WorkerService(db)

    return service.assign_worker_to_batch(

        data.worker_id,

        data.production_batch_id
    )


# =================================================
# REMOVE WORKER FROM BATCH
# =================================================

@router.delete(
    "/{worker_id}/batches/{production_batch_id}"
)
def remove_worker_from_batch(

    worker_id: int,

    production_batch_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = WorkerService(db)

    return service.remove_worker_from_batch(

        worker_id,

        production_batch_id
    )


# =================================================
# WORKER ASSIGNMENT HISTORY
# =================================================

@router.get(
    "/{worker_id}/assignments",
    response_model=list[
        WorkerBatchAssignmentResponse
    ]
)
def get_worker_assignments(

    worker_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = WorkerService(db)

    return service.get_worker_assignments(
        worker_id
    )


# =================================================
# BATCH ASSIGNMENTS
# =================================================

@router.get(
    "/batch/{production_batch_id}/workers",
    response_model=list[
        WorkerBatchAssignmentResponse
    ]
)
def get_batch_assignments(

    production_batch_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = WorkerService(db)

    return service.get_batch_assignments(
        production_batch_id
    )


# =================================================
# DELETE
# =================================================

@router.delete(
    "/{worker_id}"
)
def delete_worker(

    worker_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = WorkerService(db)

    return service.delete_worker(
        worker_id
    )