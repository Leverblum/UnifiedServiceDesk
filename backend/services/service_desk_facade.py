"""
Implementación del Patrón Facade (GoF) para el Subsistema Service Desk.
Punto único de orquestación de reglas de negocio, creación polimórfica,
máquina de estados, persistencia desacoplada y despacho de eventos.
"""

from typing import List, Optional, Dict, Any
import logging
from backend.repositories.base import TicketRepositoryInterface
from backend.domain.schemas.ticket import (
    TicketCreateRequest,
    TicketStatusUpdateRequest,
    TicketResponse,
    AuditLogResponse,
)
from backend.domain.factories.ticket_factories import TicketFactoryRegistry
from backend.domain.models.ticket import TicketModel
from backend.services.exceptions import TicketNotFoundError
from backend.services.observers.base import TicketSubject
from backend.services.observers.events import TicketEvent
from backend.services.observers.audit_log_observer import AuditLogObserver
from backend.services.observers.email_notifier_observer import EmailNotifierObserver

logger = logging.getLogger(__name__)


class ServiceDeskFacade:
    """
    Patrón Facade (GoF):
    Proporciona una interfaz de alto nivel unificada y simplificada que oculta
    la complejidad de los múltiples subsistemas internos (Fábricas, Repositorios,
    Máquina de Estados y Bus de Observadores).

    Los controladores/routers de FastAPI interactúan EXCLUSIVAMENTE con esta fachada.
    """

    def __init__(
        self,
        repository: TicketRepositoryInterface,
        subject: Optional[TicketSubject] = None,
        email_notifier: Optional[EmailNotifierObserver] = None,
    ):
        self._repository = repository
        self._email_notifier = email_notifier or EmailNotifierObserver()
        
        # Configuración del bus de observadores
        if subject is not None:
            self._subject = subject
        else:
            self._subject = TicketSubject()
            self._subject.attach(AuditLogObserver(self._repository))
            self._subject.attach(self._email_notifier)

    @property
    def email_notifier(self) -> EmailNotifierObserver:
        return self._email_notifier

    def create_ticket(self, request: TicketCreateRequest) -> TicketResponse:
        """
        Orquesta el caso de uso: Creación de Ticket.
        1. Resuelve la fábrica polimórfica según categoría (Factory Method).
        2. Aplica reglas de negocio y metadatos específicos.
        3. Persiste a través del repositorio (Repository).
        4. Despacha evento de creación a los observadores (Observer).
        """
        logger.info(f"Procesando creación de ticket para categoría '{request.category.value}'")
        
        # 1 y 2: Factory Method
        factory = TicketFactoryRegistry.get_factory(request.category.value)
        ticket_entity: TicketModel = factory.create_ticket(request)

        # 3: Repository
        created_ticket = self._repository.create(ticket_entity)

        # 4: Observer
        event = TicketEvent(
            ticket_id=created_ticket.id,
            event_type="TICKET_CREATED",
            old_status=None,
            new_status=created_ticket.status,
            details=f"Ticket creado bajo categoría {created_ticket.category} con prioridad {created_ticket.priority}"
        )
        self._subject.notify(event)

        # Cargar relaciones frescas para el DTO
        persisted = self._repository.get_by_id(created_ticket.id)
        return TicketResponse.model_validate(persisted or created_ticket)

    def change_ticket_status(self, ticket_id: int, request: TicketStatusUpdateRequest) -> TicketResponse:
        """
        Orquesta el caso de uso: Transición de Estado de un Ticket.
        1. Consulta la entidad existente en el repositorio.
        2. Ejecuta la transición validada por la máquina de estados (State Pattern).
        3. Persiste el nuevo estado a través del repositorio.
        4. Notifica a los observadores suscritos (Observer Pattern).
        """
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        old_status = ticket.status
        target_status = request.target_status.value

        # 2: State Pattern (lanza InvalidStateTransitionError si no está permitida)
        ticket.transition_to(target_status)

        # 3: Repository
        updated_ticket = self._repository.update(ticket)

        # 4: Observer Pattern
        details_msg = request.reason or f"Transición de estado de {old_status} a {target_status}"
        event = TicketEvent(
            ticket_id=updated_ticket.id,
            event_type="STATUS_CHANGED",
            old_status=old_status,
            new_status=updated_ticket.status,
            details=details_msg
        )
        self._subject.notify(event)

        # Cargar relaciones frescas para el DTO
        persisted = self._repository.get_by_id(updated_ticket.id)
        return TicketResponse.model_validate(persisted or updated_ticket)

    def get_ticket(self, ticket_id: int) -> TicketResponse:
        """Recupera la información completa de un ticket o lanza excepción controlada."""
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        return TicketResponse.model_validate(ticket)

    def list_tickets(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TicketResponse]:
        """Consulta tickets con filtros opcionales de categoría y estado."""
        tickets = self._repository.get_all(category=category, status=status, skip=skip, limit=limit)
        return [TicketResponse.model_validate(t) for t in tickets]

    def get_ticket_audit_logs(self, ticket_id: int) -> List[AuditLogResponse]:
        """Recupera el historial cronológico de auditoría de un ticket."""
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        logs = self._repository.get_audit_logs(ticket_id)
        return [AuditLogResponse.model_validate(log) for log in logs]

    def delete_ticket(self, ticket_id: int) -> bool:
        """Elimina un ticket si existe."""
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        return self._repository.delete(ticket_id)

    def get_sent_notifications(self) -> List[Dict[str, Any]]:
        """Retorna el registro en memoria de correos despachados por EmailNotifierObserver."""
        return self._email_notifier.sent_emails
