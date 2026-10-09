from sqlalchemy.orm import Session

from models.bom_model import BOM
from models.bom_item_model import BOMItem


class BOMRepository:

    def __init__(self, db: Session):

        self.db = db

    # =========================================
    # BOM
    # =========================================

    def create_bom(
        self,
        bom: BOM
    ):

        self.db.add(bom)
        self.db.commit()
        self.db.refresh(bom)

        return bom

    def get_by_id(
        self,
        bom_id: int
    ):

        return (
            self.db.query(BOM)
            .filter(BOM.id == bom_id)
            .first()
        )

    def get_by_product_version(
        self,
        product_id: int,
        version: str
    ):

        return (
            self.db.query(BOM)
            .filter(
                BOM.product_id == product_id,
                BOM.version == version
            )
            .first()
        )

    def get_active_by_product(
        self,
        product_id: int
    ):

        return (
            self.db.query(BOM)
            .filter(
                BOM.product_id == product_id,
                BOM.status == "Active"
            )
            .first()
        )

    def get_product_boms(
        self,
        product_id: int
    ):

        return (
            self.db.query(BOM)
            .filter(
                BOM.product_id == product_id
            )
            .order_by(
                BOM.id.desc()
            )
            .all()
        )

    def get_all(
        self,
        product_id=None,
        status=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(BOM)

        if product_id:

            query = query.filter(
                BOM.product_id == product_id
            )

        if status:

            query = query.filter(
                BOM.status == status
            )

        total = query.count()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(BOM.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def update_bom(
        self,
        bom: BOM
    ):

        self.db.commit()
        self.db.refresh(bom)

        return bom

    def delete_bom(
        self,
        bom: BOM
    ):

        self.db.delete(bom)
        self.db.commit()

    # =========================================
    # BOM ITEMS
    # =========================================

    def create_item(
        self,
        item: BOMItem
    ):

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def get_item(
        self,
        bom_id: int,
        material_id: int
    ):

        return (
            self.db.query(BOMItem)
            .filter(
                BOMItem.bom_id == bom_id,
                BOMItem.material_id == material_id
            )
            .first()
        )

    def get_item_by_id(
        self,
        item_id: int
    ):

        return (
            self.db.query(BOMItem)
            .filter(
                BOMItem.id == item_id
            )
            .first()
        )

    def get_items(
        self,
        bom_id: int
    ):

        return (
            self.db.query(BOMItem)
            .filter(
                BOMItem.bom_id == bom_id
            )
            .order_by(
                BOMItem.id.asc()
            )
            .all()
        )

    def update_item(
        self,
        item: BOMItem
    ):

        self.db.commit()
        self.db.refresh(item)

        return item

    def delete_item(
        self,
        item: BOMItem
    ):

        self.db.delete(item)
        self.db.commit()