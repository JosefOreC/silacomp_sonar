"""
Caso de uso para el entrenamiento controlado, calibración y registro de versiones de modelos (Fase 2.0).
"""

from typing import Any, Dict, Optional, Tuple

from app.application.dataset_service import DatasetService
from app.application.ground_truth_service import GroundTruthService
from app.domain.model_version import ModelVersion
from app.domain.ports import IDatasetRepository, IModelVersionRepository, IReviewRepository, ISupervisedModelTrainer, IReservedEvaluationPolicy


class TrainModelUseCase:
    """Orquesta el ciclo científico de entrenamiento, evaluación comparativa y registro de modelos."""

    def __init__(
        self,
        dataset_repo: IDatasetRepository,
        model_version_repo: IModelVersionRepository,
        trainer: ISupervisedModelTrainer,
        review_repo: Optional[IReviewRepository] = None,
        reserved_policy: Optional[IReservedEvaluationPolicy] = None,
    ) -> None:
        self.dataset_repo = dataset_repo
        self.model_version_repo = model_version_repo
        self.trainer = trainer
        self.review_repo = review_repo
        self.reserved_policy = reserved_policy

    def execute(
        self,
        algorithm: str = "calibrated_logistic",
        test_size: float = 0.25,
        use_bootstrap_if_sparse: bool = True,
        auto_activate: bool = False,
        ground_truth_policy: str = "individual",
    ) -> Tuple[ModelVersion, Dict[str, Any]]:
        """
        Ejecuta el entrenamiento sobre el dataset disponible, calcula métricas frente al baseline
        y registra la nueva versión inmutable en el repositorio de modelos.
        """
        service = DatasetService(dataset_repo=self.dataset_repo)
        examples = service.get_all_examples(limit=5000)
        if ground_truth_policy not in ("individual", "consensus"):
            raise ValueError("Política de ground truth no reconocida.")
        if ground_truth_policy == "consensus":
            if self.review_repo is None:
                raise ValueError("El entrenamiento consensuado requiere acceso a las revisiones.")
            consensus_service = GroundTruthService(self.review_repo, self.dataset_repo)
            pairs = consensus_service.get_pairs()
            has_reviews = bool(self.review_repo.list_all(limit=1))
            examples = consensus_service.consensus_examples(pairs)
            if has_reviews and not examples:
                raise ValueError("No hay pares consensuados. Solicite al menos dos revisores distintos con decisiones coincidentes antes de entrenar.")

        if self.reserved_policy is not None:
            unreserved = self.reserved_policy.filter_examples(examples)
            if examples and not unreserved:
                raise ValueError("Todos los ejemplos disponibles pertenecen a grupos reservados. Añada revisiones de grupos académicos independientes.")
            examples = unreserved

        # Si el dataset de revisiones docentes acumuladas es inicial (< 20 ejemplos),
        # complementar con bootstrap sintético de calibración para garantizar convergencia matemática.
        if len(examples) < 20 and use_bootstrap_if_sparse:
            bootstrap_samples = service.generate_bootstrap_synthetic_dataset(n_samples=120)
            examples = list(examples) + bootstrap_samples

        model_version, metrics = self.trainer.train_and_evaluate(
            examples=examples,
            algorithm=algorithm,
            test_size=test_size,
            ground_truth_policy=ground_truth_policy,
        )

        # Si se solicita activación automática y el modelo supera o iguala al baseline
        is_superior = metrics.get("baseline_comparison", {}).get("superior_to_baseline", False)
        eligible = metrics.get("split", {}).get("eligible_for_auto_activation", False)
        if auto_activate and is_superior and eligible:
            # Crear versión marcada como activa
            active_version = ModelVersion(
                version_id=model_version.version_id,
                algorithm_name=model_version.algorithm_name,
                description=model_version.description,
                parameters=model_version.parameters,
                thresholds=model_version.thresholds,
                is_active=True,
                created_at=model_version.created_at,
                metrics=model_version.metrics,
                artifact_path=model_version.artifact_path,
            )
            self.model_version_repo.save(active_version)
            return active_version, metrics

        self.model_version_repo.save(model_version)
        return model_version, metrics
