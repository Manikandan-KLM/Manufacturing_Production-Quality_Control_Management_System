from datetime import date
import math

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.machine_model import Machine
from models.production_line_model import ProductionLine

from repositories.machine_repository import (
    MachineRepository
)


class MachineService:

    ALLOWED_STATUSES = {
        "Running",
        "Idle",
        "Maintenance",
        "Breakdown",
        "Decommissioned"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = MachineRepository(
            db
        )

    # =========================================
    # PRODUCTION LINE VALIDATION
    # =========================================

    def validate_production_line(
        self,
        production_line_id: int
    ):

        production_line = (
            self.db.query(
                ProductionLine
            )
            .filter(
                ProductionLine.id
                == production_line_id
            )
            .first()
        )

        if not production_line:

            raise HTTPException(
                status_code=404,
                detail="Production line not found"
            )

        if production_line.status in {
            "Inactive",
            "Temporarily Closed"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Machine cannot be assigned "
                    "to an inactive or closed production line"
                )
            )

        return production_line

    # =========================================
    # GET MACHINE
    # =========================================

    def get_machine(
        self,
        machine_id: int
    ):

        machine = (
            self.repository
            .get_by_id(machine_id)
        )

        if not machine:

            raise HTTPException(
                status_code=404,
                detail="Machine not found"
            )

        return machine

    # =========================================
    # CREATE MACHINE
    # =========================================

    def create_machine(
        self,
        data
    ):

        # Validate machine status

        if data.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid machine status"
            )

        # Validate installation date

        if data.installation_date > date.today():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Installation date cannot be "
                    "in the future"
                )
            )

        # Validate production line

        self.validate_production_line(
            data.production_line_id
        )

        # Duplicate machine code

        existing = (
            self.repository
            .get_by_code(
                data.machine_code
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Machine code already exists"
            )

        machine = Machine(
            machine_code=data.machine_code,
            machine_name=data.machine_name,
            machine_type=data.machine_type,
            production_line_id=(
                data.production_line_id
            ),
            installation_date=(
                data.installation_date
            ),
            status=data.status,
            operating_hours=(
                data.operating_hours
            )
        )

        return self.repository.create(
            machine
        )

    # =========================================
    # LIST
    # =========================================

    def get_machines(
        self,
        search=None,
        machine_type=None,
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
                    "Page size must be between "
                    "1 and 100"
                )
            )

        if status and status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid machine status"
            )

        items, total = (
            self.repository.get_list(
                search=search,
                machine_type=machine_type,
                status=status,
                production_line_id=(
                    production_line_id
                ),
                page=page,
                page_size=page_size
            )
        )

        total_pages = (
            math.ceil(
                total / page_size
            )
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
    # UPDATE
    # =========================================

    def update_machine(
        self,
        machine_id: int,
        data
    ):

        machine = self.get_machine(
            machine_id
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # Validate installation date

        if (
            "installation_date"
            in update_data
        ):

            if (
                update_data[
                    "installation_date"
                ]
                > date.today()
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Installation date "
                        "cannot be in the future"
                    )
                )

        for field, value in (
            update_data.items()
        ):

            setattr(
                machine,
                field,
                value
            )

        return self.repository.update(
            machine
        )

    # =========================================
    # DELETE
    # =========================================

    def delete_machine(
        self,
        machine_id: int
    ):

        machine = self.get_machine(
            machine_id
        )

        if machine.status != "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only decommissioned machines "
                    "can be deleted"
                )
            )

        self.repository.delete(
            machine
        )

        return {
            "message": (
                "Machine deleted successfully"
            )
        }

    # =========================================
    # STATUS UPDATE
    # =========================================

    def update_status(
        self,
        machine_id: int,
        new_status: str
    ):

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid machine status"
            )

        machine = self.get_machine(
            machine_id
        )

        # Decommissioned machine
        # cannot become active again

        if (
            machine.status
            == "Decommissioned"
            and new_status != "Decommissioned"
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Decommissioned machine "
                    "cannot be reactivated"
                )
            )

        machine.status = new_status

        return self.repository.update(
            machine
        )

    # =========================================
    # OPERATING HOURS
    # =========================================

    def update_operating_hours(
        self,
        machine_id: int,
        operating_hours: float
    ):

        machine = self.get_machine(
            machine_id
        )

        if machine.status == "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot update operating hours "
                    "of a decommissioned machine"
                )
            )

        if operating_hours < (
            machine.operating_hours
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Operating hours cannot be "
                    "lower than current value"
                )
            )

        machine.operating_hours = (
            operating_hours
        )

        return self.repository.update(
            machine
        )

    # =========================================
    # PRODUCTION LINE ASSIGNMENT
    # =========================================

    def update_production_line(
        self,
        machine_id: int,
        production_line_id: int
    ):

        machine = self.get_machine(
            machine_id
        )

        if machine.status == "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Decommissioned machine "
                    "cannot be reassigned"
                )
            )

        self.validate_production_line(
            production_line_id
        )

        machine.production_line_id = (
            production_line_id
        )

        return self.repository.update(
            machine
        )