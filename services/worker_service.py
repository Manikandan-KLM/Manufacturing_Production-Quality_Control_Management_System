from datetime import date, datetime
import math

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.worker_model import Worker
from models.production_line_model import ProductionLine
from models.production_batch_model import ProductionBatch

from models.worker_batch_assignment_model import (
    WorkerBatchAssignment
)

from repositories.worker_repository import (
    WorkerRepository
)


class WorkerService:

    ALLOWED_SHIFTS = {
        "Morning",
        "Afternoon",
        "Night",
        "General"
    }

    ALLOWED_STATUSES = {
        "Active",
        "Inactive",
        "On Leave",
        "Suspended",
        "Resigned"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = (
            WorkerRepository(db)
        )

    # =========================================
    # GET WORKER
    # =========================================

    def get_worker(
        self,
        worker_id: int
    ):

        worker = self.repository.get_by_id(
            worker_id
        )

        if not worker:

            raise HTTPException(
                status_code=404,
                detail="Worker not found"
            )

        return worker

    # =========================================
    # VALIDATE PRODUCTION LINE
    # =========================================

    def validate_production_line(
        self,
        production_line_id: int
    ):

        line = (
            self.db.query(ProductionLine)
            .filter(
                ProductionLine.id
                == production_line_id
            )
            .first()
        )

        if not line:

            raise HTTPException(
                status_code=404,
                detail="Production line not found"
            )

        if line.status in {
            "Inactive",
            "Temporarily Closed"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot assign worker to "
                    "inactive or closed production line"
                )
            )

        return line

    # =========================================
    # CREATE WORKER
    # =========================================

    def create_worker(
        self,
        data
    ):

        if data.shift not in self.ALLOWED_SHIFTS:

            raise HTTPException(
                status_code=400,
                detail="Invalid worker shift"
            )

        if data.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid worker status"
            )

        if data.joining_date:

            if data.joining_date > date.today():

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Joining date cannot be "
                        "in the future"
                    )
                )

        existing = (
            self.repository.get_by_employee_code(
                data.employee_code
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Employee code already exists"
            )

        if data.production_line_id:

            self.validate_production_line(
                data.production_line_id
            )

        worker = Worker(

            employee_code=data.employee_code,

            full_name=data.full_name,

            skill=data.skill,

            department=data.department,

            shift=data.shift,

            production_line_id=(
                data.production_line_id
            ),

            status=data.status,

            joining_date=data.joining_date
        )

        return self.repository.create(
            worker
        )

    # =========================================
    # LIST WORKERS
    # =========================================

    def get_workers(
        self,
        search=None,
        department=None,
        shift=None,
        status=None,
        production_line_id=None,
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

        if shift and shift not in self.ALLOWED_SHIFTS:

            raise HTTPException(
                status_code=400,
                detail="Invalid worker shift"
            )

        if status and status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid worker status"
            )

        items, total = (
            self.repository.get_list(

                search=search,

                department=department,

                shift=shift,

                status=status,

                production_line_id=(
                    production_line_id
                ),

                page=page,

                page_size=page_size
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # =========================================
    # UPDATE WORKER
    # =========================================

    def update_worker(
        self,
        worker_id: int,
        data
    ):

        worker = self.get_worker(
            worker_id
        )

        if worker.status == "Resigned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Resigned worker cannot be updated"
                )
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "shift" in update_data:

            if (
                update_data["shift"]
                not in self.ALLOWED_SHIFTS
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Invalid worker shift"
                )

        if "production_line_id" in update_data:

            if update_data["production_line_id"]:

                self.validate_production_line(
                    update_data["production_line_id"]
                )

        if "joining_date" in update_data:

            if (
                update_data["joining_date"]
                and update_data["joining_date"]
                > date.today()
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Joining date cannot be "
                        "in the future"
                    )
                )

        for field, value in update_data.items():

            setattr(
                worker,
                field,
                value
            )

        return self.repository.update(
            worker
        )

    # =========================================
    # UPDATE STATUS
    # =========================================

    def update_status(
        self,
        worker_id: int,
        new_status: str
    ):

        worker = self.get_worker(
            worker_id
        )

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid worker status"
            )

        if (
            worker.status == "Resigned"
            and new_status != "Resigned"
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Resigned worker cannot "
                    "be reactivated"
                )
            )

        worker.status = new_status

        return self.repository.update(
            worker
        )

    # =========================================
    # ASSIGN WORKER TO BATCH
    # =========================================

    def assign_worker_to_batch(
        self,
        worker_id: int,
        production_batch_id: int
    ):

        # -------------------------------------
        # Worker validation
        # -------------------------------------

        worker = self.get_worker(
            worker_id
        )

        if worker.status != "Active":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only active workers can "
                    "be assigned to production batches"
                )
            )

        # -------------------------------------
        # Batch validation
        # -------------------------------------

        batch = (
            self.db.query(ProductionBatch)
            .filter(
                ProductionBatch.id
                == production_batch_id
            )
            .first()
        )

        if not batch:

            raise HTTPException(
                status_code=404,
                detail="Production batch not found"
            )

        # -------------------------------------
        # Batch completed check
        # -------------------------------------

        if batch.end_time is not None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot assign worker to "
                    "completed batch"
                )
            )

        # -------------------------------------
        # Production line validation
        # -------------------------------------

        if worker.production_line_id is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Worker must be assigned to "
                    "a production line first"
                )
            )

        if (
            worker.production_line_id
            != batch.production_line_id
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Worker and production batch "
                    "must belong to the same "
                    "production line"
                )
            )

        # -------------------------------------
        # Existing assignment
        # -------------------------------------

        existing = (
            self.repository.get_active_assignment(
                worker_id,
                production_batch_id
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail=(
                    "Worker is already assigned "
                    "to this production batch"
                )
            )

        # -------------------------------------
        # Create assignment
        # -------------------------------------

        assignment = WorkerBatchAssignment(

            worker_id=worker_id,

            production_batch_id=(
                production_batch_id
            ),

            assigned_at=datetime.utcnow(),

            is_active=True
        )

        return self.repository.create_assignment(
            assignment
        )

    # =========================================
    # REMOVE WORKER FROM BATCH
    # =========================================

    def remove_worker_from_batch(
        self,
        worker_id: int,
        production_batch_id: int
    ):

        assignment = (
            self.repository.get_active_assignment(
                worker_id,
                production_batch_id
            )
        )

        if not assignment:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Active worker assignment "
                    "not found"
                )
            )

        assignment.is_active = False

        assignment.removed_at = (
            datetime.utcnow()
        )

        self.db.commit()

        self.db.refresh(
            assignment
        )

        return assignment

    # =========================================
    # WORKER ASSIGNMENT HISTORY
    # =========================================

    def get_worker_assignments(
        self,
        worker_id: int
    ):

        self.get_worker(
            worker_id
        )

        return (
            self.repository
            .get_worker_assignments(
                worker_id
            )
        )

    # =========================================
    # BATCH ASSIGNMENTS
    # =========================================

    def get_batch_assignments(
        self,
        production_batch_id: int
    ):

        batch = (
            self.db.query(ProductionBatch)
            .filter(
                ProductionBatch.id
                == production_batch_id
            )
            .first()
        )

        if not batch:

            raise HTTPException(
                status_code=404,
                detail="Production batch not found"
            )

        return (
            self.repository
            .get_batch_assignments(
                production_batch_id
            )
        )

    # =========================================
    # DELETE WORKER
    # =========================================

    def delete_worker(
        self,
        worker_id: int
    ):

        worker = self.get_worker(
            worker_id
        )

        if worker.status not in {
            "Inactive",
            "Resigned"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only inactive or resigned "
                    "workers can be deleted"
                )
            )

        self.repository.delete(
            worker
        )

        return {
            "message": (
                "Worker deleted successfully"
            )
        }