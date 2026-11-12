"""
Endpoints de la API v1 para la gestión de Usuarios, Autenticación JWT y Roles Universitarios (RBAC).
REGLA ARQUITECTÓNICA: Los endpoints consumen única y exclusivamente la Fachada ServiceDeskFacade.

Seguridad implementada (DEF-01, DEF-02, DEF-03):
- Login devuelve JWT firmado (no contraseña en texto plano).
- Contraseñas nunca expuestas en ninguna respuesta.
- Endpoint /me protegido por token JWT.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from backend.api.dependencies import get_service_desk_facade, get_current_user
from backend.services.service_desk_facade import ServiceDeskFacade
from backend.domain.schemas.user import (
    UserCreateRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)
from backend.services.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Usuarios & Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión — retorna JWT Bearer (DEF-03)",
)
def login_user(
    request: LoginRequest,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> TokenResponse:
    """
    Autentica con correo y contraseña.
    Verifica hash Argon2id y emite JWT firmado.
    Responde con { access_token, token_type, user } sin exponer el hash.
    """
    return facade.login(request.email, request.password)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario autenticado desde token JWT",
)
def get_me(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Retorna los datos del usuario autenticado extraídos del JWT válido (DEF-03)."""
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios del sistema universitario",
)
def list_users(
    role: Optional[str] = Query(
        None,
        description="Filtrar por rol: STUDENT, STAFF, IT_STUDENT_SUPPORT, IT_STAFF_SUPPORT, ADMIN",
    ),
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> List[UserResponse]:
    """Retorna la lista de usuarios registrados, permitiendo filtrar por rol."""
    return facade.list_users(role=role)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario universitario",
)
def create_user(
    request: UserCreateRequest,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> UserResponse:
    """Registra un nuevo usuario. La contraseña se hashea con Argon2id antes de persistir."""
    try:
        return facade.create_user(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/seed",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Sembrar los 5 usuarios de prueba universitarios",
)
def seed_users(
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> List[UserResponse]:
    """Genera las personas de prueba con contraseñas hasheadas (DEF-01)."""
    return facade.seed_default_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
)
def get_user(
    user_id: int,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade),
) -> UserResponse:
    """Retorna los datos de un usuario específico (sin contraseña)."""
    try:
        return facade.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
