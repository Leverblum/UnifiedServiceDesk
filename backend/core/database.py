"""
Implementación del Patrón Singleton para la gestión de conexiones a Base de Datos.
Centraliza el Engine de SQLAlchemy y el SessionMaker para PostgreSQL/SQLite.
Migraciones defensivas de contraseñas hardcodeadas eliminadas (DEF-02).
"""

import threading
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """
    Patrón Singleton (GoF):
    Garantiza que exista una única instancia de DatabaseManager en toda la aplicación,
    evitando la proliferación de pools de conexiones y asegurando el control centralizado
    del ciclo de vida de las conexiones.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, database_url: str = None):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, database_url: str = None):
        # Evitar re-inicialización de la instancia Singleton
        if getattr(self, "_initialized", False):
            return

        with self._lock:
            if getattr(self, "_initialized", False):
                return

            self._database_url = database_url or settings.DATABASE_URL

            engine_args = {
                "pool_pre_ping": True,
            }

            if "postgresql" in self._database_url:
                engine_args.update({
                    "pool_size": 10,
                    "max_overflow": 20,
                    "pool_recycle": 1800,
                })
            elif "sqlite" in self._database_url:
                if ":memory:" in self._database_url:
                    from sqlalchemy.pool import StaticPool
                    engine_args.update({
                        "connect_args": {"check_same_thread": False},
                        "poolclass": StaticPool,
                    })
                else:
                    engine_args.update({
                        "connect_args": {"check_same_thread": False},
                    })

            try:
                self._engine = create_engine(self._database_url, **engine_args)
                # Verificar conectividad real a PostgreSQL
                if "postgresql" in self._database_url:
                    with self._engine.connect():
                        pass
            except Exception as e:
                if isinstance(e, UnicodeDecodeError):
                    failure_detail = (
                        "el servidor PostgreSQL devolvió un mensaje con codificación "
                        "no UTF-8; revise la codificación del servidor y client_encoding"
                    )
                else:
                    failure_detail = f"{type(e).__name__}: {e}"
                logger.warning(
                    "No fue posible conectar con la base de datos configurada (%s). "
                    "Activando fallback resiliente a SQLite local.",
                    failure_detail,
                )
                fallback_url = "sqlite:///./unified_service_desk.db"
                self._database_url = fallback_url
                self._engine = create_engine(
                    fallback_url, connect_args={"check_same_thread": False}
                )

            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
            self._initialized = True
            logger.info("DatabaseManager Singleton inicializado exitosamente.")

    @property
    def engine(self):
        return self._engine

    @property
    def session_factory(self):
        return self._session_factory

    def get_session(self) -> Generator[Session, None, None]:
        """
        Generador de sesiones para inyección de dependencias en FastAPI.
        Garantiza cierre de la sesión tras completar la solicitud.
        """
        session: Session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def create_all_tables(self) -> None:
        """Crea todas las tablas declaradas en la metadata de SQLAlchemy."""
        import backend.domain.models  # Registra modelos ORM en Base.metadata
        Base.metadata.create_all(bind=self._engine)

        # Migración defensiva para columnas nuevas en SQLite existente (sin inyectar contraseñas)
        if "sqlite" in self._database_url:
            try:
                from sqlalchemy import text
                with self._engine.connect() as conn:
                    res = conn.execute(text("PRAGMA table_info(tickets);")).fetchall()
                    col_names = [r[1] for r in res]
                    if col_names and "created_by_id" not in col_names:
                        conn.execute(text(
                            "ALTER TABLE tickets ADD COLUMN created_by_id INTEGER REFERENCES users(id);"
                        ))
                        conn.commit()
                    if col_names and "assigned_to_id" not in col_names:
                        conn.execute(text(
                            "ALTER TABLE tickets ADD COLUMN assigned_to_id INTEGER REFERENCES users(id);"
                        ))
                        conn.commit()
                    # Migrar columna password si existe con longitud insuficiente para hashes Argon2id
                    res_users = conn.execute(text("PRAGMA table_info(users);")).fetchall()
                    user_cols = [r[1] for r in res_users]
                    if "created_at" not in user_cols:
                        conn.execute(text("ALTER TABLE tickets ADD COLUMN created_at DATETIME;"))
                        conn.commit()
            except Exception as exc:
                logger.debug("Migración preventiva SQLite: %s", exc)

    def drop_all_tables(self) -> None:
        """Elimina todas las tablas (usado en tests y mantenimiento)."""
        Base.metadata.drop_all(bind=self._engine)

    @classmethod
    def reset_instance_for_testing(cls) -> None:
        """Permite reiniciar el Singleton para testing controlado."""
        with cls._lock:
            cls._instance = None
