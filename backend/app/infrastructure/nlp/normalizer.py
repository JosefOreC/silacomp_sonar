"""
Normalizador de texto controlado para documentos académicos.
Preserva rigurosamente el vocabulario técnico, siglas y conceptos de dominio.
"""

import re
import unicodedata
from typing import Dict, Set

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
SPECIAL_PUNCT_TERMS: Dict[str, str] = {
    "c++": "cpp",
    "c#": "csharp",
    ".net": "dotnet",
    "b+": "bplus",
    "b*": "bstar",
}

# Diccionario canónico de acrónimos y conceptos técnicos de ingeniería y ciencias
TECHNICAL_ACRONYMS: Dict[str, str] = {
    # Bases de datos y modelos relacionales
    "bbdd": "base de datos",
    "bd": "base de datos",
    "dbms": "sistema de gestion de bases de datos",
    "sgbd": "sistema de gestion de bases de datos",
    "rdbms": "sistema relacional de bases de datos",
    "sgrbd": "sistema relacional de bases de datos",
    "er": "entidad relacion",
    "mer": "modelo entidad relacion",
    "der": "diagrama entidad relacion",
    "df": "dependencias funcionales",
    "1fn": "primera forma normal",
    "2fn": "segunda forma normal",
    "3fn": "tercera forma normal",
    "fnbc": "forma normal de boyce codd",
    "bcnf": "forma normal de boyce codd",
    "sql": "sql Structured Query Language",
    "nosql": "nosql base de datos no relacional",

    # Redes y telecomunicaciones
    "wan": "red de area amplia wan",
    "lan": "red de area local lan",
    "wlan": "red inalambrica wlan",
    "man": "red de area metropolitana man",
    "vpn": "red privada virtual vpn",
    "qos": "calidad de servicio qos",
    "acl": "lista de control de acceso acl",
    "nat": "traduccion de direcciones de red nat",
    "pat": "traduccion de direcciones y puertos pat",
    "ospf": "protocolo ospf enrutamiento",
    "ospfv2": "protocolo ospf enrutamiento",
    "bgp": "protocolo bgp enrutamiento",
    "rip": "protocolo rip enrutamiento",
    "tcp": "protocolo de control de transmision tcp",
    "udp": "protocolo de datagramas udp",
    "ip": "protocolo de internet ip",
    "ipv4": "protocolo ipv4 direcciones",
    "ipv6": "protocolo ipv6 direcciones",
    "osi": "modelo osi capas",
    "dns": "sistema de nombres de dominio dns",
    "dhcp": "configuracion dinamica de host dhcp",
    "vlan": "red de area local virtual vlan",
    "stp": "spanning tree protocol stp",
    "ipsec": "seguridad ipsec tunel",

    # Programación, arquitectura e ingeniería de software
    "poo": "programacion orientada a objetos",
    "oop": "programacion orientada a objetos",
    "uml": "lenguaje unificado de modelado uml",
    "mvc": "modelo vista controlador mvc",
    "api": "interfaz de programacion api",
    "rest": "arquitectura rest servicios",
    "crud": "operaciones crear leer actualizar eliminar crud",
    "so": "sistemas operativos",
    "os": "sistemas operativos",
    "ia": "inteligencia artificial",
    "ai": "inteligencia artificial",
    "ml": "aprendizaje automatico machine learning",
    "dl": "aprendizaje profundo deep learning",
    "nlp": "procesamiento de lenguaje natural pln",
    "pln": "procesamiento de lenguaje natural pln",
    "ti": "tecnologias de informacion",
    "it": "tecnologias de informacion",
}

# Sinónimos y equivalencias técnicas académicas universales
CONCEPT_SYNONYMS: Dict[str, str] = {
    "router": "encaminador enrutador enrutamiento routing",
    "encaminador": "router enrutador enrutamiento routing",
    "enrutador": "router encaminador enrutamiento routing",
    "switch": "conmutador conmutacion switching",
    "conmutador": "switch conmutacion switching",
    "conmutacion": "switch conmutador switching",
    "redireccionamiento": "redireccion enrutamiento arp resolucion direcciones gateway",
    "arp": "resolucion direcciones redireccionamiento ethernet enlace mac",
    "enlace": "enlace datos tramas datalink mac ethernet",
    "subneteo": "subredes mascara flsm vlsm direccionamiento",
    "subred": "subneteo mascara flsm vlsm direccionamiento",
    "subredes": "subneteo mascara flsm vlsm direccionamiento",
    "flsm": "subredes mascara subneteo direccionamiento",
    "vlsm": "subredes mascara subneteo direccionamiento",
    "ethernet": "conmutacion enlace ieee802 arp",
    "numericos": "binario hexadecimal decimal conversion direccionamiento subredes",
    "seguridad": "ciberseguridad proteccion firewall autenticacion cifrado vlan",
    "aplicacion": "aplicaciones servicios protocolos http dns smtp pop ftp dhcp",
    "pequeña": "diseño configuracion switches integradora red lan",
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
    def expand_technical_acronyms(cls, text: str) -> str:
        """Expande siglas y conceptos técnicos estándar para maximizar la afinidad léxico-semántica."""
        if not text:
            return ""
        words = text.split()
        expanded = []
        for w in words:
            low = w.lower().strip(".,:;()[]-")
            if low in TECHNICAL_ACRONYMS:
                expanded.append(f"{w} {TECHNICAL_ACRONYMS[low]}")
            else:
                expanded.append(w)
        return " ".join(expanded)

    @classmethod
    def expand_technical_synonyms(cls, text: str) -> str:
        """Enriquece el texto con sinónimos técnicos y conceptos equivalentes."""
        if not text:
            return ""
        words = text.split()
        expanded = []
        for w in words:
            low = cls.strip_accents(w.lower().strip(".,:;()[]-"))
            if low in CONCEPT_SYNONYMS:
                expanded.append(f"{w} {CONCEPT_SYNONYMS[low]}")
            else:
                expanded.append(w)
        return " ".join(expanded)

    @classmethod
    def normalize_for_indexing(cls, text: str, remove_stopwords: bool = True, expand_acronyms: bool = True) -> str:
        """
        Normaliza el texto para vectorización léxica (TF-IDF):
        - Minúsculas
        - Expansión de acrónimos técnicos y sinónimos conceptuales
        - Eliminación de acentos
        - Mapeo de signos técnicos (c++ -> cpp, b+ -> bplus)
        - Limpieza de puntuación
        - Remoción controlada de stopwords si se solicita
        """
        if not text:
            return ""

        # Expansión previa de acrónimos técnicos y sinónimos
        if expand_acronyms:
            text = cls.expand_technical_acronyms(text)
            text = cls.expand_technical_synonyms(text)

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
