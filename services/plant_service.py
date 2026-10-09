from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.plant_model import Plant
from models.user_model import User

from repositories.plant_repository import PlantRepository

from schemas.plant_schema import (
    PlantCreateRequest,
    PlantUpdateRequest
)


class PlantService:

    ALLOWED_STATUSES = {
        "Active",
        "Maintenance",
        "Temporarily Closed",
        "Inactive"
    }

    def __init__(self, db: Session):

        self.db = db
        self.repository = PlantRepository(db)

    # -----------------------------------------
    # CREATE PLANT
    # -----------------------------------------

    def create_plant(
        self,
        request: PlantCreateRequest
    ):

        existing_plant = self.repository.get_by_code(
            request.plant_code
        )

        if existing_plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plant code already exists"
            )

        if request.status not in self.ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plant status"
            )

        if request.manager_id is not None:

            manager = (
                self.db.query(User)
                .filter(User.id == request.manager_id)
                .first()
            )

            if not manager:
                raise HTTPException(
                    status_code=404,
                    detail="Manager not found"
                )

            if manager.role != "Plant Manager":
                raise HTTPException(
                    status_code=400,
                    detail="Selected user is not a Plant Manager"
                )

            if not manager.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Plant Manager account is inactive"
                )

        plant = Plant(
            plant_code=request.plant_code,
            plant_name=request.plant_name,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            production_capacity=request.production_capacity,
            capacity_unit=request.capacity_unit,
            status=request.status,
            manager_id=request.manager_id
        )

        return self.repository.create(plant)

    # -----------------------------------------
    # GET ALL PLANTS
    # -----------------------------------------

    def get_all_plants(self):

        return self.repository.get_all()

    # -----------------------------------------
    # GET PLANT
    # -----------------------------------------

    def get_plant(self, plant_id: int):

        plant = self.repository.get_by_id(plant_id)

        if not plant:
            raise HTTPException(
                status_code=404,
                detail="Plant not found"
            )

        return plant

    # -----------------------------------------
    # UPDATE PLANT
    # -----------------------------------------

    def update_plant(
        self,
        plant_id: int,
        request: PlantUpdateRequest
    ):

        plant = self.get_plant(plant_id)

        if request.status is not None:

            if request.status not in self.ALLOWED_STATUSES:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid plant status"
                )

            plant.status = request.status

        if request.plant_name is not None:
            plant.plant_name = request.plant_name

        if request.address is not None:
            plant.address = request.address

        if request.city is not None:
            plant.city = request.city

        if request.state is not None:
            plant.state = request.state

        if request.country is not None:
            plant.country = request.country

        if request.production_capacity is not None:
            plant.production_capacity = request.production_capacity

        if request.capacity_unit is not None:
            plant.capacity_unit = request.capacity_unit

        if request.manager_id is not None:

            manager = (
                self.db.query(User)
                .filter(User.id == request.manager_id)
                .first()
            )

            if not manager:
                raise HTTPException(
                    status_code=404,
                    detail="Manager not found"
                )

            if manager.role != "Plant Manager":
                raise HTTPException(
                    status_code=400,
                    detail="Selected user is not a Plant Manager"
                )

            if not manager.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Plant Manager account is inactive"
                )

            plant.manager_id = request.manager_id

        return self.repository.update(plant)

    # -----------------------------------------
    # UPDATE STATUS
    # -----------------------------------------

    def update_status(
        self,
        plant_id: int,
        new_status: str
    ):

        plant = self.get_plant(plant_id)

        if new_status not in self.ALLOWED_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid plant status"
            )

        plant.status = new_status

        return self.repository.update(plant)

    # -----------------------------------------
    # UPDATE CAPACITY
    # -----------------------------------------

    def update_capacity(
        self,
        plant_id: int,
        production_capacity: float,
        capacity_unit: str
    ):

        plant = self.get_plant(plant_id)

        if production_capacity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Production capacity must be greater than zero"
            )

        plant.production_capacity = production_capacity
        plant.capacity_unit = capacity_unit

        return self.repository.update(plant)

    # -----------------------------------------
    # ASSIGN MANAGER
    # -----------------------------------------

    def assign_manager(
        self,
        plant_id: int,
        manager_id: int
    ):

        plant = self.get_plant(plant_id)

        manager = (
            self.db.query(User)
            .filter(User.id == manager_id)
            .first()
        )

        if not manager:
            raise HTTPException(
                status_code=404,
                detail="Manager not found"
            )

        if manager.role != "Plant Manager":
            raise HTTPException(
                status_code=400,
                detail="Selected user is not a Plant Manager"
            )

        if not manager.is_active:
            raise HTTPException(
                status_code=400,
                detail="Plant Manager account is inactive"
            )

        plant.manager_id = manager_id

        return self.repository.update(plant)