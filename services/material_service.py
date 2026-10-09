import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.material_model import Material
from models.material_history_model import MaterialHistory

from repositories.material_repository import (
    MaterialRepository
)


class MaterialService:

    ALLOWED_STATUSES = {
        "Active",
        "Inactive",
        "Discontinued"
    }

    def __init__(self, db: Session):

        self.repository = MaterialRepository(db)

    # -----------------------------------------
    # CREATE
    # -----------------------------------------

    def create_material(
        self,
        data,
        current_user
    ):

        existing = self.repository.get_by_code(
            data.material_code
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Material code already exists"
            )

        if data.status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid material status"
            )

        if data.reorder_level < data.minimum_stock_level:

            raise HTTPException(
                status_code=400,
                detail="Reorder level cannot be lower than minimum stock level"
            )

        material = Material(
            material_code=data.material_code,
            material_name=data.material_name,
            category=data.category,
            unit=data.unit,
            available_quantity=data.available_quantity,
            minimum_stock_level=data.minimum_stock_level,
            reorder_level=data.reorder_level,
            supplier_reference=data.supplier_reference,
            status=data.status,
            description=data.description
        )

        material = self.repository.create(material)

        # Initial stock history
        if data.available_quantity > 0:

            history = MaterialHistory(
                material_id=material.id,
                transaction_type="STOCK_IN",
                quantity=data.available_quantity,
                previous_quantity=0,
                new_quantity=data.available_quantity,
                reference="INITIAL_STOCK",
                remarks="Initial material stock",
                performed_by=current_user.id
            )

            self.repository.create_history(history)

        return material

    # -----------------------------------------
    # GET
    # -----------------------------------------

    def get_material(
        self,
        material_id: int
    ):

        material = self.repository.get_by_id(
            material_id
        )

        if not material:

            raise HTTPException(
                status_code=404,
                detail="Material not found"
            )

        return material

    # -----------------------------------------
    # LIST
    # -----------------------------------------

    def get_materials(
        self,
        search=None,
        category=None,
        status=None,
        unit=None,
        low_stock=False,
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
                detail="Invalid material status"
            )

        items, total = self.repository.get_list(
            search=search,
            category=category,
            status=status,
            unit=unit,
            low_stock=low_stock,
            page=page,
            page_size=page_size
        )

        total_pages = math.ceil(
            total / page_size
        ) if total else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # -----------------------------------------
    # UPDATE
    # -----------------------------------------

    def update_material(
        self,
        material_id: int,
        data
    ):

        material = self.get_material(
            material_id
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "status" in update_data:

            if update_data["status"] not in self.ALLOWED_STATUSES:

                raise HTTPException(
                    status_code=400,
                    detail="Invalid material status"
                )

        new_minimum = update_data.get(
            "minimum_stock_level",
            material.minimum_stock_level
        )

        new_reorder = update_data.get(
            "reorder_level",
            material.reorder_level
        )

        if new_reorder < new_minimum:

            raise HTTPException(
                status_code=400,
                detail="Reorder level cannot be lower than minimum stock level"
            )

        for field, value in update_data.items():

            setattr(
                material,
                field,
                value
            )

        return self.repository.update(
            material
        )

    # -----------------------------------------
    # DELETE
    # -----------------------------------------

    def delete_material(
        self,
        material_id: int
    ):

        material = self.get_material(
            material_id
        )

        self.repository.delete(
            material
        )

        return {
            "message": "Material deleted successfully"
        }

    # -----------------------------------------
    # STATUS
    # -----------------------------------------

    def update_status(
        self,
        material_id: int,
        new_status: str
    ):

        if new_status not in self.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid material status"
            )

        material = self.get_material(
            material_id
        )

        material.status = new_status

        return self.repository.update(
            material
        )

    # -----------------------------------------
    # STOCK IN
    # -----------------------------------------

    def stock_in(
        self,
        material_id: int,
        data,
        current_user
    ):

        material = self.get_material(
            material_id
        )

        if material.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Cannot add stock to inactive or discontinued material"
            )

        previous_quantity = (
            material.available_quantity
        )

        new_quantity = (
            previous_quantity + data.quantity
        )

        material.available_quantity = new_quantity

        self.repository.update(
            material
        )

        history = MaterialHistory(
            material_id=material.id,
            transaction_type="STOCK_IN",
            quantity=data.quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reference=data.reference,
            remarks=data.remarks,
            performed_by=current_user.id
        )

        self.repository.create_history(
            history
        )

        return material

    # -----------------------------------------
    # STOCK OUT
    # -----------------------------------------

    def stock_out(
        self,
        material_id: int,
        data,
        current_user
    ):

        material = self.get_material(
            material_id
        )

        if material.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Cannot issue inactive or discontinued material"
            )

        previous_quantity = (
            material.available_quantity
        )

        # IMPORTANT:
        # Prevent negative inventory

        if data.quantity > previous_quantity:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock. "
                    f"Available quantity: {previous_quantity}"
                )
            )

        new_quantity = (
            previous_quantity - data.quantity
        )

        # Extra safety check

        if new_quantity < 0:

            raise HTTPException(
                status_code=400,
                detail="Inventory quantity cannot be negative"
            )

        material.available_quantity = new_quantity

        self.repository.update(
            material
        )

        history = MaterialHistory(
            material_id=material.id,
            transaction_type="STOCK_OUT",
            quantity=data.quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reference=data.reference,
            remarks=data.remarks,
            performed_by=current_user.id
        )

        self.repository.create_history(
            history
        )

        return material

    # -----------------------------------------
    # ADJUSTMENT
    # -----------------------------------------

    def adjust_stock(
        self,
        material_id: int,
        data,
        current_user
    ):

        material = self.get_material(
            material_id
        )

        previous_quantity = (
            material.available_quantity
        )

        new_quantity = (
            previous_quantity + data.quantity
        )

        # IMPORTANT:
        # Prevent negative inventory

        if new_quantity < 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Adjustment would result in negative inventory"
                )
            )

        material.available_quantity = new_quantity

        self.repository.update(
            material
        )

        history = MaterialHistory(
            material_id=material.id,
            transaction_type="ADJUSTMENT",
            quantity=data.quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reference=data.reference,
            remarks=data.remarks,
            performed_by=current_user.id
        )

        self.repository.create_history(
            history
        )

        return material

    # -----------------------------------------
    # HISTORY
    # -----------------------------------------

    def get_history(
        self,
        material_id: int
    ):

        self.get_material(
            material_id
        )

        return self.repository.get_history(
            material_id
        )