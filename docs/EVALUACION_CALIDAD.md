# Evaluación de calidad según el manual de la Universidad Continental

Referencia: `Manual_Evaluacion_Calidad_Software.pdf`, páginas 8–10 y 18–21.
El objetivo de esta entrega de Fase 3 es cumplir el 100% de la rúbrica (20/20).
El manual exige **cobertura global mínima de 80%**, no cobertura de 100%.
La nota oficial se calcula exclusivamente en Quantum tras la entrega en GitLab.

| Criterio | Requisito para puntuación máxima | Puntos |
|---|---|---:|
| Seguridad | A | 5 |
| Fiabilidad | A | 4 |
| Cobertura global | ≥80% | 4 |
| Mantenibilidad | A | 4 |
| Hotspots | Sin hotspots o ≥80% revisados | 2 |
| Duplicación | ≤3% | 1 |

No se excluyen carpetas de código, reglas ni archivos difíciles de cubrir.
Las fuentes evaluadas son `backend/app` y `frontend/src`; las pruebas son
`tests`, `frontend/tests` y `frontend/e2e`. Las herramientas, dependencias,
datos de ejecución y documentos no forman parte del código de aplicación.
Se eliminaron todos los patrones de `sonar.exclusions`. El manual permite
como máximo cinco exclusiones individuales de configuración y penaliza
excluir carpetas con diez puntos. Más de 2500 hallazgos anulan la nota.

## Datos académicos y pipeline

`.gitlab-ci.yml` incluye el pipeline oficial `root/laboratorio-quality`,
archivo `/gitlab/quality-pipeline.yml`, sin sustituir sus etapas ni avisos.
`project.yml` contiene los datos proporcionados por el grupo. Se normalizó
el curso a **Taller de Investigación II**, texto exacto de las opciones
permitidas, y se ubicaron `evaluator` y `members` dentro de `academic`,
conforme al ejemplo visual de la página 9. Se conserva el peso solicitado
de 80%; según el manual, el motor actual calcula siempre la nota sobre 20.

Crear estos archivos no envía mensajes. El push y el pipeline oficial
desencadenan la evaluación y la notificación a docente e integrantes.

## Repetir la verificación

Desde la raíz, con Docker Desktop iniciado y `.env` local preparado:

```powershell
docker compose -f compose.sonarqube.yaml up -d --wait --wait-timeout 600
docker compose -f compose.sonarqube.yaml --profile tools run --rm --build backend-tests

Push-Location frontend
npm.cmd ci --cache ../.cache/npm
npm.cmd run test:coverage
npm.cmd run test:types
npm.cmd run build
npm.cmd run lint
Pop-Location

# Solo para preparar o restaurar el gate en la instancia LOCAL.
.venv/Scripts/python.exe scripts/check_sonar_quality.py --configure-gate

# Mantener los archivos estables mientras se ejecuta el escáner.
docker compose -f compose.sonarqube.yaml --profile tools run --rm sonar-scanner
.venv/Scripts/python.exe scripts/check_sonar_quality.py
```

El verificador solo usa la biblioteca estándar de Python; también puede
ejecutarse con `python`. Lee el token local de `.env` o del entorno sin
imprimirlo. La opción `--configure-gate` requiere `SONAR_ADMIN_PASSWORD`.
El gate local incorpora los seis criterios globales y, adicionalmente,
exige cero bugs, vulnerabilidades y code smells. No modifica el gate del
servidor institucional. `check_sonar_quality.py` devuelve código 1 si no se
alcanza 20/20, hay incidencias abiertas o el gate no evaluó todas las condiciones
globales exigidas. Comprueba los comparadores y umbrales; acepta valores más
estrictos y rechaza condiciones duplicadas, ignoradas o sin aprobar. La condición
de revisión de hotspots puede faltar únicamente cuando el recuento es cero.
Los errores de conexión, respuesta o métricas devuelven código 2 y sustituyen
el informe anterior por `cumple: false`; no se reutiliza un éxito histórico.

Vitest exige además un mínimo local de **80% de líneas y 70% de ramas** para
todo `frontend/src`. Estas protecciones se ejecutan con `npm.cmd run test:coverage`
y no sustituyen la medida global de SonarQube. El alcance y las regresiones de
integración se describen en [PLAN_SESION_29.md](PLAN_SESION_29.md). La ampliación
de comparaciones de la versión 3.3.0 está en
[COMPARACION_POR_LOTES.md](COMPARACION_POR_LOTES.md); sus pruebas regeneran los
mismos reportes, sin excluir las nuevas fuentes del análisis.

Los siguientes informes **sí deben versionarse**, porque el pipeline
institucional analiza archivos y no ejecuta pruebas:

- `.reports/coverage.xml`: cobertura de líneas y ramas Python.
- `.reports/pytest.xml`: resultados JUnit del backend.
- `frontend/coverage/lcov.info`: cobertura de todo el frontend, también
  archivos sin pruebas. El comando normaliza las rutas Windows a rutas
  relativas del repositorio para importar el reporte desde Linux.

Los logs, capturas y `.reports/sonarqube-compliance.json` son evidencias
locales ignoradas por Git. Nunca versionar `.env` ni tokens.

## Entrega oficial

1. Generar nuevamente las coberturas después de cualquier cambio de código.
2. Comprobar que las pruebas y el escáner terminan con código 0.
3. Revisar `git status` y comprobar que aparecen los tres reportes anteriores.
4. Registrar y subir los cambios al repositorio GitLab indicado para la entrega.
5. Verificar `detect`, `quality` y `notify`, las métricas del servidor
   institucional y el correo oficial. Las versiones y perfiles de análisis
   institucionales pueden producir hallazgos distintos de los locales.

La aceptación científica de Fase 3 y la calidad del código son evaluaciones
distintas. Estas pruebas no sustituyen las anotaciones ni los experimentos
institucionales sobre datos reales.
