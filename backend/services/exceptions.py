"""
Excepciones de la capa de servicios.
"""

class TicketNotFoundError(Exception):
    """Se lanza cuando un ticket solicitado no existe en el sistema."""
    def __init__(self, ticket_id: int):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket con ID {ticket_id} no fue encontrado.")


class UserNotFoundError(Exception):
    """Se lanza cuando un usuario solicitado no existe en el sistema."""
    def __init__(self, user_id_or_email: str):
        self.identifier = user_id_or_email
        super().__init__(f"Usuario '{user_id_or_email}' no fue encontrado.")


class UnauthorizedRoleActionError(Exception):
    """Se lanza cuando un usuario intenta realizar una acción no permitida para su rol (RBAC)."""
    def __init__(self, role: str, action: str):
        self.role = role
        self.action = action
        super().__init__(f"El rol '{role}' no tiene autorización para realizar la acción: '{action}'.")
