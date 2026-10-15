"""Reserva y comparación controlada de versiones sobre anotaciones exhaustivas."""

from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from app.application.ground_truth_service import GroundTruthService
from app.domain.academic_sources import academic_source_tokens, connected_source_group_count
from app.domain.evaluation_metrics import aggregate_comparisons, correspondence_metrics, POSITIVE
from app.domain.ground_truth import ConsensusStatus
from app.domain.model_version import ModelVersion
from app.domain.ports import (
    IComparisonRepository, IComparisonEvaluationEngine, IModelVersionRepository,
    IScientificEvaluationRepository, ISyllabusRepository,
)
from app.domain.review import DatasetExample
from app.domain.scientific_evaluation import EvaluationSnapshot, EvaluationExperiment, EvaluationValidationError, evaluation_digest
from app.domain.scoring import BASELINE_VERSION, DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS


class ScientificEvaluationService:
    def __init__(
        self, repository: IScientificEvaluationRepository, comparisons: IComparisonRepository,
        syllabi: ISyllabusRepository, ground_truth: GroundTruthService,
        models: IModelVersionRepository, engine: IComparisonEvaluationEngine,
    ) -> None:
        self.repository, self.comparisons, self.syllabi = repository, comparisons, syllabi
        self.ground_truth, self.models, self.engine = ground_truth, models, engine

    def create_snapshot(self, name: str, comparison_ids: List[str]) -> EvaluationSnapshot:
        if not name.strip() or not comparison_ids or len(set(comparison_ids)) != len(comparison_ids):
            raise EvaluationValidationError("Indique un nombre y comparaciones distintas para reservar.")
        pairs = self.ground_truth.get_pairs()
        lookup = {(p.comparison_id, p.objective_item_id, p.compared_item_id): p for p in pairs}
        cases, reserved, examples = [], set(), []
        cell_count = 0
        nlp_budget = 0
        for comparison_id in sorted(comparison_ids):
            comparison = self.comparisons.get_by_id(comparison_id)
            if comparison is None:
                raise EvaluationValidationError(f"Comparación no encontrada: {comparison_id}.")
            source_ids = [comparison.objective_syllabus_id, comparison.compared_syllabus_id]
            sources = []
            for source_id in source_ids:
                syllabus = self.syllabi.get_by_id(source_id)
                if syllabus is None or not syllabus.university or not syllabus.university.strip() or not (syllabus.course_code or syllabus.course_name or '').strip():
                    raise EvaluationValidationError("Complete universidad y asignatura de ambos sílabos antes de reservar.")
                sources.append({"id": syllabus.id, "university": syllabus.university,
                                "course": syllabus.course_code or syllabus.course_name, "sha256_hash": syllabus.sha256_hash})
            obj_items = self.syllabi.get_content_items(source_ids[0])
            cmp_items = self.syllabi.get_content_items(source_ids[1])
            if not obj_items or not cmp_items:
                raise EvaluationValidationError("La evaluación requiere contenidos en ambos sílabos.")
            cell_count += len(obj_items) * len(cmp_items)
            nlp_budget += len(obj_items) * len(cmp_items) + len(cmp_items) ** 2
            if cell_count > 10000:
                raise EvaluationValidationError("El snapshot supera el límite de 10000 pares; seleccione menos comparaciones.")
            if nlp_budget > 20000:
                raise EvaluationValidationError("La captura supera 20000 pares de cálculo NLP; seleccione menos comparaciones.")
            labels = []
            for obj in obj_items:
                for cmp in cmp_items:
                    pair = lookup.get((comparison_id, obj.id, cmp.id))
                    if pair is None or pair.status != ConsensusStatus.CONSENSUS or pair.consensus_label.value == "UNCERTAIN":
                        raise EvaluationValidationError(
                            f"{comparison_id}: falta consenso definitivo en el par {obj.id} / {cmp.id}. "
                            "Se requiere la matriz completa; los pares no revisados no son negativos."
                        )
                    labels.append({"objective_item_id": obj.id, "compared_item_id": cmp.id,
                                   "label": pair.consensus_label.value, "review_ids": sorted(v.id for v in pair.votes)})
                    example = DatasetExample(
                        id=f"RESERVED-{comparison_id}-{obj.id}-{cmp.id}", review_id=pair.example.review_id,
                        objective_item_id=obj.id, compared_item_id=cmp.id, objective_text=obj.text, compared_text=cmp.text,
                        source_university_obj=sources[0]["university"], source_university_cmp=sources[1]["university"],
                        source_course_obj=sources[0]["course"], source_course_cmp=sources[1]["course"],
                        source_syllabus_obj=source_ids[0], source_syllabus_cmp=source_ids[1],
                        source_syllabus_hash_obj=sources[0]["sha256_hash"], source_syllabus_hash_cmp=sources[1]["sha256_hash"],
                    )
                    examples.append(example)
                    reserved.update(academic_source_tokens(example))
                    reserved.update(academic_source_tokens(pair.example))
            cases.append({"comparison_id": comparison_id, "objective_syllabus": sources[0], "compared_syllabus": sources[1],
                          "objective_items": [asdict(item) for item in obj_items], "compared_items": [asdict(item) for item in cmp_items],
                          "labels": labels, "weights": dict(DEFAULT_WEIGHTS), "thresholds": dict(DEFAULT_THRESHOLDS)})
        # Validar toda la anotación antes de invocar NLP o guardar una reserva.
        for case in cases:
            case["nlp_trace"] = self.engine.capture(case)
        payload = {"schema_version": 1, "protocol": "full-comparison-replay-001", "cases": cases,
                   "reserved_source_tokens": sorted(reserved), "fingerprint": self.engine.fingerprint(),
                   "independent_groups": connected_source_group_count(examples), "pair_count": cell_count}
        snapshot = EvaluationSnapshot("SNAP-" + uuid.uuid4().hex, name.strip(), datetime.now(), evaluation_digest(payload), payload)
        self.repository.save_snapshot(snapshot)
        return snapshot

    def _model(self, version_id: str, snapshot: EvaluationSnapshot) -> Optional[ModelVersion]:
        if version_id == BASELINE_VERSION:
            return None
        model = self.models.get_by_id(version_id)
        if model is None:
            raise EvaluationValidationError(f"Modelo no encontrado: {version_id}.")
        sources = model.metrics.get("data_source_tokens")
        if model.metrics.get("data_provenance_schema") != 2 or not sources or any(token[0] == "unknown_provenance" for token in sources):
            raise EvaluationValidationError("El modelo carece de procedencia verificable. Reentrene con revisiones humanas no reservadas.")
        reserved = {tuple(token) for token in snapshot.payload["reserved_source_tokens"]}
        if reserved.intersection(tuple(token) for token in sources):
            raise EvaluationValidationError("El modelo estuvo expuesto a fuentes del conjunto reservado; no se ejecutó el experimento.")
        return model

    def run_experiment(
        self, snapshot_id: str, reference_version: str, candidate_version: str, criteria: Dict[str, Any],
    ) -> EvaluationExperiment:
        snapshot = self.repository.get_snapshot(snapshot_id)
        if snapshot is None:
            raise EvaluationValidationError("Snapshot no encontrado.")
        if snapshot.content_hash != evaluation_digest(snapshot.payload):
            raise EvaluationValidationError("El contenido del snapshot fue alterado.")
        if snapshot.payload["fingerprint"] != self.engine.fingerprint():
            raise EvaluationValidationError("El código o el entorno cambió; el replay de este snapshot no es compatible.")
        if reference_version == candidate_version:
            raise EvaluationValidationError("Seleccione versiones distintas para comparar.")
        models = {"reference": self._model(reference_version, snapshot), "candidate": self._model(candidate_version, snapshot)}
        evaluations = {}
        for role, model in models.items():
            rows, manifest = [], None
            for case in snapshot.payload["cases"]:
                prediction, case_manifest = self.engine.evaluate(case, model)
                if manifest is not None and manifest != case_manifest:
                    raise EvaluationValidationError("La identidad del modelo cambió entre comparaciones.")
                manifest = case_manifest
                rows.append(correspondence_metrics(case, prediction))
            evaluations[role] = {"manifest": manifest, "aggregate": aggregate_comparisons(rows), "comparisons": rows}
        ref, cand = evaluations["reference"]["aggregate"], evaluations["candidate"]["aggregate"]
        regressions = []
        for before, after in zip(evaluations["reference"]["comparisons"], evaluations["candidate"]["comparisons"]):
            regressions.append({"comparison_id": before["comparison_id"], "f1_delta": after["f1"] - before["f1"],
                                "objective_error_delta": after["objective_coverage_error"] - before["objective_coverage_error"],
                                "compared_error_delta": after["compared_coverage_error"] - before["compared_coverage_error"]})
        positives = sum(label["label"] in POSITIVE for case in snapshot.payload["cases"] for label in case["labels"])
        checks = {
            "f1_gain": cand["f1"] - ref["f1"] >= criteria["min_f1_gain"] - 1e-12,
            "recall": ref["recall"] - cand["recall"] <= criteria["max_recall_drop"] + 1e-12,
            "objective_coverage": cand["objective_coverage_mae"] - ref["objective_coverage_mae"] <= criteria["max_coverage_mae_increase"] + 1e-12,
            "compared_coverage": cand["compared_coverage_mae"] - ref["compared_coverage_mae"] <= criteria["max_coverage_mae_increase"] + 1e-12,
            "per_comparison_f1": all(-row["f1_delta"] <= criteria["max_per_comparison_f1_drop"] + 1e-12 for row in regressions),
            "per_comparison_coverage": all(max(row["objective_error_delta"], row["compared_error_delta"])
                                           <= criteria["max_per_comparison_coverage_increase"] + 1e-12 for row in regressions),
            "independent_groups": snapshot.payload["independent_groups"] >= criteria["min_independent_groups"],
            "positive_and_negative_support": 0 < positives < snapshot.payload["pair_count"],
        }
        report = {"snapshot_hash": snapshot.content_hash, "protocol": snapshot.payload["protocol"],
                  "fingerprint_hash": evaluation_digest(snapshot.payload["fingerprint"]),
                  "sample": {"comparisons": len(snapshot.payload["cases"]), "pairs": snapshot.payload["pair_count"],
                             "independent_groups": snapshot.payload["independent_groups"], "positive_pairs": positives,
                             "negative_pairs": snapshot.payload["pair_count"] - positives},
                  "evaluations": evaluations, "criteria": criteria, "checks": checks, "regressions": regressions,
                  "promotion_recommended": all(checks.values()), "automatic_activation": False}
        experiment = EvaluationExperiment("EXP-" + uuid.uuid4().hex, snapshot.id, datetime.now(), report)
        self.repository.save_experiment(experiment)
        return experiment
