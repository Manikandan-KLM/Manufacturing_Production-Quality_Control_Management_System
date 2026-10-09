from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from db.database import get_db

from models.user_model import User

from schemas.report_schema import (
    ReportFilters
)

from services.report_service import (
    ReportService
)

from utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Advanced Reports"]
)


# =====================================================
# DAILY PRODUCTION
# =====================================================

@router.get("/daily-production")
def daily_production_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.daily_production(
        db,
        filters
    )


# =====================================================
# MONTHLY PRODUCTION
# =====================================================

@router.get("/monthly-production")
def monthly_production_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.monthly_production(
        db,
        filters
    )


# =====================================================
# MACHINE PERFORMANCE
# =====================================================

@router.get("/machine-performance")
def machine_performance_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.machine_performance(
        db,
        filters
    )


# =====================================================
# PRODUCT PRODUCTION
# =====================================================

@router.get("/product-production")
def product_production_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.product_production(
        db,
        filters
    )


# =====================================================
# QUALITY
# =====================================================

@router.get("/quality")
def quality_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.quality(
        db,
        filters
    )


# =====================================================
# DEFECT ANALYSIS
# =====================================================

@router.get("/defects")
def defect_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.defects(
        db,
        filters
    )


# =====================================================
# MATERIAL CONSUMPTION
# =====================================================

@router.get("/material-consumption")
def material_consumption_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.materials(
        db,
        filters
    )


# =====================================================
# WORKER PERFORMANCE
# =====================================================

@router.get("/worker-performance")
def worker_performance_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.workers(
        db,
        filters
    )


# =====================================================
# SHIFT PERFORMANCE
# =====================================================

@router.get("/shift-performance")
def shift_performance_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.shifts(
        db,
        filters
    )


# =====================================================
# DOWNTIME
# =====================================================

@router.get("/downtime")
def downtime_report(
    filters: ReportFilters = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ReportService.downtime(
        db,
        filters
    )