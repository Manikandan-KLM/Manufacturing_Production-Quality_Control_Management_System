from datetime import datetime, timezone

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from models.user_model import User
from models.revoked_token_model import RevokedToken

from repositories.user_repository import UserRepository

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)


ALLOWED_ROLES = {
    "Super Admin",
    "Plant Manager",
    "Production Manager",
    "Quality Manager",
    "Maintenance Engineer",
    "Store Manager"
}


class AuthService:

    def __init__(self, db: Session):

        self.db = db

        self.user_repository = UserRepository(db)

    # -------------------------
    # REGISTER
    # -------------------------

    def register(
        self,
        full_name: str,
        email: str,
        password: str,
        role: str
    ):

        existing_user = (
            self.user_repository.get_by_email(email)
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if role not in ALLOWED_ROLES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )

        # Security:
        # Normal users should not create Super Admin
        # directly through registration.

        if role == "Super Admin":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super Admin cannot be self-registered"
            )

        user = User(
            full_name=full_name,
            email=email.lower(),
            password_hash=hash_password(password),
            role=role,
            is_active=True
        )

        return self.user_repository.create(user)

    # -------------------------
    # LOGIN
    # -------------------------

    def login(
        self,
        email: str,
        password: str
    ):

        user = (
            self.user_repository.get_by_email(
                email.lower()
            )
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(
            password,
            user.password_hash
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        access_token = create_access_token(
            user.id,
            user.role
        )

        refresh_token = create_refresh_token(
            user.id,
            user.role
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    # -------------------------
    # REFRESH TOKEN
    # -------------------------

    def refresh_token(
        self,
        refresh_token: str
    ):

        if self.is_token_revoked(refresh_token):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )

        payload = decode_token(refresh_token)

        if not payload:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        if payload.get("type") != "refresh":

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")

        if not user_id:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = self.user_repository.get_by_id(
            int(user_id)
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        access_token = create_access_token(
            user.id,
            user.role
        )

        new_refresh_token = create_refresh_token(
            user.id,
            user.role
        )

        # Revoke old refresh token
        self.revoke_token(refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    # -------------------------
    # LOGOUT
    # -------------------------

    def logout(
        self,
        refresh_token: str
    ):

        payload = decode_token(refresh_token)

        if not payload:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        ).replace(tzinfo=None)

        token = RevokedToken(
            token=refresh_token,
            expires_at=expires_at
        )

        self.db.add(token)

        self.db.commit()

        return {
            "message": "Logged out successfully"
        }

    # -------------------------
    # REVOKE TOKEN
    # -------------------------

    def revoke_token(
        self,
        token: str
    ):

        payload = decode_token(token)

        if not payload:
            return

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        ).replace(tzinfo=None)

        existing = (
            self.db.query(RevokedToken)
            .filter(
                RevokedToken.token == token
            )
            .first()
        )

        if existing:
            return

        revoked_token = RevokedToken(
            token=token,
            expires_at=expires_at
        )

        self.db.add(revoked_token)

        self.db.commit()

    # -------------------------
    # CHECK REVOKED TOKEN
    # -------------------------

    def is_token_revoked(
        self,
        token: str
    ) -> bool:

        token_record = (
            self.db.query(RevokedToken)
            .filter(
                RevokedToken.token == token
            )
            .first()
        )

        return token_record is not None

    # -------------------------
    # CHANGE PASSWORD
    # -------------------------

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ):

        if not verify_password(
            current_password,
            user.password_hash
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        user.password_hash = hash_password(
            new_password
        )

        self.user_repository.update(user)

        return {
            "message": "Password changed successfully"
        }

    # -------------------------
    # DEACTIVATE USER
    # -------------------------

    def deactivate_user(
        self,
        user_id: int
    ):

        user = self.user_repository.get_by_id(
            user_id
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = False

        self.user_repository.update(user)

        return user

    # -------------------------
    # ACTIVATE USER
    # -------------------------

    def activate_user(
        self,
        user_id: int
    ):

        user = self.user_repository.get_by_id(
            user_id
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = True

        self.user_repository.update(user)

        return user