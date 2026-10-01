import sys
sys.path.insert(0, 'backend')
import re

TECHNICAL_ACRONYMS = {
    # Bases de datos y modelos
    "bbdd": "base de datos",
    "bd": "base de datos",
    "dbms": "sistema gestion bases datos",
    "sgbd": "sistema gestion bases datos",
    "rdbms": "sistema relacional bases datos",
    "er": "entidad relacion",
    "mer": "modelo entidad relacion",
    "der": "diagrama entidad relacion",
    "df": "dependencias funcionales",
    "1fn": "primera forma normal",
    "2fn": "segunda forma normal",
    "3fn": "tercera forma normal",
    "fnbc": "forma normal boyce codd",
    "bcnf": "forma normal boyce codd",
    "sql": "sql Structured Query Language",
    "nosql": "nosql no relacional",
    
    # Redes y telecomunicaciones
    "wan": "red area amplia wan",
    "lan": "red area local lan",
    "vpn": "red privada virtual vpn",
    "qos": "calidad servicio qos",
    "acl": "lista control acceso acl",
    "nat": "traduccion direcciones red nat",
    "ospf": "protocolo ospf enrutamiento",
    "tcp": "protocolo control transmision tcp",
    "udp": "protocolo datagramas udp",
    "ip": "protocolo internet ip",
    "ipv4": "protocolo ipv4 direcciones",
    "ipv6": "protocolo ipv6 direcciones",
    "ipsec": "seguridad ipsec tunel",
    
    # Programación e Ingeniería
    "poo": "programacion orientada objetos",
    "oop": "programacion orientada objetos",
    "uml": "lenguaje modelado uml",
    "api": "interfaz programacion api",
    "rest": "arquitectura rest servicios",
    "crud": "operaciones crear leer actualizar eliminar crud",
    "so": "sistemas operativos",
    "os": "sistemas operativos",
    "ia": "inteligencia artificial",
    "ai": "inteligencia artificial",
    "ml": "aprendizaje automatico machine learning",
}

def expand_technical_terms(text: str) -> str:
    words = text.split()
    expanded = []
    for w in words:
        low = w.lower()
        if low in TECHNICAL_ACRONYMS:
            expanded.append(TECHNICAL_ACRONYMS[low])
        else:
            expanded.append(w)
    return " ".join(expanded)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Caso 1: Un sílabo dice "Diseño con modelo ER y BBDD relacionales"
# El otro dice: "Modelo Entidad Relación en Bases de Datos"
text_a = "Diseño con modelo ER y BBDD relacionales"
text_b = "Modelo Entidad Relación en Bases de Datos relacionales"

vec = TfidfVectorizer()
m_orig = vec.fit_transform([text_a.lower(), text_b.lower()])
sim_orig = cosine_similarity(m_orig[0:1], m_orig[1:2])[0][0]

exp_a = expand_technical_terms(text_a.lower())
exp_b = expand_technical_terms(text_b.lower())
vec2 = TfidfVectorizer()
m_exp = vec2.fit_transform([exp_a, exp_b])
sim_exp = cosine_similarity(m_exp[0:1], m_exp[1:2])[0][0]

print("Caso ER y BBDD vs Entidad Relación en Bases de Datos:")
print(f"  Similitud léxica original: {sim_orig:.4f}")
print(f"  Similitud léxica con expansión técnica: {sim_exp:.4f}")

# Caso 2: Redes WAN y VPN
text_c = "Conceptos de WAN e implementación de VPN"
text_d = "Redes de Área Amplia y túneles de Red Privada Virtual"

vec = TfidfVectorizer()
m_orig2 = vec.fit_transform([text_c.lower(), text_d.lower()])
sim_orig2 = cosine_similarity(m_orig2[0:1], m_orig2[1:2])[0][0]

exp_c = expand_technical_terms(text_c.lower())
exp_d = expand_technical_terms(text_d.lower())
vec2 = TfidfVectorizer()
m_exp2 = vec2.fit_transform([exp_c, exp_d])
sim_exp2 = cosine_similarity(m_exp2[0:1], m_exp2[1:2])[0][0]

print("\nCaso WAN y VPN vs Redes de Área Amplia y Red Privada Virtual:")
print(f"  Similitud léxica original: {sim_orig2:.4f}")
print(f"  Similitud léxica con expansión técnica: {sim_exp2:.4f}")
