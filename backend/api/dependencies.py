"""
Proveedores de Inyección de Dependencias (FastAPI Depends).
Conecta el DatabaseManager Singleton, los Repositorios y la Fachada.
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.core.database import DatabaseManager
from backend.repositories.base import TicketRepositoryInterface
from backend.repositories.ticket_repository import SQLAlchemyTicketRepository
from backend.repositories.user_repository import UserRepositoryInterface, SQLAlchemyUserRepository
from backend.services.service_desk_facade import ServiceDeskFacade


def get_db_session() -> Generator[Session, None, None]:
    """
    Obtiene una sesión de base de datos desde el DatabaseManager (Singleton).
    Garantiza el cierre automático de la conexión tras la ejecución de la petición HTTP.
    """
    db_manager = DatabaseManager()
    yield from db_manager.get_session()


def get_ticket_repository(
    session: Session = Depends(get_db_session)
) -> TicketRepositoryInterface:
    """
    Inyecta la implementación concreta de TicketRepositoryInterface.
    Aísla los endpoints de los detalles de SQLAlchemy.
    """
    return SQLAlchemyTicketRepository(session)


def get_user_repository(
    session: Session = Depends(get_db_session)
) -> UserRepositoryInterface:
    """
    Inyecta la implementación concreta de UserRepositoryInterface.
    """
    return SQLAlchemyUserRepository(session)


def get_service_desk_facade(
    ticket_repository: TicketRepositoryInterface = Depends(get_ticket_repository),
    user_repository: UserRepositoryInterface = Depends(get_user_repository)
) -> ServiceDeskFacade:
    """
    Inyecta la fachada ServiceDeskFacade configurada con los repositorios.
    Los endpoints de FastAPI SOLO interactúan con esta fachada.
    """
    return ServiceDeskFacade(
        repository=ticket_repository,
        user_repository=user_repository
    )
