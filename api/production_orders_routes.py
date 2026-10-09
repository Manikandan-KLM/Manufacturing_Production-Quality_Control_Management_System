from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.production_order_schema import (
    ProductionOrderCreateRequest,
    ProductionOrderUpdateRequest,
    ProductionOrderStatusUpdateRequest,
    ProductionOrderResponse,
    ProductionOrderListResponse
)

from services.production_order_service import (
    ProductionOrderService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/production-orders",
    tags=["Production Orders"]
)


# =================================================
# CREATE
# =================================================

@router.post(
    "",
    response_model=ProductionOrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_production_order(
    data: ProductionOrderCreateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = ProductionOrderService(db)

    return service.create_order(data)


# =================================================
# LIST
# =================================================

@router.get(
    "",
    response_model=ProductionOrderListResponse
)
def get_production_orders(

    search: str | None = None,

    order_status: str | None = Query(
        default=None,
        alias="status"
    ),

    priority: str | None = None,

    product_id: int | None = None,

    production_line_id: int | None = None,

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

    service = ProductionOrderService(db)

    return service.get_orders(

        search=search,

        status=order_status,

        priority=priority,

        product_id=product_id,

        production_line_id=production_line_id,

        page=page,

        page_size=page_size
    )


# =================================================
# GET ONE
# =================================================

@router.get(
    "/{order_id}",
    response_model=ProductionOrderResponse
)
def get_production_order(

    order_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    )
):

    service = ProductionOrderService(db)

    return service.get_order(order_id)


# =================================================
# UPDATE
# =================================================

@router.put(
    "/{order_id}",
    response_model=ProductionOrderResponse
)
def update_production_order(

    order_id: int,

    data: ProductionOrderUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
            "Production Manager"
        )
    )
):

    service = ProductionOrderService(db)

    return service.update_order(
        order_id,
        data
    )


# =================================================
# STATUS UPDATE
# =================================================

@router.patch(
    "/{order_id}/status",
    response_model=ProductionOrderResponse
)
def update_production_order_status(

    order_id: int,

    data: ProductionOrderStatusUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = ProductionOrderService(db)

    return service.update_status(
        order_id,
        data.status
    )


# =================================================
# DELETE
# =================================================

@router.delete(
    "/{order_id}"
)
def delete_production_order(

    order_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = ProductionOrderService(db)

    return service.delete_order(
        order_id
    )