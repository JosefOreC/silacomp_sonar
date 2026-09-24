"""
Pruebas unitarias para NlpVectorService (similitud léxica, semántica, keywords y estructural).
"""

from app.infrastructure.nlp.vector_service import NlpVectorService


def test_lexical_similarity_identical_and_different() -> None:
    service = NlpVectorService()
    sim_identical = service.compute_lexical_similarity(
        "Bases de datos relacionales y modelo relacional",
        "Bases de datos relacionales y modelo relacional",
    )
    assert sim_identical == 1.0

    sim_diff = service.compute_lexical_similarity(
        "Álgebra relacional y operadores",
        "Biología molecular y genética avanzada",
    )
    assert sim_diff < 0.15


def test_semantic_similarity_paraphrased() -> None:
    service = NlpVectorService()
    sim = service.compute_semantic_similarity(
        "Normalización del modelo relacional y dependencias funcionales",
        "Formas normales y eliminación de redundancia de datos",
    )
    # Debe ser apreciable conceptualmente
    assert sim >= 0.28


def test_extract_shared_keywords() -> None:
    service = NlpVectorService()
    keywords = service.extract_shared_keywords(
        "Diseño de esquemas con SQL y claves primarias y foráneas.",
        "Implementación de consultas complejas mediante SQL con claves primarias.",
    )
    assert "sql" in keywords
    assert any("clave" in k or "primaria" in k for k in keywords)


def test_compute_structural_similarity() -> None:
    service = NlpVectorService()
    # Mismo orden relativo y misma unidad
    sim_close = service.compute_structural_similarity(
        order_a=1, total_items_a=5, order_b=1, total_items_b=5, unit_a=1, unit_b=1
    )
    assert sim_close > 0.85

    # Unidades muy distantes (Unidad 1 vs Unidad 5)
    sim_far = service.compute_structural_similarity(
        order_a=1, total_items_a=10, order_b=10, total_items_b=10, unit_a=1, unit_b=5
    )
    assert sim_far < 0.40
