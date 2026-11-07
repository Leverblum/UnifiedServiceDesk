"""
Endpoints de la API v1 para la gestión de Usuarios, Autenticación y Roles Universitarios (RBAC).
REGLA ARQUITECTÓNICA: Los endpoints consumen única y exclusivamente la Fachada ServiceDeskFacade.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from backend.api.dependencies import get_service_desk_facade
from backend.services.service_desk_facade import ServiceDeskFacade
from backend.domain.schemas.user import (
    UserCreateRequest,
    LoginRequest,
    UserResponse,
)
from backend.services.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Usuarios & Autenticación"])


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con correo institucional"
)
def login_user(
    request: LoginRequest,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> UserResponse:
    """Verifica la existencia del usuario institucional y valida contraseña."""
    try:
        user = facade.get_user_by_email(request.email)
        # Validar contraseña simple para MVP
        db_user = facade.get_user_model_by_email(request.email)
        if db_user and hasattr(db_user, 'password') and db_user.password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta."
            )
        return user
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ninguna cuenta registrada con el correo '{request.email}'. Verifica e intenta de nuevo."
        )


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios del sistema universitario"
)
def list_users(
    role: Optional[str] = Query(None, description="Filtrar por rol: STUDENT, STAFF, IT_STUDENT_SUPPORT, IT_STAFF_SUPPORT, ADMIN"),
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> List[UserResponse]:
    """Retorna la lista de usuarios registrados, permitiendo filtrar por rol."""
    return facade.list_users(role=role)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario universitario"
)
def create_user(
    request: UserCreateRequest,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> UserResponse:
    """Registra un nuevo usuario con su rol correspondiente."""
    try:
        return facade.create_user(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/seed",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Sembrar los 5 usuarios de prueba universitarios"
)
def seed_users(
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> List[UserResponse]:
    """Genera las personas de prueba: Admin, Estudiante, Personal, TI Estudiantes y TI Personal."""
    return facade.seed_default_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de un usuario"
)
def get_user(
    user_id: int,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> UserResponse:
    """Retorna los datos de un usuario por su ID."""
    try:
        return facade.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
