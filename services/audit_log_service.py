from typing import Any

from sqlalchemy.orm import Session

from models.audit_log_model import AuditLog
from repositories.audit_log_repository import (
    AuditLogRepository,
)


class AuditLogService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditLogRepository(db)

    # =====================================================
    # CREATE AUDIT LOG
    # =====================================================

    def create_log(
        self,
        user_id: int | None,
        action: str,
        entity: str,
        entity_id: str | int | None = None,
        previous_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=(
                str(entity_id)
                if entity_id is not None
                else None
            ),
            previous_value=previous_value,
            new_value=new_value,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return self.repository.create(
            audit_log
        )

    # =====================================================
    # LOGIN
    # =====================================================

    def log_login(
        self,
        user_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ):

        return self.create_log(
            user_id=user_id,
            action="LOGIN",
            entity="User",
            entity_id=user_id,
            description="User logged in successfully",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    # =====================================================
    # CREATE
    # =====================================================

    def log_create(
        self,
        user_id: int,
        entity: str,
        entity_id: int | str,
        new_value: dict[str, Any],
        description: str | None = None,
    ):

        return self.create_log(
            user_id=user_id,
            action="CREATE",
            entity=entity,
            entity_id=entity_id,
            new_value=new_value,
            description=description,
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def log_update(
        self,
        user_id: int,
        entity: str,
        entity_id: int | str,
        previous_value: dict[str, Any],
        new_value: dict[str, Any],
        description: str | None = None,
    ):

        return self.create_log(
            user_id=user_id,
            action="UPDATE",
            entity=entity,
            entity_id=entity_id,
            previous_value=previous_value,
            new_value=new_value,
            description=description,
        )

    # =====================================================
    # APPROVAL
    # =====================================================

    def log_approval(
        self,
        user_id: int,
        entity: str,
        entity_id: int | str,
        previous_value: dict[str, Any] | None,
        new_value: dict[str, Any],
        description: str | None = None,
    ):

        return self.create_log(
            user_id=user_id,
            action="APPROVE",
            entity=entity,
            entity_id=entity_id,
            previous_value=previous_value,
            new_value=new_value,
            description=description,
        )

    # =====================================================
    # STATUS CHANGE
    # =====================================================

    def log_status_change(
        self,
        user_id: int,
        entity: str,
        entity_id: int | str,
        old_status: str,
        new_status: str,
        description: str | None = None,
    ):

        return self.create_log(
            user_id=user_id,
            action="STATUS_CHANGE",
            entity=entity,
            entity_id=entity_id,
            previous_value={
                "status": old_status
            },
            new_value={
                "status": new_status
            },
            description=description,
        )

    # =====================================================
    # MATERIAL MOVEMENT
    # =====================================================

    def log_material_movement(
        self,
        user_id: int,
        movement_id: int,
        movement_type: str,
        previous_quantity: float,
        new_quantity: float,
        quantity: float,
    ):

        return self.create_log(
            user_id=user_id,
            action="MATERIAL_MOVEMENT",
            entity="InventoryMovement",
            entity_id=movement_id,
            previous_value={
                "quantity": previous_quantity
            },
            new_value={
                "quantity": new_quantity
            },
            description=(
                f"{movement_type}: "
                f"{quantity} units"
            ),
        )

    # =====================================================
    # INVENTORY ADJUSTMENT
    # =====================================================

    def log_inventory_adjustment(
        self,
        user_id: int,
        movement_id: int,
        previous_quantity: float,
        new_quantity: float,
        reason: str | None = None,
    ):

        return self.create_log(
            user_id=user_id,
            action="INVENTORY_ADJUSTMENT",
            entity="InventoryMovement",
            entity_id=movement_id,
            previous_value={
                "quantity": previous_quantity
            },
            new_value={
                "quantity": new_quantity
            },
            description=reason,
        )

    # =====================================================
    # BATCH CREATION
    # =====================================================

    def log_batch_creation(
        self,
        user_id: int,
        batch_id: int,
        new_value: dict[str, Any],
    ):

        return self.create_log(
            user_id=user_id,
            action="BATCH_CREATE",
            entity="ProductionBatch",
            entity_id=batch_id,
            new_value=new_value,
            description=(
                "Production batch created"
            ),
        )

    # =====================================================
    # QUALITY INSPECTION
    # =====================================================

    def log_quality_inspection(
        self,
        user_id: int,
        inspection_id: int,
        new_value: dict[str, Any],
    ):

        return self.create_log(
            user_id=user_id,
            action="QUALITY_INSPECTION",
            entity="QualityInspection",
            entity_id=inspection_id,
            new_value=new_value,
            description=(
                "Quality inspection recorded"
            ),
        )

    # =====================================================
    # DEFECT CREATION
    # =====================================================

    def log_defect_creation(
        self,
        user_id: int,
        defect_id: int,
        new_value: dict[str, Any],
    ):

        return self.create_log(
            user_id=user_id,
            action="DEFECT_CREATE",
            entity="Defect",
            entity_id=defect_id,
            new_value=new_value,
            description="Defect created",
        )

    # =====================================================
    # MAINTENANCE
    # =====================================================

    def log_maintenance(
        self,
        user_id: int,
        maintenance_id: int,
        new_value: dict[str, Any],
    ):

        return self.create_log(
            user_id=user_id,
            action="MAINTENANCE",
            entity="Maintenance",
            entity_id=maintenance_id,
            new_value=new_value,
            description="Maintenance record created",
        )