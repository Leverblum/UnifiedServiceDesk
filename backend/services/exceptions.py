"""
Excepciones de la capa de servicios.
"""

class TicketNotFoundError(Exception):
    """Se lanza cuando un ticket solicitado no existe en el sistema."""
    def __init__(self, ticket_id: int):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket con ID {ticket_id} no fue encontrado.")
