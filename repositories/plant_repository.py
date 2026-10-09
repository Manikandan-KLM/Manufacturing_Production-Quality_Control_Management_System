from sqlalchemy.orm import Session

from models.plant_model import Plant


class PlantRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, plant: Plant):
        self.db.add(plant)
        self.db.commit()
        self.db.refresh(plant)

        return plant

    def get_by_id(self, plant_id: int):
        return (
            self.db.query(Plant)
            .filter(Plant.id == plant_id)
            .first()
        )

    def get_by_code(self, plant_code: str):
        return (
            self.db.query(Plant)
            .filter(Plant.plant_code == plant_code)
            .first()
        )

    def get_all(self):
        return (
            self.db.query(Plant)
            .order_by(Plant.id.desc())
            .all()
        )

    def update(self, plant: Plant):
        self.db.commit()
        self.db.refresh(plant)

        return plant

    def delete(self, plant: Plant):
        self.db.delete(plant)
        self.db.commit()