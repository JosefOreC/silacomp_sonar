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

def extract_meaningful_phrases(text: str):
    # Separa por saltos de línea, puntos seguidos de espacio o mayúscula, punto y coma
    raw_parts = re.split(r'[\n;]+|(?<=[a-záéíóú0-9])\.\s+', text)
    clean_parts = []
    for p in raw_parts:
        p_clean = p.strip()
        # descartar frases triviales
        if len(p_clean) >= 4 and not p_clean.lower().startswith(('en esta unidad', 'descargado', 'downloaded')):
            clean_parts.append(p_clean)
    return clean_parts

print(f"Evaluando {len(obj_items)} temas del objetivo vs {len(cmp_items)} temas del comparado...")

results = []

for obj in obj_items:
    obj_id, obj_title, obj_text, obj_unit = obj
    core_obj = obj_title.split(" - ")[-1].strip() if " - " in obj_title else obj_title.strip()
    full_obj = f"{obj_title}. {obj_text}".strip()
    obj_phrases = extract_meaningful_phrases(full_obj)
    if core_obj not in obj_phrases:
        obj_phrases.insert(0, core_obj)
        
    best_match = None
    best_score = -1.0
    
    for cmp in cmp_items:
        cmp_id, cmp_title, cmp_text, cmp_unit = cmp
        core_cmp = cmp_title.split(" - ")[-1].strip() if " - " in cmp_title else cmp_title.strip()
        full_cmp = f"{cmp_title}. {cmp_text}".strip()
        cmp_phrases = extract_meaningful_phrases(full_cmp)
        if core_cmp not in cmp_phrases:
            cmp_phrases.insert(0, core_cmp)
            
        # 1. Similitud a nivel de texto completo
        s_full = vs.compute_semantic_similarity(full_obj, full_cmp)
        l_full = vs.compute_lexical_similarity(full_obj, full_cmp)
        k_full = vs.compute_keyword_overlap(full_obj, full_cmp)
        
        # 2. Similitud a nivel de núcleos
        s_core = vs.compute_semantic_similarity(core_obj, core_cmp)
        l_core = vs.compute_lexical_similarity(core_obj, core_cmp)
        k_core = vs.compute_keyword_overlap(core_obj, core_cmp)
        
        # 3. Similitud asimétrica multi-frase (sub-tópicos)
        # Comprobar si core_obj hace match directo con alguna frase de cmp
        s_phrase_max = 0.0
        l_phrase_max = 0.0
        k_phrase_max = 0.0
        for cp in cmp_phrases:
            sp = vs.compute_semantic_similarity(core_obj, cp)
            lp = vs.compute_lexical_similarity(core_obj, cp)
            kp = vs.compute_keyword_overlap(core_obj, cp)
            if sp > s_phrase_max: s_phrase_max = sp
            if lp > l_phrase_max: l_phrase_max = lp
            if kp > k_phrase_max: k_phrase_max = kp
            
        # Comprobar si core_cmp hace match directo con alguna frase de obj
        for op in obj_phrases:
            sp = vs.compute_semantic_similarity(op, core_cmp)
            lp = vs.compute_lexical_similarity(op, core_cmp)
            kp = vs.compute_keyword_overlap(op, core_cmp)
            if sp > s_phrase_max: s_phrase_max = sp
            if lp > l_phrase_max: l_phrase_max = lp
            if kp > k_phrase_max: k_phrase_max = kp
            
        sem_sim = max(s_full, s_core, s_phrase_max)
        lex_sim = max(l_full, l_core, l_phrase_max)
        key_sim = max(k_full, k_core, k_phrase_max)
        
        # Estructural
        est_sim = vs.compute_structural_similarity(1, len(obj_items), 1, len(cmp_items), obj_unit, cmp_unit)
        
        # Adaptativo
        if sem_sim >= 0.75 or lex_sim >= 0.70:
            score = 0.55 * sem_sim + 0.30 * lex_sim + 0.15 * key_sim
        else:
            score = 0.45 * sem_sim + 0.25 * lex_sim + 0.15 * key_sim + 0.15 * est_sim
            
        if score > best_score:
            best_score = score
            best_match = (score, sem_sim, lex_sim, key_sim, cmp_id, cmp_title, cmp_unit)
            
    results.append((obj_id, obj_title, obj_unit, best_match))

print("\n" + "="*80)
print(f"RESULTADOS DE CONVALIDACIÓN (TOTAL TEMAS OBJETIVO: {len(results)})")
print("="*80)

match_count = 0
partial_count = 0
uncertain_count = 0
nomatch_count = 0

for obj_id, obj_title, obj_unit, m in results:
    score, sem, lex, kw, cmp_id, cmp_title, cmp_unit = m
    if score >= 0.75:
        status = "MATCH"
        match_count += 1
    elif score >= 0.60:
        status = "PARTIAL_MATCH"
        partial_count += 1
    elif score >= 0.45:
        status = "UNCERTAIN"
        uncertain_count += 1
    else:
        status = "NO_MATCH"
        nomatch_count += 1
        
    print(f"[{status:13}] Score={score:.3f} (sem={sem:.2f}, lex={lex:.2f}, kw={kw:.2f})")
    print(f"   OBJ (U{obj_unit}): {obj_title}")
    print(f"   CMP (U{cmp_unit}): {cmp_title}\n")

total_covered = match_count + partial_count
coverage = (total_covered / len(results)) * 100
avg_score = sum(r[3][0] for r in results) / len(results)

print("="*80)
print(f"RESUMEN FINAL:")
print(f"Matches directos: {match_count}")
print(f"Matches parciales: {partial_count}")
print(f"Inciertos: {uncertain_count}")
print(f"No match: {nomatch_count}")
print(f"COBERTURA OBJETIVO CONVALIDADA: {coverage:.1f}% ({total_covered}/{len(results)})")
print(f"SCORE GLOBAL: {avg_score:.4f}")
print("="*80)
