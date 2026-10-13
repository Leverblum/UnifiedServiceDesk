"""
Definición de la interfaz base para el Patrón State (GoF).
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.domain.models.ticket import TicketModel


class TicketState(ABC):
    """
    Patrón State (GoF):
    Interfaz abstracta que define el comportamiento dependiente del estado para un Ticket.
    Cada subclase representa un estado concreto y encapsula las reglas de transición válidas.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre canónico del estado (ej. OPEN, IN_PROCESS, etc.)."""
        pass

    @abstractmethod
    def allowed_transitions(self) -> List[str]:
        """Lista de nombres de estados hacia los cuales es válido transicionar."""
        pass

    def transition_to(self, target_status: str, context: "TicketModel") -> "TicketState":
        """
        Orquesta la transición hacia el estado objetivo delegando en el método
        específico del estado concreto.
        """
        target = target_status.upper()
        if target not in self.allowed_transitions():
            from backend.domain.states.exceptions import InvalidStateTransitionError
            raise InvalidStateTransitionError(
                current_status=self.name,
                target_status=target,
                allowed=self.allowed_transitions()
            )

        # Invocación de la transición semántica
        if target == "OPEN":
            return self.reopen(context)
        elif target == "IN_PROCESS":
            return self.start_progress(context)
        elif target == "RESOLVED":
            return self.resolve(context)
        elif target == "CLOSED":
            return self.close(context)
        else:
            from backend.domain.states.exceptions import InvalidStateTransitionError
            raise InvalidStateTransitionError(self.name, target, self.allowed_transitions())

    def start_progress(self, context: "TicketModel") -> "TicketState":
        from backend.domain.states.exceptions import InvalidStateTransitionError
        raise InvalidStateTransitionError(self.name, "IN_PROCESS", self.allowed_transitions())

    def resolve(self, context: "TicketModel") -> "TicketState":
        from backend.domain.states.exceptions import InvalidStateTransitionError
        raise InvalidStateTransitionError(self.name, "RESOLVED", self.allowed_transitions())

    def close(self, context: "TicketModel") -> "TicketState":
        from backend.domain.states.exceptions import InvalidStateTransitionError
        raise InvalidStateTransitionError(self.name, "CLOSED", self.allowed_transitions())

    def reopen(self, context: "TicketModel") -> "TicketState":
        from backend.domain.states.exceptions import InvalidStateTransitionError
        raise InvalidStateTransitionError(self.name, "OPEN", self.allowed_transitions())
