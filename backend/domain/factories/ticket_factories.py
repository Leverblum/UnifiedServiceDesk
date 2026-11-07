"""
Implementación del Patrón Factory Method (GoF) para la creación polimórfica de Tickets.
Soporta:
- Trámites y Servicios Estudiantiles:
  * CertificadoTicketFactory (CERTIFICADO)
  * MatriculaTicketFactory (MATRICULA)
  * RadicadoTicketFactory (RADICADO)
  * CampusVirtualTicketFactory (CAMPUS_VIRTUAL)
- Soporte e Infraestructura para Personal Universitario:
  * HardwareTicketFactory (HARDWARE)
  * SoftwareTicketFactory (SOFTWARE)
  * AccessTicketFactory (ACCESS)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from backend.domain.models.ticket import TicketModel
from backend.domain.schemas.ticket import TicketCreateRequest, TicketPriority, TicketCategory
from backend.domain.factories.exceptions import FactoryValidationError


class TicketFactory(ABC):
    """
    Patrón Factory Method (GoF) - Creador Abstracto:
    Declara el método de fábrica que retorna un objeto TicketModel configurado
    con las invariantes de negocio de su categoría.
    """

    @abstractmethod
    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        pass


# ============================================================
# FÁBRICAS PARA TRÁMITES Y SERVICIOS ESTUDIANTILES
# ============================================================

class CertificadoTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Solicitud de Certificados Académicos:
    - Regla: Requiere obligatoriamente 'student_code' y 'certificate_type' (ej. Notas, Estudio, Buena Conducta).
    - Prioridad por defecto: MEDIUM.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        student_code = metadata.get("student_code")
        cert_type = metadata.get("certificate_type")

        if not student_code or not cert_type:
            raise FactoryValidationError(
                category=TicketCategory.CERTIFICADO.value,
                message="Se requiere 'student_code' (código de estudiante) y 'certificate_type' (tipo de certificado)."
            )

        metadata["digital_delivery"] = metadata.get("digital_delivery", True)
        metadata["academic_period"] = metadata.get("academic_period", "2026-2")

        priority = request.priority.value if request.priority else TicketPriority.MEDIUM.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.CERTIFICADO.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


class MatriculaTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Ajustes e Incidencias de Matrícula:
    - Regla: Requiere 'student_code' y 'subject_or_program' (asignatura o programa académico).
    - Prioridad por defecto: HIGH (la matrícula afecta directamente la inscripción de materias).
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        student_code = metadata.get("student_code")
        program = metadata.get("subject_or_program") or metadata.get("academic_program")

        if not student_code or not program:
            raise FactoryValidationError(
                category=TicketCategory.MATRICULA.value,
                message="Se requiere 'student_code' y 'subject_or_program' para tramitar el ajuste de matrícula."
            )

        metadata["requires_academic_approval"] = True
        priority = request.priority.value if request.priority else TicketPriority.HIGH.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.MATRICULA.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


class RadicadoTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Radicados y Peticiones Formales Universitarias:
    - Regla: Requiere 'request_type' (petición, queja, reclamo o solicitud especial).
    - Enriquecimiento: Genera número radicado consecutivo interno.
    - Prioridad por defecto: MEDIUM.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        request_type = metadata.get("request_type")

        if not request_type:
            raise FactoryValidationError(
                category=TicketCategory.RADICADO.value,
                message="Se requiere 'request_type' (tipo de petición o radicado)."
            )

        import uuid
        metadata["radicado_number"] = metadata.get("radicado_number", f"RAD-{uuid.uuid4().hex[:8].upper()}")
        priority = request.priority.value if request.priority else TicketPriority.MEDIUM.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.RADICADO.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


class CampusVirtualTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Incidencias en Campus Virtual y Plataformas de Aprendizaje:
    - Regla: Requiere 'platform_name' (Moodle, Teams, Correo Institucional).
    - Prioridad por defecto: HIGH.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        platform_name = metadata.get("platform_name")

        if not platform_name:
            raise FactoryValidationError(
                category=TicketCategory.CAMPUS_VIRTUAL.value,
                message="Se requiere 'platform_name' (plataforma afectada ej. Moodle, Teams, Aula Virtual)."
            )

        priority = request.priority.value if request.priority else TicketPriority.HIGH.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.CAMPUS_VIRTUAL.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


# ============================================================
# FÁBRICAS PARA SOPORTE E INFRAESTRUCTURA DE PERSONAL / DOCENTES
# ============================================================

class HardwareTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Tickets de Hardware en Oficinas y Aulas:
    - Regla: Requiere 'serial_number' o 'device_type' (ej. Teclado, Proyector aula, PC docente).
    - Prioridad por defecto: HIGH.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        serial = metadata.get("serial_number")
        device_type = metadata.get("device_type")

        if not serial and not device_type:
            raise FactoryValidationError(
                category=TicketCategory.HARDWARE.value,
                message="Se requiere 'serial_number' o 'device_type' en los metadatos específicos."
            )

        metadata["warranty_check_required"] = metadata.get("warranty_check_required", True)
        if serial:
            metadata["serial_number"] = str(serial).strip().upper()

        priority = request.priority.value if request.priority else TicketPriority.HIGH.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.HARDWARE.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


class SoftwareTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Tickets de Software y Sistemas Académicos:
    - Regla: Requiere obligatoriamente 'software_name'.
    - Prioridad por defecto: MEDIUM.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        software_name = metadata.get("software_name")

        if not software_name:
            raise FactoryValidationError(
                category=TicketCategory.SOFTWARE.value,
                message="Se requiere 'software_name' en los metadatos específicos."
            )

        metadata["version"] = metadata.get("version", "Institucional")
        metadata["os_environment"] = metadata.get("os_environment", "Windows Campus")
        priority = request.priority.value if request.priority else TicketPriority.MEDIUM.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.SOFTWARE.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


class AccessTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Accesos y Permisos Institucionales:
    - Regla: Requiere 'target_system' y ('system_role' o 'user_account').
    - Prioridad por defecto: CRITICAL.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        target_system = metadata.get("target_system")
        system_role = metadata.get("system_role") or metadata.get("user_account")

        if not target_system or not system_role:
            raise FactoryValidationError(
                category=TicketCategory.ACCESS.value,
                message="Se requiere 'target_system' y ('system_role' o 'user_account') en los metadatos específicos."
            )

        metadata["approval_required"] = True
        metadata["audit_clearance"] = metadata.get("audit_clearance", "PENDING_SECURITY_APPROVAL")
        priority = request.priority.value if request.priority else TicketPriority.CRITICAL.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.ACCESS.value,
            priority=priority,
            status="OPEN",
            created_by_id=request.created_by_id,
            specific_metadata=metadata
        )


class TicketFactoryRegistry:
    """
    Registro y despachador de Fábricas Concretas (Open/Closed Principle).
    """
    _registry: Dict[str, Type[TicketFactory]] = {
        # Estudiantes
        TicketCategory.CERTIFICADO.value: CertificadoTicketFactory,
        TicketCategory.MATRICULA.value: MatriculaTicketFactory,
        TicketCategory.RADICADO.value: RadicadoTicketFactory,
        TicketCategory.CAMPUS_VIRTUAL.value: CampusVirtualTicketFactory,
        # Personal
        TicketCategory.HARDWARE.value: HardwareTicketFactory,
        TicketCategory.SOFTWARE.value: SoftwareTicketFactory,
        TicketCategory.ACCESS.value: AccessTicketFactory,
    }

    @classmethod
    def register(cls, category: str, factory_cls: Type[TicketFactory]) -> None:
        cls._registry[category.upper()] = factory_cls

    @classmethod
    def get_factory(cls, category: str) -> TicketFactory:
        cat_key = category.upper() if category else ""
        factory_cls = cls._registry.get(cat_key)
        if not factory_cls:
            valid_cats = list(cls._registry.keys())
            raise FactoryValidationError(
                category=category,
                message=f"Categoría desconocida. Categorías registradas válidas: {valid_cats}"
            )
        return factory_cls()
