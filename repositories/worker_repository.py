from sqlalchemy.orm import Session

from models.worker_model import Worker
from models.worker_batch_assignment_model import (
    WorkerBatchAssignment
)


class WorkerRepository:

    def __init__(self, db: Session):

        self.db = db

    # =========================================
    # WORKER CREATE
    # =========================================

    def create(
        self,
        worker: Worker
    ):

        self.db.add(worker)

        self.db.commit()

        self.db.refresh(worker)

        return worker

    # =========================================
    # GET WORKER
    # =========================================

    def get_by_id(
        self,
        worker_id: int
    ):

        return (
            self.db.query(Worker)
            .filter(
                Worker.id == worker_id
            )
            .first()
        )

    # =========================================
    # GET EMPLOYEE CODE
    # =========================================

    def get_by_employee_code(
        self,
        employee_code: str
    ):

        return (
            self.db.query(Worker)
            .filter(
                Worker.employee_code
                == employee_code
            )
            .first()
        )

    # =========================================
    # LIST
    # =========================================

    def get_list(
        self,
        search=None,
        department=None,
        shift=None,
        status=None,
        production_line_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(Worker)

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                Worker.employee_code.ilike(pattern)
                |
                Worker.full_name.ilike(pattern)
                |
                Worker.skill.ilike(pattern)
            )

        if department:

            query = query.filter(
                Worker.department == department
            )

        if shift:

            query = query.filter(
                Worker.shift == shift
            )

        if status:

            query = query.filter(
                Worker.status == status
            )

        if production_line_id:

            query = query.filter(
                Worker.production_line_id
                == production_line_id
            )

        total = query.count()

        offset = (
            (page - 1) * page_size
        )

        items = (
            query
            .order_by(
                Worker.id.desc()
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
        worker: Worker
    ):

        self.db.commit()

        self.db.refresh(worker)

        return worker

    # =========================================
    # DELETE
    # =========================================

    def delete(
        self,
        worker: Worker
    ):

        self.db.delete(worker)

        self.db.commit()

    # =========================================
    # ASSIGNMENT
    # =========================================

    def create_assignment(
        self,
        assignment: WorkerBatchAssignment
    ):

        self.db.add(assignment)

        self.db.commit()

        self.db.refresh(assignment)

        return assignment

    # =========================================
    # EXISTING ASSIGNMENT
    # =========================================

    def get_assignment(
        self,
        worker_id: int,
        production_batch_id: int
    ):

        return (
            self.db.query(
                WorkerBatchAssignment
            )
            .filter(
                WorkerBatchAssignment.worker_id
                == worker_id,
                WorkerBatchAssignment.production_batch_id
                == production_batch_id
            )
            .first()
        )

    # =========================================
    # ACTIVE ASSIGNMENT
    # =========================================

    def get_active_assignment(
        self,
        worker_id: int,
        production_batch_id: int
    ):

        return (
            self.db.query(
                WorkerBatchAssignment
            )
            .filter(
                WorkerBatchAssignment.worker_id
                == worker_id,

                WorkerBatchAssignment.production_batch_id
                == production_batch_id,

                WorkerBatchAssignment.is_active
                == True
            )
            .first()
        )

    # =========================================
    # WORKER ASSIGNMENTS
    # =========================================

    def get_worker_assignments(
        self,
        worker_id: int
    ):

        return (
            self.db.query(
                WorkerBatchAssignment
            )
            .filter(
                WorkerBatchAssignment.worker_id
                == worker_id
            )
            .order_by(
                WorkerBatchAssignment.id.desc()
            )
            .all()
        )

    # =========================================
    # BATCH ASSIGNMENTS
    # =========================================

    def get_batch_assignments(
        self,
        production_batch_id: int
    ):

        return (
            self.db.query(
                WorkerBatchAssignment
            )
            .filter(
                WorkerBatchAssignment
                .production_batch_id
                == production_batch_id
            )
            .order_by(
                WorkerBatchAssignment.id.desc()
            )
            .all()
        )