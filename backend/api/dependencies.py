"""
Proveedores de Inyección de Dependencias (FastAPI Depends).
Conecta el DatabaseManager Singleton, los Repositorios y la Fachada.
Incluye dependencias de autenticación JWT y autorización RBAC (DEF-03).
"""

from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.core.database import DatabaseManager
from backend.core.security import decode_access_token
from backend.repositories.base import TicketRepositoryInterface
from backend.repositories.ticket_repository import SQLAlchemyTicketRepository
from backend.repositories.user_repository import UserRepositoryInterface, SQLAlchemyUserRepository
from backend.services.service_desk_facade import ServiceDeskFacade
from backend.domain.schemas.user import UserResponse, UserRole

# OAuth2 Bearer scheme — tokenUrl apunta al endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login", auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    """
    Obtiene una sesión de base de datos desde el DatabaseManager (Singleton).
    Garantiza el cierre automático de la conexión tras la ejecución de la petición HTTP.
    """
    db_manager = DatabaseManager()
    yield from db_manager.get_session()


def get_ticket_repository(
    session: Session = Depends(get_db_session),
) -> TicketRepositoryInterface:
    return SQLAlchemyTicketRepository(session)


def get_user_repository(
    session: Session = Depends(get_db_session),
) -> UserRepositoryInterface:
    return SQLAlchemyUserRepository(session)


def get_service_desk_facade(
    ticket_repository: TicketRepositoryInterface = Depends(get_ticket_repository),
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> ServiceDeskFacade:
    """
    Inyecta la fachada ServiceDeskFacade configurada con los repositorios.
    Los endpoints de FastAPI SOLO interactúan con esta fachada.
    """
    return ServiceDeskFacade(
        repository=ticket_repository,
        user_repository=user_repository,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> UserResponse:
    """
    Dependencia que extrae y valida el usuario del JWT Bearer token (DEF-03).
    Lanza 401 si no hay token o el token es inválido/expirado.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado. Se requiere token Bearer.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return facade.get_current_user_from_token(token)


def get_optional_current_user(
    token: str = Depends(oauth2_scheme),
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> UserResponse | None:
    """
    Variante opcional: retorna None si no hay token (para endpoints semi-públicos).
    """
    if not token:
        return None
    try:
        return facade.get_current_user_from_token(token)
    except HTTPException:
        return None


def require_roles(allowed_roles: List[UserRole]):
    """
    Fábrica de dependencias RBAC. Genera una dependencia que valida que
    el usuario autenticado tenga uno de los roles permitidos (DEF-03).

    Uso:
        @router.get("/admin-only", dependencies=[Depends(require_roles([UserRole.ADMIN]))])
    """
    def _check_role(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        allowed_values = [r.value for r in allowed_roles]
        if current_user.role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acceso denegado. Rol '{current_user.role}' no tiene permiso. "
                    f"Roles requeridos: {allowed_values}"
                ),
            )
        return current_user

    return _check_role
