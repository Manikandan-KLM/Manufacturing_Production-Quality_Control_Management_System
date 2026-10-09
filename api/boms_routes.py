from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.bom_schema import (
    BOMCreateRequest,
    BOMUpdateRequest,
    BOMStatusUpdateRequest,
    BOMItemCreateRequest,
    BOMItemUpdateRequest,
    BOMResponse,
    BOMDetailResponse,
    BOMListResponse,
    BOMItemResponse
)

from services.bom_service import (
    BOMService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/boms",
    tags=["Bill of Materials"]
)


# =========================================
# CREATE BOM
# =========================================

@router.post(
    "",
    response_model=BOMResponse,
    status_code=status.HTTP_201_CREATED
)
def create_bom(
    data: BOMCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = BOMService(db)

    return service.create_bom(
        data
    )


# =========================================
# LIST BOM
# =========================================

@router.get(
    "",
    response_model=BOMListResponse
)
def get_boms(
    product_id: int | None = None,
    bom_status: str | None = Query(
        default=None,
        alias="status"
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = BOMService(db)

    return service.get_boms(
        product_id=product_id,
        status=bom_status,
        page=page,
        page_size=page_size
    )


# =========================================
# GET BOM
# =========================================

@router.get(
    "/{bom_id}",
    response_model=BOMDetailResponse
)
def get_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = BOMService(db)

    return service.get_bom_details(
        bom_id
    )


# =========================================
# UPDATE BOM
# =========================================

@router.put(
    "/{bom_id}",
    response_model=BOMResponse
)
def update_bom(
    bom_id: int,
    data: BOMUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = BOMService(db)

    return service.update_bom(
        bom_id,
        data
    )


# =========================================
# DELETE BOM
# =========================================

@router.delete(
    "/{bom_id}"
)
def delete_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = BOMService(db)

    return service.delete_bom(
        bom_id
    )


# =========================================
# BOM STATUS
# =========================================

@router.patch(
    "/{bom_id}/status",
    response_model=BOMResponse
)
def update_bom_status(
    bom_id: int,
    data: BOMStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = BOMService(db)

    return service.update_status(
        bom_id,
        data.status
    )


# =========================================
# ADD MATERIAL
# =========================================

@router.post(
    "/{bom_id}/materials",
    response_model=BOMItemResponse,
    status_code=status.HTTP_201_CREATED
)
def add_material(
    bom_id: int,
    data: BOMItemCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = BOMService(db)

    return service.add_material(
        bom_id,
        data
    )


# =========================================
# UPDATE MATERIAL
# =========================================

@router.put(
    "/{bom_id}/materials/{material_id}",
    response_model=BOMItemResponse
)
def update_material(
    bom_id: int,
    material_id: int,
    data: BOMItemUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = BOMService(db)

    return service.update_material(
        bom_id,
        material_id,
        data
    )


# =========================================
# REMOVE MATERIAL
# =========================================

@router.delete(
    "/{bom_id}/materials/{material_id}"
)
def remove_material(
    bom_id: int,
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = BOMService(db)

    return service.remove_material(
        bom_id,
        material_id
    )


# =========================================
# GET MATERIALS
# =========================================

@router.get(
    "/{bom_id}/materials",
    response_model=list[BOMItemResponse]
)
def get_materials(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = BOMService(db)

    return service.get_materials(
        bom_id
    )