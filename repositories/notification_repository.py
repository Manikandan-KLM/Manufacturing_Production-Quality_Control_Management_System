from datetime import datetime

from sqlalchemy.orm import Session

from models.notification_model import Notification


class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def get_by_id(
        self,
        notification_id: int,
    ) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id
            )
            .first()
        )

    def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ):
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )

        if unread_only:
            query = query.filter(
                Notification.is_read.is_(False)
            )

        return (
            query
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_unread(
        self,
        user_id: int,
    ) -> int:
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .count()
        )

    def mark_as_read(
        self,
        notification: Notification,
    ) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()

        self.db.flush()
        self.db.refresh(notification)

        return notification

    def mark_all_as_read(
        self,
        user_id: int,
    ) -> int:
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .update(
                {
                    Notification.is_read: True,
                    Notification.read_at: datetime.utcnow(),
                },
                synchronize_session=False,
            )
        )