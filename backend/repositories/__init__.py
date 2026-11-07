"""
Exportación de componentes de la capa de repositorios.
"""

from backend.repositories.base import TicketRepositoryInterface
from backend.repositories.ticket_repository import SQLAlchemyTicketRepository
from backend.repositories.user_repository import UserRepositoryInterface, SQLAlchemyUserRepository

__all__ = [
    "TicketRepositoryInterface",
    "SQLAlchemyTicketRepository",
    "UserRepositoryInterface",
    "SQLAlchemyUserRepository"
]
