"""
Entrenador de Modelos Supervisados de Clasificación y Calibración Probabilística mediante Scikit-Learn.
Implementa el puerto ISupervisedModelTrainer (Fase 2.0).
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from app.application.dataset_service import DatasetService, FEATURE_NAMES, LABEL_TO_INT
from app.domain.comparison import MatchClassification
from app.domain.model_version import ModelVersion
from app.domain.ports import ISupervisedModelTrainer
from app.domain.review import DatasetExample


MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data",
    "models",
)


class SklearnSupervisedTrainer(ISupervisedModelTrainer):
    """
    Entrena, calibra probabilidades y evalúa modelos supervisados contra el baseline heurístico.
    Garantiza explicabilidad matemática, determinismo y serialización de artefactos para inferencia.
    """

    def __init__(self, models_dir: Optional[str] = None) -> None:
        self.models_dir = models_dir or MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)

    def train_and_evaluate(
        self,
        examples: List[DatasetExample],
        algorithm: str = "calibrated_logistic",
        test_size: float = 0.25,
        random_state: int = 42,
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

        # División balanceada estratificada
        stratify_opt = y if min(np.bincount(y)) >= 2 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_opt,
        )

        version_id = f"sup-{algorithm[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

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
            # Calibración de probabilidades con validación cruzada
            cv_folds = min(3, min(np.bincount(y_train)))
            if cv_folds >= 2:
                clf = CalibratedClassifierCV(estimator=base_lr, method="sigmoid", cv=cv_folds)
            else:
                clf = base_lr

            clf.fit(X_train, y_train)

            # Coeficientes si es base_lr
            if hasattr(clf, "coef_"):
                coefs = np.mean(np.abs(clf.coef_), axis=0)
                norm_coefs = coefs / (np.sum(coefs) + 1e-9)
                feature_importances = {name: round(float(c), 4) for name, c in zip(feature_names, norm_coefs)}
            algorithm_display = "CalibratedLogisticRegression"
            description = "Regresión logística regularizada con calibración sigmoidea de probabilidades (Platt Scaling)."

        # Predicciones en conjunto de prueba
        y_pred = clf.predict(X_test)

        # Métricas del modelo supervisado
        acc = float(accuracy_score(y_test, y_pred))
        f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
        prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        # Evaluación comparativa contra el Baseline Heurístico sobre el mismo X_test
        y_baseline_pred = self._compute_heuristic_baseline_predictions(X_test)
        base_acc = float(accuracy_score(y_test, y_baseline_pred))
        base_f1_macro = float(f1_score(y_test, y_baseline_pred, average="macro", zero_division=0))
        base_prec_macro = float(precision_score(y_test, y_baseline_pred, average="macro", zero_division=0))
        base_rec_macro = float(recall_score(y_test, y_baseline_pred, average="macro", zero_division=0))

        metrics: Dict[str, Any] = {
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
        Calcula las predicciones categóricas que asignaría la regla heurística compuesta
        sobre el conjunto de prueba para permitir benchmarking formal directo.
        """
        # X[:, 0]=sem, X[:, 1]=lex, X[:, 2]=asym, X[:, 3]=struct, X[:, 4]=keyword
        composite_scores = (
            0.40 * X[:, 0]
            + 0.30 * X[:, 1]
            + 0.15 * X[:, 2]
            + 0.15 * X[:, 3]
        )
        preds = np.zeros(len(X), dtype=np.int64)
        for i, score in enumerate(composite_scores):
            if score >= 0.75 or (X[i, 1] >= 0.85 and X[i, 0] >= 0.65):
                preds[i] = 2  # MATCH
            elif score >= 0.58 or X[i, 2] >= 0.60:
                preds[i] = 1  # PARTIAL_MATCH
            else:
                preds[i] = 0  # NO_MATCH
        return preds
