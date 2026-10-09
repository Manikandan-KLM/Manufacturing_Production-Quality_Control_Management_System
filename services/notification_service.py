from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.notification_model import Notification
from repositories.notification_repository import (
    NotificationRepository,
)


class NotificationService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)

    # --------------------------------------------------
    # CREATE NOTIFICATION
    # --------------------------------------------------

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        severity: str = "Medium",
        entity: str | None = None,
        entity_id: int | str | None = None,
    ) -> Notification:

        allowed_severities = {
            "Low",
            "Medium",
            "High",
            "Critical",
        }

        if severity not in allowed_severities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification severity",
            )

        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            severity=severity,
            entity=entity,
            entity_id=(
                str(entity_id)
                if entity_id is not None
                else None
            ),
        )

        return self.repository.create(notification)

    # --------------------------------------------------
    # GET MY NOTIFICATIONS
    # --------------------------------------------------

    def get_my_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ):
        return self.repository.get_user_notifications(
            user_id=user_id,
            skip=skip,
            limit=limit,
            unread_only=unread_only,
        )

    # --------------------------------------------------
    # UNREAD COUNT
    # --------------------------------------------------

    def get_unread_count(
        self,
        user_id: int,
    ) -> int:
        return self.repository.count_unread(user_id)

    # --------------------------------------------------
    # MARK ONE AS READ
    # --------------------------------------------------

    def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:

        notification = self.repository.get_by_id(
            notification_id
        )

        if notification is None or notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if not notification.is_read:
            self.repository.mark_as_read(notification)

        return notification

    # --------------------------------------------------
    # MARK ALL AS READ
    # --------------------------------------------------

    def mark_all_as_read(
        self,
        user_id: int,
    ) -> int:
        return self.repository.mark_all_as_read(user_id)

    # --------------------------------------------------
    # 1. LOW RAW MATERIAL STOCK
    # --------------------------------------------------

    def notify_low_stock(
        self,
        user_id: int,
        material_id: int,
        material_name: str,
        available_quantity: float,
        minimum_stock: float,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="LOW_STOCK",
            title="Low Raw Material Stock",
            message=(
                f"{material_name} stock is low. "
                f"Available: {available_quantity}; "
                f"minimum required: {minimum_stock}."
            ),
            severity="High",
            entity="Material",
            entity_id=material_id,
        )

    # --------------------------------------------------
    # 2. PRODUCTION ORDER DEADLINE
    # --------------------------------------------------

    def notify_order_deadline(
        self,
        user_id: int,
        order_id: int,
        order_number: str,
        deadline_message: str,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="ORDER_DEADLINE",
            title="Production Order Deadline",
            message=(
                f"Production order {order_number}: "
                f"{deadline_message}"
            ),
            severity="High",
            entity="ProductionOrder",
            entity_id=order_id,
        )

    # --------------------------------------------------
    # 3. MACHINE BREAKDOWN
    # --------------------------------------------------

    def notify_machine_breakdown(
        self,
        user_id: int,
        machine_id: int,
        machine_name: str,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="MACHINE_BREAKDOWN",
            title="Machine Breakdown",
            message=(
                f"Machine {machine_name} has reported "
                "a breakdown. Please investigate."
            ),
            severity="Critical",
            entity="Machine",
            entity_id=machine_id,
        )

    # --------------------------------------------------
    # 4. MAINTENANCE DUE
    # --------------------------------------------------

    def notify_maintenance_due(
        self,
        user_id: int,
        machine_id: int,
        machine_name: str,
        due_date: str,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="MAINTENANCE_DUE",
            title="Maintenance Due",
            message=(
                f"Maintenance for {machine_name} is due "
                f"on {due_date}."
            ),
            severity="High",
            entity="Machine",
            entity_id=machine_id,
        )

    # --------------------------------------------------
    # 5. CRITICAL QUALITY DEFECT
    # --------------------------------------------------

    def notify_critical_defect(
        self,
        user_id: int,
        defect_id: int,
        defect_number: str,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="CRITICAL_DEFECT",
            title="Critical Quality Defect",
            message=(
                f"Critical defect {defect_number} "
                "requires immediate investigation."
            ),
            severity="Critical",
            entity="Defect",
            entity_id=defect_id,
        )

    # --------------------------------------------------
    # 6. HIGH REJECTION RATE
    # --------------------------------------------------

    def notify_high_rejection_rate(
        self,
        user_id: int,
        batch_id: int,
        batch_number: str,
        rejection_rate: float,
        threshold: float = 5.0,
    ):
        if rejection_rate <= threshold:
            return None

        return self.create_notification(
            user_id=user_id,
            notification_type="HIGH_REJECTION_RATE",
            title="High Rejection Rate",
            message=(
                f"Batch {batch_number} has a rejection rate "
                f"of {rejection_rate:.2f}%, exceeding "
                f"the {threshold:.2f}% threshold."
            ),
            severity="High",
            entity="ProductionBatch",
            entity_id=batch_id,
        )

    # --------------------------------------------------
    # 7. PRODUCTION DELAY
    # --------------------------------------------------

    def notify_production_delay(
        self,
        user_id: int,
        order_id: int,
        order_number: str,
        delay_message: str,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="PRODUCTION_DELAY",
            title="Production Delay",
            message=(
                f"Production order {order_number}: "
                f"{delay_message}"
            ),
            severity="High",
            entity="ProductionOrder",
            entity_id=order_id,
        )

    # --------------------------------------------------
    # 8. APPROVAL PENDING
    # --------------------------------------------------

    def notify_approval_pending(
        self,
        user_id: int,
        order_id: int,
        order_number: str,
    ):
        return self.create_notification(
            user_id=user_id,
            notification_type="APPROVAL_PENDING",
            title="Production Approval Pending",
            message=(
                f"Production order {order_number} "
                "is waiting for approval."
            ),
            severity="Medium",
            entity="ProductionOrder",
            entity_id=order_id,
        )