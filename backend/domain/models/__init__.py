"""
Exportación de modelos ORM del dominio.
"""

from backend.domain.models.ticket import TicketModel
from backend.domain.models.audit_log import AuditLogModel

__all__ = ["TicketModel", "AuditLogModel"]
