"""
Esquemas de validación y DTOs para la entidad Usuario y roles (RBAC Universitario).
Roles institucionales (5 oficiales — DEF-05):
- STUDENT          : Estudiantes de la universidad
- STAFF            : Personal administrativo y docente de la universidad
- IT_STUDENT_SUPPORT: Personal de TI especializado en servicios para estudiantes
- IT_STAFF_SUPPORT : Personal de TI especializado en infraestructura y personal
- ADMIN            : Administrador general del Service Desk
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserRole(str, Enum):
    STUDENT = "STUDENT"                        # Estudiante universitario
    STAFF = "STAFF"                            # Personal / Docente
    IT_STUDENT_SUPPORT = "IT_STUDENT_SUPPORT"  # TI Soporte Estudiantes
    IT_STAFF_SUPPORT = "IT_STAFF_SUPPORT"      # TI Soporte Personal/Campus
    ADMIN = "ADMIN"                            # Administrador General


class LoginRequest(BaseModel):
    """DTO para autenticación — requiere correo y contraseña explícita (DEF-01 / DEF-02)."""
    email: EmailStr = Field(..., description="Correo institucional para iniciar sesión")
    password: str = Field(..., min_length=4, description="Contraseña del usuario")


class UserCreateRequest(BaseModel):
    """DTO para crear o registrar un nuevo usuario en el Service Desk Universitario."""
    email: EmailStr = Field(..., description="Correo institucional del usuario")
    full_name: str = Field(..., min_length=2, max_length=255, description="Nombre completo del usuario")
    role: UserRole = Field(default=UserRole.STUDENT, description="Rol del usuario en la institución")
    department: Optional[str] = Field(None, max_length=100, description="Facultad, Carrera o Dependencia Universitaria")
    password: str = Field(..., min_length=4, description="Contraseña del usuario (se almacena hasheada)")


class UserSimpleResponse(BaseModel):
    """DTO conciso para representar usuarios anidados en respuestas de tickets."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    department: Optional[str] = None


class UserResponse(BaseModel):
    """DTO completo para respuestas detalladas de usuario (sin contraseña — DEF-01)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    """DTO para la respuesta del endpoint de login con JWT (DEF-03)."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
