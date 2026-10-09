import math

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.product_model import Product

from repositories.product_repository import (
    ProductRepository
)

from schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest
)


class ProductService:

    ALLOWED_STATUSES = {
        "Active",
        "Inactive",
        "Discontinued"
    }

    def __init__(self, db: Session):

        self.db = db

        self.repository = ProductRepository(db)

    # =========================================
    # CREATE PRODUCT
    # =========================================

    def create_product(
        self,
        request: ProductCreateRequest
    ):

        # Product code duplicate check

        existing_product = (
            self.repository.get_by_product_code(
                request.product_code
            )
        )

        if existing_product:

            raise HTTPException(
                status_code=400,
                detail="Product code already exists"
            )

        # SKU duplicate check

        existing_sku = (
            self.repository.get_by_sku(
                request.sku
            )
        )

        if existing_sku:

            raise HTTPException(
                status_code=400,
                detail="SKU already exists"
            )

        # Status validation

        if request.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid product status"
            )

        product = Product(

            product_code=request.product_code,

            product_name=request.product_name,

            category=request.category,

            sku=request.sku,

            unit_of_measurement=(
                request.unit_of_measurement
            ),

            status=request.status,

            standard_production_time=(
                request.standard_production_time
            ),

            production_time_unit=(
                request.production_time_unit
            ),

            description=request.description
        )

        return self.repository.create(product)

    # =========================================
    # GET PRODUCT
    # =========================================

    def get_product(
        self,
        product_id: int
    ):

        product = (
            self.repository.get_by_id(
                product_id
            )
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return product

    # =========================================
    # GET PRODUCTS
    # =========================================

    def get_products(
        self,
        search: str | None,
        category: str | None,
        status: str | None,
        unit: str | None,
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
                detail="Invalid product status"
            )

        items, total = (
            self.repository.get_list(
                search=search,
                category=category,
                status=status,
                unit=unit,
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

    # =========================================
    # UPDATE PRODUCT
    # =========================================

    def update_product(
        self,
        product_id: int,
        request: ProductUpdateRequest
    ):

        product = self.get_product(
            product_id
        )

        # -------------------------------------
        # SKU
        # -------------------------------------

        if request.sku is not None:

            existing_sku = (
                self.repository.get_by_sku(
                    request.sku
                )
            )

            if (
                existing_sku
                and existing_sku.id != product_id
            ):

                raise HTTPException(
                    status_code=400,
                    detail="SKU already exists"
                )

            product.sku = request.sku

        # -------------------------------------
        # STATUS
        # -------------------------------------

        if request.status is not None:

            if request.status not in self.ALLOWED_STATUSES:

                raise HTTPException(
                    status_code=400,
                    detail="Invalid product status"
                )

            product.status = request.status

        # -------------------------------------
        # OTHER FIELDS
        # -------------------------------------

        if request.product_name is not None:

            product.product_name = (
                request.product_name
            )

        if request.category is not None:

            product.category = request.category

        if request.unit_of_measurement is not None:

            product.unit_of_measurement = (
                request.unit_of_measurement
            )

        if request.standard_production_time is not None:

            product.standard_production_time = (
                request.standard_production_time
            )

        if request.production_time_unit is not None:

            product.production_time_unit = (
                request.production_time_unit
            )

        if request.description is not None:

            product.description = (
                request.description
            )

        return self.repository.update(product)

    # =========================================
    # DELETE
    # =========================================

    def delete_product(
        self,
        product_id: int
    ):

        product = self.get_product(
            product_id
        )

        self.repository.delete(product)

        return {
            "message": "Product deleted successfully"
        }

    # =========================================
    # UPDATE STATUS
    # =========================================

    def update_status(
        self,
        product_id: int,
        new_status: str
    ):

        product = self.get_product(
            product_id
        )

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid product status"
            )

        product.status = new_status

        return self.repository.update(product)