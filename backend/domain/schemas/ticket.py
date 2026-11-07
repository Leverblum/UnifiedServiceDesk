"""
Esquemas de validación y DTOs (Data Transfer Objects) con Pydantic.
Adaptado para Servicios Universitarios Integrales:
- Casos de Estudiantes: ACADEMIC_CERTIFICATE, MATRICULA, RADICADO, CAMPUS_VIRTUAL
- Casos de Personal Universitario: HARDWARE, SOFTWARE, ACCESS, INFRASTRUCTURE
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from backend.domain.schemas.user import UserSimpleResponse


class TicketCategory(str, Enum):
    # Servicios y Trámites para Estudiantes
    CERTIFICADO = "CERTIFICADO"           # Certificados de notas, constancias de estudio
    MATRICULA = "MATRICULA"               # Ajustes de matrícula, homologaciones, cupos
    RADICADO = "RADICADO"                 # Solicitudes formales, peticiones académicas
    CAMPUS_VIRTUAL = "CAMPUS_VIRTUAL"     # Aula virtual, correo institucional, Teams

    # Servicios TI para Personal Administrativo y Docente
    HARDWARE = "HARDWARE"                 # Teclado, equipo de cómputo, proyectores en aulas
    SOFTWARE = "SOFTWARE"                 # ERP académico, software de laboratorios
    ACCESS = "ACCESS"                     # Permisos de red, VPN institucional, sistemas


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
    DTO para la creación de un nuevo Ticket de servicio o soporte universitario.
    """
    title: str = Field(..., min_length=3, max_length=255, description="Título conciso del requerimiento o caso")
    description: str = Field(..., min_length=5, description="Descripción detallada de la solicitud o incidencia")
    category: TicketCategory = Field(..., description="Categoría que determina la factoría polimórfica a instanciar")
    priority: Optional[TicketPriority] = Field(None, description="Prioridad opcional; la fábrica asigna una por defecto")
    specific_metadata: Dict[str, Any] = Field(default_factory=dict, description="Campos específicos requeridos por categoría")
    created_by_id: Optional[int] = Field(None, description="ID del usuario solicitante (estudiante o personal)")


class TicketStatusUpdateRequest(BaseModel):
    """
    DTO para la transición de estado del Ticket.
    """
    target_status: TicketStatus = Field(..., description="Estado destino a transicionar")
    reason: Optional[str] = Field(None, description="Motivo o comentario adicional para el registro de auditoría")
    user_id: Optional[int] = Field(None, description="ID del usuario que ejecuta la acción")


class TicketAssignRequest(BaseModel):
    """
    DTO para asignar o reasignar un ticket a un especialista técnico o administrativo.
    """
    assigned_to_id: Optional[int] = Field(..., description="ID del técnico de soporte asignado (o None para desasignar)")
    reason: Optional[str] = Field(None, description="Motivo de la asignación o reasignación")
    assigned_by_user_id: Optional[int] = Field(None, description="ID del usuario o admin que realiza la asignación")


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
    created_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    creator: Optional[UserSimpleResponse] = None
    assignee: Optional[UserSimpleResponse] = None
    created_at: datetime
    updated_at: datetime
    audit_logs: Optional[List[AuditLogResponse]] = None
