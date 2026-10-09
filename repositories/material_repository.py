from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from models.material_model import Material
from models.material_history_model import MaterialHistory


class MaterialRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------
    # MATERIAL
    # -----------------------------------------

    def create(self, material: Material):

        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        return material

    def get_by_id(self, material_id: int):

        return (
            self.db.query(Material)
            .filter(Material.id == material_id)
            .first()
        )

    def get_by_code(self, material_code: str):

        return (
            self.db.query(Material)
            .filter(Material.material_code == material_code)
            .first()
        )

    def get_list(
        self,
        search: str | None = None,
        category: str | None = None,
        status: str | None = None,
        unit: str | None = None,
        low_stock: bool = False,
        page: int = 1,
        page_size: int = 10
    ):

        query = self.db.query(Material)

        if search:

            search_pattern = f"%{search}%"

            query = query.filter(
                or_(
                    Material.material_name.ilike(search_pattern),
                    Material.material_code.ilike(search_pattern),
                    Material.supplier_reference.ilike(search_pattern)
                )
            )

        if category:
            query = query.filter(
                Material.category == category
            )

        if status:
            query = query.filter(
                Material.status == status
            )

        if unit:
            query = query.filter(
                Material.unit == unit
            )

        if low_stock:

            query = query.filter(
                Material.available_quantity
                <= Material.reorder_level
            )

        total = query.count()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(Material.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def update(self, material: Material):

        self.db.commit()
        self.db.refresh(material)

        return material

    def delete(self, material: Material):

        self.db.delete(material)
        self.db.commit()

    # -----------------------------------------
    # HISTORY
    # -----------------------------------------

    def create_history(
        self,
        history: MaterialHistory
    ):

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        return history

    def get_history(
        self,
        material_id: int
    ):

        return (
            self.db.query(MaterialHistory)
            .filter(
                MaterialHistory.material_id == material_id
            )
            .order_by(
                MaterialHistory.id.desc()
            )
            .all()
        )