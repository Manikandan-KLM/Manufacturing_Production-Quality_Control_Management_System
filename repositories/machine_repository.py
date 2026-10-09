from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.machine_model import Machine


class MachineRepository:

    def __init__(
        self,
        db: Session
    ):

        self.db = db

    # =========================================
    # CREATE
    # =========================================

    def create(
        self,
        machine: Machine
    ):

        self.db.add(machine)

        self.db.commit()

        self.db.refresh(machine)

        return machine

    # =========================================
    # GET BY ID
    # =========================================

    def get_by_id(
        self,
        machine_id: int
    ):

        return (
            self.db.query(Machine)
            .filter(
                Machine.id == machine_id
            )
            .first()
        )

    # =========================================
    # GET BY CODE
    # =========================================

    def get_by_code(
        self,
        machine_code: str
    ):

        return (
            self.db.query(Machine)
            .filter(
                Machine.machine_code
                == machine_code
            )
            .first()
        )

    # =========================================
    # LIST
    # =========================================

    def get_list(
        self,
        search=None,
        machine_type=None,
        status=None,
        production_line_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(Machine)

        # Search
        if search:

            search_pattern = (
                f"%{search}%"
            )

            query = query.filter(
                or_(
                    Machine.machine_code.ilike(
                        search_pattern
                    ),
                    Machine.machine_name.ilike(
                        search_pattern
                    ),
                    Machine.machine_type.ilike(
                        search_pattern
                    )
                )
            )

        # Machine type
        if machine_type:

            query = query.filter(
                Machine.machine_type
                == machine_type
            )

        # Status
        if status:

            query = query.filter(
                Machine.status
                == status
            )

        # Production line
        if production_line_id:

            query = query.filter(
                Machine.production_line_id
                == production_line_id
            )

        total = query.count()

        offset = (
            (page - 1)
            * page_size
        )

        items = (
            query
            .order_by(
                Machine.id.desc()
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
        machine: Machine
    ):

        self.db.commit()

        self.db.refresh(machine)

        return machine

    # =========================================
    # DELETE
    # =========================================

    def delete(
        self,
        machine: Machine
    ):

        self.db.delete(machine)

        self.db.commit()