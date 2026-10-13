"""
Implementaciones concretas del Patrón State (GoF) para el ciclo de vida del Ticket:
- OpenState
- InProcessState
- ResolvedState
- ClosedState
"""

from typing import List, TYPE_CHECKING
from backend.domain.states.base import TicketState

if TYPE_CHECKING:
    from backend.domain.models.ticket import TicketModel


class OpenState(TicketState):
    """
    Estado inicial de un ticket recién creado.
    Solo puede ser tomado en atención pasando a InProcessState.
    """
    @property
    def name(self) -> str:
        return "OPEN"

    def allowed_transitions(self) -> List[str]:
        return ["IN_PROCESS"]

    def start_progress(self, context: "TicketModel") -> "TicketState":
        return InProcessState()


class InProcessState(TicketState):
    """
    Estado en el que un técnico se encuentra trabajando activamente en la incidencia.
    Puede transicionar a ResolvedState o retornar a OpenState si se desasigna.
    """
    @property
    def name(self) -> str:
        return "IN_PROCESS"

    def allowed_transitions(self) -> List[str]:
        return ["RESOLVED", "OPEN"]

    def resolve(self, context: "TicketModel") -> "TicketState":
        return ResolvedState()

    def reopen(self, context: "TicketModel") -> "TicketState":
        return OpenState()


class ResolvedState(TicketState):
    """
    Estado en el que la solución fue propuesta o implementada.
    El usuario o técnico puede confirmarla cerrando el ticket (ClosedState)
    o rechazarla devolviéndolo a InProcessState.
    """
    @property
    def name(self) -> str:
        return "RESOLVED"

    def allowed_transitions(self) -> List[str]:
        return ["CLOSED", "IN_PROCESS"]

    def close(self, context: "TicketModel") -> "TicketState":
        return ClosedState()

    def start_progress(self, context: "TicketModel") -> "TicketState":
        return InProcessState()

    def reopen(self, context: "TicketModel") -> "TicketState":
        return InProcessState()


class ClosedState(TicketState):
    """
    Estado final o archivado del ticket.
    Permite únicamente reapertura formal en casos excepcionales retornando a OpenState.
    """
    @property
    def name(self) -> str:
        return "CLOSED"

    def allowed_transitions(self) -> List[str]:
        return ["OPEN"]

    def reopen(self, context: "TicketModel") -> "TicketState":
        return OpenState()


def get_state_instance(status_name: str) -> TicketState:
    """
    Función de mapeo para hidratar la instancia de estado adecuada
    a partir del valor persistido en el modelo.
    """
    mapping = {
        "OPEN": OpenState,
        "IN_PROCESS": InProcessState,
        "RESOLVED": ResolvedState,
        "CLOSED": ClosedState,
    }
    status_upper = status_name.upper() if status_name else "OPEN"
    state_cls = mapping.get(status_upper)
    if not state_cls:
        raise ValueError(f"Estado de ticket desconocido: '{status_name}'")
    return state_cls()
