"""Correspondencias y cobertura de una matriz humana exhaustiva."""

from typing import Any, Dict

from app.domain.comparison import Comparison, MatchClassification

POSITIVE = {MatchClassification.MATCH.value, MatchClassification.PARTIAL_MATCH.value}


def correspondence_metrics(case: Dict[str, Any], prediction: Comparison) -> Dict[str, Any]:
    gold = {(label["objective_item_id"], label["compared_item_id"]) for label in case["labels"] if label["label"] in POSITIVE}
    selected = {(match.objective_item_id, match.compared_item_id) for match in prediction.matches if match.classification.value in POSITIVE}
    true_positive = len(gold & selected)
    false_positive = len(selected - gold)
    false_negative = len(gold - selected)
    precision = true_positive / len(selected) if selected else (1.0 if not gold else 0.0)
    recall = true_positive / len(gold) if gold else 1.0
    f1 = 2 * true_positive / (len(selected) + len(gold)) if selected or gold else 1.0

    def expected_coverage(items, index):
        curricular = [item for item in items if item["unit_number"] and item["unit_number"] > 0]
        effective = curricular or items
        covered = {pair[index] for pair in gold}
        return round(100 * sum(item["id"] in covered for item in effective) / len(effective), 1)

    expected_obj = expected_coverage(case["objective_items"], 0)
    expected_cmp = expected_coverage(case["compared_items"], 1)
    return {
        "comparison_id": case["comparison_id"], "true_positive": true_positive,
        "false_positive": false_positive, "false_negative": false_negative,
        "precision": precision, "recall": recall, "f1": f1,
        "expected_objective_coverage": expected_obj, "expected_compared_coverage": expected_cmp,
        "predicted_objective_coverage": prediction.objective_coverage,
        "predicted_compared_coverage": prediction.compared_coverage,
        "objective_coverage_error": abs(prediction.objective_coverage - expected_obj),
        "compared_coverage_error": abs(prediction.compared_coverage - expected_cmp),
        "global_score": prediction.global_score,
        "predicted_pairs": [{"objective_item_id": m.objective_item_id, "compared_item_id": m.compared_item_id,
                             "classification": m.classification.value, "score": m.score,
                             "objective_page": m.objective_page, "compared_page": m.compared_page} for m in prediction.matches],
    }


def aggregate_comparisons(rows: list[Dict[str, Any]]) -> Dict[str, float]:
    tp = sum(row["true_positive"] for row in rows)
    fp = sum(row["false_positive"] for row in rows)
    fn = sum(row["false_negative"] for row in rows)
    return {
        "precision": tp / (tp + fp) if tp + fp else (1.0 if not fn else 0.0),
        "recall": tp / (tp + fn) if tp + fn else 1.0,
        "f1": 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 1.0,
        "macro_f1": sum(row["f1"] for row in rows) / len(rows),
        "objective_coverage_mae": sum(row["objective_coverage_error"] for row in rows) / len(rows),
        "compared_coverage_mae": sum(row["compared_coverage_error"] for row in rows) / len(rows),
    }
