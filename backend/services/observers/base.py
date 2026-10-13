"""
Definición de las abstracciones del Patrón Observer (GoF).
- TicketObserver (Interfaz Suscriptora)
- TicketSubject (Sujeto Notificador)
"""

from abc import ABC, abstractmethod
from typing import List
import logging
from backend.services.observers.events import TicketEvent

logger = logging.getLogger(__name__)


class TicketObserver(ABC):
    """
    Patrón Observer (GoF) - Interfaz Observador:
    Define el método de actualización que invocará el sujeto ante eventos relevantes.
    """

    @abstractmethod
    def update(self, event: TicketEvent) -> None:
        """Reacciona a la notificación emitida por el TicketSubject."""
        pass


class TicketSubject:
    """
    Patrón Observer (GoF) - Sujeto Concreto (Publisher):
    Mantiene el registro dinámico de observadores suscritos
    y difunde los eventos ocurridos en el ciclo de vida del Ticket.
    """

    def __init__(self):
        self._observers: List[TicketObserver] = []

    def attach(self, observer: TicketObserver) -> None:
        """Suscribe un nuevo observador al bus de eventos."""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observador '{observer.__class__.__name__}' suscrito.")

    def detach(self, observer: TicketObserver) -> None:
        """Cancela la suscripción de un observador."""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"Observador '{observer.__class__.__name__}' desuscrito.")

    def notify(self, event: TicketEvent) -> None:
        """
        Notifica a todos los observadores registrados sobre el evento ocurrido.
        Si un observador falla, captura el error para no romper la transacción principal.
        """
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                logger.error(
                    f"Error en observador '{observer.__class__.__name__}' al procesar {event}: {e}",
                    exc_info=True
                )
