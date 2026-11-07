"""
Modelo ORM de SQLAlchemy para la entidad Usuario (User / RBAC).
Soporta los roles universitarios: STUDENT, STAFF, IT_STUDENT_SUPPORT, IT_STAFF_SUPPORT, ADMIN.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base


class UserModel(Base):
    """
    Entidad de persistencia para los usuarios del sistema Unified Service Desk.
    Controla el control de acceso basado en roles (RBAC).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="STUDENT", index=True)
    department = Column(String(100), nullable=True)
    password = Column(String(255), nullable=False, default='12345')
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)

    # Relaciones con Tickets
    created_tickets = relationship(
        "TicketModel",
        foreign_keys="[TicketModel.created_by_id]",
        back_populates="creator"
    )

    assigned_tickets = relationship(
        "TicketModel",
        foreign_keys="[TicketModel.assigned_to_id]",
        back_populates="assignee"
    )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email}', role='{self.role}', name='{self.full_name}')>"
