from sqlalchemy.orm import Session

from models.audit_log_model import AuditLog


class AuditLogRepository:

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:

        self.db.add(audit_log)

        self.db.flush()

        self.db.refresh(audit_log)

        return audit_log

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        audit_log_id: int,
    ):

        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.id == audit_log_id
            )
            .first()
        )

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ):

        return (
            self.db.query(AuditLog)
            .order_by(
                AuditLog.timestamp.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # =====================================================
    # FILTER BY USER
    # =====================================================

    def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ):

        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.user_id == user_id
            )
            .order_by(
                AuditLog.timestamp.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # =====================================================
    # FILTER BY ENTITY
    # =====================================================

    def get_by_entity(
        self,
        entity: str,
        entity_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ):

        query = (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity == entity
            )
        )

        if entity_id:
            query = query.filter(
                AuditLog.entity_id == entity_id
            )

        return (
            query
            .order_by(
                AuditLog.timestamp.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )