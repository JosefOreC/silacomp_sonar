"""Umbrales de la rúbrica del manual; no dependen de un servidor SonarQube."""

import json
from urllib.error import URLError

import pytest

from scripts import check_sonar_quality as quality
from scripts.check_sonar_quality import CONDITIONS, grade, quality_failures


def measures(**changes):
    return dict(security_rating="1", reliability_rating="1", sqale_rating="1", coverage="80",
                security_hotspots="0", duplicated_lines_density="3", bugs="0", vulnerabilities="0",
                code_smells="0", **changes)


def test_maximum_and_official_example():
    assert grade(measures())["nota_estimada"] == 20
    values = measures()
    values.update(reliability_rating="2", coverage="72", security_hotspots="10", security_hotspots_reviewed="60", duplicated_lines_density="2.4")
    assert grade(values)["nota_estimada"] == 17
    assert grade(values, exclusion_penalty=True)["nota_estimada"] == 7


@pytest.mark.parametrize("coverage,points", [(80, 4), (79.9, 3), (65, 3), (64.9, 2), (50, 2), (49.9, 1), (30, 1), (29.9, 0)])
def test_coverage_boundaries(coverage, points):
    values = measures()
    values["coverage"] = str(coverage)
    assert grade(values)["puntos"]["cobertura"] == points


def test_saturation_limit_and_missing_metrics():
    values = measures()
    values["code_smells"] = "2500"
    assert grade(values)["nota_estimada"] == 20
    values["code_smells"] = "2501"
    assert grade(values)["nota_estimada"] == 0
    values["security_hotspots"] = "1"
    with pytest.raises(KeyError):
        grade(values)


def effective_gate():
    return {"status": "OK", "ignoredConditions": False, "conditions": [
        {"metricKey": metric, "comparator": comparator, "errorThreshold": threshold, "status": "OK"}
        for metric, comparator, threshold in CONDITIONS
    ]}


def test_effective_gate_without_hotspots():
    values = measures()
    gate = effective_gate()
    gate["conditions"] = [c for c in gate["conditions"] if c["metricKey"] != "security_hotspots_reviewed"]
    assert quality_failures(values, gate, 0, grade(values)) == []


@pytest.mark.parametrize("metric", [c[0] for c in CONDITIONS if c[0] != "security_hotspots_reviewed"])
def test_gate_rejects_missing_global_conditions_even_when_ok(metric):
    values = measures()
    gate = effective_gate()
    gate["conditions"] = [c for c in gate["conditions"] if c["metricKey"] != metric]
    assert quality_failures(values, gate, 0, grade(values))


@pytest.mark.parametrize("changes", [
    {"errorThreshold": "79"}, {"errorThreshold": "nan"},
    {"comparator": "GT"}, {"status": "ERROR"}, {"status": "NO_VALUE"},
])
def test_gate_rejects_ineffective_coverage_condition(changes):
    values = measures()
    gate = effective_gate()
    next(c for c in gate["conditions"] if c["metricKey"] == "coverage").update(changes)
    assert quality_failures(values, gate, 0, grade(values))


def test_gate_rejects_relaxed_duplication_and_duplicate_conditions():
    values = measures()
    gate = effective_gate()
    next(c for c in gate["conditions"] if c["metricKey"] == "duplicated_lines_density")["errorThreshold"] = "5"
    assert quality_failures(values, gate, 0, grade(values))
    gate = effective_gate()
    gate["conditions"].append(gate["conditions"][0].copy())
    assert quality_failures(values, gate, 0, grade(values))


def test_stricter_gate_is_accepted_and_hotspots_require_an_effective_condition():
    values = measures()
    values.update(security_hotspots="5", security_hotspots_reviewed="100", coverage="90")
    gate = effective_gate()
    next(c for c in gate["conditions"] if c["metricKey"] == "coverage")["errorThreshold"] = "85"
    assert quality_failures(values, gate, 0, grade(values)) == []
    gate["conditions"] = [c for c in gate["conditions"] if c["metricKey"] != "security_hotspots_reviewed"]
    assert quality_failures(values, gate, 0, grade(values))


def test_maximum_rubric_does_not_hide_open_issues_or_ignored_conditions():
    values = measures()
    values["code_smells"] = "1"
    assert grade(values)["nota_estimada"] == 20
    assert quality_failures(values, effective_gate(), 0, grade(values))
    values["code_smells"] = "0"
    assert quality_failures(values, effective_gate(), 1, grade(values))
    gate = effective_gate()
    gate["ignoredConditions"] = True
    assert quality_failures(values, gate, 0, grade(values))
    gate = effective_gate()
    gate["status"] = "ERROR"
    assert quality_failures(values, gate, 0, grade(values))


@pytest.mark.parametrize("metric,value", [
    ("coverage", "nan"), ("coverage", "101"), ("duplicated_lines_density", "-1"),
    ("bugs", "-1"), ("security_hotspots", "-1"), ("security_rating", "nan"),
])
def test_invalid_measurements_cannot_produce_a_grade(metric, value):
    values = measures()
    values[metric] = value
    with pytest.raises(ValueError):
        grade(values)


def test_failed_server_query_replaces_stale_success_report(tmp_path, monkeypatch):
    monkeypatch.setattr(quality, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["check_sonar_quality.py"])
    quality.write_report({"cumple": True})

    def unavailable(request, timeout):
        raise URLError("Servidor detenido")

    monkeypatch.setattr(quality, "urlopen", unavailable)
    assert quality.main() == 2
    report = json.loads((tmp_path / ".reports/sonarqube-compliance.json").read_text(encoding="utf-8"))
    assert report["cumple"] is False
    assert "Servidor detenido" in report["error"]
