from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.defect_model import Defect


class DefectRepository:

    def __init__(self, db: Session):

        self.db = db

    # =========================================
    # CREATE
    # =========================================

    def create(
        self,
        defect: Defect
    ):

        self.db.add(defect)

        self.db.commit()

        self.db.refresh(defect)

        return defect

    # =========================================
    # GET BY ID
    # =========================================

    def get_by_id(
        self,
        defect_id: int
    ):

        return (
            self.db.query(Defect)
            .filter(
                Defect.id == defect_id
            )
            .first()
        )

    # =========================================
    # GET BY NUMBER
    # =========================================

    def get_by_number(
        self,
        defect_number: str
    ):

        return (
            self.db.query(Defect)
            .filter(
                Defect.defect_number
                == defect_number
            )
            .first()
        )

    # =========================================
    # LIST
    # =========================================

    def get_list(
        self,
        search=None,
        defect_type=None,
        severity=None,
        resolution_status=None,
        production_batch_id=None,
        product_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(Defect)

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                or_(
                    Defect.defect_number.ilike(
                        pattern
                    ),
                    Defect.defect_type.ilike(
                        pattern
                    ),
                    Defect.root_cause.ilike(
                        pattern
                    )
                )
            )

        if defect_type:

            query = query.filter(
                Defect.defect_type
                == defect_type
            )

        if severity:

            query = query.filter(
                Defect.severity
                == severity
            )

        if resolution_status:

            query = query.filter(
                Defect.resolution_status
                == resolution_status
            )

        if production_batch_id:

            query = query.filter(
                Defect.production_batch_id
                == production_batch_id
            )

        if product_id:

            query = query.filter(
                Defect.product_id
                == product_id
            )

        total = query.count()

        offset = (
            page - 1
        ) * page_size

        items = (
            query
            .order_by(
                Defect.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    # =========================================
    # UPDATE
    # =========================================

    def update(
        self,
        defect: Defect
    ):

        self.db.commit()

        self.db.refresh(defect)

        return defect