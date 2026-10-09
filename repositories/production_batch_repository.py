from sqlalchemy.orm import Session

from models.production_batch_model import ProductionBatch


class ProductionBatchRepository:

    def __init__(self, db: Session):

        self.db = db

    # -----------------------------------------
    # CREATE
    # -----------------------------------------

    def create(
        self,
        batch: ProductionBatch
    ):

        self.db.add(batch)

        self.db.commit()

        self.db.refresh(batch)

        return batch

    # -----------------------------------------
    # GET BY ID
    # -----------------------------------------

    def get_by_id(
        self,
        batch_id: int
    ):

        return (
            self.db.query(ProductionBatch)
            .filter(
                ProductionBatch.id == batch_id
            )
            .first()
        )

    # -----------------------------------------
    # GET BY BATCH NUMBER
    # -----------------------------------------

    def get_by_batch_number(
        self,
        batch_number: str
    ):

        return (
            self.db.query(ProductionBatch)
            .filter(
                ProductionBatch.batch_number
                == batch_number
            )
            .first()
        )

    # -----------------------------------------
    # LIST
    # -----------------------------------------

    def get_list(
        self,
        production_order_id=None,
        production_line_id=None,
        machine_id=None,
        supervisor_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(
            ProductionBatch
        )

        if production_order_id:

            query = query.filter(
                ProductionBatch.production_order_id
                == production_order_id
            )

        if production_line_id:

            query = query.filter(
                ProductionBatch.production_line_id
                == production_line_id
            )

        if machine_id:

            query = query.filter(
                ProductionBatch.machine_id
                == machine_id
            )

        if supervisor_id:

            query = query.filter(
                ProductionBatch.supervisor_id
                == supervisor_id
            )

        total = query.count()

        offset = (
            (page - 1) * page_size
        )

        items = (
            query
            .order_by(
                ProductionBatch.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    # -----------------------------------------
    # UPDATE
    # -----------------------------------------

    def update(
        self,
        batch: ProductionBatch
    ):

        self.db.commit()

        self.db.refresh(batch)

        return batch

    # -----------------------------------------
    # DELETE
    # -----------------------------------------

    def delete(
        self,
        batch: ProductionBatch
    ):

        self.db.delete(batch)

        self.db.commit()