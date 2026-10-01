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


def test_bipartite_matching_prevents_greedy_cannibalization() -> None:
    """
    Verifica que la asignación global bipartita prevenga que un ítem inicial
    con afinidad moderada canibalice un candidato que tiene afinidad casi perfecta
    con un ítem posterior.
    """
    vector_service = NlpVectorService()
    use_case = CompareSyllabiUseCase(vector_service=vector_service)
    assert use_case.model_version == "bipartite-adaptive-002"

    obj_items = [
        ContentItem(
            id="OBJ-01",
            syllabus_id="S_OBJ",
            section_name="Unidad 1",
            title="Redes de Computadoras y Enrutamiento Básico",
            text="Fundamentos de interconexión, topologías de red y conceptos generales de enrutamiento.",
            normalized_text="fundamentos interconexion topologias red conceptos generales enrutamiento",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=1,
        ),
        ContentItem(
            id="OBJ-02",
            syllabus_id="S_OBJ",
            section_name="Unidad 2",
            title="Protocolo OSPF y Enrutamiento Dinámico WAN",
            text="Configuración avanzada del protocolo de enrutamiento dinámico OSPF v2 para redes WAN empresariales.",
            normalized_text="configuracion avanzada protocolo enrutamiento dinamico ospf v2 redes wan empresariales",
            page_start=2,
            page_end=2,
            order=2,
            unit_number=2,
        ),
    ]

    # CMP-01 tiene match perfecto con OBJ-02 y match parcial con OBJ-01
    # CMP-02 tiene match aceptable con OBJ-01
    cmp_items = [
        ContentItem(
            id="CMP-01",
            syllabus_id="S_CMP",
            section_name="Módulo 1",
            title="Protocolo OSPF y Enrutamiento Dinámico WAN",
            text="Configuración avanzada del protocolo de enrutamiento dinámico OSPF v2 para redes WAN empresariales.",
            normalized_text="configuracion avanzada protocolo enrutamiento dinamico ospf v2 redes wan empresariales",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=1,
        ),
        ContentItem(
            id="CMP-02",
            syllabus_id="S_CMP",
            section_name="Módulo 2",
            title="Fundamentos de Redes y Topologías",
            text="Interconexión y conceptos generales de redes de computadoras y topologías.",
            normalized_text="interconexion conceptos generales redes computadoras topologias",
            page_start=2,
            page_end=2,
            order=2,
            unit_number=2,
        ),
    ]

    comp = use_case.execute(
        objective_syllabus_id="S_OBJ",
        compared_syllabus_id="S_CMP",
        objective_items=obj_items,
        compared_items=cmp_items,
    )

    # Con asignación óptima global:
    # OBJ-02 DEBE emparejar con CMP-01 (match perfecto)
    # OBJ-01 DEBE emparejar con CMP-02 (match adecuado)
    match_obj2 = next((m for m in comp.matches if m.objective_item_id == "OBJ-02"), None)
    assert match_obj2 is not None
    assert match_obj2.compared_item_id == "CMP-01"
    assert match_obj2.classification == MatchClassification.MATCH

    match_obj1 = next((m for m in comp.matches if m.objective_item_id == "OBJ-01"), None)
    assert match_obj1 is not None
    assert match_obj1.compared_item_id == "CMP-02"


def test_adaptive_weights_preserves_score_across_different_units() -> None:
    """
    Verifica que la ponderación adaptativa reduzca la penalización estructural
    cuando la afinidad conceptual (semántica/léxica) es alta, permitiendo
    clasificar MATCH aún cuando los temas estén en unidades curriculares opuestas.
    """
    vector_service = NlpVectorService()
    use_case = CompareSyllabiUseCase(vector_service=vector_service)

    # OBJ está en Unidad 1, orden 1
    obj_item = ContentItem(
        id="OBJ-UNIT1",
        syllabus_id="S_OBJ",
        section_name="Unidad I",
        title="Normalización de Bases de Datos",
        text="Dependencias funcionales, primera forma normal 1FN, segunda forma normal 2FN y tercera forma normal 3FN.",
        normalized_text="dependencias funcionales primera forma normal 1fn segunda forma normal 2fn tercera forma normal 3fn",
        page_start=1,
        page_end=1,
        order=1,
        unit_number=1,
    )

    # CMP está en Unidad 5, orden 15 (gran desfase estructural)
    cmp_item = ContentItem(
        id="CMP-UNIT5",
        syllabus_id="S_CMP",
        section_name="Unidad V",
        title="Formas Normales y Normalización en BBDD",
        text="Dependencias funcionales, primera forma normal 1FN, segunda forma normal 2FN y tercera forma normal 3FN.",
        normalized_text="dependencias funcionales primera forma normal 1fn segunda forma normal 2fn tercera forma normal 3fn",
        page_start=10,
        page_end=10,
        order=15,
        unit_number=5,
    )

    comp = use_case.execute(
        objective_syllabus_id="S_OBJ",
        compared_syllabus_id="S_CMP",
        objective_items=[obj_item],
        compared_items=[cmp_item],
    )

    assert len(comp.matches) == 1
    match = comp.matches[0]
    # Gracias a los pesos adaptativos, la estructura no degrada el score por debajo de 0.85
    assert match.classification == MatchClassification.MATCH
    assert match.score_breakdown.weights["structural"] == 0.0
    assert match.score_breakdown.weights["semantic"] == 0.50


def test_target_driven_subsumption_universal_coverage() -> None:
    """
    Verifica que el análisis orientado al Sílabo Objetivo valide que múltiples
    tópicos atómicos del objetivo queden convalidos cuando el sílabo comparado
    presenta un bloque integrado comprensivo que los abarca a todos.
    """
    vector_service = NlpVectorService()
    use_case = CompareSyllabiUseCase(vector_service=vector_service)

    # El Sílabo Objetivo desglosa 3 temas atómicos de Álgebra Lineal
    obj_items = [
        ContentItem(
            id="OBJ-ALG-01",
            syllabus_id="S_OBJ_MATH",
            section_name="Unidad 2: Matrices y Determinantes",
            title="Cálculo de Determinantes",
            text="Álgebra Lineal. Unidad 2: Matrices y Determinantes. Cálculo de determinantes por cofactores y propiedades.",
            normalized_text="algebra lineal matrices determinantes calculo determinantes cofactores propiedades",
            page_start=1,
            page_end=1,
            order=1,
            unit_number=2,
        ),
        ContentItem(
            id="OBJ-ALG-02",
            syllabus_id="S_OBJ_MATH",
            section_name="Unidad 2: Matrices y Determinantes",
            title="Matriz Inversa",
            text="Álgebra Lineal. Unidad 2: Matrices y Determinantes. Matriz inversa, método de Gauss-Jordan y matriz adjunta.",
            normalized_text="algebra lineal matrices determinantes matriz inversa metodo gauss jordan matriz adjunta",
            page_start=1,
            page_end=1,
            order=2,
            unit_number=2,
        ),
        ContentItem(
            id="OBJ-ALG-03",
            syllabus_id="S_OBJ_MATH",
            section_name="Unidad 2: Matrices y Determinantes",
            title="Regla de Cramer",
            text="Álgebra Lineal. Unidad 2: Matrices y Determinantes. Solución de sistemas de ecuaciones lineales mediante la Regla de Cramer.",
            normalized_text="algebra lineal matrices determinantes solucion sistemas ecuaciones lineales regla cramer",
            page_start=2,
            page_end=2,
            order=3,
            unit_number=2,
        ),
    ]

    # El Sílabo Comparado tiene 1 solo bloque integral que enseña todo el conjunto
    cmp_items = [
        ContentItem(
            id="CMP-ALG-BLOCK",
            syllabus_id="S_CMP_MATH",
            section_name="Módulo I: Álgebra Matricial",
            title="Matrices, Determinantes y Sistemas Lineales",
            text="Álgebra Matricial. Módulo I. Matrices, cálculo de determinantes por cofactores, matriz inversa por Gauss-Jordan y solución de sistemas de ecuaciones con la Regla de Cramer.",
            normalized_text="algebra matricial matrices calculo determinantes cofactores matriz inversa gauss jordan solucion sistemas ecuaciones regla cramer",
            page_start=1,
            page_end=2,
            order=1,
            unit_number=1,
        )
    ]

    comp = use_case.execute(
        objective_syllabus_id="S_OBJ_MATH",
        compared_syllabus_id="S_CMP_MATH",
        objective_items=obj_items,
        compared_items=cmp_items,
    )

    # Los 3 temas del objetivo deben quedar cubiertos y convalidos por el bloque
    assert comp.objective_coverage == 100.0
    assert len(comp.matches) == 3
    for m in comp.matches:
        assert m.compared_item_id == "CMP-ALG-BLOCK"
        assert m.classification in (MatchClassification.MATCH, MatchClassification.PARTIAL_MATCH)
        assert m.score_breakdown.composite_score >= 0.70




