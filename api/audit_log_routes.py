from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from db.database import get_db

from models.user_model import User

from schemas.audit_log_schema import (
    AuditLogResponse,
)

from repositories.audit_log_repository import (
    AuditLogRepository,
)

from utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/api/v1/audit-logs",
    tags=["Audit Logs"],
)


# =========================================================
# GET ALL AUDIT LOGS
# =========================================================

@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
    ),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
        )
    ),
    db: Session = Depends(get_db),
):

    repository = AuditLogRepository(db)

    return repository.get_all(
        skip=skip,
        limit=limit,
    )


# =========================================================
# GET BY USER
# =========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse],
)
def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
        )
    ),
    db: Session = Depends(get_db),
):

    repository = AuditLogRepository(db)

    return repository.get_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


# =========================================================
# GET BY ENTITY
# =========================================================

@router.get(
    "/entity/{entity}",
    response_model=list[AuditLogResponse],
)
def get_entity_audit_logs(
    entity: str,
    entity_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Plant Manager",
        )
    ),
    db: Session = Depends(get_db),
):

    repository = AuditLogRepository(db)

    return repository.get_by_entity(
        entity=entity,
        entity_id=entity_id,
        skip=skip,
        limit=limit,
    )