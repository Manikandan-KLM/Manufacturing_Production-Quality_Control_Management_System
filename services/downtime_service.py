from datetime import datetime

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.downtime_model import Downtime
from models.machine_model import Machine
from models.production_line_model import ProductionLine
from models.user_model import User

from repositories.downtime_repository import (
    DowntimeRepository
)


class DowntimeService:

    ALLOWED_CATEGORIES = {
        "Machine Breakdown",
        "Material Shortage",
        "Quality Issue",
        "Power Failure",
        "Maintenance",
        "Operator Issue"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = DowntimeRepository(
            db
        )

    # =====================================================
    # MACHINE
    # =====================================================

    def get_machine(
        self,
        machine_id: int
    ):

        machine = (
            self.db.query(Machine)
            .filter(
                Machine.id == machine_id
            )
            .first()
        )

        if not machine:

            raise HTTPException(
                status_code=404,
                detail="Machine not found"
            )

        return machine

    # =====================================================
    # PRODUCTION LINE
    # =====================================================

    def get_production_line(
        self,
        production_line_id: int
    ):

        line = (
            self.db.query(
                ProductionLine
            )
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

        return line

    # =====================================================
    # RESPONSIBLE PERSON
    # =====================================================

    def get_responsible_person(
        self,
        user_id: int
    ):

        user = (
            self.db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="Responsible person not found"
            )

        if not user.is_active:

            raise HTTPException(
                status_code=400,
                detail="Responsible person is inactive"
            )

        return user

    # =====================================================
    # CREATE DOWNTIME
    # =====================================================

    def create_downtime(
        self,
        data
    ):

        # -----------------------------
        # Validate category
        # -----------------------------

        if data.category not in self.ALLOWED_CATEGORIES:

            raise HTTPException(
                status_code=400,
                detail="Invalid downtime category"
            )

        # -----------------------------
        # Machine
        # -----------------------------

        machine = self.get_machine(
            data.machine_id
        )

        # -----------------------------
        # Production line
        # -----------------------------

        line = self.get_production_line(
            data.production_line_id
        )

        # -----------------------------
        # Verify machine belongs to line
        # -----------------------------

        if (
            machine.production_line_id
            != data.production_line_id
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Machine does not belong "
                    "to the selected production line"
                )
            )

        # -----------------------------
        # Responsible person
        # -----------------------------

        self.get_responsible_person(
            data.responsible_person_id
        )

        # -----------------------------
        # Duplicate number
        # -----------------------------

        existing = (
            self.repository
            .get_by_number(
                data.downtime_number
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Downtime number already exists"
            )

        # -----------------------------
        # Future start time
        # -----------------------------

        if data.start_time > datetime.utcnow():

            raise HTTPException(
                status_code=400,
                detail="Start time cannot be in the future"
            )

        # -----------------------------
        # Create
        # -----------------------------

        downtime = Downtime(

            downtime_number=data.downtime_number,

            machine_id=data.machine_id,

            production_line_id=(
                data.production_line_id
            ),

            responsible_person_id=(
                data.responsible_person_id
            ),

            category=data.category,

            reason=data.reason,

            start_time=data.start_time,

            end_time=None,

            duration_minutes=0
        )

        # -----------------------------
        # Machine status
        # -----------------------------

        if data.category == "Machine Breakdown":

            machine.status = "Breakdown"

        elif data.category == "Maintenance":

            machine.status = "Maintenance"

        self.db.add(downtime)

        self.db.commit()

        self.db.refresh(downtime)

        return downtime

    # =====================================================
    # END DOWNTIME
    # =====================================================

    def end_downtime(
        self,
        downtime_id: int,
        end_time: datetime
    ):

        downtime = (
            self.repository
            .get_by_id(
                downtime_id
            )
        )

        if not downtime:

            raise HTTPException(
                status_code=404,
                detail="Downtime record not found"
            )

        # Already ended

        if downtime.end_time is not None:

            raise HTTPException(
                status_code=400,
                detail="Downtime has already been ended"
            )

        # End time validation

        if end_time < downtime.start_time:

            raise HTTPException(
                status_code=400,
                detail=(
                    "End time cannot be earlier "
                    "than start time"
                )
            )

        if end_time > datetime.utcnow():

            raise HTTPException(
                status_code=400,
                detail="End time cannot be in the future"
            )

        # Calculate duration

        duration = (
            end_time
            - downtime.start_time
        ).total_seconds() / 60

        downtime.end_time = end_time

        downtime.duration_minutes = round(
            duration,
            2
        )

        # Machine status

        machine = self.get_machine(
            downtime.machine_id
        )

        if downtime.category == "Machine Breakdown":

            machine.status = "Idle"

        elif downtime.category == "Maintenance":

            machine.status = "Idle"

        return self.repository.update(
            downtime
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update_downtime(
        self,
        downtime_id: int,
        data
    ):

        downtime = (
            self.repository
            .get_by_id(
                downtime_id
            )
        )

        if not downtime:

            raise HTTPException(
                status_code=404,
                detail="Downtime record not found"
            )

        if downtime.end_time is not None:

            raise HTTPException(
                status_code=400,
                detail="Completed downtime cannot be modified"
            )

        if data.category is not None:

            if (
                data.category
                not in self.ALLOWED_CATEGORIES
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Invalid downtime category"
                )

            downtime.category = data.category

        if data.reason is not None:

            downtime.reason = data.reason

        if data.responsible_person_id is not None:

            self.get_responsible_person(
                data.responsible_person_id
            )

            downtime.responsible_person_id = (
                data.responsible_person_id
            )

        return self.repository.update(
            downtime
        )

    # =====================================================
    # GET
    # =====================================================

    def get_downtime(
        self,
        downtime_id: int
    ):

        downtime = (
            self.repository
            .get_by_id(
                downtime_id
            )
        )

        if not downtime:

            raise HTTPException(
                status_code=404,
                detail="Downtime record not found"
            )

        return downtime

    # =====================================================
    # LIST
    # =====================================================

    def get_list(
        self,
        machine_id=None,
        production_line_id=None,
        category=None,
        page=1,
        page_size=10
    ):

        if page < 1:

            raise HTTPException(
                status_code=400,
                detail="Page must be at least 1"
            )

        if page_size < 1 or page_size > 100:

            raise HTTPException(
                status_code=400,
                detail="Page size must be between 1 and 100"
            )

        if category:

            if category not in self.ALLOWED_CATEGORIES:

                raise HTTPException(
                    status_code=400,
                    detail="Invalid downtime category"
                )

        items, total = (
            self.repository.get_list(
                machine_id=machine_id,
                production_line_id=production_line_id,
                category=category,
                page=page,
                page_size=page_size
            )
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

    # =====================================================
    # DOWNTIME PERCENTAGE
    # =====================================================

    def calculate_downtime_percentage(
        self,
        machine_id: int,
        total_period_minutes: float,
        start_date,
        end_date
    ):

        if total_period_minutes <= 0:

            raise HTTPException(
                status_code=400,
                detail="Total period must be greater than zero"
            )

        self.get_machine(
            machine_id
        )

        downtime_minutes = (
            self.repository
            .get_total_downtime_minutes(
                machine_id,
                start_date,
                end_date
            )
        )

        percentage = (
            downtime_minutes
            / total_period_minutes
        ) * 100

        return {
            "machine_id": machine_id,

            "total_period_minutes": (
                total_period_minutes
            ),

            "downtime_minutes": (
                round(
                    downtime_minutes,
                    2
                )
            ),

            "downtime_percentage": (
                round(
                    percentage,
                    2
                )
            )
        }