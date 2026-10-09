import math

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.production_line_model import ProductionLine
from models.plant_model import Plant
from models.user_model import User

from repositories.production_line_repository import (
    ProductionLineRepository
)

from schemas.production_line_schema import (
    ProductionLineCreateRequest,
    ProductionLineUpdateRequest
)


class ProductionLineService:

    ALLOWED_STATUSES = {
        "Active",
        "Maintenance",
        "Inactive",
        "Temporarily Closed"
    }

    def __init__(self, db: Session):

        self.db = db

        self.repository = (
            ProductionLineRepository(db)
        )

    # ==================================================
    # VALIDATE PLANT
    # ==================================================

    def validate_plant(self, plant_id: int):

        plant = (
            self.db.query(Plant)
            .filter(Plant.id == plant_id)
            .first()
        )

        if not plant:

            raise HTTPException(
                status_code=404,
                detail="Plant not found"
            )

        if plant.status == "Inactive":

            raise HTTPException(
                status_code=400,
                detail="Cannot assign production line to inactive plant"
            )

        return plant

    # ==================================================
    # VALIDATE SUPERVISOR
    # ==================================================

    def validate_supervisor(
        self,
        supervisor_id: int
    ):

        supervisor = (
            self.db.query(User)
            .filter(User.id == supervisor_id)
            .first()
        )

        if not supervisor:

            raise HTTPException(
                status_code=404,
                detail="Supervisor not found"
            )

        if not supervisor.is_active:

            raise HTTPException(
                status_code=400,
                detail="Supervisor account is inactive"
            )

        return supervisor

    # ==================================================
    # CREATE
    # ==================================================

    def create_line(
        self,
        request: ProductionLineCreateRequest
    ):

        existing = (
            self.repository.get_by_code(
                request.line_code
            )
        )

        if existing:

            raise HTTPException(
                status_code=400,
                detail="Production line code already exists"
            )

        # Validate status
        if request.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid production line status"
            )

        # Validate plant
        self.validate_plant(
            request.plant_id
        )

        # Validate supervisor
        if request.supervisor_id is not None:

            self.validate_supervisor(
                request.supervisor_id
            )

        line = ProductionLine(

            line_code=request.line_code,

            line_name=request.line_name,

            production_capacity=(
                request.production_capacity
            ),

            capacity_unit=request.capacity_unit,

            plant_id=request.plant_id,

            status=request.status,

            supervisor_id=request.supervisor_id
        )

        return self.repository.create(line)

    # ==================================================
    # GET BY ID
    # ==================================================

    def get_line(self, line_id: int):

        line = (
            self.repository.get_by_id(
                line_id
            )
        )

        if not line:

            raise HTTPException(
                status_code=404,
                detail="Production line not found"
            )

        return line

    # ==================================================
    # GET LIST
    # ==================================================

    def get_lines(
        self,
        search: str | None,
        status: str | None,
        plant_id: int | None,
        page: int,
        page_size: int
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

        if status and status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid production line status"
            )

        items, total = (
            self.repository.get_list(
                search=search,
                status=status,
                plant_id=plant_id,
                page=page,
                page_size=page_size
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total > 0
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # ==================================================
    # UPDATE
    # ==================================================

    def update_line(
        self,
        line_id: int,
        request: ProductionLineUpdateRequest
    ):

        line = self.get_line(line_id)

        if request.status is not None:

            if request.status not in self.ALLOWED_STATUSES:

                raise HTTPException(
                    status_code=400,
                    detail="Invalid production line status"
                )

            line.status = request.status

        if request.line_name is not None:

            line.line_name = request.line_name

        if request.production_capacity is not None:

            line.production_capacity = (
                request.production_capacity
            )

        if request.capacity_unit is not None:

            line.capacity_unit = (
                request.capacity_unit
            )

        if request.plant_id is not None:

            self.validate_plant(
                request.plant_id
            )

            line.plant_id = request.plant_id

        if request.supervisor_id is not None:

            self.validate_supervisor(
                request.supervisor_id
            )

            line.supervisor_id = (
                request.supervisor_id
            )

        return self.repository.update(line)

    # ==================================================
    # DELETE
    # ==================================================

    def delete_line(self, line_id: int):

        line = self.get_line(line_id)

        self.repository.delete(line)

        return {
            "message": "Production line deleted successfully"
        }

    # ==================================================
    # STATUS
    # ==================================================

    def update_status(
        self,
        line_id: int,
        new_status: str
    ):

        line = self.get_line(line_id)

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid production line status"
            )

        line.status = new_status

        return self.repository.update(line)

    # ==================================================
    # SUPERVISOR
    # ==================================================

    def assign_supervisor(
        self,
        line_id: int,
        supervisor_id: int
    ):

        line = self.get_line(line_id)

        self.validate_supervisor(
            supervisor_id
        )

        line.supervisor_id = supervisor_id

        return self.repository.update(line)