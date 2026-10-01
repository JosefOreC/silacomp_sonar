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

def extract_pure_topic_and_sentences(title: str, text: str):
    # Núcleo del tema (sin "Unidad X: " ni "Tema - ")
    core_title = title.split(" - ")[-1].strip() if " - " in title else title.strip()
    
    # Oraciones del texto original
    # Quitar cualquier mención del nombre del curso o prefijos conocidos de unidad
    t_clean = re.sub(r'^(?:redes\s+de\s+computadores|redes\s+y\s+comunicaci[oó]n\s+de\s+datos\s+i|redes\s+avanzadas|sistemas\s+de\s+bases\s+de\s+datos|base\s+de\s+datos\s+i)[\.\:\-\s]*', '', text, flags=re.IGNORECASE)
    t_clean = re.sub(r'^(?:protocolos\s+y\s+comunicaciones\s+de\s+red|capa\s+de\s+acceso\s+a\s+la\s+red\s+y\s+capa\s+de\s+internet|la\s+capa\s+de\s+transporte\s+y\s+el\s+direccionamiento|la\s+capa\s+de\s+aplicaci[oó]n\s+y\s+soluci[oó]n\s+de\s+problemas|capa\s+de\s+acceso\s+a\s+red|capa\s+de\s+red|capa\s+de\s+transporte|capa\s+de\s+aplicaci[oó]n)[\.\:\-\s]*', '', t_clean, flags=re.IGNORECASE)
    
    raw_sentences = re.split(r'[\n;]+|(?<=[a-záéíóú0-9])\.\s+', t_clean)
    meaningful = [core_title]
    for s in raw_sentences:
        sc = s.strip(" .:\t\n\r-")
        if len(sc) >= 4 and not sc.lower().startswith(('en esta unidad', 'descargado', 'downloaded', 'lomoarcpsd', 'scan to open')):
            if sc.lower() not in [m.lower() for m in meaningful]:
                meaningful.append(sc)
                
    return core_title, meaningful

print("=== EVALUACIÓN CON TEMAS Y SUB-FRASES PURAS ===")

results = []

for obj in obj_items:
    obj_id, obj_title, obj_text, obj_unit = obj
    core_obj, obj_phrases = extract_pure_topic_and_sentences(obj_title, obj_text)
    
    best_candidate = None
    best_score = -1.0
    
    for cmp in cmp_items:
        cmp_id, cmp_title, cmp_text, cmp_unit = cmp
        core_cmp, cmp_phrases = extract_pure_topic_and_sentences(cmp_title, cmp_text)
        
        # 1. Similitud entre los dos núcleos directos
        s_core = vs.compute_semantic_similarity(core_obj, core_cmp)
        l_core = vs.compute_lexical_similarity(core_obj, core_cmp)
        k_core = vs.compute_keyword_overlap(core_obj, core_cmp)
        
        # 2. Similitud multi-frase: si core_obj está en alguna frase de cmp
        s_phrase_max = 0.0
        l_phrase_max = 0.0
        k_phrase_max = 0.0
        best_p_match = ""
        
        for cp in cmp_phrases:
            sp = vs.compute_semantic_similarity(core_obj, cp)
            lp = vs.compute_lexical_similarity(core_obj, cp)
            kp = vs.compute_keyword_overlap(core_obj, cp)
            if sp > s_phrase_max: s_phrase_max = sp
            if lp > l_phrase_max: 
                l_phrase_max = lp
                best_p_match = cp
            if kp > k_phrase_max: k_phrase_max = kp
            
        for op in obj_phrases:
            sp = vs.compute_semantic_similarity(op, core_cmp)
            lp = vs.compute_lexical_similarity(op, core_cmp)
            kp = vs.compute_keyword_overlap(op, core_cmp)
            if sp > s_phrase_max: s_phrase_max = sp
            if lp > l_phrase_max: l_phrase_max = lp
            if kp > k_phrase_max: k_phrase_max = kp
            
        sem = max(s_core, s_phrase_max)
        lex = max(l_core, l_phrase_max)
        kw = max(k_core, k_phrase_max)
        
        # Estructural
        est = vs.compute_structural_similarity(1, len(obj_items), 1, len(cmp_items), obj_unit, cmp_unit)
        
        if sem >= 0.75 or lex >= 0.70:
            pair_score = 0.55 * sem + 0.30 * lex + 0.15 * kw
        else:
            pair_score = 0.45 * sem + 0.25 * lex + 0.15 * kw + 0.15 * est
            
        if pair_score > best_score:
            best_score = pair_score
            best_candidate = (pair_score, sem, lex, kw, cmp_id, cmp_title, cmp_unit, core_obj, core_cmp, best_p_match)
            
    results.append((obj_id, obj_title, obj_unit, best_candidate))

print("\n" + "="*85)
print("EMPAREJAMIENTO CURRICULAR PURO:")
print("="*85)

matches_direct = 0
matches_partial = 0
matches_uncertain = 0
no_matches = 0

for obj_id, obj_title, obj_unit, cand in results:
    score, sem, lex, kw, cmp_id, cmp_title, cmp_unit, c_obj, c_cmp, p_match = cand
    if score >= 0.75:
        tag = "MATCH"
        matches_direct += 1
    elif score >= 0.58:
        tag = "PARTIAL_MATCH"
        matches_partial += 1
    elif score >= 0.45:
        tag = "UNCERTAIN"
        matches_uncertain += 1
    else:
        tag = "NO_MATCH"
        no_matches += 1
        
    print(f"[{tag:13}] Score={score:.3f} (sem={sem:.2f}, lex={lex:.2f}, kw={kw:.2f})")
    print(f"   OBJ: '{c_obj}' (U{obj_unit})")
    print(f"   CMP: '{cmp_title}' (U{cmp_unit})")
    if p_match:
        print(f"   EVIDENCIA FRASE: '{p_match}'")
    print()

total_convalidado = matches_direct + matches_partial
cov_pct = (total_convalidado / len(results)) * 100
avg_sc = sum(r[3][0] for r in results) / len(results)

print("="*85)
print(f"RESUMEN FINAL:")
print(f"Matches directos: {matches_direct}")
print(f"Matches parciales: {matches_partial}")
print(f"Inciertos: {matches_uncertain}")
print(f"No match: {no_matches}")
print(f"COBERTURA OBJETIVO CONVALIDADA: {cov_pct:.1f}% ({total_convalidado}/{len(results)})")
print(f"SCORE GLOBAL: {avg_sc:.4f}")
print("="*85)
