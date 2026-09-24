"""
Excepciones de dominio del sistema de comparación de sílabos.
"""


class ConvCompError(Exception):
    """Excepción base del sistema."""
    pass


class PdfValidationError(ConvCompError):
    """Error al validar formato o metadatos de un PDF."""
    pass


class PdfCorruptedError(ConvCompError):
    """El archivo PDF está dañado o no puede ser leído."""
    pass


class InsufficientDigitalTextError(ConvCompError):
    """
    El archivo PDF tiene contenido de texto insuficiente (probablemente escaneado).
    Informa que el soporte OCR está reservado para la Fase 2.
    """
    def __init__(self, message: str = "No se pudo extraer suficiente texto del documento. El archivo parece ser un documento escaneado sin capa de texto seleccionable. El soporte para OCR estará disponible en la Fase 2."):
        super().__init__(message)


class SyllabusNotFoundError(ConvCompError):
    """No se encontró el sílabo especificado."""
    pass


class ComparisonNotFoundError(ConvCompError):
    """No se encontró la comparación especificada."""
    pass
