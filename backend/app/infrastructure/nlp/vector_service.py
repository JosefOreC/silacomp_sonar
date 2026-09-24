"""
Servicio de vectorización y similitud léxica, semántica y contextual.
Implementa el puerto INlpVectorService con scikit-learn y Sentence Transformers.
"""

import logging
from typing import List, Optional, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.domain.ports import INlpVectorService
from app.infrastructure.nlp.normalizer import TextNormalizer

logger = logging.getLogger(__name__)


class NlpVectorService(INlpVectorService):
    """
    Motor híbrido de cálculo de similitud:
    - Léxica: TF-IDF con n-gramas (1, 2) y similitud coseno.
    - Semántica: Sentence Transformers (embeddings densos multilingües) con similitud coseno.
    - Evidencia léxica: Intersección de n-gramas y palabras clave significativas.
    - Estructural: Proximidad de orden relativo y coincidencia de tipo de unidad.
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        self._model = None
        self._model_load_failed = False

    def _get_embedding_model(self):
        """Carga perezosa (lazy-loading) del modelo de Sentence Transformers con manejo defensivo."""
        if self._model is not None:
            return self._model
        if self._model_load_failed:
            return None

        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Cargando modelo Sentence Transformer: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            return self._model
        except Exception as e:
            logger.warning("No fue posible cargar el modelo Sentence Transformer (%s): %s. Se utilizará estimador semántico alternativo.", self.model_name, e)
            self._model_load_failed = True
            return None

    def encode_texts(self, texts: List[str]) -> Optional[np.ndarray]:
        """Codifica un lote completo de textos en vectores normalizados de embeddings."""
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        model = self._get_embedding_model()
        if model is None:
            return None
        try:
            clean_texts = [TextNormalizer.clean_display_text(t) for t in texts]
            embeddings = model.encode(clean_texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings
        except Exception as e:
            logger.warning("Error en batch encoding con Sentence Transformer: %s", e)
            return None


    def compute_lexical_similarity(self, text_a: str, text_b: str) -> float:
        """
        Calcula la similitud léxica mediante TF-IDF unigrama+bigrama y similitud coseno.
        Rango: [0.0, 1.0].
        """
        norm_a = TextNormalizer.normalize_for_indexing(text_a)
        norm_b = TextNormalizer.normalize_for_indexing(text_b)

        if not norm_a or not norm_b:
            return 0.0

        if norm_a == norm_b:
            return 1.0

        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            tfidf_matrix = vectorizer.fit_transform([norm_a, norm_b])
            sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            return max(0.0, min(1.0, round(sim, 4)))
        except Exception:
            return 0.0

    def compute_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """
        Calcula la similitud semántica mediante embeddings densos y similitud coseno.
        Si el modelo neuronal no está disponible (red/offline), usa estimación léxico-conceptual de respaldo.
        """
        clean_a = TextNormalizer.clean_display_text(text_a)
        clean_b = TextNormalizer.clean_display_text(text_b)

        if not clean_a or not clean_b:
            return 0.0

        if clean_a.lower() == clean_b.lower():
            return 1.0

        model = self._get_embedding_model()
        if model is not None:
            try:
                embeddings = model.encode([clean_a, clean_b], convert_to_numpy=True)
                norm_a = np.linalg.norm(embeddings[0])
                norm_b = np.linalg.norm(embeddings[1])
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                cos_sim = float(np.dot(embeddings[0], embeddings[1]) / (norm_a * norm_b))
                return max(0.0, min(1.0, round(cos_sim, 4)))
            except Exception as e:
                logger.warning("Error computando embeddings con Sentence Transformer: %s", e)

        # Respaldo determinista si el modelo neuronal no está presente
        return self._fallback_semantic_similarity(clean_a, clean_b)

    def _fallback_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """
        Estimador semántico de respaldo basado en n-gramas de caracteres y similitud de Jaccard ampliada.
        Garantiza que el sistema funcione 100% offline sin dependencias de red.
        """
        norm_a = TextNormalizer.normalize_for_indexing(text_a)
        norm_b = TextNormalizer.normalize_for_indexing(text_b)

        words_a = set(norm_a.split())
        words_b = set(norm_b.split())

        if not words_a or not words_b:
            return 0.0

        # Similitud de palabras compartidas
        jaccard_words = len(words_a & words_b) / len(words_a | words_b)

        # Similitud de tri-gramas de caracteres para capturar raíces morfológicas
        tri_a = {norm_a[i:i+3] for i in range(len(norm_a) - 2)}
        tri_b = {norm_b[i:i+3] for i in range(len(norm_b) - 2)}
        jaccard_tri = len(tri_a & tri_b) / len(tri_a | tri_b) if tri_a and tri_b else 0.0

        score = 0.5 * jaccard_words + 0.5 * jaccard_tri
        return max(0.0, min(1.0, round(score, 4)))

    def extract_shared_keywords(self, text_a: str, text_b: str) -> List[str]:
        """
        Extrae los términos técnicos y palabras clave sustantivas presentes en ambos contenidos.
        """
        norm_a = TextNormalizer.normalize_for_indexing(text_a)
        norm_b = TextNormalizer.normalize_for_indexing(text_b)

        words_a = set(norm_a.split())
        words_b = set(norm_b.split())

        # Palabras individuales compartidas de longitud >= 3
        shared = {w for w in (words_a & words_b) if len(w) >= 3}

        # Bigramas compartidos
        bigrams_a = self._extract_bigrams(norm_a)
        bigrams_b = self._extract_bigrams(norm_b)
        shared_bigrams = bigrams_a & bigrams_b

        # Unir bigramas primero y luego unigramas significativos
        result: List[str] = sorted(list(shared_bigrams), key=lambda x: len(x), reverse=True)
        for w in sorted(list(shared), key=lambda x: len(x), reverse=True):
            if w not in result:
                result.append(w)

        return result[:12]  # Hasta 12 términos de evidencia

    def compute_keyword_overlap(self, text_a: str, text_b: str) -> float:
        """
        Calcula el coeficiente de solapamiento de vocabulario y términos clave (Jaccard ponderado).
        """
        norm_a = TextNormalizer.normalize_for_indexing(text_a)
        norm_b = TextNormalizer.normalize_for_indexing(text_b)

        tokens_a = set(norm_a.split())
        tokens_b = set(norm_b.split())

        if not tokens_a or not tokens_b:
            return 0.0

        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return round(intersection / union, 4) if union > 0 else 0.0

    def compute_structural_similarity(
        self,
        order_a: int,
        total_items_a: int,
        order_b: int,
        total_items_b: int,
        unit_a: Optional[int] = None,
        unit_b: Optional[int] = None,
    ) -> float:
        """
        Evalúa la proximidad en el flujo curricular:
        - Coincidencia o cercanía de número de unidad (50% del componente).
        - Proximidad de orden relativo en el curso (50% del componente).
        """
        # 1. Proximidad de orden relativo: |pos_rel_a - pos_rel_b|
        rel_a = order_a / max(1, total_items_a)
        rel_b = order_b / max(1, total_items_b)
        order_diff = abs(rel_a - rel_b)
        order_score = max(0.0, 1.0 - (order_diff * 1.5))

        # 2. Proximidad de unidad
        if unit_a is not None and unit_b is not None:
            if unit_a == unit_b:
                unit_score = 1.0
            else:
                unit_diff = abs(unit_a - unit_b)
                unit_score = max(0.0, 1.0 - (unit_diff * 0.35))
        else:
            unit_score = order_score

        composite_structural = 0.5 * order_score + 0.5 * unit_score
        return max(0.0, min(1.0, round(composite_structural, 4)))

    def _extract_bigrams(self, normalized_text: str) -> Set[str]:
        """Extrae conjunto de bigramas a partir del texto normalizado."""
        words = normalized_text.split()
        if len(words) < 2:
            return set()
        return {f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)}
