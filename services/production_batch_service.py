from datetime import datetime
import math

from fastapi import HTTPException

from sqlalchemy.orm import Session

from models.production_batch_model import ProductionBatch
from models.production_order_model import ProductionOrder
from models.production_line_model import ProductionLine
from models.machine_model import Machine
from models.user_model import User

from repositories.production_batch_repository import (
    ProductionBatchRepository
)


class ProductionBatchService:

    def __init__(self, db: Session):

        self.db = db

        self.repository = (
            ProductionBatchRepository(db)
        )

    # =========================================
    # GET BATCH
    # =========================================

    def get_batch(
        self,
        batch_id: int
    ):

        batch = self.repository.get_by_id(
            batch_id
        )

        if not batch:

            raise HTTPException(
                status_code=404,
                detail="Production batch not found"
            )

        return batch

    # =========================================
    # VALIDATE PRODUCTION ORDER
    # =========================================

    def validate_production_order(
        self,
        production_order_id: int
    ):

        order = (
            self.db.query(ProductionOrder)
            .filter(
                ProductionOrder.id
                == production_order_id
            )
            .first()
        )

        if not order:

            raise HTTPException(
                status_code=404,
                detail="Production order not found"
            )

        if order.status in {
            "Completed",
            "Cancelled"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot create batch for "
                    f"{order.status.lower()} production order"
                )
            )

        return order

    # =========================================
    # VALIDATE PRODUCTION LINE
    # =========================================

    def validate_production_line(
        self,
        production_line_id: int
    ):

        line = (
            self.db.query(ProductionLine)
            .filter(
                ProductionLine.id
                == production_line_id
            )
            .first()
        )

        if not line:

            raise HTTPException(
                status_code=404,
                detail="Production line not found"
            )

        if line.status in {
            "Inactive",
            "Temporarily Closed"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Production line is inactive "
                    "or temporarily closed"
                )
            )

        return line

    # =========================================
    # VALIDATE MACHINE
    # =========================================

    def validate_machine(
        self,
        machine_id: int,
        production_line_id: int
    ):

        machine = (
            self.db.query(Machine)
            .filter(
                Machine.id == machine_id
            )
            .first()
        )

        if not machine:

            raise HTTPException(
                status_code=404,
                detail="Machine not found"
            )

        if machine.production_line_id != production_line_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Machine does not belong to "
                    "the selected production line"
                )
            )

        if machine.status in {
            "Maintenance",
            "Breakdown",
            "Decommissioned"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Machine is not available "
                    "for production"
                )
            )

        return machine

    # =========================================
    # VALIDATE SUPERVISOR
    # =========================================

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

    # =========================================
    # GENERATE BATCH NUMBER
    # =========================================

    def generate_batch_number(self):

        last_batch = (
            self.db.query(ProductionBatch)
            .order_by(
                ProductionBatch.id.desc()
            )
            .first()
        )

        if not last_batch:

            number = 1

        else:

            number = last_batch.id + 1

        return f"BATCH{number:06d}"

    # =========================================
    # CREATE BATCH
    # =========================================

    def create_batch(
        self,
        data
    ):

        # Validate order

        order = (
            self.validate_production_order(
                data.production_order_id
            )
        )

        # Planned quantity cannot exceed
        # remaining production order quantity

        existing_batches = (
            self.db.query(ProductionBatch)
            .filter(
                ProductionBatch.production_order_id
                == data.production_order_id
            )
            .all()
        )

        already_planned = sum(
            batch.planned_quantity
            for batch in existing_batches
        )

        remaining_quantity = (
            order.quantity - already_planned
        )

        if data.planned_quantity > remaining_quantity:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Planned batch quantity exceeds "
                    "remaining production order quantity"
                )
            )

        # Validate production line

        self.validate_production_line(
            data.production_line_id
        )

        # Validate machine

        self.validate_machine(
            data.machine_id,
            data.production_line_id
        )

        # Validate supervisor

        self.validate_supervisor(
            data.supervisor_id
        )

        # Generate batch number

        batch_number = (
            self.generate_batch_number()
        )

        batch = ProductionBatch(

            batch_number=batch_number,

            production_order_id=(
                data.production_order_id
            ),

            planned_quantity=(
                data.planned_quantity
            ),

            produced_quantity=0,

            rejected_quantity=0,

            start_time=None,

            end_time=None,

            production_line_id=(
                data.production_line_id
            ),

            machine_id=(
                data.machine_id
            ),

            supervisor_id=(
                data.supervisor_id
            )
        )

        return self.repository.create(batch)

    # =========================================
    # LIST BATCHES
    # =========================================

    def get_batches(
        self,
        production_order_id=None,
        production_line_id=None,
        machine_id=None,
        supervisor_id=None,
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
                detail=(
                    "Page size must be between 1 and 100"
                )
            )

        items, total = (
            self.repository.get_list(

                production_order_id=(
                    production_order_id
                ),

                production_line_id=(
                    production_line_id
                ),

                machine_id=machine_id,

                supervisor_id=supervisor_id,

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
    # UPDATE BATCH
    # =========================================

    def update_batch(
        self,
        batch_id: int,
        data
    ):

        batch = self.get_batch(
            batch_id
        )

        if batch.end_time is not None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Completed batch cannot be updated"
                )
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        production_line_id = (
            update_data.get(
                "production_line_id",
                batch.production_line_id
            )
        )

        machine_id = (
            update_data.get(
                "machine_id",
                batch.machine_id
            )
        )

        # Validate line

        self.validate_production_line(
            production_line_id
        )

        # Validate machine

        self.validate_machine(
            machine_id,
            production_line_id
        )

        # Validate supervisor

        if "supervisor_id" in update_data:

            self.validate_supervisor(
                update_data["supervisor_id"]
            )

        # Planned quantity validation

        if "planned_quantity" in update_data:

            if (
                update_data["planned_quantity"]
                < batch.produced_quantity
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Planned quantity cannot be "
                        "less than produced quantity"
                    )
                )

        for field, value in update_data.items():

            setattr(
                batch,
                field,
                value
            )

        return self.repository.update(
            batch
        )

    # =========================================
    # UPDATE QUANTITIES
    # =========================================

    def update_quantities(
        self,
        batch_id: int,
        produced_quantity: float,
        rejected_quantity: float
    ):

        batch = self.get_batch(
            batch_id
        )

        if batch.end_time is not None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot update quantities "
                    "after batch completion"
                )
            )

        if (
            produced_quantity
            + rejected_quantity
            > batch.planned_quantity
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Produced quantity plus rejected "
                    "quantity cannot exceed planned quantity"
                )
            )

        batch.produced_quantity = (
            produced_quantity
        )

        batch.rejected_quantity = (
            rejected_quantity
        )

        return self.repository.update(
            batch
        )

    # =========================================
    # UPDATE TIME
    # =========================================

    def update_time(
        self,
        batch_id: int,
        start_time,
        end_time
    ):

        batch = self.get_batch(
            batch_id
        )

        if start_time and end_time:

            if end_time < start_time:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "End time cannot be before "
                        "start time"
                    )
                )

        if start_time:

            batch.start_time = start_time

        if end_time:

            if not batch.start_time:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Start time must be set "
                        "before end time"
                    )
                )

            if end_time < batch.start_time:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "End time cannot be before "
                        "start time"
                    )
                )

            batch.end_time = end_time

        return self.repository.update(
            batch
        )

    # =========================================
    # CALCULATE METRICS
    # =========================================

    def calculate_metrics(
        self,
        batch_id: int
    ):

        batch = self.get_batch(
            batch_id
        )

        planned = batch.planned_quantity

        produced = batch.produced_quantity

        rejected = batch.rejected_quantity

        # -------------------------------------
        # Completion %
        # -------------------------------------

        completion_percentage = (
            produced / planned
        ) * 100 if planned > 0 else 0

        # -------------------------------------
        # Rejection %
        # -------------------------------------

        rejection_percentage = (
            rejected / produced
        ) * 100 if produced > 0 else 0

        # -------------------------------------
        # Good quantity
        # -------------------------------------

        good_quantity = (
            produced - rejected
        )

        # -------------------------------------
        # Production efficiency
        # -------------------------------------

        production_efficiency = (
            good_quantity / planned
        ) * 100 if planned > 0 else 0

        return {
            "batch_id": batch.id,

            "batch_number": (
                batch.batch_number
            ),

            "planned_quantity": planned,

            "produced_quantity": produced,

            "rejected_quantity": rejected,

            "good_quantity": good_quantity,

            "completion_percentage": round(
                completion_percentage,
                2
            ),

            "rejection_percentage": round(
                rejection_percentage,
                2
            ),

            "production_efficiency": round(
                production_efficiency,
                2
            )
        }

    # =========================================
    # DELETE
    # =========================================

    def delete_batch(
        self,
        batch_id: int
    ):

        batch = self.get_batch(
            batch_id
        )

        if batch.start_time is not None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Started production batch "
                    "cannot be deleted"
                )
            )

        self.repository.delete(
            batch
        )

        return {
            "message": (
                "Production batch deleted successfully"
            )
        }