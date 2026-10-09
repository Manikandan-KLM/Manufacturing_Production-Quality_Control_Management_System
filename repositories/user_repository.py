from sqlalchemy.orm import Session

from models.user_model import User


class UserRepository:

    def __init__(self, db: Session):

        self.db = db

    def get_by_id(
        self,
        user_id: int
    ):

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(
        self,
        email: str
    ):

        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def create(
        self,
        user: User
    ):

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user

    def update(
        self,
        user: User
    ):

        self.db.commit()

        self.db.refresh(user)

        return user