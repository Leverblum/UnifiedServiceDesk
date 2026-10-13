"""
Modelo ORM de SQLAlchemy para el Registro de Auditoría (Audit Log).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base


class AuditLogModel(Base):
    """
    Entidad de registro para el patrón Observer (AuditLogObserver).
    Persiste cada cambio de estado y evento relevante en el ciclo de vida del ticket.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)   # CREATED, STATUS_CHANGED, COMMENTED
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    ticket = relationship("TicketModel", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLogModel(id={self.id}, ticket_id={self.ticket_id}, event='{self.event_type}', new_status='{self.new_status}')>"
