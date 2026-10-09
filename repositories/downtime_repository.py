from sqlalchemy import func

from sqlalchemy.orm import Session

from models.downtime_model import Downtime


class DowntimeRepository:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        downtime: Downtime
    ):

        self.db.add(downtime)

        self.db.commit()

        self.db.refresh(downtime)

        return downtime

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        downtime_id: int
    ):

        return (
            self.db.query(Downtime)
            .filter(
                Downtime.id == downtime_id
            )
            .first()
        )

    # =====================================================
    # GET BY NUMBER
    # =====================================================

    def get_by_number(
        self,
        downtime_number: str
    ):

        return (
            self.db.query(Downtime)
            .filter(
                Downtime.downtime_number
                == downtime_number
            )
            .first()
        )

    # =====================================================
    # GET LIST
    # =====================================================

    def get_list(
        self,
        machine_id=None,
        production_line_id=None,
        category=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(Downtime)

        if machine_id:

            query = query.filter(
                Downtime.machine_id == machine_id
            )

        if production_line_id:

            query = query.filter(
                Downtime.production_line_id
                == production_line_id
            )

        if category:

            query = query.filter(
                Downtime.category == category
            )

        total = query.count()

        offset = (
            page - 1
        ) * page_size

        items = (
            query
            .order_by(
                Downtime.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        downtime: Downtime
    ):

        self.db.commit()

        self.db.refresh(downtime)

        return downtime

    # =====================================================
    # GET DOWNTIME MINUTES
    # =====================================================

    def get_total_downtime_minutes(
        self,
        machine_id: int,
        start_date,
        end_date
    ):

        result = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        Downtime.duration_minutes
                    ),
                    0
                )
            )
            .filter(
                Downtime.machine_id == machine_id,
                Downtime.start_time >= start_date,
                Downtime.start_time <= end_date,
                Downtime.end_time.isnot(None)
            )
            .scalar()
        )

        return float(result or 0)