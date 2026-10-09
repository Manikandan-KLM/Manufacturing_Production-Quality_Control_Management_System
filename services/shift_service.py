from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.shift_model import Shift
from models.shift_worker_model import ShiftWorker
from models.shift_machine_usage_model import ShiftMachineUsage
from models.shift_production_output_model import ShiftProductionOutput

from models.plant_model import Plant
from models.worker_model import Worker
from models.machine_model import Machine
from models.production_batch_model import ProductionBatch

from repositories.shift_repository import ShiftRepository


class ShiftService:

    ALLOWED_SHIFT_TYPES = {
        "Morning",
        "Evening",
        "Night"
    }

    ALLOWED_STATUSES = {
        "Active",
        "Inactive"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = ShiftRepository(db)

    # =========================================
    # CREATE SHIFT
    # =========================================

    def create_shift(
        self,
        data
    ):

        if data.shift_type not in self.ALLOWED_SHIFT_TYPES:

            raise HTTPException(
                status_code=400,
                detail="Invalid shift type"
            )

        if data.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid shift status"
            )

        if data.start_time == data.end_time:

            raise HTTPException(
                status_code=400,
                detail="Start time and end time cannot be same"
            )

        plant = (
            self.db.query(Plant)
            .filter(Plant.id == data.plant_id)
            .first()
        )

        if not plant:

            raise HTTPException(
                status_code=404,
                detail="Plant not found"
            )

        existing = self.repository.get_by_code(
            data.shift_code
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Shift code already exists"
            )

        shift = Shift(
            shift_code=data.shift_code,
            shift_name=data.shift_name,
            start_time=data.start_time,
            end_time=data.end_time,
            shift_type=data.shift_type,
            status=data.status,
            plant_id=data.plant_id
        )

        return self.repository.create(shift)

    # =========================================
    # GET SHIFT
    # =========================================

    def get_shift(
        self,
        shift_id: int
    ):

        shift = self.repository.get_by_id(
            shift_id
        )

        if not shift:

            raise HTTPException(
                status_code=404,
                detail="Shift not found"
            )

        return shift

    # =========================================
    # LIST SHIFTS
    # =========================================

    def get_shifts(
        self,
        search=None,
        shift_type=None,
        status=None,
        plant_id=None,
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
                detail="Page size must be between 1 and 100"
            )

        if shift_type and shift_type not in self.ALLOWED_SHIFT_TYPES:

            raise HTTPException(
                status_code=400,
                detail="Invalid shift type"
            )

        if status and status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid shift status"
            )

        items, total = self.repository.get_list(
            search=search,
            shift_type=shift_type,
            status=status,
            plant_id=plant_id,
            page=page,
            page_size=page_size
        )

        total_pages = (
            (total + page_size - 1)
            // page_size
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # =========================================
    # UPDATE SHIFT
    # =========================================

    def update_shift(
        self,
        shift_id: int,
        data
    ):

        shift = self.get_shift(shift_id)

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "shift_type" in update_data:

            if update_data["shift_type"] not in self.ALLOWED_SHIFT_TYPES:

                raise HTTPException(
                    status_code=400,
                    detail="Invalid shift type"
                )

        if "plant_id" in update_data:

            plant = (
                self.db.query(Plant)
                .filter(
                    Plant.id == update_data["plant_id"]
                )
                .first()
            )

            if not plant:

                raise HTTPException(
                    status_code=404,
                    detail="Plant not found"
                )

        new_start = update_data.get(
            "start_time",
            shift.start_time
        )

        new_end = update_data.get(
            "end_time",
            shift.end_time
        )

        if new_start == new_end:

            raise HTTPException(
                status_code=400,
                detail="Start time and end time cannot be same"
            )

        for field, value in update_data.items():

            setattr(
                shift,
                field,
                value
            )

        return self.repository.update(
            shift
        )

    # =========================================
    # UPDATE STATUS
    # =========================================

    def update_status(
        self,
        shift_id: int,
        status: str
    ):

        shift = self.get_shift(shift_id)

        if status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid shift status"
            )

        shift.status = status

        return self.repository.update(
            shift
        )

    # =========================================
    # ASSIGN WORKER
    # =========================================

    def assign_worker(
        self,
        shift_id: int,
        worker_id: int,
        work_date
    ):

        shift = self.get_shift(shift_id)

        if shift.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Cannot assign workers to inactive shift"
            )

        worker = (
            self.db.query(Worker)
            .filter(Worker.id == worker_id)
            .first()
        )

        if not worker:

            raise HTTPException(
                status_code=404,
                detail="Worker not found"
            )

        if worker.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Only active workers can be assigned"
            )

        if worker.production_line_id is None:

            raise HTTPException(
                status_code=400,
                detail="Worker must have production line assignment"
            )

        existing = self.repository.get_worker_assignment(
            shift_id,
            worker_id,
            work_date
        )

        if existing and existing.is_active:

            raise HTTPException(
                status_code=409,
                detail="Worker already assigned to this shift"
            )

        assignment = ShiftWorker(
            shift_id=shift_id,
            worker_id=worker_id,
            work_date=work_date,
            assigned_at=datetime.utcnow(),
            is_active=True
        )

        return self.repository.create_worker_assignment(
            assignment
        )

    # =========================================
    # REMOVE WORKER
    # =========================================

    def remove_worker(
        self,
        shift_id: int,
        worker_id: int,
        work_date
    ):

        assignment = self.repository.get_worker_assignment(
            shift_id,
            worker_id,
            work_date
        )

        if not assignment:

            raise HTTPException(
                status_code=404,
                detail="Worker assignment not found"
            )

        if not assignment.is_active:

            raise HTTPException(
                status_code=400,
                detail="Worker is already removed"
            )

        assignment.is_active = False

        return self.repository.update_assignment(
            assignment
        )