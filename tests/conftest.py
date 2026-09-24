"""
Fixtures globales y compartidas para la suite de pruebas unitarias.
"""

import os
import sys

# Asegurar que el paquete app en backend sea importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import fitz
import pytest


@pytest.fixture
def sample_digital_pdf(tmp_path: str) -> str:
    """Genera un archivo PDF digital con texto seleccionable para pruebas."""
    pdf_path = os.path.join(str(tmp_path), "sample_syllabus.pdf")
    doc = fitz.open()

    # Página 1: Sumilla y Datos Generales
    page1 = doc.new_page()
    page1.insert_text(
        (50, 72),
        "UNIVERSIDAD NACIONAL DE INGENIERÍA\n"
        "SÍLABO DEL CURSO: BASE DE DATOS I\n"
        "CÓDIGO: INF-201\n\n"
        "I. SUMILLA\n"
        "El curso introduce los conceptos fundamentales de sistemas de gestión de bases de datos relacionales, "
        "modelo relacional, álgebra relacional, normalización y optimización de consultas SQL.\n\n"
        "II. COMPETENCIAS\n"
        "- Diseña esquemas relacionales normalizados.\n"
        "- Implementa consultas complejas mediante lenguaje SQL estándar.\n"
    )

    # Página 2: Unidades de Aprendizaje
    page2 = doc.new_page()
    page2.insert_text(
        (50, 72),
        "III. UNIDAD I: MODELO RELACIONAL\n"
        "Semana 1: Conceptos de tablas, tuplas, atributos, claves primarias y foráneas.\n"
        "Semana 2: Álgebra relacional, selección, proyección y reuniones naturales.\n\n"
        "IV. UNIDAD II: NORMALIZACIÓN\n"
        "Semana 3: Dependencias funcionales, primera y segunda forma normal.\n"
        "Semana 4: Tercera forma normal (3FN) y Forma Normal de Boyce-Codd.\n"
    )

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def blank_scanned_pdf(tmp_path: str) -> str:
    """Genera un archivo PDF sin texto digital (simulando documento escaneado)."""
    pdf_path = os.path.join(str(tmp_path), "blank_scanned.pdf")
    doc = fitz.open()
    doc.new_page()  # Página en blanco sin texto
    doc.save(pdf_path)
    doc.close()
    return pdf_path
