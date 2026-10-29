# Plan de implementación — Sesión 29 — 2026-10-28

## Objetivo y punto de partida

Continuar la implementación con mejoras verificables de los flujos existentes y
sostener la puntuación máxima de la rúbrica de SonarQube. El usuario confirmó
ambos objetivos. Se preservan la arquitectura modular, los contratos REST y la
separación entre predicción original y revisión humana.

Se revisaron las reglas, TASKS, el planteamiento general, los flujos de Fase 3,
los experimentos, las guías de calidad y Docker, los informes conservados y las
páginas 8–10 y 18–21 del manual PDF local. La planificación antigua del
planteamiento se interpreta junto con la bitácora actual: Fases 1–3 implementadas,
115 tareas cerradas y validación científica institucional pendiente.

La evidencia del 17 de octubre registra A/A/A, cero incidencias y hotspots,
82,4% de cobertura global, 1,1% de duplicación y 20/20 estimado. Es una referencia
histórica hasta repetir el análisis sobre el estado final de esta sesión.

## Alcance y orden de ejecución

| Tarea | Implementación / entrega | Dependencia | Aceptación |
|---|---|---|---|
| TASK-32.1 | Auditar documentos, configuración y evidencia; registrar este plan | Ninguna | Alcance y criterios trazables al manual |
| TASK-32.2 | Endurecer `scripts/check_sonar_quality.py` contra gates incompletos y hallazgos abiertos | 32.1 | Pruebas rechazan falsos positivos; hotspot ausente solo se admite si no existen hotspots |
| TASK-32.3 | Probar navegación sincronizada, cierre y revisión del visor doble | 32.1 | Selección actualiza ambos PDF; la revisión conserva la predicción y el revisor |
| TASK-32.4 | Probar la integración de la aplicación y corregir fallos reproducibles encontrados | 32.3 | Comparación, evidencia y revisión coherentes al navegar; errores permiten recuperación |
| TASK-32.5 | Proteger y regenerar cobertura de frontend completo | 32.3, 32.4 | Piso local de 80% de líneas y 70% de ramas, sin excluir fuentes |
| TASK-32.6 | Ejecutar suites, tipos, lint, build y análisis real SonarQube | 32.2–32.5 | Pruebas aprobadas; gate efectivo; A/A/A, cobertura global ≥80%, duplicación ≤3%, cero incidencias; hotspots sin pendientes |
| TASK-32.7 | Actualizar evidencias, bitácora y preparación de entrega institucional | 32.6 para declarar nota actual | Tres reportes entregables y resultado actual, o limitaciones explícitas si falta infraestructura |
| TASK-32.8 | Recuperar Docker/WSL y verificar el servidor tras reiniciar | Intervención de entorno solicitada durante la sesión | Docker responde y los servicios de calidad arrancan saludables |

El verificador actual comprueba que haya alguna condición del gate; se reforzará
para exigir las condiciones globales necesarias y sus umbrales. La rúbrica puede
dar 20 puntos con algunos code smells; el objetivo adicional del proyecto exige
cero incidencias abiertas y se verificará por separado.

El visor doble figura con 0% de cobertura Vitest; `App.tsx`, con 60,37% de líneas,
y gestión de modelos, con 54,25%. Se priorizan pruebas de conducta que ejerciten
sus integraciones. Los mínimos de frontend son protecciones locales adicionales:
la rúbrica otorga los cuatro puntos con cobertura global ≥80%; no exige 100%.

## Verificación y evidencias

1. Pruebas de regresión del verificador, incluidas condiciones ausentes, umbrales
   relajados, condiciones fallidas y errores de consulta.
2. Vitest con V8 y LCOV relativo, tipado de pruebas/aplicación, lint y build.
3. Suite Python con XML de cobertura y JUnit; preferir la imagen Docker que
   contiene embeddings reales. Pruebas Playwright con almacenamiento aislado.
4. Scanner sobre archivos estables y consulta del gate y las métricas finales.
5. Registrar fecha, análisis, resultados y limitaciones en los documentos de
   calidad y en TASKS; conservar resultados anteriores como históricos.

Los entregables de cobertura son `.reports/coverage.xml`, `.reports/pytest.xml`
y `frontend/coverage/lcov.info`. Los secretos continúan en `.env` ignorado.

## Dependencias y límites

- Al inicio Docker no responde y no está disponible `coverage` en el entorno
  Python local. Tras la recuperación de virtualización y el reinicio comunicado
  por el usuario, Docker 29.7.2 responde; se reutilizan las imágenes de pruebas
  con embeddings reales y los volúmenes de SonarQube/PostgreSQL.
- El único remoto configurado es GitHub (`origin`). La entrega oficial necesita
  el repositorio GitLab institucional y su acceso; preparar archivos no ejecuta
  `detect`, `quality` ni `notify`.
- La nota local se distinguirá de la nota oficial de Quantum. No se atribuirán
  resultados nuevos a informes del 17 de octubre.
- La Fase 4 enumera usuarios, historial y PostgreSQL, pero no tiene un incremento
  detallado acordado. Esta sesión cierra calidad e integración de lo existente;
  la autenticación, migración de base y gestión documental requieren su propio
  diseño y criterios. Las anotaciones reales tampoco se sustituyen por fixtures.

## Cierre esperado

Código y pruebas revisables, cobertura actualizada y una nueva evaluación real
si la infraestructura está disponible. Una tarea se marca completa solo con su
evidencia; las verificaciones que no puedan ejecutarse quedan pendientes.

## Cierre verificado — 2026-10-28

Las ocho tareas del Paquete 32 están completadas localmente. Se corrigió la
propagación del dictamen del visor a resultados y se reforzó el verificador.
Aprobaron 137 pruebas Python, 116 Vitest y 4 de navegador, además de tipos,
lint y build. La cobertura frontend alcanza 86,57% de líneas y 73,65% de ramas.

Nuevo análisis `167bc699-6ae2-47fe-9a44-3975bfc14ee1`: gate PASSED,
A/A/A, cero incidencias/hotspots, cobertura global 85,0%, duplicación 1,1%
y 20/20 estimado. Verificador terminado con código 0 y `cumple: true`.
Los tres reportes de entrega están regenerados. Las evidencias y limitaciones
constan en [RESULTADO_SONARQUBE.md](RESULTADO_SONARQUBE.md).

La entrega oficial continúa pendiente: el remoto actual es GitHub, y se requiere
el destino/acceso de GitLab institucional para ejecutar su pipeline. Este cierre
acredita implementación y calidad local; no emite una nota de Quantum.
