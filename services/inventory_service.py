from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.inventory_movement_model import (
    InventoryMovement
)

from models.product_inventory_model import (
    ProductInventory
)

from models.material_model import Material
from models.product_model import Product
from models.production_batch_model import ProductionBatch

from repositories.inventory_repository import (
    InventoryRepository
)


class InventoryService:

    ALLOWED_MOVEMENT_TYPES = {
        "Raw Material Receipt",
        "Material Consumption",
        "Finished Goods Production",
        "Rejected Goods",
        "Stock Adjustment"
    }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.repository = InventoryRepository(
            db
        )

    # =====================================================
    # DUPLICATE TRANSACTION CHECK
    # =====================================================

    def check_transaction_number(
        self,
        transaction_number: str
    ):

        existing = (
            self.repository
            .get_by_transaction_number(
                transaction_number
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Transaction number already exists"
            )

    # =====================================================
    # GET MATERIAL
    # =====================================================

    def get_material(
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
                detail="Material is inactive"
            )

        return material

    # =====================================================
    # GET PRODUCT
    # =====================================================

    def get_product(
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
                detail="Product is inactive"
            )

        return product

    # =====================================================
    # GET BATCH
    # =====================================================

    def get_batch(
        self,
        production_batch_id: int
    ):

        batch = (
            self.db.query(
                ProductionBatch
            )
            .filter(
                ProductionBatch.id
                == production_batch_id
            )
            .first()
        )

        if not batch:

            raise HTTPException(
                status_code=404,
                detail="Production batch not found"
            )

        return batch

    # =====================================================
    # RAW MATERIAL RECEIPT
    # =====================================================

    def receive_material(
        self,
        data,
        performed_by: int
    ):

        self.check_transaction_number(
            data.transaction_number
        )

        material = self.get_material(
            data.material_id
        )

        quantity_before = (
            material.available_quantity
        )

        quantity_after = (
            quantity_before
            + data.quantity
        )

        material.available_quantity = (
            quantity_after
        )

        movement = InventoryMovement(

            transaction_number=(
                data.transaction_number
            ),

            movement_type=(
                "Raw Material Receipt"
            ),

            material_id=data.material_id,

            product_id=None,

            production_batch_id=None,

            quantity=data.quantity,

            quantity_before=quantity_before,

            quantity_after=quantity_after,

            reference_number=(
                data.reference_number
            ),

            reason=data.reason,

            performed_by=performed_by
        )

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement

    # =====================================================
    # MATERIAL CONSUMPTION
    # =====================================================

    def consume_material(
        self,
        data,
        performed_by: int
    ):

        self.check_transaction_number(
            data.transaction_number
        )

        material = self.get_material(
            data.material_id
        )

        batch = self.get_batch(
            data.production_batch_id
        )

        quantity_before = (
            material.available_quantity
        )

        if quantity_before < data.quantity:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Insufficient material stock"
                )
            )

        quantity_after = (
            quantity_before
            - data.quantity
        )

        material.available_quantity = (
            quantity_after
        )

        movement = InventoryMovement(

            transaction_number=(
                data.transaction_number
            ),

            movement_type=(
                "Material Consumption"
            ),

            material_id=data.material_id,

            product_id=None,

            production_batch_id=(
                batch.id
            ),

            quantity=data.quantity,

            quantity_before=quantity_before,

            quantity_after=quantity_after,

            reference_number=(
                data.reference_number
            ),

            reason=data.reason,

            performed_by=performed_by
        )

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement

    # =====================================================
    # FINISHED GOODS PRODUCTION
    # =====================================================

    def record_finished_goods(
        self,
        data,
        performed_by: int
    ):

        self.check_transaction_number(
            data.transaction_number
        )

        product = self.get_product(
            data.product_id
        )

        batch = self.get_batch(
            data.production_batch_id
        )

        # Product finished stock is maintained
        # through a movement history in this level.

        movement = InventoryMovement(

            transaction_number=(
                data.transaction_number
            ),

            movement_type=(
                "Finished Goods Production"
            ),

            material_id=None,

            product_id=product.id,

            production_batch_id=batch.id,

            quantity=data.quantity,

            quantity_before=0,

            quantity_after=data.quantity,

            reference_number=(
                data.reference_number
            ),

            reason=data.reason,

            performed_by=performed_by
        )

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement

    # =====================================================
    # REJECTED GOODS
    # =====================================================

    def record_rejected_goods(
        self,
        data,
        performed_by: int
    ):

        self.check_transaction_number(
            data.transaction_number
        )

        product = self.get_product(
            data.product_id
        )

        batch = self.get_batch(
            data.production_batch_id
        )

        movement = InventoryMovement(

            transaction_number=(
                data.transaction_number
            ),

            movement_type="Rejected Goods",

            material_id=None,

            product_id=product.id,

            production_batch_id=batch.id,

            quantity=data.quantity,

            quantity_before=0,

            quantity_after=data.quantity,

            reference_number=(
                data.reference_number
            ),

            reason=data.reason,

            performed_by=performed_by
        )

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement

    # =====================================================
    # STOCK ADJUSTMENT
    # =====================================================

    def adjust_stock(
        self,
        data,
        performed_by: int
    ):

        self.check_transaction_number(
            data.transaction_number
        )

        material = self.get_material(
            data.material_id
        )

        quantity_before = (
            material.available_quantity
        )

        quantity_after = (
            quantity_before
            + data.quantity
        )

        if quantity_after < 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Stock adjustment cannot "
                    "make inventory negative"
                )
            )

        material.available_quantity = (
            quantity_after
        )

        movement = InventoryMovement(

            transaction_number=(
                data.transaction_number
            ),

            movement_type="Stock Adjustment",

            material_id=data.material_id,

            product_id=None,

            production_batch_id=None,

            quantity=data.quantity,

            quantity_before=quantity_before,

            quantity_after=quantity_after,

            reference_number=(
                data.reference_number
            ),

            reason=data.reason,

            performed_by=performed_by
        )

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement

    # =====================================================
    # HISTORY
    # =====================================================

    def get_history(
        self,
        movement_type=None,
        material_id=None,
        product_id=None,
        production_batch_id=None,
        page=1,
        page_size=10
    ):

        if page < 1:

            raise HTTPException(
                status_code=400,
                detail="Page must be at least 1"
            )

        if page_size < 1 or page_size > 100:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Page size must be between 1 and 100"
                )
            )

        if movement_type:

            if movement_type not in (
                self.ALLOWED_MOVEMENT_TYPES
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Invalid movement type"
                )

        items, total = (
            self.repository.get_list(
                movement_type=movement_type,
                material_id=material_id,
                product_id=product_id,
                production_batch_id=production_batch_id,
                page=page,
                page_size=page_size
            )
        )

        total_pages = (
            (total + page_size - 1)
            // page_size
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # =====================================================
    # GET TRANSACTION
    # =====================================================

    def get_transaction(
        self,
        movement_id: int
    ):

        movement = (
            self.repository
            .get_by_id(
                movement_id
            )
        )

        if not movement:

            raise HTTPException(
                status_code=404,
                detail="Inventory transaction not found"
            )

        return movement


    def record_finished_goods(
        self,
        data,
        performed_by: int
):

        self.check_transaction_number(
          data.transaction_number
    )

        product = self.get_product(
          data.product_id
    )

        batch = self.get_batch(
          data.production_batch_id
    )

        inventory = (
          self.db.query(ProductInventory)
          .filter(
            ProductInventory.product_id
            == product.id
        )
        .first()
    )

        if not inventory:

          inventory = ProductInventory(
            product_id=product.id,
            available_quantity=0,
            rejected_quantity=0
        )

        self.db.add(inventory)

        self.db.flush()

        quantity_before = (
           inventory.available_quantity
    )

        quantity_after = (
           quantity_before
           + data.quantity
    )

        inventory.available_quantity = (
           quantity_after
    )

        movement = InventoryMovement(

            transaction_number=(
              data.transaction_number
        ),

            movement_type=(
               "Finished Goods Production"
        ),

            material_id=None,

            product_id=product.id,

            production_batch_id=batch.id,

            quantity=data.quantity,

            quantity_before=quantity_before,

            quantity_after=quantity_after,

            reference_number=data.reference_number,

            reason=data.reason,

            performed_by=performed_by
    )

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement