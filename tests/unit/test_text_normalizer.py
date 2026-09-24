"""
Pruebas unitarias para el normalizador de texto controlado.
"""

from app.infrastructure.nlp.normalizer import TextNormalizer


def test_strip_accents() -> None:
    assert TextNormalizer.strip_accents("Álgebra Relacional y Normalización") == "Algebra Relacional y Normalizacion"
    # Preservar la eñe
    assert TextNormalizer.strip_accents("Diseño de Base de Datos en Español") == "Diseño de Base de Datos en Español"


def test_normalize_for_indexing_preserves_tech_terms() -> None:
    text = "Introducción a SQL, C++ y normalización 3FN con árboles B+"
    normalized = TextNormalizer.normalize_for_indexing(text)

    # Debe contener los términos técnicos clave
    assert "sql" in normalized
    assert "cpp" in normalized
    assert "3fn" in normalized
    assert "bplus" in normalized
    # Debe haber eliminado stopwords estándar
    assert "introduccion" in normalized
    assert "arboles" in normalized
    assert "con" not in normalized.split()


def test_clean_display_text() -> None:
    messy = "Línea 1    con   muchos espacios.\n\n\n\nLínea 2."
    cleaned = TextNormalizer.clean_display_text(messy)
    assert "  " not in cleaned
    assert "\n\n\n" not in cleaned
