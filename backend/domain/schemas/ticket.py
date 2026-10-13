"""
Esquemas de validación y DTOs (Data Transfer Objects) con Pydantic.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TicketCategory(str, Enum):
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    ACCESS = "ACCESS"


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROCESS = "IN_PROCESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TicketCreateRequest(BaseModel):
    """
    DTO para la creación de un nuevo Ticket.
    """
    title: str = Field(..., min_length=3, max_length=255, description="Título conciso del ticket")
    description: str = Field(..., min_length=5, description="Descripción detallada de la incidencia")
    category: TicketCategory = Field(..., description="Categoría que determina la factoría a instanciar")
    priority: Optional[TicketPriority] = Field(None, description="Prioridad opcional; si no se especifica, la fábrica asigna una por defecto")
    specific_metadata: Dict[str, Any] = Field(default_factory=dict, description="Campos específicos requeridos por categoría")


class TicketStatusUpdateRequest(BaseModel):
    """
    DTO para la transición de estado del Ticket.
    """
    target_status: TicketStatus = Field(..., description="Estado destino a transicionar")
    reason: Optional[str] = Field(None, description="Motivo o comentario adicional para el registro de auditoría")


class AuditLogResponse(BaseModel):
    """
    DTO de respuesta para entradas de auditoría.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    event_type: str
    old_status: Optional[str] = None
    new_status: str
    details: Optional[str] = None
    created_at: datetime


class TicketResponse(BaseModel):
    """
    DTO de respuesta para información completa de un Ticket.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    specific_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    audit_logs: Optional[List[AuditLogResponse]] = None
