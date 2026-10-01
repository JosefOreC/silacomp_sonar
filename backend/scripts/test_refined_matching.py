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

def get_clean_topic_phrases(title: str, text: str):
    # Aislar el núcleo del título sin prefijo de unidad
    core = title.split(" - ")[-1].strip() if " - " in title else title.strip()
    
    # Extraer oraciones de contenido
    # Quitar cabeceras repetitivas de universidad o curso
    raw_sentences = re.split(r'[\n;]+|(?<=[a-záéíóú0-9])\.\s+', text)
    clean = []
    
    # Siempre incluir el núcleo del tema como frase primordial
    if core and len(core) >= 3:
        clean.append(core)
        
    for s in raw_sentences:
        s_clean = s.strip()
        # Limpiar si contiene prefijos de unidad o curso
        if " - " in s_clean:
            s_clean = s_clean.split(" - ")[-1].strip()
        # Descartar boilerplates
        if len(s_clean) >= 4 and not s_clean.lower().startswith(('redes de computadores', 'redes y comunicaci', 'en esta unidad', 'descargado', 'downloaded', 'lomoarcpsd', 'scan to open')):
            if s_clean not in clean:
                clean.append(s_clean)
                
    return core, clean

print(f"Evaluando {len(obj_items)} temas del objetivo vs {len(cmp_items)} temas del comparado con frases limpias...")

results = []

for obj in obj_items:
    obj_id, obj_title, obj_text, obj_unit = obj
    core_obj, obj_phrases = get_clean_topic_phrases(obj_title, obj_text)
    full_obj = f"{obj_title}. {obj_text}".strip()
    
    best_match = None
    best_score = -1.0
    
    for cmp in cmp_items:
        cmp_id, cmp_title, cmp_text, cmp_unit = cmp
        core_cmp, cmp_phrases = get_clean_topic_phrases(cmp_title, cmp_text)
        full_cmp = f"{cmp_title}. {cmp_text}".strip()
        
        # 1. Similitud a nivel de texto completo
        s_full = vs.compute_semantic_similarity(full_obj, full_cmp)
        l_full = vs.compute_lexical_similarity(full_obj, full_cmp)
        k_full = vs.compute_keyword_overlap(full_obj, full_cmp)
        
        # 2. Similitud a nivel de núcleos
        s_core = vs.compute_semantic_similarity(core_obj, core_cmp)
        l_core = vs.compute_lexical_similarity(core_obj, core_cmp)
        k_core = vs.compute_keyword_overlap(core_obj, core_cmp)
        
        # 3. Similitud asimétrica multi-frase (sub-tópicos de contenido puro)
        s_phrase_max = 0.0
        l_phrase_max = 0.0
        k_phrase_max = 0.0
        
        # Match de core_obj contra las frases de contenido de cmp
        for cp in cmp_phrases:
            sp = vs.compute_semantic_similarity(core_obj, cp)
            lp = vs.compute_lexical_similarity(core_obj, cp)
            kp = vs.compute_keyword_overlap(core_obj, cp)
            if sp > s_phrase_max: s_phrase_max = sp
            if lp > l_phrase_max: l_phrase_max = lp
            if kp > k_phrase_max: k_phrase_max = kp
            
        # Match de core_cmp contra las frases de contenido de obj
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
        
        # Similitud estructural
        est_sim = vs.compute_structural_similarity(1, len(obj_items), 1, len(cmp_items), obj_unit, cmp_unit)
        
        # Ponderación adaptativa: neutralizar penalización estructural ante afinidad real
        if sem_sim >= 0.75 or lex_sim >= 0.70:
            score = 0.55 * sem_sim + 0.30 * lex_sim + 0.15 * key_sim
        else:
            score = 0.45 * sem_sim + 0.25 * lex_sim + 0.15 * key_sim + 0.15 * est_sim
            
        if score > best_score:
            best_score = score
            best_match = (score, sem_sim, lex_sim, key_sim, cmp_id, cmp_title, cmp_unit, core_obj, core_cmp)
            
    results.append((obj_id, obj_title, obj_unit, best_match))

print("\n" + "="*80)
print(f"RESULTADOS REFINADOS (TOTAL TEMAS OBJETIVO: {len(results)})")
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
    print(f"   OBJ: '{core_o}' (U{obj_unit})")
    print(f"   CMP: '{cmp_title}' (U{cmp_unit})\n")

total_covered = match_count + partial_count
coverage = (total_covered / len(results)) * 100
avg_score = sum(r[3][0] for r in results) / len(results)

print("="*80)
print(f"RESUMEN FINAL REFINADO:")
print(f"Matches directos (>= 0.75): {match_count}")
print(f"Matches parciales (>= 0.60): {partial_count}")
print(f"Inciertos: {uncertain_count}")
print(f"No match: {nomatch_count}")
print(f"COBERTURA OBJETIVO CONVALIDADA: {coverage:.1f}% ({total_covered}/{len(results)})")
print(f"SCORE GLOBAL: {avg_score:.4f}")
print("="*80)
