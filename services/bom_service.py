import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.bom_model import BOM
from models.bom_item_model import BOMItem

from repositories.bom_repository import (
    BOMRepository
)

from models.product_model import Product
from models.material_model import Material


class BOMService:

    ALLOWED_STATUSES = {
        "Active",
        "Inactive"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = BOMRepository(
            db
        )

    # =========================================
    # PRODUCT VALIDATION
    # =========================================

    def validate_product(
        self,
        product_id: int
    ):

        product = (
            self.db.query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        if product.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="BOM can only be created for an active product"
            )

        return product

    # =========================================
    # MATERIAL VALIDATION
    # =========================================

    def validate_material(
        self,
        material_id: int
    ):

        material = (
            self.db.query(Material)
            .filter(
                Material.id == material_id
            )
            .first()
        )

        if not material:

            raise HTTPException(
                status_code=404,
                detail="Material not found"
            )

        if material.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Only active materials can be added to BOM"
            )

        return material

    # =========================================
    # CREATE BOM
    # =========================================

    def create_bom(
        self,
        data
    ):

        self.validate_product(
            data.product_id
        )

        if data.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid BOM status"
            )

        existing = (
            self.repository
            .get_by_product_version(
                data.product_id,
                data.version
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="BOM version already exists for this product"
            )

        # If creating Active BOM,
        # deactivate existing active BOM

        if data.status == "Active":

            active_bom = (
                self.repository
                .get_active_by_product(
                    data.product_id
                )
            )

            if active_bom:

                active_bom.status = "Inactive"

                self.repository.update_bom(
                    active_bom
                )

        bom = BOM(
            product_id=data.product_id,
            version=data.version,
            status=data.status,
            description=data.description
        )

        return self.repository.create_bom(
            bom
        )

    # =========================================
    # GET BOM
    # =========================================

    def get_bom(
        self,
        bom_id: int
    ):

        bom = self.repository.get_by_id(
            bom_id
        )

        if not bom:

            raise HTTPException(
                status_code=404,
                detail="BOM not found"
            )

        return bom

    # =========================================
    # GET BOM DETAILS
    # =========================================

    def get_bom_details(
        self,
        bom_id: int
    ):

        bom = self.get_bom(
            bom_id
        )

        items = self.repository.get_items(
            bom_id
        )

        return {
            "id": bom.id,
            "product_id": bom.product_id,
            "version": bom.version,
            "status": bom.status,
            "description": bom.description,
            "items": items
        }

    # =========================================
    # LIST BOM
    # =========================================

    def get_boms(
        self,
        product_id=None,
        status=None,
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
                detail="Page size must be between 1 and 100"
            )

        if status and status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid BOM status"
            )

        items, total = (
            self.repository.get_all(
                product_id=product_id,
                status=status,
                page=page,
                page_size=page_size
            )
        )

        total_pages = (
            math.ceil(total / page_size)
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
    # UPDATE BOM
    # =========================================

    def update_bom(
        self,
        bom_id: int,
        data
    ):

        bom = self.get_bom(
            bom_id
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "version" in update_data:

            existing = (
                self.repository
                .get_by_product_version(
                    bom.product_id,
                    update_data["version"]
                )
            )

            if existing and existing.id != bom.id:

                raise HTTPException(
                    status_code=409,
                    detail="BOM version already exists"
                )

        for field, value in update_data.items():

            setattr(
                bom,
                field,
                value
            )

        return self.repository.update_bom(
            bom
        )

    # =========================================
    # DELETE BOM
    # =========================================

    def delete_bom(
        self,
        bom_id: int
    ):

        bom = self.get_bom(
            bom_id
        )

        self.repository.delete_bom(
            bom
        )

        return {
            "message": "BOM deleted successfully"
        }

    # =========================================
    # ACTIVATE / DEACTIVATE BOM
    # =========================================

    def update_status(
        self,
        bom_id: int,
        new_status: str
    ):

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid BOM status"
            )

        bom = self.get_bom(
            bom_id
        )

        # -------------------------------------
        # ACTIVATING BOM
        # -------------------------------------

        if new_status == "Active":

            existing_active = (
                self.repository
                .get_active_by_product(
                    bom.product_id
                )
            )

            if (
                existing_active
                and existing_active.id != bom.id
            ):

                existing_active.status = "Inactive"

                self.repository.update_bom(
                    existing_active
                )

        bom.status = new_status

        return self.repository.update_bom(
            bom
        )

    # =========================================
    # ADD MATERIAL
    # =========================================

    def add_material(
        self,
        bom_id: int,
        data
    ):

        bom = self.get_bom(
            bom_id
        )

        # Do not modify active BOM directly.
        # Create a new version instead.

        if bom.status == "Active":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Active BOM cannot be modified directly. "
                    "Create a new BOM version."
                )
            )

        self.validate_material(
            data.material_id
        )

        existing = (
            self.repository.get_item(
                bom_id,
                data.material_id
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Material already exists in this BOM"
            )

        item = BOMItem(
            bom_id=bom_id,
            material_id=data.material_id,
            quantity_required=data.quantity_required
        )

        return self.repository.create_item(
            item
        )

    # =========================================
    # UPDATE MATERIAL QUANTITY
    # =========================================

    def update_material(
        self,
        bom_id: int,
        material_id: int,
        data
    ):

        bom = self.get_bom(
            bom_id
        )

        if bom.status == "Active":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Active BOM cannot be modified directly. "
                    "Create a new BOM version."
                )
            )

        item = (
            self.repository
            .get_item(
                bom_id,
                material_id
            )
        )

        if not item:

            raise HTTPException(
                status_code=404,
                detail="Material not found in BOM"
            )

        item.quantity_required = (
            data.quantity_required
        )

        return self.repository.update_item(
            item
        )

    # =========================================
    # REMOVE MATERIAL
    # =========================================

    def remove_material(
        self,
        bom_id: int,
        material_id: int
    ):

        bom = self.get_bom(
            bom_id
        )

        if bom.status == "Active":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Active BOM cannot be modified directly. "
                    "Create a new BOM version."
                )
            )

        item = (
            self.repository
            .get_item(
                bom_id,
                material_id
            )
        )

        if not item:

            raise HTTPException(
                status_code=404,
                detail="Material not found in BOM"
            )

        self.repository.delete_item(
            item
        )

        return {
            "message": "Material removed from BOM successfully"
        }

    # =========================================
    # GET BOM MATERIALS
    # =========================================

    def get_materials(
        self,
        bom_id: int
    ):

        self.get_bom(
            bom_id
        )

        return self.repository.get_items(
            bom_id
        )

    # =========================================
    # PRODUCT BOM HISTORY
    # =========================================

    def get_product_boms(
        self,
        product_id: int
    ):

        self.validate_product(
            product_id
        )

        return (
            self.repository
            .get_product_boms(
                product_id
            )
        )