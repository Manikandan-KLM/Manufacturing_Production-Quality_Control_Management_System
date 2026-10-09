from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.production_order_model import ProductionOrder


class ProductionOrderRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------
    # CREATE
    # -----------------------------------------

    def create(self, order: ProductionOrder):

        self.db.add(order)

        self.db.commit()

        self.db.refresh(order)

        return order

    # -----------------------------------------
    # GET BY ID
    # -----------------------------------------

    def get_by_id(self, order_id: int):

        return (
            self.db.query(ProductionOrder)
            .filter(
                ProductionOrder.id == order_id
            )
            .first()
        )

    # -----------------------------------------
    # GET BY ORDER NUMBER
    # -----------------------------------------

    def get_by_order_number(
        self,
        order_number: str
    ):

        return (
            self.db.query(ProductionOrder)
            .filter(
                ProductionOrder.order_number == order_number
            )
            .first()
        )

    # -----------------------------------------
    # LIST
    # -----------------------------------------

    def get_list(
        self,
        search=None,
        status=None,
        priority=None,
        product_id=None,
        production_line_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(
            ProductionOrder
        )

        # Search order number
        if search:

            search_pattern = f"%{search}%"

            query = query.filter(
                ProductionOrder.order_number.ilike(
                    search_pattern
                )
            )

        # Status filter
        if status:

            query = query.filter(
                ProductionOrder.status == status
            )

        # Priority filter
        if priority:

            query = query.filter(
                ProductionOrder.priority == priority
            )

        # Product filter
        if product_id:

            query = query.filter(
                ProductionOrder.product_id == product_id
            )

        # Production line filter
        if production_line_id:

            query = query.filter(
                ProductionOrder.production_line_id
                == production_line_id
            )

        total = query.count()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(
                ProductionOrder.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    # -----------------------------------------
    # UPDATE
    # -----------------------------------------

    def update(
        self,
        order: ProductionOrder
    ):

        self.db.commit()

        self.db.refresh(order)

        return order

    # -----------------------------------------
    # DELETE
    # -----------------------------------------

    def delete(
        self,
        order: ProductionOrder
    ):

        self.db.delete(order)

        self.db.commit()