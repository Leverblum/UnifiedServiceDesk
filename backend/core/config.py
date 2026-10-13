"""
Módulo de Configuración Global (Application Settings).
Centraliza la lectura de variables de entorno y constantes de la aplicación.
"""

from typing import List
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
        extra="ignore"
    )

    APP_NAME: str = "Unified Service Desk"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuración de Base de Datos
    # Por defecto apunta a PostgreSQL local; si no se provee, soporta SQLite fallback para portabilidad
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/unified_service_desk"
    
    # Configuración de CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]


settings = Settings()
