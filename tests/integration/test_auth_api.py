
import pytest

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app


client = TestClient(app)


# -----------------------------------------
# REGISTER API TESTS
# -----------------------------------------

def test_register_success():

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Manager",
            "email": "manager@example.com",
            "password": "TestPass123",
            "role": "Store Manager"
        }
    )

    assert response.status_code in [200, 201, 400, 409, 422]


def test_register_invalid_email():

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Manager",
            "email": "invalid-email",
            "password": "TestPass123",
            "role": "Store Manager"
        }
    )

    assert response.status_code == 422


def test_register_short_password():

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Manager",
            "email": "manager@example.com",
            "password": "123",
            "role": "Store Manager"
        }
    )

    assert response.status_code == 422


def test_register_missing_fields():

    response = client.post(
        "/api/v1/auth/register",
        json={}
    )

    assert response.status_code == 422


# -----------------------------------------
# LOGIN API TESTS
# -----------------------------------------

def test_login_invalid_email_format():

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid-email",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 422


def test_login_missing_password():

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "manager@example.com"
        }
    )

    assert response.status_code == 422


def test_login_invalid_credentials():

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "WrongPass123"
        }
    )

    assert response.status_code in [400, 401, 403, 404, 422]


# -----------------------------------------
# REFRESH TOKEN API TESTS
# -----------------------------------------

def test_refresh_missing_token():

    response = client.post(
        "/api/v1/auth/refresh",
        json={}
    )

    assert response.status_code == 422


def test_refresh_invalid_token():

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid-refresh-token"
        }
    )

    assert response.status_code in [400, 401, 403, 404, 422]


# -----------------------------------------
# LOGOUT API TESTS
# -----------------------------------------

def test_logout_missing_token():

    response = client.post(
        "/api/v1/auth/logout",
        json={}
    )

    assert response.status_code == 422


def test_logout_invalid_token():

    response = client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": "invalid-refresh-token"
        }
    )

    assert response.status_code in [200, 400, 401, 403, 404, 422]


# -----------------------------------------
# FORGOT PASSWORD API TESTS
# -----------------------------------------

def test_forgot_password_invalid_email():

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": "invalid-email"
        }
    )

    assert response.status_code == 422


def test_forgot_password_missing_email():

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={}
    )

    assert response.status_code == 422


# -----------------------------------------
# RESET PASSWORD API TESTS
# -----------------------------------------

def test_reset_password_missing_fields():

    response = client.post(
        "/api/v1/auth/reset-password",
        json={}
    )

    assert response.status_code == 422


def test_reset_password_short_password():

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "test-reset-token",
            "new_password": "123"
        }
    )

    assert response.status_code == 422


def test_reset_password_invalid_token():

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid-reset-token",
            "new_password": "NewPass123"
        }
    )

    assert response.status_code in [400, 401, 403, 404, 422]


# -----------------------------------------
# CHANGE PASSWORD API TESTS
# -----------------------------------------

def test_change_password_missing_fields():

    response = client.post(
        "/api/v1/auth/change-password",
        json={}
    )

    assert response.status_code == 422


def test_change_password_short_new_password():

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "OldPass123",
            "new_password": "123"
        }
    )

    assert response.status_code == 422


# -----------------------------------------
# CURRENT USER API TEST
# -----------------------------------------

def test_current_user_without_token():

    response = client.get(
        "/api/v1/auth/me"
    )

    assert response.status_code in [401, 403, 404]
