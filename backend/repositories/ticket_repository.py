"""
Implementación Concreta del Patrón Repository (GoF) con SQLAlchemy.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from backend.repositories.base import TicketRepositoryInterface
from backend.domain.models.ticket import TicketModel
from backend.domain.models.audit_log import AuditLogModel


class SQLAlchemyTicketRepository(TicketRepositoryInterface):
    """
    Repositorio concreto que encapsula todas las operaciones SQL y consultas ORM
    hacia PostgreSQL / SQLite a través de la sesión activa de SQLAlchemy.
    """

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, ticket_id: int) -> Optional[TicketModel]:
        """Recupera un ticket junto con sus relaciones para evitar consultas N+1."""
        return (
            self._session.query(TicketModel)
            .options(
                joinedload(TicketModel.audit_logs),
                joinedload(TicketModel.creator),
                joinedload(TicketModel.assignee)
            )
            .filter(TicketModel.id == ticket_id)
            .first()
        )

    def get_all(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        created_by_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        unassigned_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[TicketModel]:
        query = (
            self._session.query(TicketModel)
            .options(
                joinedload(TicketModel.audit_logs),
                joinedload(TicketModel.creator),
                joinedload(TicketModel.assignee)
            )
        )
        
        if category:
            query = query.filter(TicketModel.category == category.upper())
        if status:
            query = query.filter(TicketModel.status == status.upper())
        if created_by_id is not None:
            query = query.filter(TicketModel.created_by_id == created_by_id)
        if assigned_to_id is not None:
            query = query.filter(TicketModel.assigned_to_id == assigned_to_id)
        if unassigned_only:
            query = query.filter(TicketModel.assigned_to_id.is_(None))

        return query.order_by(TicketModel.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, ticket: TicketModel) -> TicketModel:
        self._session.add(ticket)
        self._session.commit()
        self._session.refresh(ticket)
        return ticket

    def update(self, ticket: TicketModel) -> TicketModel:
        self._session.merge(ticket)
        self._session.commit()
        self._session.refresh(ticket)
        return ticket

    def delete(self, ticket_id: int) -> bool:
        ticket = self.get_by_id(ticket_id)
        if not ticket:
            return False
        self._session.delete(ticket)
        self._session.commit()
        return True

    def add_audit_log(self, audit_log: AuditLogModel) -> AuditLogModel:
        self._session.add(audit_log)
        self._session.commit()
        self._session.refresh(audit_log)
        return audit_log

    def get_audit_logs(self, ticket_id: int) -> List[AuditLogModel]:
        return (
            self._session.query(AuditLogModel)
            .filter(AuditLogModel.ticket_id == ticket_id)
            .order_by(AuditLogModel.created_at.asc())
            .all()
        )
