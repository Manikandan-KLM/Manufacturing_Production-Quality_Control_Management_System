from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.defect_model import Defect
from models.production_batch_model import ProductionBatch
from models.product_model import Product
from models.quality_inspection_model import QualityInspection
from models.user_model import User

from repositories.defect_repository import (
    DefectRepository
)


class DefectService:

    ALLOWED_SEVERITIES = {
        "Minor",
        "Major",
        "Critical"
    }

    ALLOWED_STATUSES = {
        "Open",
        "In Progress",
        "Resolved",
        "Closed"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = DefectRepository(
            db
        )

    # =========================================
    # CREATE DEFECT
    # =========================================

    def create_defect(
        self,
        data,
        reported_by: int
    ):

        # -------------------------------------
        # Validate severity
        # -------------------------------------

        if data.severity not in self.ALLOWED_SEVERITIES:

            raise HTTPException(
                status_code=400,
                detail="Invalid defect severity"
            )

        # -------------------------------------
        # Duplicate defect number
        # -------------------------------------

        existing = (
            self.repository.get_by_number(
                data.defect_number
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Defect number already exists"
            )

        # -------------------------------------
        # Validate production batch
        # -------------------------------------

        batch = (
            self.db.query(ProductionBatch)
            .filter(
                ProductionBatch.id
                == data.production_batch_id
            )
            .first()
        )

        if not batch:

            raise HTTPException(
                status_code=404,
                detail="Production batch not found"
            )

        # -------------------------------------
        # Validate product
        # -------------------------------------

        product = (
            self.db.query(Product)
            .filter(
                Product.id == data.product_id
            )
            .first()
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # Product should be active/discontinued
        # check according to your business rules

        if product.status == "Inactive":

            raise HTTPException(
                status_code=400,
                detail="Cannot create defect for inactive product"
            )

        # -------------------------------------
        # Validate quantity
        # -------------------------------------

        if data.quantity_affected <= 0:

            raise HTTPException(
                status_code=400,
                detail="Affected quantity must be greater than 0"
            )

        # -------------------------------------
        # Validate batch quantity
        # -------------------------------------

        batch_total = (
            batch.produced_quantity
            + batch.rejected_quantity
        )

        if data.quantity_affected > batch_total:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Affected quantity cannot exceed "
                    "batch output quantity"
                )
            )

        # -------------------------------------
        # Validate inspection
        # -------------------------------------

        if data.quality_inspection_id:

            inspection = (
                self.db.query(QualityInspection)
                .filter(
                    QualityInspection.id
                    == data.quality_inspection_id
                )
                .first()
            )

            if not inspection:

                raise HTTPException(
                    status_code=404,
                    detail="Quality inspection not found"
                )

            if (
                inspection.production_batch_id
                != data.production_batch_id
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Inspection does not belong "
                        "to the selected production batch"
                    )
                )

            if inspection.overall_result != "Fail":

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Defect can only be created "
                        "from a failed quality inspection"
                    )
                )

        # -------------------------------------
        # Validate reporter
        # -------------------------------------

        reporter = (
            self.db.query(User)
            .filter(
                User.id == reported_by
            )
            .first()
        )

        if not reporter:

            raise HTTPException(
                status_code=404,
                detail="Reporting user not found"
            )

        defect = Defect(
            defect_number=data.defect_number,
            defect_type=data.defect_type,
            severity=data.severity,
            production_batch_id=data.production_batch_id,
            product_id=data.product_id,
            quality_inspection_id=data.quality_inspection_id,
            quantity_affected=data.quantity_affected,
            root_cause=data.root_cause,
            corrective_action=data.corrective_action,
            resolution_status="Open",
            reported_by=reported_by
        )

        return self.repository.create(
            defect
        )

    # =========================================
    # GET DEFECT
    # =========================================

    def get_defect(
        self,
        defect_id: int
    ):

        defect = (
            self.repository.get_by_id(
                defect_id
            )
        )

        if not defect:

            raise HTTPException(
                status_code=404,
                detail="Defect not found"
            )

        return defect

    # =========================================
    # LIST DEFECTS
    # =========================================

    def get_defects(
        self,
        search=None,
        defect_type=None,
        severity=None,
        resolution_status=None,
        production_batch_id=None,
        product_id=None,
        page=1,
        page_size=10
    ):

        if page < 1:

            raise HTTPException(
                status_code=400,
                detail="Page must be greater than 0"
            )

        if page_size < 1 or page_size > 100:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Page size must be between 1 and 100"
                )
            )

        if (
            severity
            and severity not in self.ALLOWED_SEVERITIES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid defect severity"
            )

        if (
            resolution_status
            and resolution_status
            not in self.ALLOWED_STATUSES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid resolution status"
            )

        items, total = (
            self.repository.get_list(
                search=search,
                defect_type=defect_type,
                severity=severity,
                resolution_status=resolution_status,
                production_batch_id=production_batch_id,
                product_id=product_id,
                page=page,
                page_size=page_size
            )
        )

        total_pages = (
            total + page_size - 1
        ) // page_size

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # =========================================
    # UPDATE DEFECT
    # =========================================

    def update_defect(
        self,
        defect_id: int,
        data
    ):

        defect = self.get_defect(
            defect_id
        )

        if defect.resolution_status == "Closed":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Closed defect cannot be modified"
                )
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "severity" in update_data:

            if (
                update_data["severity"]
                not in self.ALLOWED_SEVERITIES
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Invalid defect severity"
                )

        if (
            "quantity_affected"
            in update_data
        ):

            if (
                update_data["quantity_affected"]
                <= 0
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Affected quantity must be "
                        "greater than 0"
                    )
                )

        for field, value in update_data.items():

            setattr(
                defect,
                field,
                value
            )

        return self.repository.update(
            defect
        )

    # =========================================
    # UPDATE STATUS
    # =========================================

    def update_status(
        self,
        defect_id: int,
        resolution_status: str,
        user_id: int
    ):

        defect = self.get_defect(
            defect_id
        )

        if (
            resolution_status
            not in self.ALLOWED_STATUSES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid resolution status"
            )

        current_status = (
            defect.resolution_status
        )

        # -------------------------------------
        # Status transition rules
        # -------------------------------------

        allowed_transitions = {

            "Open": {
                "In Progress"
            },

            "In Progress": {
                "Resolved"
            },

            "Resolved": {
                "Closed",
                "In Progress"
            },

            "Closed": set()
        }

        if (
            resolution_status
            not in allowed_transitions[
                current_status
            ]
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status transition: "
                    f"{current_status} -> "
                    f"{resolution_status}"
                )
            )

        defect.resolution_status = (
            resolution_status
        )

        if resolution_status in {
            "Resolved",
            "Closed"
        }:

            defect.resolved_by = user_id

            defect.resolved_at = (
                datetime.utcnow()
            )

        return self.repository.update(
            defect
        )