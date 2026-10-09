from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.production_order_model import ProductionOrder
from models.production_batch_model import ProductionBatch
from models.quality_inspection_model import QualityInspection
from models.user_model import User

from repositories.production_workflow_repository import (
    ProductionWorkflowRepository
)


class ProductionWorkflowService:

    # -----------------------------------------
    # VALID TRANSITIONS
    # -----------------------------------------

    VALID_TRANSITIONS = {
        "Draft": [
            "Pending Supervisor Review"
        ],

        "Pending Supervisor Review": [
            "Supervisor Approved",
            "Supervisor Rejected"
        ],

        "Supervisor Approved": [
            "Material Checked"
        ],

        "Material Checked": [
            "In Production"
        ],

        "In Production": [
            "Quality Approved"
        ],

        "Quality Approved": [
            "Completed"
        ],

        "Completed": [
            "Manager Approved"
        ],

        "Supervisor Rejected": [],
        "Manager Approved": []
    }

    # -----------------------------------------
    # COMMON TRANSITION VALIDATION
    # -----------------------------------------

    @staticmethod
    def validate_transition(
        order: ProductionOrder,
        target_status: str
    ):

        current_status = order.status

        allowed_statuses = (
            ProductionWorkflowService
            .VALID_TRANSITIONS
            .get(current_status, [])
        )

        if target_status not in allowed_statuses:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid workflow transition: "
                    f"{current_status} -> {target_status}"
                )
            )

    # -----------------------------------------
    # GET ORDER
    # -----------------------------------------

    @staticmethod
    def get_order(
        db: Session,
        order_id: int
    ):

        order = (
            db.query(ProductionOrder)
            .filter(
                ProductionOrder.id == order_id
            )
            .first()
        )

        if not order:

            raise HTTPException(
                status_code=404,
                detail="Production order not found"
            )

        return order

    # -----------------------------------------
    # UPDATE STATUS
    # -----------------------------------------

    @staticmethod
    def update_status(
        db: Session,
        order: ProductionOrder,
        target_status: str,
        action: str,
        user: User,
        remarks: str | None = None
    ):

        old_status = order.status

        ProductionWorkflowService.validate_transition(
            order,
            target_status
        )

        order.status = target_status

        ProductionWorkflowRepository.create(
            db=db,
            production_order_id=order.id,
            from_status=old_status,
            to_status=target_status,
            action=action,
            performed_by=user.id,
            remarks=remarks
        )

        db.commit()
        db.refresh(order)

        return order

    # -----------------------------------------
    # SUBMIT FOR SUPERVISOR REVIEW
    # -----------------------------------------

    @staticmethod
    def submit_for_review(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Pending Supervisor Review",
            action="Submitted for Supervisor Review",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # SUPERVISOR APPROVAL
    # -----------------------------------------

    @staticmethod
    def supervisor_approve(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        if user.role not in [
            "Production Manager",
            "Plant Manager"
        ]:

            raise HTTPException(
                status_code=403,
                detail="Only authorized manager can approve"
            )

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        order.supervisor_reviewed_by = user.id
        order.supervisor_reviewed_at = datetime.utcnow()

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Supervisor Approved",
            action="Supervisor Approved Production Order",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # SUPERVISOR REJECT
    # -----------------------------------------

    @staticmethod
    def supervisor_reject(
        db: Session,
        order_id: int,
        user: User,
        remarks: str
    ):

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        if order.status != "Pending Supervisor Review":

            raise HTTPException(
                status_code=400,
                detail="Order is not waiting for supervisor review"
            )

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Supervisor Rejected",
            action="Supervisor Rejected Production Order",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # MATERIAL CHECK
    # -----------------------------------------

    @staticmethod
    def check_material_availability(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        if order.status != "Supervisor Approved":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Material availability can be checked "
                    "only after supervisor approval"
                )
            )

        # ----------------------------------
        # BOM MATERIAL CHECK
        # ----------------------------------
        #
        # Here integrate Level 6 BOM + Level 5
        # Material management.
        #
        # Example:
        #
        # required_quantity <= available_quantity
        #
        # If any material is insufficient:
        # raise HTTPException(400, ...)
        #

        order.material_checked_by = user.id
        order.material_checked_at = datetime.utcnow()

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Material Checked",
            action="Material Availability Checked",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # START PRODUCTION
    # -----------------------------------------

    @staticmethod
    def start_production(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        if order.status != "Material Checked":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Production can start only after "
                    "material availability check"
                )
            )

        order.production_started_at = datetime.utcnow()

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="In Production",
            action="Production Started",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # QUALITY APPROVAL
    # -----------------------------------------

    @staticmethod
    def quality_approve(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        if order.status != "In Production":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Quality inspection can be completed "
                    "only when production is in progress"
                )
            )

        # ----------------------------------
        # QUALITY INSPECTION CHECK
        # ----------------------------------

        inspection = (
            db.query(QualityInspection)
            .filter(
                QualityInspection.production_batch_id.in_(
                    db.query(
                        ProductionBatch.id
                    ).filter(
                        ProductionBatch.production_order_id
                        == order.id
                    )
                )
            )
            .order_by(
                QualityInspection.inspection_date.desc()
            )
            .first()
        )

        if not inspection:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Quality inspection is required "
                    "before production approval"
                )
            )

        if inspection.overall_result != "Pass":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Production cannot proceed because "
                    "quality inspection has not passed"
                )
            )

        order.quality_approved_at = datetime.utcnow()

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Quality Approved",
            action="Quality Inspection Approved",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # COMPLETE PRODUCTION
    # -----------------------------------------

    @staticmethod
    def complete_production(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        if order.status != "Quality Approved":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Production can be completed only "
                    "after quality approval"
                )
            )

        order.completed_at = datetime.utcnow()

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Completed",
            action="Production Completed",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # MANAGER FINAL APPROVAL
    # -----------------------------------------

    @staticmethod
    def manager_approve(
        db: Session,
        order_id: int,
        user: User,
        remarks: str | None = None
    ):

        if user.role != "Production Manager":

            raise HTTPException(
                status_code=403,
                detail="Only Production Manager can give final approval"
            )

        order = ProductionWorkflowService.get_order(
            db,
            order_id
        )

        order.manager_approved_by = user.id
        order.manager_approved_at = datetime.utcnow()

        return ProductionWorkflowService.update_status(
            db=db,
            order=order,
            target_status="Manager Approved",
            action="Manager Final Approval",
            user=user,
            remarks=remarks
        )

    # -----------------------------------------
    # WORKFLOW HISTORY
    # -----------------------------------------

    @staticmethod
    def get_history(
        db: Session,
        order_id: int
    ):

        ProductionWorkflowService.get_order(
            db,
            order_id
        )

        return ProductionWorkflowRepository.get_by_order(
            db,
            order_id
        )