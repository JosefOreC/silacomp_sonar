"""
Router de API para ejecución y consulta de Comparaciones de Sílabos.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse

from app.api.deps import (
    get_comparison_repository,
    get_syllabus_repository,
    get_vector_service,
)
from app.infrastructure.reports.html_report_generator import HtmlReportGenerator
from app.infrastructure.reports.pdf_report_generator import PdfReportGenerator
from app.api.schemas import (
    ComparisonEvidenceCatalogResponse,
    ComparisonResponse,
    ContentMatchResponse,
    CreateComparisonRequest,
    EvidenceRegionResponse,
    MatchEvidenceResponse,
    MatchSpatialEvidenceResponse,
    ScoreBreakdownResponse,
    UnmatchedItemResponse,
)
from app.application.compare_syllabi import CompareSyllabiUseCase
from app.domain.comparison import Comparison, ContentMatch, UnmatchedItem
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
from app.infrastructure.persistence.sqlite_syllabus_repository import SqliteSyllabusRepository

router = APIRouter(prefix="/comparisons", tags=["Comparaciones"])


def _map_match_to_response(m: ContentMatch) -> ContentMatchResponse:
    return ContentMatchResponse(
        id=m.id,
        comparison_id=m.comparison_id,
        objective_item_id=m.objective_item_id,
        compared_item_id=m.compared_item_id,
        objective_title=m.objective_title,
        compared_title=m.compared_title,
        objective_section=m.objective_section,
        compared_section=m.compared_section,
        objective_page=m.objective_page,
        compared_page=m.compared_page,
        score_breakdown=ScoreBreakdownResponse(
            semantic_similarity=m.score_breakdown.semantic_similarity,
            lexical_similarity=m.score_breakdown.lexical_similarity,
            keyword_overlap=m.score_breakdown.keyword_overlap,
            structural_similarity=m.score_breakdown.structural_similarity,
            composite_score=m.score_breakdown.composite_score,
            weights=m.score_breakdown.weights,
        ),
        classification=m.classification,
        evidence=MatchEvidenceResponse(
            evidence_type=m.evidence.evidence_type,
            shared_keywords=m.evidence.shared_keywords,
            semantic_score=m.evidence.semantic_score,
            lexical_score=m.evidence.lexical_score,
            objective_snippet=m.evidence.objective_snippet,
            compared_snippet=m.evidence.compared_snippet,
            objective_page=m.evidence.objective_page,
            compared_page=m.evidence.compared_page,
            objective_regions=[
                EvidenceRegionResponse(
                    id=r.id,
                    match_id=r.match_id,
                    syllabus_id=r.syllabus_id,
                    content_id=r.content_id,
                    page_number=r.page_number,
                    page_width=r.page_width,
                    page_height=r.page_height,
                    x0=r.x0,
                    y0=r.y0,
                    x1=r.x1,
                    y1=r.y1,
                    text=r.text,
                    evidence_type=r.evidence_type,
                )
                for r in (getattr(m.evidence, "objective_regions", None) or [])
            ],
            compared_regions=[
                EvidenceRegionResponse(
                    id=r.id,
                    match_id=r.match_id,
                    syllabus_id=r.syllabus_id,
                    content_id=r.content_id,
                    page_number=r.page_number,
                    page_width=r.page_width,
                    page_height=r.page_height,
                    x0=r.x0,
                    y0=r.y0,
                    x1=r.x1,
                    y1=r.y1,
                    text=r.text,
                    evidence_type=r.evidence_type,
                )
                for r in (getattr(m.evidence, "compared_regions", None) or [])
            ],
        ),
    )


def _map_unmatched_to_response(u: UnmatchedItem) -> UnmatchedItemResponse:
    return UnmatchedItemResponse(
        item_id=u.item_id,
        syllabus_id=u.syllabus_id,
        section_name=u.section_name,
        title=u.title,
        text_snippet=u.text_snippet,
        page=u.page,
        best_candidate_id=u.best_candidate_id,
        best_candidate_title=u.best_candidate_title,
        best_score=u.best_score,
    )


def _map_comparison_to_response(comp: Comparison) -> ComparisonResponse:
    return ComparisonResponse(
        id=comp.id,
        objective_syllabus_id=comp.objective_syllabus_id,
        compared_syllabus_id=comp.compared_syllabus_id,
        global_score=comp.global_score,
        objective_coverage=comp.objective_coverage,
        compared_coverage=comp.compared_coverage,
        model_version=comp.model_version,
        created_at=comp.created_at,
        counts=comp.count_by_classification,
        matches=[_map_match_to_response(m) for m in comp.matches],
        unmatched_objective=[_map_unmatched_to_response(u) for u in comp.unmatched_objective],
        unmatched_compared=[_map_unmatched_to_response(u) for u in comp.unmatched_compared],
    )


@router.post("", response_model=ComparisonResponse, status_code=status.HTTP_201_CREATED)
def create_comparison(
    payload: CreateComparisonRequest,
    syl_repo: SqliteSyllabusRepository = Depends(get_syllabus_repository),
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
    vector_service: NlpVectorService = Depends(get_vector_service),
) -> ComparisonResponse:
    """
    Ejecuta el análisis de correspondencia explicable entre dos sílabos previamente cargados.
    """
    obj_syl = syl_repo.get_by_id(payload.objective_syllabus_id)
    if not obj_syl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sílabo objetivo '{payload.objective_syllabus_id}' no encontrado.",
        )

    cmp_syl = syl_repo.get_by_id(payload.compared_syllabus_id)
    if not cmp_syl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sílabo comparado '{payload.compared_syllabus_id}' no encontrado.",
        )

    obj_items = syl_repo.get_content_items(payload.objective_syllabus_id)
    cmp_items = syl_repo.get_content_items(payload.compared_syllabus_id)

    if not obj_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El sílabo objetivo no contiene contenidos temáticos identificables.",
        )

    if not cmp_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El sílabo comparado no contiene contenidos temáticos identificables.",
        )

    use_case = CompareSyllabiUseCase(
        vector_service=vector_service,
        comparison_repository=comp_repo,
    )

    comparison = use_case.execute(
        objective_syllabus_id=payload.objective_syllabus_id,
        compared_syllabus_id=payload.compared_syllabus_id,
        objective_items=obj_items,
        compared_items=cmp_items,
        weights=payload.weights,
        thresholds=payload.thresholds,
        objective_pdf_path=obj_syl.file_path,
        compared_pdf_path=cmp_syl.file_path,
    )

    return _map_comparison_to_response(comparison)


@router.get("", response_model=List[Dict[str, Any]])
def list_comparisons(
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
    syl_repo: SqliteSyllabusRepository = Depends(get_syllabus_repository),
) -> List[Dict[str, Any]]:
    """Retorna la lista de comparaciones anteriores para el historial."""
    comps = comp_repo.list_all()
    results = []
    for c in comps:
        obj = syl_repo.get_by_id(c.objective_syllabus_id)
        cmp = syl_repo.get_by_id(c.compared_syllabus_id)
        results.append({
            "id": c.id,
            "objective_syllabus_id": c.objective_syllabus_id,
            "objective_course": obj.course_name if obj else "Desconocido",
            "objective_university": obj.university if obj else None,
            "compared_syllabus_id": c.compared_syllabus_id,
            "compared_course": cmp.course_name if cmp else "Desconocido",
            "compared_university": cmp.university if cmp else None,
            "global_score": c.global_score,
            "objective_coverage": c.objective_coverage,
            "compared_coverage": c.compared_coverage,
            "model_version": c.model_version,
            "created_at": c.created_at,
        })
    return results


@router.get("/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(
    comparison_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> ComparisonResponse:
    """Obtiene el resultado íntegro de una comparación."""
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")
    return _map_comparison_to_response(comp)


@router.get("/{comparison_id}/matches", response_model=List[ContentMatchResponse])
def get_comparison_matches(
    comparison_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> List[ContentMatchResponse]:
    """Obtiene la lista de correspondencias evaluadas para una comparación."""
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")
    return [_map_match_to_response(m) for m in comp.matches]


@router.get("/{comparison_id}/evidence", response_model=ComparisonEvidenceCatalogResponse)
def get_comparison_evidence(
    comparison_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> ComparisonEvidenceCatalogResponse:
    """
    Retorna el catálogo completo de evidencias y coordenadas espaciales vinculadas a cada correspondencia.
    """
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")

    items = []
    for m in comp.matches:
        obj_regs = [
            EvidenceRegionResponse(
                id=r.id,
                match_id=r.match_id,
                syllabus_id=r.syllabus_id,
                content_id=r.content_id,
                page_number=r.page_number,
                page_width=r.page_width,
                page_height=r.page_height,
                x0=r.x0,
                y0=r.y0,
                x1=r.x1,
                y1=r.y1,
                text=r.text,
                evidence_type=r.evidence_type,
            )
            for r in (getattr(m.evidence, "objective_regions", None) or [])
        ]
        cmp_regs = [
            EvidenceRegionResponse(
                id=r.id,
                match_id=r.match_id,
                syllabus_id=r.syllabus_id,
                content_id=r.content_id,
                page_number=r.page_number,
                page_width=r.page_width,
                page_height=r.page_height,
                x0=r.x0,
                y0=r.y0,
                x1=r.x1,
                y1=r.y1,
                text=r.text,
                evidence_type=r.evidence_type,
            )
            for r in (getattr(m.evidence, "compared_regions", None) or [])
        ]
        items.append(
            MatchSpatialEvidenceResponse(
                match_id=m.id,
                composite_score=m.score_breakdown.composite_score,
                classification=m.classification,
                objective_title=m.objective_title,
                compared_title=m.compared_title,
                objective_page=m.objective_page,
                compared_page=m.compared_page,
                objective_regions=obj_regs,
                compared_regions=cmp_regs,
            )
        )

    return ComparisonEvidenceCatalogResponse(
        comparison_id=comp.id,
        total_matches=len(items),
        evidence_items=items,
    )


@router.get("/{comparison_id}/matches/{match_id}/evidence", response_model=MatchSpatialEvidenceResponse)
def get_match_evidence_detail(
    comparison_id: str,
    match_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> MatchSpatialEvidenceResponse:
    """
    Retorna el detalle espacial unitario de las evidencias de una correspondencia.
    """
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")

    target_match = next((m for m in comp.matches if m.id == match_id), None)
    if not target_match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correspondencia no encontrada.")

    obj_regs = [
        EvidenceRegionResponse(
            id=r.id,
            match_id=r.match_id,
            syllabus_id=r.syllabus_id,
            content_id=r.content_id,
            page_number=r.page_number,
            page_width=r.page_width,
            page_height=r.page_height,
            x0=r.x0,
            y0=r.y0,
            x1=r.x1,
            y1=r.y1,
            text=r.text,
            evidence_type=r.evidence_type,
        )
        for r in (getattr(target_match.evidence, "objective_regions", None) or [])
    ]
    cmp_regs = [
        EvidenceRegionResponse(
            id=r.id,
            match_id=r.match_id,
            syllabus_id=r.syllabus_id,
            content_id=r.content_id,
            page_number=r.page_number,
            page_width=r.page_width,
            page_height=r.page_height,
            x0=r.x0,
            y0=r.y0,
            x1=r.x1,
            y1=r.y1,
            text=r.text,
            evidence_type=r.evidence_type,
        )
        for r in (getattr(target_match.evidence, "compared_regions", None) or [])
    ]

    return MatchSpatialEvidenceResponse(
        match_id=target_match.id,
        composite_score=target_match.score_breakdown.composite_score,
        classification=target_match.classification,
        objective_title=target_match.objective_title,
        compared_title=target_match.compared_title,
        objective_page=target_match.objective_page,
        compared_page=target_match.compared_page,
        objective_regions=obj_regs,
        compared_regions=cmp_regs,
    )


@router.get("/{comparison_id}/unmatched", response_model=Dict[str, List[UnmatchedItemResponse]])
def get_unmatched_items(
    comparison_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> Dict[str, List[UnmatchedItemResponse]]:
    """Obtiene los contenidos sin correspondencia suficiente de ambos sílabos."""
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")
    return {
        "unmatched_objective": [_map_unmatched_to_response(u) for u in comp.unmatched_objective],
        "unmatched_compared": [_map_unmatched_to_response(u) for u in comp.unmatched_compared],
    }


@router.get("/{comparison_id}/report/pdf")
def get_pdf_report(
    comparison_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
    syl_repo: SqliteSyllabusRepository = Depends(get_syllabus_repository),
):
    """Genera y descarga el informe formal en formato PDF (ReportLab)."""
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")
    obj_syl = syl_repo.get_by_id(comp.objective_syllabus_id)
    cmp_syl = syl_repo.get_by_id(comp.compared_syllabus_id)
    if not obj_syl or not cmp_syl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sílabos asociados no encontrados.")

    generator = PdfReportGenerator(output_dir="data/reports")
    report = generator.generate(comp, obj_syl, cmp_syl)
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=f"informe_convalidacion_{comparison_id[:8]}.pdf",
    )


@router.get("/{comparison_id}/report/html", response_class=HTMLResponse)
def get_html_report(
    comparison_id: str,
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
    syl_repo: SqliteSyllabusRepository = Depends(get_syllabus_repository),
):
    """Genera el informe formal en formato HTML imprimible (@media print)."""
    comp = comp_repo.get_by_id(comparison_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparación no encontrada.")
    obj_syl = syl_repo.get_by_id(comp.objective_syllabus_id)
    cmp_syl = syl_repo.get_by_id(comp.compared_syllabus_id)
    if not obj_syl or not cmp_syl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sílabos asociados no encontrados.")

    html_content = HtmlReportGenerator.generate_html(comp, obj_syl, cmp_syl)
    return HTMLResponse(content=html_content)

