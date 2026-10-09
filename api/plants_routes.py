from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from models.user_model import User

from schemas.plant_schema import (
    PlantCreateRequest,
    PlantUpdateRequest,
    PlantStatusUpdateRequest,
    PlantCapacityUpdateRequest,
    PlantManagerUpdateRequest,
    PlantResponse
)

from services.plant_service import PlantService

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/plants",
    tags=["Plants"]
)


# ==================================================
# CREATE PLANT
# ==================================================

@router.post(
    "",
    response_model=PlantResponse,
    status_code=status.HTTP_201_CREATED
)
def create_plant(
    request: PlantCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Super Admin")
    )
):

    service = PlantService(db)

    return service.create_plant(request)


# ==================================================
# GET ALL PLANTS
# ==================================================

@router.get(
    "",
    response_model=list[PlantResponse]
)
def get_all_plants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = PlantService(db)

    return service.get_all_plants()


# ==================================================
# GET PLANT DETAILS
# ==================================================

@router.get(
    "/{plant_id}",
    response_model=PlantResponse
)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = PlantService(db)

    return service.get_plant(plant_id)


# ==================================================
# UPDATE PLANT
# ==================================================

@router.put(
    "/{plant_id}",
    response_model=PlantResponse
)
def update_plant(
    plant_id: int,
    request: PlantUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Super Admin")
    )
):

    service = PlantService(db)

    return service.update_plant(
        plant_id,
        request
    )


# ==================================================
# UPDATE STATUS
# ==================================================

@router.patch(
    "/{plant_id}/status",
    response_model=PlantResponse
)
def update_status(
    plant_id: int,
    request: PlantStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Super Admin")
    )
):

    service = PlantService(db)

    return service.update_status(
        plant_id,
        request.status
    )


# ==================================================
# UPDATE CAPACITY
# ==================================================

@router.patch(
    "/{plant_id}/capacity",
    response_model=PlantResponse
)
def update_capacity(
    plant_id: int,
    request: PlantCapacityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager"
        )
    )
):

    service = PlantService(db)

    return service.update_capacity(
        plant_id,
        request.production_capacity,
        request.capacity_unit
    )


# ==================================================
# ASSIGN MANAGER
# ==================================================

@router.patch(
    "/{plant_id}/manager",
    response_model=PlantResponse
)
def assign_manager(
    plant_id: int,
    request: PlantManagerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Super Admin")
    )
):

    service = PlantService(db)

    return service.assign_manager(
        plant_id,
        request.manager_id
    )