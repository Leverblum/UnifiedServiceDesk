"""
Implementación del Patrón Facade (GoF) para el Subsistema Service Desk Universitario.
Punto único de orquestación de reglas de negocio, creación polimórfica,
gestión de usuarios (RBAC), asignación a especialistas de TI/Académicos, máquina de estados,
persistencia desacoplada y despacho de eventos.
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
        
        # Configuración del bus de observadores
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
    # GESTIÓN DE USUARIOS Y ROLES (RBAC UNIVERSITARIO)
    # ==========================================

    def seed_default_users(self) -> List[UserResponse]:
        """
        Siembra los 5 usuarios de prueba universitarios solicitados para el MVP:
        1. Administrador General (ADMIN)
        2. Estudiante (STUDENT)
        3. Personal de la Universidad (STAFF)
        4. Personal de TI - Soporte Estudiantes (IT_STUDENT_SUPPORT)
        5. Personal de TI - Soporte Personal / Campus (IT_STAFF_SUPPORT)
        """
        if not self._user_repository:
            return []

        seed_data = [
            # 1. Administrador General
            UserModel(
                email="admin@universidad.edu.co",
                full_name="Ing. Andrés Valenzuela",
                role=UserRole.ADMIN.value,
                department="Dirección General de Tecnologías & Admisiones"
            ),
            # 2. Estudiante
            UserModel(
                email="estudiante.camilo@universidad.edu.co",
                full_name="Camilo Torres",
                role=UserRole.STUDENT.value,
                department="Facultad de Ingeniería de Sistemas (Pregrado)"
            ),
            # 3. Personal de la Universidad (Docente / Administrativo)
            UserModel(
                email="profesora.helena@universidad.edu.co",
                full_name="Dra. Helena Restrepo",
                role=UserRole.STAFF.value,
                department="Departamento de Ciencias Básicas & Aulas de Clase"
            ),
            # 4. Personal de TI - Soporte Estudiantes
            UserModel(
                email="soporte.estudiantes@universidad.edu.co",
                full_name="Mateo Rivas (Soporte Estudiantes)",
                role=UserRole.IT_STUDENT_SUPPORT.value,
                department="Mesa de Servicios Académicos & Admisiones"
            ),
            # 5. Personal de TI - Soporte Personal / Infraestructura
            UserModel(
                email="soporte.personal@universidad.edu.co",
                full_name="Ing. Laura Méndez (Soporte Personal)",
                role=UserRole.IT_STAFF_SUPPORT.value,
                department="Infraestructura Tecnológica, Campus & Aulas"
            ),
        ]

        created_count = 0
        for u in seed_data:
            if not self._user_repository.get_by_email(u.email):
                self._user_repository.create(u)
                created_count += 1

        if created_count:
            logger.info("Sembrados exitosamente %s usuarios de prueba universitarios.", created_count)
        return self.list_users()

    def list_users(self, role: Optional[str] = None) -> List[UserResponse]:
        """Consulta usuarios del sistema, con filtro opcional por rol."""
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
        """Busca un usuario por su correo para inicio de sesión."""
        if not self._user_repository:
            raise UserNotFoundError(email)
        user = self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(email)
        return UserResponse.model_validate(user)

    def get_user_model_by_email(self, email: str):
        """Retorna el modelo ORM directamente para validación de contraseña."""
        if not self._user_repository:
            return None
        return self._user_repository.get_by_email(email)

    def create_user(self, request: UserCreateRequest) -> UserResponse:
        """Crea un nuevo usuario en el sistema validando unicidad de correo."""
        if not self._user_repository:
            raise RuntimeError("UserRepository no está disponible.")

        existing = self._user_repository.get_by_email(request.email)
        if existing:
            raise ValueError(f"Ya existe un usuario con el correo institucional: {request.email}")

        user_entity = UserModel(
            email=request.email,
            full_name=request.full_name,
            role=request.role.value,
            department=request.department,
            password=request.password,
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
        logger.info(f"Procesando creación de ticket universitario para categoría '{request.category.value}'")
        
        creator_name = None
        creator_email = None
        if request.created_by_id and self._user_repository:
            creator = self._user_repository.get_by_id(request.created_by_id)
            if creator:
                creator_name = creator.full_name
                creator_email = creator.email

        # 1 y 2: Factory Method
        factory = TicketFactoryRegistry.get_factory(request.category.value)
        ticket_entity: TicketModel = factory.create_ticket(request)

        # 3: Repository
        created_ticket = self._repository.create(ticket_entity)

        # 4: Observer
        event = TicketEvent(
            ticket_id=created_ticket.id,
            event_type="TICKET_CREATED",
            old_status=None,
            new_status=created_ticket.status,
            details=f"Ticket creado bajo categoría {created_ticket.category} con prioridad {created_ticket.priority}",
            user_name=creator_name,
            user_email=creator_email
        )
        self._subject.notify(event)

        persisted = self._repository.get_by_id(created_ticket.id)
        return TicketResponse.model_validate(persisted or created_ticket)

    def assign_ticket(self, ticket_id: int, request: TicketAssignRequest) -> TicketResponse:
        """
        Orquesta la asignación de Ticket a Especialista de TI.
        Valida que el usuario asignado tenga un rol técnico o administrativo:
        - IT_STUDENT_SUPPORT
        - IT_STAFF_SUPPORT
        - ADMIN
        """
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        assignee_name = None
        assignee_email = None

        allowed_tech_roles = [
            UserRole.IT_STUDENT_SUPPORT.value,
            UserRole.IT_STAFF_SUPPORT.value,
            UserRole.ADMIN.value
        ]

        if request.assigned_to_id is not None:
            if not self._user_repository:
                raise RuntimeError("UserRepository no disponible para validar especialista.")
            tech = self._user_repository.get_by_id(request.assigned_to_id)
            if not tech:
                raise UserNotFoundError(str(request.assigned_to_id))
            if tech.role not in allowed_tech_roles:
                raise UnauthorizedRoleActionError(tech.role, "Ser asignado como especialista a cargo del caso")
            
            ticket.assigned_to_id = tech.id
            assignee_name = tech.full_name
            assignee_email = tech.email
            
            # Si el ticket estaba en estado OPEN, se pasa a IN_PROCESS
            if ticket.status == "OPEN":
                ticket.transition_to("IN_PROCESS")
        else:
            ticket.assigned_to_id = None

        updated_ticket = self._repository.update(ticket)

        # Observer Notification
        creator_name = updated_ticket.creator.full_name if updated_ticket.creator else "Usuario"
        creator_email = updated_ticket.creator.email if updated_ticket.creator else None

        reason_text = request.reason or (f"Caso asignado a {assignee_name}" if assignee_name else "Caso desasignado")
        event = TicketEvent(
            ticket_id=updated_ticket.id,
            event_type="TICKET_ASSIGNED",
            old_status="OPEN" if ticket.status == "IN_PROCESS" else ticket.status,
            new_status=updated_ticket.status,
            details=reason_text,
            user_name=creator_name,
            user_email=creator_email,
            assignee_name=assignee_name,
            assignee_email=assignee_email
        )
        self._subject.notify(event)

        persisted = self._repository.get_by_id(updated_ticket.id)
        return TicketResponse.model_validate(persisted or updated_ticket)

    def change_ticket_status(self, ticket_id: int, request: TicketStatusUpdateRequest) -> TicketResponse:
        """
        Orquesta el caso de uso: Transición de Estado de un Ticket.
        Aplica reglas de autorización según el rol (RBAC):
        - Estudiantes (STUDENT) y Personal (STAFF) solo pueden solicitar reapertura formal a OPEN.
        - Equipos de TI (IT_STUDENT_SUPPORT, IT_STAFF_SUPPORT) y ADMIN avanzan estados en el flujo.
        """
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        old_status = ticket.status
        target_status = request.target_status.value

        # Control de acceso basado en roles si se especifica user_id
        if request.user_id and self._user_repository:
            user = self._user_repository.get_by_id(request.user_id)
            if user and user.role in [UserRole.STUDENT.value, UserRole.STAFF.value]:
                if target_status not in ["OPEN"]:
                    raise UnauthorizedRoleActionError(
                        user.role,
                        f"Transicionar ticket a '{target_status}'. Como solicitante solo puedes solicitar reapertura del caso a 'OPEN'."
                    )

        # 2: State Pattern (lanza InvalidStateTransitionError si no está permitida)
        ticket.transition_to(target_status)

        # 3: Repository
        updated_ticket = self._repository.update(ticket)

        # 4: Observer Pattern
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
            assignee_email=assignee_email
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
        limit: int = 100
    ) -> List[TicketResponse]:
        """Consulta tickets con filtros opcionales."""
        tickets = self._repository.get_all(
            category=category,
            status=status,
            created_by_id=created_by_id,
            assigned_to_id=assigned_to_id,
            unassigned_only=unassigned_only,
            skip=skip,
            limit=limit
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
