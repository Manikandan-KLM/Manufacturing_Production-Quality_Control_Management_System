from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from db.database import get_db
from models.user_model import User
from schemas.notification_schema import (
    NotificationResponse,
)
from services.notification_service import (
    NotificationService,
)
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"],
)


# ==================================================
# GET MY NOTIFICATIONS
# ==================================================

@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return service.get_my_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )


# ==================================================
# GET UNREAD COUNT
# ==================================================

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return {
        "unread_count": service.get_unread_count(
            current_user.id
        )
    }


# ==================================================
# MARK ONE AS READ
# ==================================================

@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    notification = service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    db.commit()

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id,
    }


# ==================================================
# MARK ALL AS READ
# ==================================================

@router.patch("/read-all")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    count = service.mark_all_as_read(
        current_user.id
    )

    db.commit()

    return {
        "message": "Notifications marked as read",
        "updated_count": count,
    }