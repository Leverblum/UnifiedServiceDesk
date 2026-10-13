"""
Excepciones de dominio para el ciclo de vida y máquina de estados de Tickets.
"""

class InvalidStateTransitionError(ValueError):
    """
    Se lanza cuando se intenta realizar una transición de estado no permitida
    según la política del estado actual del Ticket.
    """
    def __init__(self, current_status: str, target_status: str, allowed: list):
        self.current_status = current_status
        self.target_status = target_status
        self.allowed = allowed
        super().__init__(
            f"Transición inválida: no se puede cambiar de '{current_status}' a '{target_status}'. "
            f"Transiciones permitidas desde este estado: {allowed}."
        )
