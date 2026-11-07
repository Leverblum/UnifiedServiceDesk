"""
Definición de eventos de dominio para el patrón Observer.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class TicketEvent:
    """
    Objeto de Transferencia de Evento inmutable.
    Encapsula el estado de la mutación para que los observadores
    reaccionen sin acoplarse directamente al modelo ORM.
    """
    ticket_id: int
    event_type: str        # TICKET_CREATED, STATUS_CHANGED, TICKET_ASSIGNED, TICKET_DELETED
    old_status: Optional[str]
    new_status: str
    details: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    assignee_name: Optional[str] = None
    assignee_email: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)
