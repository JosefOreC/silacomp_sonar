"""Verifica la rúbrica del manual contra la API real de SonarQube.

No sustituye la calificación oficial del pipeline Quantum. Solo usa stdlib.
"""

import argparse
import base64
import json
import math
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
GATE = "ConvComp - Manual UC 20 puntos"
CONDITIONS = (
    ("security_rating", "GT", "1"), ("reliability_rating", "GT", "1"),
    ("sqale_rating", "GT", "1"), ("coverage", "LT", "80"),
    ("security_hotspots_reviewed", "LT", "80"),
    ("duplicated_lines_density", "GT", "3"),
    ("bugs", "GT", "0"), ("vulnerabilities", "GT", "0"), ("code_smells", "GT", "0"),
)
METRICS = (
    "security_rating,reliability_rating,sqale_rating,coverage,line_coverage,branch_coverage,"
    "security_hotspots,security_hotspots_reviewed,duplicated_lines_density,bugs,vulnerabilities,"
    "code_smells,ncloc,alert_status"
)


def grade(measures: dict[str, str], exclusion_penalty: bool = False) -> dict:
    """Aplica umbrales inclusivos y penalizaciones de las páginas 18–21."""
    ratings = [float(measures[k]) for k in ("security_rating", "reliability_rating", "sqale_rating")]
    if any(r < 1 or r > 5 or not r.is_integer() for r in ratings):
        raise ValueError("Las calificaciones deben estar entre A (1) y E (5)")
    coverage = float(measures["coverage"])
    hotspots = int(measures["security_hotspots"])
    counts = [int(measures[k]) for k in ("bugs", "vulnerabilities", "code_smells", "security_hotspots")]
    if any(count < 0 for count in counts):
        raise ValueError("Los recuentos de hallazgos no pueden ser negativos")
    reviewed = float(measures["security_hotspots_reviewed"]) if hotspots else 100
    duplication = float(measures["duplicated_lines_density"])
    if any(not math.isfinite(v) or not 0 <= v <= 100 for v in (coverage, reviewed, duplication)):
        raise ValueError("Los porcentajes deben ser finitos y estar entre 0 y 100")
    points = {
        "seguridad": (5 - ratings[0]) * 1.25,
        "fiabilidad": 5 - ratings[1],
        "cobertura": next((p for threshold, p in ((80, 4), (65, 3), (50, 2), (30, 1)) if coverage >= threshold), 0),
        "mantenibilidad": 5 - ratings[2],
        "hotspots": next((p for threshold, p in ((80, 2), (70, 1.5), (50, 1), (30, .5)) if reviewed >= threshold), 0),
        "duplicacion": next((p for threshold, p in ((3, 1), (5, .75), (10, .5), (20, .25)) if duplication <= threshold), 0),
    }
    findings = sum(counts)
    total = 0 if findings > 2500 else max(0, sum(points.values()) - (10 if exclusion_penalty else 0))
    return {"puntos": points, "nota_estimada": total, "maximo": 20,
            "hallazgos": findings, "penalizacion_exclusiones": exclusion_penalty,
            "advertencia": "Estimación local; la nota oficial corresponde al pipeline Quantum."}


def quality_failures(measures: dict[str, str], status: dict, open_issues: int,
                     rubric: dict) -> list[str]:
    """Exige la rúbrica y un gate global efectivo, incluso con un estado OK."""
    failures = []
    if rubric["nota_estimada"] != 20:
        failures.append("La rúbrica no alcanza 20/20.")
    if status["status"] != "OK":
        failures.append("El Quality Gate no está aprobado.")
    if status.get("ignoredConditions"):
        failures.append("El Quality Gate contiene condiciones ignoradas.")
    if open_issues != 0 or any(int(measures[k]) != 0 for k in ("bugs", "vulnerabilities", "code_smells")):
        failures.append("Existen incidencias abiertas o recuentos de incidencias distintos de cero.")
    conditions = status["conditions"]
    for metric, comparator, threshold in CONDITIONS:
        # SonarQube no devuelve esta medida cuando no existen hotspots.
        if metric == "security_hotspots_reviewed" and int(measures["security_hotspots"]) == 0:
            continue
        matches = [c for c in conditions if c["metricKey"] == metric]
        if len(matches) != 1:
            failures.append(f"Falta una condición global única: {metric}.")
            continue
        condition = matches[0]
        actual_threshold = float(condition["errorThreshold"])
        required_threshold = float(threshold)
        relaxed = actual_threshold > required_threshold if comparator == "GT" else actual_threshold < required_threshold
        if condition["comparator"] != comparator or not math.isfinite(actual_threshold) or relaxed:
            failures.append(f"Umbral global insuficiente: {metric}.")
    if any(c["status"] != "OK" for c in conditions):
        failures.append("Hay condiciones del gate sin aprobar.")
    return failures


def write_report(report: dict) -> None:
    """Sustituye la evidencia anterior también cuando la comprobación falla."""
    output = ROOT / ".reports" / "sonarqube-compliance.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def settings() -> dict[str, str]:
    """Lee secretos locales sin imprimirlos ni incorporarlos a las evidencias."""
    values = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    values.update(os.environ)
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--project", default="convcomp")
    parser.add_argument("--configure-gate", action="store_true", help="Crea/actualiza y asigna el gate local; requiere administrador")
    args = parser.parse_args()
    try:
        return check_server(args)
    except (URLError, OSError, ValueError, KeyError, TypeError) as error:
        # Un error de consulta nunca conserva un informe anterior con cumple=true.
        report = {"cumple": False, "error": str(error), "project": args.project, "url": args.url}
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2


def check_server(args: argparse.Namespace) -> int:
    """Consulta el servidor y genera evidencia del proyecto solicitado."""
    values = settings()
    credentials = "admin:" + values["SONAR_ADMIN_PASSWORD"] if args.configure_gate else values.get("SONAR_TOKEN", "") + ":"
    auth = "Basic " + base64.b64encode(credentials.encode()).decode()

    def api(path: str, data: dict | None = None) -> dict:
        request = Request(args.url.rstrip("/") + "/api/" + path,
                          data=urlencode(data).encode() if data is not None else None,
                          headers={"Authorization": auth})
        with urlopen(request, timeout=60) as response:
            content = response.read()
            return json.loads(content) if content else {}

    if args.configure_gate:
        existing = api("qualitygates/list")["qualitygates"]
        if not any(g["name"] == GATE for g in existing):
            api("qualitygates/create", {"name": GATE})
        current = {c["metric"]: c for c in api("qualitygates/show?" + urlencode({"name": GATE}))["conditions"]}
        for metric, op, error in CONDITIONS:
            data = {"metric": metric, "op": op, "error": error}
            if metric in current:
                api("qualitygates/update_condition", {**data, "id": current[metric]["id"]})
            else:
                api("qualitygates/create_condition", {**data, "gateName": GATE})
        api("qualitygates/select", {"gateName": GATE, "projectKey": args.project})
        print("Quality Gate configurado; ejecutar un nuevo análisis para evaluar condiciones.")
        return 0

    project_query = urlencode({"projectKey": args.project})
    measures = api("measures/component?" + urlencode({"component": args.project, "metricKeys": METRICS}))
    metric_values = {m["metric"]: m["value"] for m in measures["component"]["measures"]}
    gate = api("qualitygates/project_status?" + project_query)
    issues = api("issues/search?" + urlencode({"componentKeys": args.project, "resolved": "false", "ps": 500}))
    try:
        analyses = api("project_analyses/search?" + urlencode({"project": args.project, "ps": 1}))
    except HTTPError as error:
        if error.code != 403:
            raise
        analyses = {"analyses": [], "nota": "El token no permite consultar historial; métricas y gate sí verificados."}
    properties = (ROOT / "sonar-project.properties").read_text(encoding="utf-8")
    exclusions = [line.split("=", 1)[1] for line in properties.splitlines() if line.startswith("sonar.exclusions=")]
    patterns = [p.strip() for value in exclusions for p in value.split(",") if p.strip()]
    penalty = len(patterns) > 5 or any("*" in pattern or "?" in pattern for pattern in patterns)
    rubric = grade(metric_values, penalty)
    status = gate["projectStatus"]
    failures = quality_failures(metric_values, status, int(issues["total"]), rubric)
    compliant = not failures
    report = {"gate": gate, "measures": measures, "issues": issues, "analyses": analyses,
              "rubric": rubric, "cumple": compliant, "incumplimientos": failures}
    write_report(report)
    print(json.dumps({"rubrica": rubric, "metricas": metric_values, "cumple": compliant,
                      "incumplimientos": failures}, ensure_ascii=False, indent=2))
    return 0 if compliant else 1


if __name__ == "__main__":
    raise SystemExit(main())
