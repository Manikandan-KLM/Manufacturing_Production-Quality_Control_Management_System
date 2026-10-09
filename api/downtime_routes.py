from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    status,
    Query
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.downtime_schema import (
    DowntimeCreateRequest,
    DowntimeEndRequest,
    DowntimeUpdateRequest,
    DowntimeResponse,
    DowntimeListResponse,
    DowntimePercentageResponse
)

from services.downtime_service import (
    DowntimeService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/downtime",
    tags=["Downtime Management"]
)


# =========================================================
# CREATE DOWNTIME
# =========================================================

@router.post(
    "",
    response_model=DowntimeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_downtime(
    data: DowntimeCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager",
            "Maintenance Engineer"
        )
    )
):

    service = DowntimeService(db)

    return service.create_downtime(
        data
    )


# =========================================================
# GET DOWNTIME
# =========================================================

@router.get(
    "/{downtime_id}",
    response_model=DowntimeResponse
)
def get_downtime(
    downtime_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    service = DowntimeService(db)

    return service.get_downtime(
        downtime_id
    )


# =========================================================
# END DOWNTIME
# =========================================================

@router.patch(
    "/{downtime_id}/end",
    response_model=DowntimeResponse
)
def end_downtime(
    downtime_id: int,
    data: DowntimeEndRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager",
            "Maintenance Engineer"
        )
    )
):

    service = DowntimeService(db)

    return service.end_downtime(
        downtime_id,
        data.end_time
    )


# =========================================================
# UPDATE DOWNTIME
# =========================================================

@router.put(
    "/{downtime_id}",
    response_model=DowntimeResponse
)
def update_downtime(
    downtime_id: int,
    data: DowntimeUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager",
            "Maintenance Engineer"
        )
    )
):

    service = DowntimeService(db)

    return service.update_downtime(
        downtime_id,
        data
    )


# =========================================================
# LIST DOWNTIME
# =========================================================

@router.get(
    "",
    response_model=DowntimeListResponse
)
def list_downtime(
    machine_id: int | None = Query(
        default=None,
        gt=0
    ),

    production_line_id: int | None = Query(
        default=None,
        gt=0
    ),

    category: str | None = None,

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

    service = DowntimeService(db)

    return service.get_list(
        machine_id=machine_id,
        production_line_id=production_line_id,
        category=category,
        page=page,
        page_size=page_size
    )


# =========================================================
# DOWNTIME PERCENTAGE
# =========================================================

@router.get(
    "/machine/{machine_id}/percentage",
    response_model=DowntimePercentageResponse
)
def downtime_percentage(
    machine_id: int,

    total_period_minutes: float = Query(
        gt=0
    ),

    start_date: datetime = Query(),

    end_date: datetime = Query(),

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = DowntimeService(db)

    if end_date <= start_date:

        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    return service.calculate_downtime_percentage(
        machine_id=machine_id,
        total_period_minutes=total_period_minutes,
        start_date=start_date,
        end_date=end_date
    )