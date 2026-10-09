from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from models.user_model import User

from schemas.production_workflow_schema import (
    WorkflowActionRequest,
    WorkflowHistoryResponse
)

from services.production_workflow_service import (
    ProductionWorkflowService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/production-orders",
    tags=["Production Order Workflow"]
)


# =====================================================
# SUBMIT FOR SUPERVISOR REVIEW
# =====================================================

@router.post(
    "/{order_id}/submit-review"
)
def submit_review(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager"
        )
    )
):

    return ProductionWorkflowService.submit_for_review(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# SUPERVISOR APPROVE
# =====================================================

@router.post(
    "/{order_id}/supervisor-approve"
)
def supervisor_approve(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager",
            "Plant Manager"
        )
    )
):

    return ProductionWorkflowService.supervisor_approve(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# SUPERVISOR REJECT
# =====================================================

@router.post(
    "/{order_id}/supervisor-reject"
)
def supervisor_reject(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager",
            "Plant Manager"
        )
    )
):

    return ProductionWorkflowService.supervisor_reject(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# MATERIAL AVAILABILITY
# =====================================================

@router.post(
    "/{order_id}/check-material"
)
def check_material(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager",
            "Store Manager"
        )
    )
):

    return ProductionWorkflowService.check_material_availability(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# START PRODUCTION
# =====================================================

@router.post(
    "/{order_id}/start-production"
)
def start_production(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager",
            "Plant Manager"
        )
    )
):

    return ProductionWorkflowService.start_production(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# QUALITY APPROVAL
# =====================================================

@router.post(
    "/{order_id}/quality-approve"
)
def quality_approve(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Quality Manager"
        )
    )
):

    return ProductionWorkflowService.quality_approve(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# COMPLETE PRODUCTION
# =====================================================

@router.post(
    "/{order_id}/complete"
)
def complete_production(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager",
            "Plant Manager"
        )
    )
):

    return ProductionWorkflowService.complete_production(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# FINAL MANAGER APPROVAL
# =====================================================

@router.post(
    "/{order_id}/manager-approve"
)
def manager_approve(
    order_id: int,
    data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Production Manager"
        )
    )
):

    return ProductionWorkflowService.manager_approve(
        db=db,
        order_id=order_id,
        user=current_user,
        remarks=data.remarks
    )


# =====================================================
# WORKFLOW HISTORY
# =====================================================

@router.get(
    "/{order_id}/workflow-history",
    response_model=list[WorkflowHistoryResponse]
)
def workflow_history(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return ProductionWorkflowService.get_history(
        db=db,
        order_id=order_id
    )