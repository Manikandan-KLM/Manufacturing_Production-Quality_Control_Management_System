from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.inventory_schema import (
    RawMaterialReceiptRequest,
    MaterialConsumptionRequest,
    FinishedGoodsProductionRequest,
    RejectedGoodsRequest,
    StockAdjustmentRequest,
    InventoryMovementResponse,
    InventoryMovementListResponse
)

from services.inventory_service import (
    InventoryService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory Management"]
)


# =========================================================
# RAW MATERIAL RECEIPT
# =========================================================

@router.post(
    "/receipts",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def receive_material(
    data: RawMaterialReceiptRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = InventoryService(db)

    return service.receive_material(
        data,
        current_user.id
    )


# =========================================================
# MATERIAL CONSUMPTION
# =========================================================

@router.post(
    "/consumption",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def consume_material(
    data: MaterialConsumptionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager",
            "Production Manager"
        )
    )
):

    service = InventoryService(db)

    return service.consume_material(
        data,
        current_user.id
    )


# =========================================================
# FINISHED GOODS
# =========================================================

@router.post(
    "/finished-goods",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def finished_goods(
    data: FinishedGoodsProductionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager",
            "Store Manager"
        )
    )
):

    service = InventoryService(db)

    return service.record_finished_goods(
        data,
        current_user.id
    )


# =========================================================
# REJECTED GOODS
# =========================================================

@router.post(
    "/rejected-goods",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def rejected_goods(
    data: RejectedGoodsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager",
            "Quality Manager"
        )
    )
):

    service = InventoryService(db)

    return service.record_rejected_goods(
        data,
        current_user.id
    )


# =========================================================
# STOCK ADJUSTMENT
# =========================================================

@router.post(
    "/adjustment",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def stock_adjustment(
    data: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Store Manager"
        )
    )
):

    service = InventoryService(db)

    return service.adjust_stock(
        data,
        current_user.id
    )


# =========================================================
# TRANSACTION HISTORY
# =========================================================

@router.get(
    "",
    response_model=InventoryMovementListResponse
)
def inventory_history(
    movement_type: str | None = None,

    material_id: int | None = Query(
        default=None,
        gt=0
    ),

    product_id: int | None = Query(
        default=None,
        gt=0
    ),

    production_batch_id: int | None = Query(
        default=None,
        gt=0
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

    current_user=Depends(
        get_current_user
    )
):

    service = InventoryService(db)

    return service.get_history(
        movement_type=movement_type,
        material_id=material_id,
        product_id=product_id,
        production_batch_id=production_batch_id,
        page=page,
        page_size=page_size
    )


# =========================================================
# GET TRANSACTION
# =========================================================

@router.get(
    "/transaction/{movement_id}",
    response_model=InventoryMovementResponse
)
def get_transaction(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    service = InventoryService(db)

    return service.get_transaction(
        movement_id
    )