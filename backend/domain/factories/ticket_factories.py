"""
Implementación del Patrón Factory Method (GoF) para la creación polimórfica de Tickets.
Cada creador concreto aplica reglas de negocio, validaciones y metadatos específicos.
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
        """
        Método de fábrica abstracto. Las subclases implementan las reglas
        específicas de validación, prioridad por defecto y enriquecimiento de metadatos.
        """
        pass


class HardwareTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Tickets de Hardware:
    - Regla: Requiere obligatoriamente 'serial_number' o 'device_type' en specific_metadata.
    - Prioridad por defecto: HIGH (un fallo de hardware detiene la operatividad física del usuario).
    - Enriquecimiento: Marca 'warranty_check_required' en True.
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

        # Enriquecimiento de reglas de negocio
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
            specific_metadata=metadata
        )


class SoftwareTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Tickets de Software:
    - Regla: Requiere obligatoriamente 'software_name' en specific_metadata.
    - Prioridad por defecto: MEDIUM.
    - Enriquecimiento: Captura versión y entorno del sistema operativo si no se indican.
    """

    def create_ticket(self, request: TicketCreateRequest) -> TicketModel:
        metadata = dict(request.specific_metadata or {})
        
        software_name = metadata.get("software_name")
        if not software_name:
            raise FactoryValidationError(
                category=TicketCategory.SOFTWARE.value,
                message="Se requiere 'software_name' en los metadatos específicos."
            )

        metadata["version"] = metadata.get("version", "No especificada")
        metadata["os_environment"] = metadata.get("os_environment", "Windows/Linux Generic")

        priority = request.priority.value if request.priority else TicketPriority.MEDIUM.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.SOFTWARE.value,
            priority=priority,
            status="OPEN",
            specific_metadata=metadata
        )


class AccessTicketFactory(TicketFactory):
    """
    Fábrica Concreta para Tickets de Permisos y Accesos:
    - Regla: Requiere obligatoriamente 'target_system' y 'system_role' o 'user_account'.
    - Prioridad por defecto: CRITICAL (los bloqueos de permisos o incidentes de seguridad son críticos).
    - Enriquecimiento: Exige 'approval_required' = True para control de seguridad/compliance.
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

        # Invariante de seguridad
        metadata["approval_required"] = True
        metadata["audit_clearance"] = metadata.get("audit_clearance", "PENDING_SECURITY_APPROVAL")

        priority = request.priority.value if request.priority else TicketPriority.CRITICAL.value

        return TicketModel(
            title=request.title,
            description=request.description,
            category=TicketCategory.ACCESS.value,
            priority=priority,
            status="OPEN",
            specific_metadata=metadata
        )


class TicketFactoryRegistry:
    """
    Registro y despachador de Fábricas Concretas.
    Permite extender el sistema con nuevas categorías sin modificar el código cliente (Open/Closed Principle).
    """
    _registry: Dict[str, Type[TicketFactory]] = {
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
