import sys
sys.path.insert(0, 'backend')
from app.infrastructure.nlp.vector_service import NlpVectorService

svc = NlpVectorService()

# Títulos y textos
title_a = "NORMALIZACIÓN - Tercera forma normal (3FN) y Forma Normal de Boyce-Codd."
text_a = "Semana 4: Tercera forma normal (3FN) y Forma Normal de Boyce-Codd. Ejercicios aplicados."

title_b = "Formas Normales Avanzadas (3FN y BCNF)"
text_b = "Descomposición sin pérdida, dependencias funcionales, tercera forma normal y Boyce-Codd."

# Similitud texto completo actual
full_a = f"{title_a}. {text_a}"
full_b = f"{title_b}. {text_b}"

sim_full = svc.compute_semantic_similarity(full_a, full_b)
sim_titles = svc.compute_semantic_similarity(title_a, title_b)

multi_scale = max(sim_full, 0.65 * sim_full + 0.35 * sim_titles)

print(f"Similitud texto completo: {sim_full:.4f}")
print(f"Similitud solo títulos:   {sim_titles:.4f}")
print(f"Multi-scale semántica:    {multi_scale:.4f}")
