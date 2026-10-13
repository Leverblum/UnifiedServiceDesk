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
    event_type: str        # TICKET_CREATED, STATUS_CHANGED, TICKET_DELETED
    old_status: Optional[str]
    new_status: str
    details: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)
