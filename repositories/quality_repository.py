from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.quality_inspection_model import QualityInspection
from models.quality_parameter_model import QualityParameter


class QualityRepository:

    def __init__(self, db: Session):

        self.db = db

    # =========================================
    # INSPECTION
    # =========================================

    def create_inspection(
        self,
        inspection: QualityInspection
    ):

        self.db.add(inspection)

        self.db.commit()

        self.db.refresh(inspection)

        return inspection

    def get_inspection_by_id(
        self,
        inspection_id: int
    ):

        return (
            self.db.query(QualityInspection)
            .filter(
                QualityInspection.id == inspection_id
            )
            .first()
        )

    def get_by_number(
        self,
        inspection_number: str
    ):

        return (
            self.db.query(QualityInspection)
            .filter(
                QualityInspection.inspection_number
                == inspection_number
            )
            .first()
        )

    def get_inspection_list(
        self,
        inspection_type=None,
        overall_result=None,
        production_batch_id=None,
        inspector_id=None,
        page=1,
        page_size=10
    ):

        query = self.db.query(
            QualityInspection
        )

        if inspection_type:

            query = query.filter(
                QualityInspection.inspection_type
                == inspection_type
            )

        if overall_result:

            query = query.filter(
                QualityInspection.overall_result
                == overall_result
            )

        if production_batch_id:

            query = query.filter(
                QualityInspection.production_batch_id
                == production_batch_id
            )

        if inspector_id:

            query = query.filter(
                QualityInspection.inspector_id
                == inspector_id
            )

        total = query.count()

        offset = (
            page - 1
        ) * page_size

        items = (
            query
            .order_by(
                QualityInspection.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def update_inspection(
        self,
        inspection: QualityInspection
    ):

        self.db.commit()

        self.db.refresh(inspection)

        return inspection

    # =========================================
    # PARAMETERS
    # =========================================

    def create_parameter(
        self,
        parameter: QualityParameter
    ):

        self.db.add(parameter)

        self.db.commit()

        self.db.refresh(parameter)

        return parameter

    def get_parameter_by_id(
        self,
        parameter_id: int
    ):

        return (
            self.db.query(QualityParameter)
            .filter(
                QualityParameter.id
                == parameter_id
            )
            .first()
        )

    def get_parameters(
        self,
        inspection_id: int
    ):

        return (
            self.db.query(QualityParameter)
            .filter(
                QualityParameter.inspection_id
                == inspection_id
            )
            .order_by(
                QualityParameter.id.asc()
            )
            .all()
        )

    def update_parameter(
        self,
        parameter: QualityParameter
    ):

        self.db.commit()

        self.db.refresh(parameter)

        return parameter

    def delete_parameter(
        self,
        parameter: QualityParameter
    ):

        self.db.delete(parameter)

        self.db.commit()