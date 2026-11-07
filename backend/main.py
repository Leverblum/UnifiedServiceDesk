"""
Punto de Entrada Principal (Entrypoint) para la Aplicación FastAPI.
Configura middlewares, ciclo de vida (Lifespan), CORS y montaje de routers.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.database import DatabaseManager
from backend.api.v1.router import api_v1_router

# Configuración de Logging Estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("UnifiedServiceDesk")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Inicializa el pool del DatabaseManager (Singleton), asegura la creación de tablas
    y siembra usuarios iniciales si la base de datos está vacía.
    """
    logger.info("Iniciando aplicación Unified Service Desk...")
    try:
        db_manager = DatabaseManager()
        db_manager.create_all_tables()
        logger.info("Tablas de base de datos verificadas/creadas exitosamente.")

        # Sembrar usuarios iniciales para pruebas inmediatas de roles
        from backend.repositories.ticket_repository import SQLAlchemyTicketRepository
        from backend.repositories.user_repository import SQLAlchemyUserRepository
        from backend.services.service_desk_facade import ServiceDeskFacade
        session = next(db_manager.get_session())
        try:
            facade = ServiceDeskFacade(
                repository=SQLAlchemyTicketRepository(session),
                user_repository=SQLAlchemyUserRepository(session)
            )
            facade.seed_default_users()
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error al inicializar base de datos / seed users: {e}")

    yield

    logger.info("Cerrando aplicación Unified Service Desk...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para el Sistema Unificado de Gestión de Tickets TI (Unified Service Desk)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuración de CORS para integración con Frontend (Vite + React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montaje de Rutas v1
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Salud"])
def health_check():
    """Endpoint de verificación de estado y conectividad del servicio."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
