"""Los campos anulables de respuesta siguen siendo obligatorios en Pydantic v2."""

import pytest
from pydantic import ValidationError

from app.api.schemas import ReviewerAgreementResponse, ReviewResponse


def test_nullable_metrics_require_explicit_presence():
    data = dict(reviewer_a="A", reviewer_b="B", common_pairs=0, agreements=0)
    with pytest.raises(ValidationError):
        ReviewerAgreementResponse(**data)
    response = ReviewerAgreementResponse(
        **data, observed_agreement=None, expected_agreement=None, cohen_kappa=None
    )
    assert response.model_dump()["cohen_kappa"] is None
    assert set(response.model_json_schema()["required"]) >= {
        "observed_agreement", "expected_agreement", "cohen_kappa"
    }


def test_review_original_prediction_cannot_be_silently_omitted():
    required = ReviewResponse.model_json_schema()["required"]
    assert "match_id" in required
    assert "prediction_before" in required
