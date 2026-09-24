"""
Generador de informes formales en formato HTML imprimible (@media print).
"""

from datetime import datetime
from app.domain.comparison import Comparison, MatchClassification
from app.domain.syllabus import Syllabus


DISCLAIMER_TEXT = (
    "El presente documento corresponde a un informe de análisis computacional de correspondencia "
    "entre los sílabos proporcionados. Los resultados se obtienen mediante técnicas de procesamiento de lenguaje natural, "
    "análisis léxico, análisis semántico y criterios estructurales configurados para el sistema. "
    "La información presentada constituye una pre-evaluación y elemento de apoyo para la revisión académica, "
    "por lo que no sustituye la evaluación, validación ni decisión de las autoridades o responsables académicos correspondientes."
)


class HtmlReportGenerator:
    """Genera una página HTML formal y estilizada apta para impresión o exportación PDF desde navegador."""

    @classmethod
    def generate_html(cls, comparison: Comparison, obj_syllabus: Syllabus, cmp_syllabus: Syllabus) -> str:
        date_str = comparison.created_at.strftime("%d/%m/%Y %H:%M")
        global_pct = round(comparison.global_score * 100.0, 1)

        counts = comparison.count_by_classification
        total_matches = comparison.total_matches

        # Construir filas de tabla de matches
        match_rows_html = []
        for m in sorted(comparison.matches, key=lambda x: x.score, reverse=True):
            badge_class = {
                MatchClassification.MATCH: "badge-match",
                MatchClassification.PARTIAL_MATCH: "badge-partial",
                MatchClassification.UNCERTAIN: "badge-uncertain",
                MatchClassification.NO_MATCH: "badge-nomatch",
            }.get(m.classification, "badge-uncertain")

            kw_str = ", ".join(m.evidence.shared_keywords[:5]) or "Evidencia semántica contextual"

            match_rows_html.append(f"""
            <tr>
                <td><strong>{m.objective_title}</strong><br><small class="text-muted">{m.objective_section} (Pág. {m.objective_page})</small></td>
                <td><strong>{m.compared_title}</strong><br><small class="text-muted">{m.compared_section} (Pág. {m.compared_page})</small></td>
                <td style="text-align: center;"><span class="badge {badge_class}">{m.classification.value}</span></td>
                <td style="text-align: center; font-weight: bold;">{m.score:.2f}</td>
                <td><small>{kw_str}</small></td>
            </tr>
            """)

        # Construir detalle de correspondencias
        detail_blocks_html = []
        for idx, m in enumerate(sorted(comparison.matches, key=lambda x: x.score, reverse=True), start=1):
            kw_list_html = "".join(f"<li><code>{kw}</code></li>" for kw in m.evidence.shared_keywords) or "<li><em>Similitud conceptual en espacio de embeddings</em></li>"
            detail_blocks_html.append(f"""
            <div class="match-detail-card">
                <h4>6.{idx}. {m.objective_title} &harr; {m.compared_title}</h4>
                <div class="grid-2">
                    <div class="box-content">
                        <strong>Sílabo Objetivo:</strong> {m.objective_section} (Pág. {m.objective_page})<br>
                        <em>"{m.evidence.objective_snippet}"</em>
                    </div>
                    <div class="box-content">
                        <strong>Sílabo Comparado:</strong> {m.compared_section} (Pág. {m.compared_page})<br>
                        <em>"{m.evidence.compared_snippet}"</em>
                    </div>
                </div>
                <div class="indicators-row">
                    <span><strong>Score Ponderado:</strong> {m.score:.3f}</span>
                    <span><strong>Semántica:</strong> {m.score_breakdown.semantic_similarity:.2f}</span>
                    <span><strong>Léxica:</strong> {m.score_breakdown.lexical_similarity:.2f}</span>
                    <span><strong>Solapamiento:</strong> {m.score_breakdown.keyword_overlap:.2f}</span>
                    <span><strong>Estructural:</strong> {m.score_breakdown.structural_similarity:.2f}</span>
                </div>
                <div class="keywords-box">
                    <strong>Términos clave compartidos:</strong>
                    <ul class="inline-list">{kw_list_html}</ul>
                </div>
            </div>
            """)

        # Construir brechas
        unmatched_obj_html = []
        for u in comparison.unmatched_objective:
            best_ref = f"{u.best_candidate_title} (Score: {u.best_score:.2f})" if u.best_candidate_title else "Ninguno"
            unmatched_obj_html.append(f"""
            <tr>
                <td><strong>{u.title}</strong></td>
                <td>{u.section_name}</td>
                <td style="text-align: center;">Pág. {u.page}</td>
                <td><small>{best_ref}</small></td>
            </tr>
            """)

        unmatched_cmp_html = []
        for u in comparison.unmatched_compared:
            best_ref = f"{u.best_candidate_title} (Score: {u.best_score:.2f})" if u.best_candidate_title else "Ninguno"
            unmatched_cmp_html.append(f"""
            <tr>
                <td><strong>{u.title}</strong></td>
                <td>{u.section_name}</td>
                <td style="text-align: center;">Pág. {u.page}</td>
                <td><small>{best_ref}</small></td>
            </tr>
            """)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe de Comparación de Sílabos — {comparison.id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1E293B;
            line-height: 1.5;
            background: #FFFFFF;
            padding: 30px;
            max-width: 960px;
            margin: 0 auto;
        }}
        .header {{
            border-bottom: 2px solid #0F172A;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        h1 {{ margin: 0 0 6px 0; font-size: 24px; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; }}
        h2 {{ font-size: 18px; color: #1E293B; border-bottom: 1px solid #CBD5E1; padding-bottom: 6px; margin-top: 30px; }}
        h3 {{ font-size: 15px; color: #334155; margin-top: 20px; }}
        h4 {{ font-size: 14px; margin: 0 0 10px 0; color: #0F172A; }}
        .meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            background: #F8FAFC;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #E2E8F0;
            margin-bottom: 24px;
        }}
        .kpi-row {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .kpi-card {{
            flex: 1;
            padding: 16px;
            background: #F1F5F9;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #CBD5E1;
        }}
        .kpi-val {{ font-size: 32px; font-weight: bold; color: #0284C7; margin-bottom: 4px; }}
        .kpi-label {{ font-size: 12px; color: #475569; text-transform: uppercase; font-weight: 600; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin: 16px 0;
        }}
        th, td {{
            border: 1px solid #CBD5E1;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{ background: #F1F5F9; font-weight: 600; color: #334155; }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            display: inline-block;
        }}
        .badge-match {{ background: #DCFCE7; color: #166534; }}
        .badge-partial {{ background: #FEF3C7; color: #92400E; }}
        .badge-uncertain {{ background: #F3E8FF; color: #6B21A8; }}
        .badge-nomatch {{ background: #FEE2E2; color: #991B1B; }}
        .match-detail-card {{
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
            background: #FAFAFA;
            page-break-inside: avoid;
        }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 12px; }}
        .box-content {{ background: #FFFFFF; border: 1px solid #E2E8F0; padding: 10px; border-radius: 4px; font-size: 12px; }}
        .indicators-row {{ font-size: 12px; color: #334155; display: flex; gap: 16px; margin: 10px 0; border-top: 1px dashed #CBD5E1; padding-top: 8px; }}
        .inline-list {{ list-style: none; padding: 0; margin: 6px 0 0 0; display: flex; flex-wrap: wrap; gap: 6px; }}
        .inline-list li code {{ background: #E2E8F0; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
        .disclaimer-box {{
            background: #FFFBEB;
            border-left: 4px solid #F59E0B;
            padding: 14px;
            font-size: 12px;
            color: #78350F;
            margin-top: 30px;
            line-height: 1.5;
        }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
            .match-detail-card {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div style="float: right; text-align: right;">
            <small>ID: {comparison.id}</small><br>
            <small>Fecha: {date_str}</small><br>
            <small>Versión: {comparison.model_version}</small>
        </div>
        <h1>Informe de Comparación de Sílabos</h1>
        <p style="color: #64748B; margin-top: 4px;">Sistema Inteligente de Pre-Evaluación de Correspondencia Académica</p>
    </div>

    <div class="meta-grid">
        <div>
            <h3 style="margin-top: 0; color: #0284C7;">Sílabo Objetivo (Referencia)</h3>
            <p><strong>Curso:</strong> {obj_syllabus.course_name or obj_syllabus.filename}</p>
            <p><strong>Universidad:</strong> {obj_syllabus.university or "No especificada"}</p>
            <p><strong>Código:</strong> {obj_syllabus.course_code or "N/D"}</p>
            <p><strong>Páginas:</strong> {obj_syllabus.total_pages} | <strong>Contenidos evaluados:</strong> {len(obj_syllabus.pages)}</p>
        </div>
        <div>
            <h3 style="margin-top: 0; color: #64748B;">Sílabo Comparado (Evaluado)</h3>
            <p><strong>Curso:</strong> {cmp_syllabus.course_name or cmp_syllabus.filename}</p>
            <p><strong>Universidad:</strong> {cmp_syllabus.university or "No especificada"}</p>
            <p><strong>Código:</strong> {cmp_syllabus.course_code or "N/D"}</p>
            <p><strong>Páginas:</strong> {cmp_syllabus.total_pages} | <strong>Contenidos evaluados:</strong> {len(cmp_syllabus.pages)}</p>
        </div>
    </div>

    <h2>1. Resumen Ejecutivo de Resultados</h2>
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-val">{global_pct} %</div>
            <div class="kpi-label">Correspondencia Global Estimada</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{comparison.objective_coverage}%</div>
            <div class="kpi-label">Cobertura del Objetivo</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{comparison.compared_coverage}%</div>
            <div class="kpi-label">Cobertura del Comparado</div>
        </div>
    </div>

    <h3>Distribución de Correspondencias Identificadas ({total_matches} relaciones)</h3>
    <table>
        <thead>
            <tr>
                <th>Clasificación</th>
                <th style="text-align: center;">Cantidad</th>
                <th>Criterio Técnico</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="badge badge-match">MATCH</span></td>
                <td style="text-align: center; font-weight: bold;">{counts.get("MATCH", 0)}</td>
                <td>Correspondencia fuerte demostrable (&ge; 0.85)</td>
            </tr>
            <tr>
                <td><span class="badge badge-partial">PARTIAL_MATCH</span></td>
                <td style="text-align: center; font-weight: bold;">{counts.get("PARTIAL_MATCH", 0)}</td>
                <td>Correspondencia parcial relevante (0.70 &ndash; 0.84)</td>
            </tr>
            <tr>
                <td><span class="badge badge-uncertain">UNCERTAIN</span></td>
                <td style="text-align: center; font-weight: bold;">{counts.get("UNCERTAIN", 0)}</td>
                <td>Requiere revisión académica humana (0.50 &ndash; 0.69)</td>
            </tr>
            <tr>
                <td><span class="badge badge-nomatch">NO_MATCH</span></td>
                <td style="text-align: center; font-weight: bold;">{counts.get("NO_MATCH", 0)}</td>
                <td>Sin evidencia de relación suficiente (&lt; 0.50)</td>
            </tr>
        </tbody>
    </table>

    <h2>2. Tabla Sinóptica de Correspondencias</h2>
    <table>
        <thead>
            <tr>
                <th>Contenido Objetivo</th>
                <th>Contenido Comparado</th>
                <th style="text-align: center;">Tipo</th>
                <th style="text-align: center;">Score</th>
                <th>Evidencia Principal</th>
            </tr>
        </thead>
        <tbody>
            {"".join(match_rows_html)}
        </tbody>
    </table>

    <h2>3. Detalle de Correspondencias y Evidencias Observables</h2>
    {"".join(detail_blocks_html)}

    <h2>4. Brechas y Contenidos sin Correspondencia</h2>
    <h3>4.1 Contenidos del Sílabo Objetivo no cubiertos ({len(comparison.unmatched_objective)})</h3>
    <table>
        <thead>
            <tr>
                <th>Tema / Contenido</th>
                <th>Unidad</th>
                <th style="text-align: center;">Página</th>
                <th>Mejor Candidato Detectado</th>
            </tr>
        </thead>
        <tbody>
            {"".join(unmatched_obj_html) if unmatched_obj_html else '<tr><td colspan="4" style="text-align:center;">Todos los contenidos del objetivo presentan cobertura.</td></tr>'}
        </tbody>
    </table>

    <h3>4.2 Contenidos del Sílabo Comparado no presentes en el Objetivo ({len(comparison.unmatched_compared)})</h3>
    <table>
        <thead>
            <tr>
                <th>Tema / Contenido</th>
                <th>Unidad</th>
                <th style="text-align: center;">Página</th>
                <th>Mejor Candidato en Objetivo</th>
            </tr>
        </thead>
        <tbody>
            {"".join(unmatched_cmp_html) if unmatched_cmp_html else '<tr><td colspan="4" style="text-align:center;">Todos los contenidos del comparado coinciden con el objetivo.</td></tr>'}
        </tbody>
    </table>

    <h2>5. Trazabilidad y Metodología Computacional</h2>
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; font-size: 12px; border-radius: 4px;">
        <p><strong>Extracción:</strong> PyMuPDF (Preservación de coordenadas y número de página física).</p>
        <p><strong>Normalización:</strong> TextNormalizer (Minúsculas, diacríticos, stopwords académicas y protección de símbolos técnicos como c++, b+, sql).</p>
        <p><strong>Representación:</strong> TF-IDF unigrama+bigrama (scikit-learn) y Embeddings densos multilingües (Sentence Transformers).</p>
        <p><strong>Fórmula de Scoring:</strong> Score = 0.40 &times; Semántica + 0.30 &times; Léxica + 0.15 &times; Palabras Clave + 0.15 &times; Estructura.</p>
        <p><strong>Versión del Modelo:</strong> {comparison.model_version} | <strong>ID de Comparación:</strong> {comparison.id}</p>
    </div>

    <div class="disclaimer-box">
        <strong>NOTA FORMAL SOBRE EL ALCANCE DEL RESULTADO:</strong><br>
        {DISCLAIMER_TEXT}
    </div>
</body>
</html>
"""
