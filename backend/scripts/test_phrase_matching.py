import sys
sys.path.insert(0, '.')
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.nlp.normalizer import TextNormalizer

vs = NlpVectorService()

test_cases = [
    (
        "Fundamentos de seguridad en redes",
        "Redes y Comunicación de Datos I. Capa de Aplicación. VLAN. Conceptos básicos de Data Center. Fundamentos de seguridad en la red."
    ),
    (
        "Configuración básica de router",
        "Redes y Comunicación de Datos I. Capa de red. Introducción al diseño lógico. Redes de circuitos virtuales y de datagramas. Estructura de un router. Enrutamiento básico."
    ),
    (
        "Resolución de redireccionamiento",
        "Redes y Comunicación de Datos I. Capa de Acceso a Red. Ethernet y ARP. Conmutadores de la capa de enlace. Enrutamiento básico."
    ),
    (
        "Sistemas numéricos",
        "Redes y Comunicación de Datos I. Capa de red. Subredes con mascara de subred de longitud fija - FLSM. Subredes con mascara de subred de longitud variable - VLSM. Direccionamiento IPv4."
    ),
    (
        "Capa de aplicación",
        "Redes y Comunicación de Datos I. Capa de Aplicación. Fundamentos de las aplicaciones de red. DNS: servicio de directorio de Internet. La web y HTTP."
    ),
    (
        "Construir una red pequeña",
        "Redes y Comunicación de Datos I. Capa de Aplicación. Sesión integradora de conceptos de redes y protocolos. Configuración básica de switches y terminales."
    )
]

for obj_title, cmp_text in test_cases:
    print(f"\n=======================================================")
    print(f"OBJ: '{obj_title}'")
    print(f"CMP TEXT: '{cmp_text}'")
    
    # 1. Directo texto completo
    sem_full = vs.compute_semantic_similarity(obj_title, cmp_text)
    lex_full = vs.compute_lexical_similarity(obj_title, cmp_text)
    kw_full = vs.compute_keyword_overlap(obj_title, cmp_text)
    comp_full = round(0.50 * sem_full + 0.30 * lex_full + 0.20 * kw_full, 4)
    print(f"FULL MATCH: comp={comp_full:.3f} (sem={sem_full:.2f}, lex={lex_full:.2f}, kw={kw_full:.2f})")
    
    # 2. Descomposición por frases u oraciones (sub-tópicos)
    phrases = [p.strip() for p in cmp_text.replace('\n', '. ').split('.') if len(p.strip()) >= 3]
    best_comp = 0.0
    best_p = ""
    best_parts = ()
    for p in phrases:
        s = vs.compute_semantic_similarity(obj_title, p)
        l = vs.compute_lexical_similarity(obj_title, p)
        k = vs.compute_keyword_overlap(obj_title, p)
        c = round(0.50 * s + 0.30 * l + 0.20 * k, 4)
        if c > best_comp:
            best_comp = c
            best_p = p
            best_parts = (s, l, k)
    
    print(f"BEST PHRASE MATCH: comp={best_comp:.3f} (sem={best_parts[0]:.2f}, lex={best_parts[1]:.2f}, kw={best_parts[2]:.2f})")
    print(f"   Phrase matched: '{best_p}'")
