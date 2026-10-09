from sqlalchemy.orm import Session

from models.inventory_movement_model import (
    InventoryMovement
)


class InventoryRepository:

    def __init__(
        self,
        db: Session
    ):

        self.db = db

    # =====================================================
    # CREATE MOVEMENT
    # =====================================================

    def create(
        self,
        movement: InventoryMovement
    ):

        self.db.add(movement)

        self.db.commit()

        self.db.refresh(movement)

        return movement

    # =====================================================
    # GET BY TRANSACTION NUMBER
    # =====================================================

    def get_by_transaction_number(
        self,
        transaction_number: str
    ):

        return (
            self.db.query(
                InventoryMovement
            )
            .filter(
                InventoryMovement.transaction_number
                == transaction_number
            )
            .first()
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        movement_id: int
    ):

        return (
            self.db.query(
                InventoryMovement
            )
            .filter(
                InventoryMovement.id
                == movement_id
            )
            .first()
        )

    # =====================================================
    # GET LIST
    # =====================================================

    def get_list(
        self,
        movement_type=None,
        material_id=None,
        product_id=None,
        production_batch_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(
            InventoryMovement
        )

        if movement_type:

            query = query.filter(
                InventoryMovement.movement_type
                == movement_type
            )

        if material_id:

            query = query.filter(
                InventoryMovement.material_id
                == material_id
            )

        if product_id:

            query = query.filter(
                InventoryMovement.product_id
                == product_id
            )

        if production_batch_id:

            query = query.filter(
                InventoryMovement.production_batch_id
                == production_batch_id
            )

        total = query.count()

        offset = (
            page - 1
        ) * page_size

        items = (
            query
            .order_by(
                InventoryMovement.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total