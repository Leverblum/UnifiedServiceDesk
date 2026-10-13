"""
Exportación de componentes de la capa de repositorios.
"""

from backend.repositories.base import TicketRepositoryInterface
from backend.repositories.ticket_repository import SQLAlchemyTicketRepository

__all__ = ["TicketRepositoryInterface", "SQLAlchemyTicketRepository"]
