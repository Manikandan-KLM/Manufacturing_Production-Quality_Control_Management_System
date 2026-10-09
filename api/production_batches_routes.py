from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.production_batch_schema import (
    ProductionBatchCreateRequest,
    ProductionBatchUpdateRequest,
    ProductionQuantityUpdateRequest,
    ProductionBatchTimeRequest,
    ProductionBatchResponse,
    ProductionBatchMetricsResponse,
    ProductionBatchListResponse
)

from services.production_batch_service import (
    ProductionBatchService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/production-batches",
    tags=["Production Batches"]
)


# =================================================
# CREATE BATCH
# =================================================

@router.post(
    "",
    response_model=ProductionBatchResponse,
    status_code=status.HTTP_201_CREATED
)
def create_production_batch(

    data: ProductionBatchCreateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = ProductionBatchService(db)

    return service.create_batch(data)


# =================================================
# LIST BATCHES
# =================================================

@router.get(
    "",
    response_model=ProductionBatchListResponse
)
def get_production_batches(

    production_order_id: int | None = None,

    production_line_id: int | None = None,

    machine_id: int | None = None,

    supervisor_id: int | None = None,

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

    service = ProductionBatchService(db)

    return service.get_batches(

        production_order_id=(
            production_order_id
        ),

        production_line_id=(
            production_line_id
        ),

        machine_id=machine_id,

        supervisor_id=supervisor_id,

        page=page,

        page_size=page_size
    )


# =================================================
# GET BATCH
# =================================================

@router.get(
    "/{batch_id}",
    response_model=ProductionBatchResponse
)
def get_production_batch(

    batch_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = ProductionBatchService(db)

    return service.get_batch(
        batch_id
    )


# =================================================
# UPDATE BATCH
# =================================================

@router.put(
    "/{batch_id}",
    response_model=ProductionBatchResponse
)
def update_production_batch(

    batch_id: int,

    data: ProductionBatchUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = ProductionBatchService(db)

    return service.update_batch(
        batch_id,
        data
    )


# =================================================
# UPDATE QUANTITIES
# =================================================

@router.patch(
    "/{batch_id}/quantities",
    response_model=ProductionBatchResponse
)
def update_production_quantities(

    batch_id: int,

    data: ProductionQuantityUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = ProductionBatchService(db)

    return service.update_quantities(

        batch_id,

        data.produced_quantity,

        data.rejected_quantity
    )


# =================================================
# UPDATE TIME
# =================================================

@router.patch(
    "/{batch_id}/time",
    response_model=ProductionBatchResponse
)
def update_production_time(

    batch_id: int,

    data: ProductionBatchTimeRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = ProductionBatchService(db)

    return service.update_time(

        batch_id,

        data.start_time,

        data.end_time
    )


# =================================================
# METRICS
# =================================================

@router.get(
    "/{batch_id}/metrics",
    response_model=ProductionBatchMetricsResponse
)
def get_production_metrics(

    batch_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = ProductionBatchService(db)

    return service.calculate_metrics(
        batch_id
    )


# =================================================
# DELETE
# =================================================

@router.delete(
    "/{batch_id}"
)
def delete_production_batch(

    batch_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = ProductionBatchService(db)

    return service.delete_batch(
        batch_id
    )