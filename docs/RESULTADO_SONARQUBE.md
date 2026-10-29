# Resultado de despliegue y análisis SonarQube

## Validación actual — 2026-10-29 — Sesión 31, comparación por lotes

**20/20 estimado localmente, con Quality Gate PASSED y cero incidencias.**
El análisis final terminó con código 0 y `EXECUTION SUCCESS`. El verificador
de la rúbrica devolvió código 0, `cumple: true` y ningún incumplimiento. Las
fuentes nuevas permanecen dentro del alcance; no se excluyó código ni se
desactivaron reglas.

Análisis `baa7f940-1d0e-497d-b968-9465156d0a9b`, fechado por el servidor a las
**00:01:49 America/Lima** del 29 de octubre. Escáner finalizado a las
**00:04:31**. SonarQube **26.10.0.133078**, estado `UP`.

| Criterio | Resultado real | Puntos |
|---|---|---:|
| Seguridad | A · 0 vulnerabilidades | 5/5 |
| Fiabilidad | A · 0 bugs | 4/4 |
| Cobertura global | 86,4% | 4/4 |
| Mantenibilidad | A · 0 code smells | 4/4 |
| Security hotspots | 0 | 2/2 |
| Duplicación | 0,7% | 1/1 |
| **Total estimado local** | **100% de los puntos** | **20/20** |

SonarQube informa **90,7%** de líneas, **75,1%** de ramas y **13 206** líneas
de código. Frente a la sesión 30, cobertura global de 85,6% a **86,4%** y
duplicación de 0,8% a **0,7%**. Se verificaron las condiciones efectivas del gate
y la ausencia de incidencias abiertas, además de las notas A/A/A.

### Implementación y pruebas

- Versión **3.3.0**, fase 3: un objetivo frente a hasta cinco candidatos,
  modelo fijo, ranking por cobertura del objetivo/afinidad/ID, resultados
  independientes y acceso a sus análisis e informes. Historial y JSON del lote,
  UUID idempotente y conservación de avances parciales en SQLite. Uso y límites
  en [COMPARACION_POR_LOTES.md](COMPARACION_POR_LOTES.md).
- **172 pruebas Python aprobadas en Docker en 58,59 s**, sin omisiones;
  dos advertencias de deprecación de dependencias. Cobertura backend:
  **90,86%** de líneas y **73,97%** de ramas. Incluye 35 casos nuevos de dominio
  y API: límites, interrupción, recuperación, modelo fijo y errores parciales.
- **134 pruebas Vitest aprobadas**: **89,69%** de líneas, **76,17%** de ramas,
  **88,41%** de sentencias y **81,48%** de funciones. Mínimos 80/70 aprobados;
  LCOV regenerado con 26 rutas relativas de fuentes.
- **8 pruebas Chrome aprobadas en 1,2 min** en la ejecución final: cuatro
  científicas, dos visuales y dos de lotes. Descarga JSON/PDF, análisis,
  idempotencia tras recarga y resultados parciales en móvil verificados con
  API y base temporal reales. Capturas de escritorio y móvil inspeccionadas.
- Tipado estricto de aplicación/pruebas/navegador, lint, build y
  `git diff --check` aprobados. El primer análisis detectó una etiqueta de
  candidato sin texto accesible explícito; se corrigió, se repitieron las
  pruebas de frontend/navegador y el análisis final quedó sin hallazgos.

### Publicación y evidencias

Web disponible en <http://localhost:5173>, pestaña **Por lotes**. Salud API
**3.3.0/fase 3**, catálogo e historial de lotes HTTP 200. Chrome confirmó
ausencia de errores JavaScript y desbordamiento horizontal móvil. Esta
comprobación del despliegue solo consultó datos; los lotes de prueba se crearon
en bases temporales aisladas.

Se reconstruyó el frontend con su Dockerfile y se actualizó la capa de código
de la API sobre sus dependencias locales, conservando la imagen previa como
`convcomp-backend:runtime-session31` y los volúmenes existentes. Las **70 fuentes
Python** desplegadas coinciden con el repositorio por SHA-256 normalizado;
`pip check` no encontró incompatibilidades.

Evidencias locales ignoradas por Git:

- `.reports/session31-sonar-scanner.log`, `session31-compliance.log`,
  `sonarqube-compliance.json` y `session31-analyses.json`.
- `.reports/session31-backend-tests.log`, `session31-frontend-tests.log`,
  `session31-frontend-checks.log`, `session31-browser-tests.log` y
  `session31-validation.json`.
- `.reports/session31-backend-refresh.log`, `session31-frontend-docker-build.log`,
  `session31-docker-final.log`, `session31-docker-check.json`,
  `session31-source-integrity.json` y `session31-pip-check.log`.
- `.reports/session31-batch-desktop.png`, `session31-batch-mobile.png`,
  `session31-docker-desktop.png` y `session31-docker-mobile.png`.

Los reportes de entrega regenerados son `.reports/coverage.xml`,
`.reports/pytest.xml` y `frontend/coverage/lcov.info`. Se conservan los límites:
sin reanudación automática de lotes interrumpidos, autenticación de Fase 4 ni
validación científica institucional. La nota oficial de Quantum permanece
pendiente de la entrega en GitLab; **20/20 es una estimación local verificable**.
Los cambios permanecen sin commit y el escáner advierte de información SCM
incompleta, sin impedir las comprobaciones globales.

## Validación histórica — 2026-10-28 — Sesión 30, rediseño violeta

**Máxima puntuación local conservada: 20/20 estimado según el manual.**
El análisis final terminó con código 0, `EXECUTION SUCCESS` y **Quality Gate
PASSED**. El verificador reforzado devolvió código 0, `cumple: true` y ningún
incumplimiento. Seguridad, fiabilidad y mantenibilidad mantienen **A/A/A**.

Análisis `18cb74aa-78aa-4cac-ae4b-93d7dd9793a1`, fechado por el servidor a las
**23:01:22 America/Lima**; el escáner terminó a las **23:04:09** del 28 de octubre.
SonarQube **26.10.0.133078**. Se analizaron las fuentes finales después de los
ajustes de contraste y formato, sin excluir código ni desactivar reglas.

| Criterio | Resultado real | Puntos |
|---|---|---:|
| Seguridad | A · 0 vulnerabilidades | 5/5 |
| Fiabilidad | A · 0 bugs | 4/4 |
| Cobertura global | 85,6% | 4/4 |
| Mantenibilidad | A · 0 code smells | 4/4 |
| Security hotspots | 0 | 2/2 |
| Duplicación | 0,8% | 1/1 |
| **Total estimado local** | **100% de los puntos** | **20/20** |

Cobertura global de líneas: **90,0%**; de ramas: **74,4%**. Tamaño: **12 524**
líneas de código. Frente a la sesión 29, cobertura de 85,0% a **85,6%** y
duplicación de 1,1% a **0,8%**.

### Implementación y comprobaciones

- Rediseño según las dos capturas SaaS y la paleta académica violeta aportadas
  por el usuario. Navegación blanca, cabecera violeta, fondo lavanda, paneles
  adaptables, favicon propio y metadatos en español.
- Carga de ambos sílabos mediante un panel reutilizable, sin modificar las
  peticiones REST. Metadatos independientes, procesamiento, fallos y reintentos
  probados. No se inventan cifras, testimonios ni capacidades del producto.
- Catálogo, resultados, auditoría, modelos y guía adaptados al tema. El visor
  mantiene la geometría de las evidencias. El descargo institucional sigue
  presente en el pie común de todas las vistas.
- **120 pruebas Vitest aprobadas** en la ejecución final; frontend completo:
  **88,86%** de líneas, **75,77%** de ramas, **87,26%** de sentencias y **78,93%**
  de funciones. Mínimos de 80/70 aprobados y LCOV relativo regenerado.
- **6 pruebas de navegador aprobadas en 42,7 s**: dos del rediseño y las cuatro
  científicas existentes. Escritorio 1440 × 1050 y móvil 390 × 844; navegación,
  ausencia de desbordamiento, guía, foco, Tab/Shift+Tab y Escape comprobados.
- Tipado de aplicación/pruebas/navegador, lint, build y `git diff --check`
  aprobados. Se añadieron los tipos DOM al proyecto TypeScript que compila las
  pruebas de navegador, sin sustituir sus comprobaciones por código sin tipos.
- El código backend no cambia en esta sesión. Se reutilizan sus XML/JUnit,
  generados en la sesión 29 con **137 pruebas aprobadas**, cobertura de líneas
  **90,22%** y ramas **72,95%** sobre las mismas fuentes.

### Despliegue y evidencias

La aplicación está saludable en <http://localhost:5173>. El frontend se construyó
con su Dockerfile. La API local tenía cuatro fuentes anteriores; se actualizó
su capa de código conservando las dependencias y los volúmenes. Todas sus
fuentes Python coinciden por SHA-256 con el repositorio, y `pip check` terminó
sin incompatibilidades. API 3.2.1/fase 3 y catálogo HTTP 200, sin excepciones
JavaScript ni desbordamiento horizontal móvil en la comprobación de publicación.

Evidencias locales ignoradas por Git:

- `.reports/session30-sonar-final.log`, `session30-compliance.log` y
  `sonarqube-compliance.json`: escáner, condiciones, medidas y rúbrica.
- `.reports/session30-analyses.json`: ID, fecha del análisis y servidor.
- `.reports/session30-frontend-tests.log`, `session30-frontend-checks.log`
  y `session30-browser-tests.log`: pruebas y comprobaciones finales.
- `.reports/session30-docker-final.log`, `session30-backend-refresh.log`,
  `session30-container-sources.json` y `session30-docker-check.json`.
- `.reports/session30-docker-desktop.png`, `session30-docker-mobile.png`
  y las capturas de la suite `session30-home-*`, `session30-guide-*` y modelos.

Los reportes de entrega siguen siendo `.reports/coverage.xml`,
`.reports/pytest.xml` y `frontend/coverage/lcov.info`. La nota oficial de Quantum
continúa pendiente de la entrega en GitLab institucional; el 20/20 anterior
es una estimación local verificable. El alcance visual está documentado en
[DISENO_WEB.md](DISENO_WEB.md).

## Validación histórica — 2026-10-28 — Sesión 29

**20/20 estimado según el manual, verificado contra un nuevo análisis real.**
SonarScanner terminó con código 0, `EXECUTION SUCCESS` y **Quality Gate PASSED**.
El verificador reforzado también terminó con código 0, `cumple: true` y lista
vacía de incumplimientos. Se comprobaron las once condiciones devueltas por el
gate, incluidos los umbrales globales; no hubo condiciones ignoradas.

Análisis `167bc699-6ae2-47fe-9a44-3975bfc14ee1`, fechado por el servidor a las
**20:58:23 America/Lima**; el escáner terminó a las **21:02:09** del 28 de octubre.
SonarQube **26.10.0.133078**; Docker **29.7.2**, operativo después de restaurar
la virtualización y reiniciar Windows.

| Criterio del manual | Resultado real | Puntos |
|---|---|---:|
| Seguridad | A · 0 vulnerabilidades | 5/5 |
| Fiabilidad | A · 0 bugs | 4/4 |
| Cobertura global | 85,0% | 4/4 |
| Mantenibilidad | A · 0 code smells | 4/4 |
| Security hotspots | 0 | 2/2 |
| Duplicación | 1,1% | 1/1 |
| **Total estimado** | **100% de los puntos** | **20/20** |

La cobertura global subió de **82,4% a 85,0%**. SonarQube informa **89,6%** de
líneas y **73,3%** de ramas, con 12 763 líneas de código. No se excluyeron
fuentes ni se desactivaron reglas para conseguir estos resultados.

### Implementación y validación de esta sesión

- Una revisión guardada desde el visor doble comunica el par y la decisión a
  `App`, actualizando el dictamen humano en tabla/evidencia sin alterar la
  clasificación IA original. Los contratos HTTP se mantienen.
- El verificador rechaza condiciones globales ausentes, duplicadas, ignoradas,
  sin aprobar o con umbrales relajados, además de incidencias abiertas. Un fallo
  de consulta sustituye el informe anterior por `cumple: false` y devuelve 2.
- **137 pruebas Python aprobadas** en Docker en **110,78 s**, sin omisiones,
  con dos deprecaciones de dependencias. Cobertura backend: **90,22%** de líneas,
  **72,95%** de ramas y **86,87%** combinada; XML y JUnit regenerados.
- **116 pruebas Vitest aprobadas**: cobertura frontend de **86,57%** de líneas
  y **73,65%** de ramas, frente a 77,01% y 65,10% anteriores. Se incorporan
  mínimos locales de 80% de líneas y 70% de ramas sobre todo `frontend/src`.
- Visor doble: **100% de líneas**; aplicación: **81,13%**; gestión de modelos:
  **96,8%**. Las pruebas comprueban navegación, cierre, revisión, entrenamiento,
  activación explícita y recuperación tras errores; no atribuyen rendimiento
  científico a los datos controlados.
- **4 pruebas de navegador aprobadas** en **45,8 s**, usando Chrome local
  mediante `CONVCOMP_BROWSER_EXECUTABLE` porque falta el Chromium de Playwright.
- Tipado estricto de pruebas/aplicación, lint, build y `git diff --check` correctos.
  Pipeline YAML y estructura de metadatos académicos verificados.

### Evidencias y entrega

Evidencias locales ignoradas por Git:

- `.reports/session29-sonar-scanner.log`: nuevo escáner y gate.
- `.reports/sonarqube-compliance.json` y `.reports/session29-compliance.log`:
  métricas, condiciones, recuentos, rúbrica y resultado del verificador.
- `.reports/session29-analyses.json`: ID/fecha del análisis y versión del servidor.
- `.reports/session29-backend-tests.log`, `.reports/session29-frontend-tests.log`,
  `.reports/session29-browser-tests.log` y `.reports/session29-frontend-checks.log`.
- `.reports/session29-validation.json`: resumen de pruebas y cobertura.

Entregables regenerados y habilitados para Git: `.reports/coverage.xml`,
`.reports/pytest.xml` y `frontend/coverage/lcov.info`, con rutas relativas válidas.
El escáner advierte de falta de información SCM para cambios sin commit; el
análisis global y las condiciones anteriores sí se ejecutaron correctamente.

Esta es una **estimación local**, no una nota oficial emitida por Quantum.
El remoto configurado sigue siendo GitHub; faltan el destino y acceso al GitLab
institucional para entregar y verificar `detect`, `quality` y `notify`.
No se ejecutó ese pipeline. Los servicios locales de calidad quedan saludables
en [SonarQube](http://localhost:9000/dashboard?id=convcomp).

Plan y cierre: [PLAN_SESION_29.md](PLAN_SESION_29.md), [TASKS.md](TASKS.md).

## Validación histórica — 2026-10-17

**Cumplimiento local de la rúbrica del manual: 20/20 (100%).** SonarScanner
terminó con código 0, `EXECUTION SUCCESS` y **Quality Gate PASSED**. El gate
evalúa condiciones globales efectivas, incluidas cobertura mínima de 80%,
calificaciones A, duplicación máxima de 3% y cero incidencias abiertas.

Análisis `0e0ec603-3f87-4a75-92af-5d2a8def4e54`, iniciado a las
**18:13:55 America/Lima**, escáner finalizado a las **18:16:23**.
Se conservan las versiones SonarQube 26.10.0.133078 y SonarScanner 8.1.0.6389.

| Criterio del manual | Resultado real | Puntos |
|---|---|---:|
| Seguridad | A · 0 vulnerabilidades | 5/5 |
| Fiabilidad | A · 0 bugs | 4/4 |
| Cobertura global | 82,4% | 4/4 |
| Mantenibilidad | A · 0 code smells | 4/4 |
| Security hotspots | 0; puntuación automática según el manual | 2/2 |
| Duplicación | 1,1% | 1/1 |
| **Total estimado según la rúbrica** | **100% de los puntos** | **20/20** |

Cobertura global de líneas: **87,7%**; de ramas: **68,9%**. Los 47 hallazgos
del análisis histórico quedaron resueltos por cambios de código, sin
excluir carpetas ni desactivar reglas. El manual exige 80% de cobertura
global para la puntuación máxima; no exige 100% de cobertura.

### Cambios y validaciones

- Carga de PDF síncrona ejecutada por FastAPI en su grupo de hilos, sin
  bloquear el bucle asíncrono; PDF vacío devuelve HTTP 400 y no se persiste.
- Campos obligatorios anulables declarados como `Tipo | None`, conservando
  presencia obligatoria y aceptación de `null`. Se probaron contrato y esquema.
- Botones de formulario con tipo explícito, promesa de render PDF gestionada,
  etiquetas asociadas a controles y selección de PDF/modelo mediante botones
  nativos accesibles.
- Expresiones regulares con retroceso excesivo corregidas conservando el
  filtrado de títulos y números.
- **113 pruebas Python aprobadas** en Docker en **43,86 s**, sin omisiones,
  con dos advertencias de deprecación de dependencias. Coverage.py: líneas
  3477/3854 (**90,22%**), ramas 677/928 (**72,95%**), combinada **86,87%**.
- **100 pruebas Vitest aprobadas**: contratos HTTP, fallos de servidor,
  carga de PDF, evidencia, revisiones inmutables, anotación, auditoría,
  reserva científica y recuperación de informes. Cobertura de todo el
  frontend: líneas **77,01%**, ramas **65,10%**; incluye archivos sin pruebas.
- **4 pruebas Playwright aprobadas** en Chromium en **14,2 s**.
- Compilación, comprobación estricta de tipos de aplicación/pruebas y lint
  correctos. `npm audit`: **0 vulnerabilidades** tras actualizar la dependencia
  transitiva `source-map-js` a una versión corregida.
- `.gitlab-ci.yml` y `project.yml` preparados con los datos del grupo y del
  docente; curso normalizado a `Taller de Investigación II`, peso 80%.
- XML Python/JUnit y LCOV habilitados para versionarse; rutas LCOV relativas
  compatibles con el escáner Linux. Sin patrones `sonar.exclusions`.

### Evidencias y alcance

- `.reports/quality-sonar-scanner.log`: escáner y gate final.
- `.reports/sonarqube-compliance.json`: métricas, condiciones, incidencias
  abiertas y cálculo reproducible de la rúbrica; `cumple: true`.
- `.reports/quality-final-analyses.json`: identificador e historial final.
- `.reports/quality-backend-tests.log`, `.reports/quality-frontend-tests.log`
  y `.reports/quality-browser-tests.log`: ejecución de pruebas.
- `.reports/coverage.xml`, `.reports/pytest.xml` y
  `frontend/coverage/lcov.info`: reportes que deben acompañar la entrega.

El token del proyecto puede leer métricas y gate, pero no el historial de
análisis. El verificador informa esa limitación sin omitir la comprobación
de los criterios. El historial de esta sesión se consultó separadamente
con las credenciales administrativas locales, sin exportarlas.

La calificación anterior es **una estimación local verificable**, no una
nota emitida por Quantum. Queda pendiente registrar/subir los cambios al
GitLab institucional y verificar `detect`, `quality`, `notify` y el correo
oficial. No se ejecutó ese pipeline ni se enviaron correos en esta sesión.
El perfil y la versión del servidor institucional pueden producir resultados
distintos. Consulte [EVALUACION_CALIDAD.md](EVALUACION_CALIDAD.md) para repetir
las comprobaciones y preparar la entrega.

## Registro histórico del 2026-10-15

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
