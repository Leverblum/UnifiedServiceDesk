"""
Observador Concreto: AuditLogObserver.
Registra cada evento de mutación de ticket en la tabla de auditoría mediante el repositorio.
"""

import logging
from backend.services.observers.base import TicketObserver
from backend.services.observers.events import TicketEvent
from backend.repositories.base import TicketRepositoryInterface
from backend.domain.models.audit_log import AuditLogModel

logger = logging.getLogger(__name__)


class AuditLogObserver(TicketObserver):
    """
    Patrón Observer (GoF) - Observador Concreto:
    Persiste en la base de datos un registro formal de auditoría cada vez que
    un ticket es creado, modificado o transicionado de estado.
    """

    def __init__(self, repository: TicketRepositoryInterface):
        self._repository = repository

    def update(self, event: TicketEvent) -> None:
        log_entry = AuditLogModel(
            ticket_id=event.ticket_id,
            event_type=event.event_type,
            old_status=event.old_status,
            new_status=event.new_status,
            details=event.details or f"Evento '{event.event_type}' procesado por AuditLogObserver",
            created_at=event.timestamp
        )
        self._repository.add_audit_log(log_entry)
        logger.info(
            f"[AuditLogObserver] Auditoría persistida para Ticket #{event.ticket_id}: "
            f"Evento={event.event_type}, Estado={event.old_status} -> {event.new_status}"
        )
