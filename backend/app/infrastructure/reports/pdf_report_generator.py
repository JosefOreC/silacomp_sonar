"""
Generador de informes formales en PDF mediante ReportLab.
Implementa el puerto IReportGenerator con todas las secciones estándar del planteamiento.
"""

from datetime import datetime
import os
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.domain.comparison import Comparison, MatchClassification
from app.domain.model_version import Report, ReportFormat
from app.domain.ports import IReportGenerator
from app.domain.syllabus import Syllabus


DISCLAIMER_TEXT = (
    "El presente documento corresponde a un informe de análisis computacional de correspondencia "
    "entre los sílabos proporcionados. Los resultados se obtienen mediante técnicas de procesamiento de lenguaje natural, "
    "análisis léxico, análisis semántico y criterios estructurales configurados para el sistema. "
    "La información presentada constituye una pre-evaluación y elemento de apoyo para la revisión académica, "
    "por lo que no sustituye la evaluación, validación ni decisión de las autoridades o responsables académicos correspondientes."
)


class PdfReportGenerator(IReportGenerator):
    """Genera documentos PDF formales descargables utilizando ReportLab."""

    def __init__(self, output_dir: str = "data/reports") -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(
        self,
        comparison: Comparison,
        obj_syllabus: Syllabus,
        cmp_syllabus: Syllabus,
        report_format: ReportFormat = ReportFormat.PDF,
    ) -> Report:
        """Construye y compila el documento PDF formal."""
        report_id = f"REP-{comparison.id}"
        filename = f"informe_{comparison.id}.pdf"
        file_path = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0F172A"),
            alignment=1,  # Centrado
            spaceAfter=15,
        )

        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=12,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )

        meta_label_style = ParagraphStyle(
            "DocMetaLabel",
            parent=body_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0F172A"),
        )

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=body_style,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#78350F"),
            backColor=colors.HexColor("#FFFBEB"),
            borderColor=colors.HexColor("#F59E0B"),
            borderWidth=1,
            borderPadding=8,
            spaceBefore=15,
        )

        story = []

        # --- PORTADA / CABECERA ---
        story.append(Paragraph("INFORME DE COMPARACIÓN DE SÍLABOS", title_style))
        story.append(Paragraph("<font size=10 color='#64748B'>Pre-Evaluación Computacional de Correspondencia Académica</font>", ParagraphStyle("Sub", alignment=1, spaceAfter=15)))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=15))

        # Ficha de identificación
        meta_data = [
            [
                Paragraph("<b>SÍLABO OBJETIVO (Referencia)</b>", meta_label_style),
                Paragraph("<b>SÍLABO COMPARADO (Evaluado)</b>", meta_label_style),
            ],
            [
                Paragraph(f"<b>Curso:</b> {obj_syllabus.course_name or obj_syllabus.filename}<br/><b>Universidad:</b> {obj_syllabus.university or 'N/E'}<br/><b>Código:</b> {obj_syllabus.course_code or 'N/D'}<br/><b>Páginas:</b> {obj_syllabus.total_pages}", body_style),
                Paragraph(f"<b>Curso:</b> {cmp_syllabus.course_name or cmp_syllabus.filename}<br/><b>Universidad:</b> {cmp_syllabus.university or 'N/E'}<br/><b>Código:</b> {cmp_syllabus.course_code or 'N/D'}<br/><b>Páginas:</b> {cmp_syllabus.total_pages}", body_style),
            ],
            [
                Paragraph(f"<b>ID Comparación:</b> {comparison.id}", body_style),
                Paragraph(f"<b>Fecha:</b> {comparison.created_at.strftime('%d/%m/%Y %H:%M')}", body_style),
            ],
        ]

        t_meta = Table(meta_data, colWidths=[265, 265])
        t_meta.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(t_meta)
        story.append(Spacer(1, 15))

        # --- 1. RESUMEN EJECUTIVO ---
        story.append(Paragraph("1. Resumen Ejecutivo de Resultados", h2_style))

        global_pct = round(comparison.global_score * 100.0, 1)
        kpi_data = [
            [
                Paragraph(f"<font size=18 color='#0284C7'><b>{global_pct} %</b></font><br/><font size=8 color='#475569'>CORRESPONDENCIA GLOBAL</font>", ParagraphStyle("K1", alignment=1)),
                Paragraph(f"<font size=18 color='#0F172A'><b>{comparison.objective_coverage}%</b></font><br/><font size=8 color='#475569'>COBERTURA DEL OBJETIVO</font>", ParagraphStyle("K2", alignment=1)),
                Paragraph(f"<font size=18 color='#0F172A'><b>{comparison.compared_coverage}%</b></font><br/><font size=8 color='#475569'>COBERTURA DEL COMPARADO</font>", ParagraphStyle("K3", alignment=1)),
            ]
        ]
        t_kpi = Table(kpi_data, colWidths=[176, 176, 176])
        t_kpi.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ])
        )
        story.append(t_kpi)
        story.append(Spacer(1, 10))

        # Tabla de distribución
        counts = comparison.count_by_classification
        dist_data = [
            ["Clasificación", "Cantidad", "Criterio Técnico"],
            ["MATCH (Alta)", str(counts.get("MATCH", 0)), "Correspondencia demostrable con evidencia suficiente (>= 0.85)"],
            ["PARTIAL_MATCH (Parcial)", str(counts.get("PARTIAL_MATCH", 0)), "Correspondencia parcial relevante (0.70 - 0.84)"],
            ["UNCERTAIN (Incierta)", str(counts.get("UNCERTAIN", 0)), "Requiere revisión humana prioritaria (0.50 - 0.69)"],
            ["NO_MATCH (Sin correspondencia)", str(counts.get("NO_MATCH", 0)), "Sin evidencia de relación suficiente (< 0.50)"],
        ]
        t_dist = Table(dist_data, colWidths=[140, 60, 330])
        t_dist.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_dist)
        story.append(Spacer(1, 15))

        # --- 2. TABLA PRINCIPAL DE CORRESPONDENCIAS ---
        story.append(Paragraph("2. Tabla de Correspondencias Identificadas", h2_style))

        match_table_data = [["Contenido Objetivo", "Contenido Comparado", "Tipo", "Score", "Evidencia y BBox"]]
        for m in sorted(comparison.matches, key=lambda x: x.score, reverse=True)[:25]:  # Hasta 25 principales en tabla
            kw_str = ", ".join(m.evidence.shared_keywords[:3]) or "Evidencia semántica"
            spatial_info = ""
            obj_regs = getattr(m.evidence, "objective_regions", None) or []
            cmp_regs = getattr(m.evidence, "compared_regions", None) or []
            if obj_regs or cmp_regs:
                coords = []
                if obj_regs:
                    r0 = obj_regs[0]
                    coords.append(f"Obj P.{r0.page_number} [{r0.x0:.0f},{r0.y0:.0f}]")
                if cmp_regs:
                    rc = cmp_regs[0]
                    coords.append(f"Cmp P.{rc.page_number} [{rc.x0:.0f},{rc.y0:.0f}]")
                spatial_info = f"<br/><font color='#1D4ED8' size=6.5><b>BBox:</b> {' | '.join(coords)}</font>"

            match_table_data.append([
                Paragraph(f"<b>{m.objective_title[:42]}</b><br/><font color='#64748B' size=7>{m.objective_section} (Pág. {m.objective_page})</font>", body_style),
                Paragraph(f"<b>{m.compared_title[:42]}</b><br/><font color='#64748B' size=7>{m.compared_section} (Pág. {m.compared_page})</font>", body_style),
                m.classification.value,
                f"{m.score:.2f}",
                Paragraph(f"<font size=7>{kw_str}</font>{spatial_info}", body_style),
            ])

        t_matches = Table(match_table_data, colWidths=[130, 130, 70, 45, 155])
        t_matches.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ALIGN", (2, 0), (3, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_matches)
        story.append(Spacer(1, 15))

        # --- 3. CONTENIDOS SIN CORRESPONDENCIA ---
        story.append(Paragraph("3. Brechas y Contenidos sin Correspondencia", h2_style))

        unmatched_obj_data = [["Tema Objetivo No Cubierto", "Unidad", "Pág.", "Mejor Candidato Detectado"]]
        for u in comparison.unmatched_objective[:10]:
            best = f"{u.best_candidate_title[:35]} ({u.best_score:.2f})" if u.best_candidate_title else "N/D"
            unmatched_obj_data.append([
                Paragraph(u.title, body_style),
                Paragraph(u.section_name, body_style),
                str(u.page),
                Paragraph(best, body_style),
            ])

        if len(unmatched_obj_data) > 1:
            t_unmatched = Table(unmatched_obj_data, colWidths=[190, 120, 40, 180])
            t_unmatched.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ])
            )
            story.append(t_unmatched)
        else:
            story.append(Paragraph("<i>Todos los contenidos del objetivo presentan cobertura estimada.</i>", body_style))

        story.append(Spacer(1, 15))

        # --- 4. TRAZABILIDAD Y METODOLOGÍA ---
        story.append(Paragraph("4. Metodología y Trazabilidad Computacional", h2_style))
        method_text = (
            f"<b>Motor computacional:</b> PyMuPDF (extracción no destructiva por página) + TextNormalizer + "
            f"TF-IDF n-gramas + Embeddings semánticos multilingües.<br/>"
            f"<b>Fórmula de Score:</b> 0.40 Semántica + 0.30 Léxica + 0.15 Palabras Clave + 0.15 Estructura.<br/>"
            f"<b>Versión del algoritmo:</b> {comparison.model_version} | <b>Identificador:</b> {comparison.id}"
        )
        story.append(Paragraph(method_text, body_style))

        # --- 5. ANEXO DE TRAZABILIDAD ESPACIAL DE EVIDENCIAS (FASE 1.5) ---
        has_spatial_evidence = any(
            (getattr(m.evidence, "objective_regions", None) or getattr(m.evidence, "compared_regions", None))
            for m in comparison.matches
        )

        if has_spatial_evidence:
            story.append(Spacer(1, 10))
            story.append(Paragraph("5. Anexo de Trazabilidad Espacial de Evidencias (Fase 1.5)", h2_style))
            spatial_intro = (
                "Para garantizar la transparencia pericial y reproducibilidad técnica conforme a la Fase 1.5, "
                "se listan las coordenadas espaciales exactas (puntos tipográficos 72 DPI) "
                "localizadas de forma no destructiva en los documentos fuente:"
            )
            story.append(Paragraph(spatial_intro, body_style))
            story.append(Spacer(1, 6))

            spatial_table_data = [["ID Coincidencia", "Páginas y Bounding Boxes Objetivo", "Páginas y Bounding Boxes Comparado", "Texto Evidencia Localizado"]]
            for m in sorted(comparison.matches, key=lambda x: x.score, reverse=True)[:15]:
                obj_regs = getattr(m.evidence, "objective_regions", None) or []
                cmp_regs = getattr(m.evidence, "compared_regions", None) or []
                if not obj_regs and not cmp_regs:
                    continue

                obj_desc = "<br/>".join([f"Pág. {r.page_number} [{r.x0:.1f}, {r.y0:.1f}, {r.x1:.1f}, {r.y1:.1f}]" for r in obj_regs[:2]]) or "N/D"
                cmp_desc = "<br/>".join([f"Pág. {r.page_number} [{r.x0:.1f}, {r.y0:.1f}, {r.x1:.1f}, {r.y1:.1f}]" for r in cmp_regs[:2]]) or "N/D"
                snippet = (m.evidence.objective_snippet[:90] + "...") if m.evidence.objective_snippet else "Sin extracto"

                spatial_table_data.append([
                    Paragraph(f"<font size=7><b>{m.id}</b><br/>{m.classification.value} ({m.score:.2f})</font>", body_style),
                    Paragraph(f"<font size=6.5 color='#1E40AF'>{obj_desc}</font>", body_style),
                    Paragraph(f"<font size=6.5 color='#047857'>{cmp_desc}</font>", body_style),
                    Paragraph(f"<font size=6.5 color='#475569'><i>\"{snippet}\"</i></font>", body_style),
                ])

            if len(spatial_table_data) > 1:
                t_spatial = Table(spatial_table_data, colWidths=[90, 140, 140, 160])
                t_spatial.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ])
                )
                story.append(t_spatial)

        story.append(Paragraph(f"<b>NOTA DE ALCANCE ACADÉMICO:</b><br/>{DISCLAIMER_TEXT}", disclaimer_style))

        # Compilar PDF
        doc.build(story)

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        return Report(
            report_id=report_id,
            comparison_id=comparison.id,
            report_format=ReportFormat.PDF,
            report_version="1.0",
            file_path=file_path,
            generated_at=datetime.now(),
            model_version=comparison.model_version,
            file_size_bytes=file_size,
        )
