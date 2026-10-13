"""
Excepciones de validación específicas para la fábrica polimórfica de tickets.
"""

class FactoryValidationError(ValueError):
    """
    Se lanza cuando un ticket no cumple las reglas de negocio específicas
    requeridas por su tipo polimórfico (Hardware, Software, Access).
    """
    def __init__(self, category: str, message: str):
        self.category = category
        super().__init__(f"Error de validación en fábrica [{category}]: {message}")
