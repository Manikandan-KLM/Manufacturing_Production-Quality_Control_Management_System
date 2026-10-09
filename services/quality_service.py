from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.quality_inspection_model import (
    QualityInspection
)

from models.quality_parameter_model import (
    QualityParameter
)

from models.production_batch_model import (
    ProductionBatch
)

from models.user_model import User

from repositories.quality_repository import (
    QualityRepository
)


class QualityService:

    ALLOWED_INSPECTION_TYPES = {
        "Incoming Material Inspection",
        "In-Process Inspection",
        "Final Product Inspection"
    }

    ALLOWED_RESULTS = {
        "Pending",
        "Pass",
        "Fail"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = QualityRepository(
            db
        )

    # =========================================
    # CREATE INSPECTION
    # =========================================

    def create_inspection(
        self,
        data
    ):

        # Validate inspection type

        if (
            data.inspection_type
            not in self.ALLOWED_INSPECTION_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid inspection type"
            )

        # Duplicate inspection number

        existing = (
            self.repository.get_by_number(
                data.inspection_number
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Inspection number already exists"
            )

        # Validate batch

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

        # Validate inspector

        inspector = (
            self.db.query(User)
            .filter(
                User.id == data.inspector_id
            )
            .first()
        )

        if not inspector:

            raise HTTPException(
                status_code=404,
                detail="Inspector not found"
            )

        if not inspector.is_active:

            raise HTTPException(
                status_code=400,
                detail="Inspector account is inactive"
            )

        if inspector.role != "Quality Manager":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Inspector must have Quality Manager role"
                )
            )

        # Future date validation

        if data.inspection_date > date.today():

            raise HTTPException(
                status_code=400,
                detail="Inspection date cannot be in the future"
            )

        inspection = QualityInspection(
            inspection_number=data.inspection_number,
            inspection_type=data.inspection_type,
            production_batch_id=data.production_batch_id,
            inspector_id=data.inspector_id,
            inspection_date=data.inspection_date,
            overall_result="Pending",
            remarks=data.remarks
        )

        return (
            self.repository.create_inspection(
                inspection
            )
        )

    # =========================================
    # GET INSPECTION
    # =========================================

    def get_inspection(
        self,
        inspection_id: int
    ):

        inspection = (
            self.repository.get_inspection_by_id(
                inspection_id
            )
        )

        if not inspection:

            raise HTTPException(
                status_code=404,
                detail="Quality inspection not found"
            )

        return inspection

    # =========================================
    # LIST INSPECTIONS
    # =========================================

    def get_inspections(
        self,
        inspection_type=None,
        overall_result=None,
        production_batch_id=None,
        inspector_id=None,
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
            inspection_type
            and inspection_type
            not in self.ALLOWED_INSPECTION_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid inspection type"
            )

        if (
            overall_result
            and overall_result
            not in self.ALLOWED_RESULTS
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid inspection result"
            )

        items, total = (
            self.repository.get_inspection_list(
                inspection_type=inspection_type,
                overall_result=overall_result,
                production_batch_id=production_batch_id,
                inspector_id=inspector_id,
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
    # ADD PARAMETER
    # =========================================

    def add_parameter(
        self,
        inspection_id: int,
        data
    ):

        inspection = self.get_inspection(
            inspection_id
        )

        # Completed inspection cannot
        # receive new parameters

        if inspection.overall_result in {
            "Pass",
            "Fail"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot add parameter to completed inspection"
                )
            )

        # Calculate parameter result

        if data.actual_value == data.expected_value:

            result = "Pass"

        else:

            result = "Fail"

        parameter = QualityParameter(
            inspection_id=inspection_id,
            parameter_name=data.parameter_name,
            unit=data.unit,
            expected_value=data.expected_value,
            actual_value=data.actual_value,
            result=result,
            remarks=data.remarks
        )

        parameter = (
            self.repository.create_parameter(
                parameter
            )
        )

        self.update_overall_result(
            inspection_id
        )

        return parameter

    # =========================================
    # UPDATE PARAMETER
    # =========================================

    def update_parameter(
        self,
        parameter_id: int,
        data
    ):

        parameter = (
            self.repository.get_parameter_by_id(
                parameter_id
            )
        )

        if not parameter:

            raise HTTPException(
                status_code=404,
                detail="Quality parameter not found"
            )

        inspection = self.get_inspection(
            parameter.inspection_id
        )

        if inspection.overall_result in {
            "Pass",
            "Fail"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot modify parameter "
                    "after inspection completion"
                )
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            setattr(
                parameter,
                field,
                value
            )

        expected = parameter.expected_value
        actual = parameter.actual_value

        if actual == expected:

            parameter.result = "Pass"

        else:

            parameter.result = "Fail"

        parameter = (
            self.repository.update_parameter(
                parameter
            )
        )

        self.update_overall_result(
            parameter.inspection_id
        )

        return parameter

    # =========================================
    # UPDATE OVERALL RESULT
    # =========================================

    def update_overall_result(
        self,
        inspection_id: int
    ):

        inspection = self.get_inspection(
            inspection_id
        )

        parameters = (
            self.repository.get_parameters(
                inspection_id
            )
        )

        if not parameters:

            inspection.overall_result = "Pending"

        elif any(
            parameter.result == "Fail"
            for parameter in parameters
        ):

            inspection.overall_result = "Fail"

        elif all(
            parameter.result == "Pass"
            for parameter in parameters
        ):

            inspection.overall_result = "Pass"

        else:

            inspection.overall_result = "Pending"

        return (
            self.repository.update_inspection(
                inspection
            )
        )

    # =========================================
    # GET PARAMETERS
    # =========================================

    def get_parameters(
        self,
        inspection_id: int
    ):

        self.get_inspection(
            inspection_id
        )

        return (
            self.repository.get_parameters(
                inspection_id
            )
        )