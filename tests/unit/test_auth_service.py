
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from services.auth_service import AuthService


# --------------------------------------------------
# FIXTURES
# --------------------------------------------------

@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def auth_service(db):
    with patch("services.auth_service.UserRepository") as repo_class:
        service = AuthService(db)
        service.user_repository = repo_class.return_value
        yield service


@pytest.fixture
def active_user():
    return SimpleNamespace(
        id=1,
        full_name="Test User",
        email="test@example.com",
        password_hash="hashed_password",
        role="Plant Manager",
        is_active=True,
    )


@pytest.fixture
def inactive_user():
    return SimpleNamespace(
        id=2,
        full_name="Inactive User",
        email="inactive@example.com",
        password_hash="hashed_password",
        role="Plant Manager",
        is_active=False,
    )


# --------------------------------------------------
# REGISTER TESTS
# --------------------------------------------------

def test_register_success(auth_service, active_user):
    auth_service.user_repository.get_by_email.return_value = None

    with patch(
        "services.auth_service.hash_password",
        return_value="hashed_password",
    ):
        auth_service.user_repository.create.return_value = active_user

        result = auth_service.register(
            full_name="Test User",
            email="test@example.com",
            password="StrongPass123!",
            role="Plant Manager",
        )

    assert result == active_user

    auth_service.user_repository.get_by_email.assert_called_once_with(
        "test@example.com"
    )
    auth_service.user_repository.create.assert_called_once()

    created_user = (
        auth_service.user_repository.create.call_args.args[0]
    )

    assert created_user.full_name == "Test User"
    assert created_user.email == "test@example.com"
    assert created_user.password_hash == "hashed_password"
    assert created_user.role == "Plant Manager"
    assert created_user.is_active is True


def test_register_email_is_normalized(auth_service, active_user):
    auth_service.user_repository.get_by_email.return_value = None
    auth_service.user_repository.create.return_value = active_user

    with patch(
        "services.auth_service.hash_password",
        return_value="hashed_password",
    ):
        auth_service.register(
            full_name="Test User",
            email="TEST@EXAMPLE.COM",
            password="StrongPass123!",
            role="Plant Manager",
        )

    auth_service.user_repository.get_by_email.assert_called_once_with(
        "TEST@EXAMPLE.COM"
    )

    created_user = (
        auth_service.user_repository.create.call_args.args[0]
    )
    assert created_user.email == "test@example.com"


def test_register_duplicate_email(auth_service, active_user):
    auth_service.user_repository.get_by_email.return_value = active_user

    with pytest.raises(HTTPException) as exc:
        auth_service.register(
            "Test User",
            "test@example.com",
            "StrongPass123!",
            "Plant Manager",
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already registered"
    auth_service.user_repository.create.assert_not_called()


def test_register_invalid_role(auth_service):
    auth_service.user_repository.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth_service.register(
            "Test User",
            "test@example.com",
            "StrongPass123!",
            "Invalid Role",
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid role"


def test_register_super_admin_forbidden(auth_service):
    auth_service.user_repository.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth_service.register(
            "Test User",
            "admin@example.com",
            "StrongPass123!",
            "Super Admin",
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Super Admin cannot be self-registered"
    auth_service.user_repository.create.assert_not_called()


# --------------------------------------------------
# LOGIN TESTS
# --------------------------------------------------

def test_login_success(auth_service, active_user):
    auth_service.user_repository.get_by_email.return_value = active_user

    with (
        patch(
            "services.auth_service.verify_password",
            return_value=True,
        ),
        patch(
            "services.auth_service.create_access_token",
            return_value="access-token",
        ) as access_mock,
        patch(
            "services.auth_service.create_refresh_token",
            return_value="refresh-token",
        ) as refresh_mock,
    ):
        result = auth_service.login(
            "test@example.com",
            "StrongPass123!",
        )

    assert result == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "token_type": "bearer",
    }

    access_mock.assert_called_once_with(1, "Plant Manager")
    refresh_mock.assert_called_once_with(1, "Plant Manager")


def test_login_email_is_normalized(auth_service, active_user):
    auth_service.user_repository.get_by_email.return_value = active_user

    with (
        patch("services.auth_service.verify_password", return_value=True),
        patch("services.auth_service.create_access_token", return_value="a"),
        patch("services.auth_service.create_refresh_token", return_value="r"),
    ):
        auth_service.login("TEST@EXAMPLE.COM", "StrongPass123!")

    auth_service.user_repository.get_by_email.assert_called_once_with(
        "test@example.com"
    )


def test_login_user_not_found(auth_service):
    auth_service.user_repository.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth_service.login("missing@example.com", "password")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid email or password"


def test_login_wrong_password(auth_service, active_user):
    auth_service.user_repository.get_by_email.return_value = active_user

    with patch(
        "services.auth_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(HTTPException) as exc:
            auth_service.login("test@example.com", "wrong-password")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid email or password"


def test_login_deactivated_user(auth_service, inactive_user):
    auth_service.user_repository.get_by_email.return_value = inactive_user

    with patch("services.auth_service.verify_password", return_value=True):
        with pytest.raises(HTTPException) as exc:
            auth_service.login("inactive@example.com", "password")

    assert exc.value.status_code == 403
    assert exc.value.detail == "Account is deactivated"


# --------------------------------------------------
# REFRESH TOKEN TESTS
# --------------------------------------------------

def test_refresh_token_success(auth_service, active_user):
    auth_service.is_token_revoked = MagicMock(return_value=False)

    payload = {
        "sub": "1",
        "type": "refresh",
    }

    auth_service.user_repository.get_by_id.return_value = active_user
    auth_service.revoke_token = MagicMock()

    with (
        patch("services.auth_service.decode_token", return_value=payload),
        patch(
            "services.auth_service.create_access_token",
            return_value="new-access",
        ),
        patch(
            "services.auth_service.create_refresh_token",
            return_value="new-refresh",
        ),
    ):
        result = auth_service.refresh_token("old-refresh")

    assert result == {
        "access_token": "new-access",
        "refresh_token": "new-refresh",
        "token_type": "bearer",
    }

    auth_service.user_repository.get_by_id.assert_called_once_with(1)
    auth_service.revoke_token.assert_called_once_with("old-refresh")


def test_refresh_token_already_revoked(auth_service):
    auth_service.is_token_revoked = MagicMock(return_value=True)

    with pytest.raises(HTTPException) as exc:
        auth_service.refresh_token("revoked-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Refresh token has been revoked"


def test_refresh_token_invalid(auth_service):
    auth_service.is_token_revoked = MagicMock(return_value=False)

    with patch("services.auth_service.decode_token", return_value=None):
        with pytest.raises(HTTPException) as exc:
            auth_service.refresh_token("invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid refresh token"


def test_refresh_token_wrong_type(auth_service):
    auth_service.is_token_revoked = MagicMock(return_value=False)

    with patch(
        "services.auth_service.decode_token",
        return_value={"sub": "1", "type": "access"},
    ):
        with pytest.raises(HTTPException) as exc:
            auth_service.refresh_token("access-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token type"


def test_refresh_token_user_not_found(auth_service):
    auth_service.is_token_revoked = MagicMock(return_value=False)
    auth_service.user_repository.get_by_id.return_value = None

    with patch(
        "services.auth_service.decode_token",
        return_value={"sub": "99", "type": "refresh"},
    ):
        with pytest.raises(HTTPException) as exc:
            auth_service.refresh_token("refresh-token")

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


def test_refresh_token_inactive_user(auth_service, inactive_user):
    auth_service.is_token_revoked = MagicMock(return_value=False)
    auth_service.user_repository.get_by_id.return_value = inactive_user

    with patch(
        "services.auth_service.decode_token",
        return_value={"sub": "2", "type": "refresh"},
    ):
        with pytest.raises(HTTPException) as exc:
            auth_service.refresh_token("refresh-token")

    assert exc.value.status_code == 403
    assert exc.value.detail == "Account is deactivated"


# --------------------------------------------------
# LOGOUT TESTS
# --------------------------------------------------

def test_logout_success(auth_service, db):
    payload = {
        "exp": datetime(
            2027, 1, 1, tzinfo=timezone.utc
        ).timestamp()
    }

    with patch(
        "services.auth_service.decode_token",
        return_value=payload,
    ):
        result = auth_service.logout("refresh-token")

    assert result == {"message": "Logged out successfully"}
    db.add.assert_called_once()
    db.commit.assert_called_once()

    revoked_token = db.add.call_args.args[0]
    assert revoked_token.token == "refresh-token"
    assert isinstance(revoked_token.expires_at, datetime)


def test_logout_invalid_token(auth_service, db):
    with patch("services.auth_service.decode_token", return_value=None):
        with pytest.raises(HTTPException) as exc:
            auth_service.logout("invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"
    db.add.assert_not_called()
    db.commit.assert_not_called()


# --------------------------------------------------
# REVOKE TOKEN TESTS
# --------------------------------------------------

def test_revoke_token_success(auth_service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    payload = {
        "exp": datetime(
            2027, 1, 1, tzinfo=timezone.utc
        ).timestamp()
    }

    with patch(
        "services.auth_service.decode_token",
        return_value=payload,
    ):
        auth_service.revoke_token("refresh-token")

    db.add.assert_called_once()
    db.commit.assert_called_once()

    revoked_token = db.add.call_args.args[0]
    assert revoked_token.token == "refresh-token"


def test_revoke_token_invalid_payload(auth_service, db):
    with patch("services.auth_service.decode_token", return_value=None):
        auth_service.revoke_token("invalid-token")

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_revoke_token_already_exists(auth_service, db):
    existing_token = SimpleNamespace(token="refresh-token")

    db.query.return_value.filter.return_value.first.return_value = (
        existing_token
    )

    with patch(
        "services.auth_service.decode_token",
        return_value={
            "exp": datetime(
                2027, 1, 1, tzinfo=timezone.utc
            ).timestamp()
        },
    ):
        auth_service.revoke_token("refresh-token")

    db.add.assert_not_called()
    db.commit.assert_not_called()


# --------------------------------------------------
# CHECK REVOKED TOKEN TESTS
# --------------------------------------------------

def test_is_token_revoked_true(auth_service, db):
    db.query.return_value.filter.return_value.first.return_value = (
        SimpleNamespace(token="revoked-token")
    )

    assert auth_service.is_token_revoked("revoked-token") is True


def test_is_token_revoked_false(auth_service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    assert auth_service.is_token_revoked("active-token") is False


# --------------------------------------------------
# CHANGE PASSWORD TESTS
# --------------------------------------------------

def test_change_password_success(auth_service, active_user):
    with (
        patch("services.auth_service.verify_password", return_value=True),
        patch(
            "services.auth_service.hash_password",
            return_value="new-hashed-password",
        ),
    ):
        result = auth_service.change_password(
            active_user,
            "old-password",
            "new-password",
        )

    assert result == {"message": "Password changed successfully"}
    assert active_user.password_hash == "new-hashed-password"
    auth_service.user_repository.update.assert_called_once_with(active_user)


def test_change_password_wrong_current_password(
    auth_service, active_user
):
    with patch("services.auth_service.verify_password", return_value=False):
        with pytest.raises(HTTPException) as exc:
            auth_service.change_password(
                active_user,
                "wrong-password",
                "new-password",
            )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Current password is incorrect"
    auth_service.user_repository.update.assert_not_called()


# --------------------------------------------------
# DEACTIVATE USER TESTS
# --------------------------------------------------

def test_deactivate_user_success(auth_service, active_user):
    auth_service.user_repository.get_by_id.return_value = active_user

    result = auth_service.deactivate_user(1)

    assert result == active_user
    assert active_user.is_active is False
    auth_service.user_repository.update.assert_called_once_with(active_user)


def test_deactivate_user_not_found(auth_service):
    auth_service.user_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth_service.deactivate_user(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


# --------------------------------------------------
# ACTIVATE USER TESTS
# --------------------------------------------------

def test_activate_user_success(auth_service, inactive_user):
    auth_service.user_repository.get_by_id.return_value = inactive_user

    result = auth_service.activate_user(2)

    assert result == inactive_user
    assert inactive_user.is_active is True
    auth_service.user_repository.update.assert_called_once_with(inactive_user)


def test_activate_user_not_found(auth_service):
    auth_service.user_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth_service.activate_user(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"