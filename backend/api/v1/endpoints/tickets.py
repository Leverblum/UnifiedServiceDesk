"""
Endpoints de la API v1 para la gestión de Tickets.
REGLA ARQUITECTÓNICA ESTRICTA:
Está terminantemente prohibido acceder a la base de datos o modelos de SQLAlchemy aquí.
Toda interacción se canaliza única y exclusivamente a través de ServiceDeskFacade.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from backend.api.dependencies import get_service_desk_facade
from backend.services.service_desk_facade import ServiceDeskFacade
from backend.domain.schemas.ticket import (
    TicketCreateRequest,
    TicketStatusUpdateRequest,
    TicketResponse,
    AuditLogResponse,
)
from backend.services.exceptions import TicketNotFoundError
from backend.domain.states.exceptions import InvalidStateTransitionError
from backend.domain.factories.exceptions import FactoryValidationError

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo ticket (Factory Method + Observer)"
)
def create_ticket(
    request: TicketCreateRequest,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> TicketResponse:
    """
    Crea un ticket procesándolo polimórficamente a través de Factory Method.
    Registra el evento de auditoría y notifica vía Observer.
    """
    try:
        return facade.create_ticket(request)
    except FactoryValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[TicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar tickets con filtros y paginación"
)
def list_tickets(
    category: Optional[str] = Query(None, description="Filtro opcional por categoría (HARDWARE, SOFTWARE, ACCESS)"),
    ticket_status: Optional[str] = Query(None, alias="status", description="Filtro por estado (OPEN, IN_PROCESS, RESOLVED, CLOSED)"),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Límite de registros por página"),
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> List[TicketResponse]:
    """Recupera la lista de tickets aplicando filtros opcionales."""
    return facade.list_tickets(category=category, status=ticket_status, skip=skip, limit=limit)


@router.get(
    "/notifications/sent",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Historial de correos simulados despachados (EmailNotifierObserver)"
)
def list_sent_notifications(
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> List[Dict[str, Any]]:
    """Permite auditar las notificaciones que fueron enviadas por el observador de correo."""
    return facade.get_sent_notifications()


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de un ticket específico"
)
def get_ticket(
    ticket_id: int,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> TicketResponse:
    """Obtiene los datos completos de un ticket por su identificador primario."""
    try:
        return facade.get_ticket(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Transicionar estado del ticket (State Pattern + Observer)"
)
def change_ticket_status(
    ticket_id: int,
    request: TicketStatusUpdateRequest,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> TicketResponse:
    """
    Ejecuta una transición de estado validada por la máquina de estados.
    Despacha notificaciones a los observadores ante el cambio.
    """
    try:
        return facade.change_ticket_status(ticket_id, request)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{ticket_id}/audit-logs",
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar historial de auditoría del ticket"
)
def get_ticket_audit_logs(
    ticket_id: int,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> List[AuditLogResponse]:
    """Obtiene el historial cronológico de eventos registrados para el ticket."""
    try:
        return facade.get_ticket_audit_logs(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un ticket del sistema"
)
def delete_ticket(
    ticket_id: int,
    facade: ServiceDeskFacade = Depends(get_service_desk_facade)
) -> None:
    """Elimina físicamente un ticket y sus logs en cascada."""
    try:
        facade.delete_ticket(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
