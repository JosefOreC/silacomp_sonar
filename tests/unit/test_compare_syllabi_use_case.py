"""
Pruebas unitarias para CompareSyllabiUseCase.
"""

from app.application.compare_syllabi import CompareSyllabiUseCase
from app.domain.comparison import MatchClassification
from app.domain.content import ContentItem
from app.infrastructure.nlp.vector_service import NlpVectorService


def test_compare_syllabi_flow_and_bidirectionality() -> None:
    vector_service = NlpVectorService()
    use_case = CompareSyllabiUseCase(vector_service=vector_service, model_version="test-v1")

    # Sílabo Objetivo: 3 contenidos
    obj_items = [
        ContentItem(
            id="OBJ-01",
            syllabus_id="S_OBJ",
            section_name="Unidad I",
            title="Modelo Relacional",
            text="Conceptos del modelo relacional, tablas, tuplas, claves primarias y foráneas.",
            normalized_text="modelo relacional tablas tuplas claves primarias foraneas",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=1,
        ),
        ContentItem(
            id="OBJ-02",
            syllabus_id="S_OBJ",
            section_name="Unidad II",
            title="Normalización",
            text="Primera, segunda y tercera forma normal 3FN.",
            normalized_text="primera segunda tercera forma normal 3fn",
            page_start=2,
            page_end=2,
            order=2,
            unit_number=2,
        ),
        ContentItem(
            id="OBJ-03",
            syllabus_id="S_OBJ",
            section_name="Unidad III",
            title="Optimización Avanzada de Consultas",
            text="Planes de ejecución, índices B+ y optimización interna de queries.",
            normalized_text="planes ejecucion indices bplus optimizacion interna queries",
            page_start=3,
            page_end=3,
            order=3,
            unit_number=3,
        ),
    ]

    # Sílabo Comparado: 2 contenidos (1 coincide alto, 1 coincide normalización, ninguno para optimización, 1 extra)
    cmp_items = [
        ContentItem(
            id="CMP-01",
            syllabus_id="S_CMP",
            section_name="Módulo 1",
            title="Estructuras Relacionales",
            text="Tablas, tuplas, atributos, claves primarias y foráneas del modelo relacional.",
            normalized_text="tablas tuplas atributos claves primarias foraneas modelo relacional",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=1,
        ),
        ContentItem(
            id="CMP-02",
            syllabus_id="S_CMP",
            section_name="Módulo 2",
            title="Formas Normales y Normalización",
            text="Dependencias funcionales, primera, segunda y tercera forma normal 3FN.",
            normalized_text="dependencias funcionales primera segunda tercera forma normal 3fn",
            page_start=2,
            page_end=2,
            order=2,
            unit_number=2,
        ),
        ContentItem(
            id="CMP-03",
            syllabus_id="S_CMP",
            section_name="Módulo 3",
            title="NoSQL y Big Data",
            text="Bases de datos orientadas a documentos MongoDB y Cassandra.",
            normalized_text="bases datos orientadas documentos mongodb cassandra",
            page_start=3,
            page_end=3,
            order=3,
            unit_number=3,
        ),
    ]

    comparison = use_case.execute(
        objective_syllabus_id="S_OBJ",
        compared_syllabus_id="S_CMP",
        objective_items=obj_items,
        compared_items=cmp_items,
    )

    # Verificaciones de estructura
    assert comparison.id.startswith("COMP-")
    assert comparison.total_matches >= 2
    assert comparison.global_score > 0.40

    # Comprobar que OBJ-01 emparejó con CMP-01 con score alto
    match_01 = next((m for m in comparison.matches if m.objective_item_id == "OBJ-01" and m.compared_item_id == "CMP-01"), None)
    assert match_01 is not None
    assert match_01.classification in (MatchClassification.MATCH, MatchClassification.PARTIAL_MATCH)
    assert "claves primarias" in match_01.evidence.shared_keywords or "modelo relacional" in match_01.evidence.shared_keywords or "tablas" in match_01.evidence.shared_keywords

    # Comprobar contenidos sin correspondencia
    # OBJ-03 (Optimización) no debería tener match con NoSQL (CMP-03)
    unmatched_obj_ids = [u.item_id for u in comparison.unmatched_objective]
    assert "OBJ-03" in unmatched_obj_ids

    # CMP-03 (NoSQL) no está en el objetivo y debe aparecer en unmatched_compared
    unmatched_cmp_ids = [u.item_id for u in comparison.unmatched_compared]
    assert "CMP-03" in unmatched_cmp_ids

    # Coberturas
    assert comparison.objective_coverage > 50.0  # Al menos 2 de 3 cubiertos
    assert comparison.compared_coverage > 50.0


def test_redundancy_suppression_and_anti_duplication() -> None:
    """Verifica que el motor de IA no repita candidatos idénticos ni sature correspondencias redundantes."""
    vector_service = NlpVectorService()
    use_case = CompareSyllabiUseCase(vector_service=vector_service, model_version="test-anti-redundancy")

    obj_items = [
        ContentItem(
            id="OBJ-A",
            syllabus_id="S_OBJ",
            section_name="Unidad I",
            title="Protocolo OSPF",
            text="Configuración y enrutamiento con el protocolo OSPF v2 para redes WAN.",
            normalized_text="configuracion enrutamiento protocolo ospf v2 redes wan",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=1,
        ),
        ContentItem(
            id="OBJ-B",
            syllabus_id="S_OBJ",
            section_name="Unidad II",
            title="Listas de Control de Acceso ACL",
            text="Filtrado de paquetes mediante ACL estándar y extendidas IPv4.",
            normalized_text="filtrado paquetes mediante acl estandar extendidas ipv4",
            page_start=2,
            page_end=2,
            order=2,
            unit_number=2,
        ),
    ]

    # Varios ítems comparados, algunos muy redundantes entre sí
    cmp_items = [
        ContentItem(
            id="CMP-A1",
            syllabus_id="S_CMP",
            section_name="Módulo 1",
            title="Enrutamiento Dinámico OSPF",
            text="Configuración y enrutamiento con el protocolo OSPF v2 para redes WAN empresariales.",
            normalized_text="configuracion enrutamiento protocolo ospf v2 redes wan empresariales",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=1,
        ),
        ContentItem(
            id="CMP-A2",  # Casi duplicado de A1
            syllabus_id="S_CMP",
            section_name="Módulo 1",
            title="Enrutamiento OSPF",
            text="Configuración del protocolo OSPF v2 para redes WAN empresariales.",
            normalized_text="configuracion protocolo ospf v2 redes wan empresariales",
            page_start=1,
            page_end=1,
            order=2,
            unit_number=1,
        ),
        ContentItem(
            id="CMP-B1",
            syllabus_id="S_CMP",
            section_name="Módulo 2",
            title="Seguridad con Listas de Control de Acceso ACL",
            text="Filtrado de paquetes mediante ACL estándar y extendidas IPv4 en routers.",
            normalized_text="filtrado paquetes mediante acl estandar extendidas ipv4 routers",
            page_start=2,
            page_end=2,
            order=3,
            unit_number=2,
        ),
    ]

    comp = use_case.execute(
        objective_syllabus_id="S_OBJ",
        compared_syllabus_id="S_CMP",
        objective_items=obj_items,
        compared_items=cmp_items,
    )

    # 1. No debe haber pares idénticos repetidos
    match_pairs = [(m.objective_item_id, m.compared_item_id) for m in comp.matches]
    assert len(match_pairs) == len(set(match_pairs))

    # 2. OBJ-A no debe emitir candidatos redundantes (A1 y A2 son prácticamente el mismo texto, solo se elige el mejor)
    matches_for_obj_a = [m for m in comp.matches if m.objective_item_id == "OBJ-A"]
    assert len(matches_for_obj_a) == 1
    assert matches_for_obj_a[0].compared_item_id in ("CMP-A1", "CMP-A2")


    # 3. OBJ-B debe emparejar con CMP-B1
    matches_for_obj_b = [m for m in comp.matches if m.objective_item_id == "OBJ-B"]
    assert len(matches_for_obj_b) == 1
    assert matches_for_obj_b[0].compared_item_id == "CMP-B1"


def test_compare_identical_syllabi_gives_100_percent() -> None:
    """Verifica que dos sílabos con contenidos 100% idénticos alcancen 100% de cobertura y score 1.0."""
    vector_service = NlpVectorService()
    use_case = CompareSyllabiUseCase(vector_service=vector_service, model_version="test-v1")

    items_obj = [
        ContentItem(
            id=f"OBJ-{i:02d}",
            syllabus_id="S_IDENTICAL_OBJ",
            section_name=f"Unidad {i}",
            title=f"Tema Relevante {i}",
            text=f"Descripción completa y detallada del contenido del tema {i} con conceptos avanzados.",
            normalized_text=f"descripcion completa detallada contenido tema {i} conceptos avanzados",
            page_start=i,
            page_end=i,
            order=i,
            unit_number=i,
        )
        for i in range(1, 11)
    ]

    items_cmp = [
        ContentItem(
            id=f"CMP-{i:02d}",
            syllabus_id="S_IDENTICAL_CMP",
            section_name=f"Unidad {i}",
            title=f"Tema Relevante {i}",
            text=f"Descripción completa y detallada del contenido del tema {i} con conceptos avanzados.",
            normalized_text=f"descripcion completa detallada contenido tema {i} conceptos avanzados",
            page_start=i,
            page_end=i,
            order=i,
            unit_number=i,
        )
        for i in range(1, 11)
    ]

    comp = use_case.execute(
        objective_syllabus_id="S_IDENTICAL_OBJ",
        compared_syllabus_id="S_IDENTICAL_CMP",
        objective_items=items_obj,
        compared_items=items_cmp,
    )

    assert comp.objective_coverage == 100.0
    assert comp.compared_coverage == 100.0
    assert comp.global_score == 1.0
    assert len(comp.matches) == 10
    assert len(comp.unmatched_objective) == 0
    assert len(comp.unmatched_compared) == 0
    for m in comp.matches:
        assert m.classification == MatchClassification.MATCH
        assert m.score_breakdown.composite_score == 1.0


