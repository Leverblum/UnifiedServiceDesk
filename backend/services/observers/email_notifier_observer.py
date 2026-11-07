"""
Observador Concreto: EmailNotifierObserver.
Simula el despacho de notificaciones por correo electrónico ante cambios en tickets.
"""

import logging
from typing import List, Dict, Any
from backend.services.observers.base import TicketObserver
from backend.services.observers.events import TicketEvent

logger = logging.getLogger(__name__)


class EmailNotifierObserver(TicketObserver):
    """
    Patrón Observer (GoF) - Observador Concreto:
    Simula el envío de correos electrónicos a los interesados (usuario solicitante y equipo de TI)
    ante transiciones de estado, asignaciones o creación de incidencias.
    Mantiene un historial en memoria de los correos despachados para fines de depuración/inspección.
    """
    _sent_emails_history: List[Dict[str, Any]] = []

    def __init__(self):
        pass

    @property
    def sent_emails(self) -> List[Dict[str, Any]]:
        return list(self._sent_emails_history)

    @classmethod
    def clear_history(cls) -> None:
        cls._sent_emails_history.clear()

    def update(self, event: TicketEvent) -> None:
        subject = f"[Unified Service Desk] Notificación Ticket #{event.ticket_id} [{event.event_type}]"
        recipient = event.user_email or "usuario@empresa.com"
        
        if event.event_type == "TICKET_CREATED":
            body = (
                f"Estimado/a {event.user_name or 'Usuario'},\n\n"
                f"Su ticket #{event.ticket_id} ha sido registrado exitosamente con estado inicial '{event.new_status}'.\n"
                f"Detalles: {event.details or 'Sin detalles adicionales'}\n\n"
                f"El equipo de Soporte TI revisará su solicitud a la brevedad.\n\n"
                f"Equipo de Soporte TI."
            )
        elif event.event_type == "TICKET_ASSIGNED":
            body = (
                f"Estimado equipo,\n\n"
                f"El ticket #{event.ticket_id} ha sido asignado al especialista: {event.assignee_name or 'Técnico TI'}.\n"
                f"Solicitante: {event.user_name or 'Usuario'}\n"
                f"Observación: {event.details or 'Asignación de ticket'}\n\n"
                f"Equipo de Soporte TI."
            )
            recipient = f"{recipient}, {event.assignee_email or 'soporte@empresa.com'}"
        else:
            body = (
                f"Estimado/a {event.user_name or 'Usuario'},\n\n"
                f"El estado de su ticket #{event.ticket_id} ha cambiado:\n"
                f"Estado previo: {event.old_status or 'N/A'}\n"
                f"Nuevo estado:  {event.new_status}\n"
                f"Observación:   {event.details or 'Transición de estado automática'}\n"
                f"Técnico a cargo: {event.assignee_name or 'Por asignar'}\n\n"
                f"Equipo de Soporte TI."
            )

        email_payload = {
            "ticket_id": event.ticket_id,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "timestamp": event.timestamp.isoformat()
        }

        self._sent_emails_history.append(email_payload)
        logger.info(
            f"[EmailNotifierObserver] Correo simulado despachado para Ticket #{event.ticket_id}:\n"
            f"  Destinatario: {recipient}\n"
            f"  Asunto: {subject}\n"
            f"  Nuevo Estado: {event.new_status}"
        )
