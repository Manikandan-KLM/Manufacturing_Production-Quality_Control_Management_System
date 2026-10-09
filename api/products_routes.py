from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from models.user_model import User

from fastapi import Query

from sqlalchemy import func, select

from models.product_model import Product

from schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
    ProductStatusUpdateRequest
)

from services.product_service import (
    ProductService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)


# ==================================================
# CREATE
# ==================================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    request: ProductCreateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = ProductService(db)

    return service.create_product(
        request
    )


# ==================================================
# LIST
# SEARCH + FILTER
# ==================================================

@router.get(
    "",
    response_model=ProductListResponse
)
def get_products(
    search: str | None = Query(
        default=None
    ),

    category: str | None = Query(
        default=None
    ),

    status: str | None = Query(
        default=None
    ),

    unit: str | None = Query(
        default=None
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

    current_user: User = Depends(
        get_current_user
    )
):

    service = ProductService(db)

    return service.get_products(
        search=search,
        category=category,
        status=status,
        unit=unit,
        page=page,
        page_size=page_size
    )


# ==================================================
# GET DETAILS
# ==================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    service = ProductService(db)

    return service.get_product(
        product_id
    )


# ==================================================
# UPDATE
# ==================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,

    request: ProductUpdateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = ProductService(db)

    return service.update_product(
        product_id,
        request
    )


# ==================================================
# DELETE
# ==================================================

@router.delete(
    "/{product_id}"
)
def delete_product(
    product_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin"
        )
    )
):

    service = ProductService(db)

    return service.delete_product(
        product_id
    )


# ==================================================
# STATUS
# ==================================================

@router.patch(
    "/{product_id}/status",
    response_model=ProductResponse
)
def update_product_status(
    product_id: int,

    request: ProductStatusUpdateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Production Manager"
        )
    )
):

    service = ProductService(db)

    return service.update_status(
        product_id,
        request.status
    )



@router.get("/")
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.scalar(
        select(func.count()).select_from(Product)
    ) or 0

    items = db.scalars(
        select(Product)
        .order_by(Product.id)
        .offset(skip)
        .limit(limit)
    ).all()

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }