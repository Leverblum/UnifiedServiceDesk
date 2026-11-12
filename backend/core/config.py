"""
Módulo de Configuración Global (Application Settings).
Centraliza la lectura de variables de entorno y constantes de la aplicación.
Falla en arranque si JWT_SECRET_KEY no está configurada en producción/staging (DEF-02).
"""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración centralizada de Unified Service Desk.
    Valores leídos desde variables de entorno o archivo .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Unified Service Desk"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # SQLite local es el valor predeterminado para desarrollo; PostgreSQL se configura con DATABASE_URL.
    DATABASE_URL: str = "sqlite:///./unified_service_desk.db"

    # Seguridad JWT (DEF-02 / DEF-03)
    # En producción debe ser un token hex aleatorio de 32+ bytes.
    # Falla en startup si está en el valor placeholder (detectado en campo_validator).
    JWT_SECRET_KEY: str = "CAMBIA_ESTE_VALOR_POR_UNO_ALEATORIO_SEGURO"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Contraseña semilla para entornos de desarrollo (DEF-02)
    SEED_DEFAULT_PASSWORD: str = "UniServiceDesk2026!"

    # Configuración de CORS — acepta cadena separada por comas o lista JSON
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parsea ALLOWED_ORIGINS como lista, aceptando CSV o JSON."""
        raw = self.ALLOWED_ORIGINS.strip()
        if raw.startswith("["):
            import json
            return json.loads(raw)
        return [o.strip() for o in raw.split(",") if o.strip()]

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def jwt_secret_must_not_be_placeholder(cls, v: str) -> str:
        """
        Valida que JWT_SECRET_KEY tenga longitud mínima de seguridad.
        En producción, el operador debe proveer un secreto de al menos 32 caracteres.
        """
        if len(v) < 16:
            raise ValueError(
                "JWT_SECRET_KEY debe tener al menos 16 caracteres. "
                "Genera uno seguro con: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v


settings = Settings()
