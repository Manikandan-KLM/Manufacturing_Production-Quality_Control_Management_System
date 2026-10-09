from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.dashboard_schema import (
    ManufacturingDashboardResponse
)

from services.dashboard_service import (
    DashboardService
)

from utils.dependencies import (
    get_current_user
)

from models.user_model import User


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Manufacturing Dashboard"]
)


@router.get(
    "/summary",
    response_model=ManufacturingDashboardResponse
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return DashboardService.get_dashboard(db)