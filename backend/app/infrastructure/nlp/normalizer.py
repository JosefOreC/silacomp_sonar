"""
Normalizador de texto controlado para documentos académicos.
Preserva rigurosamente el vocabulario técnico, siglas y conceptos de dominio.
"""

import re
import unicodedata
from typing import Set

# Conjunto seleccionado de palabras vacías (stopwords) del español académico
# No incluye términos que aporten distinción técnica (como 'no', 'sin', 'mas', 'menos')
ACADEMIC_STOPWORDS: Set[str] = {
    "a", "al", "ante", "bajo", "cabe", "con", "contra", "de", "del", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para", "por",
    "segun", "sobre", "tras", "el", "la", "los", "las", "un", "una", "unos",
    "unas", "este", "esta", "estos", "estas", "aquel", "aquella", "aquellos",
    "y", "e", "o", "u", "pero", "aunque", "que", "cual", "quien", "cuyo",
    "donde", "cuando", "como", "su", "sus", "mi", "mis", "tu", "tus",
    "se", "lo", "le", "les", "nos", "te", "me", "suya", "suyo", "tambien",
    "ademas", "asi", "cada", "otro", "otra", "otros", "otras",
}

# Mapeo de términos técnicos con signos que normalmente serían eliminados por el regex
SPECIAL_PUNCT_TERMS = {
    "c++": "cpp",
    "c#": "csharp",
    ".net": "dotnet",
    "b+": "bplus",
    "b*": "bstar",
}


class TextNormalizer:
    """Procesador de limpieza y normalización lingüística para comparación textual."""

    @staticmethod
    def strip_accents(text: str) -> str:
        """Elimina tildes y diacríticos preservando la 'ñ'."""
        text = text.replace("ñ", "__enie__").replace("Ñ", "__ENIE__")
        nfkd = unicodedata.normalize("NFKD", text)
        no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
        return no_accents.replace("__enie__", "ñ").replace("__ENIE__", "ñ")

    @classmethod
    def normalize_for_indexing(cls, text: str, remove_stopwords: bool = True) -> str:
        """
        Normaliza el texto para vectorización léxica (TF-IDF):
        - Minúsculas
        - Eliminación de acentos
        - Mapeo de signos técnicos (c++ -> cpp, b+ -> bplus)
        - Limpieza de puntuación
        - Remoción controlada de stopwords si se solicita
        """
        if not text:
            return ""

        # Conversión a minúsculas
        cleaned = text.lower()
        cleaned = cls.strip_accents(cleaned)

        # Proteger términos especiales con signos
        for term, replacement in SPECIAL_PUNCT_TERMS.items():
            cleaned = cleaned.replace(term, f" {replacement} ")

        # Remover caracteres especiales y puntuación no alfanumérica
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)

        # Limpiar espacios repetidos
        words = cleaned.split()

        if remove_stopwords:
            words = [w for w in words if w not in ACADEMIC_STOPWORDS and len(w) > 1]

        return " ".join(words)

    @classmethod
    def clean_display_text(cls, text: str) -> str:
        """Limpia saltos de línea repetidos y espaciado excesivo sin alterar el texto original."""
        if not text:
            return ""
        # Normalizar espacios en blanco horizontales
        cleaned = re.sub(r"[ \t]+", " ", text)
        # Normalizar saltos de línea excesivos
        cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
        return cleaned.strip()
