# Experimentos reservados de comparaciones completas

## Criterios y alcance

Un snapshot congela listas completas de contenidos, procedencia académica, etiquetas humanas, IDs de revisiones, parámetros de comparación y resultados de las llamadas NLP necesarias para reproducir el algoritmo de selección global. Exige consenso en cada par de la matriz objetivo × comparado; no convierte pares desconocidos en negativos. Las etiquetas `UNCERTAIN` deben resolverse antes de reservar una comparación. Se conservan huella del código, versiones de dependencias y hash de contenido.

Los casos reservados se excluyen de entrenamientos posteriores mediante las mismas fuentes académicas que usa la partición por grupos. Las versiones anteriores sin procedencia verificable o con fuentes reservadas expuestas no se consideran candidatas válidas para promoción. No se sustituyen modelos ausentes por el baseline durante un experimento.

La evaluación ejecuta el comparador completo, incluyendo generación de candidatos, selección y coberturas, sin guardar comparaciones nuevas ni modificar resultados históricos. Las características NLP se reproducen desde el snapshot, y los artefactos de modelo se identifican por SHA-256. Un cambio de código incompatible, una llamada NLP no registrada o un artefacto alterado invalida la ejecución.

Se miden precisión/recall/F1 de correspondencias positivas y error absoluto de cobertura en ambos sentidos. `MATCH` y `PARTIAL_MATCH` son correspondencias positivas; `NO_MATCH` es negativo. La cobertura esperada usa los mismos contenidos curriculares efectivos del comparador. No se inventa una puntuación global humana para calcular errores sobre el score continuo.

## Comparación controlada

Baseline y candidato se ejecutan sobre el mismo snapshot. La recomendación exige mejora mínima de F1, ausencia de regresión en recall y errores de cobertura, límites por comparación y al menos dos grupos académicos independientes. Los criterios y resultados por comparación quedan registrados. Una recomendación no activa modelos: la activación continúa siendo una operación separada.

Los resultados describen el conjunto revisado disponible. La autenticación de revisores y la adquisición de anotaciones institucionales siguen siendo requisitos externos al experimento automatizado. Reservar matrices completas puede requerir ampliar las anotaciones desde los enlaces manuales de la API.

## Uso y API

En Gestión de modelos, el panel de evaluación permite seleccionar comparaciones anotadas, crear el conjunto reservado, elegir referencia y candidato y consultar experimentos guardados. El baseline está disponible como referencia sin artefacto entrenado. Reservar fuentes es permanente en esta versión: no existe endpoint de borrado ni liberación para entrenamiento.

| Endpoint | Operación |
|---|---|
| `POST /api/evaluation/snapshots` | Crear con `name` y `comparison_ids` (hasta 20 comparaciones distintas) |
| `GET /api/evaluation/snapshots` | Listar metadatos recientes (`limit`, máximo 100) |
| `GET /api/evaluation/snapshots/{id}` | Consultar metadatos |
| `GET /api/evaluation/snapshots/{id}/export` | Descargar contenidos, etiquetas, procedencia y traza NLP |
| `POST /api/evaluation/experiments` | Ejecutar con `snapshot_id`, `reference_version`, `candidate_version` y `criteria` opcionales |
| `GET /api/evaluation/experiments` | Listar informes recientes |
| `GET /api/evaluation/experiments/{id}` | Consultar un informe persistido |
| `GET /api/evaluation/experiments/{id}/export` | Descargar el informe JSON |

Una matriz incompleta, desacuerdo, etiqueta incierta, procedencia incompatible, artefacto ausente o entorno modificado produce conflicto 409. Las consultas por ID inexistente devuelven 404 y los parámetros inválidos, 422. La captura admite como máximo 10000 pares anotados y un presupuesto de 20000 pares de cálculo NLP por snapshot.

## Métricas y criterios registrados

La precisión, recall y F1 agregadas suman verdaderos positivos, falsos positivos y falsos negativos de las correspondencias seleccionadas; se incluye también F1 macro por comparación. Si no existen positivos esperados ni predichos, F1 vale 1, pero ese caso por sí solo no permite recomendar promoción: el conjunto debe contener pares positivos y negativos. El error de cobertura se expresa en puntos porcentuales y se promedia por comparación.

Por defecto se exige mejora de F1 de al menos 0.01, caída máxima de recall de 0 y aumento máximo de error de cobertura de 0, tanto agregado como por comparación. La caída de F1 por comparación admite hasta 0.05 y se requieren al menos dos grupos académicos independientes. La API permite configurar estos criterios; la UI expone los dos límites de F1 y conserva los demás valores por defecto. Todos se guardan junto con las comprobaciones y deltas individuales.

Los modelos nuevos registran `data_provenance_schema=2` y tokens de todas las fuentes humanas expuestas durante entrenamiento y validación interna. La reserva excluye transitivamente universidad/asignatura, sílabos, contenidos, pares de texto normalizados y hashes de documentos compartidos. Los modelos antiguos sin esa procedencia y los entrenados solo con sintéticos requieren entrenamiento humano independiente antes de participar en este protocolo.

El score supervisado alimenta el comparador completo; las categorías finales mantienen los umbrales del pipeline congelado. Se conserva el atajo de contenido idéntico del comparador. Un manifiesto fija artefacto, parámetros y procedencia por ID de versión: reemplazar el artefacto exige registrar una versión nueva. La traza congela resultados NLP; no vuelve a extraer PDFs ni vuelve a calcular embeddings durante el replay. No se admite importar snapshots exportados en esta entrega.

Las pruebas automatizadas utilizan matrices y modelos controlados para comprobar reproducibilidad, fugas, regresiones y conservación de datos. Sus resultados no demuestran rendimiento sobre sílabos institucionales reales. El flujo integrado se verifica también en Chromium mediante reserva, ejecución, exportación, recuperación y manejo de errores; el procedimiento está en [VALIDACION_NAVEGADOR.md](VALIDACION_NAVEGADOR.md). La aceptación manual institucional y la evaluación de otras pantallas siguen siendo actividades distintas.
