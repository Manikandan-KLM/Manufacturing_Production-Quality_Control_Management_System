from sqlalchemy.orm import Session

from models.product_model import Product


class ProductRepository:

    def __init__(self, db: Session):

        self.db = db

    # =========================================
    # CREATE
    # =========================================

    def create(
        self,
        product: Product
    ):

        self.db.add(product)

        self.db.commit()

        self.db.refresh(product)

        return product

    # =========================================
    # GET BY ID
    # =========================================

    def get_by_id(
        self,
        product_id: int
    ):

        return (
            self.db.query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )

    # =========================================
    # GET BY PRODUCT CODE
    # =========================================

    def get_by_product_code(
        self,
        product_code: str
    ):

        return (
            self.db.query(Product)
            .filter(
                Product.product_code == product_code
            )
            .first()
        )

    # =========================================
    # GET BY SKU
    # =========================================

    def get_by_sku(
        self,
        sku: str
    ):

        return (
            self.db.query(Product)
            .filter(
                Product.sku == sku
            )
            .first()
        )

    # =========================================
    # LIST
    # =========================================

    def get_list(
        self,
        search: str | None = None,
        category: str | None = None,
        status: str | None = None,
        unit: str | None = None,
        page: int = 1,
        page_size: int = 10
    ):

        query = self.db.query(Product)

        # -------------------------------------
        # SEARCH
        # -------------------------------------

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                Product.product_name.ilike(
                    search_value
                )
                |
                Product.product_code.ilike(
                    search_value
                )
                |
                Product.sku.ilike(
                    search_value
                )
            )

        # -------------------------------------
        # CATEGORY FILTER
        # -------------------------------------

        if category:

            query = query.filter(
                Product.category == category
            )

        # -------------------------------------
        # STATUS FILTER
        # -------------------------------------

        if status:

            query = query.filter(
                Product.status == status
            )

        # -------------------------------------
        # UNIT FILTER
        # -------------------------------------

        if unit:

            query = query.filter(
                Product.unit_of_measurement == unit
            )

        # -------------------------------------
        # TOTAL
        # -------------------------------------

        total = query.count()

        # -------------------------------------
        # PAGINATION
        # -------------------------------------

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(
                Product.id.desc()
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
        product: Product
    ):

        self.db.commit()

        self.db.refresh(product)

        return product

    # =========================================
    # DELETE
    # =========================================

    def delete(
        self,
        product: Product
    ):

        self.db.delete(product)

        self.db.commit()