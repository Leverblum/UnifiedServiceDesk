"""
Implementación del Patrón Facade (GoF) para el Subsistema Service Desk Universitario.
Punto único de orquestación de reglas de negocio, creación polimórfica,
gestión de usuarios (RBAC), asignación a especialistas de TI/Académicos, máquina de estados,
persistencia desacoplada y despacho de eventos.

Seguridad (DEF-01 / DEF-02):
- Todas las contraseñas se hashean con Argon2id antes de persistir.
- El seed usa SEED_DEFAULT_PASSWORD de settings (variable de entorno).
- Nunca se persiste ni retorna texto plano de contraseña.
"""

from typing import List, Optional, Dict, Any
import logging
from backend.repositories.base import TicketRepositoryInterface
from backend.repositories.user_repository import UserRepositoryInterface
from backend.domain.schemas.ticket import (
    TicketCreateRequest,
    TicketStatusUpdateRequest,
    TicketAssignRequest,
    TicketResponse,
    AuditLogResponse,
)
from backend.domain.schemas.user import (
    UserCreateRequest,
    UserResponse,
    UserRole,
    TokenResponse,
)
from backend.domain.factories.ticket_factories import TicketFactoryRegistry
from backend.domain.models.ticket import TicketModel
from backend.domain.models.user import UserModel
from backend.services.exceptions import (
    TicketNotFoundError,
    UserNotFoundError,
    UnauthorizedRoleActionError,
)
from backend.services.observers.base import TicketSubject
from backend.services.observers.events import TicketEvent
from backend.services.observers.audit_log_observer import AuditLogObserver
from backend.services.observers.email_notifier_observer import EmailNotifierObserver
from backend.core.security import hash_password, verify_password, create_access_token
from backend.core.config import settings

logger = logging.getLogger(__name__)


class ServiceDeskFacade:
    """
    Patrón Facade (GoF):
    Proporciona una interfaz unificada de alto nivel que oculta la complejidad
    de los múltiples subsistemas internos (Fábricas polimórficas, Repositorios,
    Máquina de Estados, RBAC y Bus de Observadores).

    Los controladores/routers de FastAPI interactúan EXCLUSIVAMENTE con esta fachada.
    """

    def __init__(
        self,
        repository: TicketRepositoryInterface,
        user_repository: Optional[UserRepositoryInterface] = None,
        subject: Optional[TicketSubject] = None,
        email_notifier: Optional[EmailNotifierObserver] = None,
    ):
        self._repository = repository
        self._user_repository = user_repository
        self._email_notifier = email_notifier or EmailNotifierObserver()

        if subject is not None:
            self._subject = subject
        else:
            self._subject = TicketSubject()
            self._subject.attach(AuditLogObserver(self._repository))
            self._subject.attach(self._email_notifier)

    @property
    def email_notifier(self) -> EmailNotifierObserver:
        return self._email_notifier

    # ==========================================
    # AUTENTICACIÓN CON JWT (DEF-03)
    # ==========================================

    def login(self, email: str, password: str) -> TokenResponse:
        """
        Autentica al usuario y emite un JWT firmado (DEF-03).
        Verifica contraseña con Argon2id (DEF-01).
        Nunca expone el hash de contraseña en la respuesta.

        Returns:
            TokenResponse con access_token (JWT Bearer) y datos básicos del usuario.

        Raises:
            HTTPException(401): Si email o contraseña son incorrectos.
        """
        from fastapi import HTTPException, status

        if not self._user_repository:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Repositorio de usuarios no disponible.")

        db_user = self._user_repository.get_by_email(email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(data={"sub": str(db_user.id), "role": db_user.role})
        user_response = UserResponse.model_validate(db_user)
        return TokenResponse(access_token=token, token_type="bearer", user=user_response)

    def get_current_user_from_token(self, token: str) -> UserResponse:
        """
        Extrae y valida el usuario del JWT. Usado por get_current_user dependency.
        """
        from fastapi import HTTPException, status
        from backend.core.security import decode_access_token

        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin subject.")
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Subject inválido en token.")

        if not self._user_repository:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Repositorio de usuarios no disponible.")

        db_user = self._user_repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")
        return UserResponse.model_validate(db_user)

    # ==========================================
    # GESTIÓN DE USUARIOS Y ROLES (RBAC UNIVERSITARIO)
    # ==========================================

    def seed_default_users(self) -> List[UserResponse]:
        """
        Siembra los 5 usuarios de prueba universitarios para el MVP.
        Las contraseñas se toman de SEED_DEFAULT_PASSWORD (variable de entorno)
        y se hashean con Argon2id antes de persistir. (DEF-01 / DEF-02)
        """
        if not self._user_repository:
            return []

        # Cada usuario recibe un hash independiente (salt único por usuario) — DEF-01
        def _make_seed_user(email, full_name, role, department):
            return UserModel(
                email=email,
                full_name=full_name,
                role=role,
                department=department,
                password=hash_password(settings.SEED_DEFAULT_PASSWORD),
            )

        seed_data = [
            _make_seed_user(
                "admin@universidad.edu.co",
                "Ing. Andrés Valenzuela",
                UserRole.ADMIN.value,
                "Dirección General de Tecnologías & Admisiones",
            ),
            _make_seed_user(
                "estudiante.camilo@universidad.edu.co",
                "Camilo Torres",
                UserRole.STUDENT.value,
                "Facultad de Ingeniería de Sistemas (Pregrado)",
            ),
            _make_seed_user(
                "profesora.helena@universidad.edu.co",
                "Dra. Helena Restrepo",
                UserRole.STAFF.value,
                "Departamento de Ciencias Básicas & Aulas de Clase",
            ),
            _make_seed_user(
                "soporte.estudiantes@universidad.edu.co",
                "Mateo Rivas (Soporte Estudiantes)",
                UserRole.IT_STUDENT_SUPPORT.value,
                "Mesa de Servicios Académicos & Admisiones",
            ),
            _make_seed_user(
                "soporte.personal@universidad.edu.co",
                "Ing. Laura Méndez (Soporte Personal)",
                UserRole.IT_STAFF_SUPPORT.value,
                "Infraestructura Tecnológica, Campus & Aulas",
            ),
        ]

        created_count = 0
        for u in seed_data:
            if not self._user_repository.get_by_email(u.email):
                self._user_repository.create(u)
                created_count += 1

        if created_count:
            logger.info("Sembrados %s usuarios de prueba universitarios (contraseñas hasheadas).", created_count)
        return self.list_users()

    def list_users(self, role: Optional[str] = None) -> List[UserResponse]:
        """Consulta usuarios del sistema con filtro opcional por rol."""
        if not self._user_repository:
            return []
        users = self._user_repository.get_all(role=role)
        return [UserResponse.model_validate(u) for u in users]

    def get_user(self, user_id: int) -> UserResponse:
        """Obtiene un usuario específico por su ID."""
        if not self._user_repository:
            raise UserNotFoundError(str(user_id))
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        return UserResponse.model_validate(user)

    def get_user_by_email(self, email: str) -> UserResponse:
        """Busca un usuario por su correo."""
        if not self._user_repository:
            raise UserNotFoundError(email)
        user = self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(email)
        return UserResponse.model_validate(user)

    def create_user(self, request: UserCreateRequest) -> UserResponse:
        """
        Crea un nuevo usuario en el sistema.
        La contraseña se hashea con Argon2id antes de persistir. (DEF-01)
        Nunca se devuelve la contraseña en la respuesta.
        """
        if not self._user_repository:
            raise RuntimeError("UserRepository no está disponible.")

        existing = self._user_repository.get_by_email(request.email)
        if existing:
            raise ValueError(f"Ya existe un usuario con el correo institucional: {request.email}")

        hashed = hash_password(request.password)
        user_entity = UserModel(
            email=request.email,
            full_name=request.full_name,
            role=request.role.value,
            department=request.department,
            password=hashed,
        )
        saved = self._user_repository.create(user_entity)
        return UserResponse.model_validate(saved)

    # ==========================================
    # CASOS DE USO DE TICKETS
    # ==========================================

    def create_ticket(self, request: TicketCreateRequest) -> TicketResponse:
        """
        Orquesta el caso de uso: Creación de Ticket.
        1. Resuelve la fábrica polimórfica según categoría (Factory Method).
        2. Aplica reglas de negocio y metadatos específicos.
        3. Persiste a través del repositorio (Repository).
        4. Despacha evento de creación a los observadores (Observer).
        """
        logger.info(
            "Procesando creación de ticket universitario para categoría '%s'",
            request.category.value
        )

        creator_name = None
        creator_email = None
        if request.created_by_id and self._user_repository:
            creator = self._user_repository.get_by_id(request.created_by_id)
            if creator:
                creator_name = creator.full_name
                creator_email = creator.email

        factory = TicketFactoryRegistry.get_factory(request.category.value)
        ticket_entity: TicketModel = factory.create_ticket(request)

        created_ticket = self._repository.create(ticket_entity)

        event = TicketEvent(
            ticket_id=created_ticket.id,
            event_type="TICKET_CREATED",
            old_status=None,
            new_status=created_ticket.status,
            details=(
                f"Ticket creado bajo categoría {created_ticket.category} "
                f"con prioridad {created_ticket.priority}"
            ),
            user_name=creator_name,
            user_email=creator_email,
        )
        self._subject.notify(event)

        persisted = self._repository.get_by_id(created_ticket.id)
        return TicketResponse.model_validate(persisted or created_ticket)

    def assign_ticket(self, ticket_id: int, request: TicketAssignRequest) -> TicketResponse:
        """
        Orquesta la asignación de Ticket a Especialista de TI.
        Solo permite roles: IT_STUDENT_SUPPORT, IT_STAFF_SUPPORT, ADMIN.
        """
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        assignee_name = None
        assignee_email = None

        allowed_tech_roles = [
            UserRole.IT_STUDENT_SUPPORT.value,
            UserRole.IT_STAFF_SUPPORT.value,
            UserRole.ADMIN.value,
        ]

        if request.assigned_to_id is not None:
            if not self._user_repository:
                raise RuntimeError("UserRepository no disponible para validar especialista.")
            tech = self._user_repository.get_by_id(request.assigned_to_id)
            if not tech:
                raise UserNotFoundError(str(request.assigned_to_id))
            if tech.role not in allowed_tech_roles:
                raise UnauthorizedRoleActionError(
                    tech.role, "Ser asignado como especialista a cargo del caso"
                )

            ticket.assigned_to_id = tech.id
            assignee_name = tech.full_name
            assignee_email = tech.email

            if ticket.status == "OPEN":
                ticket.transition_to("IN_PROCESS")
        else:
            ticket.assigned_to_id = None

        updated_ticket = self._repository.update(ticket)

        creator_name = updated_ticket.creator.full_name if updated_ticket.creator else "Usuario"
        creator_email = updated_ticket.creator.email if updated_ticket.creator else None

        reason_text = request.reason or (
            f"Caso asignado a {assignee_name}" if assignee_name else "Caso desasignado"
        )
        event = TicketEvent(
            ticket_id=updated_ticket.id,
            event_type="TICKET_ASSIGNED",
            old_status="OPEN" if ticket.status == "IN_PROCESS" else ticket.status,
            new_status=updated_ticket.status,
            details=reason_text,
            user_name=creator_name,
            user_email=creator_email,
            assignee_name=assignee_name,
            assignee_email=assignee_email,
        )
        self._subject.notify(event)

        persisted = self._repository.get_by_id(updated_ticket.id)
        return TicketResponse.model_validate(persisted or updated_ticket)

    def change_ticket_status(self, ticket_id: int, request: TicketStatusUpdateRequest) -> TicketResponse:
        """
        Orquesta el caso de uso: Transición de Estado de un Ticket.
        RBAC:
        - STUDENT y STAFF solo pueden solicitar reapertura a OPEN.
        - IT_STUDENT_SUPPORT, IT_STAFF_SUPPORT y ADMIN avanzan estados.
        """
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        old_status = ticket.status
        target_status = request.target_status.value

        if request.user_id and self._user_repository:
            user = self._user_repository.get_by_id(request.user_id)
            if user and user.role in [UserRole.STUDENT.value, UserRole.STAFF.value]:
                if target_status not in ["OPEN"]:
                    raise UnauthorizedRoleActionError(
                        user.role,
                        (
                            f"Transicionar ticket a '{target_status}'. "
                            "Como solicitante solo puedes solicitar reapertura del caso a 'OPEN'."
                        ),
                    )

        ticket.transition_to(target_status)
        updated_ticket = self._repository.update(ticket)

        creator_name = updated_ticket.creator.full_name if updated_ticket.creator else "Usuario"
        creator_email = updated_ticket.creator.email if updated_ticket.creator else None
        assignee_name = updated_ticket.assignee.full_name if updated_ticket.assignee else None
        assignee_email = updated_ticket.assignee.email if updated_ticket.assignee else None

        details_msg = request.reason or f"Transición de estado de {old_status} a {target_status}"
        event = TicketEvent(
            ticket_id=updated_ticket.id,
            event_type="STATUS_CHANGED",
            old_status=old_status,
            new_status=updated_ticket.status,
            details=details_msg,
            user_name=creator_name,
            user_email=creator_email,
            assignee_name=assignee_name,
            assignee_email=assignee_email,
        )
        self._subject.notify(event)

        persisted = self._repository.get_by_id(updated_ticket.id)
        return TicketResponse.model_validate(persisted or updated_ticket)

    def get_ticket(self, ticket_id: int) -> TicketResponse:
        """Recupera la información completa de un ticket."""
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        return TicketResponse.model_validate(ticket)

    def list_tickets(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        created_by_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        unassigned_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TicketResponse]:
        """Consulta tickets con filtros opcionales."""
        tickets = self._repository.get_all(
            category=category,
            status=status,
            created_by_id=created_by_id,
            assigned_to_id=assigned_to_id,
            unassigned_only=unassigned_only,
            skip=skip,
            limit=limit,
        )
        return [TicketResponse.model_validate(t) for t in tickets]

    def get_ticket_audit_logs(self, ticket_id: int) -> List[AuditLogResponse]:
        """Recupera el historial cronológico de auditoría de un ticket."""
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        logs = self._repository.get_audit_logs(ticket_id)
        return [AuditLogResponse.model_validate(log) for log in logs]

    def delete_ticket(self, ticket_id: int) -> bool:
        """Elimina un ticket si existe."""
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        return self._repository.delete(ticket_id)

    def get_sent_notifications(self) -> List[Dict[str, Any]]:
        """Retorna el registro en memoria de correos despachados por EmailNotifierObserver."""
        return self._email_notifier.sent_emails

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas agregadas del service desk universitario (RF-07 / CP-08).
        """
        all_tickets = self._repository.get_all(limit=10000)
        total = len(all_tickets)

        by_status: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}

        for t in all_tickets:
            by_status[t.status] = by_status.get(t.status, 0) + 1
            by_category[t.category] = by_category.get(t.category, 0) + 1
            by_priority[t.priority] = by_priority.get(t.priority, 0) + 1

        open_count = by_status.get("OPEN", 0)
        in_process_count = by_status.get("IN_PROCESS", 0)
        resolved_count = by_status.get("RESOLVED", 0)
        closed_count = by_status.get("CLOSED", 0)

        resolution_rate = (
            round((resolved_count + closed_count) / total * 100, 2) if total > 0 else 0.0
        )

        return {
            "total_tickets": total,
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority,
            "open_count": open_count,
            "in_process_count": in_process_count,
            "resolved_count": resolved_count,
            "closed_count": closed_count,
            "resolution_rate_pct": resolution_rate,
        }
