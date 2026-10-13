"""
Interfaz Abstracta para el Patrón Repository (GoF).
Aísla la capa de dominio y de servicios de la tecnología de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from backend.domain.models.ticket import TicketModel
from backend.domain.models.audit_log import AuditLogModel


class TicketRepositoryInterface(ABC):
    """
    Contrato formal para el acceso y manipulación de datos de Tickets.
    Permite el desacoplamiento total de SQLAlchemy y facilita pruebas con mocks.
    """

    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Optional[TicketModel]:
        """Obtiene un ticket por su identificador primario."""
        pass

    @abstractmethod
    def get_all(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TicketModel]:
        """Obtiene la lista de tickets aplicando filtros opcionales y paginación."""
        pass

    @abstractmethod
    def create(self, ticket: TicketModel) -> TicketModel:
        """Persiste un nuevo ticket en la base de datos."""
        pass

    @abstractmethod
    def update(self, ticket: TicketModel) -> TicketModel:
        """Actualiza un ticket existente."""
        pass

    @abstractmethod
    def delete(self, ticket_id: int) -> bool:
        """Elimina un ticket por su identificador."""
        pass

    @abstractmethod
    def add_audit_log(self, audit_log: AuditLogModel) -> AuditLogModel:
        """Registra un evento de auditoría asociado a un ticket."""
        pass

    @abstractmethod
    def get_audit_logs(self, ticket_id: int) -> List[AuditLogModel]:
        """Obtiene el historial de auditoría de un ticket ordenado cronológicamente."""
        pass
