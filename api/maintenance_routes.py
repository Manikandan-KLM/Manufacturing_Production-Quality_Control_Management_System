from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.maintenance_schema import (
    MaintenanceScheduleCreateRequest,
    MaintenanceScheduleUpdateRequest,
    MaintenanceScheduleStatusRequest,
    MaintenanceCreateRequest,
    MaintenanceUpdateRequest,
    MaintenanceStatusRequest,
    SparePartUsageRequest,
    MaintenanceResponse,
    MaintenanceScheduleResponse,
    MaintenanceSparePartResponse,
    MaintenanceAlertResponse
)

from services.maintenance_service import (
    MaintenanceService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/maintenance",
    tags=["Machine Maintenance"]
)


# =========================================================
# CREATE MAINTENANCE SCHEDULE
# =========================================================

@router.post(
    "/schedules",
    response_model=MaintenanceScheduleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_schedule(
    data: MaintenanceScheduleCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.create_schedule(data)


# =========================================================
# UPDATE SCHEDULE
# =========================================================

@router.put(
    "/schedules/{schedule_id}",
    response_model=MaintenanceScheduleResponse
)
def update_schedule(
    schedule_id: int,
    data: MaintenanceScheduleUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.update_schedule(
        schedule_id,
        data
    )


# =========================================================
# SCHEDULE STATUS
# =========================================================

@router.patch(
    "/schedules/{schedule_id}/status",
    response_model=MaintenanceScheduleResponse
)
def update_schedule_status(
    schedule_id: int,
    data: MaintenanceScheduleStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.update_schedule_status(
        schedule_id,
        data.status
    )


# =========================================================
# CREATE MAINTENANCE
# =========================================================

@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_maintenance(
    data: MaintenanceCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.create_maintenance(data)


# =========================================================
# GET MAINTENANCE
# =========================================================

@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaintenanceService(db)

    maintenance = (
        service.repository
        .get_maintenance_by_id(
            maintenance_id
        )
    )

    if not maintenance:

        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    return maintenance


# =========================================================
# UPDATE MAINTENANCE
# =========================================================

@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def update_maintenance(
    maintenance_id: int,
    data: MaintenanceUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.update_maintenance(
        maintenance_id,
        data
    )


# =========================================================
# MAINTENANCE STATUS
# =========================================================

@router.patch(
    "/{maintenance_id}/status",
    response_model=MaintenanceResponse
)
def update_maintenance_status(
    maintenance_id: int,
    data: MaintenanceStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.update_maintenance_status(
        maintenance_id,
        data.status
    )


# =========================================================
# SPARE PART USAGE
# =========================================================

@router.post(
    "/{maintenance_id}/spare-parts",
    response_model=MaintenanceSparePartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_spare_part(
    maintenance_id: int,
    data: SparePartUsageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer",
            "Store Manager"
        )
    )
):

    service = MaintenanceService(db)

    return service.add_spare_part(
        maintenance_id,
        data
    )


# =========================================================
# SPARE PART HISTORY
# =========================================================

@router.get(
    "/{maintenance_id}/spare-parts",
    response_model=list[MaintenanceSparePartResponse]
)
def get_spare_parts(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaintenanceService(db)

    return service.repository.get_spare_parts(
        maintenance_id
    )


# =========================================================
# MAINTENANCE HISTORY
# =========================================================

@router.get(
    "/history/{machine_id}",
    response_model=list[MaintenanceResponse]
)
def get_machine_history(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaintenanceService(db)

    return service.get_history(
        machine_id
    )


# =========================================================
# GENERATE DUE ALERTS
# =========================================================

@router.post(
    "/alerts/generate",
    response_model=list[MaintenanceAlertResponse]
)
def generate_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Maintenance Engineer"
        )
    )
):

    service = MaintenanceService(db)

    return service.generate_due_alerts()


# =========================================================
# GET ALERTS
# =========================================================

@router.get(
    "/alerts",
    response_model=list[MaintenanceAlertResponse]
)
def get_alerts(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaintenanceService(db)

    return service.get_alerts(
        unread_only
    )


# =========================================================
# MARK ALERT READ
# =========================================================

@router.patch(
    "/alerts/{alert_id}/read",
    response_model=MaintenanceAlertResponse
)
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaintenanceService(db)

    return service.mark_alert_read(
        alert_id
    )