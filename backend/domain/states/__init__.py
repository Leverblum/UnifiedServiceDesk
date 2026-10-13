"""
Exportación de componentes del patrón State.
"""

from backend.domain.states.base import TicketState
from backend.domain.states.exceptions import InvalidStateTransitionError
from backend.domain.states.ticket_states import (
    OpenState,
    InProcessState,
    ResolvedState,
    ClosedState,
    get_state_instance,
)

__all__ = [
    "TicketState",
    "InvalidStateTransitionError",
    "OpenState",
    "InProcessState",
    "ResolvedState",
    "ClosedState",
    "get_state_instance",
]
