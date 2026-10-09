from sqlalchemy.orm import Session

from models.production_line_model import ProductionLine


class ProductionLineRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------
    # CREATE
    # -----------------------------------------

    def create(self, line: ProductionLine):

        self.db.add(line)
        self.db.commit()
        self.db.refresh(line)

        return line

    # -----------------------------------------
    # GET BY ID
    # -----------------------------------------

    def get_by_id(self, line_id: int):

        return (
            self.db.query(ProductionLine)
            .filter(
                ProductionLine.id == line_id
            )
            .first()
        )

    # -----------------------------------------
    # GET BY CODE
    # -----------------------------------------

    def get_by_code(self, line_code: str):

        return (
            self.db.query(ProductionLine)
            .filter(
                ProductionLine.line_code == line_code
            )
            .first()
        )

    # -----------------------------------------
    # GET LIST
    # -----------------------------------------

    def get_list(
        self,
        search: str | None = None,
        status: str | None = None,
        plant_id: int | None = None,
        page: int = 1,
        page_size: int = 10
    ):

        query = self.db.query(ProductionLine)

        # Search
        if search:

            search_value = f"%{search}%"

            query = query.filter(
                ProductionLine.line_name.ilike(
                    search_value
                )
                |
                ProductionLine.line_code.ilike(
                    search_value
                )
            )

        # Status filter
        if status:

            query = query.filter(
                ProductionLine.status == status
            )

        # Plant filter
        if plant_id:

            query = query.filter(
                ProductionLine.plant_id == plant_id
            )

        # Total
        total = query.count()

        # Pagination
        offset = (page - 1) * page_size

        items = (
            query
            .order_by(
                ProductionLine.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    # -----------------------------------------
    # UPDATE
    # -----------------------------------------

    def update(self, line: ProductionLine):

        self.db.commit()
        self.db.refresh(line)

        return line

    # -----------------------------------------
    # DELETE
    # -----------------------------------------

    def delete(self, line: ProductionLine):

        self.db.delete(line)
        self.db.commit()