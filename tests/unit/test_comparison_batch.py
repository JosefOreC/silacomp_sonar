"""Invariantes, ranking, idempotencia y conservación de resultados parciales."""

from dataclasses import replace
from datetime import datetime, timezone, timedelta
import sqlite3
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.application.comparison_batch_service import CompareSyllabusBatch, ComparisonBatchQuery
from app.domain.comparison import Comparison
from app.domain.comparison_batch import (
    BatchResult, BatchSyllabus, BatchValidationError, ComparisonBatch, ComparisonBatchView,
    BatchNotFoundError, validate_batch_ids,
)
from app.domain.scoring import DEFAULT_THRESHOLDS, DEFAULT_WEIGHTS, BASELINE_VERSION
from app.infrastructure.persistence.database import DatabaseManager
from app.infrastructure.persistence.sqlite_comparison_batch_repository import SqliteComparisonBatchRepository
from app.api.deps import get_syllabus_repository
from tests.integration.test_ground_truth_endpoints import seed_comparison


def batch():
    return ComparisonBatch('CB-test', BatchSyllabus('O', 'Objetivo', None),
                           tuple(BatchSyllabus(value, value, None) for value in ('A', 'B', 'C')),
                           BASELINE_VERSION, dict(DEFAULT_WEIGHTS), dict(DEFAULT_THRESHOLDS), datetime.now(timezone.utc))


@pytest.mark.parametrize('objective,candidates', [('', ('A',)), ('O', ()), ('O', ('O',)),
    ('O', ('A', 'A')), ('O', ('A', 'B', 'C', 'D', 'E', 'F')), ('O', (' ',))])
def test_batch_rejects_invalid_selection(objective, candidates):
    with pytest.raises(BatchValidationError):
        validate_batch_ids(objective, candidates)


def test_ranking_prioritizes_coverage_then_score_then_stable_id():
    results = (BatchResult('C', 'C3', .99, 70, 95), BatchResult('B', 'C2', .8, 90, 60), BatchResult('A', 'C1', .8, 90, 50))
    view = ComparisonBatchView(batch(), results, datetime.now(timezone.utc))
    assert view.status == 'COMPLETED'
    assert view.ranking == ['A', 'B', 'C']
    assert replace(view, results=tuple(reversed(results))).ranking == view.ranking
    assert replace(view, completed_at=None).status == 'RUNNING'
    failed = BatchResult('B', error_code='NO_CONTENT', error='Sin contenidos')
    partial = replace(view, results=(results[0], failed))
    assert partial.status == 'PARTIAL'
    assert partial.ranking == ['C']
    assert replace(view, results=(failed,)).status == 'FAILED'


@pytest.mark.parametrize('changes', [
    {'global_score': float('nan')}, {'objective_coverage': 101}, {'compared_coverage': -1},
    {'global_score': None}, {'error': 'Error'}, {'error_code': 'FAIL'},
])
def test_success_requires_finite_individual_metrics(changes):
    values = dict(compared_syllabus_id='A', comparison_id='C1', global_score=.8, objective_coverage=80, compared_coverage=70)
    values.update(changes)
    with pytest.raises(BatchValidationError):
        BatchResult(**values)


@pytest.mark.parametrize('changes', [{}, {'error': 'Error'}, {'error': 'Error', 'error_code': 'FAIL', 'global_score': .5}])
def test_failures_cannot_invent_a_score(changes):
    with pytest.raises(BatchValidationError):
        BatchResult('A', **changes)


def test_repository_is_append_only_and_recoverable(tmp_path):
    repo = SqliteComparisonBatchRepository(DatabaseManager(str(tmp_path / 'batch.db')))
    original = batch()
    assert repo.create(original)
    assert not repo.create(replace(original, model_version='otro'))
    assert repo.get(original.id) == original
    assert repo.get('missing') is None
    result = BatchResult('A', 'C1', .8, 80, 70)
    repo.add_result(original.id, result)
    with pytest.raises(sqlite3.IntegrityError):
        repo.add_result(original.id, replace(result, objective_coverage=1))
    query = ComparisonBatchQuery(repo)
    assert query.get(original.id).status == 'RUNNING'
    assert query.get(original.id).results == (result,)
    finished = datetime.now(timezone.utc)
    repo.complete(original.id, finished)
    repo.complete(original.id, finished + timedelta(days=1))
    assert repo.get_completion(original.id) == finished
    assert query.list_recent()[0].results == (result,)
    with pytest.raises(BatchNotFoundError):
        query.get('missing')


def test_interrupted_execution_preserves_results_and_replay_does_not_rerun(tmp_path):
    seed_comparison(1, size=1)
    seed_comparison(2, size=1)
    repo = SqliteComparisonBatchRepository(DatabaseManager(str(tmp_path / 'batch.db')))
    runner = Mock()
    runner.execute.side_effect = [
        Comparison('NEW', 'OBJ-SYL-1', 'CMP-SYL-1', .8, 80, 70, BASELINE_VERSION, datetime.now()),
        KeyboardInterrupt(),
    ]
    factory = Mock(return_value=(runner, BASELINE_VERSION))
    service = CompareSyllabusBatch(get_syllabus_repository(), repo, factory)
    request_id = uuid4()
    with pytest.raises(KeyboardInterrupt):
        service.execute(request_id, 'OBJ-SYL-1', ('CMP-SYL-1', 'CMP-SYL-2'))
    view, created = service.execute(request_id, 'OBJ-SYL-1', ('CMP-SYL-1', 'CMP-SYL-2'))
    assert not created and view.status == 'RUNNING'
    assert view.results[0].comparison_id == 'NEW'
    assert len(view.results) == 1
    assert runner.execute.call_count == 2
    factory.assert_called_once()


def test_budget_is_checked_before_loading_the_model_or_persisting(tmp_path):
    seed_comparison(1, size=1)
    syllabi = get_syllabus_repository()
    original = syllabi.get_content_items
    syllabi.get_content_items = lambda identifier: original(identifier) * (201 if identifier.startswith('OBJ') else 100)
    repository = Mock()
    repository.get.return_value = None
    factory = Mock()
    service = CompareSyllabusBatch(syllabi, repository, factory)
    with pytest.raises(BatchValidationError, match='presupuesto'):
        service.execute(uuid4(), 'OBJ-SYL-1', ('CMP-SYL-1',))
    factory.assert_not_called()
    repository.create.assert_not_called()
