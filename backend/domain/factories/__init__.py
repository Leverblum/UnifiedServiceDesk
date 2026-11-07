"""
Exportación de componentes del patrón Factory Method.
"""

from backend.domain.factories.exceptions import FactoryValidationError
from backend.domain.factories.ticket_factories import (
    TicketFactory,
    CertificadoTicketFactory,
    MatriculaTicketFactory,
    RadicadoTicketFactory,
    CampusVirtualTicketFactory,
    HardwareTicketFactory,
    SoftwareTicketFactory,
    AccessTicketFactory,
    TicketFactoryRegistry,
)

__all__ = [
    "FactoryValidationError",
    "TicketFactory",
    "CertificadoTicketFactory",
    "MatriculaTicketFactory",
    "RadicadoTicketFactory",
    "CampusVirtualTicketFactory",
    "HardwareTicketFactory",
    "SoftwareTicketFactory",
    "AccessTicketFactory",
    "TicketFactoryRegistry",
]
