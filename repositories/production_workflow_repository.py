from sqlalchemy.orm import Session

from models.production_workflow_model import (
    ProductionWorkflowHistory
)


class ProductionWorkflowRepository:

    @staticmethod
    def create(
        db: Session,
        production_order_id: int,
        from_status: str | None,
        to_status: str,
        action: str,
        performed_by: int,
        remarks: str | None = None
    ):

        history = ProductionWorkflowHistory(
            production_order_id=production_order_id,
            from_status=from_status,
            to_status=to_status,
            action=action,
            performed_by=performed_by,
            remarks=remarks
        )

        db.add(history)
        db.flush()

        return history

    @staticmethod
    def get_by_order(
        db: Session,
        production_order_id: int
    ):

        return (
            db.query(ProductionWorkflowHistory)
            .filter(
                ProductionWorkflowHistory.production_order_id
                == production_order_id
            )
            .order_by(
                ProductionWorkflowHistory.created_at.asc()
            )
            .all()
        )