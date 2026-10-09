from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.shift_model import Shift
from models.shift_worker_model import ShiftWorker
from models.shift_machine_usage_model import ShiftMachineUsage
from models.shift_production_output_model import ShiftProductionOutput


class ShiftRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------
    # SHIFT
    # -----------------------------------------

    def create(self, shift: Shift):

        self.db.add(shift)

        self.db.commit()

        self.db.refresh(shift)

        return shift

    def get_by_id(self, shift_id: int):

        return (
            self.db.query(Shift)
            .filter(Shift.id == shift_id)
            .first()
        )

    def get_by_code(self, shift_code: str):

        return (
            self.db.query(Shift)
            .filter(Shift.shift_code == shift_code)
            .first()
        )

    def get_list(
        self,
        search=None,
        shift_type=None,
        status=None,
        plant_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(Shift)

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                or_(
                    Shift.shift_code.ilike(pattern),
                    Shift.shift_name.ilike(pattern)
                )
            )

        if shift_type:
            query = query.filter(
                Shift.shift_type == shift_type
            )

        if status:
            query = query.filter(
                Shift.status == status
            )

        if plant_id:
            query = query.filter(
                Shift.plant_id == plant_id
            )

        total = query.count()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(Shift.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def update(self, shift: Shift):

        self.db.commit()

        self.db.refresh(shift)

        return shift

    def delete(self, shift: Shift):

        self.db.delete(shift)

        self.db.commit()

    # -----------------------------------------
    # WORKER
    # -----------------------------------------

    def create_worker_assignment(
        self,
        assignment: ShiftWorker
    ):

        self.db.add(assignment)

        self.db.commit()

        self.db.refresh(assignment)

        return assignment

    def get_worker_assignment(
        self,
        shift_id: int,
        worker_id: int,
        work_date
    ):

        return (
            self.db.query(ShiftWorker)
            .filter(
                ShiftWorker.shift_id == shift_id,
                ShiftWorker.worker_id == worker_id,
                ShiftWorker.work_date == work_date
            )
            .first()
        )

    def get_shift_workers(
        self,
        shift_id: int
    ):

        return (
            self.db.query(ShiftWorker)
            .filter(
                ShiftWorker.shift_id == shift_id,
                ShiftWorker.is_active == True
            )
            .all()
        )

    def get_worker_count(
        self,
        shift_id: int
    ):

        return (
            self.db.query(ShiftWorker)
            .filter(
                ShiftWorker.shift_id == shift_id,
                ShiftWorker.is_active == True
            )
            .count()
        )

    # -----------------------------------------
    # MACHINE
    # -----------------------------------------

    def create_machine_usage(
        self,
        usage: ShiftMachineUsage
    ):

        self.db.add(usage)

        self.db.commit()

        self.db.refresh(usage)

        return usage

    def get_machine_usages(
        self,
        shift_id: int
    ):

        return (
            self.db.query(ShiftMachineUsage)
            .filter(
                ShiftMachineUsage.shift_id == shift_id
            )
            .all()
        )

    # -----------------------------------------
    # PRODUCTION OUTPUT
    # -----------------------------------------

    def create_production_output(
        self,
        output: ShiftProductionOutput
    ):

        self.db.add(output)

        self.db.commit()

        self.db.refresh(output)

        return output

    def get_production_outputs(
        self,
        shift_id: int
    ):

        return (
            self.db.query(ShiftProductionOutput)
            .filter(
                ShiftProductionOutput.shift_id == shift_id
            )
            .all()
        )