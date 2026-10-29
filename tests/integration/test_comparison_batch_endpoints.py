"""Lotes reales con NLP controlado; no modifican el almacenamiento de desarrollo."""

from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_vector_service, get_comparison_repository, get_model_repository
from app.application.compare_syllabi import CompareSyllabiUseCase
from app.domain.scoring import BASELINE_VERSION
from app.main import app
from tests.integration.test_ground_truth_endpoints import seed_comparison
from tests.integration.test_scientific_evaluation_endpoints import ControlledVectors, register_candidate


@pytest.fixture
def client():
    app.dependency_overrides[get_vector_service] = lambda: ControlledVectors()
    yield TestClient(app)
    app.dependency_overrides.pop(get_vector_service, None)


def payload():
    return {'request_id': str(uuid4()), 'objective_syllabus_id': 'OBJ-SYL-1',
            'compared_syllabus_ids': ['CMP-SYL-1', 'CMP-SYL-2']}


def test_batch_executes_independent_comparisons_and_reuses_the_same_request(client):
    old = seed_comparison(1, size=2)
    seed_comparison(2, size=2)
    request = payload()
    response = client.post('/api/comparison-batches', json=request)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['status'] == 'COMPLETED' and data['model_version'] == BASELINE_VERSION
    assert 'global_score' not in data and 'objective_coverage' not in data
    assert len(data['ranking']) == len(data['results']) == 2
    for result in data['results']:
        detail = client.get('/api/comparisons/' + result['comparison_id']).json()
        assert detail['objective_syllabus_id'] == 'OBJ-SYL-1'
        assert detail['compared_syllabus_id'] == result['compared_syllabus_id']
        assert detail['objective_coverage'] == result['objective_coverage']
        assert detail['compared_coverage'] == result['compared_coverage']
        assert detail['counts'] == result['counts']
        assert result['error'] is None
    assert len(get_comparison_repository().list_all()) == 4
    assert client.post('/api/comparison-batches', json=request).json() == data
    assert client.post('/api/comparison-batches', json=request).status_code == 200
    assert len(get_comparison_repository().list_all()) == 4
    assert client.get('/api/comparison-batches/' + data['id']).json() == data
    assert client.get('/api/comparison-batches').json() == [data]
    export = client.get('/api/comparison-batches/' + data['id'] + '/export')
    assert export.json() == data and 'attachment' in export.headers['content-disposition']
    assert get_comparison_repository().get_by_id(old.id).global_score == old.global_score
    changed = {**request, 'compared_syllabus_ids': list(reversed(request['compared_syllabus_ids']))}
    assert client.post('/api/comparison-batches', json=changed).status_code == 409


def test_empty_candidate_does_not_invalidate_other_results(client):
    seed_comparison(1, size=1)
    seed_comparison(2, size=0)
    data = client.post('/api/comparison-batches', json=payload()).json()
    assert data['status'] == 'PARTIAL'
    assert data['ranking'] == ['CMP-SYL-1']
    failure = next(result for result in data['results'] if result['error'])
    assert failure['comparison_id'] is None and failure['global_score'] is None
    assert failure['error_code'] == 'NO_CONTENT'
    request = payload()
    request['compared_syllabus_ids'] = ['CMP-SYL-2']
    assert client.post('/api/comparison-batches', json=request).json()['status'] == 'FAILED'


@pytest.mark.parametrize('changes,status', [
    ({'compared_syllabus_ids': []}, 422), ({'compared_syllabus_ids': ['CMP-SYL-1'] * 2}, 422),
    ({'compared_syllabus_ids': ['OBJ-SYL-1']}, 422), ({'compared_syllabus_ids': ['X'] * 6}, 422),
    ({'compared_syllabus_ids': ['X' * 101]}, 422), ({'request_id': 'invalido'}, 422),
    ({'objective_syllabus_id': 'missing'}, 404), ({'compared_syllabus_ids': ['missing']}, 404),
    ({'weights': {'semantic': 1}}, 422),
])
def test_invalid_requests_do_not_create_a_batch(client, changes, status):
    seed_comparison(1, size=1)
    seed_comparison(2, size=1)
    response = client.post('/api/comparison-batches', json={**payload(), **changes})
    assert response.status_code == status, response.text
    assert client.get('/api/comparison-batches').json() == []


def test_missing_sources_and_invalid_history_queries(client):
    assert client.get('/api/comparison-batches/missing').status_code == 404
    assert client.get('/api/comparison-batches/missing/export').status_code == 404
    assert client.get('/api/comparison-batches?limit=0').status_code == 422
    seed_comparison(1, size=0)
    request = {**payload(), 'compared_syllabus_ids': ['CMP-SYL-1']}
    assert client.post('/api/comparison-batches', json=request).status_code == 422


def test_unexpected_pair_failure_is_recorded_without_leaking_details(client, monkeypatch):
    seed_comparison(1, size=1)
    seed_comparison(2, size=1)
    execute = CompareSyllabiUseCase.execute

    def fail_second(self, **kwargs):
        if kwargs['compared_syllabus_id'] == 'CMP-SYL-2':
            raise RuntimeError('internal-private-path')
        return execute(self, **kwargs)

    monkeypatch.setattr(CompareSyllabiUseCase, 'execute', fail_second)
    response = client.post('/api/comparison-batches', json=payload())
    assert response.status_code == 201
    assert response.json()['status'] == 'PARTIAL'
    assert 'internal-private-path' not in response.text


def test_unavailable_active_model_is_not_silently_replaced(client, monkeypatch):
    seed_comparison(1, size=1)
    seed_comparison(2, size=1)
    repository = get_model_repository()
    monkeypatch.setattr(repository, 'get_active_model', lambda: object())
    monkeypatch.setattr('app.api.comparison_batch_router.get_model_repository', lambda: repository)
    monkeypatch.setattr('app.api.comparison_batch_router.ModelInferenceService.load_model', lambda self, model: False)
    assert client.post('/api/comparison-batches', json=payload()).status_code == 409
    assert client.get('/api/comparison-batches').json() == []


def test_model_is_pinned_even_when_another_version_is_activated_during_the_batch(client, monkeypatch):
    seed_comparison(1, size=2)
    seed_comparison(2, size=2)
    register_candidate('fixed-model')
    register_candidate('next-model')
    repository = get_model_repository()
    repository.set_active_model('fixed-model')
    execute = CompareSyllabiUseCase.execute

    def activate_next(self, **kwargs):
        result = execute(self, **kwargs)
        repository.set_active_model('next-model')
        return result

    monkeypatch.setattr(CompareSyllabiUseCase, 'execute', activate_next)
    data = client.post('/api/comparison-batches', json=payload()).json()
    assert data['status'] == 'COMPLETED'
    assert data['model_version'] == 'fixed-model'
    assert repository.get_active_model().version_id == 'next-model'
    assert all(get_comparison_repository().get_by_id(result['comparison_id']).model_version == 'fixed-model'
               for result in data['results'])


def test_reading_history_does_not_initialize_nlp(client, monkeypatch):
    monkeypatch.setattr('app.api.comparison_batch_router.ModelInferenceService', lambda: pytest.fail('No debe cargar modelos'))
    assert client.get('/api/comparison-batches').json() == []
    assert client.get('/api/comparison-batches/missing').status_code == 404
