import sys
sys.path.insert(0, '.')
import sqlite3
import numpy as np
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.nlp.normalizer import TextNormalizer

conn = sqlite3.connect('data/convcomp.db')
c = conn.cursor()

c.execute("SELECT id, title, text, unit_number FROM content_items WHERE syllabus_id = 'SYL-EA2CE0F95B' ORDER BY unit_number, order_num")
obj_items = c.fetchall()

c.execute("SELECT id, title, text, unit_number FROM content_items WHERE syllabus_id = 'SYL-E33C810E99' ORDER BY unit_number, order_num")
cmp_items = c.fetchall()

vs = NlpVectorService()

print(f"Total obj: {len(obj_items)}, Total cmp: {len(cmp_items)}")

# Analizar ítems específicos no cubiertos
target_unmatched_ids = [
    'SYL-EA2CE0F95B-CONT-006', # Sistemas numéricos
    'SYL-EA2CE0F95B-CONT-010', # Resolución de redireccionamiento
    'SYL-EA2CE0F95B-CONT-011', # Configuración básica de router
    'SYL-EA2CE0F95B-CONT-015', # Capa de aplicación
    'SYL-EA2CE0F95B-CONT-016', # Fundamentos de seguridad en redes
    'SYL-EA2CE0F95B-CONT-017', # Construir una red pequeña
]

for obj in obj_items:
    if obj[0] not in target_unmatched_ids:
        continue
    obj_id, obj_title, obj_text, obj_unit = obj
    core_obj = obj_title.split(" - ")[-1].strip() if " - " in obj_title else obj_title.strip()
    full_obj = f"{obj_title}. {obj_text}"
    
    print(f"\n=======================================================")
    print(f"OBJ: [{obj_id}] U{obj_unit}: {obj_title}")
    print(f"CORE: '{core_obj}'")
    print(f"TEXT SNIPPET: {obj_text[:120]}...")
    print(f"-------------------------------------------------------")
    
    scores = []
    for cmp in cmp_items:
        cmp_id, cmp_title, cmp_text, cmp_unit = cmp
        core_cmp = cmp_title.split(" - ")[-1].strip() if " - " in cmp_title else cmp_title.strip()
        full_cmp = f"{cmp_title}. {cmp_text}"
        
        sem_core = vs.compute_semantic_similarity(core_obj, core_cmp)
        sem_full = vs.compute_semantic_similarity(full_obj, full_cmp)
        sem = max(sem_core, sem_full)
        
        lex_core = vs.compute_lexical_similarity(core_obj, core_cmp)
        lex_full = vs.compute_lexical_similarity(full_obj, full_cmp)
        lex = max(lex_core, lex_full)
        
        kw_core = vs.compute_keyword_overlap(core_obj, core_cmp)
        kw_full = vs.compute_keyword_overlap(full_obj, full_cmp)
        kw = max(kw_core, kw_full)
        
        est = vs.compute_structural_similarity(1, len(obj_items), 1, len(cmp_items), obj_unit, cmp_unit)
        
        composite = round(0.50 * sem + 0.25 * lex + 0.15 * kw + 0.10 * est, 4)
        scores.append((composite, sem, lex, kw, cmp_id, cmp_title, cmp_text[:80]))
        
    scores.sort(key=lambda x: x[0], reverse=True)
    for s in scores[:5]:
        print(f"  Score={s[0]:.3f} (sem={s[1]:.2f}, lex={s[2]:.2f}, kw={s[3]:.2f}) -> [{s[4]}] {s[5]}")
