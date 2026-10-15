# Fase 3: Ground truth, acuerdo y aprendizaje activo

## Primera entrega: pares revisados y consenso

Cada revisión es un evento que conserva autor, fecha, decisión y justificación. Corregir una decisión genera otra revisión, sin actualizar el evento anterior ni la predicción IA. Para consolidar un par se utiliza el último voto de cada identificador de revisor (normalizado en espacios y mayúsculas), ordenando por fecha e ID en caso de empate.

La unidad de análisis es `(comparación, contenido objetivo, contenido comparado)`, incluyendo enlaces manuales válidos. Dos o más revisores distintos que coinciden producen estado `CONSENSUS`; un solo revisor produce `SINGLE_REVIEW`; decisiones distintas producen `DISAGREEMENT`. Una mayoría no resuelve automáticamente un desacuerdo. Las cuatro etiquetas originales se mantienen separadas en la evaluación humana.

El acuerdo se calcula por pareja de revisores sobre pares evaluados por ambos. Se informa número de pares comunes, acuerdo observado y kappa nominal de Cohen: `(acuerdo observado - acuerdo esperado) / (1 - acuerdo esperado)`. Sin pares comunes o cuando el acuerdo esperado es 1, kappa es `null`; no se interpreta como acuerdo perfecto. Los identificadores representan autores declarados; la autenticación de usuarios pertenece a Fase 4.

## API y entrenamiento

- `GET /api/dataset/ground-truth`: resumen y pares consolidados; filtros de comparación y estado, con paginación.
- `GET /api/dataset/ground-truth/export?format=json|csv`: exportación completa de la vista consolidada para el filtro solicitado.
- `GET /api/dataset/agreement`: acuerdo por pareja de revisores; filtro opcional de comparación.
- `POST /api/models/train`: política `ground_truth_policy=consensus|individual`. La UI propone consenso; los clientes existentes conservan por defecto la política individual. Ambas políticas quedan registradas en las métricas.

Entrenar con consenso aporta una observación por par acordado, conservando IDs de las revisiones fuente. Si existen revisiones pero no pares consensuados, se solicita más revisión humana; no se sustituye silenciosamente ese conjunto por bootstrap. La separación académica y la exclusión de sintéticos de la evaluación humana siguen vigentes.

Los pares y exportaciones incluyen características, procedencia, voto vigente y referencias de página de ambos documentos cuando están disponibles. Las revisiones históricas sin vínculos recuperables no se convierten en pares ficticios; el resumen cuenta eventos vinculados. Si un par manual también tiene correspondencia evaluada, se conservan sus características para entrenamiento. Los pares manuales sin características no se entrenan como vectores vacíos.

## Segunda entrega: cola y lotes de aprendizaje activo

La estrategia `annotation-priority-001` considera las correspondencias guardadas y los pares manuales ya propuestos mediante revisiones válidas. No genera un producto cartesiano de contenidos ni inventa candidatos para temas sin pareja. Su cobertura tiene como denominador los pares propuestos de las comparaciones seleccionadas, incluidos los consensuados.

El orden de atención es: desacuerdo, revisión única y ausencia de revisión. Dentro de cada grupo se prioriza la etiqueta `UNCERTAIN`, después la distancia al umbral de referencia más cercano y finalmente IDs estables. Los umbrales de referencia son los defaults del scoring adaptativo; no se presentan como parámetros recuperados del modelo histórico ni como probabilidades. Una distancia de hasta 0.05 activa la explicación de cercanía a un umbral.

La cola excluye pares consensuados. Si se identifica un revisor, excluye también su propio voto único: repetirlo no aporta una segunda opinión. El autor puede corregir su voto en un desacuerdo, conservando el historial. Los pares manuales sin score se muestran sin puntuación, manteniendo textos y referencias de página.

- `GET /api/active-learning/queue`: filtros de comparación, motivo y autor; paginación y cobertura del ámbito completo, independiente de los filtros de elegibilidad.
- `POST /api/active-learning/batches`: selección fija de hasta 100 pares para un autor, según los filtros y el orden de prioridad. Sin candidatos responde 409.
- `GET /api/active-learning/batches`: recuperación de lotes recientes, incluso después de recargar la aplicación.
- `GET /api/active-learning/batches/{id}`: selección inicial, estado actual, cobertura y casos elegibles para el autor del lote.
- `POST /api/active-learning/batches/{id}/complete`: cierre idempotente; registra cobertura final y fecha sin sobrescribir cierres previos.

Los votos se registran mediante el endpoint de revisiones existente y preservan la predicción original. Auditoría actualiza sus recuentos y el panel de consenso tras guardar una revisión. Es posible abrir el informe y las evidencias PDF, y recuperar después el lote persistido.

Las tablas `annotation_batches` y `annotation_batch_completions` conservan selección y cierre por separado. Cada lote guarda estrategia y umbrales de referencia, casos y métricas iniciales del lote y del ámbito. El cierre guarda esas métricas finales; las revisiones futuras solo cambian el estado actual. Si desaparece una fuente, la consulta de progreso responde 409 y no completa artificialmente el lote.

La medición compara cuántos pares tienen alguna revisión y cuántos tienen consenso, mostrando cantidades y porcentajes. Una muestra vacía produce porcentajes `null`. El lote puede cerrarse después del aporte de un solo autor: ese voto aumenta la cobertura revisada, pero no crea consenso por sí solo. Los cambios entre inicio y cierre pueden incluir aportes concurrentes de otros revisores; no se atribuyen exclusivamente al autor del lote.

## Tercera entrega: experimentos reservados

El Paquete 28 implementa snapshots inmutables con la matriz completa de consenso definitivo, exclusión de sus fuentes de futuros entrenamientos y comparación de versiones mediante replay de las características NLP congeladas. Gestión de modelos permite reservar comparaciones, ejecutar experimentos, consultar regresiones y exportar informes. Los detalles y límites están en [EXPERIMENTOS_FASE_3.md](EXPERIMENTOS_FASE_3.md).

El alcance de desarrollo de Fase 3 está completado. La validación institucional exige todavía anotaciones exhaustivas e independientes y modelos entrenados fuera de los grupos reservados. Los experimentos no activan modelos; el consenso sigue siendo una etiqueta experimental para aprendizaje, no una resolución oficial de convalidación.
