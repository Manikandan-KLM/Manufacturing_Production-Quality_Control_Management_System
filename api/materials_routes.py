from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.material_schema import (
    MaterialCreateRequest,
    MaterialUpdateRequest,
    MaterialStatusUpdateRequest,
    StockInRequest,
    StockOutRequest,
    MaterialAdjustmentRequest,
    MaterialResponse,
    MaterialListResponse,
    MaterialHistoryResponse
)

from services.material_service import (
    MaterialService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/materials",
    tags=["Materials"]
)


# =========================================
# CREATE MATERIAL
# =========================================

@router.post(
    "",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED
)
def create_material(
    data: MaterialCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = MaterialService(db)

    return service.create_material(
        data,
        current_user
    )


# =========================================
# GET MATERIALS
# =========================================

@router.get(
    "",
    response_model=MaterialListResponse
)
def get_materials(
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    unit: str | None = None,
    low_stock: bool = Query(
        default=False
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

    service = MaterialService(db)

    return service.get_materials(
        search=search,
        category=category,
        status=status,
        unit=unit,
        low_stock=low_stock,
        page=page,
        page_size=page_size
    )


# =========================================
# GET SINGLE MATERIAL
# =========================================

@router.get(
    "/{material_id}",
    response_model=MaterialResponse
)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaterialService(db)

    return service.get_material(
        material_id
    )


# =========================================
# UPDATE MATERIAL
# =========================================

@router.put(
    "/{material_id}",
    response_model=MaterialResponse
)
def update_material(
    material_id: int,
    data: MaterialUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = MaterialService(db)

    return service.update_material(
        material_id,
        data
    )


# =========================================
# DELETE MATERIAL
# =========================================

@router.delete(
    "/{material_id}"
)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = MaterialService(db)

    return service.delete_material(
        material_id
    )


# =========================================
# STATUS
# =========================================

@router.patch(
    "/{material_id}/status",
    response_model=MaterialResponse
)
def update_material_status(
    material_id: int,
    data: MaterialStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = MaterialService(db)

    return service.update_status(
        material_id,
        data.status
    )


# =========================================
# STOCK IN
# =========================================

@router.post(
    "/{material_id}/stock-in",
    response_model=MaterialResponse
)
def stock_in(
    material_id: int,
    data: StockInRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = MaterialService(db)

    return service.stock_in(
        material_id,
        data,
        current_user
    )


# =========================================
# STOCK OUT
# =========================================

@router.post(
    "/{material_id}/stock-out",
    response_model=MaterialResponse
)
def stock_out(
    material_id: int,
    data: StockOutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager",
            "Production Manager"
        )
    )
):

    service = MaterialService(db)

    return service.stock_out(
        material_id,
        data,
        current_user
    )


# =========================================
# STOCK ADJUSTMENT
# =========================================

@router.post(
    "/{material_id}/adjustment",
    response_model=MaterialResponse
)
def adjust_stock(
    material_id: int,
    data: MaterialAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = MaterialService(db)

    return service.adjust_stock(
        material_id,
        data,
        current_user
    )


# =========================================
# MATERIAL HISTORY
# =========================================

@router.get(
    "/{material_id}/history",
    response_model=list[MaterialHistoryResponse]
)
def get_material_history(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = MaterialService(db)

    return service.get_history(
        material_id
    )