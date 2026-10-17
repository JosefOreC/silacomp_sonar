# Resultado de despliegue y análisis SonarQube

Validación realizada el **2026-10-15**, zona America/Lima. Análisis iniciado
a las 20:21:05 y escáner finalizado a las 20:23:28.

## Servicios disponibles

- Aplicación: <http://localhost:5173>.
- Salud de API: <http://localhost:5173/api/health>, versión 3.2.1, fase 3.
- Proyecto SonarQube: <http://localhost:9000/dashboard?id=convcomp>.
- Acceso SonarQube: usuario `admin`; contraseña en `SONAR_ADMIN_PASSWORD`
  dentro de `.env`. El token de proyecto está en `SONAR_TOKEN`.

API, frontend, SonarQube y PostgreSQL quedaron saludables. Las imágenes de
aplicación se construyeron correctamente y `pip check` en la API no encontró
dependencias incompatibles. La primera validación utilizó `APP_PORT=18080`
tras el rechazo de Windows al puerto 8080. Posteriormente se cambió a
`APP_PORT=5173` para coincidir con la dirección usada por el usuario. La interfaz
y sus consultas a la API se verificaron en Chromium sin errores JavaScript.

Se comprobó la carga y descarga de un PDF sintético, su presencia en SQLite,
la respuesta de la web y la navegación SPA. Tras recrear ambos contenedores,
el PDF siguió listado y su SHA-256 coincidió. El archivo
`validacion_docker_sintetica.pdf` permanece en el volumen de esta instancia.

## Pruebas y cobertura

La suite dentro de Docker terminó con **99 pruebas aprobadas**, sin fallos
ni pruebas omitidas, en **45,63 segundos**. Se conservaron dos advertencias
de deprecación de dependencias. La imagen de pruebas descarga previamente
el modelo real `paraphrase-multilingual-MiniLM-L12-v2` y lo utiliza offline.

| Medición del backend con coverage.py | Resultado |
|---|---:|
| Líneas cubiertas | 3467 / 3851 — 90,03 % |
| Ramas cubiertas | 673 / 926 — 72,68 % |
| Cobertura combinada | 86,67 % |

## Análisis estático

SonarQube Community **26.10.0.133078**, SonarScanner CLI **8.1.0.6389**,
Java 21. El escáner finalizó con código 0 y `EXECUTION SUCCESS`.
Identificador de análisis: `bed09672-824a-4027-b8a1-30627d761684`.

Se indexaron 120 archivos. Fuentes: `backend/app` y `frontend/src`;
pruebas: `tests` y `frontend/e2e`. Se importaron cobertura Python y resultados
JUnit. No se generó cobertura de frontend ni se ejecutó Playwright en esta
sesión. El escáner omitió el análisis de dependencias SCA.

| Métrica de SonarQube para el proyecto | Resultado |
|---|---:|
| Quality Gate | OK / PASSED |
| Incidencias clasificadas como BUG | 4 |
| Problemas de mantenibilidad (CODE_SMELL) | 43 |
| Vulnerabilidades detectadas en este alcance | 0 |
| Security hotspots | 0 |
| Cobertura global | 75,0 % |
| Cobertura global de líneas | 75,5 % |
| Duplicación | 1,1 % |
| Líneas de código | 12 761 |
| Fiabilidad / seguridad / mantenibilidad | C / A / A |

El Quality Gate de este primer análisis devolvió `conditions: []`: ninguna
condición fue evaluada. El estado aprobado no significa que los hallazgos
estén resueltos. La cobertura global incluye el frontend, que no tiene un
reporte de cobertura configurado.

## Hallazgos para revisar

Las cuatro incidencias clasificadas como BUG son:

| Archivo y línea | Regla | Revisión propuesta |
|---|---|---|
| `backend/app/api/syllabus_router.py:61` | `python:S7493` | Evitar escritura síncrona de archivos dentro del endpoint asíncrono de carga. |
| `frontend/src/components/PdfDocumentViewer.tsx:165` | `typescript:S9383` | Hacer explícito cómo se gestiona la promesa de `renderPage()` en el efecto. |
| `frontend/src/components/ScientificEvaluationPanel.tsx:84` | `typescript:S9011` | Declarar `type="submit"` para expresar la intención del botón del formulario. |
| `frontend/src/components/ScientificEvaluationPanel.tsx:104` | `typescript:S9011` | Declarar `type="submit"` para expresar la intención del botón del formulario. |

En severidad heredada, las 47 incidencias se distribuyen en 26 CRITICAL,
20 MAJOR y 1 MINOR. Las 26 CRITICAL pertenecen a `python:S8396`, en
`backend/app/api/schemas.py`, por campos `Optional` sin valor predeterminado.
Son modelos de respuesta: conviene revisar si cada campo debe estar presente
y aceptar `null`, o si debe poder omitirse, antes de añadir `= None` a todos.
Los hallazgos requieren revisión del contrato y del comportamiento esperado.

## Evidencias locales

- `.reports/docker-tests.log`: construcción de la imagen de pruebas y suite.
- `.reports/coverage.xml` y `.reports/pytest.xml`: cobertura y resultados.
- `.reports/deployment-check.json`: ID y SHA-256 del PDF de persistencia.
- `.reports/sonar-scanner.log`: ejecución y Quality Gate.
- `.reports/sonarqube-summary.json`: métricas, condiciones y hallazgos de la API.

Estos artefactos y `.env` están excluidos de Git. Los contenedores quedaron
en ejecución. La guía [DOCKER_SONARQUBE.md](DOCKER_SONARQUBE.md) documenta
cómo repetir las pruebas, ejecutar otro análisis y detener los servicios.
