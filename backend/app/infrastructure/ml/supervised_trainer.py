"""
Entrenador de Modelos Supervisados de Clasificación y Calibración Probabilística mediante Scikit-Learn.
Implementa el puerto ISupervisedModelTrainer (Fase 2.0).
"""

from datetime import datetime
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupKFold

from app.application.dataset_service import DatasetService, LABEL_TO_INT
from app.domain.scoring import (
    BASELINE_VERSION, DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS,
    adaptive_pair_score, classify_score, has_content_affinity,
)
from app.domain.model_version import ModelVersion
from app.domain.ports import ISupervisedModelTrainer
from app.domain.review import DatasetExample
from app.domain.academic_sources import academic_source_tokens
from app.settings import data_dir
from app.infrastructure.ml.academic_split import is_synthetic, split_examples


class SklearnSupervisedTrainer(ISupervisedModelTrainer):
    """
    Entrena, calibra probabilidades y evalúa modelos supervisados contra el baseline heurístico.
    Garantiza explicabilidad matemática, determinismo y serialización de artefactos para inferencia.
    """

    def __init__(self, models_dir: Optional[str] = None) -> None:
        self.models_dir = models_dir or str(data_dir() / "models")
        os.makedirs(self.models_dir, exist_ok=True)

    def train_and_evaluate(
        self,
        examples: List[DatasetExample],
        algorithm: str = "calibrated_logistic",
        test_size: float = 0.25,
        random_state: int = 42,
        ground_truth_policy: str = "individual",
    ) -> Tuple[ModelVersion, Dict[str, Any]]:
        """
        Entrena el modelo supervisado sobre el conjunto de ejemplos, calcula métricas de test,
        compara con el baseline heurístico y serializa el artefacto.
        """
        if len(examples) < 12:
            raise ValueError(f"Se requieren al menos 12 ejemplos para entrenamiento y evaluación (recibidos: {len(examples)}).")

        service = DatasetService(dataset_repo=None)  # Solo utilidades de matriz
        X, y, feature_names = service.extract_feature_matrix(examples)

        # Verificar que existan al menos 2 clases en el dataset
        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            raise ValueError("El dataset debe contener al menos 2 clases distintas para entrenar un clasificador supervisado.")

        train_indices, test_indices, groups, split_metadata = split_examples(examples, y, test_size, random_state)
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        calibration_method = "none"

        version_id = f"sup-{algorithm[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{uuid.uuid4().hex[:8]}"

        # Instanciar y ajustar modelo según algoritmo seleccionado
        feature_importances: Dict[str, float] = {}

        if algorithm == "random_forest":
            clf = RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                min_samples_split=3,
                random_state=random_state,
            )
            clf.fit(X_train, y_train)
            importances = clf.feature_importances_
            feature_importances = {name: round(float(imp), 4) for name, imp in zip(feature_names, importances)}
            algorithm_display = "RandomForestClassifier"
            description = "Clasificador supervisado Random Forest con evaluación de importancia de características."
        else:
            # Calibrated Logistic Regression con regularización L2
            base_lr = LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=random_state,
                solver="lbfgs",
            )
            # La calibración respeta los mismos grupos y valida solo con revisiones reales.
            cv = None
            if split_metadata["evaluation_scope"] == "synthetic":
                _, counts = np.unique(y_train, return_counts=True)
                if counts.min() >= 2:
                    cv = int(min(3, counts.min()))
                    calibration_method = "synthetic_stratified"
            else:
                real_positions = np.array([i for i, idx in enumerate(train_indices) if not is_synthetic(examples[idx])], dtype=int)
                synthetic_positions = np.array([i for i, idx in enumerate(train_indices) if is_synthetic(examples[idx])], dtype=int)
                real_groups = groups[train_indices[real_positions]]
                n_groups = len(np.unique(real_groups))
                if n_groups >= 2:
                    folds = []
                    for fit_rel, val_rel in GroupKFold(n_splits=min(3, n_groups)).split(real_positions, groups=real_groups):
                        fit = np.concatenate((real_positions[fit_rel], synthetic_positions))
                        val = real_positions[val_rel]
                        if set(y_train[fit]) != set(y_train) or set(y_train[val]) != set(y_train):
                            break
                        folds.append((fit, val))
                    else:
                        cv = folds
                        calibration_method = "academic_groups"
            clf = CalibratedClassifierCV(estimator=base_lr, method="sigmoid", cv=cv) if cv is not None else base_lr

            clf.fit(X_train, y_train)

            # Coeficientes si es base_lr
            if hasattr(clf, "coef_"):
                coefs = np.mean(np.abs(clf.coef_), axis=0)
                norm_coefs = coefs / (np.sum(coefs) + 1e-9)
                feature_importances = {name: round(float(c), 4) for name, c in zip(feature_names, norm_coefs)}
            algorithm_display = "CalibratedLogisticRegression" if cv is not None else "LogisticRegression"
            description = (
                "Regresión logística regularizada con calibración sigmoidea de probabilidades (Platt Scaling)."
                if cv is not None else "Regresión logística regularizada sin calibración adicional: grupos insuficientes."
            )

        # Predicciones en conjunto de prueba
        y_pred = clf.predict(X_test)

        # Métricas del modelo supervisado
        acc = float(accuracy_score(y_test, y_pred))
        f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2]).tolist()

        # Evaluación comparativa contra el Baseline Heurístico sobre el mismo X_test
        y_baseline_pred = self._compute_heuristic_baseline_predictions(X_test)
        base_acc = float(accuracy_score(y_test, y_baseline_pred))
        base_f1_macro = float(f1_score(y_test, y_baseline_pred, average="macro", zero_division=0))
        base_prec_macro = float(precision_score(y_test, y_baseline_pred, average="macro", zero_division=0))
        base_rec_macro = float(recall_score(y_test, y_baseline_pred, average="macro", zero_division=0))

        metrics: Dict[str, Any] = {
            "data_provenance_schema": 2,
            "ground_truth_policy": ground_truth_policy,
            "source_review_ids": sorted({review_id for ex in examples if not is_synthetic(ex)
                                         for review_id in (ex.source_review_ids or [ex.review_id])}),
            "data_source_tokens": sorted({token for ex in examples if not is_synthetic(ex)
                                          for token in academic_source_tokens(ex)}),
            "split": split_metadata,
            "calibration_method": calibration_method,
            "test_sample_count": len(y_test),
            "train_sample_count": len(y_train),
            "accuracy": round(acc, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
            "precision_macro": round(prec_macro, 4),
            "recall_macro": round(rec_macro, 4),
            "confusion_matrix": cm,
            "feature_importances": feature_importances,
            "baseline_comparison": {
                "baseline_version": BASELINE_VERSION,
                "evaluation_unit": "content_pair",
                "includes_global_assignment": False,
                "uncertain_label_mapping": "PARTIAL_MATCH",
                "baseline_accuracy": round(base_acc, 4),
                "baseline_f1_macro": round(base_f1_macro, 4),
                "baseline_precision_macro": round(base_prec_macro, 4),
                "baseline_recall_macro": round(base_rec_macro, 4),
                "f1_gain": round(f1_macro - base_f1_macro, 4),
                "accuracy_gain": round(acc - base_acc, 4),
                "superior_to_baseline": bool(f1_macro >= base_f1_macro and acc >= base_acc),
            },
        }

        # Serialización segura del modelo a disco
        artifact_filename = f"{version_id}.joblib"
        artifact_path = os.path.join(self.models_dir, artifact_filename)
        joblib.dump(
            {
                "model": clf,
                "algorithm": algorithm_display,
                "feature_names": feature_names,
                "metrics": metrics,
                "trained_at": datetime.now().isoformat(),
            },
            artifact_path,
        )

        model_version = ModelVersion(
            version_id=version_id,
            algorithm_name=algorithm_display,
            description=description,
            parameters={
                "algorithm": algorithm,
                "test_size": test_size,
                "random_state": random_state,
                "classes": [int(c) for c in unique_classes],
            },
            thresholds={"MATCH": 0.75, "PARTIAL_MATCH": 0.58, "UNCERTAIN": 0.45},
            is_active=False,
            created_at=datetime.now(),
            metrics=metrics,
            artifact_path=artifact_path,
        )

        return model_version, metrics

    @staticmethod
    def _compute_heuristic_baseline_predictions(X: np.ndarray) -> np.ndarray:
        """
        Evalúa el scoring adaptativo por pares sobre las mismas muestras del modelo.
        No evalúa selección de candidatos, asignación bipartita ni coberturas globales.
        """
        # Las características léxicas ya incorporan contención; no se vuelve a sumar x_3.
        # Se evalúa el scoring local, sin selección de candidatos ni asignación global.
        predictions = []
        for semantic, lexical, _asymmetric, structural, keyword in X:
            score, _ = adaptive_pair_score(
                float(semantic), float(lexical), float(keyword), float(structural), DEFAULT_WEIGHTS,
            )
            classification = classify_score(
                score, DEFAULT_THRESHOLDS,
                has_content_affinity(float(semantic), float(lexical), float(keyword)),
            )
            predictions.append(LABEL_TO_INT[classification.value])
        return np.array(predictions, dtype=np.int64)
