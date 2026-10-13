"""
Modelo ORM de SQLAlchemy para la entidad Ticket.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


class TicketModel(Base):
    """
    Representación persistente del Ticket en la base de datos relacional.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)     # HARDWARE, SOFTWARE, ACCESS
    priority = Column(String(20), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), nullable=False, default="OPEN", index=True) # OPEN, IN_PROCESS, RESOLVED, CLOSED
    
    # Almacenamiento polimórfico de metadatos según la fábrica de ticket
    # Ej: { "serial_number": "HW-991" } o { "software_name": "Postgres", "version": "16" }
    specific_metadata = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relación con auditoría
    audit_logs = relationship("AuditLogModel", back_populates="ticket", cascade="all, delete-orphan")

    @property
    def current_state(self):
        from backend.domain.states.ticket_states import get_state_instance
        return get_state_instance(self.status)

    def transition_to(self, target_status: str):
        """
        Transiciona al estado destino utilizando el patrón State (GoF),
        asegurando que solo se apliquen transiciones válidas según la clase de estado actual.
        """
        new_state = self.current_state.transition_to(target_status, self)
        self.status = new_state.name
        return new_state

    def __repr__(self) -> str:
        return f"<TicketModel(id={self.id}, title='{self.title}', category='{self.category}', status='{self.status}')>"
