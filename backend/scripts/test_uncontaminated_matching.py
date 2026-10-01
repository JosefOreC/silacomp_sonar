import sys
sys.path.insert(0, '.')
import sqlite3
import re
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.nlp.normalizer import TextNormalizer

conn = sqlite3.connect('data/convcomp.db')
c = conn.cursor()

c.execute("SELECT id, title, text, unit_number FROM content_items WHERE syllabus_id = 'SYL-EA2CE0F95B' AND (unit_number > 0 OR unit_number IS NULL) ORDER BY unit_number, order_num")
obj_items = c.fetchall()

c.execute("SELECT id, title, text, unit_number FROM content_items WHERE syllabus_id = 'SYL-E33C810E99' AND (unit_number > 0 OR unit_number IS NULL) ORDER BY unit_number, order_num")
cmp_items = c.fetchall()

vs = NlpVectorService()

# Cursos para limpiar prefijos
course_names = [
    "redes de computadores", "redes y comunicacion de datos i", "redes y comunicacion de datos",
    "redes avanzadas", "redes wan", "sistemas de bases de datos", "base de datos i"
]

def clean_item_content(title: str, text: str):
    # 1. Extraer núcleo temático puro
    core = title.split(" - ")[-1].strip() if " - " in title else title.strip()
    
    # 2. Limpiar texto de prefijos de curso y unidad
    clean_text = text
    for cn in course_names:
        clean_text = re.sub(re.escape(cn), "", clean_text, flags=re.IGNORECASE)
        
    # Limpiar prefijos de unidad sintéticos
    clean_text = re.sub(r'^(unidades?|unidad\s+\d+|capa\s+de\s+acceso\s+a\s+la\s+red\s+y\s+capa\s+de\s+internet|protocolos\s+y\s+comunicaciones\s+de\s+red|la\s+capa\s+de\s+transporte\s+y\s+el\s+direccionamiento|la\s+capa\s+de\s+aplicaci[oó]n\s+y\s+soluci[oó]n\s+de\s+problemas)[\.\:\-\s]+', '', clean_text, flags=re.IGNORECASE)
    clean_text = clean_text.strip(" .:\t\n\r-")
    
    # Frases de contenido específicas
    raw_sentences = re.split(r'[\n;]+|(?<=[a-záéíóú0-9])\.\s+', clean_text)
    phrases = [core] if core else []
    for s in raw_sentences:
        s_c = s.strip(" .:\t\n\r-")
        if len(s_c) >= 3 and s_c.lower() not in [p.lower() for p in phrases]:
            if not s_c.lower().startswith(('en esta unidad', 'descargado', 'downloaded', 'lomoarcpsd', 'scan to open')):
                phrases.append(s_c)
                
    effective_text = f"{core}. {clean_text}".strip(" .:")
    return core, effective_text, phrases

print("Comparando ítems con textos y frases purificadas de curso/prefijo...")

results = []

for obj in obj_items:
    obj_id, obj_title, obj_text, obj_unit = obj
    core_obj, eff_obj, obj_phrases = clean_item_content(obj_title, obj_text)
    
    best_match = None
    best_score = -1.0
    
    for cmp in cmp_items:
        cmp_id, cmp_title, cmp_text, cmp_unit = cmp
        core_cmp, eff_cmp, cmp_phrases = clean_item_content(cmp_title, cmp_text)
        
        # 1. Similitud a nivel de contenido efectivo (sin prefijos de curso)
        s_eff = vs.compute_semantic_similarity(eff_obj, eff_cmp)
        l_eff = vs.compute_lexical_similarity(eff_obj, eff_cmp)
        k_eff = vs.compute_keyword_overlap(eff_obj, eff_cmp)
        
        # 2. Similitud a nivel de núcleos puros
        s_core = vs.compute_semantic_similarity(core_obj, core_cmp)
        l_core = vs.compute_lexical_similarity(core_obj, core_cmp)
        k_core = vs.compute_keyword_overlap(core_obj, core_cmp)
        
        # 3. Similitud multi-frase (sub-tópicos cruzados)
        s_phrase = 0.0
        l_phrase = 0.0
        k_phrase = 0.0
        
        for cp in cmp_phrases:
            sp = vs.compute_semantic_similarity(core_obj, cp)
            lp = vs.compute_lexical_similarity(core_obj, cp)
            kp = vs.compute_keyword_overlap(core_obj, cp)
            if sp > s_phrase: s_phrase = sp
            if lp > l_phrase: l_phrase = lp
            if kp > k_phrase: k_phrase = kp
            
        for op in obj_phrases:
            sp = vs.compute_semantic_similarity(op, core_cmp)
            lp = vs.compute_lexical_similarity(op, core_cmp)
            kp = vs.compute_keyword_overlap(op, core_cmp)
            if sp > s_phrase: s_phrase = sp
            if lp > l_phrase: l_phrase = lp
            if kp > k_phrase: k_phrase = kp
            
        sem_sim = max(s_eff, s_core, s_phrase)
        lex_sim = max(l_eff, l_core, l_phrase)
        key_sim = max(k_eff, k_core, k_phrase)
        
        # Estructural
        est_sim = vs.compute_structural_similarity(1, len(obj_items), 1, len(cmp_items), obj_unit, cmp_unit)
        
        if sem_sim >= 0.75 or lex_sim >= 0.70:
            score = 0.55 * sem_sim + 0.30 * lex_sim + 0.15 * key_sim
        else:
            score = 0.45 * sem_sim + 0.25 * lex_sim + 0.15 * key_sim + 0.15 * est_sim
            
        if score > best_score:
            best_score = score
            best_match = (score, sem_sim, lex_sim, key_sim, cmp_id, cmp_title, cmp_unit, core_obj, core_cmp)
            
    results.append((obj_id, obj_title, obj_unit, best_match))

print("\n" + "="*80)
print(f"EMPAREJAMIENTO CURRICULAR EXACTO (TOTAL TEMAS OBJETIVO: {len(results)})")
print("="*80)

match_count = 0
partial_count = 0
uncertain_count = 0
nomatch_count = 0

for obj_id, obj_title, obj_unit, m in results:
    score, sem, lex, kw, cmp_id, cmp_title, cmp_unit, core_o, core_c = m
    if score >= 0.75:
        status = "MATCH"
        match_count += 1
    elif score >= 0.58:
        status = "PARTIAL_MATCH"
        partial_count += 1
    elif score >= 0.45:
        status = "UNCERTAIN"
        uncertain_count += 1
    else:
        status = "NO_MATCH"
        nomatch_count += 1
        
    print(f"[{status:13}] Score={score:.3f} (sem={sem:.2f}, lex={lex:.2f}, kw={kw:.2f})")
    print(f"   OBJ (U{obj_unit}): '{core_o}'")
    print(f"   CMP (U{cmp_unit}): '{cmp_title}'\n")

total_covered = match_count + partial_count
coverage = (total_covered / len(results)) * 100
avg_score = sum(r[3][0] for r in results) / len(results)

print("="*80)
print(f"RESUMEN FINAL EXACTO:")
print(f"Matches directos (>= 0.75): {match_count}")
print(f"Matches parciales (>= 0.58): {partial_count}")
print(f"Inciertos: {uncertain_count}")
print(f"No match: {nomatch_count}")
print(f"COBERTURA OBJETIVO CONVALIDADA: {coverage:.1f}% ({total_covered}/{len(results)})")
print(f"SCORE GLOBAL: {avg_score:.4f}")
print("="*80)
