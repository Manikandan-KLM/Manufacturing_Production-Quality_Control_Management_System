from datetime import date
import math

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.production_order_model import ProductionOrder
from models.product_model import Product
from models.production_line_model import ProductionLine
from models.user_model import User

from repositories.production_order_repository import (
    ProductionOrderRepository
)


class ProductionOrderService:

    ALLOWED_PRIORITIES = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    ALLOWED_STATUSES = {
        "Draft",
        "Scheduled",
        "In Progress",
        "Paused",
        "Completed",
        "Cancelled"
    }

    # -----------------------------------------
    # STATUS TRANSITIONS
    # -----------------------------------------

    STATUS_TRANSITIONS = {

        "Draft": {
            "Scheduled",
            "Cancelled"
        },

        "Scheduled": {
            "In Progress",
            "Cancelled"
        },

        "In Progress": {
            "Paused",
            "Completed",
            "Cancelled"
        },

        "Paused": {
            "In Progress",
            "Cancelled"
        },

        "Completed": set(),

        "Cancelled": set()
    }

    def __init__(self, db: Session):

        self.db = db

        self.repository = (
            ProductionOrderRepository(db)
        )

    # -----------------------------------------
    # GET ORDER
    # -----------------------------------------

    def get_order(
        self,
        order_id: int
    ):

        order = self.repository.get_by_id(
            order_id
        )

        if not order:

            raise HTTPException(
                status_code=404,
                detail="Production order not found"
            )

        return order

    # -----------------------------------------
    # VALIDATE PRODUCT
    # -----------------------------------------

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
                detail="Only active products can be used"
            )

        return product

    # -----------------------------------------
    # VALIDATE PRODUCTION LINE
    # -----------------------------------------

    def validate_production_line(
        self,
        production_line_id: int
    ):

        production_line = (
            self.db.query(ProductionLine)
            .filter(
                ProductionLine.id
                == production_line_id
            )
            .first()
        )

        if not production_line:

            raise HTTPException(
                status_code=404,
                detail="Production line not found"
            )

        if production_line.status in {
            "Inactive",
            "Temporarily Closed"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Production order cannot be assigned "
                    "to an inactive or closed production line"
                )
            )

        return production_line

    # -----------------------------------------
    # VALIDATE SUPERVISOR
    # -----------------------------------------

    def validate_supervisor(
        self,
        supervisor_id: int | None
    ):

        if supervisor_id is None:
            return None

        supervisor = (
            self.db.query(User)
            .filter(
                User.id == supervisor_id
            )
            .first()
        )

        if not supervisor:

            raise HTTPException(
                status_code=404,
                detail="Supervisor not found"
            )

        if not supervisor.is_active:

            raise HTTPException(
                status_code=400,
                detail="Supervisor account is inactive"
            )

        return supervisor

    # -----------------------------------------
    # GENERATE ORDER NUMBER
    # -----------------------------------------

    def generate_order_number(self):

        last_order = (
            self.db.query(ProductionOrder)
            .order_by(
                ProductionOrder.id.desc()
            )
            .first()
        )

        if not last_order:

            number = 1

        else:

            number = last_order.id + 1

        return f"PO{number:06d}"

    # -----------------------------------------
    # CREATE ORDER
    # -----------------------------------------

    def create_order(self, data):

        # Validate priority

        if data.priority not in self.ALLOWED_PRIORITIES:

            raise HTTPException(
                status_code=400,
                detail="Invalid production order priority"
            )

        # Target date validation

        if data.target_date < date.today():

            raise HTTPException(
                status_code=400,
                detail="Target date cannot be in the past"
            )

        # Validate product

        self.validate_product(
            data.product_id
        )

        # Validate production line

        self.validate_production_line(
            data.production_line_id
        )

        # Validate supervisor

        self.validate_supervisor(
            data.supervisor_id
        )

        # Generate order number

        order_number = (
            self.generate_order_number()
        )

        order = ProductionOrder(

            order_number=order_number,

            product_id=data.product_id,

            quantity=data.quantity,

            target_date=data.target_date,

            production_line_id=data.production_line_id,

            priority=data.priority,

            supervisor_id=data.supervisor_id,

            status="Draft"
        )

        return self.repository.create(order)

    # -----------------------------------------
    # LIST ORDERS
    # -----------------------------------------

    def get_orders(
        self,
        search=None,
        status=None,
        priority=None,
        product_id=None,
        production_line_id=None,
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
                detail="Invalid production order status"
            )

        if priority and priority not in self.ALLOWED_PRIORITIES:

            raise HTTPException(
                status_code=400,
                detail="Invalid production order priority"
            )

        items, total = self.repository.get_list(

            search=search,

            status=status,

            priority=priority,

            product_id=product_id,

            production_line_id=production_line_id,

            page=page,

            page_size=page_size
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

    # -----------------------------------------
    # UPDATE ORDER
    # -----------------------------------------

    def update_order(
        self,
        order_id: int,
        data
    ):

        order = self.get_order(order_id)

        # Only Draft orders can be edited freely

        if order.status not in {
            "Draft",
            "Scheduled"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only Draft or Scheduled orders "
                    "can be updated"
                )
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # Validate product

        if "product_id" in update_data:

            self.validate_product(
                update_data["product_id"]
            )

        # Validate production line

        if "production_line_id" in update_data:

            self.validate_production_line(
                update_data["production_line_id"]
            )

        # Validate supervisor

        if "supervisor_id" in update_data:

            self.validate_supervisor(
                update_data["supervisor_id"]
            )

        # Validate priority

        if "priority" in update_data:

            if (
                update_data["priority"]
                not in self.ALLOWED_PRIORITIES
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Invalid production order priority"
                )

        # Validate target date

        if "target_date" in update_data:

            if (
                update_data["target_date"]
                < date.today()
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Target date cannot be in the past"
                )

        for field, value in update_data.items():

            setattr(
                order,
                field,
                value
            )

        return self.repository.update(order)

    # -----------------------------------------
    # UPDATE STATUS
    # -----------------------------------------

    def update_status(
        self,
        order_id: int,
        new_status: str
    ):

        order = self.get_order(order_id)

        # Validate status

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid production order status"
            )

        current_status = order.status

        # Same status

        if current_status == new_status:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Order is already in {current_status} status"
                )
            )

        allowed_next_statuses = (
            self.STATUS_TRANSITIONS[
                current_status
            ]
        )

        if new_status not in allowed_next_statuses:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status transition: "
                    f"{current_status} → {new_status}"
                )
            )

        # -------------------------------------
        # Extra business validations
        # -------------------------------------

        if new_status == "Scheduled":

            if not order.supervisor_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Supervisor must be assigned "
                        "before scheduling the order"
                    )
                )

        if new_status == "In Progress":

            if not order.supervisor_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Supervisor must be assigned "
                        "before starting production"
                    )
                )

        order.status = new_status

        return self.repository.update(order)

    # -----------------------------------------
    # DELETE ORDER
    # -----------------------------------------

    def delete_order(
        self,
        order_id: int
    ):

        order = self.get_order(order_id)

        if order.status not in {
            "Draft",
            "Cancelled"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only Draft or Cancelled orders "
                    "can be deleted"
                )
            )

        self.repository.delete(order)

        return {
            "message": (
                "Production order deleted successfully"
            )
        }