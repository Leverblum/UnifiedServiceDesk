"""
Módulo de Seguridad Centralizado — Unified Service Desk.

Implementa:
- Hashing de contraseñas con Argon2id (DEF-01 / H-SEC-01)
- Verificación de contraseñas de forma segura en tiempo constante
- Emisión y validación de JSON Web Tokens firmados (DEF-03 / H-SEC-03)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from fastapi import HTTPException, status

from backend.core.config import settings

# ============================================================
# Hashing de Contraseñas con Argon2id (DEF-01)
# ============================================================

# Configuración recomendada por OWASP para Argon2id:
# time_cost=2, memory_cost=65536 (64 MB), parallelism=2
_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain_password: str) -> str:
    """
    Genera un hash seguro Argon2id de la contraseña en texto plano.
    El resultado siempre comienza con '$argon2id$' y es único por ejecución (salt aleatorio).

    Args:
        plain_password: Contraseña en texto plano a hashear.

    Returns:
        Hash Argon2id como string (almacenable en columna VARCHAR(255)).
    """
    if not plain_password:
        raise ValueError("La contraseña no puede estar vacía.")
    return _ph.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña en texto plano contra su hash Argon2id almacenado.
    Devuelve False en lugar de propagar excepciones de verificación.

    Args:
        plain_password: Contraseña ingresada por el usuario.
        hashed_password: Hash almacenado en la base de datos.

    Returns:
        True si la contraseña coincide; False en caso contrario.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Verifica si el hash necesita ser regenerado por cambio en parámetros de costo.
    Útil para rehashing transparente en login.
    """
    return _ph.check_needs_rehash(hashed_password)


# ============================================================
# JSON Web Tokens (DEF-03 / H-SEC-03)
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JWT firmado con HS256 (o el algoritmo configurado en settings).

    Claims incluidos:
    - sub: Identificador del usuario (email o ID)
    - role: Rol institucional del usuario
    - iat: Timestamp de emisión (issued at)
    - exp: Timestamp de expiración

    Args:
        data: Diccionario con al menos {'sub': ..., 'role': ...}.
        expires_delta: Duración de validez del token (default: settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES).

    Returns:
        Token JWT como string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT: firma criptográfica, expiración y estructura.

    Lanza HTTPException(401) ante:
    - Token con firma alterada / inválida
    - Token expirado
    - Token malformado

    Args:
        token: JWT como string (sin el prefijo 'Bearer ').

    Returns:
        Payload decodificado como dict.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "iat"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o manipulado: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )
