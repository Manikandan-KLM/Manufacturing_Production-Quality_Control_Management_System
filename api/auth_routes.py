from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from db.database import get_db

from schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
    ChangePasswordRequest,
    UserResponse
)

from services.auth_service import AuthService

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


# ==========================================
# REGISTER
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    service = AuthService(db)

    return service.register(
        full_name=request.full_name,
        email=request.email,
        password=request.password,
        role=request.role
    )


# ==========================================
# LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    service = AuthService(db)

    return service.login(
        email=request.email,
        password=request.password
    )


# ==========================================
# REFRESH TOKEN
# ==========================================

@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):

    service = AuthService(db)

    return service.refresh_token(
        request.refresh_token
    )


# ==========================================
# LOGOUT
# ==========================================

@router.post(
    "/logout"
)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):

    service = AuthService(db)

    return service.logout(
        request.refresh_token
    )


# ==========================================
# CURRENT USER
# ==========================================

@router.get(
    "/me",
    response_model=UserResponse
)
def current_user(
    current_user=Depends(get_current_user)
):

    return current_user


# ==========================================
# CHANGE PASSWORD
# ==========================================

@router.post(
    "/change-password"
)
def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = AuthService(db)

    return service.change_password(
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password
    )


# ==========================================
# DEACTIVATE USER
# ==========================================

@router.patch(
    "/users/{user_id}/deactivate",
    response_model=UserResponse
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Super Admin")
    )
):

    service = AuthService(db)

    return service.deactivate_user(
        user_id
    )


# ==========================================
# ACTIVATE USER
# ==========================================

@router.patch(
    "/users/{user_id}/activate",
    response_model=UserResponse
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Super Admin")
    )
):

    service = AuthService(db)

    return service.activate_user(
        user_id
    )